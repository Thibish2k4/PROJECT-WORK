# Honeytoken Detection System - PowerShell Launcher
# Right-click and select "Run with PowerShell" or double-click

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  HONEYTOKEN DETECTION SYSTEM" -ForegroundColor Green
Write-Host "  Starting Demo Environment..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Change to script directory
Set-Location $PSScriptRoot

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`nLaunching demo system...`n" -ForegroundColor Yellow

# Run the demo launcher
python start_demo.py

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nAn error occurred. Check the output above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
