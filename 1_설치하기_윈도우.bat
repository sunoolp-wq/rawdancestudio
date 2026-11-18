@echo off
chcp 65001 >nul
rem RAW studio install (Windows, first time only)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\raw-studio\win\install.ps1"
