# Changelog

## [1.2.0] - 2025-11-10

### Added - Confirmation Filters & GitHub Workflows

- 🎯 **Advanced Confirmation Filters** (6-filter system)
  - Intrabar close confirmation (close beyond level, not just wick)
  - Multiple consecutive closes validation
  - Time/bar sustainability check
  - Percentage move threshold
  - Point/dollar move threshold
  - Volume surge confirmation (above average volume)
  - Scoring system: 4/6 required for confirmed breakout
  - Reduces false breakout signals significantly

- ⚙️ **GitHub Actions Workflows**
  - `daily-fetch.yml` - Automated data fetching (Mon-Fri after market close)
  - `daily-charts.yml` - Automated chart generation (triggered after fetch)
  - Chained workflows with smart dependencies
  - Artifact uploads (30-day retention)
  - Workflow summaries with chart lists

- 📚 **Documentation**
  - `docs/breakout-confirmation.md` - Comprehensive filter documentation
  - `docs/workflows.md` - GitHub Actions workflow guide
  - Updated README with workflow instructions
  - Configuration examples (conservative/aggressive/default)

### Enhanced
- Breakout detection now shows confirmation scores and details
- Breakout types include CONFIRMED/UNCONFIRMED suffix
- Volume analysis with ratios to average
- Per-filter pass/fail indicators in output

### Configuration
```python
CONFIRMATION_CONFIG = {
    'percentage_threshold': 0.02,   # 2% move
    'point_threshold': 2.0,          # $2 move
    'multiple_closes': 1,            # 1 consecutive close
    'time_bars': 1,                  # 1 bar sustained
    'volume_multiplier': 1.2,        # 1.2x avg volume
}
```

---

## [1.1.0] - 2025-11-10

### Added - Breakout Detection & Visualization
- ✨ **Breakout Detection Script** (`src/detect_breakouts.py`)
  - Trendline breakout detection using linear regression
  - Support/Resistance level identification
  - Swing high/low reversal point detection
  - Configurable lookback periods and thresholds
  - Real-time breakout alerts

- 📊 **Chart Visualization** (`src/visualize_breakouts.py`)
  - Candlestick charts with price action
  - Support and resistance trendlines overlay
  - Horizontal S/R levels
  - Swing point markers (triangles)
  - Breakout alert annotations
  - Auto-saved PNG charts in `charts/` directory

- 📚 **Documentation Updates**
  - Comprehensive breakout detection guide in README
  - Visualization workflow documentation
  - Updated architecture documentation
  - Added CHANGELOG.md

### Enhanced
- Updated `requirements-base.txt` to include `matplotlib>=3.7.0`
- Added `charts/` directory to `.gitignore`
- Enhanced README with breakout analysis examples

### Features
- **3 Analysis Types:**
  1. Trendline violations (bullish/bearish breakouts)
  2. Support/Resistance breaks
  3. Reversal point proximity detection

- **Visual Elements:**
  - Green/Red candlesticks
  - Dashed trendlines (orange resistance, blue support)
  - Dotted horizontal S/R levels
  - Triangle markers for swing points
  - Annotated breakout alerts with arrows

### Usage
```bash
# Detect breakouts (text output)
python src/detect_breakouts.py

# Generate visual charts
python src/visualize_breakouts.py

# Charts saved to: charts/SYMBOL_breakout.png
```

---

## [1.0.0] - 2025-11-10

### Added - Project Reorganization
- 🏗️ **Professional Project Structure**
  - Created `src/` directory for source code
  - Created `tests/` directory for test files
  - Created `scripts/` directory for helper scripts
  - Created `docs/` directory for documentation
  - Organized requirements files (base, fetch, dev)

- ✨ **Incremental Data Fetching**
  - Smart incremental fetching (only downloads new data)
  - Weekend/holiday handling (no errors on market closure)
  - Date-aware logic to avoid unnecessary API calls
  - 2-5 second updates vs 20-30 second full fetches

- 📝 **Documentation**
  - Comprehensive README with step-by-step setup
  - Migration guide (MIGRATION.md)
  - Architecture documentation (docs/architecture.md)
  - TL;DR quick start section

- 🔧 **Developer Experience**
  - Automated setup script (`scripts/setup.sh`)
  - Test script for incremental fetching
  - Organized requirements files
  - Comprehensive `.gitignore`

### Enhanced
- Updated data fetching to use relative paths (works from any location)
- Improved error handling for empty DataFrames
- Better logging for incremental fetch status
- Smart retry logic for transient failures

### Files Created
- `src/fetch_daily_prices.py` - Main data fetching script
- `src/__init__.py` - Package initialization
- `src/common/__init__.py` - Common utilities placeholder
- `tests/test_incremental.py` - Test incremental fetching
- `tests/__init__.py` - Test package initialization
- `scripts/setup.sh` - Automated setup script
- `docs/architecture.md` - Project architecture
- `MIGRATION.md` - Migration guide
- `requirements-base.txt` - Base dependencies
- `requirements-fetch.txt` - Fetch script dependencies
- `requirements-dev.txt` - Development dependencies
- `.gitignore` - Comprehensive ignore rules

### Changed
- Moved `fetch_daily_prices.py` → `src/fetch_daily_prices.py`
- Moved `test_incremental.py` → `tests/test_incremental.py`
- Split `requirements.txt` into organized files
- Updated GitHub Actions workflow paths
- Enhanced README with new structure

### Removed
- Old `requirements.txt` (replaced with organized files)
- Root-level Python scripts (moved to `src/`)

---

## [0.1.0] - Initial Release

### Features
- Basic daily price fetching for TQQQ, SP500, AAPL, UBER
- CSV storage in `data/` directory
- yfinance integration
- Basic error handling
- GitHub Actions workflow
