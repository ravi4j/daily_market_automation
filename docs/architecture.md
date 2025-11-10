# Daily Market Automation - Architecture

## Project Structure

```
daily_market_automation/
├── .github/
│   └── workflows/         # GitHub Actions workflows
├── src/                   # Source code
│   ├── fetch_daily_prices.py  # Main market data fetching script
│   └── common/           # Shared utilities
├── tests/                # Test files
│   └── test_incremental.py
├── scripts/              # Helper scripts
│   └── setup.sh          # Project setup script
├── data/                 # CSV output files
├── docs/                 # Documentation
├── requirements-*.txt    # Python dependencies
└── README.md
```

## Components

### src/fetch_daily_prices.py
Main script that fetches daily OHLCV (Open, High, Low, Close, Volume) data for configured stock symbols.

**Features:**
- Incremental fetching (only downloads new data when CSV exists)
- Automatic retry on failures
- Email notifications (optional)
- Handles multiple symbols concurrently

**Symbols tracked:**
- TQQQ (ProShares UltraPro QQQ)
- ^GSPC (S&P 500 Index)
- AAPL (Apple Inc.)
- UBER (Uber Technologies)

### src/detect_breakouts.py
Technical analysis script that identifies market breakouts and trend changes.

**Features:**
- **Trendline Detection**: Uses linear regression to identify support/resistance trendlines
- **Breakout Detection**: Alerts when price breaks above/below trendlines
- **Support/Resistance Levels**: Calculates key S/R levels from recent price action
- **Swing Points**: Identifies swing highs and lows (reversal points)
- **Trend Direction**: Determines if stock is in uptrend or downtrend

**Analysis Types:**
1. **Trendline Breakouts** - Detects when price violates established trendlines
2. **S/R Breakouts** - Identifies support breaks and resistance breaks
3. **Reversal Points** - Finds when price is near previous swing highs/lows

**Configurable Parameters:**
- Lookback period (default: 60 days)
- S/R window (default: 20 days)
- Breakout threshold (default: 2%)

### src/common/
Shared utilities for future automation scripts.

### tests/
Test files to verify script functionality.

## Data Flow

1. **Check CSV**: Script checks if CSV file exists for each symbol
2. **Incremental Fetch**: If exists, fetch only data after last date
3. **Full Fetch**: If not exists, fetch all historical data
4. **Merge & Clean**: Combine old and new data, remove duplicates
5. **Save**: Write updated CSV to `data/` directory
6. **Notify**: Send optional email summary

## Adding New Automation Scripts

1. Create new script in `src/` directory
2. Add any shared utilities to `src/common/`
3. Add tests to `tests/` directory
4. Update requirements if needed
5. Document in this file

## GitHub Actions Workflows

### .github/workflows/daily-fetch.yml
Automated data fetching workflow that runs daily.

**Schedule**: Monday-Friday at 6:35 PM America/Chicago
**Triggers**: Scheduled cron, manual dispatch

**Process:**
1. Fetches latest OHLCV data for all symbols
2. Updates CSV files incrementally
3. Commits and pushes changes to repository
4. Uploads CSV artifacts for debugging

### .github/workflows/daily-charts.yml
Automated chart generation workflow triggered after fetch completes.

**Triggers**: After daily-fetch.yml succeeds, manual dispatch
**Dependencies**: Requires successful data fetch

**Process:**
1. Runs breakout detection analysis
2. Generates PNG charts with trendlines and annotations
3. Commits and pushes chart images
4. Uploads chart artifacts (30-day retention)
5. Creates workflow summary with chart list

**Workflow Chain:**
```
daily-fetch.yml (data) → daily-charts.yml (charts)
```

See `docs/workflows.md` for detailed workflow documentation.

## Future Enhancements

- Add more symbols
- Email notifications with chart attachments
- Slack/Discord integration for breakout alerts
- Additional technical indicators (RSI, MACD, Bollinger Bands)
- Automated trading signals
- Backtesting framework
- Real-time data streaming
- Multi-timeframe analysis
- Performance metrics dashboard
