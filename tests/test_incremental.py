#!/usr/bin/env python3
"""
Test script to verify incremental fetching works correctly.
This creates a temporary CSV with old data and tests if the script fetches only new data.
"""

import os
import shutil
import pandas as pd

# Get project root (parent of tests/ directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ORIGINAL = os.path.join(DATA_DIR, "AAPL.csv")
BACKUP = os.path.join(DATA_DIR, "AAPL.csv.backup")

print("🧪 Testing Incremental Fetch")
print("=" * 50)

# 1. Backup original file
if os.path.exists(ORIGINAL):
    shutil.copy(ORIGINAL, BACKUP)
    print(f"✅ Backed up {ORIGINAL} to {BACKUP}")

    # 2. Read the CSV
    df = pd.read_csv(ORIGINAL)
    total_rows = len(df)
    print(f"📊 Original file has {total_rows} rows")

    # 3. Keep only first 3770 rows (remove last ~5 days)
    df_trimmed = df.head(3770)
    last_date = df_trimmed.iloc[-1]['Date']
    print(f"📅 Trimmed file last date: {last_date}")

    # 4. Save trimmed version
    df_trimmed.to_csv(ORIGINAL, index=False)
    print(f"✂️  Trimmed to {len(df_trimmed)} rows (removed last {total_rows - len(df_trimmed)} rows)")

    print("\n" + "=" * 50)
    print("Now run: python src/fetch_daily_prices.py")
    print("=" * 50)
    print("\nThe script should:")
    print(f"  1. Detect last date: {last_date}")
    print(f"  2. Fetch only data AFTER {last_date}")
    print(f"  3. Add ~{total_rows - len(df_trimmed)} new rows (much faster!)")
    print("\nTo restore original:")
    print(f"  mv {BACKUP} {ORIGINAL}")

else:
    print(f"❌ {ORIGINAL} not found. Run 'python src/fetch_daily_prices.py' first to create it.")
