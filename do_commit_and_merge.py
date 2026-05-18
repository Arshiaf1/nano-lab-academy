#!/usr/bin/env python3
"""
Helper script to commit and merge stage2 implementation.
"""
import subprocess
import os
import sys

def run_git(cwd, *args):
    """Run a git command in the given directory."""
    cmd = ["git", *args]
    print(f"Running in {cwd}: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result

def main():
    topic_dir = r"c:\Users\asus\nano-lab-academy.worktrees\agents-router-stage2-endpoints-implementation"
    main_dir = r"c:\Users\asus\nano-lab-academy"
    
    print("=" * 60)
    print("STEP 1: Check status in topic branch")
    print("=" * 60)
    result = run_git(topic_dir, "status", "--short")
    if result.returncode != 0:
        print("ERROR: Failed to get status")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("STEP 2: Check for uncommitted changes")
    print("=" * 60)
    result = run_git(topic_dir, "status", "--porcelain")
    if result.returncode != 0:
        print("ERROR: Failed to check status")
        sys.exit(1)
    
    has_changes = result.stdout.strip()
    if has_changes:
        print(f"Found changes:\n{has_changes}")
        print("\n" + "=" * 60)
        print("STEP 3: Stage and commit changes")
        print("=" * 60)
        
        # Stage all changes
        result = run_git(topic_dir, "add", "-A")
        if result.returncode != 0:
            print("ERROR: Failed to stage changes")
            sys.exit(1)
        
        # Get diff for commit message
        result = run_git(topic_dir, "diff", "--cached", "--stat")
        if result.returncode != 0:
            print("ERROR: Failed to get diff")
            sys.exit(1)
        
        # Commit
        commit_msg = "feat: implement Stage 2 enrollment, tasks, and evaluations endpoints\n\n" \
                     "- Add stage2.py router with learner endpoints (enroll, status, task submit)\n" \
                     "- Add admin.py with lab partner and task management endpoints\n" \
                     "- Extend store.py with Stage2 data models and persistence\n" \
                     "- Add serializers and Stage 3 unlock logic in services.py\n" \
                     "- Integrate stage2 router into main application\n" \
                     "- Seed lab partners and tasks on startup\n"
        result = run_git(topic_dir, "commit", "-m", commit_msg)
        if result.returncode != 0:
            print("ERROR: Failed to commit")
            sys.exit(1)
        
        print("\n✓ Commit successful")
    else:
        print("No uncommitted changes found")
    
    print("\n" + "=" * 60)
    print("STEP 4: Get current branch")
    print("=" * 60)
    result = run_git(topic_dir, "branch", "--show-current")
    if result.returncode != 0:
        print("ERROR: Failed to get branch name")
        sys.exit(1)
    topic_branch = result.stdout.strip()
    print(f"Topic branch: {topic_branch}")
    
    print("\n" + "=" * 60)
    print("STEP 5: Merge into main branch")
    print("=" * 60)
    result = run_git(main_dir, "merge", topic_branch, "--no-edit")
    if result.returncode != 0:
        print("ERROR: Merge failed")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(1)
    
    print("✓ Merge successful")
    
    print("\n" + "=" * 60)
    print("STEP 6: Verify merge")
    print("=" * 60)
    result = run_git(main_dir, "status", "--porcelain")
    print(f"Main branch status:\n{result.stdout}")
    
    result = run_git(main_dir, "merge-base", "--is-ancestor", topic_branch, "HEAD")
    if result.returncode == 0:
        print(f"✓ Topic branch {topic_branch} is ancestor of HEAD")
    else:
        print(f"⚠ Topic branch may not be fully merged")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Commit and merge completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
