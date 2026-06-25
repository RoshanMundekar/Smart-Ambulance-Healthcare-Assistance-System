# 🚑 Smart Ambulance & Healthcare Assistance System

An AI-powered, full-stack emergency and healthcare platform built with **FastAPI**, **MySQL**, **SpaCy NLP**, **Scikit-learn**, and **Tailwind CSS**.

---

## Features

| Module | Description |
|---|---|
| 🆘 **Emergency Dispatch** | One-tap SOS → AI analysis → ambulance allocated → hospital pre-alerted |
| 🧠 **AI Symptom Analysis** | SpaCy NLP extracts symptoms, maps to conditions, scores severity |
| 🏥 **Hospital Recommendation** | Ranked by distance, specialty, beds, rating, and traffic |
| 🚑 **Ambulance Allocation** | Nearest available unit, best driver, optimal vehicle type |
| 👨‍⚕️ **Doctor Consultation** | Search by specialty, book appointments, AI-recommended |
| 📍 **Real-time Tracking** | WebSocket-based live ambulance location updates |
| 👥 **Role-based Access** | Patient / Driver / Doctor / Hospital Admin / System Admin |
| 📊 **Admin Analytics** | Dashboard with emergency stats, fleet status, user metrics |

---

## Tech Stack

```
Backend:    Python 3.11 · FastAPI · SQLAlchemy · MySQL 8.0
AI/ML:      SpaCy (NLP) · Scikit-learn (Classification)
Auth:       JWT (python-jose) · bcrypt
Frontend:   HTML5 · Tailwind CSS · Vanilla JavaScript
Real-time:  WebSocket (FastAPI native)
Maps:       Google Maps API (optional, falls back to Haversine)
Infra:      Docker · Docker Compose · Nginx
```

---

## Project Structure

```
SMART AMBULANCE & HEALTHCARE ASSISTANCE SYSTEM/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # FastAPI route handlers
│   │   │   ├── auth.py        # Registration, login, JWT
│   │   │   ├── emergency.py   # Emergency requests, WebSocket
│   │   │   ├── appointments.py# Consultation booking, doctors
│   │   │   ├── driver.py      # Driver dashboard, location
│   │   │   ├── hospital.py    # Hospital dashboard
│   │   │   └── admin.py       # Admin panel, analytics
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── auth/              # JWT + RBAC
│   │   ├── ai/                # AI engines
│   │   │   ├── symptom_analyzer.py      # SpaCy NLP analysis
│   │   │   ├── hospital_recommender.py  # Scoring + allocation
│   │   │   └── specialist_recommender.py# Patient risk profiling
│   │   ├── database/          # SQLAlchemy connection
│   │   └── utils/             # Maps API, WebSocket manager
│   ├── ai_training/           # Model training scripts
│   │   ├── train_model.py     # Scikit-learn classifier training
│   │   └── dataset.py         # Labeled training data (70+ samples)
│   ├── main.py                # FastAPI app entry point
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   │   ├── index.html         # Landing page
│   │   ├── login.html         # Login / Register
│   │   ├── dashboard.html     # Patient dashboard + SOS button
│   │   ├── consultation.html  # Symptom check + doctor booking
│   │   ├── driver.html        # Driver dashboard
│   │   ├── hospital.html      # Hospital admin dashboard
│   │   └── admin.html         # System admin panel
│   ├── js/
│   │   ├── api.js             # HTTP client
│   │   ├── auth.js            # Auth + WebSocket
│   │   └── emergency.js       # Emergency flow logic
│   └── css/custom.css
├── database/
│   ├── schema.sql             # Full MySQL schema
│   └── seed_data.sql          # Sample data
├── docker-compose.yml
├── nginx.conf
├── .env.example
└── README.md
```

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Node.js (optional, only for running a local static server)
- Git

---

### 1. Clone & Setup

```bash
# Navigate to the project directory
cd "SMART AMBULANCE & HEALTHCARE ASSISTANCE SYSTEM"

# Copy environment file
copy .env.example .env
```

Edit `.env` and set your MySQL password and other values.

---

### 2. Database Setup

```sql
-- In MySQL shell:
mysql -u root -p
SOURCE database/schema.sql;
SOURCE database/seed_data.sql;
```

Or on Windows:
```cmd
mysql -u root -p < database\schema.sql
mysql -u root -p < database\seed_data.sql
```

---

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download SpaCy English model
python -m spacy download en_core_web_sm

# Train AI models (optional — system works without pre-trained models)
python -m ai_training.train_model

# Start the server
python main.py
```

Backend runs at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

---

### 4. Frontend Setup

Open any HTML file directly in a browser, or use VS Code Live Server:

```
frontend/pages/index.html      → Landing page
frontend/pages/login.html      → Login / Register
frontend/pages/dashboard.html  → Patient view
frontend/pages/driver.html     → Driver view
frontend/pages/hospital.html   → Hospital admin view
frontend/pages/admin.html      → System admin view
```

> **Important:** The frontend makes API calls to `http://localhost:8000`. Make sure the backend is running first.

---

### 5. Docker Setup (Full Stack)

