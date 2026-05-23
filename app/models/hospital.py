from sqlalchemy import Column, Integer, String, Boolean, Text, DECIMAL, TIMESTAMP, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hospital_name = Column(String(200), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    phone = Column(String(20))
    email = Column(String(255))
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    specializations = Column(Text)  # stored as JSON string, MySQL 5.0 has no JSON type
    emergency_supported = Column(Boolean, default=False)
    icu_beds = Column(Integer, default=0)
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), default=0.00)
    total_reviews = Column(Integer, default=0)
    license_number = Column(String(100))
    accreditation = Column(String(100))
    website = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    doctors = relationship("Doctor", back_populates="hospital")
    ambulances = relationship("Ambulance", back_populates="hospital")
    bookings = relationship("Booking", back_populates="hospital")
