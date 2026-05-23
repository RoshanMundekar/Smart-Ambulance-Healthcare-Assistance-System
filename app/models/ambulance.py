from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, Text, Enum, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ambulance_number = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(Enum("basic", "advanced", "icu", "neonatal"), default="basic")
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    current_latitude = Column(DECIMAL(10, 8))
    current_longitude = Column(DECIMAL(11, 8))
    status = Column(
        Enum("available", "en_route", "at_scene", "transporting", "maintenance", "offline"),
        default="available",
        index=True,
    )
    last_location_update = Column(DateTime)
    equipment = Column(Text)  # JSON string, MySQL 5.0 has no JSON type
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    hospital = relationship("Hospital", back_populates="ambulances")
    driver = relationship("Driver", back_populates="ambulance", uselist=False)
    bookings = relationship("Booking", back_populates="ambulance")
    emergency_requests = relationship("EmergencyRequest", back_populates="assigned_ambulance")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    ambulance_id = Column(Integer, ForeignKey("ambulances.id", ondelete="SET NULL"), nullable=True)
    driver_name = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    license_number = Column(String(100), nullable=False)
    experience_years = Column(Integer, default=0)
    performance_rating = Column(DECIMAL(3, 2), default=5.00)
    total_trips = Column(Integer, default=0)
    is_available = Column(Boolean, default=True, index=True)
    current_latitude = Column(DECIMAL(10, 8))
    current_longitude = Column(DECIMAL(11, 8))
    last_location_update = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="driver_profile")
    ambulance = relationship("Ambulance", back_populates="driver")
    emergency_requests = relationship("EmergencyRequest", back_populates="assigned_driver")
