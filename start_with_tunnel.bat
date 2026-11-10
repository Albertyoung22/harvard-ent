@echo off
chcp 65001 >nul
title 賀華實業股份有限公司 - 伺服器 + Cloudflare Tunnel 外網穿透
echo =====================================================================
echo   🌐 正在啟動 賀華實業 智慧伺服器與 Cloudflare Tunnel 外網分享...
echo =====================================================================
echo.

set "PY_EXE=C:\Users\USER\AppData\Local\Programs\Python\Python313\python.exe"
if not exist "%PY_EXE%" (
    py -3.13 --version >nul 2>&1 && (
        set "PY_EXE=py -3.13"
    ) || (
        set "PY_EXE=python"
    )
)

%PY_EXE% run.py --tunnel
pause
