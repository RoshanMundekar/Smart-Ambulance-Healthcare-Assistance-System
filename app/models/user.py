from sqlalchemy import Column, Integer, String, Boolean, Text, DECIMAL, Enum, TIMESTAMP, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum


class UserRole(str, enum.Enum):
    patient = "patient"
    driver = "driver"
    doctor = "doctor"
    hospital_admin = "hospital_admin"
    system_admin = "system_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    age = Column(Integer)
    gender = Column(Enum("male", "female", "other"))
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    blood_group = Column(Enum("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"))
    medical_history = Column(Text)
    chronic_conditions = Column(Text)
    allergies = Column(Text)
    emergency_contact_name = Column(String(150))
    emergency_contact_phone = Column(String(20))
    role = Column(Enum("patient", "driver", "doctor", "hospital_admin", "system_admin"), default="patient")
    is_active = Column(Boolean, default=True)
    profile_image = Column(String(500))
    address = Column(Text)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    bookings = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id")
    notifications = relationship("Notification", back_populates="user")
    driver_profile = relationship("Driver", back_populates="user", uselist=False)
    emergency_requests = relationship("EmergencyRequest", back_populates="user")
