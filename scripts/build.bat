@echo off
REM Atlas Quant Platform - Build Wrapper (Windows CMD)
REM Delegates to scripts/build.ps1
powershell -ExecutionPolicy Bypass -File "%~dp0build.ps1" -Target all
