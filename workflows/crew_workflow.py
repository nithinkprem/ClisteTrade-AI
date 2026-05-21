import json
from typing import Dict, Any
from crewai import Crew

# Import tools
from tools.market_data_tool import fetch_market_data
from tools.indicator_tool import compute_indicators
from tools.market_state_engine import generate_market_state
from tools.sentiment_fetcher_tool import fetch_sentiment_data
from tools.sentiment_compressor_tool import compress_sentiment

# Import agents and tasks
from agents.technical_agent import create_technical_agent, create_technical_task
from agents.sentiment_agent import create_sentiment_agent, create_sentiment_task
from agents.risk_agent import create_risk_agent, create_risk_task
from agents.decision_agent import create_decision_agent, create_decision_task

def run_trading_intelligence_flow(ticker: str, period: str = "60d", interval: str = "1d") -> Dict[str, Any]:
    """
    Orchestrates the entire data-fetching, tool-calculating, and CrewAI multi-agent workflow.
    
    Args:
        ticker (str): The asset symbol (e.g. 'AAPL', 'BTC-USD').
        period (str): Lookback period.
        interval (str): Time interval.
        
    Returns:
        Dict[str, Any]: A dictionary containing raw & structured outputs from all agents and tools.
    """
    ticker_clean = ticker.strip().upper()
    print(f"\n================ STARTING WORKFLOW FOR {ticker_clean} ================")
    
    # 1. Fetch market data & compute indicators (Phase 1)
    df = fetch_market_data(ticker_clean, period=period, interval=interval)
    df_ind = compute_indicators(df)
    market_state = generate_market_state(df_ind)
    
    # 2. Fetch news sentiment & compress it (Phase 3)
    news = fetch_sentiment_data(ticker_clean)
    sentiment_summary = compress_sentiment(news, ticker_clean)
    
    # 3. Instantiate CrewAI agents (Phases 2-5)
    tech_agent = create_technical_agent()
    sent_agent = create_sentiment_agent()
    risk_agent = create_risk_agent()
    decision_agent = create_decision_agent()
    
    # 4. Instantiate tasks with proper contexts (Phase 6)
    tech_task = create_technical_task(tech_agent)
    sent_task = create_sentiment_task(sent_agent)
    
    risk_task = create_risk_task(risk_agent)
    # Feed technical and sentiment reports as context for risk assessment
    risk_task.context = [tech_task, sent_task]
    
    decision_task = create_decision_task(decision_agent)
    # Feed technical, sentiment, and risk outputs as context for final decision
    decision_task.context = [tech_task, sent_task, risk_task]
    
    # 5. Build the Crew
    crew = Crew(
        agents=[tech_agent, sent_agent, risk_agent, decision_agent],
        tasks=[tech_task, sent_task, risk_task, decision_task],
        verbose=True
    )
    
    # 6. Kickoff execution
    inputs = {
        "ticker": ticker_clean,
        "market_state_json": json.dumps(market_state, indent=2),
        "market_state_details": json.dumps(market_state["market_state"], indent=2),
        "sentiment_summary_json": json.dumps(sentiment_summary, indent=2),
        "technical_findings": "", # placeholder filled by context
        "sentiment_findings": "", # placeholder filled by context
        "risk_findings": ""        # placeholder filled by context
    }
    
    print("Launching CrewAI agents workflow...")
    crew.kickoff(inputs=inputs)
    
    # 7. Collect results
    # Task output raw and pydantic format checks
    tech_report = tech_task.output.raw
    sent_report = sent_task.output.raw
    
    # Check output pydantic validation results
    risk_data = None
    if risk_task.output.pydantic:
        risk_data = risk_task.output.pydantic.model_dump()
    else:
        try:
            risk_data = json.loads(risk_task.output.raw)
        except:
            risk_data = {"raw_output": risk_task.output.raw}
            
    decision_data = None
    if decision_task.output.pydantic:
        decision_data = decision_task.output.pydantic.model_dump()
    else:
        try:
            decision_data = json.loads(decision_task.output.raw)
        except:
            decision_data = {"raw_output": decision_task.output.raw}
            
    # Combine results
    results = {
        "ticker": ticker_clean,
        "market_state": market_state,
        "sentiment_summary": sentiment_summary,
        "tech_report": tech_report,
        "sent_report": sent_report,
        "risk_assessment": risk_data,
        "final_decision": decision_data
    }
    
    print(f"================ WORKFLOW FOR {ticker_clean} COMPLETED ================\n")
    return results

if __name__ == "__main__":
    # Test flow execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("Testing the end-to-end workflow on TSLA...")
    res = run_trading_intelligence_flow("TSLA", period="60d", interval="1d")
    print("\n--- FINAL RUN DECISION ---")
    print(json.dumps(res["final_decision"], indent=2))
