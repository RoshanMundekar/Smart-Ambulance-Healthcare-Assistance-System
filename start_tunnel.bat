@echo off
REM Smart Ambulance - Step 1: Start Server and Tunnel
REM Run this FIRST, then run build_apk.ps1 with the tunnel URL

echo.
echo =============================================
echo   Smart Ambulance - Server + Tunnel Starter
echo =============================================
echo.
echo [1] Starting FastAPI server in a new window...
start "FastAPI Server" cmd /k "C:\Users\Admin\anaconda3\envs\fast\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo [2] Waiting 5 seconds for server to boot...
timeout /t 5 /nobreak > nul

echo [3] Starting Cloudflare tunnel...
echo     When the tunnel URL appears below, COPY it.
echo     Example: https://abc-xyz.trycloudflare.com
echo.
echo     Then open a NEW terminal and run:
echo     powershell -ExecutionPolicy Bypass -File build_apk.ps1 -TunnelUrl https://YOUR-URL.trycloudflare.com
echo.
echo =============================================
echo TUNNEL URL WILL APPEAR IN THE LOGS BELOW:
echo Look for a line that says "https://[something].trycloudflare.com"
echo DO NOT CLOSE THIS WINDOW WHILE USING THE APP!
echo =============================================
echo.
"%~dp0cloudflared.exe" tunnel --url http://localhost:8000
