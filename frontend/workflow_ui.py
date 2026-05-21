import streamlit as st
import streamlit.components.v1 as components

def render_workflow_status(active_step: str) -> str:
    """
    Renders a premium, animated HTML/CSS progress stepper for the agentic workflow.
    
    Args:
        active_step (str): The currently active step. Options:
                           'idle', 'market_data', 'sentiment_data', 'technical_agent', 
                           'sentiment_agent', 'risk_agent', 'decision_agent', 'completed'
                           
    Returns:
        str: The raw HTML/CSS string of the stepper to be rendered in the main application.
    """
    # Define the workflow steps
    steps = [
        {"id": "market_data", "label": "Market & Indicator Data"},
        {"id": "sentiment_data", "label": "News & Sentiment Fetch"},
        {"id": "technical_agent", "label": "Technical Agent Analysis"},
        {"id": "sentiment_agent", "label": "Sentiment Agent Analysis"},
        {"id": "risk_agent", "label": "Risk Assessment Agent"},
        {"id": "decision_agent", "label": "CIO Decision Agent"}
    ]
    
    # Map step index
    step_ids = [s["id"] for s in steps]
    active_idx = step_ids.index(active_step) if active_step in step_ids else (-1 if active_step == 'idle' else len(steps))
    
    # CSS for premium glassmorphic horizontal stepper
    html_content = """
    <style>
        .stepper-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0 25px 0;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            overflow-x: auto;
        }
        .step-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            position: relative;
            min-width: 100px;
            text-align: center;
        }
        .step-circle {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: #1e293b;
            border: 2px solid #475569;
            color: #94a3b8;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.4s ease;
            z-index: 2;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .step-label {
            margin-top: 10px;
            font-size: 11px;
            color: #94a3b8;
            font-weight: 500;
            max-width: 110px;
            transition: all 0.4s ease;
        }
        /* Completed state */
        .step-item.completed .step-circle {
            background: #10b981;
            border-color: #10b981;
            color: #ffffff;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        }
        .step-item.completed .step-label {
            color: #10b981;
            font-weight: 600;
        }
        /* Active state with pulsing glow */
        .step-item.active .step-circle {
            background: #3b82f6;
            border-color: #3b82f6;
            color: #ffffff;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
            animation: pulse-blue 2s infinite alternate;
        }
        .step-item.active .step-label {
            color: #60a5fa;
            font-weight: 600;
        }
        /* Connecting Lines */
        .step-connector {
            position: absolute;
            top: 19px;
            left: 50%;
            width: 100%;
            height: 2px;
            background: #475569;
            z-index: 1;
            transition: background 0.4s ease;
        }
        .step-item.completed .step-connector {
            background: #10b981;
        }
        .step-item.active .step-connector {
            background: linear-gradient(to right, #10b981, #3b82f6);
        }
        .step-item:last-child .step-connector {
            display: none;
        }
        
        @keyframes pulse-blue {
            0% {
                box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
            }
            100% {
                box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
            }
        }
    </style>
    <div class="stepper-container">
    """
    
    for idx, step in enumerate(steps):
        status_class = ""
        circle_content = str(idx + 1)
        
        if idx < active_idx:
            status_class = "completed"
            circle_content = "&#10003;"  # Checkmark symbol
        elif idx == active_idx:
            status_class = "active"
        else:
            status_class = "pending"
            
        html_content += f"""
        <div class="step-item {status_class}">
            <div class="step-circle">{circle_content}</div>
            <div class="step-label">{step["label"]}</div>
            <div class="step-connector"></div>
        </div>
        """
        
    # Add special block for when execution is complete
    if active_step == 'completed':
        html_content = html_content.replace('class="step-item completed" style="display: none;"', 'class="step-item completed"')
        
    html_content += "</div>"
    
    return html_content