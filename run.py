# run.py
import sys
import argparse
from logutil import setup_logger
from core import get_candles

logger = setup_logger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--tf", type=int, default=60)
    parser.add_argument("--no-telegram", action="store_true")
    args = parser.parse_args()

    logger.info(f"Starting run for {args.symbol} TF={args.tf}")

    try:
        df, src, y, td, tf = get_candles(args.symbol, args.tf)
        if df is None or df.empty:
            logger.error(f"No data returned for {args.symbol}")
            print(f"❌ No data for {args.symbol}")
        else:
            logger.info(f"Fetched {len(df)} rows from {src}")
            print(f"✅ Got data: {args.symbol}, rows={len(df)}")
    except Exception as e:
        logger.exception(f"Failed to fetch data for {args.symbol}")
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    main()
