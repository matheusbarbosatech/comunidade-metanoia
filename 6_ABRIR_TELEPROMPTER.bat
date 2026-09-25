@echo off
chcp 65001 > nul
title Teleprompter Ministerial // Refúgio Metanoia
cls
echo ===================================================================
echo     REFÚGIO METANOIA // TELEPROMPTER INTERATIVO PARA GRAVAÇÃO
echo ===================================================================
echo.
echo Abrindo o Teleprompter com o roteiro do seu primeiro vídeo no navegador...
echo.
echo DICAS RÁPIDAS:
echo  - Pressione a BARRA DE ESPAÇO para Iniciar / Pausar a rolagem
echo  - Use as SETAS (Cima/Baixo) para acelerar ou desacelerar o texto
echo  - Olhe para a Linha Guia Amarela enquanto fala para manter o contato visual!
echo.

start "" "%~dp0app\static\teleprompter.html"

echo Teleprompter aberto com sucesso!
timeout /t 3 > nul
exit
