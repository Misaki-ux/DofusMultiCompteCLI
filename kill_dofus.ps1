try {
    $processes = Get-Process -Name "dofus" -ErrorAction Stop
    foreach ($proc in $processes) {
        Stop-Process -Id $proc.Id -Force
    }
    Write-Host "Dofus.exe process(es) terminated successfully." -ForegroundColor Green
} catch {
    Write-Host "No Dofus.exe process found or an error occurred." -ForegroundColor Yellow
}