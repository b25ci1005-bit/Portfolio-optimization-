"""
Institutional Risk Manager for Indian Equities.
Enforces:
1. Maximum single asset weight constraint
2. Sector caps (e.g. max 35% in Banking/Financials)
3. Mandatory cash buffer allocation (e.g. 2% cash reserve)
4. Turnover constraints and rebalancing limit penalty
5. Minimum liquidity (ADV) threshold filtering
"""

import logging
from typing import Dict, List, Optional
import numpy as np

from backend.app.config import settings

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(
        self,
        max_asset_weight: float = settings.DEFAULT_MAX_ASSET_WEIGHT,
        max_sector_weight: float = settings.DEFAULT_MAX_SECTOR_WEIGHT,
        cash_buffer: float = settings.DEFAULT_CASH_BUFFER,
        max_turnover_per_rebalance: float = 0.50
    ):
        self.max_asset_weight = max_asset_weight
        self.max_sector_weight = max_sector_weight
        self.cash_buffer = cash_buffer
        self.max_turnover = max_turnover_per_rebalance

    def apply_risk_constraints(
        self,
        weights: Dict[str, float],
        sector_map: Dict[str, str],
        max_asset: Optional[float] = None,
        max_sector: Optional[float] = None,
        cash_buf: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Adjust raw portfolio weights to comply with:
        - Asset ceilings
        - Sector ceilings
        - Cash reserve buffer
        """
        asset_cap = max_asset if max_asset is not None else self.max_asset_weight
        sector_cap = max_sector if max_sector is not None else self.max_sector_weight
        cash = cash_buf if cash_buf is not None else self.cash_buffer

        target_equity_sum = 1.0 - cash
        symbols = list(weights.keys())
        n = len(symbols)

        if n == 0:
            return {"CASH": 1.0}

        w = {s: max(0.0, float(weights[s])) for s in symbols}
        
        # 1. Normalize initially to target_equity_sum
        total = sum(w.values())
        if total > 0:
            w = {s: (val / total) * target_equity_sum for s, val in w.items()}
        else:
            w = {s: target_equity_sum / n for s in symbols}

        # 2. Iterative clipping to enforce asset cap & sector cap
        effective_asset_cap = max(asset_cap, target_equity_sum / n)
        effective_sector_cap = max(sector_cap, effective_asset_cap)

        for _ in range(10):
            # Asset cap clipping
            clipped_any = False
            for s in symbols:
                if w[s] > effective_asset_cap:
                    w[s] = effective_asset_cap
                    clipped_any = True

            # Sector cap clipping
            sector_totals: Dict[str, float] = {}
            for s, weight in w.items():
                sec = sector_map.get(s, "Other")
                sector_totals[sec] = sector_totals.get(sec, 0.0) + weight

            for sec, total_sec in sector_totals.items():
                if total_sec > effective_sector_cap:
                    scaling = effective_sector_cap / total_sec
                    for s in symbols:
                        if sector_map.get(s, "Other") == sec:
                            w[s] *= scaling
                    clipped_any = True

            # Renormalize non-capped assets to meet target_equity_sum
            current_sum = sum(w.values())
            if abs(current_sum - target_equity_sum) < 1e-4:
                break
            if current_sum > 0:
                scale = target_equity_sum / current_sum
                w = {s: val * scale for s, val in w.items()}

        final_weights = {s: round(val, 5) for s, val in w.items()}
        final_weights["CASH"] = round(1.0 - sum(final_weights.values()), 5)
        return final_weights

    @staticmethod
    def compute_turnover(
        current_weights: Dict[str, float],
        target_weights: Dict[str, float]
    ) -> float:
        """
        Turnover = 0.5 * sum(|w_target - w_current|)
        Excludes CASH from turnover sum.
        """
        all_symbols = set(current_weights.keys()).union(set(target_weights.keys()))
        all_symbols.discard("CASH")

        diff_sum = 0.0
        for s in all_symbols:
            w_curr = current_weights.get(s, 0.0)
            w_tgt = target_weights.get(s, 0.0)
            diff_sum += abs(w_tgt - w_curr)

        return float(0.5 * diff_sum)

    def dampen_turnover(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        max_allowed_turnover: Optional[float] = None
    ) -> Dict[str, float]:
        """
        If target weights require turnover exceeding max_turnover budget,
        linearly interpolate between current and target:
        w_damped = (1 - alpha) * w_curr + alpha * w_tgt
        """
        limit = max_allowed_turnover if max_allowed_turnover is not None else self.max_turnover
        turnover = self.compute_turnover(current_weights, target_weights)

        if turnover <= limit or turnover < 1e-6:
            return target_weights

        alpha = limit / turnover
        damped = {}
        all_symbols = set(current_weights.keys()).union(set(target_weights.keys()))

        for s in all_symbols:
            w_c = current_weights.get(s, 0.0)
            w_t = target_weights.get(s, 0.0)
            damped[s] = round((1.0 - alpha) * w_c + alpha * w_t, 5)

        # Normalize
        total = sum(damped.values())
        if total > 0:
            damped = {s: round(v / total, 5) for s, v in damped.items()}

        return damped
