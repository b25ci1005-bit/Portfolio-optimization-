"""
Base Strategy Interface for Quantitative Paper Trading & Backtesting.
All custom trading and allocation strategies inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

class BaseStrategy(ABC):
    """
    Abstract Base Class for all Quantitative Trading & Allocation Strategies.
    
    To implement a new strategy:
    1. Subclass BaseStrategy
    2. Provide a unique `id`, `name`, and `description`
    3. Implement `generate_weights(price_df, **kwargs)` returning a dict of {symbol: weight}
    """
    id: str = "base"
    name: str = "Base Strategy"
    description: str = "Abstract base strategy"
    category: str = "General"  # Momentum, Trend, Mean-Reversion, Optimization, Factor

    @abstractmethod
    def generate_weights(
        self,
        prices: pd.DataFrame,
        current_positions: Optional[Dict[str, float]] = None,
        cash_buffer: float = 0.02,
        **kwargs
    ) -> Dict[str, float]:
        """
        Calculates target allocation weights based on historical prices.
        
        Args:
            prices: DataFrame of historical adjusted close prices (index=dates, cols=symbols).
            current_positions: Dict of current shares held {symbol: shares}.
            cash_buffer: Fraction of portfolio to retain in cash (e.g. 0.02 = 2%).
            
        Returns:
            Dict mapping ticker symbol to target weight float (e.g. {"RELIANCE.NS": 0.20, "CASH": 0.02})
            where the sum of all weights equals 1.0.
        """
        pass

    def clean_and_normalize(self, raw_weights: Dict[str, float], cash_buffer: float = 0.02) -> Dict[str, float]:
        """Utility to ensure weights are non-negative, sum to 1.0, and respect cash buffer"""
        equity_target = 1.0 - cash_buffer
        filtered = {k: max(0.0, float(v)) for k, v in raw_weights.items() if k != "CASH"}
        total = sum(filtered.values())
        
        if total > 1e-7:
            normalized = {k: round((v / total) * equity_target, 4) for k, v in filtered.items()}
        else:
            n = len(raw_weights)
            normalized = {k: round(equity_target / n, 4) for k in raw_weights.keys() if k != "CASH"}
            
        normalized["CASH"] = round(1.0 - sum(normalized.values()), 4)
        return normalized
