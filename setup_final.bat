@echo off
REM Create frontend directories
if not exist "frontend" mkdir frontend
if not exist "frontend\app" mkdir frontend\app
if not exist "frontend\components" mkdir frontend\components
if not exist "frontend\lib" mkdir frontend\lib
if not exist "frontend\public" mkdir frontend\public

REM Run the Python setup script
cd frontend
cd ..
python create_frontend.py
