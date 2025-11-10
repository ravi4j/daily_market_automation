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

## Future Enhancements

- Add more symbols
- Technical indicators calculation
- Automated trading signals
- Backtesting framework
- Real-time data streaming
