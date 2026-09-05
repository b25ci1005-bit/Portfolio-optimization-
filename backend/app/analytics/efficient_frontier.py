"""
Efficient Frontier & Capital Allocation Line (CAL) Generator.
Computes:
1. 50+ points along the Markowitz Efficient Frontier curve.
2. Minimum Variance Portfolio.
3. Tangency (Maximum Sharpe) Portfolio.
4. Capital Allocation Line (CAL) ray from (0, Rf).
5. Individual asset risk/return coordinates.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd
import cvxpy as cp
from scipy.optimize import minimize

from backend.app.config import settings

class EfficientFrontier:
    def __init__(
        self,
        returns: pd.DataFrame,
        covariance: np.ndarray,
        rf: float = settings.DEFAULT_RISK_FREE_RATE,
        num_points: int = 50
    ):
        self.returns = returns
        self.symbols = list(returns.columns)
        self.num_assets = len(self.symbols)
        self.cov = covariance
        self.rf = rf
        self.num_points = num_points
        self.mu = returns.mean().values * 252.0

    def compute_frontier(self) -> Dict[str, Any]:
        """
        Generate efficient frontier points by sweeping target returns.
        """
        min_ret = float(np.min(self.mu))
        max_ret = float(np.max(self.mu))

        # 1. Minimum Variance Portfolio
        w_min = cp.Variable(self.num_assets)
        prob_min = cp.Problem(cp.Minimize(cp.quad_form(w_min, self.cov)), [cp.sum(w_min) == 1.0, w_min >= 0.0])
        try:
            prob_min.solve(solver=cp.OSQP)
            min_var_weights = np.array(w_min.value).flatten()
        except Exception:
            min_var_weights = np.ones(self.num_assets) / self.num_assets

        min_var_ret = float(min_var_weights @ self.mu)
        min_var_vol = float(np.sqrt(max(min_var_weights @ self.cov @ min_var_weights, 1e-8)))

        # 2. Maximum Sharpe Portfolio
        def neg_sharpe(w):
            r = float(w @ self.mu)
            v = float(np.sqrt(np.maximum(w @ self.cov @ w, 1e-8)))
            return - (r - self.rf) / v

        res_sharpe = minimize(
            neg_sharpe,
            np.ones(self.num_assets) / self.num_assets,
            bounds=[(0.0, 1.0) for _ in range(self.num_assets)],
            constraints=[{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        )
        max_sharpe_weights = res_sharpe.x if res_sharpe.success else np.ones(self.num_assets) / self.num_assets
        max_sharpe_ret = float(max_sharpe_weights @ self.mu)
        max_sharpe_vol = float(np.sqrt(max(max_sharpe_weights @ self.cov @ max_sharpe_weights, 1e-8)))
        max_sharpe_ratio = float((max_sharpe_ret - self.rf) / max_sharpe_vol) if max_sharpe_vol > 0 else 0.0

        # 3. Sweep target returns from min_var_ret to max_ret
        target_returns = np.linspace(min_var_ret, max(max_ret, max_sharpe_ret * 1.1), self.num_points)
        frontier_points = []

        w = cp.Variable(self.num_assets)
        target = cp.Parameter()
        constraints = [
            cp.sum(w) == 1.0,
            w >= 0.0,
            self.mu @ w >= target
        ]
        objective = cp.Minimize(cp.quad_form(w, self.cov))
        prob = cp.Problem(objective, constraints)

        for tr in target_returns:
            target.value = tr
            try:
                prob.solve(solver=cp.OSQP, warm_start=True)
                if w.value is not None:
                    weights = np.array(w.value).flatten()
                    vol = float(np.sqrt(max(weights @ self.cov @ weights, 1e-8)))
                    ret = float(weights @ self.mu)
                    frontier_points.append({
                        "volatility": round(vol * 100, 2),
                        "expected_return": round(ret * 100, 2),
                        "sharpe": round((ret - self.rf) / vol, 2) if vol > 0 else 0.0
                    })
            except Exception:
                continue

        # Sort frontier points by volatility
        frontier_points = sorted(frontier_points, key=lambda p: p["volatility"])

        # 4. Capital Allocation Line (CAL) Points
        cal_slope = max_sharpe_ratio
        cal_vols = np.linspace(0.0, max_sharpe_vol * 1.6, 20)
        cal_points = [
            {
                "volatility": round(v * 100, 2),
                "expected_return": round((self.rf + cal_slope * v) * 100, 2)
            }
            for v in cal_vols
        ]

        # 5. Individual Asset Coordinates
        asset_points = []
        for i, sym in enumerate(self.symbols):
            asset_vol = float(np.sqrt(self.cov[i, i]))
            asset_ret = float(self.mu[i])
            asset_points.append({
                "symbol": sym,
                "volatility": round(asset_vol * 100, 2),
                "expected_return": round(asset_ret * 100, 2),
                "sharpe": round((asset_ret - self.rf) / asset_vol, 2) if asset_vol > 0 else 0.0
            })

        return {
            "frontier_curve": frontier_points,
            "capital_allocation_line": cal_points,
            "minimum_variance_portfolio": {
                "volatility": round(min_var_vol * 100, 2),
                "expected_return": round(min_var_ret * 100, 2),
                "sharpe": round((min_var_ret - self.rf) / min_var_vol, 2),
                "weights": {self.symbols[i]: round(float(min_var_weights[i]), 4) for i in range(self.num_assets)}
            },
            "tangency_portfolio": {
                "volatility": round(max_sharpe_vol * 100, 2),
                "expected_return": round(max_sharpe_ret * 100, 2),
                "sharpe": round(max_sharpe_ratio, 2),
                "weights": {self.symbols[i]: round(float(max_sharpe_weights[i]), 4) for i in range(self.num_assets)}
            },
            "individual_assets": asset_points,
            "risk_free_rate": round(self.rf * 100, 2)
        }
