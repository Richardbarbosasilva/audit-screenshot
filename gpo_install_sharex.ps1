param(
    [string]$InstallerPath = "\\LAB-DC\Software$\audit-screenshot\ShareX-19.0.2-setup.exe",
    [string]$DesiredVersion = "19.0.2",
    [string]$LogRoot = "$env:ProgramData\ScreenshotAudit\logs"
)

$ErrorActionPreference = "Stop"

function Get-InstalledShareXVersion {
    $roots = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )

    foreach ($root in $roots) {
        $item = Get-ItemProperty -Path $root -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -like "ShareX*" } |
            Select-Object -First 1

        if ($item) {
            return $item.DisplayVersion
        }
    }

    return $null
}

New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null

if (-not (Test-Path $InstallerPath)) {
    throw "Instalador do ShareX nao encontrado em $InstallerPath"
}

$installedVersion = Get-InstalledShareXVersion
if ($installedVersion) {
    try {
        if ([version]$installedVersion -ge [version]$DesiredVersion) {
            Write-Host "ShareX ja instalado em versao $installedVersion"
            exit 0
        }
    }
    catch {
        Write-Host "Nao foi possivel comparar versoes, reinstalando ShareX."
    }
}

$logPath = Join-Path $LogRoot "sharex-install.log"
$arguments = @(
    "/VERYSILENT",
    "/SUPPRESSMSGBOXES",
    "/NORESTART",
    "/SP-",
    "/NORUN",
    "/UPDATE",
    "/LOG=$logPath"
)

$process = Start-Process -FilePath $InstallerPath -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -notin @(0, 3010)) {
    throw "Falha na instalacao do ShareX. ExitCode=$($process.ExitCode)"
}

Write-Host "ShareX instalado ou atualizado com sucesso."
