@echo off
setlocal enabledelayedexpansion

REM Create frontend directory
mkdir "%~dp0frontend" 2>nul
mkdir "%~dp0frontend\app" 2>nul
mkdir "%~dp0frontend\components" 2>nul
mkdir "%~dp0frontend\lib" 2>nul
mkdir "%~dp0frontend\public" 2>nul

echo Frontend directories created successfully
