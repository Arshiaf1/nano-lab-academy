#!/usr/bin/env python
"""Test script to demonstrate learner endpoint functions and gamification."""
import sys
sys.path.insert(0, '.')

from app.main import app
from app.learner_courses import update_lesson_progress, submit_assignment
from app.gamification import get_user_status, get_leaderboard
import json

print("=" * 70)
print("STEP 1: Display all available routes")
print("=" * 70)
paths = app.route_paths()
for path in paths:
    print(f'  {path}')
print(f'\nTotal routes: {len(paths)}\n')

print("=" * 70)
print("STEP 2: Submit lesson progress activity for user 'u1'")
print("=" * 70)
lesson_result = update_lesson_progress(lesson_id=1, payload={
    "user_id": "u1",
    "completed": True
})
print(f"Result: {json.dumps(lesson_result, indent=2)}\n")

print("=" * 70)
print("STEP 3: Submit assignment for user 'u1'")
print("=" * 70)
assignment_result = submit_assignment(assignment_id=1, payload={
    "user_id": "u1",
    "text_answer": "This is my project brief submission for the course."
})
print(f"Result: {json.dumps(assignment_result, indent=2, default=str)}\n")

print("=" * 70)
print("STEP 4: Get gamification status for user 'u1'")
print("=" * 70)
status = get_user_status("u1")
print(f"Result: {json.dumps(status, indent=2)}\n")

print("=" * 70)
print("STEP 5: Get weekly leaderboard")
print("=" * 70)
leaderboard = get_leaderboard("weekly")
print(f"Weekly Leaderboard:")
for rank, entry in enumerate(leaderboard, 1):
    print(f"  {rank}. User: {entry['user_id']}, XP Earned: {entry['xp_earned']}")
print()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"✓ User u1 total XP: {status['total_xp']}")
print(f"✓ User u1 current streak: {status['current_streak']}")
print(f"✓ User u1 badges earned: {len(status['badges'])} badge(s)")
if status['badges']:
    for badge in status['badges']:
        print(f"  - {badge['name']}: {badge['description']}")
print(f"✓ Weekly leaderboard top entry: {leaderboard[0]['user_id'] if leaderboard else 'None'}")
