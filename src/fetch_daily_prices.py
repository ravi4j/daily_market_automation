#!/usr/bin/env python3
"""
Fetch daily OHLCV data for multiple symbols and store/update CSVs.

Features:
- Incremental fetching: Only downloads NEW data if CSV exists (much faster!)
- Writes/updates data/TQQQ.csv, data/SP500.csv, data/AAPL.csv, data/UBER.csv
- Flattens yfinance MultiIndex columns
- Coerces numerics, drops bad rows, rounds prices to 2 decimals
- Retries on transient download errors
- Summaries computed from *fresh* data to avoid bad legacy rows
- Continues on per-symbol failures so CI can still commit successful results
- Optional email summary via SMTP_* environment variables
"""

import os
import sys
import time
import smtplib
import socket
from email.mime.text import MIMEText
from datetime import datetime

import pandas as pd
import yaml

# --- Dependencies ---
try:
    import yfinance as yf
except ImportError:
    print("ERROR: Missing dependency 'yfinance'. Run: pip install -r requirements-fetch.txt", file=sys.stderr)
    sys.exit(1)

# --- Config ---
def load_symbols_config():
    """Load portfolio positions from config/master_config.yaml"""
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "src" else script_dir
    config_path = os.path.join(project_root, "config", "master_config.yaml")

    # Fallback: If no portfolio positions defined, return empty dict
    # (master scanner will handle symbol selection automatically)
    default_symbols = {}

    if not os.path.exists(config_path):
        print(f"⚠️  Config file not found: {config_path}")
        print("   No portfolio positions to fetch. Master scanner handles symbol selection.")
        return default_symbols

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            # Load portfolio positions from master_config.yaml
            positions = config.get('portfolio', {}).get('positions', {})
            
            if not positions:
                print("ℹ️  No portfolio positions defined in master_config.yaml")
                print("   Master scanner will select symbols automatically.")
                return default_symbols
                
            # Convert positions dict to symbols dict (positions may have share counts)
            # Format: {symbol: shares} → {symbol: symbol}
            symbols = {sym: sym for sym in positions.keys()}
            print(f"✅ Loaded {len(symbols)} portfolio positions from {config_path}")
            return symbols
    except Exception as e:
        print(f"⚠️  Error loading config file: {e}")
        print("   No portfolio positions to fetch.")
        return default_symbols

SYMBOLS = load_symbols_config()

# Get project root (parent of src/ directory when moved, or current dir if not moved)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "src" else SCRIPT_DIR
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "market_data")
os.makedirs(DATA_DIR, exist_ok=True)

# Automatically create CSV paths from SYMBOLS
def clean_name(sym: str) -> str:
    return sym.replace("^", "").upper()

# Automatically create CSV paths from SYMBOLS
CSV_PATHS = {sym.replace("^", ""): os.path.join(DATA_DIR, f"{sym.replace('^','')}.csv") for sym in SYMBOLS}

LOG_TIME_FMT = "%Y-%m-%d %H:%M:%S"


def log(msg: str):
    now = datetime.now().strftime(LOG_TIME_FMT)
    print(f"[{now}] {msg}", flush=True)


def fetch_history(ticker: str, start_date: str = None, max_retries: int = 3, sleep_s: int = 2) -> pd.DataFrame:
    """
    Fetch daily history for a ticker. Retries on transient errors.

    Args:
        ticker: Stock symbol to fetch
        start_date: If provided, fetch from this date onwards (format: 'YYYY-MM-DD')
                   If None, fetch all historical data
        max_retries: Number of retry attempts
        sleep_s: Base sleep seconds between retries
    """
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            # Fetch incrementally if start_date provided, otherwise get all history
            if start_date:
                # Check if start_date is in the future (don't try to fetch future dates)
                start_dt = pd.Timestamp(start_date)
                today = pd.Timestamp.today().normalize()
                if start_dt > today:
                    # No new data available yet (trying to fetch future dates)
                    return pd.DataFrame()

                df = yf.download(
                    ticker, start=start_date, interval="1d",
                    auto_adjust=False, progress=False, group_by="column"
                )
            else:
                df = yf.download(
                    ticker, period="max", interval="1d",
                    auto_adjust=False, progress=False, group_by="column"
                )

            # If empty DataFrame returned, it's not necessarily an error (might be no new data)
            if df.empty:
                return pd.DataFrame()

            if not isinstance(df.index, pd.DatetimeIndex):
                raise ValueError("Invalid DataFrame returned (not DatetimeIndex)")

            # ✅ FLATTEN MultiIndex columns from yfinance (drops the ticker level)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Keep only expected columns in correct order
            df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].copy()
            df.index.name = "Date"
            return df
        except Exception as e:
            last_exc = e
            error_msg = str(e).lower()
            # If it's a "start date after end date" error, it means no new data available
            if "start date cannot be after end date" in error_msg or "no price data found" in error_msg:
                log(f"No new data available for {ticker} (start_date={start_date})")
                return pd.DataFrame()
            log(f"Attempt {attempt} for {ticker} failed: {e}")
            if attempt < max_retries:
                time.sleep(sleep_s * attempt)

    # If all retries failed, raise error
    raise RuntimeError(f"Failed to fetch {ticker} after {max_retries} retries") from last_exc


