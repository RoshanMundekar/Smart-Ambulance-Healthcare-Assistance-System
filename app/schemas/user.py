from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    patient = "patient"
    driver = "driver"
    doctor = "doctor"
    hospital_admin = "hospital_admin"
    system_admin = "system_admin"


class UserRegister(BaseModel):
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: str
    email: EmailStr
    password: str
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    chronic_conditions: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    role: UserRole = UserRole.patient

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if len(v.replace("+", "").replace("-", "").replace(" ", "")) < 10:
            raise ValueError("Invalid phone number")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    age: Optional[int]
    gender: Optional[str]
    phone: str
    email: str
    blood_group: Optional[str]
    medical_history: Optional[str]
    chronic_conditions: Optional[str]
    allergies: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    role: str
    is_active: bool
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    blood_group: Optional[str] = None
    medical_history: Optional[str] = None
    chronic_conditions: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float
