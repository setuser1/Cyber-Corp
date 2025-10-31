# Flood cmd in Powershell
$target = "172.18.73.228"
Write-Host "Flooding $target with ping requests. Press Ctrl+C to stop."

while ($true) {
    $result = Test-Connection -ComputerName $target -Quiet -Count 1
    if (-not $result) {
        Write-Warning "$(Get-Date -Format 'HH:mm:ss') - Request failed: Host $target is unreachable."
    }
}