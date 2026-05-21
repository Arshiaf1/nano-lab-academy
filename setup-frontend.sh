#!/bin/bash

# Frontend Setup Script for Nano Lab Academy
# This script organizes all frontend files into proper directory structure

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"

echo "🚀 Setting up Nano Lab Academy Frontend..."
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$FRONTEND_DIR"
mkdir -p "$FRONTEND_DIR/app/auth/login"
mkdir -p "$FRONTEND_DIR/app/auth/register"
mkdir -p "$FRONTEND_DIR/app/(protected)/dashboard"
mkdir -p "$FRONTEND_DIR/components"
mkdir -p "$FRONTEND_DIR/lib"
mkdir -p "$FRONTEND_DIR/public"
mkdir -p "$FRONTEND_DIR/styles"

echo "✅ Directories created"
echo ""

# Function to move and rename files
move_file() {
    local src="$REPO_ROOT/frontend_$1"
    local dest="$FRONTEND_DIR/$2"
    
    if [ -f "$src" ]; then
        mv "$src" "$dest"
        echo "✓ Moved $1 → $2"
    else
        echo "⚠ File not found: $src"
    fi
}

echo "📋 Organizing files..."

# Root level config files
move_file "package.json" "package.json"
move_file "tsconfig.json" "tsconfig.json"
move_file "tailwind.config.ts" "tailwind.config.ts"
move_file "next.config.js" "next.config.js"
move_file "postcss.config.js" "postcss.config.js"
move_file ".eslintrc.json" ".eslintrc.json"
move_file ".env.local" ".env.local"
move_file "_.gitignore" ".gitignore"
move_file "middleware.ts" "middleware.ts"

# Global styles
move_file "globals.css" "app/globals.css"

# App routes
move_file "app_layout.tsx" "app/layout.tsx"
move_file "app_page.tsx" "app/page.tsx"
move_file "app_auth_layout.tsx" "app/auth/layout.tsx"
move_file "app_auth_login_page.tsx" "app/auth/login/page.tsx"
move_file "app_auth_register_page.tsx" "app/auth/register/page.tsx"
move_file "app_protected_dashboard_page.tsx" "app/(protected)/dashboard/page.tsx"

# Components
move_file "components_Navbar.tsx" "components/Navbar.tsx"

# Library files
move_file "lib_store.ts" "lib/store.ts"
move_file "lib_api-client.ts" "lib/api-client.ts"

echo ""
echo "✅ All files organized successfully!"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
cd "$FRONTEND_DIR"
npm install

echo ""
echo "🎉 Frontend setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Ensure backend is running: http://localhost:8000"
echo "  2. Start development server: npm run dev"
echo "  3. Open browser: http://localhost:3000"
echo ""
