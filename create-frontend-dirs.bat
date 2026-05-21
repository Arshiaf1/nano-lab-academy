@echo off
REM Create frontend directory structure
mkdir frontend
cd frontend

REM Create main directories
mkdir app
mkdir app\auth
mkdir app\auth\login
mkdir app\auth\register
mkdir app\(protected)
mkdir components
mkdir lib
mkdir public
mkdir styles

echo Frontend directory structure created successfully
cd ..
