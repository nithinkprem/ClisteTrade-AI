import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

def compress_sentiment(articles: List[Dict[str, Any]], ticker: str) -> Dict[str, Any]:
    """
    LLM-powered tool to summarize news articles, extract overall sentiment, 
    detect themes, and compress the semantic information into a structured JSON.
    
    Args:
        articles (List[Dict[str, Any]]): List of news articles with title, description, source.
        ticker (str): The asset symbol (e.g., 'AAPL').
        
    Returns:
        Dict[str, Any]: Structured sentiment summary.
    """
    if not articles:
        return {
            "sentiment_score": 0.0,
            "overall_sentiment": "Neutral",
            "detected_themes": ["No articles found"],
            "summary": "No news articles were available to analyze for this asset.",
            "confidence": 0.5
        }
        
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not defined in environment variables.")
        
    # Format articles for the prompt
    formatted_articles = ""
    for idx, art in enumerate(articles):
        formatted_articles += (
            f"Article #{idx+1}:\n"
            f"Title: {art.get('title')}\n"
            f"Source: {art.get('source')}\n"
            f"Published: {art.get('publishedAt')}\n"
            f"Description: {art.get('description')}\n"
            f"-----------------------------------------\n"
        )
        
    # Initialize client
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    system_prompt = (
        "You are an expert financial sentiment analysis engine. Your job is to process raw news headlines "
        "and summaries for a given ticker and compress them into a structured, clean JSON object. "
        "You must return ONLY the raw JSON string, without any markdown formatting or backticks."
    )
    
    user_prompt = f"""
Analyze the following news articles for {ticker.upper()}:

{formatted_articles}

Compress this information into a JSON object with the following keys:
- "sentiment_score": a float between -1.0 (extremely bearish) and +1.0 (extremely bullish)
- "overall_sentiment": "Bullish", "Bearish", or "Neutral"
- "detected_themes": a list of 2-4 strings representing the key topics or themes in the news
- "summary": a 2-3 sentence semantic compression summarizing the sentiment trends
- "confidence": a float between 0.0 and 1.0 indicating your confidence in this analysis

Do not include any markup, code blocks, or explanations outside the JSON block.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        raw_content = response.choices[0].message.content
        summary_dict = json.loads(raw_content)
        return summary_dict
        
    except Exception as e:
        print(f"Error during sentiment compression: {e}")
        # Return fallback values
        return {
            "sentiment_score": 0.0,
            "overall_sentiment": "Neutral",
            "detected_themes": ["Error in processing"],
            "summary": "An error occurred while generating the LLM news sentiment compression.",
            "confidence": 0.1
        }

if __name__ == "__main__":
    # Test sentiment compressor
    from tools.sentiment_fetcher_tool import fetch_sentiment_data
    
    print("Testing sentiment compressor...")
    articles = fetch_sentiment_data("AAPL")
    summary = compress_sentiment(articles, "AAPL")
    print("Structured sentiment summary:")
    print(json.dumps(summary, indent=2))
