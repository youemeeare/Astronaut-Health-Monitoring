
$ErrorActionPreference = "Stop"

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host " ASTRA-MED X - DEPENDENCY INSTALLER" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check project folders
$folders = @("backend", "frontend", "mobile")

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        throw "Missing project folder: $folder. Run this script from the project root."
    }
}

# Check Python 3.12
Write-Host "`n[1/5] Checking Python 3.12..." -ForegroundColor Yellow

py -3.12 --version
if ($LASTEXITCODE -ne 0) {
    throw "Python 3.12 is missing. Install Python 3.12 first."
}

# Check Node.js
Write-Host "`n[2/5] Checking Node.js..." -ForegroundColor Yellow

node --version
if ($LASTEXITCODE -ne 0) {
    throw "Node.js is missing."
}

npm --version
if ($LASTEXITCODE -ne 0) {
    throw "npm is missing."
}

# Backend installation
Write-Host "`n[3/5] Installing Python backend dependencies..." -ForegroundColor Yellow

Push-Location backend

try {
    if (!(Test-Path ".venv")) {
        py -3.12 -m venv .venv
    }

    & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip

    if (!(Test-Path "requirements.txt")) {
        throw "backend/requirements.txt not found."
    }

    & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

    if ($LASTEXITCODE -ne 0) {
        throw "Backend dependency installation failed."
    }
}
finally {
    Pop-Location
}

# Frontend installation
Write-Host "`n[4/5] Installing React frontend dependencies..." -ForegroundColor Yellow

Push-Location frontend

try {
    if (!(Test-Path "package.json")) {
        throw "frontend/package.json not found."
    }

    npm install

    if ($LASTEXITCODE -ne 0) {
        throw "Frontend installation failed."
    }
}
finally {
    Pop-Location
}

# Mobile installation
Write-Host "`n[5/5] Installing Expo mobile dependencies..." -ForegroundColor Yellow

Push-Location mobile

try {
    if (!(Test-Path "package.json")) {
        throw "mobile/package.json not found."
    }

    npm install

    if ($LASTEXITCODE -ne 0) {
        throw "Mobile npm installation failed."
    }

    npx expo install --fix

    if ($LASTEXITCODE -ne 0) {
        throw "Expo compatibility installation failed."
    }

    npx expo-doctor

    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Expo Doctor reported issues. Review its output."
    }
}
finally {
    Pop-Location
}

Write-Host "`n=====================================" -ForegroundColor Green
Write-Host " INSTALLATION PROCESS COMPLETED!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host "`nNext: Start backend, frontend and mobile separately."
