@echo off
cd /d "c:\Users\asus\nano-lab-academy.worktrees\agents-nextjs-setup-typescript-tailwind"
if not exist frontend mkdir frontend
cd frontend
echo Creating Next.js project...
call npx create-next-app@latest . --typescript --tailwind --app --eslint --import-alias --no-git --skip-install
if errorlevel 1 (
    echo Error creating Next.js project
    exit /b 1
)
echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo Error installing npm dependencies
    exit /b 1
)
echo Setup completed successfully
