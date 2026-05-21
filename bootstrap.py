import os
import json
import sys

def setup_frontend():
    """Bootstrap the Next.js frontend structure"""
    base = r"c:\Users\asus\nano-lab-academy.worktrees\agents-frontend-dashboard-courses-lessons-pages\frontend"
    
    # Create all needed directories
    dirs = ["app", "components", "lib", "public"]
    
    for d in dirs:
        path = os.path.join(base, d)
        try:
            os.makedirs(path, exist_ok=True)
            print(f"✓ {path}")
        except Exception as e:
            print(f"✗ {path}: {e}")
            return False
    
    # package.json
    pkg = {
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
    
    files = {
        "package.json": json.dumps(pkg, indent=2),
        ".gitignore": "/node_modules\n/.next\n/out\n/build\n.env*.local\n.DS_Store\n",
        ".env.local": "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1\n",
    }
    
    for fname, content in files.items():
        try:
            with open(os.path.join(base, fname), "w") as f:
                f.write(content)
            print(f"✓ {fname}")
        except Exception as e:
            print(f"✗ {fname}: {e}")
    
    print("\n✓ Frontend bootstrap complete!")
    return True

if __name__ == "__main__":
    setup_frontend()
