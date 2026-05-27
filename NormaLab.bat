@echo off
title NormaLab GRC
echo.
echo  ╔═══════════════════════════════════╗
echo  ║      NormaLab GRC — Iniciando     ║
echo  ╚═══════════════════════════════════╝
echo.

cd /d "%~dp0"

:: Iniciar el servidor en segundo plano
start "" /B python run.py

:: Esperar 2 segundos y abrir el navegador
timeout /t 2 /nobreak >nul
start http://localhost:8090

echo  Servidor iniciado en http://localhost:8090
echo  Cerrá esta ventana para detener el servidor.
echo.
pause
