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


@router.post("/users", status_code=201)
def create_user(
    full_name: str,
    email: str,
    phone: str,
    password: str,
    role: str = "patient",
    age: Optional[int] = None,
    gender: Optional[str] = None,
    blood_group: Optional[str] = None,
    medical_history: Optional[str] = None,
    chronic_conditions: Optional[str] = None,
    hospital_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=get_password_hash(password),
        role=role,
        age=age,
        gender=gender,
        blood_group=blood_group,
        medical_history=medical_history,
        chronic_conditions=chronic_conditions,
        hospital_id=hospital_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


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


@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": f"User {user.full_name} activated"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account. Ask another system admin to do this."
        )
    if user.role == "system_admin":
        raise HTTPException(
            status_code=403,
            detail="System admin accounts cannot be deleted for security reasons. Deactivate instead."
        )
    db.delete(user)
    db.commit()
    return {"message": f"User {user.full_name} deleted"}



# ---- Hospitals ----

@router.post("/hospitals", status_code=201)
def create_hospital(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    hospital = Hospital(**payload)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.post("/hospitals/create-with-account", status_code=201)
def create_hospital_with_account(
    hospital_name: str,
    address: str,
    city: str,
    state: str,
    zip_code: str,
    phone: str,
    email: str,
    latitude: float,
    longitude: float,
    specializations: str,
    emergency_supported: bool,
    available_beds: int,
    icu_beds: int,
    admin_name: str,
    admin_email: str,
    admin_phone: str,
    admin_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.email == admin_email).first():
        raise HTTPException(status_code=400, detail="Admin email already registered")
    if db.query(User).filter(User.phone == admin_phone).first():
        raise HTTPException(status_code=400, detail="Admin phone already registered")

    # Create Hospital
    hospital = Hospital(
        hospital_name=hospital_name,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        phone=phone,
        email=email,
        latitude=latitude,
        longitude=longitude,
        specializations=specializations,
        emergency_supported=emergency_supported,
        available_beds=available_beds,
        icu_beds=icu_beds,
    )
    db.add(hospital)
    db.flush()

    # Create User (Hospital Admin role) linked to the newly created hospital
    user = User(
        full_name=admin_name,
        email=admin_email,
        phone=admin_phone,
        password_hash=get_password_hash(admin_password),
        role="hospital_admin",
        hospital_id=hospital.id,
    )
    db.add(user)
    db.commit()
    db.refresh(hospital)
    db.refresh(user)

    return {
        "hospital_id": hospital.id,
        "user_id": user.id,
        "hospital_name": hospital.hospital_name,
        "admin_email": user.email,
        "admin_name": user.full_name,
        "message": f"Hospital {hospital.hospital_name} and admin account created successfully.",
    }


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


@router.delete("/hospitals/{hospital_id}")
def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    hospital.is_active = False
    db.commit()
    return {"message": f"Hospital {hospital.hospital_name} deactivated"}


@router.get("/hospitals")
def list_hospitals_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospitals = db.query(Hospital).all()
    return [
        {
            "id": h.id,
            "hospital_name": h.hospital_name,
            "address": h.address,
            "city": h.city,
            "phone": h.phone,
            "email": h.email,
            "latitude": float(h.latitude),
            "longitude": float(h.longitude),
            "specializations": h.specializations,
            "emergency_supported": h.emergency_supported,
            "icu_beds": h.icu_beds,
            "total_beds": h.total_beds,
            "available_beds": h.available_beds,
            "rating": float(h.rating or 0),
            "is_active": h.is_active,
        }
        for h in hospitals
    ]


# ---- Doctors ----

@router.get("/doctors")
def list_doctors_admin(
    hospital_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(Doctor, Hospital).join(Hospital, Doctor.hospital_id == Hospital.id)
    if hospital_id:
        query = query.filter(Doctor.hospital_id == hospital_id)
    results = query.all()
    return [
        {
            "id": d.id,
            "doctor_name": d.doctor_name,
            "specialization": d.specialization,
            "qualification": d.qualification,
            "experience_years": d.experience_years,
            "consultation_fee": float(d.consultation_fee or 0),
            "rating": float(d.rating or 0),
            "is_available": d.is_available,
            "is_active": d.is_active,
            "hospital_id": d.hospital_id,
            "hospital_name": h.hospital_name,
        }
        for d, h in results
    ]


@router.post("/doctors", status_code=201)
def create_doctor(
    hospital_id: int,
    doctor_name: str,
    specialization: str,
    qualification: Optional[str] = None,
    experience_years: int = 0,
    consultation_fee: float = 0.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    doctor = Doctor(
        hospital_id=hospital_id,
        doctor_name=doctor_name,
        specialization=specialization,
        qualification=qualification,
        experience_years=experience_years,
        consultation_fee=consultation_fee,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/doctors/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.is_active = False
    db.commit()
    return {"message": f"Doctor {doctor.doctor_name} deactivated"}


# ---- Drivers ----

@router.get("/drivers")
def list_drivers_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    drivers = db.query(Driver).all()
    result = []
    for d in drivers:
        ambulance = db.query(Ambulance).filter(Ambulance.id == d.ambulance_id).first() if d.ambulance_id else None
        hospital = db.query(Hospital).filter(Hospital.id == ambulance.hospital_id).first() if ambulance and ambulance.hospital_id else None
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
            "ambulance_id": d.ambulance_id,
            "ambulance_number": ambulance.ambulance_number if ambulance else None,
            "ambulance_status": ambulance.status if ambulance else None,
            "ambulance_type": ambulance.vehicle_type if ambulance else None,
            "hospital_name": hospital.hospital_name if hospital else None,
            "hospital_id": hospital.id if hospital else None,
        })
    return result


@router.post("/drivers", status_code=201)
def create_driver(
    user_id: int,
    driver_name: str,
    phone: str,
    license_number: str,
    experience_years: int = 0,
    ambulance_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(Driver).filter(Driver.user_id == user_id).first():
        raise HTTPException(status_code=400, detail="Driver profile already exists for this user")
    # Update user role to driver
    user.role = "driver"
    driver = Driver(
        user_id=user_id,
        ambulance_id=ambulance_id,
        driver_name=driver_name,
        phone=phone,
        license_number=license_number,
        experience_years=experience_years,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.post("/drivers/create-with-account", status_code=201)
def create_driver_with_account(
    full_name: str,
    email: str,
    phone: str,
    password: str,
    license_number: str,
    experience_years: int = 0,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    ambulance_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    One-shot: create a User account (role=driver) + Driver profile together.
    The driver can immediately log in with email + password.
    """
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # 1. Create the user account
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=get_password_hash(password),
        role="driver",
        age=age,
        gender=gender,
    )
    db.add(user)
    db.flush()   # get user.id without committing

    # 2. Create the driver profile linked to that user
    driver = Driver(
        user_id=user.id,
        ambulance_id=ambulance_id,
        driver_name=full_name,
        phone=phone,
        license_number=license_number,
        experience_years=experience_years,
    )
    db.add(driver)
    db.commit()
    db.refresh(driver)

    return {
        "driver_id": driver.id,
        "user_id": user.id,
        "driver_name": driver.driver_name,
        "email": user.email,
        "phone": user.phone,
        "message": "Driver account and profile created. They can now log in with the provided credentials.",
    }


@router.patch("/drivers/{driver_id}/toggle-active")
def toggle_driver_active(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    driver.is_active = not driver.is_active
    db.commit()
    return {"message": f"Driver {driver.driver_name} {'activated' if driver.is_active else 'deactivated'}", "is_active": driver.is_active}


@router.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(driver)
    db.commit()
    return {"message": f"Driver {driver.driver_name} removed"}


# ---- Ambulances ----

@router.get("/ambulances")
def list_ambulances(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    ambulances = db.query(Ambulance).all()
    result = []
    for a in ambulances:
        driver = db.query(Driver).filter(Driver.ambulance_id == a.id, Driver.is_active == True).first()
        hospital = db.query(Hospital).filter(Hospital.id == a.hospital_id).first() if a.hospital_id else None
        # Get active emergency for this driver
        active_em = None
        if driver:
            from app.models.booking import EmergencyRequest
            active_em = db.query(EmergencyRequest).filter(
                EmergencyRequest.assigned_driver_id == driver.id,
                EmergencyRequest.status.notin_(["completed", "cancelled"]),
            ).first()
        result.append({
            "id": a.id,
            "number": a.ambulance_number,
            "type": a.vehicle_type,
            "status": a.status,
            "hospital_id": a.hospital_id,
            "hospital_name": hospital.hospital_name if hospital else None,
            "hospital_city": hospital.city if hospital else None,
            "lat": float(a.current_latitude or 0),
            "lon": float(a.current_longitude or 0),
            "is_active": a.is_active,
            "driver_id": driver.id if driver else None,
            "driver_name": driver.driver_name if driver else None,
            "driver_phone": driver.phone if driver else None,
            "driver_available": driver.is_available if driver else None,
            "driver_rating": float(driver.performance_rating or 0) if driver else None,
            "active_emergency_id": active_em.id if active_em else None,
            "active_emergency_status": active_em.status if active_em else None,
            "active_emergency_type": active_em.emergency_type if active_em else None,
        })
    return result


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
