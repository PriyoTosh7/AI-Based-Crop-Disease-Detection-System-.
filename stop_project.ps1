$ports = @(8000)
foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        try {
            Stop-Process -Id $connection.OwningProcess -Force -ErrorAction Stop
            Write-Host "Stopped process on port $port" -ForegroundColor Green
        } catch {
            Write-Host "Could not stop process on port $port: $_" -ForegroundColor Yellow
        }
    }
}
