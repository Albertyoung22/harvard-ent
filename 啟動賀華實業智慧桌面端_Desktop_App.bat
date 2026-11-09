@echo off
chcp 65001 >nul
title 賀華實業股份有限公司 - Google OR-Tools CP-SAT 智慧製造與無障礙桌面應用程式 (Desktop App)
cd /d "%~dp0"
echo ============================================================================
echo  正在啟動 賀華實業股份有限公司 (HARVARD ENTERPRISES INC.) 桌面應用程式...
echo  內建引擎：Google OR-Tools CP-SAT + Flask + Waitress + WCAG 2.1 AAA
echo ============================================================================
python desktop_app.py
if errorlevel 1 (
    echo 執行發生錯誤，請確認已安裝 Python 與套件：pip install -r requirements.txt
    pause
)
