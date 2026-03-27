param(
    [string]$SourceRoot = "\\LAB-DC\Software$\audit-screenshot\agent",
    [string]$ToolsRoot = "\\LAB-DC\Software$\audit-screenshot\tools",
    [string]$ScriptsRoot = "\\LAB-DC\Software$\audit-screenshot\scripts",
    [string]$InstallRoot = "C:\Program Files\ScreenshotAudit",
    [string]$ProgramDataRoot = "$env:ProgramData\ScreenshotAudit"
)

$ErrorActionPreference = "Stop"

function Copy-IfDifferent {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$DestinationPath
    )

    if (-not (Test-Path $SourcePath)) {
        throw "Arquivo de origem nao encontrado: $SourcePath"
    }

    $destinationDir = Split-Path -Path $DestinationPath -Parent
    New-Item -ItemType Directory -Force -Path $destinationDir | Out-Null

    if (Test-Path $DestinationPath) {
        $sourceHash = (Get-FileHash -Path $SourcePath -Algorithm SHA256).Hash
        $destinationHash = (Get-FileHash -Path $DestinationPath -Algorithm SHA256).Hash
        if ($sourceHash -eq $destinationHash) {
            return
        }
    }

    Copy-Item -Path $SourcePath -Destination $DestinationPath -Force
}

New-Item -ItemType Directory -Force -Path $InstallRoot | Out-Null
New-Item -ItemType Directory -Force -Path "$ProgramDataRoot\assets" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProgramDataRoot\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProgramDataRoot\spool" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProgramDataRoot\tmp" | Out-Null
New-Item -ItemType Directory -Force -Path "$ProgramDataRoot\data" | Out-Null

$binarySource = Join-Path $SourceRoot "ScreenshotAuditAgent.exe"
$configSource = Join-Path $SourceRoot "agent_config.json"
$logoSource = Join-Path $SourceRoot "logo.png"
$nssmSource = Join-Path $ToolsRoot "nssm.exe"
$serviceScriptSource = Join-Path $ScriptsRoot "install_agent_service.ps1"

$binaryDestination = Join-Path $InstallRoot "ScreenshotAuditAgent.exe"
$configDestination = Join-Path $InstallRoot "agent_config.json"
$logoDestination = Join-Path "$ProgramDataRoot\assets" "logo.png"
$nssmDestination = Join-Path $InstallRoot "nssm.exe"
$serviceScriptDestination = Join-Path $InstallRoot "install_agent_service.ps1"

Copy-IfDifferent -SourcePath $binarySource -DestinationPath $binaryDestination
Copy-IfDifferent -SourcePath $configSource -DestinationPath $configDestination
Copy-IfDifferent -SourcePath $logoSource -DestinationPath $logoDestination
Copy-IfDifferent -SourcePath $nssmSource -DestinationPath $nssmDestination
Copy-IfDifferent -SourcePath $serviceScriptSource -DestinationPath $serviceScriptDestination

powershell.exe -ExecutionPolicy Bypass -File $serviceScriptDestination `
    -BinaryPath $binaryDestination `
    -ConfigPath $configDestination `
    -NssmPath $nssmDestination `
    -ProgramDataRoot $ProgramDataRoot

Write-Host "Agent instalado ou atualizado com sucesso."
