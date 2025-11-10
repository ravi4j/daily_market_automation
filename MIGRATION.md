# Migration Guide - Project Reorganization

## What Changed?

The project has been reorganized into a more professional structure to support multiple automation scripts.

### Old Structure
```
daily_market_automation/
├── fetch_daily_prices.py
├── test_incremental.py
├── data/
└── requirements.txt
```

### New Structure
```
daily_market_automation/
├── src/
│   ├── fetch_daily_prices.py    ← Moved here
│   └── common/                   ← New: shared utilities
├── tests/
│   └── test_incremental.py      ← Moved here
├── scripts/
│   └── setup.sh                  ← New: automated setup
├── docs/
│   └── architecture.md           ← New: documentation
├── data/                         ← Same location
├── requirements-base.txt         ← New: organized deps
├── requirements-fetch.txt        ← New: organized deps
└── requirements-dev.txt          ← New: organized deps
```

## Migration Steps

### Option 1: Clean Migration (Recommended)

If you want to keep the old files as backup:

```bash
# The old files are still in the root directory
# New files are in their proper locations
# You can safely delete the old files once you verify everything works:

# Test the new structure first
python src/fetch_daily_prices.py

# If it works, you can remove old files
rm fetch_daily_prices.py  # Old file (keep if you want backup)
rm test_incremental.py    # Old file (keep if you want backup)
```

### Option 2: Just Start Using New Paths

Simply start using the new paths:

**Old command:**
```bash
python fetch_daily_prices.py
```

**New command:**
```bash
python src/fetch_daily_prices.py
```

## What You Need to Update

### 1. GitHub Actions Workflows

If you have `.github/workflows/` files, update them:

**Old:**
```yaml
- run: python fetch_daily_prices.py
```

**New:**
```yaml
- run: python src/fetch_daily_prices.py
```

### 2. Cron Jobs

**Old:**
```cron
30 18 * * * python fetch_daily_prices.py
```

**New:**
```cron
30 18 * * * python src/fetch_daily_prices.py
```

### 3. Requirements Installation

**Old:**
```bash
pip install -r requirements.txt
```

**New (better organized):**
```bash
pip install -r requirements-fetch.txt  # For running the fetch script
pip install -r requirements-dev.txt    # For development
```

## Benefits of New Structure

✅ **Organized**: Source code separated from tests and docs
✅ **Scalable**: Easy to add more automation scripts in `src/`
✅ **Professional**: Follows Python best practices
✅ **Reusable**: Shared utilities can go in `src/common/`
✅ **Better Dependencies**: Organized requirements files
✅ **Documentation**: Clear structure documented in `docs/`

## No Data Loss

- ✅ Your `data/` directory is unchanged
- ✅ All CSV files remain in the same location
- ✅ The script automatically finds the correct data directory

## Questions?

See `README.md` for full documentation and `docs/architecture.md` for technical details.
