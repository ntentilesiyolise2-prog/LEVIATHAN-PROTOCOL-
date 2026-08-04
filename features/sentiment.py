# leviathan/features/sentiment.py
from typing import Dict, Any

class SentimentAnalyzer:
    def compute(self, symbol: str) -> Dict[str, Any]:
        return {"sentiment_vader_positive": 0.5, "sentiment_vader_negative": 0.3, "sentiment_vader_neutral": 0.2, "sentiment_compound": 0.0, "sentiment_label": "NEUTRAL", "sentiment_news_count": 0}
