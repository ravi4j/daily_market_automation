#!/usr/bin/env python3
"""
Fetch daily OHLCV data for TQQQ and the S&P 500 (^GSPC) and store/update CSVs.

Features:
- Writes/updates data/TQQQ.csv and data/SP500.csv
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

# --- Dependencies ---
try:
    import yfinance as yf
except ImportError:
    print("ERROR: Missing dependency 'yfinance'. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

# --- Config ---
SYMBOLS = {
    "TQQQ": "TQQQ",
    "SP500": "^GSPC",
    "AAPL": "AAPL",
    "UBER": "UBER",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
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


def fetch_history(ticker: str, max_retries: int = 3, sleep_s: int = 2) -> pd.DataFrame:
    """Fetch latest daily history for a ticker. Retries on transient errors."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            # group_by="column" returns a column-structured DataFrame (can still be MultiIndex)
            df = yf.download(
                ticker, period="max", interval="1d",
                auto_adjust=False, progress=False, group_by="column"
            )
            if not isinstance(df.index, pd.DatetimeIndex) or df.empty:
                raise ValueError("Empty or invalid DataFrame returned")

            # ✅ FLATTEN MultiIndex columns from yfinance (drops the ticker level)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Keep only expected columns in correct order
            df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].copy()
            df.index.name = "Date"
            return df
        except Exception as e:
            last_exc = e
            log(f"Attempt {attempt} for {ticker} failed: {e}")
            time.sleep(sleep_s * attempt)
    raise RuntimeError(f"Failed to fetch {ticker} after retries") from last_exc


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
            log(f"Fetching {sym_key} ({ticker}) ...")
            df = fetch_history(ticker)

            # Keep last ~15 years (keeps CSVs small but current)
            cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(years=15)
            df = df[df.index >= cutoff]

            # --- summary values taken from *fresh* data (avoid legacy CSV issues) ---
            last_row_new = df.iloc[-1]  # one row as a Series (scalar fields)
            last_date_new = df.index[-1].date()
            adj_close_val = float(last_row_new["Adj Close"])
            close_val     = float(last_row_new["Close"])

            path = CSV_PATHS[sym_key]

            # Load existing if present
            if os.path.exists(path):
                try:
                    old = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
                except Exception as e:
                    log(f"Warning reading existing CSV for {sym_key}: {e}; starting fresh.")
                    old = pd.DataFrame()
            else:
                old = pd.DataFrame()

            # Combine, de-dup by date, sort
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
