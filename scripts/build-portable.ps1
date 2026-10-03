param([string]$Python = ".venv\Scripts\python.exe")
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
& $Python scripts/build_release.py
if ($LASTEXITCODE -ne 0) { throw "Release build failed." }
