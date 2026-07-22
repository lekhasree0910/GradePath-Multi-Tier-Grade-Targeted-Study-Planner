# 🎓 GradePath — AI-Driven Multi-Tier Grade-Targeted Study Planner

<p align="center">
  <img src="https://img.shields.io/badge/Django-6.x-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
  <img src="https://img.shields.io/badge/MongoDB-Atlas-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Groq-Mixtral--8x7b-F55036?style=for-the-badge&logo=lightning&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/JavaScript-ES6%2B-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/>
  <img src="https://img.shields.io/badge/HTML5-Semantic-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/>
  <img src="https://img.shields.io/badge/CSS3-Glassmorphism-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"/>
  </p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-success?style=flat-square" alt="status"/>
  </p>

> ✨ **GradePath** is a full-stack intelligent study planning platform that adapts personalized study schedules to a student's exact grade targets using AI-driven scheduling across three calibrated tiers (Baseline, Plus5, Plus10). 🚀

---

## 📋 Table of Contents

1. [🌟 Project Overview](#-project-overview)
2. [✨ Key Features](#-key-features)
3. [🛠 Tech Stack](#-tech-stack)
4. [📁 Project Structure](#-project-structure)
5. [🏗 Architecture](#-architecture)
6. [🗄 Database Schema](#-database-schema)
7. [🔌 API Endpoints](#-api-endpoints)
8. [🚀 Implementation Steps](#-implementation-steps)
9. [⚙️ Configuration & Environment Variables](#-configuration--environment-variables)
10. [▶️ Running the Project](#-running-the-project)
11. [🧪 Testing](#-testing)
12. [🗺 Page Map](#-page-map)
13. [👤 User Roles & Access](#-user-roles--access)
14. [🤖 AI Engine Details](#-ai-engine-details)
15. [📷 OCR & Syllabus Upload](#-ocr--syllabus-upload)
16. [⚠️ Known Limitations & Future Work](#-known-limitations--future-work)

---

## 🌟 Project Overview

GradePath is designed for students preparing for academic or competitive exams 📚. Given a syllabus, target grade, exam date, and availability, the platform:

1. 🔍 **Parses and analyses the syllabus** using the Groq AI API (with a keyword-based fallback engine)
2. 🗓️ **Generates a day-by-day study schedule** with three grade-targeted tiers
3. 📈 **Tracks progress** in real time and recalculates the remaining schedule dynamically
4. 🗃️ **Stores completed plans** in a personal Vault for reference
5. 💬 **Provides an AI chat assistant** to answer study-related questions

🛠 Admins can monitor system-wide usage analytics, manage student accounts, and approve administrator registration requests.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **Multi-Tier Study Plans** | Three parallel plans — Baseline (current grade), Plus5 (+5% target), Plus10 (+10% target) |
| 🧠 **AI Syllabus Analysis** | Groq API (Mixtral-8x7b) breaks syllabi into weighted topics with complexity scores |
| 📷 **OCR Syllabus Upload** | Upload `.txt`, `.pdf`, or images (`.png`, `.jpg`) — Tesseract OCR extracts the text |
| 🗓️ **Smart Scheduler** | Allocates study days, builds topic sessions, adds revision buffers |
| ⏱️ **Pace Tracking** | Classifies learner pace as *OnTrack*, *Behind*, or *Ahead* each day |
| 🔄 **Plan Recompression** | Automatically redistributes remaining topics if the student falls behind |
| 📝 **Feedback & Versioning** | Students submit feedback; plan versions are tracked in history |
| 🗃️ **Plan Vault** | Personal archive of all generated study plans |
| 🤖 **AI Chat Assistant** | Context-aware chatbot (Groq) with rule-based fallback |
| 🧭 **Ready-Made Roadmaps** | Pre-seeded course roadmaps (Python, Web Dev, Data Science, etc.) |
| 📊 **Admin Dashboard** | Usage analytics, difficulty trends, student management, access request approvals |
| 🌌 **Glassmorphism UI** | Dark-mode, gradient-rich, animated frontend with Font Awesome icons |

---

## 🛠 Tech Stack

### ⚙️ Backend

<p>
  <img src="https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white" alt="Django"/>
  <img src="https://img.shields.io/badge/Django%20REST%20Framework-A30000?style=flat-square&logo=django&logoColor=white" alt="DRF"/>
  <img src="https://img.shields.io/badge/MongoDB%20Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB Atlas"/>
  <img src="https://img.shields.io/badge/SQLite3-07405E?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite3"/>
  <img src="https://img.shields.io/badge/Groq%20API-F55036?style=flat-square&logo=lightning&logoColor=white" alt="Groq"/>
  <img src="https://img.shields.io/badge/Tesseract%20OCR-4285F4?style=flat-square&logo=googlelens&logoColor=white" alt="Tesseract"/>
</p>

| Layer | Technology |
|---|---|
| 🌐 Web Framework | **Django 6.x** (with Django REST Framework) |
| 🍃 Primary Database | **MongoDB Atlas** (via `pymongo`) |
| 🗄️ Secondary DB | **SQLite3** (Django sessions / admin) |
| 🧠 AI / LLM | **Groq API** — Mixtral-8x7b-32768 |
| 👁️ OCR | **Tesseract OCR** + `pytesseract` + `Pillow` |
| 📄 PDF Parsing | `pypdf` |
| 🔑 Auth | Token-based (UUID tokens stored in MongoDB `sessions` collection) |
| 🔒 Password Hashing | Django PBKDF2-SHA256 (`make_password` / `check_password`) |
| 🌍 CORS | `django-cors-headers` |
| 🧩 Env Management | `python-dotenv` |

### 🎨 Frontend

<p>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5"/>
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3"/>
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JavaScript"/>
  <img src="https://img.shields.io/badge/Font%20Awesome-528DD7?style=flat-square&logo=fontawesome&logoColor=white" alt="Font Awesome"/>
</p>

| Layer | Technology |
|---|---|
| 🏷️ Markup | **HTML5** (semantic, multi-page) |
| 🎨 Styling | **Vanilla CSS** (glassmorphism, CSS custom properties, dark/light themes) |
| ⚡ Logic | **Vanilla JavaScript** (ES6+, Fetch API) |
| 🔣 Icons | **Font Awesome 6.4** |
| 🔤 Fonts | Times New Roman / system serif (configurable via CSS variables) |

---

## 📁 Project Structure

```
Gradepath/
├── .env                         # Root environment variables (Groq API key, etc.)
├── GradePath_SRS_v2.docx        # Software Requirements Specification
├── user_credentials.md          # Dev/test credentials reference
├── README.md                    # This file
│
├── Backend/
│   ├── manage.py                # Django management entry point
│   ├── db.sqlite3                # SQLite for Django internals
│   ├── test_suite.py             # End-to-end HTTP test suite (standalone)
│   ├── run_tests.py              # Test runner helper
│   ├── .env                      # Backend-specific env overrides
│   ├── uploads/                  # Temporary directory for uploaded syllabus files
│   │
│   ├── gradepath/                # Django project configuration
│   │   ├── settings.py           # App settings, MongoDB, Groq, CORS config
│   │   ├── urls.py               # Root URL router (API + Frontend static serving)
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   └── api/                      # Main Django app
│       ├── models.py             # MongoDB collection handles + counter seeding
│       ├── views.py              # All REST API view functions (~1176 lines)
│       ├── urls.py               # API URL patterns
│       ├── ai_engine.py          # Groq API integration + fallback syllabus analyser
│       ├── scheduler.py          # Study plan generation + recompression logic
│       ├── ocr_util.py           # File-to-text extraction (TXT, PDF, Image/OCR)
│       ├── admin.py              # Django admin registrations
│       ├── apps.py
│       ├── tests.py               # Django unit tests
│       └── migrations/            # Django migration files
│
└── Frontend/
    ├── index.html                # Landing page (hero, features, how-it-works)
    ├── register.html             # Student & Admin registration
    ├── login_student.html        # Student login
    ├── login_admin.html          # Admin login
    ├── student_dashboard.html    # Student progress dashboard
    ├── admin_dashboard.html      # Admin analytics dashboard
    ├── courses.html              # Browse ready-made course roadmaps
    ├── customize.html            # Study plan customisation form
    ├── plan_output.html          # View generated study plan tiers
    ├── vault.html                # Saved plan archive
    ├── style.css                 # Global styles + design tokens (~40 KB)
    ├── script.js                 # All frontend logic (~70 KB)
    └── assets/                   # Static assets (hero images, etc.)
```

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    🖥️  BROWSER (Student / Admin)                          │
│                                                                            │
│  index.html ─ register.html ─ login_*.html ─ dashboard ─ customize ─ vault│
│                   └─── script.js (Fetch API calls) ────────────────────┘  │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │ HTTP (port 8000)
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              🌐 Django Backend (manage.py runserver)                      │
│                                                                            │
│  gradepath/urls.py                                                         │
│    ├── /         → serve Frontend HTML files statically                    │
│    ├── /api/     → api/urls.py → views.py                                  │
│    └── /admin/   → Django admin                                            │
│                                                                            │
│  api/views.py  ──►  ai_engine.py  ──► 🧠 Groq Cloud API (Mixtral)          │
│                ──►  scheduler.py  (pure Python scheduling logic)           │
│                ──►  ocr_util.py   (Tesseract / pypdf)                      │
│                ──►  models.py     ──► 🍃 MongoDB Atlas                     │
│                                                                            │
│  Sessions stored in MongoDB "sessions" collection (UUID bearer tokens)     │
└──────────────────────────────────────────────────────────────────────────┘
```

### 🔑 Request Authentication Flow

```
Client                                  Backend
  │                                        │
  │─── POST /api/auth/login/ ─────────────►│
  │                                        │  verify credentials (PBKDF2)
  │◄── { token: "uuid-token" } ───────────│  store session in MongoDB
  │                                        │
  │─── GET /api/... (Authorization: Bearer <token>) ──►│
  │                                        │  look up token in db_sessions
  │◄── protected data ─────────────────────│
```

---

## 🗄 Database Schema

GradePath uses **MongoDB Atlas** 🍃 (`gradepath_db` database) with the following collections:

### 👤 `users`
```json
{
  "user_id": 101,
  "full_name": "Ananya Rao",
  "email": "ananya.rao@example.com",
  "password": "<PBKDF2 hash>",
  "role": "Student",
  "created_at": "ISO-8601"
}
```

### 🔑 `sessions`
```json
{
  "token": "uuid-v4",
  "user_id": 101,
  "email": "...",
  "role": "Student",
  "full_name": "...",
  "created_at": "ISO-8601"
}
```

### 🧭 `courses`
```json
{
  "course_id": 11,
  "course_name": "Python Core",
  "category": "Software Development",
  "description": "...",
  "stage_count": 5,
  "stages": [
    { "stage_number": 1, "title": "Syntax & Basics", "topics": ["Variables", "Data Types"] }
  ],
  "created_by": 999,
  "created_at": "ISO-8601"
}
```

### 📝 `customization_requests`
```json
{
  "request_id": 301,
  "user_id": 101,
  "subject_name": "Computer Science Core",
  "exam_category": "Academic",
  "answer_format": "Descriptive",
  "exam_date": "2026-10-15",
  "target_grade_percent": 85,
  "available_hours_per_day": 3,
  "selected_days": ["Mon", "Wed", "Fri"],
  "learner_level": "Intermediate",
  "syllabus_text": "...",
  "created_at": "ISO-8601"
}
```

### 🗓️ `plans`
```json
{
  "plan_id": 301,
  "request_id": 201,
  "user_id": 101,
  "tier": "Baseline",
  "daily_schedule": [
    {
      "date": "2026-07-25",
      "topics": [
        { "topic_id": "topic_01", "topic_name": "Data Structures", "tasks": ["..."] }
      ],
      "is_revision": false
    }
  ],
  "version": 1,
  "created_at": "ISO-8601"
}
```

### 📈 `progress`
```json
{
  "progress_id": 601,
  "plan_id": 301,
  "user_id": 101,
  "completed_topic_ids": ["topic_01", "topic_02"],
  "pace": "OnTrack",
  "updated_at": "ISO-8601"
}
```

### 🗃️ `vault`
```json
{
  "vault_id": 501,
  "student_id": 101,
  "plan_id": 301,
  "subject_name": "Computer Science Core",
  "tier": "Plus5",
  "saved_at": "ISO-8601",
  "status": "active"
}
```

### 🔢 Auto-Increment Counters (`counters` collection)

| Counter | Start Value | Next Issued |
|---|---|---|
| `user_id` | 100 | 101 |
| `request_id` | 200 | 201 |
| `plan_id` | 300 | 301 |
| `feedback_id` | 400 | 401 |
| `vault_id` | 500 | 501 |
| `progress_id` | 600 | 601 |
| `admin_request_id` | 700 | 701 |
| `course_id` | 10 | 11 |

---

## 🔌 API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

All protected endpoints require the header:
```
Authorization: Bearer <token>
```

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | ✅ | Register a new Student or Admin |
| `POST` | `/api/auth/login/` | ✅ | Login and receive a bearer token |
| `POST` | `/api/auth/logout/` | ✅ | Invalidate the current session |
| `GET/PATCH` | `/api/users/<user_id>/profile/` | ✅ | Get or update user profile |
| `POST` | `/api/auth/admin-request/` | ✅ | Submit an admin access request |

**Register payload:**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword",
  "role": "Student"
}
```

**Login payload:**
```json
{
  "email": "jane@example.com",
  "password": "securepassword",
  "role": "Student"
}
```

---

### 🧭 Courses & Roadmaps

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/courses/` | ✅ | List all available course roadmaps |
| `GET` | `/api/courses/<course_id>/` | ✅ | Get a single course with all stages |

---

### 📷 Syllabus

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/syllabus-bank/` | ❌ | Get the pre-built syllabus bank |
| `POST` | `/api/syllabus/upload/` | ✅ | Upload a `.txt`, `.pdf`, or image file for OCR extraction |

---

### 🗓️ Study Plan Customisation

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/plans/customize/` | ✅ | Submit preferences — generates 3-tier study plans |
| `GET` | `/api/plans/request/<request_id>/` | ✅ | Get all plans for a customisation request |
| `GET` | `/api/plans/<plan_id>/` | ✅ | Get a specific plan's full daily schedule |

**Customise payload:**
```json
{
  "subject_name": "Computer Science Core",
  "exam_category": "Academic",
  "answer_format": "Descriptive",
  "exam_date": "2026-10-15",
  "target_grade_percent": 85,
  "available_hours_per_day": 3,
  "selected_days": ["Mon", "Wed", "Fri", "Sat"],
  "learner_level": "Intermediate",
  "syllabus_text": "Data Structures, Algorithms, OS, DBMS, Networks"
}
```

Exam categories: `Academic` | `Competitive` | `Vocational`
Answer formats: `MCQ` | `Descriptive` | `Oral` | `Practical`
Learner levels: `Beginner` | `Intermediate` | `Advanced`

---

### 📈 Progress Tracking

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/plans/<plan_id>/progress/` | ✅ | Fetch current progress + pace status |
| `POST` | `/api/plans/<plan_id>/progress/` | ✅ | Update completed topic IDs |
| `POST` | `/api/plans/<plan_id>/recompress/` | ✅ | Recompute remaining schedule after delays |

---

### 📝 Feedback & Versioning

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/plans/<plan_id>/feedback/` | ✅ | Submit a feedback entry for the plan |
| `GET` | `/api/plans/<plan_id>/versions/` | ✅ | View version history of a plan |

---

### 🗃️ Plan Vault

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/vault/<student_id>/` | ✅ | List all saved plans for a student |
| `GET` | `/api/vault/session/<vault_id>/` | ✅ | Get a specific saved plan |
| `DELETE` | `/api/vault/session/<vault_id>/` | ✅ | Delete a vault entry |
| `POST` | `/api/vault/session/<vault_id>/reopen/` | ✅ | Mark a closed plan as active again |

---

### 🛠 Admin

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/admin/analytics/usage/` | ✅ Admin | System-wide usage metrics |
| `GET` | `/api/admin/analytics/difficulty-trends/` | ✅ Admin | Topic difficulty trend data |
| `GET` | `/api/admin/students/` | ✅ Admin | List all registered students |
| `GET` | `/api/admin/requests/` | ✅ Admin | List pending admin access requests |
| `POST` | `/api/admin/requests/<request_id>/action/` | ✅ Admin | Approve or reject an access request |

---

### 💬 AI Chat

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/chat/` | ✅ | Send a message to the AI study assistant |

**Chat payload:**
```json
{
  "message": "What should I study today?",
  "context": "Student studying Data Structures, exam in 30 days."
}
```

---

## 🚀 Implementation Steps

Follow these steps in order to set up and run GradePath from scratch.

---

### 1️⃣ Step 1 — Prerequisites

Ensure the following are installed on your system:

- 🐍 **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- 📦 **pip** (bundled with Python)
- 🍃 **MongoDB Atlas account** — [cloud.mongodb.com](https://cloud.mongodb.com/) (free M0 tier is sufficient)
- 🧠 **Groq API key** — [console.groq.com](https://console.groq.com/) (free tier available)
- 👁️ **Tesseract OCR** (optional, for image syllabus uploads)
  - Windows: Download installer from [UB Mannheim Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
  - Default install path expected: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- 🌐 A modern browser and a code editor (VS Code recommended)

---

### 2️⃣ Step 2 — Clone / Open the Project

```powershell
# If using Git
git clone <your-repo-url> Gradepath
cd Gradepath

# OR navigate to the existing project folder
cd "C:\Users\Y.Lekhasree\OneDrive\Desktop\Project-FDA\Gradepath"
```

---

### 3️⃣ Step 3 — Create and Activate a Virtual Environment

```powershell
# From the Gradepath root directory
python -m venv venv

# Activate on Windows PowerShell
.\venv\Scripts\Activate.ps1

# Activate on Windows CMD
.\venv\Scripts\activate.bat
```

> ✅ You should see `(venv)` at the start of your terminal prompt.

---

### 4️⃣ Step 4 — Install Python Dependencies

```powershell
pip install django djangorestframework django-cors-headers pymongo python-dotenv requests pypdf pillow pytesseract
```

| Package | Purpose |
|---|---|
| `django` | 🌐 Core web framework |
| `djangorestframework` | 🔧 REST API decorator utilities |
| `django-cors-headers` | 🌍 CORS policy for browser-backend communication |
| `pymongo` | 🍃 MongoDB Atlas driver |
| `python-dotenv` | 🧩 Load `.env` configuration files |
| `requests` | 📡 HTTP calls to Groq API |
| `pypdf` | 📄 PDF text extraction |
| `pillow` | 🖼️ Image processing for OCR |
| `pytesseract` | 👁️ Python wrapper for Tesseract OCR binary |

---

### 5️⃣ Step 5 — Configure Environment Variables

**Root `.env`** (`Gradepath/.env`) — already present, update the Groq key:

```env
# Required: Groq AI API key for syllabus analysis and chatbot
GROQ_API_KEY=your_groq_api_key_here

# Optional overrides
# GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
# GROQ_MODEL=mixtral-8x7b-32768
```

**Backend `.env`** (`Gradepath/Backend/.env`) — create if missing:

```env
# MongoDB Atlas connection string
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/

# Django secret key — change this in production!
DJANGO_SECRET_KEY=your-very-long-secret-key-here

# Debug mode (set False in production)
DJANGO_DEBUG=True

# Allowed hosts (comma-separated)
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

> 🍃 **How to get your MongoDB URI:**
> 1. Log in to [cloud.mongodb.com](https://cloud.mongodb.com/)
> 2. Create a free **M0 Cluster**
> 3. Go to **Database Access** → Add a database user with username and password
> 4. Go to **Network Access** → Add your IP (or `0.0.0.0/0` for dev)
> 5. Go to **Connect → Drivers → Python** → copy the connection string
> 6. Replace `<username>` and `<password>` in the URI

---

### 6️⃣ Step 6 — Run Django Migrations

GradePath uses SQLite for Django's built-in admin and auth tables:

```powershell
cd Backend
python manage.py makemigrations
python manage.py migrate
```

---

### 7️⃣ Step 7 — (Optional) Create Django Superuser

Only needed to access Django's built-in admin panel at `/django-admin/`:

```powershell
python manage.py createsuperuser
```

> ℹ️ **Note:** This is separate from GradePath's own admin system. You do not need this to use GradePath's Admin Dashboard.

---

### 8️⃣ Step 8 — Seed Initial Data

GradePath seeds data **automatically** on startup:

| Data | How it Seeds |
|---|---|
| 🔢 MongoDB ID counters | `api/models.py` — runs on Django app import |
| 🧭 Course roadmaps (Python, Web Dev, etc.) | `views.py → seed_courses_if_empty()` — runs on first `/api/courses/` request |
| 🔐 Admin user | Must be created manually via registration |

**Create the admin user** (with the server running from Step 9):

```powershell
# Windows PowerShell — one-liner to register the admin
$body = '{"full_name":"Platform Admin","email":"admin@gradepath.com","password":"adminpassword","role":"Admin","access_code":"GRADEPATH_ADMIN_2024"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/register/ -Method POST -Body $body -ContentType 'application/json'
```

Or navigate to `http://127.0.0.1:8000/register.html`, select the **Administrator** tab, and enter the access code `GRADEPATH_ADMIN_2024`.

---

### 9️⃣ Step 9 — Start the Development Server

```powershell
# Ensure you are inside the Backend directory
cd "C:\Users\Y.Lekhasree\OneDrive\Desktop\Project-FDA\Gradepath\Backend"

# Start the server
python manage.py runserver
```

Expected output:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
July 22, 2026 - 20:34:00
Django version 6.0.x, using settings 'gradepath.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

> 🌐 The Django project serves **both** the API and all Frontend HTML/CSS/JS files from a single server — no separate frontend server is needed.

---

### 🔟 Step 10 — Access the Application

Open your browser and go to:

| URL | Page |
|---|---|
| `http://127.0.0.1:8000/` | 🏠 Landing Page |
| `http://127.0.0.1:8000/register.html` | 📝 Register |
| `http://127.0.0.1:8000/login_student.html` | 🎓 Student Login |
| `http://127.0.0.1:8000/login_admin.html` | 🔐 Admin Login |
| `http://127.0.0.1:8000/courses.html` | 📚 Course Roadmaps |
| `http://127.0.0.1:8000/customize.html` | ✏️ Create Study Plan |
| `http://127.0.0.1:8000/student_dashboard.html` | 📊 Student Dashboard |
| `http://127.0.0.1:8000/admin_dashboard.html` | 🛠 Admin Dashboard |
| `http://127.0.0.1:8000/vault.html` | 🗃 Plan Vault |

---

### 1️⃣1️⃣ Step 11 — (Optional) Configure Tesseract OCR for Image Uploads

To support image-based syllabus uploads (`.png`, `.jpg`, etc.):

1. Download and install Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Ensure the binary exists at one of the auto-detected paths:
   - `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
3. No additional code changes needed — `ocr_util.py` auto-detects the path

> 👁️ Without Tesseract, the app returns a subject-specific mock syllabus (based on keywords in the filename) as a graceful fallback.

---

## ⚙️ Configuration & Environment Variables

| Variable | File | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | `.env` (root) | — | Required for AI features 🧠 |
| `GROQ_API_URL` | `.env` (root) | `https://api.groq.com/openai/v1/chat/completions` | Groq API endpoint |
| `GROQ_MODEL` | `.env` (root) | `mixtral-8x7b-32768` | LLM model to use |
| `MONGO_URI` | `Backend/.env` | Atlas URI (dev default) | MongoDB connection string 🍃 |
| `DJANGO_SECRET_KEY` | `Backend/.env` | Insecure dev key | **Change before production!** ⚠️ |
| `DJANGO_DEBUG` | `Backend/.env` | `True` | Set `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `Backend/.env` | `*` | Comma-separated allowed hosts |

### 🌍 CORS Configuration

The backend allows requests from VS Code Live Server by default:

```python
# Backend/gradepath/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
```

To add other origins (e.g., a deployed frontend URL), append to this list in `settings.py`.

---

## 🧪 Testing

### ✅ End-to-End Test Suite

```powershell
# Make sure the Django server is running first (Step 9)
cd Backend
python test_suite.py
```

**Tests covered:**

| # | Test Case |
|---|---|
| 1 | 🌐 All HTML pages are accessible (HTTP 200) |
| 2 | 🎨 CSS stylesheet accessible |
| 3 | ⚡ JS script accessible |
| 4 | 📝 Student registration |
| 5 | 🔑 Student login (valid credentials) |
| 6 | 🚫 Invalid credential rejection |
| 7 | 🔐 Admin login |
| 8 | 🧭 Courses list API |
| 9 | 🧭 Course detail API |
| 10 | 📷 Syllabus bank API |
| 11 | 🗓️ Create a 3-tier custom study plan |
| 12 | 🗃️ Fetch saved vault plans |
| 13 | 🔔 Submit admin access request |

**Sample output:**
```
================================================================================
              GRADEPATH END-TO-END COMPREHENSIVE TEST SUITE
================================================================================
Page: Landing Page                       | PASS     | HTTP 200
API: Register Student                    | PASS     | Code 201
API: Login Student                       | PASS     | Code 200: Token received: True
API: Reject Invalid Credentials          | PASS     | Code 401
API: Login Admin                         | PASS     | Code 200: Token received: True
API: Get Courses List                    | PASS     | Found 8 courses
API: Create Custom Study Plan            | PASS     | Code 201
...
--------------------------------------------------------------------------------
SUMMARY: 13 / 13 tests passed successfully. ✅
================================================================================
```

### 🐍 Django Unit Tests

```powershell
cd Backend
python manage.py test api
```

---

## 🗺 Page Map

| Page | File | Access | Description |
|---|---|---|---|
| 🏠 Landing Page | `index.html` | Public | Hero, features, how-it-works, AI chat widget |
| 📝 Register | `register.html` | Public | Student & Admin registration with tabbed UI |
| 🎓 Student Login | `login_student.html` | Public | Login form for students |
| 🔐 Admin Login | `login_admin.html` | Public | Login form for administrators |
| 📊 Student Dashboard | `student_dashboard.html` | 🔒 Student | Progress tracking, pace indicator, daily goals |
| 🛠 Admin Dashboard | `admin_dashboard.html` | 🔒 Admin | Usage analytics, student management |
| 📚 Courses | `courses.html` | Public | Browse pre-built learning roadmaps |
| ✏️ Customize Planner | `customize.html` | 🔒 Student | Form to generate personalised study plans |
| 📈 Plan Output | `plan_output.html` | 🔒 Student | View and compare 3 study plan tiers |
| 🗃 Plan Vault | `vault.html` | 🔒 Student | Archive of all past generated plans |

---

## 👤 User Roles & Access

### 🎓 Student
- 📝 Register with email and password on the Register page
- 🗓️ Create personalised study plans (3 tiers generated automatically)
- 📈 Track daily progress and study pace (OnTrack / Behind / Ahead)
- 🕘 View plan version history and submit topic feedback
- 🗃️ Save plans to the personal Vault
- 💬 Use the AI chat assistant

### 🛠 Admin
- 🔑 Registration requires **Access Code**: `GRADEPATH_ADMIN_2024`
- 🔔 Alternative: Submit an access request → existing admin approves → code is revealed
- 📊 View system-wide usage analytics and difficulty trends
- 👥 Manage student accounts
- ✅ Approve or reject admin access requests

### 🔑 Development Credentials

| Role | Email | Password |
|---|---|---|
| 🛠 Admin (Primary) | `admin@gradepath.com` | `adminpassword` |
| 🛠 Admin (Test) | `admintest@gradepath.com` | `admin123` |
| 🎓 Student (Demo) | `ananya.rao@example.com` | `ananya123` |
| 🎓 Student (Tester) | `tester@gradepath.com` | `password123` |

> ⚠️ **Warning:** These credentials are for development and testing only. Rotate all passwords and remove this section before any production deployment.

---

## 🤖 AI Engine Details

### `api/ai_engine.py`

#### 🔍 `analyze_syllabus(syllabus_text, exam_category, answer_format)`

| Step | Action |
|---|---|
| 1 | 📡 Calls Groq API (Mixtral-8x7b-32768) with a structured analysis prompt |
| 2 | 🧩 Parses JSON response into topic objects |
| 3 | 🔄 Falls back to keyword-based simulation if API fails |
| 4 | 📤 Returns list: `[{ topic_id, topic_name, subtopics, complexity, weight }]` |

**Complexity scoring (fallback keyword engine):**

| Score | Meaning | Example Keywords |
|---|---|---|
| 1 | 🟢 Very Easy | intro, history, overview |
| 2 | 🟢 Easy | basics, fundamentals, definitions |
| 3 | 🟡 Medium (default) | — |
| 4 | 🟠 Hard | algorithms, analysis, mechanics, electromagnetism |
| 5 | 🔴 Very Hard | quantum, deep learning, advanced, cryptography |

**Exam category modifiers:**
- `Competitive` → score +1 (max 5) ⬆️
- `Vocational` or `Oral` format → score -1 (min 1) ⬇️

#### 💬 `get_chat_response(message, context="")`
- 📡 Calls Groq API with a study-assistant system prompt
- 🔄 Falls back to keyword-matched canned responses (hello, progress, study, break, thanks)

#### 🔐 `get_syllabus_hash(syllabus_text)`
- Returns SHA-256 hash for syllabus caching/deduplication

---

### `api/scheduler.py`

#### 🗓️ `generate_plans(topics, request_data)`

Generates **three complete day-by-day schedules** in parallel:

| Tier | Sessions per Topic | Extras |
|---|---|---|
| 🟢 `Baseline` | 1x | Core tasks only |
| 🟡 `Plus5` | 1.5x | + Weekly self-assessment quizzes |
| 🔴 `Plus10` | 2x | + Speed drills, negative marking simulations |

#### 🔄 `recompress_schedule(plan, completed_topic_ids)`
When a student falls behind: redistributes remaining uncompleted topics across remaining available days, preserving the revision buffer at the end.

#### 📝 `apply_feedback_patch(plan, feedback)`
Adjusts future topic sessions based on student-submitted difficulty feedback.

#### 📅 Revision Buffer Logic

| Total Study Days | Revision Days Added |
|---|---|
| ≤ 3 days | 0 |
| 4–10 days | 2 |
| > 10 days | 15% of total (bounded 3–15 days) |

---

## 📷 OCR & Syllabus Upload

`api/ocr_util.py` — `extract_text_from_file(file_path)`

| Input Format | Extraction Method |
|---|---|
| 📄 `.txt`, `.json`, `.csv` | Direct UTF-8 file read |
| 📕 `.pdf` | `pypdf.PdfReader` — extracts searchable text layer |
| 🖼️ `.png`, `.jpg`, `.jpeg`, `.bmp`, `.webp` | Tesseract OCR via `pytesseract` + `Pillow` |

**Graceful fallback (no Tesseract):** Returns a pre-written subject-appropriate syllabus based on keywords in the uploaded filename (`physics`, `chemistry`, `math`, etc.).

---

## ⚠️ Known Limitations & Future Work

| Area | Current State | Planned Improvement |
|---|---|---|
| 🔑 Authentication | Simple UUID tokens stored in MongoDB | Migrate to JWT (with expiry and refresh tokens) |
| 🔒 Django Secret Key | Hardcoded insecure fallback | Use strong random key via environment variable |
| 🌍 CORS Origins | Dev origins only (port 5500) | Make configurable per-environment |
| 👁️ Tesseract Detection | Windows-specific paths hardcoded | Cross-platform `shutil.which` detection |
| 🧩 Duplicate Function | `get_chat_response` defined twice in `ai_engine.py` | Refactor to single clean implementation |
| 🗑️ Uploaded File Cleanup | Uploaded syllabus files not auto-deleted | Add periodic cleanup scheduled task |
| 🚦 Rate Limiting | None | Add per-user API rate limits |
| 🔐 HTTPS | HTTP only (dev) | Add SSL/TLS for production deployment |
| 📄 Pagination | Some endpoints return full lists | Add cursor-based pagination |
| 📧 Email Verification | Not implemented | Add email OTP on registration |
| 🔁 Password Reset | Not implemented | Add reset-by-email flow |

---

*Built with 🌐 Django · 🍃 MongoDB · 🧠 Groq AI · ⚡ Vanilla JS*
