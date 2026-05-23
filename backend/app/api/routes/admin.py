from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database.connection import get_db
from app.models.user import User
from app.models.hospital import Hospital
from app.models.doctor import Doctor
from app.models.ambulance import Ambulance, Driver
from app.models.booking import Booking, EmergencyRequest
from app.auth.rbac import require_admin
from app.auth.jwt import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    total_users = db.query(User).count()
    total_hospitals = db.query(Hospital).filter(Hospital.is_active == True).count()
    total_doctors = db.query(Doctor).filter(Doctor.is_active == True).count()
    total_ambulances = db.query(Ambulance).filter(Ambulance.is_active == True).count()
    available_ambulances = db.query(Ambulance).filter(Ambulance.status == "available", Ambulance.is_active == True).count()
    total_bookings = db.query(Booking).count()
    total_emergencies = db.query(EmergencyRequest).count()
    completed_emergencies = db.query(EmergencyRequest).filter(EmergencyRequest.status == "completed").count()

    avg_response = db.query(func.avg(EmergencyRequest.response_time_minutes)).filter(
        EmergencyRequest.response_time_minutes.isnot(None)
    ).scalar()

    emergency_by_type = (
        db.query(EmergencyRequest.emergency_type, func.count(EmergencyRequest.id))
        .group_by(EmergencyRequest.emergency_type)
        .all()
    )

    booking_by_type = (
        db.query(Booking.booking_type, func.count(Booking.id))
        .group_by(Booking.booking_type)
        .all()
    )

    return {
        "users": {
            "total": total_users,
            "by_role": {
                role: db.query(User).filter(User.role == role).count()
                for role in ["patient", "driver", "doctor", "hospital_admin", "system_admin"]
            },
        },
        "hospitals": {"total": total_hospitals},
        "doctors": {"total": total_doctors},
        "ambulances": {
            "total": total_ambulances,
            "available": available_ambulances,
            "in_use": total_ambulances - available_ambulances,
        },
        "bookings": {
            "total": total_bookings,
            "by_type": {t: c for t, c in booking_by_type},
        },
        "emergencies": {
            "total": total_emergencies,
            "completed": completed_emergencies,
            "avg_response_minutes": round(float(avg_response or 0), 1),
            "by_type": {t: c for t, c in emergency_by_type},
        },
    }


# ---- Users ----

@router.get("/users")
def list_users(
    role: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.full_name} deactivated"}


# ---- Hospitals ----

@router.post("/hospitals", status_code=201)
def create_hospital(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    hospital = Hospital(**payload)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.put("/hospitals/{hospital_id}")
def update_hospital(
    hospital_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    for key, value in payload.items():
        if hasattr(hospital, key):
            setattr(hospital, key, value)
    db.commit()
    db.refresh(hospital)
    return hospital


# ---- Ambulances ----

@router.get("/ambulances")
def list_ambulances(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ambulances = db.query(Ambulance).all()
    return [
        {
            "id": a.id,
            "number": a.ambulance_number,
            "type": a.vehicle_type,
            "status": a.status,
            "hospital_id": a.hospital_id,
            "lat": float(a.current_latitude or 0),
            "lon": float(a.current_longitude or 0),
            "is_active": a.is_active,
        }
        for a in ambulances
    ]


@router.post("/ambulances", status_code=201)
def create_ambulance(
    ambulance_number: str,
    vehicle_type: str = "basic",
    hospital_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(Ambulance).filter(Ambulance.ambulance_number == ambulance_number).first():
        raise HTTPException(status_code=400, detail="Ambulance number already exists")
    amb = Ambulance(ambulance_number=ambulance_number, vehicle_type=vehicle_type, hospital_id=hospital_id)
    db.add(amb)
    db.commit()
    db.refresh(amb)
    return amb


@router.get("/emergency/active")
def get_active_emergencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    emergencies = (
        db.query(EmergencyRequest)
        .filter(EmergencyRequest.status.notin_(["completed", "cancelled"]))
        .order_by(EmergencyRequest.created_at.desc())
        .all()
    )
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "emergency_type": e.emergency_type,
            "severity": e.severity,
            "status": e.status,
            "eta_minutes": e.eta_minutes,
            "assigned_ambulance_id": e.assigned_ambulance_id,
            "assigned_hospital_id": e.assigned_hospital_id,
            "created_at": e.created_at.isoformat(),
        }
        for e in emergencies
    ]
