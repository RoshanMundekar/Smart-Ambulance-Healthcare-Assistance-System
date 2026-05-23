from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmergencyRequest(BaseModel):
    latitude: float
    longitude: float
    emergency_type: str = "other"
    symptoms: Optional[str] = None
    address: Optional[str] = None


class EmergencyResponse(BaseModel):
    id: int
    user_id: int
    emergency_type: str
    severity: str
    patient_latitude: float
    patient_longitude: float
    patient_address: Optional[str]
    assigned_ambulance_id: Optional[int]
    assigned_hospital_id: Optional[int]
    assigned_driver_id: Optional[int]
    ai_specialist_recommendation: Optional[str]
    eta_minutes: Optional[int]
    route_distance_km: Optional[float]
    hospital_notified: bool
    driver_notified: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class EmergencyStatusUpdate(BaseModel):
    status: str
    eta_minutes: Optional[int] = None
    notes: Optional[str] = None


class AmbulanceLocation(BaseModel):
    ambulance_id: int
    latitude: float
    longitude: float
    speed: Optional[float] = None
    heading: Optional[int] = None


class RouteInfo(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    distance_km: float
    duration_minutes: int
    polyline: Optional[str] = None


class HospitalRecommendation(BaseModel):
    hospital_id: int
    hospital_name: str
    distance_km: float
    eta_minutes: int
    available_beds: int
    rating: float
    emergency_supported: bool
    specializations: List[str]
    score: float


class DoctorRecommendation(BaseModel):
    doctor_id: int
    doctor_name: str
    specialization: str
    hospital_name: str
    experience_years: int
    rating: float
    consultation_fee: float
    is_available: bool
    score: float
