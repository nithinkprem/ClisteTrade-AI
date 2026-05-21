import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_financial_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    """
    Generates a premium, interactive Plotly chart with 3 subplots:
    1. Candlestick chart overlaid with EMA20 and EMA50.
    2. MACD (MACD, Signal, and Histogram).
    3. RSI with threshold lines at 30 and 70.
    
    All subplots share the X-axis for synchronized zooming and panning.
    
    Args:
        df (pd.DataFrame): DataFrame containing indicators (Date index, Open, High, Low, Close, EMA20, EMA50, RSI, MACD, MACD_signal, MACD_hist).
        ticker (str): The ticker symbol to display in the title.
        
    Returns:
        go.Figure: Plotly figure ready to be rendered in Streamlit.
    """
    # Create subplots
    fig = make_subplots(
        rows=3, 
        cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03, 
        subplot_titles=(f"{ticker} Price & EMAs", "MACD (12, 26, 9)", "RSI (14)"),
        row_width=[0.2, 0.2, 0.6]  # Bottom to top ratios
    )
    
    # ------------------ ROW 1: Candlesticks & EMAs ------------------
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="OHLC",
            increasing_line_color='#10b981',  # Emerald green
            decreasing_line_color='#ef4444',  # Crimson red
            increasing_fillcolor='#10b981',
            decreasing_fillcolor='#ef4444',
            opacity=0.95
        ),
        row=1, col=1
    )
    
    # EMA 20
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA20'],
            mode='lines',
            line=dict(color='#3b82f6', width=1.5),  # Cobalt blue
            name="EMA 20"
        ),
        row=1, col=1
    )
    
    # EMA 50
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['EMA50'],
            mode='lines',
            line=dict(color='#f59e0b', width=1.5),  # Amber orange
            name="EMA 50"
        ),
        row=1, col=1
    )
    
    # ------------------ ROW 2: MACD ------------------
    # MACD Line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            line=dict(color='#818cf8', width=1.5),  # Indigo
            name="MACD"
        ),
        row=2, col=1
    )
    
    # Signal Line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD_signal'],
            mode='lines',
            line=dict(color='#f472b6', width=1.5),  # Pink
            name="Signal"
        ),
        row=2, col=1
    )
    
    # Histogram (color code based on positive/negative)
    hist_colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['MACD_hist']]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['MACD_hist'],
            marker_color=hist_colors,
            name="Histogram",
            opacity=0.75
        ),
        row=2, col=1
    )
    
    # ------------------ ROW 3: RSI ------------------
    # RSI Line
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            line=dict(color='#a78bfa', width=1.8),  # Purple
            name="RSI"
        ),
        row=3, col=1
    )
    
    # RSI Overbought Line (70)
    fig.add_shape(
        type="line",
        x0=df.index[0],
        y0=70,
        x1=df.index[-1],
        y1=70,
        line=dict(color="#ef4444", width=1, dash="dash"),
        row=3, col=1
    )
    
    # RSI Oversold Line (30)
    fig.add_shape(
        type="line",
        x0=df.index[0],
        y0=30,
        x1=df.index[-1],
        y1=30,
        line=dict(color="#10b981", width=1, dash="dash"),
        row=3, col=1
    )
    
    # ------------------ STYLING ------------------
    # Apply a premium dark layout
    fig.update_layout(
        template="plotly_dark",
        height=750,
        margin=dict(l=50, r=20, t=50, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis_rangeslider_visible=False,  # Hide range slider to keep it neat
        hovermode="x unified",
        paper_bgcolor='rgba(15, 23, 42, 1)',  # Slate 900
        plot_bgcolor='rgba(15, 23, 42, 1)',   # Slate 900
    )
    
    # Refine axis settings and gridlines
    for i in [1, 2, 3]:
        fig.update_xaxes(
            showgrid=True,
            gridcolor='rgba(51, 65, 85, 0.4)',  # Slate 700 with opacity
            linecolor='rgba(71, 85, 105, 0.8)',
            row=i, col=1
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(51, 65, 85, 0.4)',
            linecolor='rgba(71, 85, 105, 0.8)',
            row=i, col=1
        )
        
    # Y-axis bounds for RSI
    fig.update_yaxes(range=[10, 90], row=3, col=1)
    
    return fig

if __name__ == "__main__":
    # Test chart generation script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.market_data_tool import fetch_market_data
    from tools.indicator_tool import compute_indicators
    
    df = fetch_market_data("AAPL", period="60d")
    df_ind = compute_indicators(df)
    fig = create_financial_chart(df_ind, "AAPL")
    print("Chart created successfully! Type is go.Figure:", isinstance(fig, go.Figure))
