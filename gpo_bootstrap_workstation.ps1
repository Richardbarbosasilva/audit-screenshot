param(
    [string]$ShareXInstallerPath = "\\LAB-DC\Software$\audit-screenshot\ShareX-19.0.2-setup.exe",
    [string]$ShareXVersion = "19.0.2",
    [string]$AgentSourceRoot = "\\LAB-DC\Software$\audit-screenshot\agent",
    [string]$ToolsRoot = "\\LAB-DC\Software$\audit-screenshot\tools",
    [string]$ScriptsRoot = "\\LAB-DC\Software$\audit-screenshot\scripts"
)

$ErrorActionPreference = "Stop"
$localLogRoot = "$env:ProgramData\ScreenshotAudit\logs"
New-Item -ItemType Directory -Force -Path $localLogRoot | Out-Null
$transcriptPath = Join-Path $localLogRoot "gpo-bootstrap.log"

Start-Transcript -Path $transcriptPath -Append

try {
    $sharexScript = Join-Path $ScriptsRoot "gpo_install_sharex.ps1"
    $agentScript = Join-Path $ScriptsRoot "gpo_install_agent.ps1"

    powershell.exe -ExecutionPolicy Bypass -File $sharexScript `
        -InstallerPath $ShareXInstallerPath `
        -DesiredVersion $ShareXVersion `
        -LogRoot $localLogRoot

    powershell.exe -ExecutionPolicy Bypass -File $agentScript `
        -SourceRoot $AgentSourceRoot `
        -ToolsRoot $ToolsRoot `
        -ScriptsRoot $ScriptsRoot

    Write-Host "Bootstrap da workstation concluido."
}
finally {
    Stop-Transcript
}
