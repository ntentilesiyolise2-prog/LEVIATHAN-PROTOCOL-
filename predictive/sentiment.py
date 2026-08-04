# leviathan/predictive/sentiment.py
import feedparser
import re
from typing import Dict, Any, List
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from loguru import logger

class PredictiveSentiment:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.feeds = ["http://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC", "http://feeds.reuters.com/reuters/businessNews", "http://feeds.marketwatch.com/marketwatch/marketpulse"]
    def analyze(self, symbol: str) -> Dict[str, Any]:
        headlines = self._fetch_news(symbol)
        if not headlines: return {'score': 0.0, 'label': 'NEUTRAL', 'count': 0}
        scores = [self.analyzer.polarity_scores(h)['compound'] for h in headlines]
        avg = sum(scores)/len(scores) if scores else 0
        label = "POSITIVE" if avg > 0.05 else "NEGATIVE" if avg < -0.05 else "NEUTRAL"
        return {'score': round(avg,3), 'label': label, 'count': len(headlines)}
    def _fetch_news(self, symbol: str) -> List[str]:
        headlines = []
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    title = entry.get('title', '')
                    if re.search(r'\b' + re.escape(symbol.split('=')[0]) + r'\b', title, re.IGNORECASE):
                        headlines.append(title)
                if headlines: break
            except Exception as e: logger.warning(f"RSS feed failed: {e}")
        return headlines
