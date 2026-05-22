# 🧪 Nano Lab Academy — Technical Specification

> **Single source of truth for AI agents, developers, and stakeholders.**
> Defines all models, endpoints, business logic, security protocols, and development phases.

---

# 🏗️ 1. System Architecture

| Component          | Technology                                                 |
| ------------------ | ---------------------------------------------------------- |
| **Frontend**       | Next.js 14 (App Router), TypeScript, Tailwind CSS, Zustand |
| **Backend**        | Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Alembic     |
| **Database**       | PostgreSQL 15+ (Production) / SQLite (Development)         |
| **Cache**          | Redis                                                      |
| **File Storage**   | AWS S3 / ArvanCloud                                        |
| **Video Hosting**  | Vimeo / Bunny Stream                                       |
| **Authentication** | Argon2, JWT (OAuth2), RBAC                                 |
| **Payments**       | Zarinpal / Stripe (Mocked in MVP)                          |

---

# 🗄️ 2. Database Schema

---

## 2.1 Core User & Plan

### `users`

| Field             | Type       |
| ----------------- | ---------- |
| id                | UUID       |
| email             | unique     |
| password_hash     | text       |
| full_name         | text       |
| role              | enum       |
| plan_id           | FK → plans |
| plan_active_until | datetime   |
| avatar_url        | text       |
| created_at        | datetime   |
| updated_at        | datetime   |

### `plans`

| Field         | Type                 |
| ------------- | -------------------- |
| id            | UUID                 |
| name          | basics / pro / ultra |
| description   | text                 |
| monthly_price | integer              |
| is_active     | boolean              |

---

## 2.2 Course Content

### `courses`

* id (UUID)
* plan_id (FK)
* title
* description
* order_index

### `sections`

* id (UUID)
* course_id (FK)
* title
* description
* order_index

### `lessons`

* id (UUID)
* section_id (FK)
* title
* video_provider_id
* video_duration_seconds
* notes_pdf_url
* order_index
* is_free_preview (bool)
* requires_completion (bool)

### `quizzes`

* id (UUID)
* lesson_id (nullable FK)
* section_id (nullable FK)
* title
* pass_threshold
* max_attempts

### `questions`

* id (UUID)
* quiz_id (FK)
* question_text
* question_type
* options (JSONB)
* correct_answer
* points

### `assignments`

* id (UUID)
* lesson_id (FK)
* title
* description
* max_score
* due_date

### `final_exams`

* id (UUID)
* course_id (FK)
* title
* duration_minutes
* pass_threshold
* max_attempts

---

## 2.3 Enrollments & Progress

### `enrollments`

* id (UUID)
* user_id (FK)
* course_id (FK)
* stage
* stage1_completed
* stage2_completed
* stage1_deadline
* stage1_locked
* stage2_enrollment_id

### `lesson_progress`

* id (UUID)
* user_id (FK)
* lesson_id (FK)
* watched
* watched_at

### `quiz_attempts`

* id (UUID)
* user_id (FK)
* quiz_id (FK)
* score
* passed
* attempted_at

### `assignment_submissions`

* id (UUID)
* user_id (FK)
* assignment_id (FK)
* file_url
* text_answer
* score
* graded_by
* graded_at

### `exam_attempts`

* id (UUID)
* user_id (FK)
* exam_id (FK)
* score
* passed
* started_at
* submitted_at

---

## 2.4 Stage 2 — Lab Contribution

### `stage2_tasks`

* id (UUID)
* plan_id (FK)
* title
* description

### `lab_partners`

* id (UUID)
* name
* address
* contact_email
* is_active

### `stage2_enrollments`

* id (UUID)
* user_id (FK)
* lab_partner_id (FK)
* status
* start_date
* end_date

### `stage2_task_evaluations`

* id (UUID)
* stage2_enrollment_id (FK)
* task_id (FK)
* supervisor_id (FK)
* score
* comments
* evaluated_at

