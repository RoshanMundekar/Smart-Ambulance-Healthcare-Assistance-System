# 🚑 Smart Ambulance & Healthcare Assistance System
## 🎓 Teacher Demo Guide — Step-by-Step Walkthrough

> **For students:** Follow every step in order. Each section tells you **what to click**, **what to say**, and **what to highlight** to your teacher.

---

## 📋 Before You Start — Checklist

Run through this checklist **before** calling your teacher:

- [ ] MySQL is running (check Task Manager / Services)
- [ ] The backend server is started (see Step 0 below)
- [ ] Browser is open at `http://localhost:8000`
- [ ] You have **4 browser tabs** ready (one per role)
- [ ] Swagger UI loads at `http://localhost:8000/docs`

---

## 🚀 Step 0 — Start the Server

Open a terminal in the project folder and run:

```bash
# If using Anaconda environment named 'fast':
C:\Users\Admin\anaconda3\envs\fast\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or if python is in PATH:
python -m uvicorn main:app --reload
```

✅ **Success message you should see:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

> ⚠️ If you see a **database error**, make sure MySQL is running and the `.env` file has your correct DB password.

---

## 🌐 Step 1 — Home / Landing Page

**URL:** `http://localhost:8000`

### 🖥️ What the teacher will see:
- **Hero section** — *"Next-Gen Emergency Care, One Tap Away"* with a red SOS button
- **Key stats** — `< 3 Min` response time · `500+` hospitals · `98%` satisfaction · `24/7` available
- **Feature grid** — 6 modules explained with icons
- **How It Works** — 4-step patient journey flow
- **Navigation bar** — Features · How It Works · Login · Register

### 🎤 What to say:
> *"This is the landing page of our Smart Ambulance & Healthcare Assistance System. It is an AI-powered full-stack web application built using FastAPI, MySQL, SpaCy NLP, and Scikit-learn. The system allows patients to book ambulances, consult doctors, and get AI-based medical recommendations — all in one platform with role-based access for 5 different user types."*

---

## 🔐 Step 2 — Login & Register

**URL:** `http://localhost:8000/login`

### 🖥️ What the teacher will see:
- **Two tabs:** Login and Register
- **Login form:** Email + Password fields
- **Register form:** Full name, age, phone, email, password, blood group, medical history

### 🎤 What to say:
> *"The authentication system uses JWT (JSON Web Tokens) with bcrypt password hashing. After login, the system automatically redirects each user to their role-specific dashboard. We have 5 roles: Patient, Driver, Doctor, Hospital Admin, and System Admin — each sees a completely different interface."*

### 🔑 Demo Accounts (all passwords: `password123`)

| Role | Email | Dashboard |
|------|-------|-----------|
| 🧑 Patient | `john@patient.com` | `/dashboard` |
| 🚑 Driver | `ravi.driver@ambulance.com` | `/driver` |
| 🏥 Hospital Admin | `admin@citygeneral.com` | `/hospital` |
| 🔧 System Admin | `admin@system.com` | `/admin` |

### ✅ Actions to demonstrate:
1. Show the **Register tab** — explain all fields (medical history, blood group, emergency contact)
2. Switch to **Login tab** — log in as `john@patient.com` / `password123`
3. Show the **automatic redirect** to the patient dashboard

---

## 📊 Step 3 — Patient Dashboard

**URL:** `http://localhost:8000/dashboard`  
**Login as:** `john@patient.com` / `password123`

### 🖥️ What the teacher will see:
- **SOS Emergency button** — large red button with live GPS coordinates
- **Active Emergency Monitor** — real-time cards showing ambulance, ETA, hospital, AI analysis
- **Quick Action cards** — Book Doctor · AI Symptom Check · My Bookings · My Profile
- **Health Profile card** — blood group, chronic conditions, allergies, emergency contact
- **Recent Bookings** — history with AI diagnosis results

