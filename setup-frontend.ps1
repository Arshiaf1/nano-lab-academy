# Frontend Setup Script for Nano Lab Academy (PowerShell)
# This script organizes all frontend files into proper directory structure

$ErrorActionPreference = "Stop"

$REPO_ROOT = Get-Location
$FRONTEND_DIR = Join-Path $REPO_ROOT "frontend"

Write-Host "🚀 Setting up Nano Lab Academy Frontend..." -ForegroundColor Green
Write-Host ""

# Create directory structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Cyan
$dirs = @(
    ".",
    "app\auth\login",
    "app\auth\register",
    "app\(protected)\dashboard",
    "components",
    "lib",
    "public",
    "styles"
)

foreach ($dir in $dirs) {
    $fullPath = Join-Path $FRONTEND_DIR $dir
    New-Item -ItemType Directory -Force -Path $fullPath | Out-Null
}

Write-Host "✅ Directories created" -ForegroundColor Green
Write-Host ""

# Function to move and rename files
function Move-FrontendFile {
    param(
        [string]$FileName,
        [string]$DestinationPath
    )
    
    $src = Join-Path $REPO_ROOT "frontend_$FileName"
    $dest = Join-Path $FRONTEND_DIR $DestinationPath
    
    if (Test-Path $src) {
        Move-Item -Path $src -Destination $dest -Force
        Write-Host "✓ Moved $FileName → $DestinationPath" -ForegroundColor Green
    } else {
        Write-Host "⚠ File not found: $src" -ForegroundColor Yellow
    }
}

Write-Host "📋 Organizing files..." -ForegroundColor Cyan

# Root level config files
Move-FrontendFile "package.json" "package.json"
Move-FrontendFile "tsconfig.json" "tsconfig.json"
Move-FrontendFile "tailwind.config.ts" "tailwind.config.ts"
Move-FrontendFile "next.config.js" "next.config.js"
Move-FrontendFile "postcss.config.js" "postcss.config.js"
Move-FrontendFile ".eslintrc.json" ".eslintrc.json"
Move-FrontendFile ".env.local" ".env.local"
Move-FrontendFile "_.gitignore" ".gitignore"
Move-FrontendFile "middleware.ts" "middleware.ts"

# Global styles
Move-FrontendFile "globals.css" "app\globals.css"

# App routes
Move-FrontendFile "app_layout.tsx" "app\layout.tsx"
Move-FrontendFile "app_page.tsx" "app\page.tsx"
Move-FrontendFile "app_auth_layout.tsx" "app\auth\layout.tsx"
Move-FrontendFile "app_auth_login_page.tsx" "app\auth\login\page.tsx"
Move-FrontendFile "app_auth_register_page.tsx" "app\auth\register\page.tsx"
Move-FrontendFile "app_protected_dashboard_page.tsx" "app\(protected)\dashboard\page.tsx"

# Components
Move-FrontendFile "components_Navbar.tsx" "components\Navbar.tsx"

# Library files
Move-FrontendFile "lib_store.ts" "lib\store.ts"
Move-FrontendFile "lib_api-client.ts" "lib\api-client.ts"

Write-Host ""
Write-Host "✅ All files organized successfully!" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
Push-Location $FRONTEND_DIR
npm install
Pop-Location

Write-Host ""
Write-Host "🎉 Frontend setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure backend is running: http://localhost:8000"
Write-Host "  2. Start development server: npm run dev"
Write-Host "  3. Open browser: http://localhost:3000"
Write-Host ""
