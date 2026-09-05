"""
Portfolio State and Valuation Helper.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd

class PortfolioState:
    def __init__(self, cash: float, positions: Dict[str, float], initial_capital: float = 1_000_000.0):
        self.cash = float(cash)
        self.positions = positions  # symbol -> shares count
        self.initial_capital = float(initial_capital)

    def calculate_nav(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Compute total NAV, invested equity value, cash, and current weights"""
        invested_value = 0.0
        position_values = {}

        for sym, shares in self.positions.items():
            price = current_prices.get(sym, 0.0)
            val = shares * price
            position_values[sym] = val
            invested_value += val

        total_nav = self.cash + invested_value
        pnl = total_nav - self.initial_capital
        pnl_pct = (pnl / self.initial_capital) * 100.0 if self.initial_capital > 0 else 0.0

        weights = {}
        if total_nav > 0:
            for sym, val in position_values.items():
                weights[sym] = round(val / total_nav, 5)
            weights["CASH"] = round(self.cash / total_nav, 5)
        else:
            weights = {"CASH": 1.0}

        return {
            "nav": round(total_nav, 2),
            "cash": round(self.cash, 2),
            "invested_value": round(invested_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "weights": weights,
            "position_values": position_values
        }
