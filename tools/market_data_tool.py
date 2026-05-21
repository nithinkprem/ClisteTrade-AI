import pandas as pd
import yfinance as yf
from typing import Optional

def fetch_market_data(ticker: str, period: str = "60d", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical market data (OHLCV) using yfinance.
    
    Args:
        ticker (str): The symbol of the asset (e.g., 'AAPL', 'BTC-USD', 'EURUSD=X').
        period (str): The lookback period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', 'max', '60d').
        interval (str): The bar interval (e.g., '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo').
        
    Returns:
        pd.DataFrame: DataFrame containing Date (index), Open, High, Low, Close, Volume.
    """
    print(f"Fetching market data for {ticker} (period={period}, interval={interval})...")
    try:
        # Standardize ticker names
        ticker_cleaned = ticker.strip().upper()
        
        # Download data
        ticker_obj = yf.Ticker(ticker_cleaned)
        df = ticker_obj.history(period=period, interval=interval)
        
        if df.empty:
            raise ValueError(f"No data returned for ticker {ticker_cleaned} with period={period} and interval={interval}")
            
        # Ensure standard OHLCV columns exist and are named correctly
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in df.columns:
                # If case mismatches, try to find it case-insensitively
                found = False
                for actual_col in df.columns:
                    if actual_col.lower() == col.lower():
                        df[col] = df[actual_col]
                        found = True
                        break
                if not found:
                    raise KeyError(f"Required column '{col}' is missing from fetched data.")
        
        # Select only standard columns
        df = df[required_cols].copy()
        
        # Clean index: convert timezone-aware index to naive if timezone exists
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
            
        return df
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        raise e

if __name__ == "__main__":
    # Test fetch_market_data
    try:
        test_df = fetch_market_data("AAPL", period="10d", interval="1d")
        print("Data fetched successfully!")
        print(test_df.tail())
    except Exception as ex:
        print(f"Test failed: {ex}")
