import streamlit as st
import pandas as pd
import json
import os
import sys
from dotenv import load_dotenv
from crewai import Crew

# Ensure the project root is in the Python search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Set page config with premium settings
st.set_page_config(
    page_title="ClisteTrade-AI | Trading Intelligence System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Apply Inter font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Force dark background on the entire app viewport and all layout containers */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainViewContainer"] {
        background-color: #0b1329 !important;
        color: #f8fafc !important;
    }

    /* Eliminate any remaining default margins/paddings at the top of the main container */
    [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0rem !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    section[data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox ul {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] .stSlider div[data-baseweb="slider"] {
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border-color: rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        color: #ffffff !important;
    }
    
    /* Card design */
    .premium-card {
        background: rgba(30, 41, 59, 0.35);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
    }
    
    /* Signal Badges */
    .badge-buy {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1.5px solid #10b981;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 24px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.25);
        text-align: center;
        letter-spacing: 1px;
    }
    .badge-sell {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1.5px solid #ef4444;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 24px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.25);
        text-align: center;
        letter-spacing: 1px;
    }
    .badge-hold {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1.5px solid #f59e0b;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 24px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.25);
        text-align: center;
        letter-spacing: 1px;
    }
    
    /* Mini metrics */
    .metric-container {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
    }
    .metric-box {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 12px 18px;
        flex: 1;
        margin: 0 8px;
        text-align: center;
    }
    .metric-label {
        font-size: 11px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-val {
        font-size: 18px;
        font-weight: 600;
        color: #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)

# Import backend modules
from tools.market_data_tool import fetch_market_data
from tools.indicator_tool import compute_indicators
from tools.market_state_engine import generate_market_state
from tools.sentiment_fetcher_tool import fetch_sentiment_data
from tools.sentiment_compressor_tool import compress_sentiment
from agents.technical_agent import create_technical_agent, create_technical_task
from agents.sentiment_agent import create_sentiment_agent, create_sentiment_task
from agents.risk_agent import create_risk_agent, create_risk_task
from agents.decision_agent import create_decision_agent, create_decision_task
from frontend.charts import create_financial_chart
from frontend.workflow_ui import render_workflow_status
import streamlit.components.v1 as components

# Header Title Block
st.markdown("""
<div style='margin-bottom: 25px;'>
    <h1 style='color: #ffffff; margin-bottom: 4px; font-weight: 700; font-size: 32px;'>
        ⚡ ClisteTrade-AI <span style='color: #3b82f6;'>Trading Intelligence Desk</span>
    </h1>
    <p style='color: #64748b; font-size: 14px; margin-top: 0;'>
        Multi-Agent Generative Decision Pipeline & Real-Time Analytics
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if 'workflow_state' not in st.session_state:
    st.session_state.workflow_state = 'idle'
if 'results' not in st.session_state:
    st.session_state.results = None
if 'df_ind' not in st.session_state:
    st.session_state.df_ind = None
if 'news_articles' not in st.session_state:
    st.session_state.news_articles = []

# ================= SIDEBAR =================
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px;'>
    <h3 style='color: #f1f5f9; margin-bottom: 4px;'>Controls</h3>
</div>
""", unsafe_allow_html=True)

asset_type = st.sidebar.selectbox("Select Asset Class", ["Equities", "Cryptocurrency", "Forex"])

# Selection Lists based on type
if asset_type == "Equities":
    ticker_list = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "Custom Ticker"]
    ticker_selected = st.sidebar.selectbox("Select Ticker", ticker_list)
elif asset_type == "Cryptocurrency":
    ticker_list = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "Custom Ticker"]
    ticker_selected = st.sidebar.selectbox("Select Pair", ticker_list)
else: # Forex
    ticker_list = ["EURUSD=X", "GBPUSD=X", "JPY=X", "AUDUSD=X", "Custom Ticker"]
    ticker_selected = st.sidebar.selectbox("Select Pair", ticker_list)

# Handing Custom Ticker
if ticker_selected == "Custom Ticker":
    ticker = st.sidebar.text_input("Enter Ticker Code", value="AAPL").upper().strip()
else:
    ticker = ticker_selected

# Lookback period settings
lookback_period = st.sidebar.selectbox("Historical Lookback", ["30d", "60d", "90d", "180d", "1y"])
interval = "1d" # default

st.sidebar.markdown("---")
st.sidebar.markdown("<h4 style='color: #94a3b8; font-size: 13px; margin-bottom: 10px;'>Trading Parameters</h4>", unsafe_allow_html=True)

trading_style = st.sidebar.selectbox(
    "Trading Style", 
    ["Day Trading", "Swing Trading", "Position Trading", "Scalping"]
)

risk_tolerance = st.sidebar.select_slider(
    "Risk Tolerance Profile", 
    options=["Low", "Medium", "High"]
)

st.sidebar.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
analyze_btn = st.sidebar.button("⚡ ANALYZE ASSET", use_container_width=True, type="primary")

# ================= WORKFLOW RUN LOGIC =================
if analyze_btn:
    st.session_state.results = None
    st.session_state.df_ind = None
    st.session_state.news_articles = []
    
    # Check OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("Error: OPENAI_API_KEY is not defined in the environment or .env file.")
    else:
        # Step-by-step layout placeholder
        stepper_placeholder = st.empty()
        status_text = st.empty()
        
        try:
            # STEP 1: Fetching Market Data & Indicators
            st.session_state.workflow_state = 'market_data'
            with stepper_placeholder.container():
                stepper_html = render_workflow_status('market_data')
                components.html(stepper_html, height=120)
            status_text.info(f"Downloading historical data for {ticker} using yfinance and computing technical indicators...")
            
            df = fetch_market_data(ticker, period=lookback_period, interval=interval)
            df_ind = compute_indicators(df)
            market_state = generate_market_state(df_ind)
            
            st.session_state.df_ind = df_ind
            
            # STEP 2: Fetching news & sentiment compression
            st.session_state.workflow_state = 'sentiment_data'
            with stepper_placeholder.container():
                stepper_html = render_workflow_status('sentiment_data')
                components.html(stepper_html, height=120)
            status_text.info("Querying financial news portals and compiling sentiment indexes...")
            
            news = fetch_sentiment_data(ticker)
            st.session_state.news_articles = news
            sentiment_summary = compress_sentiment(news, ticker)
            
            # STEP 3: Technical Agent execution
            st.session_state.workflow_state = 'technical_agent'
            with stepper_placeholder.container():
                stepper_html = render_workflow_status('technical_agent')
                components.html(stepper_html, height=120)
            status_text.info("Senior Technical Analyst Agent is dissecting trend strength and momentum oscillator signals...")
            
            tech_agent = create_technical_agent()
            tech_task = create_technical_task(tech_agent)
            tech_crew = Crew(agents=[tech_agent], tasks=[tech_task], verbose=True)
            tech_result = tech_crew.kickoff(inputs={
                "ticker": ticker,
                "market_state_json": json.dumps(market_state, indent=2)
            })
            tech_report = tech_result.raw
            
            # STEP 4: Sentiment Agent execution
            st.session_state.workflow_state = 'sentiment_agent'
            with stepper_placeholder.container():
                stepper_html = render_workflow_status('sentiment_agent')
                components.html(stepper_html, height=120)
            status_text.info("Senior Sentiment and Macro Analyst Agent is reading news files and determining market psychology...")
            
            sent_agent = create_sentiment_agent()
            sent_task = create_sentiment_task(sent_agent)
            sent_crew = Crew(agents=[sent_agent], tasks=[sent_task], verbose=True)
            sent_result = sent_crew.kickoff(inputs={
                "ticker": ticker,
                "sentiment_summary_json": json.dumps(sentiment_summary, indent=2)
            })
            sent_report = sent_result.raw
            
            # STEP 5: Risk Agent execution
            st.session_state.workflow_state = 'risk_agent'
            with stepper_placeholder.container():
                stepper_html = render_workflow_status('risk_agent')
                components.html(stepper_html, height=120)
            status_text.info("Senior Risk Officer Agent is looking for signal conflicts, volatility traps, and exposure limits...")
            
            risk_agent = create_risk_agent()
            risk_task = create_risk_task(risk_agent)
            risk_crew = Crew(agents=[risk_agent], tasks=[risk_task], verbose=True)
            risk_result = risk_crew.kickoff(inputs={
                "ticker": ticker,
                "technical_findings": tech_report,
                "sentiment_findings": sent_report,
                "market_state_details": json.dumps(market_state["market_state"], indent=2)
            })
            
            risk_data = None
            if risk_result.pydantic:
                risk_data = risk_result.pydantic.model_dump()
            elif risk_task.output.pydantic:
                risk_data = risk_task.output.pydantic.model_dump()
            else:
                try:
                    parsed = json.loads(risk_task.output.raw)
                    if isinstance(parsed, dict) and "risk_score" in parsed:
                        risk_data = parsed
                    else:
                        risk_data = {"raw_output": risk_task.output.raw}
                except:
                    risk_data = {"raw_output": risk_task.output.raw}
                    st.warning("Risk output extraction failed; using raw text.")
                    
            # STEP 6: Decision Agent execution
            st.session_state.workflow_state = 'decision_agent'
            with stepper_placeholder.container():
                stepper_html = render_workflow_status('decision_agent')
                components.html(stepper_html, height=120)
            status_text.info("Chief Investment Officer Agent is synthesizing expert findings and issuing final decision order...")
            
            decision_agent = create_decision_agent()
            decision_task = create_decision_task(decision_agent)
            decision_crew = Crew(agents=[decision_agent], tasks=[decision_task], verbose=True)
            decision_result = decision_crew.kickoff(inputs={
                "ticker": ticker,
                "technical_findings": tech_report,
                "sentiment_findings": sent_report,
                "risk_findings": risk_task.output.raw
            })
            
            decision_data = None
            if decision_result.pydantic:
                decision_data = decision_result.pydantic.model_dump()
            elif decision_task.output.pydantic:
                decision_data = decision_task.output.pydantic.model_dump()
            else:
                try:
                    parsed = json.loads(decision_task.output.raw)
                    if isinstance(parsed, dict) and "decision" in parsed:
                        decision_data = parsed
                    else:
                        decision_data = {"raw_output": decision_task.output.raw}
                except:
                    decision_data = {"raw_output": decision_task.output.raw}
                    st.warning("Decision output extraction failed; check Agent Output Explorer tab for details.")
            
            # STEP 7: Completed
            st.session_state.workflow_state = 'completed'
            stepper_placeholder.empty()
            status_text.empty()
            
            st.session_state.results = {
                "ticker": ticker,
                "market_state": market_state,
                "sentiment_summary": sentiment_summary,
                "tech_report": tech_report,
                "sent_report": sent_report,
                "risk_assessment": risk_data,
                "final_decision": decision_data
            }
            
        except Exception as e:
            st.session_state.workflow_state = 'idle'
            status_text.empty()
            st.error(f"Execution Error: {e}")

# ================= RENDER INTERFACE =================
# If workflow is completed, render dashboards
if st.session_state.results is not None:
    res = st.session_state.results
    decision_info = res["final_decision"]
    risk_info = res["risk_assessment"]
    market_info = res["market_state"]
    sentiment_info = res["sentiment_summary"]
    
    # 1. Risk-based decision override
    decision_val = decision_info.get("decision", "HOLD").upper()
    confidence = decision_info.get("confidence", 50)
    risk_level = risk_info.get("risk_level", "MEDIUM").upper()
    if risk_level in ("HIGH", "CRITICAL"):
        decision_val = "SELL"
        confidence = min(confidence, 60)
    elif risk_level == "MEDIUM":
        decision_val = "HOLD"
        confidence = min(confidence, 50)
    else:  # LOW
        decision_val = "BUY"
        confidence = max(confidence, 60)
    
    st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
    
    col_dec, col_met = st.columns([1, 2])
    
    with col_dec:
        st.markdown("<p style='color:#94a3b8; font-size:12px; font-weight:600; text-transform:uppercase; margin-bottom:5px;'>Final Committee Decision</p>", unsafe_allow_html=True)
        if decision_val == "BUY":
            st.markdown(f"<div class='badge-buy'>{decision_val}</div>", unsafe_allow_html=True)
        elif decision_val == "SELL":
            st.markdown(f"<div class='badge-sell'>{decision_val}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='badge-hold'>{decision_val}</div>", unsafe_allow_html=True)
            
    with col_met:
        # Metric stats
        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-box'>
                <div class='metric-label'>Confidence</div>
                <div class='metric-val' style='color:#60a5fa;'>{confidence}%</div>
            </div>
            <div class='metric-box'>
                <div class='metric-label'>Risk Level</div>
                <div class='metric-val' style='color:{"#ef4444" if risk_info.get("risk_level") in ["HIGH","CRITICAL"] else "#10b981"};'>{risk_info.get("risk_level", "MEDIUM")}</div>
            </div>
            <div class='metric-box'>
                <div class='metric-label'>RSI Index</div>
                <div class='metric-val'>{market_info["ticker_data"]["rsi"]}</div>
            </div>
            <div class='metric-box'>
                <div class='metric-label'>Bull/Bear Score</div>
                <div class='metric-val'>{market_info["market_state"]["bullish_bearish_score"]}/100</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. Main charts area
    if st.session_state.df_ind is not None:
        fig = create_financial_chart(st.session_state.df_ind, res["ticker"])
        st.plotly_chart(fig, use_container_width=True)
        
    # 3. Agent Explorer Tabs
    st.markdown("### 🔍 Agent Output Explorer")
    st.markdown("""
    <style>
    div[data-baseweb="tab-list"] button {
        color: #10b981 !important;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    tab_dec, tab_tech, tab_sent, tab_risk = st.tabs([
        "🎯 Final Decision Logic", 
        "📈 Technical Analyst Report", 
        "📰 Sentiment Analyst Report", 
        "🛡️ Risk Assessment Details"
    ])
    
    with tab_dec:
        st.markdown("#### Decision Reasoning Summary")
        for reason in decision_info.get("key_reasons", []):
            st.markdown(f"- **{reason}**")
            
        st.markdown("---")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown("<div style='background:rgba(59,130,246,0.05); border:1px solid rgba(59,130,246,0.1); border-radius:8px; padding:15px;'>", unsafe_allow_html=True)
            st.markdown("##### Technical Outlook")
            st.write(decision_info.get("technical_summary", ""))
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_p2:
            st.markdown("<div style='background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.1); border-radius:8px; padding:15px;'>", unsafe_allow_html=True)
            st.markdown("##### Sentiment Outlook")
            st.write(decision_info.get("sentiment_summary", ""))
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_p3:
            st.markdown("<div style='background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.1); border-radius:8px; padding:15px;'>", unsafe_allow_html=True)
            st.markdown("##### Risk Strategy")
            st.write(decision_info.get("risk_summary", ""))
            st.markdown("</div>", unsafe_allow_html=True)
            
    with tab_tech:
        st.markdown(res["tech_report"])
        
    with tab_sent:
        st.markdown(res["sent_report"])
        st.markdown("---")
        st.markdown("#### Analysed News Stream")
        for art in st.session_state.news_articles:
            with st.chat_message("finance", avatar="📰"):
                st.markdown(f"**{art['title']}**")
                st.caption(f"Source: {art['source']} | Date: {art['publishedAt']}")
                st.write(art['description'])
                
    with tab_risk:
        col_r1, col_r2 = st.columns([1, 2])
        
        with col_r1:
            st.markdown("<div class='premium-card' style='margin-bottom:0;'>", unsafe_allow_html=True)
            st.markdown(f"### Risk Score: <span style='color:#ef4444;'>{risk_info.get('risk_score', 0)} / 100</span>", unsafe_allow_html=True)
            st.markdown(f"**Risk Level:** `{risk_info.get('risk_level', 'MEDIUM')}`")
            st.markdown(f"**Signal Conflict:** `{'YES' if risk_info.get('conflict_detected') else 'NO'}`")
            st.markdown(f"**Volatility Risk:** `{risk_info.get('volatility_risk', 'MEDIUM')}`")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_r2:
            st.markdown("##### Suitability Assessment")
            st.info(risk_info.get("trade_suitability", ""))
            
            st.markdown("##### Key Risks Identified")
            for kr in risk_info.get("key_risks", []):
                st.markdown(f"- ⚠️ {kr}")

else:
    # Landing View placeholder
    st.markdown("""
    <div style='text-align: center; padding: 80px 20px; background: rgba(30, 41, 59, 0.2); border-radius: 15px; border: 1px dashed rgba(255,255,255,0.08); margin-top: 30px;'>
        <h2 style='color:#64748b; margin-bottom: 8px;'>System Standing By</h2>
        <p style='color:#475569; max-width:500px; margin:0 auto; font-size:14px;'>
            Configure the parameters in the left side control panel and click 'Analyze Asset' to execute the multi-agent trading analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
