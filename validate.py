#!/usr/bin/env python3
"""Lightweight app validation script."""
import sys
import os
import py_compile

# Step 1: Compile all app modules
print("=== COMPILING APP MODULES ===")
app_dir = "app"
compiled_count = 0

for file in sorted(os.listdir(app_dir)):
    if file.endswith(".py") and not file.startswith("__pycache__"):
        filepath = os.path.join(app_dir, file)
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"✓ {file}")
            compiled_count += 1
        except py_compile.PyCompileError as e:
            print(f"✗ {file}: {e}")
            sys.exit(1)

# Step 2: Import app.main
print()
print("=== IMPORTING app.main ===")
try:
    from app import main
    print("✓ app.main imported successfully")
except Exception as e:
    print(f"✗ Failed to import app.main: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Extract and display routes
print()
print("=== ROUTE ANALYSIS ===")
if hasattr(main, "app") and hasattr(main.app, "routes"):
    routes = main.app.routes
    print(f"Total routes: {len(routes)}")
    print()
    
    # Filter routes containing /stage2, /admin/lab-partners, or /admin/stage2
    target_keywords = ["/stage2", "/admin/lab-partners", "/admin/stage2"]
    filtered_routes = []
    
    for route in routes:
        route_path = str(route.path) if hasattr(route, "path") else str(route)
        for keyword in target_keywords:
            if keyword in route_path:
                filtered_routes.append(route_path)
                break
    
    if filtered_routes:
        print(f"Matching routes ({len(filtered_routes)}):")
        for route in sorted(set(filtered_routes)):
            print(f"  • {route}")
    else:
        print("No matching routes found")
else:
    print("Could not access routes from app.main")
    
print()
print("✓ Validation complete")
