# 🧪 Nano Lab Academy

> A complete learning platform that takes anyone from **zero to job-ready lab professional** through a gamified, three-stage journey.
>
> **Online Mastery → Hands-On Lab Contribution → Job/Internship Marketplace**

---

## 🚀 What It Does

Nano Lab Academy trains users for real-world laboratory careers. Learners choose a career track (**Operator, Supervisor, or Calibration Leader**), unlock content by meeting high standards (**≥80% scores**), practice in partner labs with supervisor evaluations, and finally get matched with contracted labs for internships or jobs.

---

# ✨ Core Features

### 🎥 Stage 1 — Online Mastery

* Video lessons
* Downloadable notes
* Interactive quizzes
* Assignments & final exams
* XP, streaks, badges, and leaderboards

### 🔬 Stage 2 — Hands-On Lab

* Face-to-face lab contribution
* Digital task tracking
* Supervisor evaluations
* Unlocks only after Stage 1 completion

### 💼 Stage 3 — Job Marketplace

* Internship & job board
* Verified learner profiles
* Lab partner matching system

### 🎟️ Career Plans

| Plan       | Focus                    |
| ---------- | ------------------------ |
| **Basics** | Operator                 |
| **Pro**    | Supervisor               |
| **Ultra**  | Calibration / Lab Leader |

Each plan contains a completely different curriculum — not simple feature gating.

### 🔒 Progression System

* Stage 2 requires **≥80%** in all Stage 1 content
* Stage 3 requires **≥80%** supervisor evaluation

### 🏅 Gamification Engine

* XP system
* Daily streaks
* Skill badges
* Competitive leaderboards

### 📄 Certificates

* Section completion confirmations
* Final verifiable certificate
* QR-code verification system

### 🆓 Freemium Preview

* 2–3 free introductory lessons per plan
* Public access without authentication

### ⏳ Time-Limited Progress

* Stage deadlines
* Extension/retry system

### 🔐 Premium Content Protection

* Signed video URLs
* Watermarked content
* Anti-download headers
* Protected premium media

---

# 🧑‍💻 User Roles

| Role                       | Description                               |
| -------------------------- | ----------------------------------------- |
| **Learner**                | Studies, completes labs, applies for jobs |
| **Instructor**             | Creates lessons, quizzes, and assignments |
| **Lab Supervisor**         | Evaluates Stage 2 performance             |
| **Employer / Lab Partner** | Posts internships & job opportunities     |
| **Admin**                  | Full platform management & analytics      |

---

# 🛠️ Tech Stack

| Layer              | Technology                                     |
| ------------------ | ---------------------------------------------- |
| **Frontend**       | Next.js 14, TypeScript, Tailwind CSS, Zustand  |
| **Backend**        | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic |
| **Database**       | PostgreSQL / SQLite                            |
| **Cache**          | Redis                                          |
| **File Storage**   | AWS S3 / ArvanCloud                            |
| **Video Hosting**  | Vimeo / Bunny Stream                           |
| **Authentication** | JWT, OAuth2, RBAC, Argon2                      |
| **Payments**       | Zarinpal / Stripe                              |
| **CI/CD**          | GitHub Actions, Docker                         |

---

# 📁 Project Structure

```bash
nano-lab-academy/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── routers/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── (learner)/
│   │   ├── admin/
│   │   └── api/
│   ├── components/
│   ├── public/
│   └── package.json
│
├── docker-compose.yml
└── README.md
```

---

# ⚡ Quick Start

## 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/nano-lab-academy.git
cd nano-lab-academy
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

---

## 3️⃣ Environment Variables

Create a `.env` file inside `/backend`:

```env
DATABASE_URL=sqlite+aiosqlite:///./nano_lab.db
JWT_SECRET=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

---

## 4️⃣ Run Backend

```bash
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

### Backend URLs

* API → `http://localhost:8000`
* Swagger Docs → `http://localhost:8000/docs`

---

## 5️⃣ Frontend Setup

```bash
cd ../frontend

npm install

cp .env.example .env.local
```

Set:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Run development server:

```bash
npm run dev
```

Frontend will run at:

```txt
http://localhost:3000
```

---

# 📖 Technical Documentation

The complete architecture, database schema, API endpoints, security rules, and business logic are documented in:

```txt
TECHNICAL_SPEC.md
```

This file is the **single source of truth** for developers and AI coding agents.

---

# 🤖 AI Agent Development Rules

1. Read `TECHNICAL_SPEC.md` before generating code
2. Build one feature at a time
3. Create database models before endpoints
4. Stabilize APIs before frontend implementation
5. Use Docker Compose for PostgreSQL + Redis if needed
6. Security requirements are mandatory:

   * Argon2 hashing
   * JWT authentication
   * RBAC permissions
   * Input validation

---

# 🗺️ Development Roadmap

## ✅ Completed

* [x] Project scaffolding
* [x] Database design
* [x] Authentication system
* [x] Admin content management
* [x] Learner course progression
* [x] Gamification system
* [x] Stage unlock logic
* [x] Lab contribution tracking
* [x] Job marketplace
* [x] Mock payment integration
* [x] Certificate generation

## 🚧 Upcoming

* [ ] Real payment gateways
* [ ] Advanced DRM protection
* [ ] Watermark security
* [ ] Production deployment
* [ ] Scaling infrastructure

---

# 📜 License

```txt
MIT License
```

Use freely, contribute back, or build your own academy platform.

---

# 👨‍💻 Built With

**Built by a solo founder + AI 🚀**