### 🎤 What to say:
> *"This is the patient dashboard. The most important feature is the SOS Emergency button — when a patient clicks it, the system automatically: (1) captures their GPS location, (2) runs AI symptom analysis, (3) recommends the best hospital, (4) allocates the nearest ambulance with the best driver, (5) calculates the ETA using Google Maps or Haversine formula, and (6) sends real-time WebSocket notifications to the patient, driver, and hospital — all in under 2 seconds."*

### ✅ Actions to demonstrate:
1. Point to the **GPS coordinates** shown automatically — *"Location is detected from the browser"*
2. Show the **Health Profile card** — John has Hypertension as a chronic condition
3. Click **"AI Symptom Check"** to navigate to the consultation page (Step 5)
4. Show **"My Bookings"** — previous emergency and consultation history

---

## 🧠 Step 4 — AI Symptom Analysis (KEY FEATURE)

**URL:** `http://localhost:8000/consultation`

### 🖥️ What the teacher will see:
- **Symptom input box** — free text area
- **AI Analysis results panel** — extracted symptoms, conditions, severity, specialist, confidence score
- **Doctor listing** — filterable cards with ratings, fees, specialization
- **Book Appointment form** — date, time, hospital, doctor selector

### 🎤 What to say:
> *"This is the AI consultation module. The patient types their symptoms in plain English. Our SpaCy NLP engine extracts medical keywords, maps them to a knowledge base of 45+ symptoms and 35+ conditions, calculates severity (mild/moderate/severe/critical), recommends a specialist, and gives a confidence score. For example..."*

### ✅ Actions to demonstrate — Type these symptoms and show the AI output:

**Demo 1 — Emergency symptoms:**
```
chest pain, shortness of breath, dizziness
```
Expected output:
- Severity: **Critical**
- Specialist: **Cardiologist**
- Emergency: **Yes ⚠️**
- Probable conditions: Myocardial Infarction, Angina, Pulmonary Embolism

**Demo 2 — Moderate symptoms:**
```
fever, cough, headache
```
Expected output:
- Severity: **Mild**
- Specialist: **General Physician**
- Emergency: **No**
- Probable conditions: Influenza, COVID-19, Common Cold

**Demo 3 — Neurological emergency:**
```
slurred speech, face drooping, arm weakness
```
Expected output:
- Severity: **Critical**
- Specialist: **Neurologist**
- Emergency: **Yes ⚠️** (classic FAST stroke symptoms)

### 🎤 Then say:
> *"Notice how the AI recognises these as classic stroke symptoms using the FAST protocol — Face drooping, Arm weakness, Speech difficulty. The system then recommends a Neurologist and flags it as an emergency. This analysis happens in milliseconds using our Python NLP engine with no external API call."*

---

## 🚑 Step 5 — Driver Dashboard

**URL:** `http://localhost:8000/driver`  
**Login as:** `ravi.driver@ambulance.com` / `password123`

*(Open this in a new browser tab so you can switch between roles)*

### 🖥️ What the teacher will see:
- **Driver profile card** — name, rating, total trips, availability toggle
- **Ambulance info** — vehicle number, type (basic/advanced/ICU/neonatal), equipment
- **Active Emergency card** — patient location, emergency type, ETA, patient medical info
- **Trip History** — past emergency trips with response times

### 🎤 What to say:
> *"This is the driver dashboard. When an emergency is dispatched, the driver sees the patient's real-time GPS coordinates, their medical history including blood group and allergies, and the emergency type — so they can prepare the right equipment before arrival. The driver can also toggle their availability and update their GPS location which broadcasts via WebSocket to all connected clients."*

### ✅ Actions to demonstrate:
1. Show the **ambulance details** (AMB-001, Advanced type, equipment list)
2. Show the **driver rating and trip count**
3. Show **Trip History** tab — response times and distances
4. Explain the **Toggle Availability** button — driver goes on/off duty

---

## 🏥 Step 6 — Hospital Admin Dashboard

**URL:** `http://localhost:8000/hospital`  
**Login as:** `admin@citygeneral.com` / `password123`

*(Open in another new browser tab)*