### `final_supervisor_ratings`

* id (UUID)
* stage2_enrollment_id (FK)
* supervisor_id (FK)
* overall_score
* approved
* signed_at

---

## 2.5 Gamification & Certificates

### `badges`

* id (UUID)
* name
* description
* image_url
* criteria_json

### `user_badges`

* id (UUID)
* user_id (FK)
* badge_id (FK)
* awarded_at

### `user_xp`

* id (UUID)
* user_id (FK)
* amount
* source
* created_at

### `user_streaks`

* id (UUID)
* user_id (FK)
* streak_count
* last_activity_date

### `certifications`

* id (UUID)
* user_id (FK)
* course_id (FK)
* issued_at
* cert_url
* metadata_json

---

## 2.6 Marketplace & Payments

### `job_listings`

* id (UUID)
* employer_id (FK)
* title
* description
* required_badges (JSONB)
* location
* type (internship/job)
* is_active

### `applications`

* id (UUID)
* user_id (FK)
* job_id (FK)
* cover_letter
* status
* applied_at

### `payments`

* id (UUID)
* user_id (FK)
* amount
* currency
* payment_gateway_ref
* status
* plan_id (nullable FK)
* for_stage_unlock
* created_at

---

# 🌐 3. API Endpoints

Base URL:

```txt id="skw93m"
/api/v1
```

---

## 3.1 Authentication

| Method | Endpoint         | Description          |
| ------ | ---------------- | -------------------- |
| POST   | `/auth/register` | Register new user    |
| POST   | `/auth/login`    | Login                |
| POST   | `/auth/refresh`  | Refresh access token |

---

## 3.2 Learner — Courses & Progress

| Method | Endpoint                       |
| ------ | ------------------------------ |
| GET    | `/courses/available`           |
| POST   | `/enrollments`                 |
| GET    | `/enrollments/my`              |
| GET    | `/courses/my`                  |
| GET    | `/lessons/{id}`                |
| POST   | `/lessons/{id}/progress`       |
| GET    | `/lessons/{id}/download-notes` |
| GET    | `/quizzes/{id}`                |
| POST   | `/quizzes/{id}/attempt`        |
| GET    | `/assignments/{id}`            |
| POST   | `/assignments/{id}/submit`     |
| GET    | `/exams/{course_id}/final`     |
| POST   | `/exams/{course_id}/start`     |
| POST   | `/exams/{course_id}/submit`    |

---

## 3.3 Stage Unlocking

| Method | Endpoint              |
| ------ | --------------------- |
| GET    | `/stage/status`       |
| POST   | `/stage/check-stage1` |
| POST   | `/stage/check-stage2` |

---

## 3.4 Stage 2 — Lab

| Method | Endpoint                         |
| ------ | -------------------------------- |
| GET    | `/stage2/lab-partners`           |
| POST   | `/stage2/enroll`                 |
| GET    | `/stage2/my-status`              |
| POST   | `/stage2/tasks/{task_id}/submit` |

---

## 3.5 Stage 3 — Jobs

| Method | Endpoint           |
| ------ | ------------------ |
| GET    | `/jobs`            |
| GET    | `/jobs/{id}`       |
| POST   | `/jobs/{id}/apply` |
| GET    | `/applications/my` |

---

## 3.6 Gamification

| Method | Endpoint                    |
| ------ | --------------------------- |
| GET    | `/gamification/status`      |
| GET    | `/gamification/leaderboard` |

---

## 3.7 Certifications

| Method | Endpoint                   |
| ------ | -------------------------- |
| POST   | `/sections/{id}/confirm`   |
| GET    | `/certifications/my`       |
| POST   | `/certifications/generate` |

---

## 3.8 Payments

| Method | Endpoint                    |
| ------ | --------------------------- |
| POST   | `/payments/create-checkout` |
| POST   | `/payments/webhook`         |

