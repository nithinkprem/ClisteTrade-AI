from crewai import Agent, Task
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_technical_agent() -> Agent:
    """
    Creates and returns the Technical Analyst Agent.
    """
    # Use the model name specified in .env, default to gpt-4o-mini
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    return Agent(
        role="Senior Technical Analyst",
        goal="Deconstruct technical indicators and price trends to formulate a clear, actionable technical market bias.",
        backstory=(
            "You are a veteran Wall Street Senior Technical Analyst with 15+ years of experience "
            "analyzing equities, forex, and cryptocurrency markets. You specialize in moving average crossover "
            "strategies, momentum oscillators (RSI), trend strength validation, and MACD divergence analysis. "
            "You are disciplined, precise, and base your conclusions strictly on technical data and indicators."
        ),
        verbose=True,
        allow_delegation=False,
        llm=model_name
    )

def create_technical_task(agent: Agent) -> Task:
    """
    Creates and returns the Technical Analysis Task.
    """
    return Task(
        description=(
            "Review and analyze the following structured market state data for {ticker}:\n\n"
            "{market_state_json}\n\n"
            "Your task is to write a detailed technical analysis report. In your report, cover:\n"
            "1. **Trend Analysis**: Evaluate the current trend (Uptrend/Downtrend/Sideways) based on the latest Close vs EMA20/EMA50 relationship.\n"
            "2. **Momentum & Strength**: Analyze the RSI and MACD status (crossovers, historical momentum) and what they imply about buyers vs sellers.\n"
            "3. **Technical Bias & Confidence**: Formulate a technical bias (BULLISH, BEARISH, or NEUTRAL), list the supporting arguments, and justify the confidence level.\n\n"
            "Your analysis must be grounded in the provided indicator values. Do not make up prices or dates."
        ),
        expected_output=(
            "A structured markdown report starting with a summary box of the technical bias and confidence, "
            "followed by detailed analysis sections for Trend, Momentum, and supporting arguments."
        ),
        agent=agent
    )

if __name__ == "__main__":
    # Quick CLI test for the Technical Agent
    from crewai import Crew
    import json
    
    print("Testing Technical Agent initialization and execution...")
    
    # Mock input data
    mock_market_state = {
        "ticker_data": {
            "latest_close": 302.25,
            "ema20": 287.83,
            "ema50": 276.67,
            "rsi": 74.54,
            "macd": 9.42,
            "macd_signal": 8.45,
            "macd_hist": 0.97
        },
        "market_state": {
            "trend": "Strong Uptrend",
            "momentum_rsi": "Overbought",
            "momentum_macd": "Bullish",
            "volatility": "Medium",
            "bullish_bearish_score": 80,
            "confidence": 0.74
        }
    }
    
    agent = create_technical_agent()
    task = create_technical_task(agent)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff(inputs={
        "ticker": "AAPL",
        "market_state_json": json.dumps(mock_market_state, indent=2)
    })
    
    print("\n--- TEST RESULT ---")
    print(result)
