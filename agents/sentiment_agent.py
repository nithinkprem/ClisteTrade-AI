from crewai import Agent, Task
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sentiment_agent() -> Agent:
    """
    Creates and returns the Sentiment Analyst Agent.
    """
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    return Agent(
        role="Senior Sentiment and Macro Analyst",
        goal="Deconstruct news, market sentiment, and macroeconomic trends to formulate a clear, actionable sentiment market bias.",
        backstory=(
            "You are a global macro and sentiment strategist with 12+ years of experience "
            "tracking market psychology, news flows, and macroeconomic indicators. You study how "
            "narratives, headlines, geopolitical shifts, and sentiment indicators drive retail and "
            "institutional flow. You excel at reading between the lines of press releases and detecting shifts in consumer sentiment."
        ),
        verbose=True,
        allow_delegation=False,
        llm=model_name
    )

def create_sentiment_task(agent: Agent) -> Task:
    """
    Creates and returns the Sentiment Analysis Task.
    """
    return Task(
        description=(
            "Review and analyze the following compressed market news and sentiment data for {ticker}:\n\n"
            "{sentiment_summary_json}\n\n"
            "Your task is to write a detailed sentiment analysis report. In your report, cover:\n"
            "1. **Sentiment Trends**: Evaluate the overall news sentiment (Bullish/Bearish/Neutral) and the intensity indicated by the sentiment score.\n"
            "2. **Thematic Drivers**: Analyze the key topics or themes in the news and how they are impacting investor perception of {ticker}.\n"
            "3. **Macro/Psychological Impact**: Explain how these current news themes fit into the larger macroeconomic picture and overall market sentiment.\n"
            "4. **Sentiment Bias & Confidence**: State your final sentiment bias (BULLISH, BEARISH, or NEUTRAL), list the supporting arguments, and justify the confidence level.\n\n"
            "Base your reasoning strictly on the provided sentiment compression data. Do not make up events."
        ),
        expected_output=(
            "A structured markdown report starting with a summary box of the sentiment bias and confidence, "
            "followed by detailed analysis sections for Sentiment Trends, Thematic Drivers, and Macro/Psychological Impact."
        ),
        agent=agent
    )

if __name__ == "__main__":
    # Quick CLI test for the Sentiment Agent
    from crewai import Crew
    import json
    
    print("Testing Sentiment Agent initialization and execution...")
    
    # Mock sentiment compression output
    mock_sentiment_summary = {
        "sentiment_score": 0.65,
        "overall_sentiment": "Bullish",
        "detected_themes": [
            "AI upgrades on device",
            "Strong services growth",
            "Antitrust regulatory risk"
        ],
        "summary": "Apple's announcement of local LLM features and record services revenues have boosted analyst targets, though european antitrust challenges remain a minor headwind.",
        "confidence": 0.8
    }
    
    agent = create_sentiment_agent()
    task = create_sentiment_task(agent)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff(inputs={
        "ticker": "AAPL",
        "sentiment_summary_json": json.dumps(mock_sentiment_summary, indent=2)
    })
    
    print("\n--- TEST RESULT ---")
    print(result)
