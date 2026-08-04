# leviathan/nexus/conductor.py
import numpy as np
from typing import List, Dict, Any
import pandas as pd
from loguru import logger

class MetaNexus:
    def __init__(self):
        self.weights = {}
        self.confidence_bayes = {}
        self.history = []

    def update_weights(self, performance: Dict[str, float]):
        scores = np.array(list(performance.values()))
        if np.sum(scores) == 0: return
        exp_scores = np.exp(scores - np.max(scores))
        softmax = exp_scores / np.sum(exp_scores)
        for i, name in enumerate(performance.keys()):
            self.weights[name] = softmax[i]

    def combine(self, votes: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not votes:
            return {'direction': 'WAIT', 'confidence': 0, 'rationale': 'No votes', 'votes': []}
        buy_score = 0.0; sell_score = 0.0; total_weight = 0.0; rationale_parts = []
        for v in votes:
            source = v['source']; weight = self.weights.get(source, 0.1); conf = v['confidence'] / 100.0; total_weight += weight
            if v['direction'] == 'BUY':
                buy_score += weight * conf
                rationale_parts.append(f"{source} (BUY, {v['confidence']:.0f}%)")
            elif v['direction'] == 'SELL':
                sell_score += weight * conf
                rationale_parts.append(f"{source} (SELL, {v['confidence']:.0f}%)")
            else:
                rationale_parts.append(f"{source} (WAIT)")
        if total_weight == 0:
            return {'direction': 'WAIT', 'confidence': 0, 'rationale': 'No weight', 'votes': votes}
        buy_score /= total_weight; sell_score /= total_weight
        direction = 'BUY' if buy_score > sell_score else 'SELL' if sell_score > buy_score else 'WAIT'
        raw_conf = max(buy_score, sell_score) if direction != 'WAIT' else 0
        alpha = self.confidence_bayes.get(direction, {}).get('alpha', 1) if direction != 'WAIT' else 1
        beta = self.confidence_bayes.get(direction, {}).get('beta', 1) if direction != 'WAIT' else 1
        bayes_conf = (alpha + raw_conf * (alpha + beta)) / (alpha + beta + 1)
        confidence = min(98, max(5, int(bayes_conf * 100))) if direction != 'WAIT' else 0
        rationale = f"{direction} because " + "; ".join(rationale_parts[:5]) if direction != 'WAIT' else "No consensus."
        self.history.append({'timestamp': pd.Timestamp.utcnow().isoformat(), 'votes': votes, 'decision': direction, 'confidence': confidence, 'rationale': rationale})
        return {'direction': direction, 'confidence': confidence, 'rationale': rationale, 'votes': votes, 'buy_score': round(buy_score*100,1), 'sell_score': round(sell_score*100,1)}

    def update_bayesian(self, direction: str, outcome: bool):
        if direction not in self.confidence_bayes:
            self.confidence_bayes[direction] = {'alpha': 1, 'beta': 1}
        if outcome: self.confidence_bayes[direction]['alpha'] += 1
        else: self.confidence_bayes[direction]['beta'] += 1
