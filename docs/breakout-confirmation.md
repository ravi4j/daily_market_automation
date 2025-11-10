# Breakout Confirmation Filters

This document explains the sophisticated confirmation filters used to validate breakouts and reduce false signals.

## Overview

The system uses **6 confirmation filters** to validate breakouts. A breakout is considered **CONFIRMED** if it passes at least **4 out of 6** filters.

## The 6 Confirmation Filters

### 1. ✅ **Intrabar Close Confirmation**
**What it checks:** The candle must **close** beyond the breakout level, not just wick through it.

**Why it matters:** Wicks represent temporary price action that was rejected. A close beyond the level shows sustained conviction.

**Example:**
```
Resistance at $100
- ❌ High: $102, Close: $99  → Rejected (just a wick)
- ✅ High: $102, Close: $101 → Confirmed (closed above)
```

**Code:**
```python
if breakout_direction == 'up':
    confirmed = latest['Close'] > breakout_level
else:
    confirmed = latest['Close'] < breakout_level
```

---

### 2. ✅ **Multiple Closes Confirmation**
**What it checks:** Requires N consecutive closes beyond the breakout level.

**Why it matters:** One close could be a false breakout. Multiple closes show sustained momentum.

**Configuration:**
```python
'multiple_closes': 1,  # Default: 1 bar (can be increased to 2-3 for stronger confirmation)
```

**Example:**
```
Resistance at $100, multiple_closes = 2
- Day 1: Close $101 ✓
- Day 2: Close $102 ✓
→ Confirmed: 2 consecutive closes above $100
```

---

### 3. ✅ **Time/Bar Confirmation**
**What it checks:** Price must stay beyond the level for N bars (not just close, but entire bar).

**Why it matters:** Ensures the breakout is sustained over time, not just an intraday spike.

**Configuration:**
```python
'time_bars': 1,  # Default: 1 bar (increase to 2-3 for multi-day confirmation)
```

**Example:**
```
Resistance at $100, time_bars = 1
- Bar 1: Low $101, High $105 ✓
→ Confirmed: Entire bar stayed above $100
```

**Stricter Example:**
```
time_bars = 2
- Bar 1: Low $101 ✓
- Bar 2: Low $99 ❌
→ Not confirmed: Fell back below on Day 2
```

---

### 4. ✅ **Percentage Move Confirmation**
**What it checks:** Price must move at least X% beyond the breakout level.

**Why it matters:** Small movements could be noise. Significant % moves show real momentum.

**Configuration:**
```python
'percentage_threshold': 0.02,  # Default: 2%
```

**Example:**
```
Resistance at $100, threshold = 2%
- Close at $101 → 1% move ❌
- Close at $102 → 2% move ✅
- Close at $103 → 3% move ✅
```

**Per-Symbol Adjustment:**
```python
# Volatile stocks (TQQQ): 2-3%
# Less volatile (SP500): 1-2%
# Individual stocks: 2%
```

---

### 5. ✅ **Point/Dollar Move Confirmation**
**What it checks:** Price must move at least $X beyond the breakout level.

**Why it matters:** Provides absolute price movement threshold, useful for high-priced stocks.

**Configuration:**
```python
'point_threshold': 2.0,  # Default: $2
```

**Example:**
```
Resistance at $100, threshold = $2
- Close at $101 → $1 move ❌
- Close at $102 → $2 move ✅
- Close at $103 → $3 move ✅
```

**Why Both % and $?**
- **Percentage** works well across different price ranges
- **Dollar amount** prevents tiny moves in high-priced stocks from triggering

**Example:**
```
$10 stock: $2 move = 20% ✅ (significant)
$1000 stock: $2 move = 0.2% ❌ (insignificant)
```

---

### 6. ✅ **Volume Confirmation**
**What it checks:** Volume must be above average (default: 1.2x the 20-day average).

**Why it matters:** Breakouts with high volume show institutional participation and conviction.

**Configuration:**
```python
'volume_multiplier': 1.2,  # Default: 1.2x average (120%)
```

**Example:**
```
20-day avg volume: 10M shares
- Current volume: 8M  → 0.8x ❌
- Current volume: 12M → 1.2x ✅
- Current volume: 20M → 2.0x ✅✅ (strong confirmation)
```

**Volume Analysis:**
- **1.0-1.5x**: Normal breakout
- **1.5-2.0x**: Strong breakout
- **2.0x+**: Very strong breakout (institutional buying/selling)

---

## Configuration

### Default Configuration
```python
CONFIRMATION_CONFIG = {
    'percentage_threshold': 0.02,   # 2% move required
    'point_threshold': 2.0,          # $2 move required
    'multiple_closes': 1,            # 1 consecutive close
    'time_bars': 1,                  # 1 bar to confirm
    'volume_multiplier': 1.2,        # 1.2x average volume
}
```

### Conservative Settings (Fewer False Positives)
```python
CONFIRMATION_CONFIG = {
    'percentage_threshold': 0.03,   # 3% move
    'point_threshold': 3.0,          # $3 move
    'multiple_closes': 2,            # 2 consecutive closes
    'time_bars': 2,                  # 2 bars sustained
    'volume_multiplier': 1.5,        # 1.5x volume
}
```

