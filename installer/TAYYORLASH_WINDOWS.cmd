@echo off
chcp 65001 >nul
title DAVA USB AI tayyorlash
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\assemble.ps1"
pause