def send_email(subject: str, body: str):
    """Optional: send email summary. Configure via environment variables."""
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    to_addr = os.getenv("SMTP_TO")

    if not all([host, user, password, to_addr]):
        return  # Not configured

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_addr], msg.as_string())
    except (smtplib.SMTPException, socket.error) as e:
        log(f"Email failed: {e}")


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce price/volume columns to numeric to sanitize legacy CSV rows."""
    for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def main():
    summaries = []
    any_success = False

    for sym_key, ticker in SYMBOLS.items():
        try:
            path = CSV_PATHS[sym_key]

            # Check if CSV exists and get the last date
            start_date = None
            old = pd.DataFrame()

            if os.path.exists(path):
                try:
                    old = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
                    if not old.empty:
                        # Get the last date in the existing CSV
                        last_date = old.index[-1]
                        # Fetch from the day after the last date (to avoid duplicates)
                        start_date = (last_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                        log(f"CSV exists for {sym_key}. Fetching incrementally from {start_date}...")
                    else:
                        log(f"CSV exists but empty for {sym_key}. Fetching all history...")
                except Exception as e:
                    log(f"Warning reading existing CSV for {sym_key}: {e}; fetching all history.")
                    old = pd.DataFrame()
            else:
                log(f"No CSV found for {sym_key}. Fetching all history...")

            # Fetch history (incremental if start_date is set, otherwise all)
            df = fetch_history(ticker, start_date=start_date)

            # If no new data, skip
            if df.empty:
                log(f"No new data for {sym_key}. CSV is up to date.")
                if not old.empty:
                    last_row_old = old.iloc[-1]
                    last_date_old = old.index[-1].date()
                    summaries.append(f"{sym_key}: {last_date_old}  AdjClose={float(last_row_old['Adj Close']):.2f}  Close={float(last_row_old['Close']):.2f} (no new data)")
                    any_success = True
                continue

            # Keep last ~15 years (keeps CSVs small but current)
            cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(years=15)
            df = df[df.index >= cutoff]

            # --- summary values taken from *fresh* data (avoid legacy CSV issues) ---
            last_row_new = df.iloc[-1]  # one row as a Series (scalar fields)
            last_date_new = df.index[-1].date()
            adj_close_val = float(last_row_new["Adj Close"])
            close_val     = float(last_row_new["Close"])

            # Combine old and new data, de-dup by date, sort
            combined = pd.concat([old, df]).sort_index(ascending=False)
            combined = combined[~combined.index.duplicated(keep="first")]

            # Sanitize numeric types and drop any bogus rows
            combined = coerce_numeric(combined)
            combined = combined.dropna(subset=["Open", "High", "Low", "Close", "Adj Close"])

            # Round prices to 2 decimals (leave Volume as-is)
            combined = combined.round({
                "Open": 2, "High": 2, "Low": 2, "Close": 2, "Adj Close": 2
            })

            # Save CSV
            combined.reset_index().to_csv(path, index=False)

            # Use fresh df values for the summary line (guaranteed scalars)
            summaries.append(f"{sym_key}: {last_date_new}  AdjClose={adj_close_val:.2f}  Close={close_val:.2f}")
            log(f"Saved {sym_key} -> {path}")
            any_success = True

        except Exception as e:
            log(f"ERROR for {sym_key}: {e}")

    # Optional email summary
    if summaries:
        subject = f"Daily Market Update: {datetime.now().strftime('%Y-%m-%d')}"
        body = "\n".join(summaries)
        send_email(subject, body)

    # Exit 0 if at least one symbol succeeded, so CI can still commit
    if any_success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