### 🖥️ What the teacher will see:
- **Hospital stats card** — name, address, bed count, ICU beds, rating
- **Active Emergencies panel** — incoming patients with severity, ETA, AI specialist recommendation, patient info
- **Today's Appointments counter**
- **Available Doctors count**
- **Doctor roster** — specializations, availability, fees

### 🎤 What to say:
> *"This is the hospital administrator view. When an ambulance is dispatched, the hospital is pre-alerted automatically — they can see the incoming patient's blood group, medical history, allergies, and which specialist the AI has recommended, giving them time to prepare before the patient arrives. The admin can also update available bed counts in real time."*

### ✅ Actions to demonstrate:
1. Show **City General Hospital** details — 200 beds, 20 ICU beds, 4.5 rating
2. Show any **active emergency** cards — patient info, severity badge, AI recommendation
3. Show the **doctor roster** — Dr. Rajesh Kumar (Cardiologist), Dr. Sanjay Verma (Orthopedist)

---

## 🔧 Step 7 — System Admin Panel

**URL:** `http://localhost:8000/admin`  
**Login as:** `admin@system.com` / `password123`

*(Open in another new browser tab)*

### 🖥️ What the teacher will see:
- **Analytics Dashboard** — total users, hospitals, doctors, ambulances, bookings, emergencies
- **User management** — list and deactivate users by role
- **Fleet management** — all ambulances with status, GPS, vehicle type
- **Live Emergencies** — all active emergency requests across the system
- **Charts** — emergency breakdown by type, booking type distribution

### 🎤 What to say:
> *"The system admin has a bird's-eye view of the entire platform. They can see all active emergencies across all hospitals, manage the ambulance fleet, deactivate users, add new hospitals, and view analytics like average response time and emergency types. This is where the seeded data shows 5 hospitals, 6 ambulances, 7 doctors, and the demo users."*

### ✅ Actions to demonstrate:
1. Show the **summary cards** — total counts of everything
2. Show **Emergency by type** breakdown (cardiac, accident, stroke, etc.)
3. Show **Fleet Management** — AMB-001 through AMB-006, their types and statuses
4. Show **User list** filtered by role

---

## 📚 Step 8 — API Documentation (Swagger UI)

**URL:** `http://localhost:8000/docs`

### 🖥️ What the teacher will see:
- **Interactive Swagger UI** with all 30+ endpoints
- **7 endpoint groups:** Authentication · Emergency · Appointments · Driver · Hospital · Admin · Health
- **"Try it out"** button on each endpoint
- **JWT Authorization** button at the top

### 🎤 What to say:
> *"This is the auto-generated API documentation. FastAPI automatically generates this from our Pydantic schemas and route decorators. Each endpoint shows the request schema, response schema, error codes, and can be tested directly from the browser after pasting a JWT token. This is the complete REST API that could be consumed by a mobile app."*

### ✅ Actions to demonstrate:
1. Click **Authorize** — paste a JWT token from login
2. Expand **POST /api/appointments/analyze-symptoms** — show the request/response schema
3. Click **"Try it out"** → type symptoms → **Execute** → show the AI JSON response
4. Expand **WebSocket /api/emergency/ws/{user_id}** — explain real-time tracking

---

## 🗄️ Step 9 — Database Schema

**URL:** Show the file `database/schema.sql` in your code editor

### 🎤 What to say:
> *"Our MySQL database has 9 tables: users, hospitals, doctors, ambulances, drivers, bookings, emergency_requests, appointments, and notifications. We also have tables for location_tracking, reviews, and audit_logs. The schema is fully normalized with foreign keys and indexes optimised for the most common queries like nearest ambulance lookup and emergency status filtering."*

### ✅ Key tables to highlight:
| Table | Purpose |
|-------|---------|
| `users` | All 5 roles in one table with role ENUM |
| `emergency_requests` | Full emergency lifecycle with 8 status stages |
| `bookings` | Stores AI diagnosis + confidence score |
| `ambulances` | Live GPS + status (available/en_route/at_scene...) |
| `notifications` | WebSocket notification persistence |

