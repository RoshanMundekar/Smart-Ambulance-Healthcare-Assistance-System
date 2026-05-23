"""
Database setup script — creates all tables and inserts seed data.
Run once: python setup_db.py
"""
import sys
import json
import bcrypt
from loguru import logger
from app.database.connection import engine, Base, SessionLocal
import app.models  # noqa — registers all models

def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def setup():
    logger.info("Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Table creation failed: {e}")
        sys.exit(1)

    db = SessionLocal()
    try:
        from app.models.user import User
        from app.models.hospital import Hospital
        from app.models.doctor import Doctor
        from app.models.ambulance import Ambulance, Driver

        # Skip if already seeded
        if db.query(User).count() > 0:
            logger.info("Seed data already present — skipping.")
            return

        logger.info("Inserting seed data...")

        # ── Hospitals ──────────────────────────────────────────
        hospitals = [
            Hospital(hospital_name="City General Hospital", address="123 Main Street, Downtown",
                     city="Mumbai", state="Maharashtra", zip_code="400001",
                     phone="+91-22-12345678", email="info@citygeneral.com",
                     latitude=19.0760, longitude=72.8777,
                     specializations='["cardiology","neurology","orthopedics","emergency","surgery"]',
                     emergency_supported=True, icu_beds=20, total_beds=200, available_beds=45,
                     rating=4.5, license_number="MH-HOSP-001"),
            Hospital(hospital_name="Apollo Medical Center", address="456 Health Avenue, Andheri",
                     city="Mumbai", state="Maharashtra", zip_code="400053",
                     phone="+91-22-87654321", email="care@apollo.com",
                     latitude=19.1136, longitude=72.8697,
                     specializations='["oncology","cardiology","pediatrics","neurology","transplant"]',
                     emergency_supported=True, icu_beds=30, total_beds=350, available_beds=80,
                     rating=4.8, license_number="MH-HOSP-002"),
            Hospital(hospital_name="Metro Emergency Hospital", address="789 Emergency Road, Bandra",
                     city="Mumbai", state="Maharashtra", zip_code="400050",
                     phone="+91-22-11223344", email="emergency@metro.com",
                     latitude=19.0596, longitude=72.8295,
                     specializations='["emergency","trauma","surgery","orthopedics","burns"]',
                     emergency_supported=True, icu_beds=15, total_beds=120, available_beds=30,
                     rating=4.3, license_number="MH-HOSP-003"),
            Hospital(hospital_name="Sunshine Children Hospital", address="321 Kids Lane, Dadar",
                     city="Mumbai", state="Maharashtra", zip_code="400014",
                     phone="+91-22-44556677", email="info@sunshine.com",
                     latitude=19.0178, longitude=72.8478,
                     specializations='["pediatrics","neonatology","pediatric_surgery"]',
                     emergency_supported=False, icu_beds=10, total_beds=100, available_beds=25,
                     rating=4.6, license_number="MH-HOSP-004"),
            Hospital(hospital_name="Cardiac Care Institute", address="654 Heart Boulevard, Powai",
                     city="Mumbai", state="Maharashtra", zip_code="400076",
                     phone="+91-22-99887766", email="heart@cardiac.com",
                     latitude=19.1176, longitude=72.9060,
                     specializations='["cardiology","cardiac_surgery","electrophysiology"]',
                     emergency_supported=True, icu_beds=25, total_beds=180, available_beds=40,
                     rating=4.7, license_number="MH-HOSP-005"),
        ]
        for h in hospitals:
            db.add(h)
        db.flush()

        pw = hash_pw("password123")

        # ── Users ──────────────────────────────────────────────
        users = [
            User(full_name="Admin User",        age=35, gender="male",   phone="+91-9999999999", email="admin@system.com",              password_hash=pw, blood_group="O+", role="system_admin"),
            User(full_name="Dr. Rajesh Kumar",  age=45, gender="male",   phone="+91-9876543210", email="dr.rajesh@citygeneral.com",      password_hash=pw, blood_group="A+", role="doctor"),
            User(full_name="Dr. Priya Sharma",  age=38, gender="female", phone="+91-9876543211", email="dr.priya@apollo.com",            password_hash=pw, blood_group="B+", role="doctor"),
            User(full_name="Dr. Amit Patel",    age=52, gender="male",   phone="+91-9876543212", email="dr.amit@metro.com",             password_hash=pw, blood_group="O-", role="doctor"),
            User(full_name="Ravi Singh",        age=30, gender="male",   phone="+91-9876543213", email="ravi.driver@ambulance.com",      password_hash=pw, blood_group="B+", role="driver"),
            User(full_name="Suresh Kumar",      age=28, gender="male",   phone="+91-9876543214", email="suresh.driver@ambulance.com",    password_hash=pw, blood_group="A-", role="driver"),
            User(full_name="John Patient",      age=35, gender="male",   phone="+91-9876543215", email="john@patient.com",               password_hash=pw, blood_group="O+", role="patient",
                 medical_history="Hypertension diagnosed 2020", chronic_conditions="Hypertension"),
            User(full_name="Sarah Patient",     age=28, gender="female", phone="+91-9876543216", email="sarah@patient.com",              password_hash=pw, blood_group="AB+", role="patient",
                 medical_history="Diabetes Type 2", chronic_conditions="Diabetes"),
            User(full_name="Hospital Admin",    age=40, gender="female", phone="+91-9876543217", email="admin@citygeneral.com",           password_hash=pw, blood_group="O+", role="hospital_admin"),
        ]
        for u in users:
            db.add(u)
        db.flush()

        # ── Doctors ────────────────────────────────────────────
        avail_weekdays = '{"monday":["09:00","17:00"],"tuesday":["09:00","17:00"],"thursday":["09:00","17:00"],"friday":["09:00","17:00"]}'
        doctors = [
            Doctor(hospital_id=1, user_id=2,  doctor_name="Dr. Rajesh Kumar",  specialization="Cardiologist",       qualification="MBBS, MD (Cardiology), DM", experience_years=20, consultation_fee=1500, availability=avail_weekdays, rating=4.8),
            Doctor(hospital_id=2, user_id=3,  doctor_name="Dr. Priya Sharma",  specialization="Neurologist",        qualification="MBBS, MD (Neurology), DM",  experience_years=15, consultation_fee=2000, availability=avail_weekdays, rating=4.9),
            Doctor(hospital_id=3, user_id=4,  doctor_name="Dr. Amit Patel",    specialization="Emergency Medicine", qualification="MBBS, MD (Emergency)",       experience_years=25, consultation_fee=800,  availability='{"monday":["00:00","23:59"]}', rating=4.7),
            Doctor(hospital_id=1, user_id=None, doctor_name="Dr. Sanjay Verma",  specialization="Orthopedist",      qualification="MBBS, MS (Orthopedics)",    experience_years=18, consultation_fee=1200, availability=avail_weekdays, rating=4.5),
            Doctor(hospital_id=2, user_id=None, doctor_name="Dr. Meena Nair",    specialization="Pulmonologist",    qualification="MBBS, MD (Pulmonology)",    experience_years=12, consultation_fee=1800, availability=avail_weekdays, rating=4.6),
            Doctor(hospital_id=4, user_id=None, doctor_name="Dr. Ananya Roy",    specialization="Pediatrician",     qualification="MBBS, MD (Pediatrics), DCH",experience_years=10, consultation_fee=1000, availability=avail_weekdays, rating=4.9),
            Doctor(hospital_id=5, user_id=None, doctor_name="Dr. Vikram Mehta",  specialization="Cardiac Surgeon",  qualification="MBBS, M.Ch (Cardiac Surgery)",experience_years=22, consultation_fee=3000, availability=avail_weekdays, rating=4.9),
        ]
        for d in doctors:
            db.add(d)
        db.flush()

        # ── Ambulances ─────────────────────────────────────────
        ambulances = [
            Ambulance(ambulance_number="AMB-001", vehicle_type="advanced", hospital_id=1, current_latitude=19.0800, current_longitude=72.8800, status="available", equipment='["defibrillator","oxygen","stretcher","iv_equipment","cardiac_monitor"]'),
            Ambulance(ambulance_number="AMB-002", vehicle_type="basic",    hospital_id=1, current_latitude=19.0750, current_longitude=72.8750, status="available", equipment='["oxygen","stretcher","first_aid"]'),
            Ambulance(ambulance_number="AMB-003", vehicle_type="icu",      hospital_id=2, current_latitude=19.1150, current_longitude=72.8720, status="available", equipment='["defibrillator","ventilator","oxygen","stretcher","cardiac_monitor"]'),
            Ambulance(ambulance_number="AMB-004", vehicle_type="advanced", hospital_id=3, current_latitude=19.0610, current_longitude=72.8310, status="available", equipment='["defibrillator","oxygen","stretcher","iv_equipment"]'),
            Ambulance(ambulance_number="AMB-005", vehicle_type="neonatal", hospital_id=4, current_latitude=19.0200, current_longitude=72.8500, status="available", equipment='["incubator","oxygen","monitoring_equipment"]'),
            Ambulance(ambulance_number="AMB-006", vehicle_type="basic",    hospital_id=5, current_latitude=19.1200, current_longitude=72.9080, status="available", equipment='["oxygen","stretcher","first_aid"]'),
        ]
        for a in ambulances:
            db.add(a)
        db.flush()

        # ── Drivers ────────────────────────────────────────────
        drivers = [
            Driver(user_id=5, ambulance_id=1, driver_name="Ravi Singh",   phone="+91-9876543213", license_number="MH-DL-123456", experience_years=8,  performance_rating=4.8, is_available=True, current_latitude=19.0800, current_longitude=72.8800),
            Driver(user_id=6, ambulance_id=3, driver_name="Suresh Kumar", phone="+91-9876543214", license_number="MH-DL-789012", experience_years=5,  performance_rating=4.6, is_available=True, current_latitude=19.1150, current_longitude=72.8720),
        ]
        for d in drivers:
            db.add(d)

        db.commit()
        logger.info("✅ Seed data inserted successfully.")
        logger.info("─" * 50)
        logger.info("Demo accounts (password: password123):")
        logger.info("  Admin:          admin@system.com")
        logger.info("  Patient:        john@patient.com")
        logger.info("  Driver:         ravi.driver@ambulance.com")
        logger.info("  Hospital Admin: admin@citygeneral.com")
        logger.info("─" * 50)

    except Exception as e:
        db.rollback()
        logger.error(f"Seed data error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    setup()
