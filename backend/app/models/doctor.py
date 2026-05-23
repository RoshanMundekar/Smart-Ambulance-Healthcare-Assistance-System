from sqlalchemy import Column, Integer, String, Boolean, Text, DECIMAL, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    doctor_name = Column(String(150), nullable=False)
    specialization = Column(String(150), nullable=False, index=True)
    sub_specialization = Column(String(150))
    qualification = Column(String(300))
    license_number = Column(String(100))
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(DECIMAL(10, 2), default=0.00)
    availability = Column(Text)  # JSON string, MySQL 5.0 has no JSON type
    rating = Column(DECIMAL(3, 2), default=0.00)
    total_reviews = Column(Integer, default=0)
    bio = Column(Text)
    profile_image = Column(String(500))
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    hospital = relationship("Hospital", back_populates="doctors")
    bookings = relationship("Booking", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")
