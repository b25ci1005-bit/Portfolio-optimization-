"""
Quantitative Strategies for Paper Trading & Backtesting.
Includes:
1. Cross-Sectional Momentum Strategy (Top Quintile Momentum)
2. Dual Moving Average Trend Strategy (Fast/Slow SMA Crossover)
3. Mean Reversion RSI Strategy (Oversold Blue-Chip Rebound)
4. UserStrategyTemplate (Plug-and-play custom user code template)
"""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy

class CrossSectionalMomentumStrategy(BaseStrategy):
    id = "cross_sectional_momentum"
    name = "60-Day Cross-Sectional Momentum"
    description = "Ranks NSE assets by 60-day momentum and allocates capital to the top performing quintile."
    category = "Momentum"

    def __init__(self, lookback_period: int = 60, top_k: int = 4):
        self.lookback = lookback_period
        self.top_k = top_k

    def generate_weights(
        self,
        prices: pd.DataFrame,
        current_positions: Optional[Dict[str, float]] = None,
        cash_buffer: float = 0.02,
        **kwargs
    ) -> Dict[str, float]:
        if len(prices) < self.lookback:
            return self.clean_and_normalize({col: 1.0 / len(prices.columns) for col in prices.columns}, cash_buffer)

        # Calculate momentum: price return over lookback period
        start_p = prices.iloc[-self.lookback]
        end_p = prices.iloc[-1]
        momentum_scores = (end_p / start_p) - 1.0

        # Select top K performing assets
        top_assets = momentum_scores.sort_values(ascending=False).head(self.top_k)

        # Equal weight among top performers
        raw_weights = {sym: 1.0 / self.top_k for sym in top_assets.index}
        for sym in prices.columns:
            if sym not in raw_weights:
                raw_weights[sym] = 0.0

        return self.clean_and_normalize(raw_weights, cash_buffer)


class MovingAverageTrendStrategy(BaseStrategy):
    id = "sma_trend_crossover"
    name = "Dual Moving Average Trend Following"
    description = "Allocates to stocks where 20-day SMA is above 50-day SMA with positive trend slope."
    category = "Trend Following"

    def __init__(self, fast_window: int = 20, slow_window: int = 50):
        self.fast = fast_window
        self.slow = slow_window

    def generate_weights(
        self,
        prices: pd.DataFrame,
        current_positions: Optional[Dict[str, float]] = None,
        cash_buffer: float = 0.02,
        **kwargs
    ) -> Dict[str, float]:
        if len(prices) < self.slow:
            return self.clean_and_normalize({col: 1.0 / len(prices.columns) for col in prices.columns}, cash_buffer)

        sma_fast = prices.rolling(window=self.fast).mean().iloc[-1]
        sma_slow = prices.rolling(window=self.slow).mean().iloc[-1]

        # Bullish signal: fast SMA > slow SMA
        bullish_mask = sma_fast > sma_slow
        bullish_symbols = bullish_mask[bullish_mask].index.tolist()

        if len(bullish_symbols) == 0:
            # All in cash if market is in broad downtrend
            return {"CASH": 1.0}

        # Weight inversely proportional to 30-day volatility
        vols = prices[bullish_symbols].pct_change().rolling(30).std().iloc[-1]
        inv_vols = 1.0 / np.maximum(vols, 1e-4)
        weights_series = inv_vols / inv_vols.sum()

        raw_weights = {s: float(weights_series[s]) for s in bullish_symbols}
        for s in prices.columns:
            if s not in raw_weights:
                raw_weights[s] = 0.0

        return self.clean_and_normalize(raw_weights, cash_buffer)


class MeanReversionRSIStrategy(BaseStrategy):
    id = "rsi_mean_reversion"
    name = "RSI 14 Mean-Reversion"
    description = "Identifies oversold blue-chip stocks (RSI < 40) positioned for statistical rebound."
    category = "Mean Reversion"

    def __init__(self, rsi_period: int = 14, oversold_threshold: float = 40.0):
        self.rsi_period = rsi_period
        self.threshold = oversold_threshold

    def _compute_rsi(self, series: pd.Series) -> float:
        delta = series.diff().dropna()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        avg_gain = gains.tail(self.rsi_period).mean()
        avg_loss = losses.tail(self.rsi_period).mean()
        if avg_loss <= 1e-7:
            return 100.0
        rs = avg_gain / avg_loss
        return float(100.0 - (100.0 / (1.0 + rs)))

    def generate_weights(
        self,
        prices: pd.DataFrame,
        current_positions: Optional[Dict[str, float]] = None,
        cash_buffer: float = 0.02,
        **kwargs
    ) -> Dict[str, float]:
        if len(prices) < self.rsi_period + 5:
            return self.clean_and_normalize({col: 1.0 / len(prices.columns) for col in prices.columns}, cash_buffer)

        rsi_values = {}
        for col in prices.columns:
            rsi_values[col] = self._compute_rsi(prices[col])

        # Find oversold assets
        oversold = {sym: (self.threshold - rsi) for sym, rsi in rsi_values.items() if rsi < self.threshold}

        if not oversold:
            # If no assets oversold, allocate equally to lowest RSI assets
            lowest_3 = sorted(rsi_values.items(), key=lambda x: x[1])[:3]
            raw_weights = {s[0]: 1.0 / len(lowest_3) for s in lowest_3}
        else:
            total_gap = sum(oversold.values())
            raw_weights = {sym: gap / total_gap for sym, gap in oversold.items()}

        for sym in prices.columns:
            if sym not in raw_weights:
                raw_weights[sym] = 0.0

        return self.clean_and_normalize(raw_weights, cash_buffer)


class MyCustomStrategy(BaseStrategy):
    """
    USER STRATEGY TEMPLATE:
    Add your custom quantitative formula, technical indicators, or ML logic here!
    """
    id = "my_custom_strategy"
    name = "User Custom Strategy (Template)"
    description = "Custom quantitative logic. Edit backend/app/strategies/custom_strategies.py to customize."
    category = "Custom"

    def generate_weights(
        self,
        prices: pd.DataFrame,
        current_positions: Optional[Dict[str, float]] = None,
        cash_buffer: float = 0.02,
        **kwargs
    ) -> Dict[str, float]:
        """
        WRITE YOUR STRATEGY LOGIC HERE:
        `prices`: pandas DataFrame containing historical close prices for NSE symbols.
        `current_positions`: current shares held in paper portfolio.
        
        Example below: Blend 30-day return momentum with low volatility
        """
        returns_30d = (prices.iloc[-1] / prices.iloc[-30]) - 1.0
        vol_30d = prices.pct_change().tail(30).std()
        
        # Risk-adjusted score = Return / Volatility
        scores = returns_30d / np.maximum(vol_30d, 1e-4)
        
        # Select positive score assets
        positive_scores = scores.clip(lower=0)
        total_score = positive_scores.sum()
        
        if total_score > 1e-5:
            raw_weights = (positive_scores / total_score).to_dict()
        else:
            raw_weights = {col: 1.0 / len(prices.columns) for col in prices.columns}

        return self.clean_and_normalize(raw_weights, cash_buffer)
