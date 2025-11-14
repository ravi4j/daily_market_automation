# Portfolio Configuration

This directory contains configuration files for customizing your trading automation.

## symbols.yaml

Configure which symbols to track and analyze in your portfolio.

### File Format

```yaml
symbols:
  SYMBOL_KEY: TICKER_SYMBOL
```

- **SYMBOL_KEY**: Used for CSV filename (e.g., `AAPL.csv`)
- **TICKER_SYMBOL**: Used by yfinance to fetch data

### Examples

#### Regular Stocks
```yaml
symbols:
  AAPL: AAPL
  MSFT: MSFT
  GOOGL: GOOGL
  TSLA: TSLA
```

#### ETFs
```yaml
symbols:
  TQQQ: TQQQ      # 3x Leveraged NASDAQ
  SPY: SPY        # S&P 500 ETF
  QQQ: QQQ        # NASDAQ-100 ETF
  VTI: VTI        # Total Stock Market ETF
```

#### Market Indices
```yaml
symbols:
  SP500: ^GSPC    # S&P 500 Index
  DOW: ^DJI       # Dow Jones Industrial Average
  NASDAQ: ^IXIC   # NASDAQ Composite
```

#### Mixed Portfolio
```yaml
symbols:
  # Leveraged ETFs
  TQQQ: TQQQ
  SOXL: SOXL
  
  # Regular Stocks
  AAPL: AAPL
  NVDA: NVDA
  
  # Benchmark Indices
  SP500: ^GSPC
  NASDAQ: ^IXIC
```

### How to Update Your Portfolio

1. **Open** `config/symbols.yaml` in any text editor
2. **Add** new symbols:
   ```yaml
   symbols:
     EXISTING: EXISTING
     NEW_SYMBOL: NEW_SYMBOL  # Add this line
   ```
3. **Remove** symbols by deleting the line or commenting it out:
   ```yaml
   symbols:
     KEEP_THIS: KEEP_THIS
     # REMOVE_THIS: REMOVE_THIS  # Commented out
   ```
4. **Save** the file
5. **Run** the fetch script:
   ```bash
   python src/fetch_daily_prices.py
   ```

### Notes

- Changes take effect immediately on the next run
- No need to restart workflows or modify Python code
- Invalid tickers will be skipped with a warning
- The system will fall back to defaults if the config file is missing or invalid

### Fallback Behavior

If `config/symbols.yaml` is missing or cannot be read, the system uses these defaults:
```yaml
symbols:
  TQQQ: TQQQ
  SP500: ^GSPC
  AAPL: AAPL
  UBER: UBER
```

## Best Practices

1. **Commit the config file** to Git so workflows use your portfolio
2. **Keep 5-10 symbols** for faster processing and cleaner alerts
3. **Use ETFs over mutual funds** for better technical analysis
4. **Include a benchmark** (like ^GSPC) to compare performance
5. **Test locally** before pushing changes to production

