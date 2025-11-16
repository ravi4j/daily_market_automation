# ✅ Feature Integration Checklist

Use this checklist when adding a new feature to ensure all workflows are updated.

## 📋 Quick Checklist

### Core Implementation
- [ ] Create Python script in `scripts/` or `src/`
- [ ] Test locally: `python scripts/your_feature.py`
- [ ] Add dependencies to `requirements-base.txt` (if needed)

### Workflow Scripts (Local Automation)
- [ ] Update `scripts/run_daily_workflow.sh` (macOS/Linux daily)
- [ ] Update `scripts/run_daily_workflow.bat` (Windows daily)
- [ ] Update `scripts/run_weekly_workflow.sh` (macOS/Linux weekly)
- [ ] Update `scripts/run_weekly_workflow.bat` (Windows weekly)
- [ ] Create `scripts/run_feature_name.bat` (Windows modular, optional)

### GitHub Actions (Cloud Automation)
- [ ] Update `.github/workflows/daily-alerts.yml` (if daily)
- [ ] Update `.github/workflows/daily-news-scan.yml` (if daily)
- [ ] Update `.github/workflows/weekly-sp500-scan.yml` (if weekly)

### Task Scheduler Setup
- [ ] Update `scripts/setup_scheduled_tasks.ps1` (if needs own schedule)

### Documentation
- [ ] Update `README.md` (features list, usage)
- [ ] Update `LOCAL_SETUP_GUIDE.md` (macOS/Linux commands, cron)
- [ ] Update `LOCAL_SETUP_WINDOWS.md` (Windows commands, Task Scheduler)
- [ ] Update `LOCAL_AUTOMATION_SUMMARY.md` (schedule table)
- [ ] Create `FEATURE_QUICKSTART.md` (if major feature)
- [ ] Update `ADVANCED_FEATURES_ROADMAP.md` (mark complete)

### Testing
- [ ] Run script manually
- [ ] Run complete daily workflow
- [ ] Check logs: `tail -f logs/*.log`
- [ ] Verify Telegram notifications
- [ ] Test on both platforms (if possible)

### Commit
- [ ] Commit with descriptive message
- [ ] Push to GitHub
- [ ] Verify GitHub Actions run successfully

---

## 📖 Detailed Guide

See [`WORKFLOW_MAINTENANCE.md`](../WORKFLOW_MAINTENANCE.md) for:
- Detailed instructions for each file
- Code examples for different platforms
- Common mistakes to avoid
- Testing procedures

---

## 🚀 Quick Commands

```bash
# Test new feature
python scripts/your_feature.py

# Test full workflow
./scripts/run_daily_workflow.sh      # macOS/Linux
.\scripts\run_daily_workflow.bat     # Windows

# Check logs
tail -f logs/daily_workflow.log

# Commit
git add -A
git commit -m "feat: Add [feature name]

- Implementation details
- Files updated
- Testing notes"
git push
```

---

**Remember**: Every feature should work on:
- ✅ macOS/Linux (manual + automated)
- ✅ Windows 11 (manual + automated)
- ✅ GitHub Actions (cloud automation)

