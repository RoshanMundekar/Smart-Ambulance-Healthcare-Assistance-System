from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.connection import get_db
from app.models.user import User
from app.models.ambulance import Driver, Ambulance
from app.models.booking import EmergencyRequest
from app.auth.rbac import require_driver
from app.utils.notifications import ws_manager

router = APIRouter(prefix="/driver", tags=["Driver"])


@router.get("/dashboard")
def driver_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    ambulance = None
    if driver.ambulance_id:
        amb = db.query(Ambulance).filter(Ambulance.id == driver.ambulance_id).first()
        if amb:
            ambulance = {
                "id": amb.id,
                "number": amb.ambulance_number,
                "type": amb.vehicle_type,
                "status": amb.status,
                "equipment": amb.equipment,
            }

    # Active emergency
    active_emergency = (
        db.query(EmergencyRequest)
        .filter(
            EmergencyRequest.assigned_driver_id == driver.id,
            EmergencyRequest.status.in_(["ambulance_assigned", "en_route", "at_scene", "transporting"]),
        )
        .first()
    )

    patient_info = None
    if active_emergency:
        patient = db.query(User).filter(User.id == active_emergency.user_id).first()
        if patient:
            patient_info = {
                "id": patient.id,
                "full_name": patient.full_name,
                "age": patient.age,
                "blood_group": patient.blood_group,
                "medical_history": patient.medical_history,
                "chronic_conditions": patient.chronic_conditions,
                "allergies": patient.allergies,
                "phone": patient.phone,
            }

    return {
        "driver": {
            "id": driver.id,
            "name": driver.driver_name,
            "phone": driver.phone,
            "rating": float(driver.performance_rating),
            "total_trips": driver.total_trips,
            "is_available": driver.is_available,
        },
        "ambulance": ambulance,
        "active_emergency": {
            "id": active_emergency.id if active_emergency else None,
            "status": active_emergency.status if active_emergency else None,
            "patient_lat": float(active_emergency.patient_latitude) if active_emergency else None,
            "patient_lon": float(active_emergency.patient_longitude) if active_emergency else None,
            "patient_address": active_emergency.patient_address if active_emergency else None,
            "eta_minutes": active_emergency.eta_minutes if active_emergency else None,
            "hospital_id": active_emergency.assigned_hospital_id if active_emergency else None,
            "emergency_type": active_emergency.emergency_type if active_emergency else None,
            "patient": patient_info,
        } if active_emergency else None,
    }


@router.post("/toggle-availability")
def toggle_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")
    driver.is_available = not driver.is_available
    db.commit()
    return {"is_available": driver.is_available, "message": f"Status set to {'available' if driver.is_available else 'unavailable'}"}


@router.post("/location")
async def update_location(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.current_latitude = latitude
    driver.current_longitude = longitude
    driver.last_location_update = datetime.utcnow()

    if driver.ambulance_id:
        amb = db.query(Ambulance).filter(Ambulance.id == driver.ambulance_id).first()
        if amb:
            amb.current_latitude = latitude
            amb.current_longitude = longitude
            amb.last_location_update = datetime.utcnow()

    db.commit()

    await ws_manager.broadcast({
        "type": "location_update",
        "data": {
            "ambulance_id": driver.ambulance_id,
            "driver_id": driver.id,
            "latitude": latitude,
            "longitude": longitude,
        },
    })

    return {"message": "Location updated"}


@router.get("/trips/history")
def trip_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver),
):
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    trips = (
        db.query(EmergencyRequest)
        .filter(EmergencyRequest.assigned_driver_id == driver.id)
        .order_by(EmergencyRequest.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": t.id,
            "emergency_type": t.emergency_type,
            "severity": t.severity,
            "status": t.status,
            "response_time": t.response_time_minutes,
            "distance_km": float(t.route_distance_km or 0),
            "created_at": t.created_at.isoformat(),
        }
        for t in trips
    ]
