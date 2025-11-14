# 🎛️ Quick Start: Customize Your Portfolio

## Add/Remove Symbols in 3 Easy Steps

### 1️⃣ Open the Config File

```bash
# Edit with your favorite editor
nano config/symbols.yaml
# or
vim config/symbols.yaml
# or open in VS Code, etc.
```

### 2️⃣ Modify the Symbols

**Add a symbol:**
```yaml
symbols:
  TQQQ: TQQQ
  AAPL: AAPL
  NVDA: NVDA     # ← Just add this line!
```

**Remove a symbol:**
```yaml
symbols:
  TQQQ: TQQQ
  # AAPL: AAPL   # ← Comment it out or delete the line
  UBER: UBER
```

### 3️⃣ Test & Commit

```bash
# Test the config
python3 test_config.py

# Commit your changes
git add config/symbols.yaml
git commit -m "Update portfolio symbols"
git push
```

That's it! 🎉 The next workflow run will use your updated symbols.

---

## 📋 Common Examples

### Tech Portfolio
```yaml
symbols:
  AAPL: AAPL
  MSFT: MSFT
  GOOGL: GOOGL
  NVDA: NVDA
  TSLA: TSLA
  SP500: ^GSPC
```

### ETF Focus
```yaml
symbols:
  SPY: SPY
  QQQ: QQQ
  TQQQ: TQQQ
  SOXL: SOXL
  VTI: VTI
  SP500: ^GSPC
```

### Current Positions (Default)
```yaml
symbols:
  TQQQ: TQQQ
  SP500: ^GSPC
  AAPL: AAPL
  UBER: UBER
```

---

## ⚡ Pro Tips

1. **Keep it small** - 5-10 symbols process faster
2. **Include a benchmark** - Add ^GSPC or ^DJI for comparison
3. **Use ETFs over mutual funds** - Better for technical analysis
4. **Test locally first** - Run `python3 test_config.py` before pushing
5. **Comment, don't delete** - Use `#` to disable symbols temporarily

---

## 🔍 Finding Ticker Symbols

- **Yahoo Finance**: Search for any stock/ETF and use the symbol shown
- **Indices**: Prefix with `^` (e.g., `^GSPC` for S&P 500)
- **ETFs**: Use the standard ticker (e.g., `SPY`, `QQQ`, `TQQQ`)

---

## ❓ Troubleshooting

**Q: What if I add an invalid ticker?**
A: The script will skip it with a warning and continue with valid symbols.

**Q: Do I need to restart anything?**
A: No! Changes take effect on the next run automatically.

**Q: What if the config file is missing?**
A: The system falls back to default symbols (TQQQ, AAPL, UBER, ^GSPC).

**Q: Can I use mutual funds?**
A: Limited support - use ETF equivalents instead for better technical analysis.

---

## 📚 More Info

- Full documentation: [`config/README.md`](config/README.md)
- Examples: [`config/symbols.yaml.example`](config/symbols.yaml.example)
- Main README: [`README.md`](README.md)
