@echo off
chcp 65001 >nul
rem RAW studio open (keep this window open while using)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\raw-studio\win\start.ps1"
