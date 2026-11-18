param(
    [switch]$UseMainnet,
    [int]$Blocks = 120,
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"
$projectDir = $PSScriptRoot

function Find-Python {
    if ($env:RISKFLOW_PYTHON -and (Test-Path -LiteralPath $env:RISKFLOW_PYTHON)) {
        return $env:RISKFLOW_PYTHON
    }
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike "*WindowsApps*") {
        return $command.Source
    }
    $bundled = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path -LiteralPath $bundled) {
        return $bundled
    }
    throw "Khong tim thay Python 3.11+. Hay cai Python hoac dat bien RISKFLOW_PYTHON."
}

$pythonExe = Find-Python
Push-Location $projectDir
try {
    if ($UseMainnet) {
        & $pythonExe "scripts\run_mainnet.py" --blocks $Blocks
    } else {
        & $pythonExe "scripts\run_abm_demo.py"
    }
    if ($LASTEXITCODE -ne 0) { throw "Pipeline khong chay thanh cong." }
    Write-Host "Mo dashboard tai http://127.0.0.1:$Port" -ForegroundColor Green
    & $pythonExe "scripts\run_dashboard.py" --port $Port
} finally {
    Pop-Location
}

