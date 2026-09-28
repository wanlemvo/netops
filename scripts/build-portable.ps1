param(
    [string]$Python = "python",
    [switch]$RecreateVenv
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$LegacyPortableRoot = Join-Path $RepoRoot "portable"
$DistRoot = Join-Path $RepoRoot "netops"
$CliOutputDir = Join-Path $DistRoot "netops-cli"
$GuiOutputDir = Join-Path $DistRoot "netops-gui"
$SharedDataDir = Join-Path $DistRoot "data"
$RepoDataDir = Join-Path $RepoRoot "data"
$LegacyDistRoot = Join-Path $LegacyPortableRoot "netops"
$LegacySharedDataDir = Join-Path $LegacyDistRoot "data"
$OldOutputDir = Join-Path $LegacyPortableRoot "netops-cli"
$OldDataDir = Join-Path $OldOutputDir "data"
$BuildDir = Join-Path $RepoRoot "build\portable"
$StagingRoot = Join-Path $RepoRoot ".netops-staging"
$StagedDataDir = Join-Path $StagingRoot "data"
$GuiStaticDir = Join-Path $RepoRoot "src\netops\gui\static"
$GuiStaticData = "$GuiStaticDir;netops\gui\static"

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

function Assert-WithinOutputRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PathToCheck
    )

    $allowedRoots = @($DistRoot, $BuildDir, $StagingRoot, $LegacyPortableRoot)
    $targetFull = [System.IO.Path]::GetFullPath($PathToCheck)
    foreach ($root in $allowedRoots) {
        $rootFull = [System.IO.Path]::GetFullPath($root)
        if ($targetFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            return
        }
    }
    throw "Refusing to modify path outside portable output roots: $targetFull"
}

function Remove-OutputPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PathToRemove
    )

    if (Test-Path $PathToRemove) {
        Assert-WithinOutputRoot $PathToRemove
        Remove-Item -LiteralPath $PathToRemove -Recurse -Force
    }
}

function Test-NetOpsData {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DataDir
    )

    return (Test-Path (Join-Path $DataDir "netops.sqlite3"))
}

function Build-PortableExecutable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$EntryPoint,

        [Parameter(Mandatory = $true)]
        [string]$OutputDir,

        [switch]$IncludeGuiAssets,

        [switch]$Windowed
    )

    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    $workPath = Join-Path $BuildDir "pyinstaller-$Name"
    $pyInstallerArgs = @(
        "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--name", $Name,
        "--distpath", $OutputDir,
        "--workpath", $workPath,
        "--specpath", $BuildDir
    )
    if ($Windowed) {
        $pyInstallerArgs += "--windowed"
    } else {
        $pyInstallerArgs += "--console"
    }
    if ($IncludeGuiAssets) {
        $pyInstallerArgs += @("--add-data", $GuiStaticData)
    }
    $pyInstallerArgs += $EntryPoint

    Invoke-Checked { & $VenvPython @pyInstallerArgs }
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

Remove-OutputPath $StagingRoot
New-Item -ItemType Directory -Force -Path $StagingRoot | Out-Null
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null
if ((Test-Path $SharedDataDir) -and (Test-NetOpsData $SharedDataDir)) {
    Copy-Item -LiteralPath $SharedDataDir -Destination $StagedDataDir -Recurse -Force
} elseif ((Test-Path $LegacySharedDataDir) -and (Test-NetOpsData $LegacySharedDataDir)) {
    Copy-Item -LiteralPath $LegacySharedDataDir -Destination $StagedDataDir -Recurse -Force
} elseif ((Test-Path $OldDataDir) -and (Test-NetOpsData $OldDataDir)) {
    Copy-Item -LiteralPath $OldDataDir -Destination $StagedDataDir -Recurse -Force
} elseif ((Test-Path $RepoDataDir) -and (Test-NetOpsData $RepoDataDir)) {
    Copy-Item -LiteralPath $RepoDataDir -Destination $StagedDataDir -Recurse -Force
} elseif (Test-Path $SharedDataDir) {
    Copy-Item -LiteralPath $SharedDataDir -Destination $StagedDataDir -Recurse -Force
} elseif (Test-Path $LegacySharedDataDir) {
    Copy-Item -LiteralPath $LegacySharedDataDir -Destination $StagedDataDir -Recurse -Force
} elseif (Test-Path $OldDataDir) {
    Copy-Item -LiteralPath $OldDataDir -Destination $StagedDataDir -Recurse -Force
} elseif (Test-Path $RepoDataDir) {
    Copy-Item -LiteralPath $RepoDataDir -Destination $StagedDataDir -Recurse -Force
}

Remove-OutputPath $DistRoot
New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null

Build-PortableExecutable -Name "netops-cli" -EntryPoint "src\netops\portable_cli.py" -OutputDir $CliOutputDir
Build-PortableExecutable -Name "netops-gui" -EntryPoint "src\netops\portable_gui.py" -OutputDir $GuiOutputDir -IncludeGuiAssets -Windowed

New-Item -ItemType Directory -Force -Path $SharedDataDir | Out-Null
if (Test-Path $StagedDataDir) {
    Copy-Item -Path (Join-Path $StagedDataDir "*") -Destination $SharedDataDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path (Join-Path $SharedDataDir "assets\profile_photos") | Out-Null

@"
NetworkOps Portable

Use netops-cli\netops-cli.exe for the original terminal CLI/TUI app.
Use netops-gui\netops-gui.exe for the desktop GUI shell.

Both apps share the data\ folder in this portable root so edits made in one app appear in the other.
"@ | Set-Content -Path (Join-Path $DistRoot "README.txt")

@"
NetworkOps CLI/TUI

Double-click netops-cli.exe to launch the interactive terminal app.
Run netops-cli.exe --help from PowerShell to see CLI commands.
Shared data lives in ..\data.
"@ | Set-Content -Path (Join-Path $CliOutputDir "README.txt")

@"
NetworkOps GUI

Double-click netops-gui.exe to launch NetworkOps in its own desktop window.
The app stores records in ..\data.
"@ | Set-Content -Path (Join-Path $GuiOutputDir "README.txt")

Remove-OutputPath $LegacyPortableRoot
Remove-OutputPath $BuildDir
Remove-OutputPath $StagingRoot

Write-Host ""
Write-Host "Portable apps created:"
Write-Host "  $CliOutputDir\netops-cli.exe"
Write-Host "  $GuiOutputDir\netops-gui.exe"
Write-Host ""
Write-Host "The shared portable database will be stored at:"
Write-Host "  $SharedDataDir\netops.sqlite3"
Write-Host ""
Write-Host "Copy this whole folder to your USB drive:"
Write-Host "  $DistRoot"
