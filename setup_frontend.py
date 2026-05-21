#!/usr/bin/env python3
import os
import json

# Get the root directory
root = r"c:\Users\asus\nano-lab-academy.worktrees\agents-frontend-dashboard-courses-lessons-pages\frontend"

# Create directories
dirs = [
    "",
    "app",
    "components", 
    "lib",
    "public",
]

for d in dirs:
    path = os.path.join(root, d)
    os.makedirs(path, exist_ok=True)
    print(f"Created: {path}")

# package.json
package_json = {
    "name": "nano-lab-academy-frontend",
    "version": "0.1.0",
    "private": True,
    "scripts": {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "next lint"
    },
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "next": "^14.0.0",
        "typescript": "^5.3.3",
        "tailwindcss": "^3.3.6",
        "postcss": "^8.4.31",
        "autoprefixer": "^10.4.16",
        "zustand": "^4.4.1",
        "axios": "^1.6.2"
    },
    "devDependencies": {
        "@types/node": "^20.10.0",
        "@types/react": "^18.2.37",
        "@types/react-dom": "^18.2.15"
    }
}

with open(os.path.join(root, "package.json"), "w") as f:
    json.dump(package_json, f, indent=2)

print("✓ All directories and files created!")