### Aggressive Settings (More Signals)
```python
CONFIRMATION_CONFIG = {
    'percentage_threshold': 0.01,   # 1% move
    'point_threshold': 1.0,          # $1 move
    'multiple_closes': 1,            # 1 close
    'time_bars': 1,                  # 1 bar
    'volume_multiplier': 1.0,        # Same as average
}
```

---

## Scoring System

### Confirmation Score
- Each filter that passes = +1 point
- Maximum score = 6 points
- **Confirmed breakout** = 4+ points (66% confirmation)

### Example Breakdown

```
Resistance Breakout at $100
Current Price: $102.50

✅ Intrabar Close: $102.50 > $100        [1 point]
✅ Multiple Closes: 1 close above        [1 point]
✅ Time Sustained: Low stayed above      [1 point]
✅ Percentage: 2.5% > 2% threshold       [1 point]
✅ Point Move: $2.50 > $2 threshold      [1 point]
❌ Volume: 1.1x < 1.2x threshold         [0 points]

TOTAL: 5/6 → CONFIRMED ✅
```

### Unconfirmed Example

```
Resistance Breakout at $100
Current Price: $101.00

✅ Intrabar Close: $101 > $100           [1 point]
❌ Multiple Closes: Need 2, only 1       [0 points]
❌ Time Sustained: Low at $99.50         [0 points]
❌ Percentage: 1% < 2% threshold         [0 points]
✅ Point Move: $1 < $2 threshold         [0 points]
❌ Volume: 0.9x < 1.2x threshold         [0 points]

TOTAL: 1/6 → UNCONFIRMED ⚠️
```

---

## Output Format

When a breakout is detected, the system shows:

```
🚨 BREAKOUT DETECTED: RESISTANCE_BREAKOUT_CONFIRMED

📋 CONFIRMATION FILTERS (Score: 5/6):
   ✓ Intrabar Close: ✅
   ✓ Multiple Closes: ✅
   ✓ Time Sustained: ✅
   ✓ Percentage Move: ✅ (2.50%)
   ✓ Point Move: ✅ ($2.50)
   ✓ Volume Surge: ❌ (1.10x avg)

   ✅ BREAKOUT CONFIRMED!
```

or

```
🚨 BREAKOUT DETECTED: RESISTANCE_BREAKOUT_UNCONFIRMED

📋 CONFIRMATION FILTERS (Score: 2/6):
   ✓ Intrabar Close: ✅
   ✓ Multiple Closes: ❌
   ✓ Time Sustained: ❌
   ✓ Percentage Move: ✅ (2.10%)
   ✓ Point Move: ❌ ($1.50)
   ✓ Volume Surge: ❌ (0.95x avg)

   ⚠️ BREAKOUT UNCONFIRMED (needs more confirmation)
```

---

## Per-Symbol Customization

You can customize thresholds per symbol based on volatility:

```python
# High volatility (TQQQ, leveraged ETFs)
if symbol == "TQQQ":
    config['percentage_threshold'] = 0.03  # 3%
    config['volume_multiplier'] = 1.5      # 1.5x

# Low volatility (SP500 index)
elif symbol == "SP500":
    config['percentage_threshold'] = 0.015 # 1.5%
    config['point_threshold'] = 10.0       # $10 (higher price)

# Individual stocks
else:
    config['percentage_threshold'] = 0.02  # 2%
    config['point_threshold'] = 2.0        # $2
```

---

## Best Practices

### 1. Start Conservative
- Begin with default settings (4/6 required)
- Adjust based on your risk tolerance

### 2. Backtest Your Settings
- Test different threshold combinations
- Measure false positive rate
- Track successful breakouts

### 3. Consider Market Conditions
- **Volatile markets**: Increase thresholds
- **Range-bound markets**: Require more confirmation
- **Trending markets**: Can be more aggressive

### 4. Use Multiple Timeframes
- Daily breakouts: Current settings
- Weekly breakouts: Increase time_bars to 5
- Intraday breakouts: Use shorter lookbacks

### 5. Combine with Other Signals
- RSI divergence
- MACD crossover
- Moving average alignment
- Market breadth indicators

---

## False Breakout Prevention

The confirmation filters specifically address these common false breakout scenarios:

1. **Wick Rejections** → Intrabar close filter
2. **Single-Bar Spikes** → Multiple closes filter
3. **Intraday Fakeouts** → Time confirmation filter
4. **Noise/Volatility** → Percentage & point filters
5. **Low Volume Moves** → Volume confirmation filter

By requiring 4/6 confirmations, the system significantly reduces false signals while catching real breakouts.

---

## Summary

The 6-filter confirmation system provides:

✅ **Robust Validation** - Multiple independent checks
✅ **Flexibility** - Configurable thresholds
✅ **Reduced False Positives** - Filters out noise
✅ **Transparency** - Clear scoring system
✅ **Adaptability** - Per-symbol customization

This approach balances **signal quality** (fewer false positives) with **signal quantity** (catching real breakouts), giving you high-confidence trading signals.
