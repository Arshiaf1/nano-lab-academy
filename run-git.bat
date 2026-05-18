@echo off
cd C:\Users\asus\nano-lab-academy.worktrees\agents-job-listings-api-router-setup
echo === Git Status ===
git status --short
echo.
echo === Recent Commits ===
git log --oneline -10
echo.
echo === Stage and Commit ===
git add -A
git commit -m "stage3: Implement job listings and applications router" -m "Add Stage 3 job marketplace endpoints:
- GET /jobs with required_badges filter
- GET /jobs/{id} detail view
- POST /jobs/{id}/apply with badge requirement validation
- GET /applications/my for user applications
- Admin CRUD for job listings and application status management

Models: JobListing, JobApplication with in-memory storage.
Integrates with existing badge system for hire eligibility."
echo.
echo === After Commit ===
git status --short
git log --oneline -1
