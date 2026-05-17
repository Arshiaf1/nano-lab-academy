# Nano Lab Academy FastAPI Backend

FastAPI backend for the Nano Lab Academy project with comprehensive data models for a complete learning platform.

## Project Structure

```
.
├── main.py              # FastAPI application entry point
├── database.py          # SQLAlchemy async database configuration
├── models.py            # SQLAlchemy ORM models for all entities
├── requirements.txt     # Python dependencies
├── alembic/            # Database migrations
│   ├── env.py          # Alembic async configuration
│   └── versions/       # Migration scripts
├── alembic.ini         # Alembic configuration file
└── setup.py            # Project setup script
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Alembic Directories

Run the setup script to create the necessary directory structure and Alembic configuration:

```bash
python setup.py
```

### 3. Run Migrations

Apply all database migrations to create the schema:

```bash
alembic upgrade head
```

### 4. Run the Server

Start the FastAPI server with auto-reload enabled:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or run it directly:

```bash
python main.py
```

## API Endpoints

### Health Check
- **URL**: `/api/health`
- **Method**: GET
- **Response**: `{"status":"ok"}`

### Root
- **URL**: `/`
- **Method**: GET
- **Response**: `{"message":"Nano Lab Academy Backend is running"}`

## Database Models

### Core Models
- **User**: User accounts with roles (learner/admin/supervisor/employer), subscriptions
- **Plan**: Subscription tiers (basics/pro/ultra) with pricing

### Course Content
- **Course**: Courses associated with plans
- **Section**: Course sections with lessons
- **Lesson**: Individual lessons with videos and notes
- **Quiz**: Quizzes at section/lesson level with questions
- **Question**: Quiz questions with multiple types
- **Assignment**: Assignments for lessons
- **FinalExam**: Course final exams

### Enrollment & Progress
- **Enrollment**: Course enrollment tracking with stage progression
- **LessonProgress**: Individual lesson watch tracking
- **QuizAttempt**: Quiz attempt records with scores
- **AssignmentSubmission**: Assignment submissions with grading
- **ExamAttempt**: Final exam attempt records

### Stage 2 Practical Training
- **Stage2Task**: Practical tasks for plans
- **LabPartner**: External lab partners/employers
- **Stage2Enrollment**: User enrollment in lab partnerships
- **Stage2TaskEvaluation**: Supervisor evaluation of tasks
- **FinalSupervisorRating**: Final supervisor approval

### Gamification
- **Badge**: Achievement badges with criteria
- **UserBadge**: Badge awards to users
- **UserXP**: Experience points tracking
- **UserStreak**: Activity streak tracking

### Achievements
- **Certification**: Course completion certificates

### Job Listings
- **JobListing**: Job/internship postings by employers
- **Application**: Job applications from users

### Payments
- **Payment**: Payment transaction records for subscriptions

## Database Configuration

The project uses:
- **Database**: SQLite (nano_lab.db)
- **ORM**: SQLAlchemy with async support
- **Driver**: aiosqlite
- **Migrations**: Alembic with async support

Database URL: `sqlite+aiosqlite:///./nano_lab.db`

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sqlalchemy`: ORM with async support
- `alembic`: Database migrations
- `pydantic`: Data validation
- `python-jose`: JWT tokens
- `passlib[argon2]`: Password hashing
- `python-multipart`: Multipart form data
- `aiosqlite`: Async SQLite driver

## Development

### Access Interactive API Documentation

After starting the server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Creating New Models

1. Add your model to `models.py` inheriting from `Base`
2. Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

3. Apply the migration:

```bash
alembic upgrade head
```

### Rolling Back Migrations

To revert to a previous migration:

```bash
alembic downgrade -1  # Go back one migration
alembic downgrade <revision_id>  # Go to specific revision
```

## Environment Variables

To use environment variables for configuration, update `database.py`:

```python
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nano_lab.db")
```

Then set the variable:

```bash
# On Windows
set DATABASE_URL=sqlite+aiosqlite:///./nano_lab.db

# On Linux/Mac
export DATABASE_URL=sqlite+aiosqlite:///./nano_lab.db
```

## Schema Overview

### Enumerations

- **UserRole**: learner, admin, supervisor, employer
- **PlanType**: basics, pro, ultra
- **QuestionType**: multiple_choice, true_false, short_answer
- **Stage2Status**: pending, active, completed
- **JobType**: internship, job
- **ApplicationStatus**: pending, reviewed, accepted, rejected
- **PaymentStatus**: initiated, paid, failed

### Relationships

All relationships are properly configured with:
- Foreign key constraints
- Cascade deletes where appropriate
- Back-references for easy relationship navigation
- UUID primary keys throughout

## Notes

- All timestamps use UTC
- UUIDs are used as primary keys across all tables
- Foreign key relationships maintain referential integrity
- Enums provide type safety for select fields
- JSON fields support flexible metadata storage
