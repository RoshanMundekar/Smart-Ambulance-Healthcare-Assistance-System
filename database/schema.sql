-- ============================================================
-- SMART AMBULANCE & HEALTHCARE ASSISTANCE SYSTEM
-- MySQL 5.0-compatible Schema (utf8, LONGTEXT instead of JSON)
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_ambulance_db CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE smart_ambulance_db;

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    age INT,
    gender ENUM('male', 'female', 'other'),
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'),
    medical_history TEXT,
    chronic_conditions TEXT,
    allergies TEXT,
    emergency_contact_name VARCHAR(150),
    emergency_contact_phone VARCHAR(20),
    role ENUM('patient', 'driver', 'doctor', 'hospital_admin', 'system_admin') DEFAULT 'patient',
    is_active TINYINT(1) DEFAULT 1,
    profile_image VARCHAR(500),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- HOSPITALS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    specializations LONGTEXT,
    emergency_supported TINYINT(1) DEFAULT 0,
    icu_beds INT DEFAULT 0,
    total_beds INT DEFAULT 0,
    available_beds INT DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    license_number VARCHAR(100),
    accreditation VARCHAR(100),
    website VARCHAR(500),
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    INDEX idx_location (latitude, longitude),
    INDEX idx_emergency (emergency_supported)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- DOCTORS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    user_id INT,
    doctor_name VARCHAR(150) NOT NULL,
    specialization VARCHAR(150) NOT NULL,
    sub_specialization VARCHAR(150),
    qualification VARCHAR(300),
    license_number VARCHAR(100),
    experience_years INT DEFAULT 0,
    consultation_fee DECIMAL(10, 2) DEFAULT 0.00,
    availability LONGTEXT,
    rating DECIMAL(3, 2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    bio TEXT,
    profile_image VARCHAR(500),
    is_available TINYINT(1) DEFAULT 1,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    INDEX idx_specialization (specialization),
    INDEX idx_hospital (hospital_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- AMBULANCES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS ambulances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ambulance_number VARCHAR(50) UNIQUE NOT NULL,
    vehicle_type ENUM('basic', 'advanced', 'icu', 'neonatal') DEFAULT 'basic',
    hospital_id INT,
    current_latitude DECIMAL(10, 8),
    current_longitude DECIMAL(11, 8),
    status ENUM('available', 'en_route', 'at_scene', 'transporting', 'maintenance', 'offline') DEFAULT 'available',
    last_location_update DATETIME DEFAULT NULL,
    equipment LONGTEXT,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- DRIVERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    ambulance_id INT,
    driver_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    license_number VARCHAR(100) NOT NULL,
    experience_years INT DEFAULT 0,
    performance_rating DECIMAL(3, 2) DEFAULT 5.00,
    total_trips INT DEFAULT 0,
    is_available TINYINT(1) DEFAULT 1,
    current_latitude DECIMAL(10, 8),
    current_longitude DECIMAL(11, 8),
    last_location_update DATETIME DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ambulance_id) REFERENCES ambulances(id) ON DELETE SET NULL,
    INDEX idx_available (is_available)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- BOOKINGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_type ENUM('emergency', 'consultation', 'follow_up') NOT NULL,
    symptoms TEXT,
    symptom_severity ENUM('mild', 'moderate', 'severe', 'critical') DEFAULT 'mild',
    ai_diagnosis TEXT,
    ai_confidence_score DECIMAL(5, 4),
    hospital_id INT,
    doctor_id INT,
    ambulance_id INT,
    ambulance_required TINYINT(1) DEFAULT 0,
    booking_status ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    appointment_date DATE,
    appointment_time TIME,
    notes TEXT,
    total_cost DECIMAL(10, 2),
    payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
    FOREIGN KEY (ambulance_id) REFERENCES ambulances(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_status (booking_status),
    INDEX idx_type (booking_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- EMERGENCY REQUESTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS emergency_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    emergency_type ENUM('cardiac', 'accident', 'stroke', 'respiratory', 'other') DEFAULT 'other',
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'high',
    patient_latitude DECIMAL(10, 8) NOT NULL,
    patient_longitude DECIMAL(11, 8) NOT NULL,
    patient_address TEXT,
    assigned_ambulance_id INT,
    assigned_hospital_id INT,
    assigned_driver_id INT,
    ai_specialist_recommendation VARCHAR(200),
    eta_minutes INT,
    route_distance_km DECIMAL(8, 2),
    hospital_notified TINYINT(1) DEFAULT 0,
    driver_notified TINYINT(1) DEFAULT 0,
    status ENUM('requested', 'ambulance_assigned', 'en_route', 'at_scene', 'transporting', 'arrived', 'completed', 'cancelled') DEFAULT 'requested',
    response_time_minutes INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_ambulance_id) REFERENCES ambulances(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_driver_id) REFERENCES drivers(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_user (user_id),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- APPOINTMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INT DEFAULT 30,
    status ENUM('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    consultation_notes TEXT,
    prescription TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    INDEX idx_doctor_date (doctor_id, appointment_date),
    INDEX idx_patient (patient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type ENUM('emergency', 'booking', 'appointment', 'system', 'alert') DEFAULT 'system',
    is_read TINYINT(1) DEFAULT 0,
    related_id INT,
    related_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- LOCATION TRACKING TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS location_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type ENUM('ambulance', 'driver', 'user') NOT NULL,
    entity_id INT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    speed DECIMAL(5, 2),
    heading INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_recorded (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- REVIEWS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reviewer_id INT NOT NULL,
    entity_type ENUM('hospital', 'doctor', 'driver') NOT NULL,
    entity_id INT NOT NULL,
    rating INT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_entity (entity_type, entity_id),
    UNIQUE KEY unique_review (reviewer_id, entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================================================
-- AUDIT LOG TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INT,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
