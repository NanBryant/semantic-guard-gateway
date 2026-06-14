param(
    [int]$Port = 8000
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$targets = Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
    Where-Object {
        ($_.CommandLine -like "*uvicorn app:app*" -and $_.CommandLine -like "*$Root*") -or
        ($_.CommandLine -like "*uvicorn app:app*" -and $_.CommandLine -like "*--port $Port*")
    }

if (-not $targets) {
    Write-Host "No matching server process found."
    exit 0
}

foreach ($proc in $targets) {
    Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "Stopped PID $($proc.ProcessId)"
}