---

## 3.9 Admin Endpoints

### CRUD Management

* Plans
* Courses
* Sections
* Lessons
* Quizzes
* Assignments
* Exams

### Admin Features

* User management
* Lab partner management
* Payment monitoring
* Analytics dashboard
* Application review
* Evaluation overrides

---

# 🔐 4. Security Implementation

## Authentication

* Argon2id hashing
* JWT HS256
* 15 min access token
* 7 day refresh token
* httpOnly cookies

## RBAC

All protected endpoints use:

```python id="ax2p9w"
get_current_user + RoleChecker(required_role)
```

## Security Protections

* SQL injection prevention
* Pydantic validation
* React auto escaping
* CSRF protection
* Redis rate limiting

---

## Premium Content Protection

### Videos

* Signed URLs
* Short TTL
* Domain-locked embeds
* Optional DRM
* User-ID watermarking

### Notes

* Presigned S3 URLs
* Dynamic watermarking
* 5-minute expiration

---

# ⚙️ 5. Business Logic Rules

---

## 5.1 Stage 1 Completion

Requirements:

* All quizzes passed
* All assignments scored ≥80
* Final exam ≥80

Result:

```txt id="a7d2pl"
stage1_completed = true
stage = 2
```

---

## 5.2 Stage 1 Deadline

### Default

```txt id="6jjv41"
90-day completion window
```

### Expired

```txt id="7owmop"
stage1_locked = true
```

### Unlock

* One-time payment
* +30 day extension
* Unlocks premium access again

---

## 5.3 Stage 2 → Stage 3

Requirements:

* Supervisor approval
* Final score ≥80

Result:

```txt id="ulz1z7"
stage2_completed = true
stage = 3
```

---

## 5.4 Freemium Rules

* Maximum 3 free preview lessons
* Guest users only access previews
* Locked lessons return:

```json id="q54otf"
{
  "locked": true
}
```

---

## 5.5 Free Downloads

Any authenticated learner can download lesson notes.

---

## 5.6 Certificate Issuance

Certificate generation requires:

* All sections completed
* All tasks ≥80
* Stage 2 passed

---

# 🎮 6. Gamification Rules

| Action               | XP   |
| -------------------- | ---- |
| Lesson watched       | +10  |
| Quiz passed          | +50  |
| Perfect quiz         | +100 |
| Assignment submitted | +20  |
| Final exam passed    | +200 |

---

## 🔥 Streaks

* Consecutive active days increase streak
* Broken streak resets to zero

---

## 🏅 Badges

Automatically awarded based on achievements.

Examples:

* Quiz Master
* PCR Specialist
* Lab Math Whiz

---

## 📈 Leaderboards

* Weekly leaderboard
* Monthly leaderboard
* Cached in Redis

---

# 🛠️ 7. Admin Panel Features

### Dashboard

* Learners per stage
* MRR
* Churn
* Recent signups

### Financial Analytics

* Revenue tracking
* Plan performance
* Payment logs

### Alerts

* Failed payments
* Security anomalies
* Service health monitoring

### Content Builder

* Drag-and-drop course builder
* Quiz banks
* Assignment management

### Overrides

* Deadline extensions
* Supervisor score adjustments
* Audit reason logs

---

# 🚀 8. MVP Build Phases

| Phase       | Description                              |
| ----------- | ---------------------------------------- |
| **Phase 0** | Project setup, DB models, migrations     |
| **Phase 1** | Auth, admin CRUD, learner progress       |
| **Phase 2** | Stage unlocks, downloads, certifications |
| **Phase 3** | Lab tracking & job marketplace           |
| **Phase 4** | Payments, analytics, security hardening  |
| **Phase 5** | Testing & deployment prep                |

---

# 📌 Final Rule

> This specification is the blueprint for all generated code.
> Any AI agent contributing to this repository must strictly follow all models, endpoints, and rules defined here.
