# leviathan/learning/rl.py
import random
import numpy as np
from collections import deque
from typing import Dict, Any

class DQNAgent:
    def __init__(self, state_size: int = 20, action_size: int = 3, learning_rate: float = 0.001, gamma: float = 0.95):
        self.state_size = state_size; self.action_size = action_size; self.learning_rate = learning_rate; self.gamma = gamma
        self.epsilon = 1.0; self.epsilon_min = 0.01; self.epsilon_decay = 0.995; self.memory = deque(maxlen=2000)
        self.weights = np.random.randn(state_size, action_size) * 0.1
    def get_state(self, features: Dict[str, Any]) -> np.ndarray:
        keys = ['rsi_14','adx','atr_pct','ema_20','ema_50','ema_200','macd','bb_position','volume_ratio','poc_distance','vix','dxy','gold','spx','risk_on','pattern_hs','pattern_triangle','divergence_bullish_rsi','divergence_bearish_rsi','sentiment_compound']
        state = []
        for k in keys:
            val = features.get(k, 0)
            if isinstance(val, bool): val = 1.0 if val else 0.0
            elif isinstance(val, str): val = 0.0
            state.append(float(val))
        if len(state) < self.state_size: state += [0.0] * (self.state_size - len(state))
        return np.array(state[:self.state_size])
    def act(self, state: np.ndarray) -> int:
        if np.random.rand() <= self.epsilon: return random.randrange(self.action_size)
        q_values = np.dot(state, self.weights)
        return np.argmax(q_values)
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    def replay(self, batch_size: int = 32):
        if len(self.memory) < batch_size: return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            q_target = reward
            if not done: q_target = reward + self.gamma * np.max(np.dot(next_state, self.weights))
            prediction = np.dot(state, self.weights)[action]
            error = q_target - prediction
            self.weights[:, action] += self.learning_rate * error * state
        if self.epsilon > self.epsilon_min: self.epsilon *= self.epsilon_decay
