@echo off
chcp 65001 >nul
rem RAW studio update
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\raw-studio\win\update.ps1"
