```markdown
# 🧪 Nano Lab Academy

A complete learning platform that takes anyone from **zero to job‑ready lab professional** through a gamified, three‑stage journey:  
**Online Mastery → Hands‑On Lab Contribution → Job/Internship Marketplace.**

---

## 🚀 What It Does

Nano Lab Academy trains users for real-world laboratory careers. Learners choose a career track (Operator, Supervisor, or Calibration Leader), unlock content by meeting high standards (≥80% scores), practice in partner labs with supervisor evaluations, and finally get matched with contracted labs for internships or jobs.

### ✨ Core Features

- **🎥 Stage 1 – Online Mastery**: Video lessons, downloadable notes, interactive quizzes, assignments, and a final exam. Gamified with XP, streaks, badges, and leaderboards.
- **🔬 Stage 2 – Hands‑On Lab**: Face‑to‑face lab contribution tracked digitally. Supervisors evaluate task performance. Unlocked only after passing Stage 1.
- **💼 Stage 3 – Job Marketplace**: Curated job/internship board that matches verified, badge‑carrying learners with partner labs.
- **🎟️ Three Career Plans**: Basics (Operator), Pro (Supervisor), Ultra (Calibration/Leader). Each plan has its own full curriculum, not just feature gating.
- **🔒 Stage Gating**: Progression is earned. Stage 2 needs ≥80% in all Stage 1 work. Stage 3 needs ≥80% supervisor rating.
- **🏅 Gamification Engine**: XP, streaks, badges, leaderboards. Badges unlock based on skills (e.g., “PCR Specialist”, “Lab Math Whiz”).
- **📄 Certificates**: Section‑level confirmations and a final verifiable certificate (with QR code) upon full completion.
- **🆓 Freemium Previews**: 2‑3 free introductory videos per plan visible to unauthenticated users.
- **⏳ Stage Deadlines**: Stage 1 must be finished within a timeframe. Overdue? Pay a small fee to extend or retake exams.
- **🔐 Premium Protection**: Videos served with signed URLs, watermarked with learner identity, anti‑download headers. Notes are free to download but watermarked.

---

## 🧑‍💻 User Roles

| Role | Description |
|------|-------------|
| **Learner** | Enrolls, studies, completes labs, applies for jobs. |
| **Instructor** (via Admin) | Creates content, grades assignments, manages quizzes. |
| **Lab Supervisor** (via Admin) | Evaluates Stage 2 performance, signs off on readiness. |
| **Employer / Lab Partner** | Posts job/internship openings, reviews applicants. |
| **Admin** | Full control – users, content, payments, analytics, overrides. |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Zustand |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| **Database** | PostgreSQL (prod) / SQLite (dev) |
| **Cache** | Redis (for rate limiting, leaderboards, sessions) |
| **File Storage** | AWS S3 / ArvanCloud (notes, certificates, avatars) |
| **Video** | Vimeo / Bunny Stream (private, tokenized) |
| **Authentication** | Argon2 password hashing, JWT (OAuth2), RBAC |
| **Payments** | Gateway integration (Zarinpal / Stripe) – mocked in early MVP |
| **CI/CD** | GitHub Actions, Docker (optional) |

---

## 📁 Project Structure

```
nano-lab-academy/
├── backend/
│   ├── alembic/              # DB migrations
│   ├── app/
│   │   ├── routers/         # auth, admin, learner, stage2, stage3, payments, gamification
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── database.py      # Async engine & session
│   │   ├── auth.py          # JWT & RBAC dependencies
│   │   └── main.py          # FastAPI app entry
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js App Router pages
│   │   ├── (learner)/       # Learner routes
│   │   ├── admin/           # Admin dashboard
│   │   └── api/             # Frontend API utilities
│   ├── components/          # Reusable UI
│   ├── public/
│   └── package.json
├── docker-compose.yml       # Optional, for PostgreSQL + Redis
└── README.md
```

---

## ⚡ Quick Start (Local Development)

### 1. Clone & Install

```bash
git clone https://github.com/your-username/nano-lab-academy.git
cd nano-lab-academy

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` in `backend/`:

```
DATABASE_URL=sqlite+aiosqlite:///./nano_lab.db
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

### 3. Run Backend

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Backend will be live at `http://localhost:8000`.  
Swagger docs at `http://localhost:8000/docs`.

### 4. Frontend

```bash
cd ../frontend
npm install
cp .env.example .env.local  # set NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev
```

Open `http://localhost:3000`.

---

## 📖 Full Technical Documentation

For AI agents and developers, the complete database schema, API endpoints, business logic, security measures, and build plan are detailed in [`TECHNICAL_SPEC.md`](./TECHNICAL_SPEC.md).  
**Always refer to that file when generating code or understanding any system behaviour.**

---

## 🤖 How AI Agents Should Use This Repo

1. **Read `TECHNICAL_SPEC.md` first** – it contains the single source of truth for models, endpoints, and rules.
2. Code generation is done **one feature at a time**, following the prompts in `/docs/prompts/` or the sequence described in the development plan.
3. Backend models and migrations must be written before building endpoints.
4. Frontend pages should be created only after the corresponding API is stable.
5. Use the provided Docker Compose file if you need PostgreSQL/Redis; otherwise SQLite is fine for MVP.
6. All security rules (Argon2, JWT, RBAC, input validation) are non‑negotiable – implement them exactly as specified.

---

## 🗺️ Development Roadmap

- [x] Phase 0: Project scaffolding & database design
- [x] Phase 1: Auth, admin content CRUD, learner course viewing & progress
- [x] Phase 2: Gamification, stage‑unlock logic, free downloads
- [x] Phase 3: Stage 2 (lab contribution) tracking, Stage 3 job board
- [x] Phase 4: Payment integration (mock), certificate generation, admin alerts
- [ ] Phase 5: Real payment gateway, advanced security (DRM, watermarking), production deployment

---

## 📜 License

MIT – use this for your own lab academy, or contribute back!

---

**Built by a solo founder + AI.**  
Questions? Open an issue or reach out. 🚀
```
