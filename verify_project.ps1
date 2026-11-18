$ErrorActionPreference = "Stop"
$projectDir = $PSScriptRoot
$pythonExe = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path -LiteralPath $pythonExe)) {
    $pythonExe = (Get-Command python -ErrorAction Stop).Source
}

Push-Location $projectDir
try {
    & $pythonExe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw "Python tests failed." }
    Push-Location "contracts"
    try {
        npm test
        if ($LASTEXITCODE -ne 0) { throw "Solidity tests failed." }
    } finally {
        Pop-Location
    }
} finally {
    Pop-Location
}

