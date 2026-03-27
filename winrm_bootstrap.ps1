param()

$ErrorActionPreference = "Stop"

Enable-PSRemoting -Force
Set-Service -Name WinRM -StartupType Automatic
Start-Service -Name WinRM

Get-NetFirewallRule -DisplayGroup "Windows Remote Management" -ErrorAction SilentlyContinue |
    Set-NetFirewallRule -Enabled True

Set-Item -Path WSMan:\localhost\Service\Auth\Kerberos -Value $true
Set-Item -Path WSMan:\localhost\Service\Auth\Negotiate -Value $true

Test-WsMan localhost | Out-Null
Write-Host "WinRM habilitado com sucesso."
