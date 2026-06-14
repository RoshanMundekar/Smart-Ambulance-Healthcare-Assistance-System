from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.models.user import User
from app.models.hospital import Hospital
from app.models.doctor import Doctor
from app.models.booking import EmergencyRequest, Booking
from app.auth.rbac import require_hospital_admin
from app.auth.jwt import get_current_active_user

router = APIRouter(prefix="/hospital", tags=["Hospital"])


@router.get("/dashboard")
def hospital_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hospital_admin),
):
    # Find hospital managed by this admin
    hospital = None
    if current_user.hospital_id:
        hospital = db.query(Hospital).filter(Hospital.id == current_user.hospital_id, Hospital.is_active == True).first()
    if not hospital:
        # Fallback to the first active hospital for demo or backward compatibility
        hospital = db.query(Hospital).filter(Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    # Active emergencies incoming
    active_emergencies = (
        db.query(EmergencyRequest)
        .filter(
            EmergencyRequest.assigned_hospital_id == hospital.id,
            EmergencyRequest.status.notin_(["completed", "cancelled"]),
        )
        .order_by(EmergencyRequest.created_at.desc())
        .all()
    )

    emergencies_data = []
    for em in active_emergencies:
        patient = db.query(User).filter(User.id == em.user_id).first()
        emergencies_data.append({
            "id": em.id,
            "status": em.status,
            "severity": em.severity,
            "emergency_type": em.emergency_type,
            "eta_minutes": em.eta_minutes,
            "ai_specialist": em.ai_specialist_recommendation,
            "patient": {
                "id": patient.id if patient else None,
                "name": patient.full_name if patient else "Unknown",
                "age": patient.age if patient else None,
                "blood_group": patient.blood_group if patient else None,
                "medical_history": patient.medical_history if patient else None,
                "chronic_conditions": patient.chronic_conditions if patient else None,
                "allergies": patient.allergies if patient else None,
                "phone": patient.phone if patient else None,
            } if patient else None,
            "created_at": em.created_at.isoformat(),
        })

    # Today's appointments
    from datetime import date
    today_bookings = (
        db.query(Booking)
        .filter(
            Booking.hospital_id == hospital.id,
            Booking.appointment_date == date.today(),
            Booking.booking_status.notin_(["cancelled"]),
        )
        .count()
    )

    # Doctors on duty
    available_doctors = db.query(Doctor).filter(
        Doctor.hospital_id == hospital.id,
        Doctor.is_available == True,
    ).count()

    return {
        "hospital": {
            "id": hospital.id,
            "name": hospital.hospital_name,
            "address": hospital.address,
            "available_beds": hospital.available_beds,
            "icu_beds": hospital.icu_beds,
            "rating": float(hospital.rating or 0),
        },
        "active_emergencies": emergencies_data,
        "stats": {
            "today_appointments": today_bookings,
            "available_doctors": available_doctors,
            "active_emergencies": len(emergencies_data),
        },
    }


@router.get("/{hospital_id}/doctors")
def get_hospital_doctors(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    doctors = db.query(Doctor).filter(Doctor.hospital_id == hospital_id, Doctor.is_active == True).all()
    return [
        {
            "id": d.id,
            "name": d.doctor_name,
            "specialization": d.specialization,
            "experience_years": d.experience_years,
            "rating": float(d.rating or 0),
            "consultation_fee": float(d.consultation_fee or 0),
            "is_available": d.is_available,
            "availability": d.availability,
        }
        for d in doctors
    ]


@router.patch("/{hospital_id}/beds")
def update_bed_count(
    hospital_id: int,
    available_beds: int,
    icu_beds: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hospital_admin),
):
    if current_user.role != "system_admin" and current_user.hospital_id != hospital_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this hospital's bed count.")
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    hospital.available_beds = available_beds
    if icu_beds is not None:
        hospital.icu_beds = icu_beds
    db.commit()
    return {"message": "Bed count updated", "available_beds": available_beds}


@router.get("/drivers")
def get_hospital_drivers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hospital_admin),
):
    """Get all drivers linked to ambulances assigned to the managed hospital."""
    from app.models.ambulance import Ambulance, Driver as DriverModel
    hospital = None
    if current_user.hospital_id:
        hospital = db.query(Hospital).filter(Hospital.id == current_user.hospital_id, Hospital.is_active == True).first()
    if not hospital:
        # Fallback to first active hospital
        hospital = db.query(Hospital).filter(Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    # Get all ambulances for this hospital
    ambulances = db.query(Ambulance).filter(Ambulance.hospital_id == hospital.id).all()
    ambulance_map = {a.id: a for a in ambulances}

    # Get drivers linked to those ambulances
    ambulance_ids = [a.id for a in ambulances]
    drivers = db.query(DriverModel).filter(DriverModel.ambulance_id.in_(ambulance_ids)).all() if ambulance_ids else []

    result = []
    for d in drivers:
        amb = ambulance_map.get(d.ambulance_id)
        # Check if driver has an active emergency
        active_em = db.query(EmergencyRequest).filter(
            EmergencyRequest.assigned_driver_id == d.id,
            EmergencyRequest.status.notin_(["completed", "cancelled"]),
        ).first()
        result.append({
            "id": d.id,
            "driver_name": d.driver_name,
            "phone": d.phone,
            "license_number": d.license_number,
            "experience_years": d.experience_years,
            "performance_rating": float(d.performance_rating or 0),
            "total_trips": d.total_trips,
            "is_available": d.is_available,
            "is_active": d.is_active,
            "current_latitude": float(d.current_latitude or 0),
            "current_longitude": float(d.current_longitude or 0),
            "last_location_update": d.last_location_update.isoformat() if d.last_location_update else None,
            "ambulance_number": amb.ambulance_number if amb else None,
            "ambulance_status": amb.status if amb else None,
            "ambulance_type": amb.vehicle_type if amb else None,
            "active_emergency_id": active_em.id if active_em else None,
            "active_emergency_type": active_em.emergency_type if active_em else None,
            "active_emergency_status": active_em.status if active_em else None,
        })
    return result


@router.get("/all")
def list_hospitals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    return [
        {
            "id": h.id,
            "hospital_name": h.hospital_name,
            "address": h.address,
            "city": h.city,
            "phone": h.phone,
            "latitude": float(h.latitude),
            "longitude": float(h.longitude),
            "specializations": h.specializations,
            "emergency_supported": h.emergency_supported,
            "rating": float(h.rating or 0),
            "available_beds": h.available_beds,
        }
        for h in hospitals
    ]
