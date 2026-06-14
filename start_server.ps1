param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$Reload
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Reports = Join-Path $Root "reports"
$OutLog = Join-Path $Reports "uvicorn.out.log"
$ErrLog = Join-Path $Reports "uvicorn.err.log"
New-Item -ItemType Directory -Force -Path $Reports | Out-Null

$old = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
    Where-Object {
        ($_.CommandLine -like "*uvicorn app:app*" -and $_.CommandLine -like "*$Root*") -or
        ($_.CommandLine -like "*uvicorn app:app*" -and $_.CommandLine -like "*--port $Port*")
    }

foreach ($proc in $old) {
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1

$argsList = @("-m", "uvicorn", "app:app", "--host", $HostAddress, "--port", "$Port")
if ($Reload) {
    $argsList += "--reload"
}

$process = Start-Process `
    -FilePath "python" `
    -ArgumentList $argsList `
    -WorkingDirectory $Root `
    -WindowStyle Hidden `
    -RedirectStandardOutput $OutLog `
    -RedirectStandardError $ErrLog `
    -PassThru

Start-Sleep -Seconds 3

try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -Method GET -TimeoutSec 5
    Write-Host "Server started: http://127.0.0.1:$Port"
    Write-Host "PID: $($process.Id)"
    Write-Host "Health: $($health.status)"
    Write-Host "Logs: $OutLog"
} catch {
    Write-Host "Server failed to respond. Error log:"
    if (Test-Path $ErrLog) {
        Get-Content $ErrLog
    }
    exit 1
}
