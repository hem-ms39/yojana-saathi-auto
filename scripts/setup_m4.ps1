$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $root "venv"

if (-not (Test-Path $venvPath)) {
  python -m venv $venvPath
}

$python = Join-Path $venvPath "Scripts\\python.exe"

& $python -m pip install --upgrade pip
& $python -m pip install -e "$root\\backend[dev]"

Copy-Item "$root\\.env.example" "$root\\.env" -ErrorAction SilentlyContinue
Copy-Item "$root\\frontend\\.env.local.example" "$root\\frontend\\.env.local" -ErrorAction SilentlyContinue

Push-Location "$root\\frontend"
cmd /c npm install
Pop-Location
