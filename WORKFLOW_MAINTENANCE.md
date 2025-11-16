# 🔧 Workflow Maintenance Guide

**Important**: This guide ensures all automation scripts stay synchronized when adding new features.

---

## 📋 Checklist: Adding a New Feature

When you add a new feature to the Daily Market Automation system, follow this checklist to ensure all workflows are updated.

### ✅ Step-by-Step Integration

1. **Create the core Python script** (e.g., `scripts/new_feature.py`)
2. **Test it locally** (`python scripts/new_feature.py`)
3. **Update all workflows** (see sections below)
4. **Update documentation** (README, guides)
5. **Test complete workflows**
6. **Commit and push**

---

## 🎯 Files That Need Updates

### 1. Master Workflow Scripts

When adding a new feature, update these master workflow scripts:

#### macOS/Linux: `scripts/run_daily_workflow.sh`

**Location of changes**: Around line 40-80 (the main workflow steps)

```bash
# Example: Adding a new feature
echo ""
echo -e "${BLUE}=== Step 5: Running New Feature ===${NC}"
python scripts/new_feature_script.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} New feature completed successfully"
else
    echo -e "${RED}✗${NC} Failed to run new feature"
    exit 1
fi
```

**Files to update:**
- ✅ `scripts/run_daily_workflow.sh` (for daily features)
- ✅ `scripts/run_weekly_workflow.sh` (for weekly features)

---

#### Windows: `scripts/run_daily_workflow.bat`

**Location of changes**: Around line 60-120 (the main workflow steps)

```batch
REM Example: Adding a new feature
echo.
echo === Step 5: Running New Feature ===
echo === Step 5: Running New Feature === >> %LOG_FILE%
python scripts\new_feature_script.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to run new feature
    echo [X] Failed to run new feature >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] New feature completed successfully
    echo [OK] New feature completed successfully >> %LOG_FILE%
)
```

**Files to update:**
- ✅ `scripts/run_daily_workflow.bat` (for daily features)
- ✅ `scripts/run_weekly_workflow.bat` (for weekly features)

---

### 2. Individual Task Scripts (Windows Only)

If the feature should run independently, create a dedicated batch file:

**Template: `scripts/run_new_feature.bat`**

```batch
@echo off
REM Description of what this feature does
cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python scripts\new_feature_script.py >> logs\new_feature.log 2>&1
```

**Naming convention:**
- `run_daily_*.bat` - For daily tasks
- `run_weekly_*.bat` - For weekly tasks

---

### 3. GitHub Actions Workflows

Update the appropriate workflow file in `.github/workflows/`:

#### For Daily Features: `daily-alerts.yml`, `daily-news-scan.yml`

```yaml
# Add a new step
- name: Run New Feature
  run: |
    python scripts/new_feature_script.py
```

#### For Weekly Features: `weekly-sp500-scan.yml`

```yaml
# Add a new step
- name: Run New Feature
  run: |
    python scripts/new_feature_script.py
```

**Files to check:**
- ✅ `.github/workflows/daily-fetch.yml` (data fetching)
- ✅ `.github/workflows/daily-charts.yml` (chart generation)
- ✅ `.github/workflows/daily-alerts.yml` (trading alerts)
- ✅ `.github/workflows/daily-news-scan.yml` (news scanning)
- ✅ `.github/workflows/weekly-sp500-scan.yml` (S&P 500 scanning)
- ✅ `.github/workflows/on-demand-analysis.yml` (on-demand analysis)

---

### 4. Setup Scripts

Update setup scripts to mention new features:

#### `scripts/setup_local.sh` (macOS/Linux)

**Location**: Near the end (around line 130+), in the "Next Steps" section

```bash
echo "New Features:"
echo "  ${YELLOW}python scripts/new_feature_script.py${NC}  # Run new feature"
```

#### `scripts/setup_local.bat` (Windows)

