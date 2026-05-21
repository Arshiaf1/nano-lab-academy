# This script creates the frontend project structure
# Run this from the root directory

# Create frontend directory
New-Item -ItemType Directory -Force -Path "frontend" | Out-Null

# Create subdirectories
@("app", "app/auth", "app/auth/login", "app/auth/register", "app/(protected)", "components", "lib", "public", "styles") | ForEach-Object {
    New-Item -ItemType Directory -Force -Path "frontend/$_" | Out-Null
}

Write-Host "Frontend directory structure created successfully"
