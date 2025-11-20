# CSV Data Sorting - Implementation Guide

## 📊 Data Storage Format

All CSV files in `data/market_data/stocks/` and `data/market_data/etfs/` are stored in **DESCENDING order** (newest date first).

### Example:
```csv
Date,Open,High,Low,Close,Volume,Dividends,Stock Splits
2025-11-20,90.20,90.51,82.94,83.36,38920366,0.0,0.0  ← LATEST (row 1)
2025-11-19,90.60,91.08,88.89,89.53,18256200,0.0,0.0
2025-11-18,92.10,92.92,89.33,90.86,17439400,0.0,0.0
...
2019-05-10,42.00,45.00,41.06,41.57,186322500,0.0,0.0  ← OLDEST (last row)
```

## ✅ Benefits

1. **Easy Visual Inspection**: Latest data at the top when viewing files
2. **Quick Access**: Most recent data loads first
3. **Consistent Format**: All CSVs follow same convention

## 🔧 Implementation

### 1. Data Fetching (`src/fetch_daily_prices.py`)

```python
# Save CSVs in descending order
combined = combined.sort_index(ascending=False)
combined.reset_index().to_csv(path, index=False)
```

**Key Points**:
- Fetches new data incrementally
- Combines with old data
- Sorts descending (newest first)
- Uses `index.max()` to get latest date (order-agnostic)

### 2. Analysis Scripts

All analysis scripts **MUST** sort data ascending for proper analysis:

#### Master Scanner (`scripts/master_daily_scan.py`)
```python
df = pd.read_csv(check_file, index_col=0, parse_dates=True)
df = df.sort_index(ascending=True)  # ✅ Sort for analysis
# Now df.iloc[-1] is the LATEST row
```

#### Strategy Runner (`src/strategy_runner.py`)
```python
df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
df = df.sort_index(ascending=True)  # ✅ Sort for analysis
# Now df.iloc[-1] is the LATEST row
```

#### Symbol Selector (`src/symbol_selector.py`)
```python
df = pd.read_csv(csv_file)
# CSV is descending, so:
latest_close = df['Close'].iloc[0]   # ✅ First row = latest
prev_close = df['Close'].iloc[1]     # ✅ Second row = previous
```

**Two Approaches**:
1. **Sort ascending** → Use `iloc[-1]` for latest
2. **Don't sort** → Use `iloc[0]` for latest (CSV is descending)

## 📝 Code Review Checklist

When adding new analysis code, ensure:

- [ ] CSV is loaded correctly
- [ ] Date sorting is handled explicitly
- [ ] Latest data is accessed correctly (`iloc[-1]` after ascending sort OR `iloc[0]` from raw CSV)
- [ ] Historical lookback windows use correct indexing
- [ ] Volume/price calculations use correct row order

## 🧪 Testing

To verify correct handling:

```python
# Test script
import pandas as pd

df = pd.read_csv('data/market_data/stocks/UBER.csv')
print(f"Raw CSV first date (should be newest): {df['Date'].iloc[0]}")
print(f"Raw CSV last date (should be oldest): {df['Date'].iloc[-1]}")

df = pd.read_csv('data/market_data/stocks/UBER.csv', index_col='Date', parse_dates=True)
df = df.sort_index(ascending=True)
print(f"After sort, last date (should be newest): {df.index[-1]}")
print(f"Latest close: {df['Close'].iloc[-1]}")
```

## 🚨 Common Pitfalls

### ❌ Wrong: Assuming CSV is ascending
```python
df = pd.read_csv(file)
latest = df.iloc[-1]  # ❌ This is OLDEST, not latest!
```

### ✅ Correct: Explicit sorting
```python
df = pd.read_csv(file, index_col='Date', parse_dates=True)
df = df.sort_index(ascending=True)
latest = df.iloc[-1]  # ✅ Now this is latest
```

### ✅ Also Correct: Use index directly
```python
df = pd.read_csv(file)
latest = df.iloc[0]  # ✅ First row in descending CSV
```

## 📚 Files Updated

All these files now handle descending CSV format:

1. `src/fetch_daily_prices.py` - Saves in descending order
2. `scripts/master_daily_scan.py` - Sorts ascending for analysis
3. `src/strategy_runner.py` - Sorts ascending for analysis
4. `src/abc_strategy.py` - Sorts ascending for analysis
5. `src/symbol_selector.py` - Uses `iloc[0]` for latest (4 locations fixed)

## 🎯 Summary

**Storage**: Descending (newest first)  
**Analysis**: Sort ascending explicitly  
**Access**: `iloc[-1]` after sorting OR `iloc[0]` from raw CSV  
**Why**: Easy viewing + Correct analysis

