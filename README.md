# Placement Portal

A role-based web application that streamlines the campus placement process. Institute admins, companies, and students each get their own dashboard to manage drives, applications, and placement outcomes.

**Stack:** Flask · Vue 3 · SQLite (SQLAlchemy) · JWT · Redis · Celery · Bootstrap

---

## Features

**Admin (Institute)**
- Approve, reject, or blacklist companies; blacklist students
- Approve placement drives before they become visible to students
- View and delete companies, browse all students, drives, and applications
- Reports dashboard: totals, shortlisted/selected/rejected counts, placement rate, and per-drive stats

**Company**
- Register and manage a company profile (awaits admin approval)
- Create placement drives with eligibility rules (branch, minimum CGPA, year), salary, location, and deadline
- View applicants per drive, update application status (shortlisted / selected / rejected), and close drives

**Student**
- Register, build a profile (branch, year, CGPA, skills, phone), and upload a resume (PDF only)
- Search approved drives and browse company details
- Apply to drives with automatic eligibility checks and duplicate-application prevention
- Track application status and export application history as CSV (emailed to them)

**System**
- JWT authentication with role-based route protection (`admin`, `company`, `student`)
- Redis caching for admin and student dashboards, invalidated on relevant changes
- Celery background jobs: daily deadline reminders, monthly admin report, CSV export
- Default admin account is created automatically on first run

---

## How applying works

A student's application is accepted only if all of these pass:

1. The drive is `approved`
2. A resume PDF has been uploaded
3. The deadline has not passed
4. Student CGPA meets the drive's minimum
5. Student branch is in the drive's allowed branches
6. Student year matches the drive's eligible year
7. The student has not already applied (also enforced by a unique DB constraint)

---

## Background jobs

| Task | Trigger | What it does |
|---|---|---|
| `send_daily_reminders` | Daily, 08:00 | Emails students who haven't applied to approved drives closing within 3 days |
| `send_monthly_report` | 1st of month, 09:00 | Emails the admin an HTML report of last month's drives, applications, and selections |
| `export_applications_csv` | On demand | Emails a student their application history as a CSV attachment |

---

## Project structure

```
Placement-Portal-App/
├── backend/
│   ├── app.py              # App factory, config, auto-creates DB and admin
│   ├── extensions.py       # SQLAlchemy and JWT instances
│   ├── celery_config.py    # Celery factory and beat schedule
│   ├── tasks.py            # Celery tasks (reminders, report, CSV export)
│   ├── cache.py            # Redis cache helpers
│   ├── create_db.py        # Optional manual DB setup script
│   ├── models/             # User, Company, Student, Drive, Application
│   └── routes/             # auth, admin, company, student blueprints
└── frontend/
    └── src/
        ├── views/          # Login, Register, Admin/Company/Student dashboards
        ├── router/
        └── axios.js        # API client (attaches JWT to requests)
```

---

## Getting started

### Prerequisites
- Python 3.10+
- Node.js 20.19+ or 22.12+
- Redis running on `localhost:6379`
- [MailHog](https://github.com/mailhog/MailHog) for local email testing (SMTP on port `1025`, web UI on `8025`)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API runs on `http://localhost:5000`. The SQLite database and a default admin user are created on first run.

### 2. Celery (separate terminals, from `backend/`)

```bash
# Worker
celery -A tasks.celery_app worker --loglevel=info
# On Windows add: --pool=solo

# Scheduler (daily reminders and monthly report)
celery -A app.celery beat --loglevel=info
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

### Default admin login

| Username | Password |
|---|---|
| `admin` | `admin123` |

Change this immediately for any non-local use.

---

## API overview

All routes are prefixed with `/api` and, except register and login, require a `Bearer` JWT.

| Prefix | Key endpoints |
|---|---|
| `/auth` | `POST /register`, `POST /login` |
| `/admin` | `GET /dashboard`, `/companies`, `/students`, `/drives`, `/applications`, `/reports`; `PUT` approval and blacklist actions; `DELETE /companies/<id>` |
| `/company` | `GET /dashboard`, `POST /drives`, `GET /drives/<id>/applications`, `PUT /applications/<id>`, `PUT /drives/<id>/close`, `GET/PUT /profile` |
| `/student` | `GET /dashboard`, `GET/PUT /profile`, `POST /apply/<drive_id>`, `GET /applications`, `GET /drives/search`, `POST /upload-resume`, `POST /export-csv` |

---

## Data model

`User` (role: admin / company / student) → `Company` or `Student` profile → `Drive` (belongs to a company) → `Application` (student × drive, unique pair, with status, interview date, and feedback).

---

## Configuration notes

Settings currently live in `backend/app.py`. For anything beyond local development, move these to environment variables:

- `JWT_SECRET_KEY`
- Mail server credentials (currently MailHog on `localhost:1025`)
- Redis URLs (currently `redis://localhost:6379`)
- Default admin credentials

---

## Author

**Mridula J.B** · [GitHub](https://github.com/mridu1a) · [LinkedIn](https://www.linkedin.com/in/mridula-jb)
