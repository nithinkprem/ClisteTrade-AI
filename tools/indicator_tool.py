import pandas as pd
import numpy as np

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes EMA20, EMA50, RSI (14), and MACD (12, 26, 9) on the input DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame with at least 'Close' column.
        
    Returns:
        pd.DataFrame: Modified DataFrame with indicators added.
    """
    if df is None or df.empty:
        raise ValueError("Cannot compute indicators on empty or None DataFrame")
        
    if 'Close' not in df.columns:
        raise KeyError("DataFrame must contain a 'Close' column")
        
    df_indicators = df.copy()
    
    # 1. EMA 20 & EMA 50
    df_indicators['EMA20'] = df_indicators['Close'].ewm(span=20, adjust=False).mean()
    df_indicators['EMA50'] = df_indicators['Close'].ewm(span=50, adjust=False).mean()
    
    # 2. RSI (14)
    delta = df_indicators['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Wilders EMA formula for RSI
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    
    # Handle division by zero
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df_indicators['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. MACD (12, 26, 9)
    ema12 = df_indicators['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df_indicators['Close'].ewm(span=26, adjust=False).mean()
    df_indicators['MACD'] = ema12 - ema26
    df_indicators['MACD_signal'] = df_indicators['MACD'].ewm(span=9, adjust=False).mean()
    df_indicators['MACD_hist'] = df_indicators['MACD'] - df_indicators['MACD_signal']
    
    return df_indicators

if __name__ == "__main__":
    # Test indicator computation
    import sys
    import os
    # Add parent directory to path to import market_data_tool
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.market_data_tool import fetch_market_data
    
    try:
        df = fetch_market_data("AAPL", period="60d", interval="1d")
        df_ind = compute_indicators(df)
        print("Indicators calculated successfully!")
        print(df_ind[['Close', 'EMA20', 'EMA50', 'RSI', 'MACD', 'MACD_signal', 'MACD_hist']].tail())
    except Exception as e:
        print(f"Test failed: {e}")
