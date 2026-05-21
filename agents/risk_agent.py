from crewai import Agent, Task
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

# Load environment variables
load_dotenv()

# Define the structured output model for the Risk Agent
class RiskAssessment(BaseModel):
    risk_score: int = Field(description="Risk score from 0 to 100, where 100 represents maximum risk")
    risk_level: str = Field(description="Risk level classification: LOW, MEDIUM, HIGH, or CRITICAL")
    conflict_detected: bool = Field(description="True if there is a significant conflict between technical indicators and sentiment analysis")
    volatility_risk: str = Field(description="Assessment of volatility risk: LOW, MEDIUM, or HIGH")
    key_risks: List[str] = Field(description="List of top 2-4 key risk factors identified for the trade")
    trade_suitability: str = Field(description="A brief explanation of why the trade is suitable or unsuitable under these risk parameters")

def create_risk_agent() -> Agent:
    """
    Creates and returns the Risk Manager Agent.
    """
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    return Agent(
        role="Senior Risk Officer",
        goal="Objectively assess risk exposures, market volatility, and signal alignment to determine trade suitability.",
        backstory=(
            "You are a Senior Risk Officer with 15+ years of risk management experience at a major hedge fund. "
            "You specialize in volatility analysis, exposure management, and hedging strategies. "
            "You objectively weigh both upside and downside risks, rewarding well-supported setups "
            "while flagging genuine hazards. You avoid crying wolf and reserve HIGH/CRITICAL ratings "
            "for truly dangerous conditions."
        ),
        verbose=True,
        allow_delegation=False,
        llm=model_name
    )

def create_risk_task(agent: Agent) -> Task:
    """
    Creates and returns the Risk Assessment Task.
    """
    return Task(
        description=(
            "You are evaluating the risk profile for a potential trade in {ticker}.\n\n"
            "Review the findings from the Technical Analyst and the Sentiment Analyst:\n\n"
            "=== TECHNICAL ANALYSIS FINDINGS ===\n"
            "{technical_findings}\n\n"
            "=== SENTIMENT ANALYSIS FINDINGS ===\n"
            "{sentiment_findings}\n\n"
            "=== MARKET STATE ENGINE DETAILS ===\n"
            "{market_state_details}\n\n"
            "Your task is to analyze these findings and identify:\n"
            "1. Any conflicts between Technical analysis (trends/indicators) and News Sentiment (macro/headlines).\n"
            "2. Volatility risk based on recent price movements and macro environment.\n"
            "3. Trade suitability: determine if a position is safe, given the confidence and alignment of signals.\n\n"
            "Generate a structured risk assessment report. You must output the result strictly according to the Pydantic schema."
        ),
        expected_output="A structured JSON object adhering to the RiskAssessment schema containing risk_score, risk_level, conflict_detected, volatility_risk, key_risks, and trade_suitability.",
        output_pydantic=RiskAssessment,
        agent=agent
    )

if __name__ == "__main__":
    # Test the Risk Agent
    from crewai import Crew
    import json
    
    print("Testing Risk Agent initialization and execution...")
    
    mock_tech_findings = """
    # Technical Analysis Report: AAPL
    - Bias: BULLISH
    - Confidence: 74%
    - Trend: Strong Uptrend (Close is 302.25, above EMA20 and EMA50).
    - Momentum: RSI is 74.54 (Overbought), MACD is positive (9.42) and above Signal (8.45).
    """
    
    mock_sentiment_findings = """
    # Sentiment Analysis Report: AAPL
    - Bias: BULLISH
    - Confidence: 80%
    - Themes: AI upgrades on device, record services revenues.
    - Notes: European antitrust risk is a minor headwind.
    """
    
    mock_market_state = {
        "market_state": {
            "trend": "Strong Uptrend",
            "volatility": "Medium",
            "bullish_bearish_score": 80,
            "confidence": 0.74
        }
    }
    
    agent = create_risk_agent()
    task = create_risk_task(agent)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff(inputs={
        "ticker": "AAPL",
        "technical_findings": mock_tech_findings,
        "sentiment_findings": mock_sentiment_findings,
        "market_state_details": json.dumps(mock_market_state, indent=2)
    })
    
    print("\n--- TEST RESULT ---")
    print(type(result))
    print(result)
