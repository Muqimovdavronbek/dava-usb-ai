@echo off
chcp 65001 >nul
title DAVA USB AI
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\start_windows.ps1"
if errorlevel 1 (
  echo.
  echo Xatolik yuz berdi. Yuqoridagi xabarni yoki logs papkasini tekshiring.
  pause
)