```bash
# Copy and edit environment variables
copy .env.example .env

# Build and start all services
docker-compose up --build

# Services:
# MySQL      → localhost:3306
# Backend    → localhost:8000
# Frontend   → localhost:80
```

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Patient | john@patient.com | password123 |
| Driver | ravi.driver@ambulance.com | password123 |
| Hospital Admin | admin@citygeneral.com | password123 |
| System Admin | admin@system.com | password123 |

> Note: Passwords in seed data are hashed bcrypt strings. Replace them by registering new accounts or using the admin panel.

---

## API Documentation

After starting the backend, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/auth/register              Register new user
POST   /api/auth/login                 Login (returns JWT)
GET    /api/auth/me                    Current user profile
PUT    /api/auth/me                    Update profile

POST   /api/emergency/request          Create emergency (patient)
GET    /api/emergency/{id}             Get emergency status
PATCH  /api/emergency/{id}/status      Update status (driver/admin)
WS     /api/emergency/ws/{user_id}     Real-time WebSocket

POST   /api/appointments/analyze-symptoms   AI symptom analysis
GET    /api/appointments/doctors            List/search doctors
GET    /api/appointments/hospitals          List/search hospitals
POST   /api/appointments/book              Book appointment
GET    /api/appointments/my-bookings       User's booking history

GET    /api/driver/dashboard               Driver dashboard
POST   /api/driver/location               Update GPS location
POST   /api/driver/toggle-availability    Toggle on/off duty

GET    /api/hospital/dashboard             Hospital admin view
PATCH  /api/hospital/{id}/beds             Update bed count

GET    /api/admin/analytics                System analytics
GET    /api/admin/users                    Manage users
GET    /api/admin/ambulances               Fleet management
GET    /api/admin/emergency/active         Live emergencies
```

---

## AI Modules

### Symptom Analyzer (`app/ai/symptom_analyzer.py`)
- **SpaCy NLP**: Extracts symptom keywords from natural language text
- **Knowledge Base**: 45+ symptoms mapped to conditions + specialists
- **Outputs**: Probable conditions, severity, specialist recommendation, confidence score, emergency flag

### Hospital Recommender (`app/ai/hospital_recommender.py`)
- **Scoring formula**: Distance (40pts) + Rating (25pts) + Specialization match (20pts) + Bed availability (10pts) + Emergency readiness (5pts)
- **Route estimation**: Google Maps API (with Haversine fallback)

### Ambulance Allocator (`app/ai/hospital_recommender.py`)
- **Factors**: Distance, vehicle type match, driver performance rating
- **Emergency type aware**: ICU ambulance preferred for cardiac/stroke

### Patient Risk Profiler (`app/ai/specialist_recommender.py`)
- **Risk scoring**: Age, chronic conditions, medical history
- **Risk levels**: Low / Medium / High

### ML Classifier (`ai_training/train_model.py`)
- **Algorithm**: TF-IDF + Logistic Regression (multi-class)
- **Models**: Specialist classifier, Severity classifier
- **Dataset**: 70+ labeled training examples
- **Training**: `python -m ai_training.train_model`

---

## Configuration

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | MySQL connection string | localhost |
| `JWT_SECRET_KEY` | JWT signing key | **Change this!** |
| `GOOGLE_MAPS_API_KEY` | Maps API (optional) | empty (uses Haversine) |
| `DEBUG` | Enable debug mode | False |
| `WORKERS` | Uvicorn worker count | 4 |

---

## Production Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random string
- [ ] Set `DEBUG=False`
- [ ] Restrict `CORS_ORIGINS` to your domain
- [ ] Use a production MySQL instance with proper credentials
- [ ] Set up SSL/HTTPS (Let's Encrypt)
- [ ] Configure a proper SMTP server for email notifications
- [ ] Add Google Maps API key for real routing
- [ ] Run `python -m ai_training.train_model` to pre-train AI models
- [ ] Set up monitoring (Prometheus + Grafana or similar)
- [ ] Configure log rotation

---

## License

MIT License — Free to use, modify, and distribute.

---

## Emergency Numbers

> **This system complements, but does not replace, official emergency services.**
>
> 🆘 **National Emergency: 112**
> 🚑 **Ambulance: 108**
> 🏥 **Medical Helpline: 104**
## 📱 How to Build the Android App (APK)

The project includes an automated script to package the web application into a native Android APK using Google Bubblewrap and Cloudflare Tunnels.

### Step 1: Start the Server and Tunnel
Run the following batch script to start your FastAPI server and a Cloudflare Tunnel:
```cmd
start_tunnel.bat
```
Watch the terminal output. Cloudflare will generate a secure, temporary URL for your local server.
**Copy the URL** that looks like this:
`https://solid-according-trust-draft.trycloudflare.com`

### Step 2: Compile the APK
Open a **new** PowerShell terminal and run the build script, passing in the tunnel URL you copied:
```powershell
powershell -ExecutionPolicy Bypass -File build_apk.ps1 -TunnelUrl https://your-generated-url.trycloudflare.com
```

### Optional: Using a Permanent URL
If you have a permanent Cloudflare Named Tunnel (e.g., `https://ambulance.yourdomain.com`), you can skip the temporary tunnel and build the APK directly:
```powershell
powershell -ExecutionPolicy Bypass -File build_apk.ps1 -TunnelUrl https://ambulance.yourdomain.com
```

> **Note:** Do not close the `start_tunnel.bat` window while using the app on your phone, or the app will lose connection to your local server!