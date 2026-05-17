#!/usr/bin/env python3
import py_compile
import sys
import os

# Change to repo directory
os.chdir(r"C:\Users\asus\nano-lab-academy.worktrees\agents-gamification-module-creation")

print("=" * 60)
print("1. PYTHON COMPILE CHECK FOR APP PACKAGE")
print("=" * 60)
try:
    py_compile.compile('app', doraise=True)
    print("✓ PASS: App package compiles successfully")
except py_compile.PyCompileError as e:
    print(f"✗ FAIL: Compilation error\n{e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("2. REGISTERED ROUTES FROM APP.MAIN.APP.ROUTE_PATHS()")
print("=" * 60)
try:
    from app.main import app
    routes = app.route_paths()
    print("Registered Routes:")
    for route in routes:
        print(f"  - {route}")
    print(f"✓ PASS: {len(routes)} routes found")
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("3. DRY-RUN IMPORTS")
print("=" * 60)
try:
    import app.stage
    print("✓ PASS: app.stage imported successfully")
except Exception as e:
    print(f"✗ FAIL: app.stage import failed - {e}")
    sys.exit(1)

try:
    import app.learner_courses
    print("✓ PASS: app.learner_courses imported successfully")
except Exception as e:
    print(f"✗ FAIL: app.learner_courses import failed - {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("VALIDATION COMPLETE - ALL CHECKS PASSED")
print("=" * 60)
