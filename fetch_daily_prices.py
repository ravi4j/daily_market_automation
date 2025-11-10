#!/usr/bin/env python3
"""
Fetch daily OHLCV data for TQQQ and the S&P 500 (^GSPC) and store/update CSVs.
- Saves/updates data/TQQQ.csv and data/SP500.csv with Adjusted Close and other columns.
- Designed to be run daily via cron, Task Scheduler, or CI.
- Optional: email a brief summary if SMTP environment variables are provided.

Author: ChatGPT
"""
import os
import sys
import time
import smtplib
import socket
from email.mime.text import MIMEText
from datetime import datetime

import pandas as pd

# Try importing yfinance with a helpful error if missing
try:
    import yfinance as yf
except ImportError:
    print("ERROR: Missing dependency 'yfinance'. Run: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

SYMBOLS = {
    "TQQQ": "TQQQ",
    "SP500": "^GSPC",
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

CSV_PATHS = {
    "TQQQ": os.path.join(DATA_DIR, "TQQQ.csv"),
    "SP500": os.path.join(DATA_DIR, "SP500.csv"),
}

LOG_TIME_FMT = "%Y-%m-%d %H:%M:%S"

def log(msg: str):
    now = datetime.now().strftime(LOG_TIME_FMT)
    print(f"[{now}] {msg}", flush=True)

def fetch_history(ticker: str, max_retries: int = 3, sleep_s: int = 2) -> pd.DataFrame:
    """Fetch latest daily history for a ticker. Retries on transient errors."""
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            df = yf.download(ticker, period="max", interval="1d", auto_adjust=False, progress=False)
            # Normalize columns
            if not isinstance(df.index, pd.DatetimeIndex) or df.empty:
                raise ValueError("Empty or invalid DataFrame returned")
            df = df[["Open", "High", "Low", "Close", "Adj Close", "Volume"]].copy()
            # yfinance returns tz-naive dates; keep them as dates (no tz) for CSV stability
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

def main():
    summaries = []
    exit_code = 0
    for sym_key, ticker in SYMBOLS.items():
        try:
            log(f"Fetching {sym_key} ({ticker}) ...")
            df = fetch_history(ticker)
            # Keep only last 15 years for manageable size
            cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(years=15)
            df = df[df.index >= cutoff]

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

            combined = pd.concat([old, df]).sort_index()
            combined = combined[~combined.index.duplicated(keep="last")]

            combined.reset_index().to_csv(path, index=False)
            last_row = combined.iloc[-1]
            summaries.append(f"{sym_key}: {combined.index[-1].date()}  AdjClose={last_row['Adj Close']:.2f}  Close={last_row['Close']:.2f}")
            log(f"Saved {sym_key} -> {path}")
        except Exception as e:
            log(f"ERROR for {sym_key}: {e}")
            exit_code = 1

    # Optional email
    if summaries:
        subject = f"Daily Market Update: {datetime.now().strftime('%Y-%m-%d')}"
        body = "\n".join(summaries)
        send_email(subject, body)

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
