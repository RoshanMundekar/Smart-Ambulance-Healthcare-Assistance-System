param()

$PYTHON      = "C:\Users\Admin\anaconda3\envs\fast\python.exe"
$APP_DIR     = "D:\jack_sparrow\SMART_AMBULANCE_HEALTHCARE_ASSISTANCE_SYSTEM\SmartAmbulance"
$SERVER_PORT = 8000
$CF_LOG      = Join-Path $env:TEMP ("cf_out_" + $PID + ".txt")

# Start FastAPI
Write-Host "Starting FastAPI..."
$srvProc = Start-Process -FilePath $PYTHON -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port $SERVER_PORT" -WorkingDirectory $APP_DIR -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5

# Start Cloudflared
Write-Host "Starting Cloudflared tunnel..."
$cfArgs = "tunnel --url http://localhost:$SERVER_PORT"
$cfProc = Start-Process -FilePath "$APP_DIR\cloudflared.exe" -ArgumentList $cfArgs -RedirectStandardError $CF_LOG -PassThru -WindowStyle Hidden

Write-Host "Waiting for tunnel URL..."
$tunnelUrl = $null
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 2
    if (Test-Path $CF_LOG) {
        $content = Get-Content $CF_LOG -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $match = [regex]::Match($content, "https://[a-z0-9\-]+\.trycloudflare\.com")
            if ($match.Success) {
                $tunnelUrl = $match.Value
                break
            }
        }
    }
}

if (-not $tunnelUrl) {
    Write-Host "Failed to get Cloudflare tunnel URL."
    if (Test-Path $CF_LOG) { Get-Content $CF_LOG }
    if ($srvProc) { Stop-Process -Id $srvProc.Id -Force -ErrorAction SilentlyContinue }
    if ($cfProc)  { Stop-Process -Id $cfProc.Id -Force -ErrorAction SilentlyContinue }
    exit 1
}

Write-Host "Got URL: $tunnelUrl"
Write-Host "Waiting for Cloudflare DNS to propagate and server to become reachable..."

$dnsResolved = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $tunnelUrl -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $dnsResolved = $true
            Write-Host "Server is reachable at $tunnelUrl!"
            break
        }
    } catch {
        # Ignore errors and retry
    }
    Start-Sleep -Seconds 2
}

if (-not $dnsResolved) {
    Write-Host "WARNING: Could not verify tunnel reachability after 60 seconds. Proceeding anyway..."
}

Write-Host "Running build_apk.ps1..."

& powershell -ExecutionPolicy Bypass -File "$APP_DIR\build_apk.ps1" -TunnelUrl $tunnelUrl

# Stop processes after build
Write-Host "Stopping background processes..."
if ($srvProc) { Stop-Process -Id $srvProc.Id -Force -ErrorAction SilentlyContinue }
if ($cfProc)  { Stop-Process -Id $cfProc.Id -Force -ErrorAction SilentlyContinue }

Write-Host "Done!"
