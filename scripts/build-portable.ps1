param(
    [string]$Python = "python",
    [switch]$RecreateVenv
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$PortableRoot = Join-Path $RepoRoot "portable"
$OutputDir = Join-Path $PortableRoot "netops-cli"
$BuildDir = Join-Path $PortableRoot "_build"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

Set-Location $RepoRoot

if ($RecreateVenv -and (Test-Path ".venv")) {
    Remove-Item -LiteralPath ".venv" -Recurse -Force
}

if (-not (Test-Path $VenvPython)) {
    Invoke-Checked { & $Python -m venv .venv }
}

Invoke-Checked { & $VenvPython -m pip --version }

Invoke-Checked { & $VenvPython -m pip install --upgrade pip }
Invoke-Checked { & $VenvPython -m pip install -e ".[portable]" }

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

Invoke-Checked {
    & $VenvPython -m PyInstaller `
        --clean `
        --onefile `
        --console `
        --name netops `
        --distpath $OutputDir `
        --workpath (Join-Path $BuildDir "pyinstaller") `
        --specpath $BuildDir `
        src\netops\portable.py
}

New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir "data\assets\profile_photos") | Out-Null

Write-Host ""
Write-Host "Portable app created:"
Write-Host "  $OutputDir\netops.exe"
Write-Host ""
Write-Host "The portable database will be stored at:"
Write-Host "  $OutputDir\data\netops.sqlite3"
Write-Host ""
Write-Host "Copy this whole folder to your USB drive:"
Write-Host "  $OutputDir"
