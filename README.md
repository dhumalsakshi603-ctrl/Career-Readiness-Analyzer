# Career Readiness Analyzer

Full-stack app: **React + Django + PostgreSQL + Google Gemini**

Students register, fill a profile, upload a resume, take a Gemini-generated
MCQ skill quiz, then get an AI-calculated **Readiness Score**, **Skill Gap
Analysis**, and a **Learning Roadmap** — with a **Progress Tracker** showing
score history over time.

---

## 1. Features Implemented

| Feature | Status |
|---|---|
| Register / Login (session auth) | ✅ |
| Student Profile (education, skills, interests, target role) | ✅ |
| Resume Upload (PDF/DOCX) + Gemini analysis (skills, strengths, weaknesses) | ✅ |
| MCQ Skill Assessment Quiz (Gemini-generated) + AI feedback | ✅ |
| Readiness Score (0-100, combining profile + resume + quiz via Gemini) | ✅ |
| Skill Gap Analysis | ✅ |
| Learning Roadmap | ✅ |
| Progress Tracker (score history + chart) | ✅ |

---

## 2. Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 14+
- Free Gemini API key: https://aistudio.google.com/apikey

---

## 3. PostgreSQL Setup

```sql
CREATE DATABASE careerdb;
CREATE USER careeruser WITH PASSWORD 'careerpass';
ALTER ROLE careeruser SET client_encoding TO 'utf8';
ALTER ROLE careeruser SET default_transaction_isolation TO 'read committed';
ALTER ROLE careeruser SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE careerdb TO careeruser;
```

On Postgres 15+, also run:
```sql
\c careerdb
GRANT ALL ON SCHEMA public TO careeruser;
```

---

## 4. Backend Setup (Django)

```bash
cd backend
python -m venv venv

# Activate:
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```
DB_NAME=careerdb
DB_USER=careeruser
DB_PASSWORD=careerpass
DB_HOST=localhost
DB_PORT=5432

GEMINI_API_KEY=your_actual_gemini_key_here
GEMINI_MODEL=gemini-1.5-flash
```

Run:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```

Backend: **http://localhost:8000** · Admin: **http://localhost:8000/admin**

> Note: `psycopg2-binary` needs PostgreSQL client libraries. If install fails:
> - Ubuntu: `sudo apt install libpq-dev python3-dev`
> - Mac: `brew install postgresql`

---

## 5. Frontend Setup (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend: **http://localhost:5173**

---

## 6. How to Use It (Full Flow)

1. Go to `http://localhost:5173` → redirected to Login → **Register**
2. **Profile** tab → fill education, skills, interests, target role → Save
3. **Resume** tab → upload a `.pdf` or `.docx` resume → Gemini extracts skills,
   strengths, and weaknesses
4. **Quiz** tab → enter a topic (e.g. related to your target role) → take the
   generated MCQ quiz → see score + AI feedback
5. **Readiness** tab → click **Calculate My Readiness** → Gemini combines your
   profile + resume + latest quiz into an overall score, skill gaps, and a
   learning roadmap
6. **Progress** tab → see your readiness score history as a line chart —
   recalculate anytime to add a new data point

---

## 7. API Endpoints Reference

**Auth** (`/api/auth/`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `csrf/` | Get CSRF cookie (call once on app load) |
| POST | `register/` | Create account + auto-login |
| POST | `login/` | Login |
| POST | `logout/` | Logout |
| GET | `me/` | Current logged-in user |

**Profile / Resume / Quiz / Readiness** (`/api/`)
| Method | Endpoint | Description |
|---|---|---|
| GET/PUT | `profile/` | Get or update student profile |
| POST | `resume/upload/` | Upload resume file → Gemini analysis |
| GET | `resume/latest/` | Latest resume + analysis |
| POST | `quiz/generate/` | Generate MCQ quiz via Gemini |
| GET | `quiz/<id>/` | Get quiz questions (no answers) |
| POST | `quiz/<id>/submit/` | Submit answers → score + AI feedback |
| POST | `readiness/calculate/` | Calculate overall readiness report |
| GET | `readiness/history/` | All past assessments (progress tracker) |
| GET | `readiness/latest/` | Most recent assessment |

All endpoints except `auth/*` (csrf/register/login) require an active session
— the frontend handles this automatically via cookies.

---

## 8. Project Structure

```
career-readiness-app/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── careerproject/       # settings, urls
│   ├── accounts/            # register/login/logout
│   └── studentapp/          # profile, resume, quiz, readiness models/views
│       ├── models.py
│       ├── views.py
│       ├── gemini_service.py   # all Gemini prompts live here
│       └── resume_parser.py    # PDF/DOCX text extraction
└── frontend/
    ├── package.json
    └── src/
        ├── App.jsx
        ├── api.js
        ├── context/AuthContext.jsx
        └── components/
            ├── Login.jsx, Register.jsx
            ├── Profile.jsx
            ├── Resume.jsx
            ├── Quiz.jsx
            ├── Readiness.jsx
            └── Progress.jsx
```

---

## 9. Common Issues

- **CSRF 403 errors on POST/login** → make sure the frontend called
  `GET /api/auth/csrf/` first (AuthContext does this automatically on load).
- **Session cookie not persisting** → both frontend (`:5173`) and backend
  (`:8000`) must be on `localhost` (not mixing `127.0.0.1` and `localhost`).
- **"Could not extract any text from this file"** → the PDF is likely a
  scanned image with no real text layer; try a text-based PDF or DOCX.
- **Gemini errors** → check `GEMINI_API_KEY` in `.env`, and note the free
  tier has per-minute rate limits — wait a bit and retry.
- **psycopg2 install fails** → install PostgreSQL dev headers first (see
  Backend Setup note above).

---

## 10. Ideas to Extend Further

- Add file size/type validation feedback in the UI before upload
- Let students pick a specific past resume/quiz combo when recalculating readiness
- Add PDF export of the readiness report
- Add a leaderboard or peer comparison (aggregate, anonymized)
- Deploy: Django on Render/Railway, Postgres on Neon/Supabase, React on Vercel/Netlify