**Location**: Near the end (around line 160+), in the "Quick Commands" section

```batch
echo Quick Commands:
echo    python scripts\new_feature_script.py  - Run new feature
```

---

### 5. Task Scheduler Setup (Windows)

#### `scripts/setup_scheduled_tasks.ps1`

If the feature needs its own schedule, add a new task:

```powershell
Write-Host "[X/Y] Creating New Feature Task..." -ForegroundColor Yellow

$newFeatureTrigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday `
    -At 5:00PM

$newFeatureAction = New-ScheduledTaskAction `
    -Execute "$ProjectDir\scripts\run_new_feature.bat" `
    -WorkingDirectory $ProjectDir

Register-ScheduledTask `
    -TaskName "New Feature Task" `
    -Trigger $newFeatureTrigger `
    -Action $newFeatureAction `
    -Settings $settings `
    -User $currentUser `
    -Description "Description of new feature" `
    -RunLevel Highest
```

---

### 6. Documentation Updates

Update these documentation files:

#### `README.md`

**Location**: Features section (around line 27-47)

```markdown
- 🆕 **New Feature Name** - Brief description of what it does
```

**Location**: Quick start section (if applicable)

```bash
# Add command example
python scripts/new_feature_script.py
```

---

#### `LOCAL_SETUP_GUIDE.md`

**Location**: "Running Scripts Manually" section (around line 80-150)

```markdown
#### 7. New Feature Name

\`\`\`bash
# Run the new feature
python scripts/new_feature_script.py
\`\`\`

**Output:**
\`\`\`
✅ New feature completed successfully
\`\`\`
```

**Location**: Cron examples (around line 250-280)

```bash
# X. Run new feature at Y:ZZ PM EST
YY ZZ * * 1-5 cd $PROJECT && venv/bin/python scripts/new_feature_script.py >> logs/new_feature.log 2>&1
```

---

#### `LOCAL_SETUP_WINDOWS.md`

**Location**: "Running Scripts" section (around line 80-150)

```markdown
#### 7. New Feature Name

\`\`\`powershell
# Run the new feature
python scripts\new_feature_script.py
\`\`\`
```

**Location**: Task Scheduler table (around line 280-320)

```markdown
| New Feature Task | `run_new_feature.bat` | Y:ZZ PM | Mon-Fri |
```

---

#### `WINDOWS_QUICKSTART.md` / Quick Start Sections

**Location**: "Individual Commands" section (near end)

```markdown
# New feature
python scripts\new_feature_script.py
```

---

### 7. Summary Documents

#### `LOCAL_AUTOMATION_SUMMARY.md`

**Location**: Schedule table (around line 70-90)

```markdown
| Y:ZZ PM EST | New Feature | Description of feature |
```

**Location**: "What You'll Receive" section (around line 150-200)

```markdown
**4. New Feature Alerts (Y:ZZ PM)**
\`\`\`
🆕 NEW FEATURE RESULTS

Summary of results...
\`\`\`
```

---

## 🔄 Example: Adding "Auto-Add to Portfolio" Feature

Let's walk through adding the next planned feature as an example:

### 1. Create the Script

```bash
# Create the new script
touch scripts/auto_add_portfolio.py
```

### 2. Update Master Workflows

**`scripts/run_daily_workflow.sh`** (add after news scanner):

```bash
echo ""
echo -e "${BLUE}=== Step 5: Auto-Add High-Score Opportunities ===${NC}"
python scripts/auto_add_portfolio.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Auto-add portfolio check complete"
else
    echo -e "${RED}✗${NC} Failed to check auto-add portfolio"
    exit 1
fi
```

**`scripts/run_daily_workflow.bat`** (add after news scanner):

