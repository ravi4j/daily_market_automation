# GitHub Actions Workflows

This document describes the automated workflows that run in GitHub Actions.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Daily Automation                          │
└─────────────────────────────────────────────────────────────┘

        ⏰ Scheduled Trigger
        (Mon-Fri, 6:35 PM CT)
                 │
                 ▼
    ┌────────────────────────┐
    │  daily-fetch.yml       │
    │  Fetch Daily Prices    │
    └────────────────────────┘
                 │
                 │ 1. Fetch OHLCV data (yfinance)
                 │ 2. Update CSV files
                 │ 3. Commit & push
                 │
                 ▼
        ✅ Success / ❌ Failure
                 │
                 │ (on success)
                 ▼
    ┌────────────────────────┐
    │  daily-charts.yml      │
    │  Generate Charts       │
    └────────────────────────┘
                 │
                 │ 1. Detect breakouts
                 │ 2. Generate PNG charts
                 │ 3. Commit & push
                 │ 4. Upload artifacts
                 │
                 ▼
        📊 Charts Ready!
```

## Workflow 1: Data Fetching

**File:** `.github/workflows/daily-fetch.yml`

### Triggers
- **Scheduled**: Monday-Friday at 00:35 UTC (≈6:35 PM Chicago time)
- **Manual**: Via GitHub Actions UI or `gh workflow run daily-fetch.yml`

### Steps
1. **Checkout** - Get latest code
2. **Setup Python** - Python 3.11
3. **Install Dependencies** - `requirements-fetch.txt`
4. **Ensure Directories** - Create `data/` if needed
5. **Run Fetch Script** - `python src/fetch_daily_prices.py`
   - Fetches TQQQ, SP500, AAPL, UBER data
   - Incremental updates (only new data)
   - Smart weekend/holiday handling
6. **Commit Changes** - Push updated CSV files
7. **Upload Artifacts** - CSV files for debugging

### Outputs
- Updated CSV files in `data/` directory
- Committed and pushed to repository
- CSV artifacts (available for 90 days)

### Error Handling
- Continues on per-symbol failures
- Exits success if at least one symbol succeeds
- Logs errors for troubleshooting

---

## Workflow 2: Chart Generation

**File:** `.github/workflows/daily-charts.yml`

### Triggers
- **Workflow Run**: After `daily-fetch.yml` completes successfully
- **Manual**: Via GitHub Actions UI or `gh workflow run daily-charts.yml`

### Dependencies
- Only runs if `daily-fetch.yml` succeeded
- Uses latest committed data from fetch workflow

### Steps
1. **Checkout** - Get latest code (with fresh data)
2. **Setup Python** - Python 3.11
3. **Install Dependencies** - `requirements-base.txt` (includes matplotlib)
4. **Ensure Directories** - Create `data/` and `charts/` if needed
5. **Generate Breakout Charts** - `python src/visualize_breakouts.py`
   - Performs breakout analysis (trendlines, S/R, reversals)
   - Creates candlestick charts
   - Overlays trendlines and S/R levels
   - Adds breakout annotations
   - Saves PNG files
6. **Commit Charts** - Push PNG files with `[skip ci]` to avoid loops
7. **Upload Artifacts** - Chart images (available for 30 days)
8. **Create Summary** - Workflow summary with chart list

**Note**: `visualize_breakouts.py` imports and reuses analysis functions from `detect_breakouts.py`, so no separate detection step is needed.

### Outputs
- PNG chart files in `charts/` directory
- Committed and pushed to repository
- Chart artifacts (available for 30 days)
- Job summary with chart list

### Chart Details
Each symbol gets a chart with:
- Candlestick price action (60 days)
- Support/resistance trendlines (linear regression)
- Horizontal S/R levels
- Swing high/low markers
- Breakout alert annotations
- Statistics and info box

---

## Configuration

### Repository Settings

#### Required Permissions
1. Go to **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

#### Branch Protection (Optional)
If you have branch protection:
- Allow force pushes from workflows
- Or create a separate branch for automation

### Secrets (Optional)
For email notifications, add these secrets:
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_TO`

---

## Manual Execution

### Via GitHub UI
1. Go to **Actions** tab
2. Select workflow (e.g., "Fetch Daily Prices")
3. Click "Run workflow" button
4. Choose branch and click "Run workflow"

### Via GitHub CLI
```bash
# Fetch data manually
gh workflow run daily-fetch.yml

# Generate charts manually
gh workflow run daily-charts.yml

# View workflow runs
gh run list

# View specific run
gh run view <run-id>
```

---

## Troubleshooting

### Workflow Not Running
- Check workflow is enabled in Actions tab
- Verify schedule syntax is correct
- Ensure repository has required permissions

### Fetch Fails
- Check yfinance API is working
- Verify symbols are valid
- Check network connectivity
- Review error logs in workflow run

### Charts Not Generated
- Ensure fetch workflow succeeded first
- Verify matplotlib installed correctly
- Check data files exist in `data/`
- Review chart generation logs

### Commits Not Pushed
- Verify write permissions enabled
- Check branch protection rules
- Ensure git config is correct
- Look for merge conflicts

### Viewing Artifacts
1. Go to workflow run
2. Scroll to "Artifacts" section
3. Download ZIP file
4. Extract and view files

---

## Monitoring

### Success Indicators
- ✅ Green checkmark in Actions tab
- CSV files updated with latest date
- Charts show current prices
- No error messages in logs

### Failure Indicators
- ❌ Red X in Actions tab
- Error messages in logs
- Missing or outdated CSV files
- No chart artifacts

### Best Practices
1. Monitor first few runs carefully
2. Check artifacts to verify data quality
3. Review chart images for accuracy
4. Set up notifications for failures
5. Test manually before relying on schedule

---

## Workflow Dependencies

```
requirements-fetch.txt:
├── pandas>=2.0.0
├── numpy>=1.26.0
├── pytz>=2023.3
└── yfinance>=0.2.50

requirements-base.txt (for charts):
├── pandas>=2.0.0
├── numpy>=1.26.0
├── pytz>=2023.3
└── matplotlib>=3.7.0
```

---

## Future Enhancements

Potential workflow improvements:
- [ ] Slack/Discord notifications on breakouts
- [ ] Email charts as attachments
- [ ] Upload charts to cloud storage (S3, GCS)
- [ ] Create GitHub Issues for significant breakouts
- [ ] Generate PDF reports
- [ ] Multi-timeframe analysis (daily, weekly, monthly)
- [ ] Backtesting results in workflow
- [ ] Performance metrics dashboard
