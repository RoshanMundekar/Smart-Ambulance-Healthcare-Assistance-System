-- ============================================================
-- SEED DATA for Smart Ambulance & Healthcare System
-- ============================================================
USE smart_ambulance_db;

-- ============================================================
-- HOSPITALS
-- ============================================================
INSERT INTO hospitals (hospital_name, address, city, state, zip_code, phone, email, latitude, longitude, specializations, emergency_supported, icu_beds, total_beds, available_beds, rating, license_number) VALUES
('City General Hospital', '123 Main Street, Downtown', 'Mumbai', 'Maharashtra', '400001', '+91-22-12345678', 'info@citygeneral.com', 19.0760, 72.8777, '["cardiology", "neurology", "orthopedics", "emergency", "surgery"]', TRUE, 20, 200, 45, 4.5, 'MH-HOSP-001'),
('Apollo Medical Center', '456 Health Avenue, Andheri', 'Mumbai', 'Maharashtra', '400053', '+91-22-87654321', 'care@apollo.com', 19.1136, 72.8697, '["oncology", "cardiology", "pediatrics", "neurology", "transplant"]', TRUE, 30, 350, 80, 4.8, 'MH-HOSP-002'),
('Metro Emergency Hospital', '789 Emergency Road, Bandra', 'Mumbai', 'Maharashtra', '400050', '+91-22-11223344', 'emergency@metro.com', 19.0596, 72.8295, '["emergency", "trauma", "surgery", "orthopedics", "burns"]', TRUE, 15, 120, 30, 4.3, 'MH-HOSP-003'),
('Sunshine Children Hospital', '321 Kids Lane, Dadar', 'Mumbai', 'Maharashtra', '400014', '+91-22-44556677', 'info@sunshine.com', 19.0178, 72.8478, '["pediatrics", "neonatology", "pediatric_surgery", "pediatric_neurology"]', FALSE, 10, 100, 25, 4.6, 'MH-HOSP-004'),
('Cardiac Care Institute', '654 Heart Boulevard, Powai', 'Mumbai', 'Maharashtra', '400076', '+91-22-99887766', 'heart@cardiac.com', 19.1176, 72.9060, '["cardiology", "cardiac_surgery", "electrophysiology", "cardiac_imaging"]', TRUE, 25, 180, 40, 4.7, 'MH-HOSP-005');

