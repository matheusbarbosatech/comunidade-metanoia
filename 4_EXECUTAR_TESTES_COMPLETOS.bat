@echo off
chcp 65001 > nul
title Robô de Testes Automatizados // Ministério Metanoia
cls
echo ===================================================================
echo     MINISTÉRIO METANOIA // AUDITORIA E TESTES AUTOMATIZADOS (E2E)
echo ===================================================================
echo.
echo Executando simulação completa de uso:
echo  - Jornada do Discípulo / Usuário com Ansiedade
echo  - Jornada da Liderança (Matheus no Painel ADM)
echo  - Integridade do Banco SQLite e Rotas da API
echo  - Plataforma Web Flet e Landing Page
echo.

python scripts\robo_testes_completo.py

echo.
echo Pressione qualquer tecla para fechar...
pause > nul