---

## 🏗️ Step 10 — Project Architecture (Show Code)

Open these files in your code editor to explain the architecture:

### Backend Structure:
```
main.py                        ← FastAPI app entry point (show this first)
app/
  api/routes/emergency.py      ← 10-step emergency pipeline (show lines 26–144)
  ai/symptom_analyzer.py       ← SpaCy NLP engine (show SYMPTOM_CONDITION_MAP)
  ai/hospital_recommender.py   ← Scoring algorithm (show scoring weights)
  auth/jwt.py                  ← JWT + bcrypt authentication
  auth/rbac.py                 ← Role-Based Access Control
  utils/notifications.py       ← WebSocket ConnectionManager
```

### 🎤 What to say about emergency.py:
> *"The emergency request handler is the most complex part. In 10 sequential steps: it runs AI symptom analysis, patient risk profiling, gets specialist recommendation, reverse geocodes the GPS coordinates, scores hospitals, allocates the best ambulance, calculates the route using Google Maps (with Haversine fallback), creates the database record, updates ambulance status, and fires WebSocket notifications — all in a single POST request."*

---

## 📡 Step 11 — Live WebSocket Demo

### How to demonstrate real-time tracking:
1. Open **two browser windows** side by side
2. Window 1 — logged in as **Patient** (`john@patient.com`)
3. Window 2 — logged in as **Driver** (`ravi.driver@ambulance.com`)
4. In the Driver window, go to the driver dashboard
5. Explain: *"When the driver updates their location, it broadcasts instantly to all WebSocket clients"*

### 🎤 What to say:
> *"Our WebSocket implementation uses FastAPI's native WebSocket support. The ConnectionManager class maintains a dictionary of active connections keyed by user_id. When a driver sends a location update, it broadcasts to every connected patient and hospital simultaneously — no polling, no refresh needed."*

---

## ✅ Demo Complete — Summary for Teacher

Say this at the end:

> *"To summarise — this system demonstrates: (1) Full-stack web development with FastAPI and MySQL, (2) AI/ML integration with SpaCy NLP for medical symptom analysis and Scikit-learn classifiers, (3) Real-time communication using WebSockets, (4) Secure JWT-based authentication with Role-Based Access Control across 5 user types, (5) Geospatial algorithms using Haversine formula and Google Maps API integration, (6) A production-ready architecture with Docker support, logging, health checks, and auto-generated API documentation.*
>
> *The system has 30+ API endpoints, 9 database tables, 5 AI modules, and a complete frontend with 7 role-specific pages. Thank you."*

---

## 🆘 Troubleshooting During Demo

| Problem | Solution |
|---------|----------|
| Server won't start | Check MySQL is running, check `.env` DB password |
| Login fails | Make sure `setup_db.py` was run: `python setup_db.py` |
| "No location found" | Allow browser location access (or use Chrome) |
| Page not loading | Clear browser cache with Ctrl+Shift+R |
| WebSocket not connecting | Check server is running on port 8000 |
| AI analysis returns empty | Type full symptom phrases, not abbreviations |

---

## 🔗 Quick Reference URLs

| Page | URL |
|------|-----|
| 🏠 Home | http://localhost:8000 |
| 🔐 Login | http://localhost:8000/login |
| 📊 Patient Dashboard | http://localhost:8000/dashboard |
| 🧠 Consultation / AI | http://localhost:8000/consultation |
| 🚑 Driver Dashboard | http://localhost:8000/driver |
| 🏥 Hospital Admin | http://localhost:8000/hospital |
| 🔧 System Admin | http://localhost:8000/admin |
| 📚 API Docs (Swagger) | http://localhost:8000/docs |
| 📖 API Docs (ReDoc) | http://localhost:8000/redoc |
| ❤️ Health Check | http://localhost:8000/health |

---

*Document prepared for student demo presentation — Smart Ambulance & Healthcare Assistance System v1.0*
