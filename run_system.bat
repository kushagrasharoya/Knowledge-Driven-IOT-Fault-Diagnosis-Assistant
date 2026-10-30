@echo off
title P_311 Master Launcher
echo ======================================================================
echo Launching P_311 — Knowledge-Driven IoT Fault Diagnosis Assistant
echo ======================================================================
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe launch_demo.py
) else (
    python launch_demo.py
)
pause
