# Expected Execution Results

## Script 1: Route Paths

When running `test_script_1.py`, the output will be:

```
=== Route Paths ===
  /
  /quizzes/{quiz_id}
  /quizzes/{quiz_id}/attempt
  /assignments/my
  /assignments/{assignment_id}
  /assignments/{assignment_id}/submit
  /lessons/{lesson_id}/progress
  /gamification/status
  /gamification/leaderboard
Total routes: 9
```

### Explanation:
- The `app.route_paths()` method returns all registered routes in the application
- Routes come from three routers:
  - **Learner router**: Quiz and assignment endpoints
  - **Admin router**: (not shown in details, appears empty)
  - **Gamification router**: Gamification status and leaderboard endpoints
  - Plus the root health check route

---

## Script 2: Learner Activities and Gamification

### Step 2: Submit Lesson Progress for User 'u1'

**Function called**: `update_lesson_progress(lesson_id=1, payload={"user_id": "u1", "completed": True})`

**Expected output**:
```json
{
  "lesson_id": 1,
  "user_id": "u1",
  "completed": true,
  "xp_awarded": 10,
  "current_streak": 1,
  "badge_ids": []
}
```

**Behind the scenes**:
- Lesson completion awards 10 XP
- Streak is initialized to 1 (first activity)
- No badges awarded yet (thresholds not met)
- Activity is recorded in the gamification database

---

### Step 3: Submit Assignment for User 'u1'

**Function called**: `submit_assignment(assignment_id=1, payload={"user_id": "u1", "text_answer": "This is my project brief..."})`

**Expected output**:
```json
{
  "submission_id": 2,
  "score": null,
  "passed": null,
  "xp_awarded": 20,
  "badge_ids": [],
  "submission": {
    "id": 2,
    "kind": "assignment",
    "user_id": "u1",
    "related_id": 1,
    "status": "pending_review",
    "score": null,
    "passed": null,
    "xp_awarded": 20,
    "manual_review_required": true,
    "payload": {
      "assignment_id": 1,
      "assignment_title": "Project Brief",
      "file_url": null,
      "text_answer": "This is my project brief submission for the course.",
      "pass_threshold": 70.0
    },
    "badge_ids": [],
    "created_at": "2024-XX-XX HXX:XX:XX",
    "updated_at": "2024-XX-XX HXX:XX:XX"
  }
}
```

**Behind the scenes**:
- Assignment submission awards 20 XP
- Status is "pending_review" (manual grading needed)
- Streak is now 2 (consecutive activities)
- Still no badges (not enough XP or activities)
- Activity recorded in gamification database

---

### Step 4: Get Gamification Status for User 'u1'

**Function called**: `get_user_status("u1")`

**Expected output**:
```json
{
  "user_id": "u1",
  "total_xp": 30,
  "current_streak": 2,
  "badges": []
}
```

**Calculation**:
- Total XP = 10 (lesson) + 20 (assignment) = 30 XP
- Current streak = 2 (two activities on same/consecutive days)
- Badges = [] (no badges earned yet because:
  - quiz_perfect_5: 0 perfect quizzes
  - quiz_pass_10: 0 quizzes passed
  - assignment_pass_3: 0 assignments passed (status pending)
  - streak_7: need 7-day streak, have 2
  - xp_500: need 500 XP, have 30)

---

### Step 5: Get Weekly Leaderboard

**Function called**: `get_leaderboard("weekly")`

**Expected output**:
```
Weekly Leaderboard:
  1. User: u1, XP Earned: 30
```

**Calculation**:
- Queries all XP earned in the last 7 days
- User 'u1' is the only user with activities in the database
- XP earned this week = 30 (all activities were just created)
- Leaderboard shows top 10 users, sorted by XP descending

---

## Summary Statistics for User 'u1'

| Metric | Value |
|--------|-------|
| Total XP | 30 |
| Current Streak | 2 days |
| Badges Earned | 0 |
| Activities | 2 (1 lesson, 1 assignment) |
| Weekly Rank | #1 |
| Weekly XP | 30 |

---

## How to Run the Scripts

### Option 1: Direct Python Execution
```bash
cd C:\Users\asus\nano-lab-academy.worktrees\agents-gamification-module-creation
python test_script_1.py
python test_script_2.py
```

### Option 2: From PowerShell
```powershell
cd "C:\Users\asus\nano-lab-academy.worktrees\agents-gamification-module-creation"
python test_script_1.py
python test_script_2.py
```

### Option 3: From Command Prompt
```cmd
cd C:\Users\asus\nano-lab-academy.worktrees\agents-gamification-module-creation
python test_script_1.py
python test_script_2.py
```

---

## Key Implementation Details

### Endpoints Demonstrated

1. **Lesson Progress Endpoint** (`POST /lessons/{lesson_id}/progress`)
   - Accepts `user_id` and `completed` boolean
   - Awards 10 XP when lesson is completed
   - Updates user streak
   - Records activity event

2. **Assignment Submission Endpoint** (`POST /assignments/{assignment_id}/submit`)
   - Accepts `user_id`, `file_url`, or `text_answer`
   - Awards 20 XP immediately (submission reward)
   - Sets status to "pending_review" for manual grading
   - Updates streak
   - Records activity event

3. **Gamification Status Endpoint** (`GET /gamification/status`)
   - Returns total XP, current streak, and earned badges
   - Takes `user_id` as query parameter

4. **Leaderboard Endpoint** (`GET /gamification/leaderboard`)
   - Returns top 10 users by XP for the specified period
   - Accepts period: "daily", "weekly", "monthly", "all_time"
   - Default period: "weekly"

### Gamification Features

- **XP System**: Activities award XP points
  - Lesson completion: 10 XP
  - Assignment submission: 20 XP
  - Quiz perfect score (100%): 100 XP
  - Quiz passing (≥70%): 50 XP

- **Streaks**: Track consecutive days of activity

- **Badges**: Unlocked based on thresholds
  - quiz_perfect_5: 5 perfect quiz scores
  - quiz_pass_10: 10 quizzes passed
  - assignment_pass_3: 3 assignments passed
  - streak_7: 7-day learning streak
  - xp_500: 500 total XP earned

- **Leaderboards**: Period-based rankings (daily/weekly/monthly/all-time)
