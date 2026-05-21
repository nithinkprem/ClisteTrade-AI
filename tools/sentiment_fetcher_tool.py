import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load env variables
load_dotenv()

def fetch_sentiment_data(ticker: str, start_date: str = "", end_date: str = "") -> List[Dict[str, Any]]:
    """
    Fetches financial news articles for a given ticker.
    First tries to use NewsAPI if NEWSAPI_API_KEY is defined in environment variables.
    If the key is missing or the request fails, falls back to a realistic mock news generator.
    
    Args:
        ticker (str): The asset symbol (e.g., 'AAPL', 'BTC-USD').
        start_date (str, optional): Start date string (YYYY-MM-DD). Defaults to 7 days ago.
        end_date (str, optional): End date string (YYYY-MM-DD). Defaults to today.
        
    Returns:
        List[Dict[str, Any]]: List of article dictionaries with title, description, source, and publishedAt keys.
    """
    api_key = os.getenv("NEWSAPI_API_KEY")
    ticker_clean = ticker.strip().upper()
    
    # Calculate default dates if not provided
    today = datetime.now()
    if not end_date:
        end_date = today.strftime("%Y-%m-%d")
    if not start_date:
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        
    if api_key:
        print(f"Attempting to fetch real news for {ticker_clean} using NewsAPI...")
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": ticker_clean,
            "from": start_date,
            "to": end_date,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": api_key,
            "pageSize": 10
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                if articles:
                    return [
                        {
                            "title": art.get("title", ""),
                            "description": art.get("description", "") or art.get("content", "") or "",
                            "source": art.get("source", {}).get("name", "Unknown Source"),
                            "publishedAt": art.get("publishedAt", "")[:10]
                        }
                        for art in articles
                    ]
            print(f"NewsAPI returned status {response.status_code} or no articles. Falling back to mock news...")
        except Exception as e:
            print(f"Error fetching news from NewsAPI: {e}. Falling back to mock news...")
            
    # Mock news fallback
    print(f"Using mock news generator for {ticker_clean}...")
    return get_mock_news(ticker_clean)

def get_mock_news(ticker: str) -> List[Dict[str, Any]]:
    """
    Generates high-quality mock news articles tailored to specific tickers.
    """
    date_today = datetime.now().strftime("%Y-%m-%d")
    date_yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    date_2days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    date_3days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    
    # Predefined mock databases
    mock_db = {
        "AAPL": [
            {
                "title": "Apple Unveils New AI Integration and Chip Upgrades for Next-Gen iPhones",
                "description": "Tech giant Apple Inc. announced a series of upgrades focused on locally running LLMs, boosting analyst expectations for the upcoming product cycle.",
                "source": "Bloomberg",
                "publishedAt": date_today
            },
            {
                "title": "Apple's Services Revenue Hits Record High, Offsetting Slight Hardware Slowdown",
                "description": "Apple reports stronger-than-expected App Store and subscription revenues, confirming solid diversified growth and investor confidence.",
                "source": "Wall Street Journal",
                "publishedAt": date_yesterday
            },
            {
                "title": "Antitrust Regulators Heighten Scrutiny on Apple's App Store Policies",
                "description": "New regulatory hurdles in Europe could pressure Apple's ecosystem margins, warning of minor headwinds for services expansion.",
                "source": "Reuters",
                "publishedAt": date_2days_ago
            },
            {
                "title": "Supplier Reports Indicate Strong Initial Orders for New Apple Devices",
                "description": "Supply chain partners in Asia report steady production orders, indicating robust global consumer demand heading into the next quarter.",
                "source": "MarketWatch",
                "publishedAt": date_3days_ago
            }
        ],
        "TSLA": [
            {
                "title": "Tesla Announces Record Vehicle Deliveries for Q1, Beating Market Consensus",
                "description": "Tesla Inc. surprised analysts by delivering more vehicles than forecasted, led by strong sales in China and efficiency gains at Giga Berlin.",
                "source": "Electrek",
                "publishedAt": date_today
            },
            {
                "title": "Tesla Rolls Out Full Self-Driving Beta to All Eligible US Subscribers",
                "description": "Tesla pushes the latest version of its autonomous driving assistant software, promising fewer interventions and showcasing technical maturity.",
                "source": "Bloomberg",
                "publishedAt": date_yesterday
            },
            {
                "title": "Competition Intensifies as Rivals Launch Lower-Priced EVs",
                "description": "Tesla faces growing pricing pressure in the mid-range EV market as Asian manufacturers flood European and local markets with cheaper alternatives.",
                "source": "Reuters",
                "publishedAt": date_2days_ago
            },
            {
                "title": "CEO Outlines Tesla's Next-Generation Low-Cost Platform Timeline",
                "description": "Elon Musk hints at a faster-than-expected release date for the highly anticipated $25,000 electric vehicle to capture mass markets.",
                "source": "CNBC",
                "publishedAt": date_3days_ago
            }
        ],
        "BTC-USD": [
            {
                "title": "Bitcoin Surges Past Major Resistance as Institutional Inflows Accelerate",
                "description": "Bitcoin continues its upward trajectory, powered by heavy trading volume in spot ETFs and growing macro-hedging narratives among institutions.",
                "source": "CoinDesk",
                "publishedAt": date_today
            },
            {
                "title": "SEC Approves Additional Cryptocurrency Derivative Products",
                "description": "Regulators greenlight options trading on BTC ETFs, adding options liquidity that analysts say will mature market structure and reduce volatility.",
                "source": "Bloomberg",
                "publishedAt": date_yesterday
            },
            {
                "title": "Crypto Miners Face Margin Squeeze After Difficulty Adjustment",
                "description": "Recent changes in mining difficulty and energy costs squeeze smaller operations, but larger public miners continue expanding capacity.",
                "source": "Cointelegraph",
                "publishedAt": date_2days_ago
            },
            {
                "title": "Macroeconomic Worries Fuel Safe-Haven Play Into Digital Gold",
                "description": "Concerns over currency devaluation and high sovereign debt levels drive retail and institutional buyers toward decentralised alternative assets.",
                "source": "Forbes",
                "publishedAt": date_3days_ago
            }
        ],
        "DEFAULT": [
            {
                "title": f"Market Analysis: What's Driving Price Action in {ticker}?",
                "description": f"Analysts debate the medium-term prospects for {ticker} as volume spikes and technical charts approach key multi-month resistance levels.",
                "source": "Financial Times",
                "publishedAt": date_today
            },
            {
                "title": f"Regulatory and Macro Shifts Keep Pressure on {ticker} Sector",
                "description": f"Ongoing central bank rate decisions and regional trade developments create mixed trading signals for assets like {ticker}.",
                "source": "Reuters",
                "publishedAt": date_yesterday
            },
            {
                "title": f"Earnings and Corporate Data Beat Expectations for {ticker} Ecosystem",
                "description": f"Companies associated with {ticker} show strong balance sheet resilience, prompting upward adjustments in target valuations.",
                "source": "CNBC",
                "publishedAt": date_2days_ago
            }
        ]
    }
    
    # Try to find a matching ticker or fall back to DEFAULT
    return mock_db.get(ticker, mock_db["DEFAULT"])

if __name__ == "__main__":
    # Test news fetcher
    print("Testing fetch_sentiment_data...")
    aapl_news = fetch_sentiment_data("AAPL")
    print(f"Fetched {len(aapl_news)} articles for AAPL:")
    for art in aapl_news:
        print(f"- {art['title']} ({art['source']} - {art['publishedAt']})")
