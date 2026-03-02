# DevDeck Windows Installer
# This script installs DevDeck on Windows systems

Write-Host "🚀 Installing DevDeck..." -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    Write-Host "This script should not be run as Administrator. Please run without elevated privileges." -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow

# Check if Python 3 is installed
try {
    $pythonVersion = & python --version 2>$null
    if (-not $pythonVersion) {
        $pythonVersion = & python3 --version 2>$null
    }
} catch {
    $pythonVersion = $null
}

if (-not $pythonVersion) {
    Write-Host "Python 3 is not installed. Please install Python 3 and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Found Python: $pythonVersion" -ForegroundColor Green

# Check if pip is installed
try {
    $pipVersion = & pip --version 2>$null
} catch {
    $pipVersion = $null
}

if (-not $pipVersion) {
    Write-Host "pip is not installed. Please install pip and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Found pip: $pipVersion" -ForegroundColor Green

# Create temp directory
$tempDir = [System.IO.Path]::GetTempPath()
$installDir = Join-Path $tempDir "devdeck-install"
if (Test-Path $installDir) {
    Remove-Item -Recurse -Force $installDir
}
New-Item -ItemType Directory -Path $installDir | Out-Null
Write-Host "Created temporary directory: $installDir" -ForegroundColor Yellow

# Cleanup function
function Cleanup {
    Write-Host "Cleaning up..." -ForegroundColor Yellow
    if (Test-Path $installDir) {
        Remove-Item -Recurse -Force $installDir
    }
}

# Set up trap for cleanup
trap {
    Cleanup
    break
}

# Clone the repository
Write-Host "Cloning DevDeck repository..." -ForegroundColor Yellow
try {
    & git clone https://github.com/Xznder1984/DEV-DECK.git "$installDir\devdeck" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Git clone failed"
    }
} catch {
    Write-Host "Failed to clone repository. Trying with Invoke-WebRequest..." -ForegroundColor Red
    
    # Try downloading with Invoke-WebRequest if git fails
    try {
        $zipPath = "$installDir\devdeck.zip"
        Invoke-WebRequest -Uri "https://github.com/Xznder1984/DEV-DECK/archive/main.zip" -OutFile $zipPath
        Expand-Archive -Path $zipPath -DestinationPath $installDir
        Move-Item -Path "$installDir\DEV-DECK-main" -Destination "$installDir\devdeck"
    } catch {
        Write-Host "Failed to download DevDeck. Please check your internet connection." -ForegroundColor Red
        exit 1
    }
}

# Navigate to the DevDeck directory
Set-Location "$installDir\devdeck"

# Install DevDeck
Write-Host "Installing DevDeck..." -ForegroundColor Yellow
& pip install --user .

# Find the user's Python scripts directory
$userScriptsDir = (& python -m site --user-base) + "\Scripts"
if (!(Test-Path $userScriptsDir)) {
    $userScriptsDir = "$env:LOCALAPPDATA\Programs\Python\Python*\Scripts"
}

# Create the executable script
Write-Host "Creating executable script..." -ForegroundColor Yellow
$scriptContent = @'
@echo off
python -c "import devdeck" >nul 2>&1
if %errorlevel% == 0 (
    python -m main %*
) else (
    echo Error: DevDeck not found. Please reinstall.
    exit /b 1
)
'@
$scriptPath = "$userScriptsDir\devdeck.bat"
if (!(Test-Path $userScriptsDir)) {
    New-Item -ItemType Directory -Path $userScriptsDir | Out-Null
}
Set-Content -Path $scriptPath -Value $scriptContent

Write-Host "✅ DevDeck installed successfully!" -ForegroundColor Green
Write-Host "Run 'devdeck --help' to get started." -ForegroundColor Green
Write-Host "Note: If the 'devdeck' command is not found, please restart your PowerShell session." -ForegroundColor Yellow
