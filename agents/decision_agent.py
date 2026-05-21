from crewai import Agent, Task
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

# Load environment variables
load_dotenv()

# Define the structured output model for the Decision Agent
class TradingDecision(BaseModel):
    decision: str = Field(description="The final action choice: BUY, SELL, or HOLD")
    confidence: int = Field(description="Confidence percentage for this decision, from 0 to 100")
    key_reasons: List[str] = Field(description="List of 3 primary reasons backing this final decision")
    technical_summary: str = Field(description="A 1-2 sentence summary of the technical analysis context")
    sentiment_summary: str = Field(description="A 1-2 sentence summary of the news and macro sentiment context")
    risk_summary: str = Field(description="A 1-2 sentence summary of the risk assessment context")

def create_decision_agent() -> Agent:
    """
    Creates and returns the Decision Agent.
    """
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    return Agent(
        role="Chief Investment Officer (CIO)",
        goal="Synthesize technical, sentiment, and risk analysis reports to deliver a definitive BUY/SELL/HOLD decision.",
        backstory=(
            "You are the Chief Investment Officer of a multi-billion dollar quantitative trading desk. "
            "You are responsible for final trade approvals. You combine technical signals, fundamental news "
            "sentiment, and risk management parameters to make balanced, strategic investment decisions. "
            "You weigh evidence objectively and are equally comfortable issuing BUY, SELL, or HOLD "
            "depending on what the data supports. You reward strong confirmation across multiple signals."
        ),
        verbose=True,
        allow_delegation=False,
        llm=model_name
    )

def create_decision_task(agent: Agent) -> Task:
    """
    Creates and returns the Decision Task.
    """
    return Task(
        description=(
            "You are making the final trading decision for {ticker}.\n\n"
            "Evaluate the reports and outputs from the research specialists:\n\n"
            "=== TECHNICAL ANALYSIS ===\n"
            "{technical_findings}\n\n"
            "=== SENTIMENT & MACRO ===\n"
            "{sentiment_findings}\n\n"
            "=== RISK ASSESSMENT ===\n"
            "{risk_findings}\n\n"
            "Your task is to:\n"
            "1. Synthesize all perspectives (Technical, Sentiment, and Risk).\n"
            "2. Decide on the final action (BUY, SELL, or HOLD).\n"
            "   - BUY if technical and sentiment are aligned bullish and risks are manageable.\n"
            "   - SELL if technical and sentiment are aligned bearish or there is a clear deterioration.\n"
            "   - HOLD only when signals are mixed/conflicting or the risk/reward is unattractive.\n"
            "3. Specify your final confidence percentage and compile the summaries of the three pillars.\n\n"
            "Generate the final decision JSON strictly conforming to the TradingDecision schema."
        ),
        expected_output="A structured JSON object adhering to the TradingDecision schema containing decision, confidence, key_reasons, technical_summary, sentiment_summary, and risk_summary.",
        output_pydantic=TradingDecision,
        agent=agent
    )

if __name__ == "__main__":
    # Test the Decision Agent
    from crewai import Crew
    import json
    
    print("Testing Decision Agent initialization and execution...")
    
    mock_tech_findings = """
    - Bias: BULLISH
    - Confidence: 74%
    - Close is 302.25, in strong uptrend above EMA20 and EMA50. RSI is 74.54 (overbought), MACD is bullish.
    """
    
    mock_sent_findings = """
    - Bias: BULLISH
    - Confidence: 80%
    - Themes: AI upgrades, services growth. Regulatory antitrust issues in Europe are a minor headwind.
    """
    
    mock_risk_findings = """
    - Risk Score: 60 (Medium)
    - Volatility Risk: Medium
    - Conflict Detected: False
    - Risks: Overbought RSI, European antitrust pressure, broader macro headwinds.
    """
    
    agent = create_decision_agent()
    task = create_decision_task(agent)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff(inputs={
        "ticker": "AAPL",
        "technical_findings": mock_tech_findings,
        "sentiment_findings": mock_sent_findings,
        "risk_findings": mock_risk_findings
    })
    
    print("\n--- TEST RESULT ---")
    print(type(result))
    print(result)
