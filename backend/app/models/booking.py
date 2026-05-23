from sqlalchemy import Column, Integer, String, Boolean, Text, DECIMAL, Enum, TIMESTAMP, DateTime, ForeignKey, Date, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    booking_type = Column(Enum("emergency", "consultation", "follow_up"), nullable=False, index=True)
    symptoms = Column(Text)
    symptom_severity = Column(Enum("mild", "moderate", "severe", "critical"), default="mild")
    ai_diagnosis = Column(Text)
    ai_confidence_score = Column(DECIMAL(5, 4))
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    ambulance_id = Column(Integer, ForeignKey("ambulances.id", ondelete="SET NULL"), nullable=True)
    ambulance_required = Column(Boolean, default=False)
    booking_status = Column(
        Enum("pending", "confirmed", "in_progress", "completed", "cancelled"),
        default="pending",
        index=True,
    )
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    notes = Column(Text)
    total_cost = Column(DECIMAL(10, 2))
    payment_status = Column(Enum("pending", "paid", "refunded"), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    hospital = relationship("Hospital", back_populates="bookings")
    doctor = relationship("Doctor", back_populates="bookings")
    ambulance = relationship("Ambulance", back_populates="bookings")
    appointment = relationship("Appointment", back_populates="booking", uselist=False)


class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    emergency_type = Column(
        Enum("cardiac", "accident", "stroke", "respiratory", "other"), default="other"
    )
    severity = Column(Enum("low", "medium", "high", "critical"), default="high", index=True)
    patient_latitude = Column(DECIMAL(10, 8), nullable=False)
    patient_longitude = Column(DECIMAL(11, 8), nullable=False)
    patient_address = Column(Text)
    assigned_ambulance_id = Column(Integer, ForeignKey("ambulances.id", ondelete="SET NULL"), nullable=True)
    assigned_hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="SET NULL"), nullable=True)
    assigned_driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    ai_specialist_recommendation = Column(String(200))
    eta_minutes = Column(Integer)
    route_distance_km = Column(DECIMAL(8, 2))
    hospital_notified = Column(Boolean, default=False)
    driver_notified = Column(Boolean, default=False)
    status = Column(
        Enum("requested", "ambulance_assigned", "en_route", "at_scene", "transporting", "arrived", "completed", "cancelled"),
        default="requested",
        index=True,
    )
    response_time_minutes = Column(Integer)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="emergency_requests")
    assigned_ambulance = relationship("Ambulance", back_populates="emergency_requests")
    assigned_hospital = relationship("Hospital")
    assigned_driver = relationship("Driver", back_populates="emergency_requests")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(
        Enum("scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"),
        default="scheduled",
    )
    consultation_notes = Column(Text)
    prescription = Column(Text)
    follow_up_date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    booking = relationship("Booking", back_populates="appointment")
    doctor = relationship("Doctor", back_populates="appointments")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(
        Enum("emergency", "booking", "appointment", "system", "alert"), default="system"
    )
    is_read = Column(Boolean, default=False)
    related_id = Column(Integer)
    related_type = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="notifications")