-- ============================================================
-- USERS (passwords are bcrypt hashed version of 'password123')
-- ============================================================
INSERT INTO users (full_name, age, gender, phone, email, password_hash, blood_group, medical_history, chronic_conditions, role) VALUES
('Admin User', 35, 'male', '+91-9999999999', 'admin@system.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'O+', NULL, NULL, 'system_admin'),
('Dr. Rajesh Kumar', 45, 'male', '+91-9876543210', 'dr.rajesh@citygeneral.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'A+', NULL, NULL, 'doctor'),
('Dr. Priya Sharma', 38, 'female', '+91-9876543211', 'dr.priya@apollo.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'B+', NULL, NULL, 'doctor'),
('Dr. Amit Patel', 52, 'male', '+91-9876543212', 'dr.amit@metro.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'O-', NULL, NULL, 'doctor'),
('Ravi Singh', 30, 'male', '+91-9876543213', 'ravi.driver@ambulance.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'B+', NULL, NULL, 'driver'),
('Suresh Kumar', 28, 'male', '+91-9876543214', 'suresh.driver@ambulance.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'A-', NULL, NULL, 'driver'),
('John Patient', 35, 'male', '+91-9876543215', 'john@patient.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'O+', 'Hypertension diagnosed 2020', 'Hypertension', 'patient'),
('Sarah Patient', 28, 'female', '+91-9876543216', 'sarah@patient.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'AB+', 'Diabetes Type 2', 'Diabetes', 'patient'),
('Hospital Admin', 40, 'female', '+91-9876543217', 'admin@citygeneral.com', '$2b$12$QcCI0yEBlPHl.5GFQugtPOv/6TzZaEeo0kk8aSlho5pVSq4oI/PvC', 'O+', NULL, NULL, 'hospital_admin');

-- ============================================================
-- DOCTORS
-- ============================================================
INSERT INTO doctors (hospital_id, user_id, doctor_name, specialization, qualification, experience_years, consultation_fee, availability, rating) VALUES
(1, 2, 'Dr. Rajesh Kumar', 'Cardiologist', 'MBBS, MD (Cardiology), DM', 20, 1500.00, '{"monday": ["09:00", "17:00"], "tuesday": ["09:00", "17:00"], "wednesday": ["09:00", "13:00"], "thursday": ["09:00", "17:00"], "friday": ["09:00", "17:00"]}', 4.8),
(2, 3, 'Dr. Priya Sharma', 'Neurologist', 'MBBS, MD (Neurology), DM', 15, 2000.00, '{"monday": ["10:00", "18:00"], "tuesday": ["10:00", "18:00"], "thursday": ["10:00", "18:00"], "friday": ["10:00", "18:00"], "saturday": ["10:00", "14:00"]}', 4.9),
(3, 4, 'Dr. Amit Patel', 'Emergency Medicine', 'MBBS, MD (Emergency Medicine)', 25, 800.00, '{"monday": ["00:00", "23:59"], "tuesday": ["00:00", "23:59"], "wednesday": ["00:00", "23:59"], "thursday": ["00:00", "23:59"], "friday": ["00:00", "23:59"], "saturday": ["00:00", "23:59"], "sunday": ["00:00", "23:59"]}', 4.7),
(1, NULL, 'Dr. Sanjay Verma', 'Orthopedist', 'MBBS, MS (Orthopedics)', 18, 1200.00, '{"tuesday": ["09:00", "17:00"], "wednesday": ["09:00", "17:00"], "friday": ["09:00", "17:00"], "saturday": ["09:00", "13:00"]}', 4.5),
(2, NULL, 'Dr. Meena Nair', 'Pulmonologist', 'MBBS, MD (Pulmonology)', 12, 1800.00, '{"monday": ["09:00", "15:00"], "wednesday": ["09:00", "15:00"], "thursday": ["09:00", "15:00"], "friday": ["09:00", "15:00"]}', 4.6),
(4, NULL, 'Dr. Ananya Roy', 'Pediatrician', 'MBBS, MD (Pediatrics), DCH', 10, 1000.00, '{"monday": ["09:00", "17:00"], "tuesday": ["09:00", "17:00"], "thursday": ["09:00", "17:00"], "friday": ["09:00", "17:00"], "saturday": ["09:00", "14:00"]}', 4.9),
(5, NULL, 'Dr. Vikram Mehta', 'Cardiac Surgeon', 'MBBS, MS (Surgery), M.Ch (Cardiac Surgery)', 22, 3000.00, '{"monday": ["08:00", "16:00"], "wednesday": ["08:00", "16:00"], "friday": ["08:00", "16:00"]}', 4.9);

-- ============================================================
-- AMBULANCES
-- ============================================================
INSERT INTO ambulances (ambulance_number, vehicle_type, hospital_id, current_latitude, current_longitude, status, equipment) VALUES
('AMB-001', 'advanced', 1, 19.0800, 72.8800, 'available', '["defibrillator", "oxygen", "stretcher", "iv_equipment", "cardiac_monitor"]'),
('AMB-002', 'basic', 1, 19.0750, 72.8750, 'available', '["oxygen", "stretcher", "first_aid", "iv_equipment"]'),
('AMB-003', 'icu', 2, 19.1150, 72.8720, 'available', '["defibrillator", "ventilator", "oxygen", "stretcher", "iv_equipment", "cardiac_monitor", "infusion_pump"]'),
('AMB-004', 'advanced', 3, 19.0610, 72.8310, 'available', '["defibrillator", "oxygen", "stretcher", "iv_equipment", "cardiac_monitor"]'),
('AMB-005', 'neonatal', 4, 19.0200, 72.8500, 'available', '["incubator", "oxygen", "monitoring_equipment", "iv_equipment"]'),
('AMB-006', 'basic', 5, 19.1200, 72.9080, 'available', '["oxygen", "stretcher", "first_aid"]'),
('AMB-007', 'advanced', 2, 19.1100, 72.8680, 'maintenance', '["defibrillator", "oxygen", "stretcher", "iv_equipment"]');

-- ============================================================
-- DRIVERS
-- ============================================================
INSERT INTO drivers (user_id, ambulance_id, driver_name, phone, license_number, experience_years, performance_rating, is_available, current_latitude, current_longitude) VALUES
(5, 1, 'Ravi Singh', '+91-9876543213', 'MH-DL-123456', 8, 4.8, TRUE, 19.0800, 72.8800),
(6, 3, 'Suresh Kumar', '+91-9876543214', 'MH-DL-789012', 5, 4.6, TRUE, 19.1150, 72.8720);

-- ============================================================
-- SAMPLE BOOKINGS
-- ============================================================
INSERT INTO bookings (user_id, booking_type, symptoms, symptom_severity, ai_diagnosis, ai_confidence_score, hospital_id, doctor_id, ambulance_required, booking_status, appointment_date, appointment_time) VALUES
(7, 'consultation', 'Chest pain, shortness of breath, dizziness', 'severe', 'Possible cardiac event - Angina or MI', 0.8750, 1, 1, FALSE, 'completed', '2026-05-20', '10:00:00'),
(8, 'consultation', 'Headache, blurred vision, nausea', 'moderate', 'Possible migraine or hypertension', 0.7200, 2, 2, FALSE, 'confirmed', '2026-05-25', '14:00:00'),
(7, 'emergency', 'Severe chest pain, left arm pain', 'critical', 'Suspected Myocardial Infarction', 0.9200, 1, NULL, TRUE, 'completed', NULL, NULL);
