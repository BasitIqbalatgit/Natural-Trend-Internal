import pandas as pd

# Sample criteria for risk scoring
RISK_KEYWORDS = {
    'lawsuit': 3,
    'fraud': 5,
    'scandal': 4,
    'regulation': 2,
    'negative': 1
}

def calculate_risk_score(search_results):
    # Example scoring based on keywords found in results
    score = 0
    for result in search_results:
        for keyword, weight in RISK_KEYWORDS.items():
            if keyword.lower() in result.get('Text', '').lower():
                score += weight

    # Simple risk classification based on the score
    if score >= 10:
        risk_level = "High"
    elif score >= 5:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return f"{risk_level} (Score: {score})"
