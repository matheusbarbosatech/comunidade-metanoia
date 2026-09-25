@echo off
chcp 65001 > nul
title Transcritor de Áudios Teológicos // Ministério Metanoia
cls
echo ===================================================================
echo     MINISTÉRIO METANOIA // TRANSCRIÇÃO AUTOMÁTICA DE ÁUDIOS
echo               Powered by Deepgram Nova-2 (pt-BR)
echo ===================================================================
echo.
echo Dica: Você pode arrastar uma pasta de áudios (do Lenovo/Telegram) 
echo para esta janela ou pressionar Enter para usar a pasta padrão:
echo [data\audios_aulas]
echo.

set /p PASTA_INPUT="Arraste a pasta aqui ou aperte Enter: "

if "%PASTA_INPUT%"=="" (
    python scripts\transcritor_deepgram.py
) else (
    python scripts\transcritor_deepgram.py %PASTA_INPUT%
)

echo.
echo Processo concluído! Pressione qualquer tecla para sair.
pause > nul
