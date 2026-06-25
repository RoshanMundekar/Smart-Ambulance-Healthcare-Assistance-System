param(
    [Parameter(Mandatory=$true)]
    [string]$TunnelUrl
)

# Smart Ambulance - APK Builder
# Run AFTER start_tunnel.bat is running.
# Usage:
#   powershell -ExecutionPolicy Bypass -File build_apk.ps1 -TunnelUrl https://xyz.loca.lt

$APP_DIR  = 'D:\jack_sparrow\SMART_AMBULANCE_HEALTHCARE_ASSISTANCE_SYSTEM\SmartAmbulance'
$APK_DIR  = $APP_DIR + '\apk_build'
$MANIFEST = $APP_DIR + '\twa-manifest.json'

$TunnelUrl   = $TunnelUrl.TrimEnd('/')
$TunnelHost  = $TunnelUrl -replace 'https://', ''

Write-Host ''
Write-Host '=============================================' -ForegroundColor Cyan
Write-Host '  Smart Ambulance - APK Builder' -ForegroundColor Cyan
Write-Host '  Tunnel : ' + $TunnelUrl -ForegroundColor Cyan
Write-Host '=============================================' -ForegroundColor Cyan

# ---- Verify server is reachable via tunnel ----
Write-Host ''
Write-Host '[1/4] Verifying server reachable via tunnel...' -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri ($TunnelUrl + '/health') -UseBasicParsing -TimeoutSec 15
    Write-Host '      Server OK - HTTP ' + $health.StatusCode -ForegroundColor Green
} catch {
    Write-Host '      WARNING: Server not reachable at tunnel URL.' -ForegroundColor DarkYellow
    Write-Host '      Make sure start_tunnel.bat is running first.' -ForegroundColor DarkYellow
    Write-Host '      Continuing anyway (icons may fail)...' -ForegroundColor DarkGray
}

# ---- Patch twa-manifest.json ----
Write-Host ''
Write-Host '[2/4] Patching twa-manifest.json...' -ForegroundColor Yellow

$mf = Get-Content $MANIFEST -Raw | ConvertFrom-Json
$mf.host              = $TunnelHost
$mf.iconUrl           = $TunnelUrl + '/static/icon.png'
$mf.maskableIconUrl   = $TunnelUrl + '/static/icon.png'
$mf.monochromeIconUrl = $TunnelUrl + '/static/icon_192.png'
$mf.webManifestUrl    = $TunnelUrl + '/static/manifest.json'
$mf.fullScopeUrl      = $TunnelUrl + '/'
$mf.minSdkVersion     = 21

# Bubblewrap crashes if signingKey is missing
if (-not $mf.signingKey) {
    $mf | Add-Member -MemberType NoteProperty -Name "signingKey" -Value @{
        path  = "D:\jack_sparrow\SMART_AMBULANCE_HEALTHCARE_ASSISTANCE_SYSTEM\SmartAmbulance\android.keystore"
        alias = "android"
    }
}

# Fix missing splashScreenFadeOutDuration which causes a Groovy syntax error
if (-not $mf.splashScreenFadeOutDuration) {
    $mf | Add-Member -MemberType NoteProperty -Name "splashScreenFadeOutDuration" -Value 300
}

$jsonText = $mf | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($MANIFEST, $jsonText, (New-Object System.Text.UTF8Encoding($False)))

Write-Host '      Done. host = ' + $TunnelHost -ForegroundColor Green

# ---- Run bubblewrap build ----
Write-Host ''
Write-Host '[3/4] Running bubblewrap build...' -ForegroundColor Yellow
Write-Host '      This takes 5-10 minutes. Do not close this window.' -ForegroundColor DarkGray
Write-Host ''

if (Test-Path $APK_DIR) {
    Remove-Item -Recurse -Force $APK_DIR
}
New-Item -ItemType Directory -Path $APK_DIR | Out-Null

Set-Location $APK_DIR
    node `"..\bubblewrap_wrapper.js`"
$exitCode = $LASTEXITCODE
Set-Location $APP_DIR

# ---- Find APK ----
Write-Host ''
Write-Host '[4/4] Looking for APK file...' -ForegroundColor Yellow

$apkList = Get-ChildItem -Path $APK_DIR -Filter '*.apk' -Recurse -ErrorAction SilentlyContinue
if ($apkList.Count -eq 0) {
    $apkList = Get-ChildItem -Path $APP_DIR -Filter '*.apk' -Recurse -ErrorAction SilentlyContinue
}
$apkList = $apkList | Sort-Object Length -Descending

Write-Host ''
Write-Host '=============================================' -ForegroundColor Cyan

if ($apkList.Count -gt 0) {
    Write-Host '  SUCCESS! APK built.' -ForegroundColor Green
    Write-Host ''
    foreach ($apk in $apkList) {
        $sizeMB = [math]::Round($apk.Length / 1MB, 2)
        Write-Host '  APK  : ' + $apk.FullName -ForegroundColor Green
        Write-Host '  SIZE : ' + $sizeMB + ' MB' -ForegroundColor Green
    }
    Write-Host ''
    Write-Host '  TO INSTALL ON ANDROID:' -ForegroundColor Cyan
    Write-Host '  Via ADB (USB cable):' -ForegroundColor White
    $installCmd = 'adb install -r "' + $apkList[0].FullName + '"'
    Write-Host '    ' + $installCmd -ForegroundColor White
    Write-Host ''
    Write-Host '  Via phone manually:' -ForegroundColor White
    Write-Host '    Copy the APK to your phone, tap it, allow Unknown Sources' -ForegroundColor White
    Write-Host ''
    Write-Host '  IMPORTANT:' -ForegroundColor Yellow
    Write-Host '    The app connects to: ' + $TunnelUrl -ForegroundColor Yellow
    Write-Host '    Keep start_tunnel.bat running when using the app!' -ForegroundColor Yellow
} else {
    Write-Host '  BUILD FAILED (exit code: ' + $exitCode + ')' -ForegroundColor Red
    Write-Host '  Check the Gradle output above for errors.' -ForegroundColor DarkYellow
    Write-Host '  APK expected at: ' + $APK_DIR -ForegroundColor DarkGray
}

Write-Host '=============================================' -ForegroundColor Cyan
Write-Host ''
