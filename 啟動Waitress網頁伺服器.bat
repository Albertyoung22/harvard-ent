@echo off
chcp 65001 >nul
title 賀華實業股份有限公司 - Flask + Waitress + OR-Tools CP-SAT 伺服器
cd /d "%~dp0"
echo ============================================================================
echo  正在啟動 賀華實業股份有限公司 Flask + Waitress 網頁伺服器 (Port 8080)...
echo ============================================================================
start "" "http://127.0.0.1:8080"
python app.py
pause
