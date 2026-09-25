@echo off
chcp 65001 > nul
title Servidor Ministerial FastAPI // Metanoia
echo ============================================================
echo   🕊️ INICIANDO API MINISTERIAL & ESCOLA DE PREGADORES
echo   Versículo: Romanos 12:2
echo ============================================================
echo Documentação interativa em: http://127.0.0.1:8000/docs
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
