import argparse
import json
import sys
import os
from typing import List

# Import flow
from workflows.crew_workflow import run_trading_intelligence_flow
 
def main():
    parser = argparse.ArgumentParser(description="AI Multi-Agent Trading Intelligence CLI System")
    parser.add_argument(
        "--ticker", 
        type=str, 
        default="AAPL", 
        help="The asset symbol (e.g. AAPL, TSLA, BTC-USD)"
    )
    parser.add_argument(
        "--period", 
        type=str, 
        default="60d", 
        help="History period to fetch (e.g. 30d, 60d, 1y)"
    )
    parser.add_argument(
        "--interval", 
        type=str, 
        default="1d", 
        help="Data bar interval (e.g. 1h, 1d)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="", 
        help="Path to save the JSON output file"
    )
    
    args = parser.parse_args()
    
    try:
        results = run_trading_intelligence_flow(
            ticker=args.ticker,
            period=args.period,
            interval=args.interval
        )
        
        # Format decision printed outputs
        decision = results.get("final_decision", {})
        decision_val = decision.get("decision", "UNKNOWN")
        confidence_val = decision.get("confidence", 0)
        reasons = decision.get("key_reasons", [])
        
        print("\n" + "="*50)
        print(f"TRADING DECISION FOR {args.ticker.upper()}")
        print("="*50)
        print(f"DECISION  : {decision_val}")
        print(f"CONFIDENCE: {confidence_val}%")
        print("\nKey Supporting Reasons:")
        for idx, reason in enumerate(reasons):
            print(f"  {idx+1}. {reason}")
            
        print("\nSummaries:")
        print(f"  Technical: {decision.get('technical_summary', '')}")
        print(f"  Sentiment: {decision.get('sentiment_summary', '')}")
        print(f"  Risk     : {decision.get('risk_summary', '')}")
        print("="*50 + "\n")
        
        # Save output if path is specified
        if args.output:
            output_dir = os.path.dirname(os.path.abspath(args.output))
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"Detailed workflow execution logs saved to: {args.output}")
            
    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