```batch
REM Step 5: Auto-Add High-Score Opportunities
echo.
echo === Step 5: Auto-Add High-Score Opportunities ===
echo === Step 5: Auto-Add High-Score Opportunities === >> %LOG_FILE%
python scripts\auto_add_portfolio.py >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo [X] Failed to check auto-add portfolio
    echo [X] Failed to check auto-add portfolio >> %LOG_FILE%
    exit /b 1
) else (
    echo [OK] Auto-add portfolio check complete
    echo [OK] Auto-add portfolio check complete >> %LOG_FILE%
)
```

### 3. Update GitHub Actions

**`.github/workflows/daily-news-scan.yml`** (add after news scan step):

```yaml
- name: Auto-Add High-Score Opportunities
  run: |
    python scripts/auto_add_portfolio.py
```

### 4. Update Documentation

**`README.md`** - Add to features:

```markdown
- 🤖 **Auto-Add to Portfolio** - Automatically adds high-score opportunities to tracking
```

**`LOCAL_SETUP_GUIDE.md`** - Add command:

```markdown
#### 8. Auto-Add High-Score Opportunities

\`\`\`bash
python scripts/auto_add_portfolio.py
\`\`\`
```

**`LOCAL_AUTOMATION_SUMMARY.md`** - Update schedule:

```markdown
| 4:50 PM EST | Auto-Add Check | Add high-score opportunities to portfolio |
```

### 5. Test Everything

```bash
# Test the new script
python scripts/auto_add_portfolio.py

# Test the master workflow
./scripts/run_daily_workflow.sh  # macOS/Linux
.\scripts\run_daily_workflow.bat  # Windows

# Check logs
tail -f logs/daily_workflow.log
```

### 6. Commit and Push

```bash
git add -A
git commit -m "feat: Add auto-add to portfolio feature

- Add scripts/auto_add_portfolio.py
- Update daily workflow scripts (sh/bat)
- Update GitHub Actions workflow
- Update all documentation"
git push
```

---

## 📝 Quick Reference: Files to Update

When adding a new feature, use this checklist:

### Core Implementation
- [ ] Create Python script in `scripts/` or `src/`
- [ ] Add to `requirements-base.txt` (if new dependencies)
- [ ] Test locally

### Workflow Integration
- [ ] `scripts/run_daily_workflow.sh` (if daily)
- [ ] `scripts/run_daily_workflow.bat` (if daily)
- [ ] `scripts/run_weekly_workflow.sh` (if weekly)
- [ ] `scripts/run_weekly_workflow.bat` (if weekly)
- [ ] Create `scripts/run_feature_name.bat` (Windows modular)

### GitHub Actions
- [ ] `.github/workflows/daily-alerts.yml` or
- [ ] `.github/workflows/daily-news-scan.yml` or
- [ ] `.github/workflows/weekly-sp500-scan.yml`

### Automation Setup
- [ ] `scripts/setup_scheduled_tasks.ps1` (if needs own schedule)
- [ ] `scripts/setup_local.sh` (mention in "Next Steps")
- [ ] `scripts/setup_local.bat` (mention in "Quick Commands")

### Documentation
- [ ] `README.md` (features list, usage examples)
- [ ] `LOCAL_SETUP_GUIDE.md` (commands, cron examples)
- [ ] `LOCAL_SETUP_WINDOWS.md` (commands, Task Scheduler)
- [ ] `WINDOWS_QUICKSTART.md` (if major feature)
- [ ] `LOCAL_AUTOMATION_SUMMARY.md` (schedule, outputs)
- [ ] Create feature-specific guide (e.g., `FEATURE_QUICKSTART.md`)
- [ ] Update `ADVANCED_FEATURES_ROADMAP.md` (mark as complete)

### Testing
- [ ] Run script manually
- [ ] Run complete daily workflow
- [ ] Check logs
- [ ] Test on both platforms (if possible)
- [ ] Verify Telegram notifications

---

## 🎯 Upcoming Features

Based on `ADVANCED_FEATURES_ROADMAP.md`, here are the next features to integrate:

