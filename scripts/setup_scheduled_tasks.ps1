# PowerShell Script to Set Up Windows Task Scheduler
# Run as Administrator
# Usage: .\scripts\setup_scheduled_tasks.ps1

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Daily Market Automation" -ForegroundColor Cyan
Write-Host "  Windows Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

Write-Host "Project Directory: $ProjectDir" -ForegroundColor Gray
Write-Host ""

# Task settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Get current user
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

Write-Host "[1/3] Creating Daily Workflow Task..." -ForegroundColor Yellow

# Daily Workflow (4:30 PM, Mon-Fri)
$dailyTrigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
    -At 4:30PM

$dailyAction = New-ScheduledTaskAction `
    -Execute "$ProjectDir\scripts\run_daily_workflow.bat" `
    -WorkingDirectory $ProjectDir

try {
    Unregister-ScheduledTask -TaskName "Daily Market Automation" -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask `
        -TaskName "Daily Market Automation" `
        -Trigger $dailyTrigger `
        -Action $dailyAction `
        -Settings $settings `
        -User $currentUser `
        -Description "Fetch market data, generate charts, run strategies, and send alerts (Mon-Fri 4:30 PM EST)" `
        -RunLevel Highest
    Write-Host "  [OK] Daily Market Automation task created" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to create daily task: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[2/3] Creating Weekly S&P 500 Scan Task..." -ForegroundColor Yellow

# Weekly S&P 500 Scan (Sunday 6:00 PM)
$weeklyTrigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Sunday `
    -At 6:00PM

$weeklyAction = New-ScheduledTaskAction `
    -Execute "$ProjectDir\scripts\run_weekly_workflow.bat" `
    -WorkingDirectory $ProjectDir

try {
    Unregister-ScheduledTask -TaskName "Weekly S&P 500 Scan" -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask `
        -TaskName "Weekly S&P 500 Scan" `
        -Trigger $weeklyTrigger `
        -Action $weeklyAction `
        -Settings $settings `
        -User $currentUser `
        -Description "Scan S&P 500 for opportunities and update correlations (Sunday 6:00 PM EST)" `
        -RunLevel Highest
    Write-Host "  [OK] Weekly S&P 500 Scan task created" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to create weekly task: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/3] Creating Weekly Correlation Update Task..." -ForegroundColor Yellow

# Weekly Correlation Update (Sunday 12:00 PM)
$corrTrigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Sunday `
    -At 12:00PM

$corrScript = "$ProjectDir\scripts\run_weekly_correlations.bat"

# Create the correlation batch script if it doesn't exist
if (-not (Test-Path $corrScript)) {
    @"
@echo off
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python scripts\update_news_correlations.py >> logs\correlations.log 2>&1
"@ | Out-File -FilePath $corrScript -Encoding ASCII
}

$corrAction = New-ScheduledTaskAction `
    -Execute $corrScript `
    -WorkingDirectory $ProjectDir

try {
    Unregister-ScheduledTask -TaskName "Weekly Correlation Update" -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask `
        -TaskName "Weekly Correlation Update" `
        -Trigger $corrTrigger `
        -Action $corrAction `
        -Settings $settings `
        -User $currentUser `
        -Description "Update news correlation database (Sunday 12:00 PM EST)" `
        -RunLevel Highest
    Write-Host "  [OK] Weekly Correlation Update task created" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to create correlation task: $_" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created Tasks:" -ForegroundColor White
Write-Host "  1. Daily Market Automation" -ForegroundColor Gray
Write-Host "     - Runs: Mon-Fri at 4:30 PM EST" -ForegroundColor Gray
Write-Host "     - Fetches data, generates charts, sends alerts" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Weekly S&P 500 Scan" -ForegroundColor Gray
Write-Host "     - Runs: Sunday at 6:00 PM EST" -ForegroundColor Gray
Write-Host "     - Scans all S&P 500 stocks for opportunities" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Weekly Correlation Update" -ForegroundColor Gray
Write-Host "     - Runs: Sunday at 12:00 PM EST" -ForegroundColor Gray
Write-Host "     - Updates historical news correlations" -ForegroundColor Gray
Write-Host ""
Write-Host "Verify Tasks:" -ForegroundColor Yellow
Write-Host "  Open Task Scheduler (taskschd.msc) and check:" -ForegroundColor Gray
Write-Host "  - Task Scheduler Library" -ForegroundColor Gray
Write-Host "  - Look for 'Daily Market Automation' and 'Weekly S&P 500 Scan'" -ForegroundColor Gray
Write-Host ""
Write-Host "Test Tasks:" -ForegroundColor Yellow
Write-Host "  Right-click task -> Run" -ForegroundColor Gray
Write-Host "  OR run manually:" -ForegroundColor Gray
Write-Host "    .\scripts\run_daily_workflow.bat" -ForegroundColor Cyan
Write-Host "    .\scripts\run_weekly_workflow.bat" -ForegroundColor Cyan
Write-Host ""
Write-Host "View Logs:" -ForegroundColor Yellow
Write-Host "  Get-Content logs\daily_workflow.log -Tail 50" -ForegroundColor Cyan
Write-Host "  Get-Content logs\weekly_workflow.log -Tail 50" -ForegroundColor Cyan
Write-Host ""
Write-Host "Disable Tasks:" -ForegroundColor Yellow
Write-Host "  Disable-ScheduledTask -TaskName 'Daily Market Automation'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remove Tasks:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName 'Daily Market Automation'" -ForegroundColor Cyan
Write-Host ""

pause

