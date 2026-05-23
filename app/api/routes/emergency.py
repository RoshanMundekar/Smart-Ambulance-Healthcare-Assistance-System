from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database.connection import get_db
from app.models.user import User
from app.models.ambulance import Ambulance, Driver
from app.models.hospital import Hospital
from app.models.booking import EmergencyRequest
from app.schemas.emergency import (
    EmergencyRequest as EmergencyRequestSchema,
    EmergencyResponse, EmergencyStatusUpdate, AmbulanceLocation
)
from app.auth.jwt import get_current_active_user
from app.auth.rbac import require_driver
from app.ai.symptom_analyzer import symptom_analyzer
from app.ai.hospital_recommender import hospital_recommender, ambulance_allocator
from app.ai.specialist_recommender import patient_profile_analyzer, specialist_recommender
from app.utils.maps import get_directions, reverse_geocode
from app.utils.notifications import ws_manager, notify_user, push_emergency_update

router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.post("/request", response_model=EmergencyResponse, status_code=201)
async def create_emergency(
    payload: EmergencyRequestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Step 1: Analyze symptoms with AI
    analysis = symptom_analyzer.analyze(
        symptoms_text=payload.symptoms or payload.emergency_type,
        age=current_user.age,
        gender=current_user.gender,
        medical_history=current_user.medical_history,
    )

    # Step 2: Get patient risk profile
    risk_profile = patient_profile_analyzer.analyze_risk(
        age=current_user.age,
        gender=current_user.gender,
        medical_history=current_user.medical_history,
        chronic_conditions=current_user.chronic_conditions,
        blood_group=current_user.blood_group,
        current_symptoms=payload.symptoms,
    )

    # Step 3: Get AI specialist recommendation
    recommended_specialist = specialist_recommender.recommend_for_emergency(
        payload.emergency_type, analysis
    )

    # Step 4: Resolve address
    address = payload.address
    if not address:
        address = await reverse_geocode(payload.latitude, payload.longitude)

    # Step 5: Find best hospital
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    hospital_recs = hospital_recommender.recommend(
        hospitals=hospitals,
        patient_lat=payload.latitude,
        patient_lon=payload.longitude,
        required_specialization=recommended_specialist,
        emergency=True,
        top_n=1,
    )

    best_hospital = hospital_recs[0] if hospital_recs else None

    # Step 6: Allocate nearest ambulance
    ambulances = db.query(Ambulance).filter(Ambulance.is_active == True).all()
    drivers = db.query(Driver).filter(Driver.is_active == True).all()
    allocation = ambulance_allocator.allocate(
        ambulances=ambulances,
        drivers=drivers,
        patient_lat=payload.latitude,
        patient_lon=payload.longitude,
        emergency_type=payload.emergency_type,
    )

    # Step 7: Get route to hospital
    route_info = None
    eta_minutes = None
    if allocation and best_hospital:
        route_info = await get_directions(
            origin_lat=allocation["ambulance_lat"],
            origin_lng=allocation["ambulance_lon"],
            destination_lat=best_hospital["latitude"],
            destination_lng=best_hospital["longitude"],
        )
        eta_minutes = route_info.get("duration_minutes") if route_info else allocation.get("eta_minutes")

    # Step 8: Create emergency record
    severity = analysis.get("severity", "high")
    if severity == "critical":
        sev = "critical"
    elif severity == "severe":
        sev = "high"
    elif severity == "moderate":
        sev = "medium"
    else:
        sev = "low"

    emergency = EmergencyRequest(
        user_id=current_user.id,
        emergency_type=payload.emergency_type,
        severity=sev,
        patient_latitude=payload.latitude,
        patient_longitude=payload.longitude,
        patient_address=address,
        assigned_ambulance_id=allocation["ambulance_id"] if allocation else None,
        assigned_hospital_id=best_hospital["hospital_id"] if best_hospital else None,
        assigned_driver_id=allocation["driver_id"] if allocation else None,
        ai_specialist_recommendation=recommended_specialist,
        eta_minutes=eta_minutes,
        route_distance_km=route_info.get("distance_km") if route_info else None,
        status="ambulance_assigned" if allocation else "requested",
    )
    db.add(emergency)

    # Step 9: Update ambulance status
    if allocation:
        amb = db.query(Ambulance).filter(Ambulance.id == allocation["ambulance_id"]).first()
        if amb:
            amb.status = "en_route"

    db.commit()
    db.refresh(emergency)

    # Step 10: Send notifications
    await notify_user(
        db=db,
        user_id=current_user.id,
        title="Emergency Request Received",
        message=f"Ambulance dispatched. ETA: {eta_minutes} minutes. Hospital: {best_hospital['hospital_name'] if best_hospital else 'Nearest Hospital'}",
        notification_type="emergency",
        related_id=emergency.id,
        related_type="emergency_request",
    )

    return emergency


@router.get("/my-requests", response_model=List[EmergencyResponse])
def get_my_emergencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(EmergencyRequest).filter(EmergencyRequest.user_id == current_user.id).order_by(EmergencyRequest.created_at.desc()).all()


@router.get("/{emergency_id}", response_model=EmergencyResponse)
def get_emergency(
    emergency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency request not found")
    if emergency.user_id != current_user.id and current_user.role not in ("system_admin", "hospital_admin", "driver"):
        raise HTTPException(status_code=403, detail="Access denied")
    return emergency


@router.patch("/{emergency_id}/status", response_model=EmergencyResponse)
async def update_emergency_status(
    emergency_id: int,
    payload: EmergencyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    emergency = db.query(EmergencyRequest).filter(EmergencyRequest.id == emergency_id).first()
    if not emergency:
        raise HTTPException(status_code=404, detail="Emergency not found")

    valid_transitions = {
        "requested": ["ambulance_assigned", "cancelled"],
        "ambulance_assigned": ["en_route", "cancelled"],
        "en_route": ["at_scene"],
        "at_scene": ["transporting"],
        "transporting": ["arrived"],
        "arrived": ["completed"],
    }

    if emergency.status == payload.status:
        return emergency

    if current_user.role != "system_admin":
        allowed = valid_transitions.get(emergency.status, [])
        if payload.status not in allowed:
            raise HTTPException(status_code=400, detail=f"Cannot transition from {emergency.status} to {payload.status}")

    emergency.status = payload.status
    if payload.eta_minutes:
        emergency.eta_minutes = payload.eta_minutes
    if payload.notes:
        emergency.notes = payload.notes

    if payload.status == "completed":
        emergency.response_time_minutes = int(
            (datetime.utcnow() - emergency.created_at).total_seconds() / 60
        )
        if emergency.assigned_ambulance_id:
            amb = db.query(Ambulance).filter(Ambulance.id == emergency.assigned_ambulance_id).first()
            if amb:
                amb.status = "available"

    db.commit()
    db.refresh(emergency)

    # Push real-time update
    await ws_manager.send_to_user(
        emergency.user_id,
        {"type": "emergency_update", "data": {"status": payload.status, "eta": payload.eta_minutes}},
    )

    return emergency


@router.post("/ambulance/location")
async def update_ambulance_location(
    payload: AmbulanceLocation,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    """Driver updates ambulance GPS location in real-time."""
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    ambulance = db.query(Ambulance).filter(Ambulance.id == driver.ambulance_id).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")

    ambulance.current_latitude = payload.latitude
    ambulance.current_longitude = payload.longitude
    ambulance.last_location_update = datetime.utcnow()
    driver.current_latitude = payload.latitude
    driver.current_longitude = payload.longitude

    db.commit()

    await ws_manager.broadcast(
        {
            "type": "location_update",
            "data": {
                "ambulance_id": ambulance.id,
                "latitude": payload.latitude,
                "longitude": payload.longitude,
            },
        }
    )

    return {"message": "Location updated"}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_to_user(user_id, {"type": "ping", "data": "pong"})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
