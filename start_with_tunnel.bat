@echo off
chcp 65001 >nul
title 賀華實業股份有限公司 - 伺服器 + Cloudflare Tunnel 外網穿透
echo =====================================================================
echo   🌐 正在啟動 賀華實業 智慧伺服器與 Cloudflare Tunnel 外網分享...
echo =====================================================================
echo.
python run.py --tunnel
pause
