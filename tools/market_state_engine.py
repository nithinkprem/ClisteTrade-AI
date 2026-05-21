import pandas as pd
import numpy as np
import json
from typing import Dict, Any

def generate_market_state(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyzes an indicator-enriched DataFrame and generates a structured JSON market summary.
    
    Args:
        df (pd.DataFrame): DataFrame with columns Close, EMA20, EMA50, RSI, MACD, MACD_signal, MACD_hist.
        
    Returns:
        Dict[str, Any]: Dictionary representing the market state.
    """
    if df is None or df.empty:
        raise ValueError("DataFrame cannot be empty or None")
        
    required_cols = ['Close', 'EMA20', 'EMA50', 'RSI', 'MACD', 'MACD_signal', 'MACD_hist']
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Required indicator column '{col}' is missing")
            
    # Get the latest data point
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    close_val = float(latest['Close'])
    ema20_val = float(latest['EMA20'])
    ema50_val = float(latest['EMA50'])
    rsi_val = float(latest['RSI'])
    macd_val = float(latest['MACD'])
    macd_sig = float(latest['MACD_signal'])
    macd_hist = float(latest['MACD_hist'])
    
    # 1. Trend analysis
    if close_val > ema20_val > ema50_val:
        trend = "Strong Uptrend"
    elif close_val > ema50_val and close_val > ema20_val:
        trend = "Uptrend"
    elif close_val < ema20_val < ema50_val:
        trend = "Strong Downtrend"
    elif close_val < ema50_val and close_val < ema20_val:
        trend = "Downtrend"
    else:
        trend = "Sideways / Transitional"
        
    # 2. Momentum analysis
    rsi_status = "Neutral"
    if rsi_val > 70:
        rsi_status = "Overbought"
    elif rsi_val < 30:
        rsi_status = "Oversold"
    elif rsi_val > 50:
        rsi_status = "Bullish"
    elif rsi_val < 50:
        rsi_status = "Bearish"
        
    macd_status = "Neutral"
    if macd_val > macd_sig:
        macd_status = "Bullish Crossover" if (prev['MACD'] <= prev['MACD_signal'] if len(df) > 1 else False) else "Bullish"
    elif macd_val < macd_sig:
        macd_status = "Bearish Crossover" if (prev['MACD'] >= prev['MACD_signal'] if len(df) > 1 else False) else "Bearish"
        
    # 3. Volatility analysis (Coefficient of variation of Close over last 14 days)
    lookback = min(14, len(df))
    close_window = df['Close'].iloc[-lookback:]
    vol_coeff = float(close_window.std() / close_window.mean())
    
    if vol_coeff > 0.03:
        volatility = "High"
    elif vol_coeff > 0.01:
        volatility = "Medium"
    else:
        volatility = "Low"
        
    # 4. Bullish / Bearish Score (0 to 100)
    # Start neutral at 50
    score = 50
    
    # Trend contribution (max +/- 25)
    if "Strong Uptrend" in trend:
        score += 25
    elif "Uptrend" in trend:
        score += 15
    elif "Strong Downtrend" in trend:
        score -= 25
    elif "Downtrend" in trend:
        score -= 15
        
    # MACD contribution (max +/- 15)
    if "Bullish Crossover" in macd_status:
        score += 15
    elif "Bullish" in macd_status:
        score += 10
    elif "Bearish Crossover" in macd_status:
        score -= 15
    elif "Bearish" in macd_status:
        score -= 10
        
    # RSI contribution (max +/- 15)
    if rsi_status == "Oversold":
        score += 15  # Reversal indicator
    elif rsi_status == "Overbought":
        score -= 15  # Reversal indicator
    elif rsi_status == "Bullish":
        score += 10
    elif rsi_status == "Bearish":
        score -= 10
        
    # Price relationship to EMA20 and EMA50 (max +/- 10)
    if close_val > ema20_val:
        score += 5
    else:
        score -= 5
    if close_val > ema50_val:
        score += 5
    else:
        score -= 5
        
    # Cap score between 0 and 100
    score = int(max(0, min(100, score)))
    
    # 5. Confidence Score (0.0 to 1.0)
    # Confidence is higher when indicators align (i.e. score is very high or very low)
    # and lower when they conflict (score is near 50)
    score_deviation = abs(score - 50)  # ranges 0 to 50
    base_confidence = 0.5 + (score_deviation / 50.0) * 0.4  # ranges 0.5 to 0.9
    
    # Adjust confidence slightly down if volatility is extremely high
    if volatility == "High":
        base_confidence -= 0.05
    elif volatility == "Low":
        base_confidence += 0.05
        
    confidence = float(max(0.3, min(0.95, base_confidence)))
    
    state = {
        "ticker_data": {
            "latest_close": round(close_val, 4),
            "ema20": round(ema20_val, 4),
            "ema50": round(ema50_val, 4),
            "rsi": round(rsi_val, 2),
            "macd": round(macd_val, 4),
            "macd_signal": round(macd_sig, 4),
            "macd_hist": round(macd_hist, 4)
        },
        "market_state": {
            "trend": trend,
            "momentum_rsi": rsi_status,
            "momentum_macd": macd_status,
            "volatility": volatility,
            "bullish_bearish_score": score,
            "confidence": round(confidence, 2)
        }
    }
    
    return state

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.market_data_tool import fetch_market_data
    from tools.indicator_tool import compute_indicators
    
    try:
        df = fetch_market_data("AAPL", period="60d", interval="1d")
        df_ind = compute_indicators(df)
        state = generate_market_state(df_ind)
        print("Market State Engine output:")
        print(json.dumps(state, indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
