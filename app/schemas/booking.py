from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, time


class SymptomAnalysisRequest(BaseModel):
    symptoms: str
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: Optional[str] = None


class SymptomAnalysisResponse(BaseModel):
    symptoms_extracted: List[str]
    probable_conditions: List[dict]
    severity: str
    recommended_specialist: str
    confidence_score: float
    emergency_recommended: bool
    message: str


class BookingCreate(BaseModel):
    booking_type: str
    symptoms: Optional[str] = None
    symptom_severity: Optional[str] = "mild"
    hospital_id: Optional[int] = None
    doctor_id: Optional[int] = None
    ambulance_required: bool = False
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BookingResponse(BaseModel):
    id: int
    user_id: int
    booking_type: str
    symptoms: Optional[str]
    symptom_severity: Optional[str]
    ai_diagnosis: Optional[str]
    ai_confidence_score: Optional[float]
    hospital_id: Optional[int]
    doctor_id: Optional[int]
    ambulance_id: Optional[int]
    ambulance_required: bool
    booking_status: str
    appointment_date: Optional[date]
    appointment_time: Optional[time]
    notes: Optional[str]
    total_cost: Optional[float]
    payment_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AppointmentSlot(BaseModel):
    date: str
    time: str
    available: bool


class DoctorCard(BaseModel):
    id: int
    doctor_name: str
    specialization: str
    qualification: Optional[str]
    experience_years: int
    consultation_fee: float
    rating: float
    total_reviews: int
    is_available: bool
    hospital_name: str
    hospital_id: int
    available_slots: List[AppointmentSlot] = []

    class Config:
        from_attributes = True