### 1. Auto-Add to Portfolio (Next)
**Priority**: High
**Complexity**: Simple (~1 hour)
**Impact**: All workflow files

**Will need to update:**
- ✅ Daily workflow scripts (sh/bat)
- ✅ GitHub Actions (daily-news-scan.yml)
- ✅ Documentation (all guides)
- ✅ Schedule tables (runs after news scanner)

---

### 2. News Sentiment ML (FinBERT)
**Priority**: Medium
**Complexity**: Medium (~2-3 hours)
**Impact**: News scanner only

**Will need to update:**
- ✅ `scripts/send_news_opportunities.py` (integrate FinBERT)
- ✅ `requirements-base.txt` (add transformers, torch)
- ✅ Documentation (NEWS_SCANNER_GUIDE.md)
- ⚠️ **NOTE**: FinBERT adds ~500MB download, mention in setup guides

---

## 🚨 Common Mistakes to Avoid

### ❌ DON'T:
1. **Update only one platform** - Always update both macOS/Linux AND Windows scripts
2. **Forget GitHub Actions** - Users may still use cloud automation
3. **Skip documentation** - Users need to know about new features
4. **Ignore error handling** - Add proper logging and error checks
5. **Hardcode paths** - Use relative paths or variables

### ✅ DO:
1. **Test on both platforms** (if possible, or at least check syntax)
2. **Update all 3 workflow types**: Local (sh/bat), GitHub Actions, Task Scheduler
3. **Add logging** - `>> logs/feature_name.log 2>&1`
4. **Update schedule tables** - Show when the feature runs
5. **Add examples** - Show expected output in docs

---

## 🔍 Testing Checklist

After updating workflows for a new feature:

```bash
# 1. Test the new script alone
python scripts/new_feature.py

# 2. Test daily workflow (macOS/Linux)
./scripts/run_daily_workflow.sh

# 3. Test daily workflow (Windows)
.\scripts\run_daily_workflow.bat

# 4. Check logs were created
ls -lh logs/

# 5. Verify GitHub Actions syntax
# (Push to a test branch and watch Actions tab)

# 6. Test scheduled task (if added)
# macOS/Linux: Run cron job manually
# Windows: Right-click task → Run

# 7. Verify Telegram notifications work

# 8. Check all generated files
ls -lh data/ charts/ signals/
```

---

## 📊 Version Control Best Practices

When committing workflow updates:

```bash
# Good commit message format
git commit -m "feat: Add [Feature Name] to all workflows

- Add scripts/new_feature.py
- Update daily workflow scripts (macOS/Linux + Windows)
- Update GitHub Actions workflows
- Update Task Scheduler setup
- Update documentation (README, setup guides)
- Add feature-specific guide

Closes #issue_number"
```

---

## 🆘 Need Help?

If you're unsure what to update:

1. **Search for similar features**: Look at how existing features are integrated
2. **Use grep to find files**: `grep -r "send_news_opportunities" .`
3. **Check git history**: `git log --all --full-history --oneline -- scripts/`
4. **Review this guide**: Follow the checklist step-by-step
5. **Test incrementally**: Update one file at a time and test

---

## 📚 Related Files

- [`ADVANCED_FEATURES_ROADMAP.md`](ADVANCED_FEATURES_ROADMAP.md) - Planned features
- [`LOCAL_AUTOMATION_SUMMARY.md`](LOCAL_AUTOMATION_SUMMARY.md) - Current automation status
- [`README.md`](README.md) - Project overview
- [`.github/workflows/`](.github/workflows/) - GitHub Actions workflows
- [`scripts/`](scripts/) - All automation scripts

---

**Remember**: Every new feature should work seamlessly in:
1. ✅ Local manual execution
2. ✅ Local automated execution (cron/Task Scheduler)
3. ✅ GitHub Actions automated execution
4. ✅ Both macOS/Linux AND Windows platforms

**Keep this guide updated as the project evolves!** 🚀

