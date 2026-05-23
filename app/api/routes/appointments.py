from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time

from app.database.connection import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.hospital import Hospital
from app.models.ambulance import Ambulance, Driver
from app.models.booking import Booking, Appointment
from app.schemas.booking import (
    SymptomAnalysisRequest, SymptomAnalysisResponse,
    BookingCreate, BookingResponse, DoctorCard
)
from app.auth.jwt import get_current_active_user
from app.ai.symptom_analyzer import symptom_analyzer
from app.ai.hospital_recommender import hospital_recommender, ambulance_allocator
from app.ai.specialist_recommender import specialist_recommender
from app.utils.notifications import notify_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/analyze-symptoms", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    payload: SymptomAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    result = symptom_analyzer.analyze(
        symptoms_text=payload.symptoms,
        age=payload.age or current_user.age,
        gender=payload.gender or current_user.gender,
        medical_history=payload.medical_history or current_user.medical_history,
    )
    return SymptomAnalysisResponse(**result)


@router.get("/doctors", response_model=List[DoctorCard])
def get_available_doctors(
    specialization: Optional[str] = Query(None),
    hospital_id: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Doctor, Hospital).join(Hospital, Doctor.hospital_id == Hospital.id).filter(
        Doctor.is_active == True, Hospital.is_active == True
    )

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if hospital_id:
        query = query.filter(Doctor.hospital_id == hospital_id)
    if min_rating:
        query = query.filter(Doctor.rating >= min_rating)

    results = query.all()
    doctors = []
    for doctor, hospital in results:
        doctors.append(
            DoctorCard(
                id=doctor.id,
                doctor_name=doctor.doctor_name,
                specialization=doctor.specialization,
                qualification=doctor.qualification,
                experience_years=doctor.experience_years,
                consultation_fee=float(doctor.consultation_fee or 0),
                rating=float(doctor.rating or 0),
                total_reviews=doctor.total_reviews,
                is_available=doctor.is_available,
                hospital_name=hospital.hospital_name,
                hospital_id=hospital.id,
            )
        )
    return doctors


@router.get("/hospitals")
def get_hospitals(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    specialization: Optional[str] = Query(None),
    emergency_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Hospital).filter(Hospital.is_active == True)
    if emergency_only:
        query = query.filter(Hospital.emergency_supported == True)
    hospitals = query.all()

    if lat and lon:
        recommendations = hospital_recommender.recommend(
            hospitals=hospitals,
            patient_lat=lat,
            patient_lon=lon,
            required_specialization=specialization,
            emergency=emergency_only,
        )
        return recommendations

    return [
        {
            "id": h.id,
            "hospital_name": h.hospital_name,
            "address": h.address,
            "city": h.city,
            "specializations": h.specializations,
            "emergency_supported": h.emergency_supported,
            "rating": float(h.rating or 0),
            "available_beds": h.available_beds,
            "phone": h.phone,
            "latitude": float(h.latitude),
            "longitude": float(h.longitude),
        }
        for h in hospitals
    ]


@router.post("/book", response_model=BookingResponse, status_code=201)
async def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Run AI analysis if symptoms provided
    ai_diagnosis = None
    ai_score = None
    if payload.symptoms:
        analysis = symptom_analyzer.analyze(
            symptoms_text=payload.symptoms,
            age=current_user.age,
            gender=current_user.gender,
            medical_history=current_user.medical_history,
        )
        ai_diagnosis = analysis.get("probable_conditions", [{}])[0].get("condition") if analysis.get("probable_conditions") else None
        ai_score = analysis.get("confidence_score")

    # Calculate cost
    total_cost = None
    if payload.doctor_id:
        doctor = db.query(Doctor).filter(Doctor.id == payload.doctor_id).first()
        if doctor:
            total_cost = float(doctor.consultation_fee or 0)

    # Handle ambulance allocation
    ambulance_id = None
    if payload.ambulance_required and payload.latitude and payload.longitude:
        ambulances = db.query(Ambulance).filter(Ambulance.is_active == True).all()
        drivers = db.query(Driver).filter(Driver.is_active == True).all()
        allocation = ambulance_allocator.allocate(
            ambulances=ambulances,
            drivers=drivers,
            patient_lat=payload.latitude,
            patient_lon=payload.longitude,
        )
        if allocation:
            ambulance_id = allocation["ambulance_id"]
            amb = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
            if amb:
                amb.status = "en_route"

    booking = Booking(
        user_id=current_user.id,
        booking_type=payload.booking_type,
        symptoms=payload.symptoms,
        symptom_severity=payload.symptom_severity,
        ai_diagnosis=ai_diagnosis,
        ai_confidence_score=ai_score,
        hospital_id=payload.hospital_id,
        doctor_id=payload.doctor_id,
        ambulance_id=ambulance_id,
        ambulance_required=payload.ambulance_required,
        booking_status="confirmed" if payload.doctor_id else "pending",
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        notes=payload.notes,
        total_cost=total_cost,
    )
    db.add(booking)
    db.flush()

    # Create appointment record if doctor is booked
    if payload.doctor_id and payload.appointment_date and payload.appointment_time:
        appt = Appointment(
            booking_id=booking.id,
            patient_id=current_user.id,
            doctor_id=payload.doctor_id,
            appointment_date=payload.appointment_date,
            appointment_time=payload.appointment_time,
            status="confirmed",
        )
        db.add(appt)

    db.commit()
    db.refresh(booking)

    await notify_user(
        db=db,
        user_id=current_user.id,
        title="Booking Confirmed",
        message=f"Your {payload.booking_type} booking has been confirmed.",
        notification_type="booking",
        related_id=booking.id,
        related_type="booking",
    )

    return booking


@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    if status:
        query = query.filter(Booking.booking_status == status)
    return query.order_by(Booking.created_at.desc()).all()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id and current_user.role not in ("system_admin", "doctor", "hospital_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    return booking


@router.patch("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if booking.booking_status in ("completed", "cancelled"):
        raise HTTPException(status_code=400, detail="Cannot cancel a completed or already cancelled booking")

    booking.booking_status = "cancelled"
    if booking.ambulance_id:
        amb = db.query(Ambulance).filter(Ambulance.id == booking.ambulance_id).first()
        if amb:
            amb.status = "available"

    db.commit()
    return {"message": "Booking cancelled successfully"}
