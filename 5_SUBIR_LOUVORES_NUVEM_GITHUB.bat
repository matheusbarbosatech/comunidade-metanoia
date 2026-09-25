@echo off
chcp 65001 > nul
title Upload de Louvores para o GitHub CDN // Ministério Metanoia
cls
echo ===================================================================
echo     MINISTÉRIO METANOIA // UPLOAD DE LOUVORES PARA A NUVEM 24/7
echo               Powered by GitHub Releases & Azure CDN
echo ===================================================================
echo.
echo Este script enviará automaticamente os 50 arquivos MP3 para a
echo rede de CDN global do seu repositório no GitHub.
echo.
echo Quando o upload terminar, as músicas tocarão 24h por dia na sua
echo Landing Page e no App mesmo que o seu computador esteja desligado!
echo.

python scripts\upload_releases_github.py

echo.
echo Pressione qualquer tecla para fechar...
pause > nul
