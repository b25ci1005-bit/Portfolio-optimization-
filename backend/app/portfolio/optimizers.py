"""
Portfolio Optimization Engine.
Implements:
1. Minimum Variance (CVXPY Convex QP)
2. Maximum Sharpe Ratio (Tangency Portfolio with Indian Rf = 6.5%)
3. Risk Parity / Equal Risk Contribution (Spinu Algorithm / SQP)
4. Hierarchical Risk Parity (HRP from scratch: Clustering, Quasi-Diagonalization, Recursive Bisection)
5. Black-Litterman Model (Equilibrium Prior + Investor Views -> Bayesian Posterior)
6. CVaR (Expected Shortfall) Convex Optimization
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import cvxpy as cp
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

from backend.app.config import settings

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    def __init__(
        self,
        returns: pd.DataFrame,
        covariance: np.ndarray,
        expected_returns: Optional[np.ndarray] = None,
        rf: float = settings.DEFAULT_RISK_FREE_RATE,
        max_asset_weight: float = settings.DEFAULT_MAX_ASSET_WEIGHT
    ):
        self.returns = returns
        self.symbols = list(returns.columns)
        self.num_assets = len(self.symbols)
        self.cov = covariance
        self.rf = rf
        self.max_weight = max_asset_weight

        # Ensure valid expected returns
        if expected_returns is None:
            self.mu = returns.mean().values * 252.0
        else:
            self.mu = expected_returns

    def optimize_minimum_variance(self) -> Dict[str, Any]:
        """
        Minimum Variance Portfolio:
        min w^T Sigma w  s.t. sum(w) = 1, 0 <= w_i <= max_weight
        """
        w = cp.Variable(self.num_assets)
        risk = cp.quad_form(w, self.cov)
        
        # Max asset weight constraint
        effective_max = max(self.max_weight, 1.0 / self.num_assets)
        constraints = [
            cp.sum(w) == 1.0,
            w >= 0.0,
            w <= effective_max
        ]
        
        prob = cp.Problem(cp.Minimize(risk), constraints)
        try:
            prob.solve(solver=cp.OSQP, eps_abs=1e-6, eps_rel=1e-6)
            if w.value is None:
                prob.solve(solver=cp.CLARABEL)
            weights = np.array(w.value).flatten()
        except Exception as e:
            logger.warning(f"CVXPY min variance failed: {e}. Falling back to SLSQP.")
            weights = self._scipy_min_var(effective_max)

        weights = self._clean_and_normalize_weights(weights)
        return self._format_result("Minimum Variance", weights)

    def _scipy_min_var(self, max_weight: float) -> np.ndarray:
        def obj(w):
            return float(w @ self.cov @ w)
        w0 = np.ones(self.num_assets) / self.num_assets
        bnds = [(0.0, max_weight) for _ in range(self.num_assets)]
        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
        res = minimize(obj, w0, method='SLSQP', bounds=bnds, constraints=cons)
        return res.x if res.success else w0

    def optimize_maximum_sharpe(self) -> Dict[str, Any]:
        """
        Maximum Sharpe Ratio (Tangency Portfolio):
        max (w^T mu - Rf) / sqrt(w^T Sigma w) s.t. sum(w) = 1, 0 <= w_i <= max_weight
        """
        effective_max = max(self.max_weight, 1.0 / self.num_assets)
        
        # Negative Sharpe Objective for SLSQP minimization
        def neg_sharpe(w):
            port_return = float(w @ self.mu)
            port_vol = float(np.sqrt(np.maximum(w @ self.cov @ w, 1e-8)))
            return - (port_return - self.rf) / port_vol

        w0 = np.ones(self.num_assets) / self.num_assets
        bounds = [(0.0, effective_max) for _ in range(self.num_assets)]
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

        res = minimize(
            neg_sharpe,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'maxiter': 500}
        )

        weights = res.x if res.success else w0
        weights = self._clean_and_normalize_weights(weights)
        return self._format_result("Maximum Sharpe Ratio", weights)

    def optimize_risk_parity(self) -> Dict[str, Any]:
        """
        Risk Parity / Equal Risk Contribution (ERC):
        Spinu (2013) convex formulation / Cyclical risk contribution matching:
        w_i * (Sigma * w)_i = (1/N) * (w^T Sigma w)
        """
        effective_max = max(self.max_weight, 1.0 / self.num_assets)

        def risk_parity_objective(w):
            port_vol = np.sqrt(np.maximum(w @ self.cov @ w, 1e-8))
            marginal_risk = (self.cov @ w) / port_vol
            risk_contributions = w * marginal_risk
            target_risk = port_vol / self.num_assets
            return float(np.sum((risk_contributions - target_risk) ** 2))

        w0 = np.ones(self.num_assets) / self.num_assets
        bounds = [(0.001, effective_max) for _ in range(self.num_assets)]
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]

        res = minimize(
            risk_parity_objective,
            w0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-10, 'maxiter': 500}
        )

        weights = res.x if res.success else w0
        weights = self._clean_and_normalize_weights(weights)
        return self._format_result("Risk Parity (ERC)", weights)

    def optimize_hierarchical_risk_parity(self) -> Dict[str, Any]:
        """
        Hierarchical Risk Parity (HRP) from scratch:
        1. Tree clustering using correlation distance matrix
        2. Quasi-diagonalization of covariance matrix
        3. Recursive bisection allocating inversely proportional to cluster variance
        """
        corr = self.returns.corr().values
        cov = self.cov.copy()

        # Step 1: Distance matrix D_ij = sqrt(0.5 * (1 - rho_ij))
        dist = np.sqrt(np.maximum(0.5 * (1.0 - corr), 0.0))
        np.fill_diagonal(dist, 0.0)

        # Step 2: Hierarchical Clustering (Linkage)
        condensed_dist = squareform(dist, checks=False)
        link = linkage(condensed_dist, method='single')

        # Step 3: Quasi-Diagonalization (Dendrogram leaf ordering)
        sort_order = self._get_quasi_diag_order(link, self.num_assets)
        sorted_cov = cov[np.ix_(sort_order, sort_order)]

        # Step 4: Recursive Bisection
        weights_sorted = pd.Series(1.0, index=range(self.num_assets))
        cluster_list = [list(range(self.num_assets))]

        while len(cluster_list) > 0:
            cluster_list = [
                c[j:k]
                for c in cluster_list
                for j, k in ((0, len(c) // 2), (len(c) // 2, len(c)))
                if len(c) > 1
            ]
            for i in range(0, len(cluster_list), 2):
                c1 = cluster_list[i]
                c2 = cluster_list[i + 1]
                
                v1 = self._get_cluster_variance(sorted_cov, c1)
                v2 = self._get_cluster_variance(sorted_cov, c2)
                
                # Allocation factor alpha
                alpha = 1.0 - v1 / (v1 + v2) if (v1 + v2) > 0 else 0.5
                
                weights_sorted.iloc[c1] *= alpha
                weights_sorted.iloc[c2] *= (1.0 - alpha)

        # Unsort weights back to original asset order
        weights = np.zeros(self.num_assets)
        for sorted_idx, orig_idx in enumerate(sort_order):
            weights[orig_idx] = weights_sorted.iloc[sorted_idx]

        # Apply max asset weight if needed
        effective_max = max(self.max_weight, 1.0 / self.num_assets)
        weights = np.clip(weights, 0.0, effective_max)
        weights = self._clean_and_normalize_weights(weights)

        return self._format_result("Hierarchical Risk Parity", weights)

    def _get_quasi_diag_order(self, link: np.ndarray, num_assets: int) -> List[int]:
        """Compute dendrogram leaf traversal order for quasi-diagonalization"""
        def get_leaves(node_id):
            if node_id < num_assets:
                return [node_id]
            left = int(link[node_id - num_assets, 0])
            right = int(link[node_id - num_assets, 1])
            return get_leaves(left) + get_leaves(right)

        root_id = 2 * num_assets - 2
        return get_leaves(root_id)

    def _get_cluster_variance(self, cov: np.ndarray, cluster_indices: List[int]) -> float:
        """Compute inverse-variance weighted cluster variance"""
        sub_cov = cov[np.ix_(cluster_indices, cluster_indices)]
        inv_diag = 1.0 / np.maximum(np.diag(sub_cov), 1e-8)
        w = inv_diag / np.sum(inv_diag)
        return float(w @ sub_cov @ w)

    def optimize_black_litterman(
        self,
        views: Optional[Dict[str, float]] = None,
        view_confidences: Optional[Dict[str, float]] = None,
        tau: float = 0.05,
        risk_aversion: float = 3.0
    ) -> Dict[str, Any]:
        """
        Black-Litterman Model:
        Prior Equilibrium Returns: Pi = lambda * Sigma * w_mkt
        Investor Views: P * mu = Q + epsilon, epsilon ~ N(0, Omega)
        Posterior expected returns and covariance fed into Mean-Variance optimizer.
        """
        # Market Portfolio weights prior (Equal weight baseline or size proxy)
        w_mkt = np.ones(self.num_assets) / self.num_assets
        pi = risk_aversion * (self.cov @ w_mkt)

        effective_max = max(self.max_weight, 1.0 / self.num_assets)

        if not views:
            # Default institutional view: Assets with positive 60-day momentum have +2% expected tilt
            views = {}
            for i, sym in enumerate(self.symbols):
                if self.mu[i] > np.median(self.mu):
                    views[sym] = float(self.mu[i] * 1.1)

        # Build Pick matrix P and View vector Q
        view_symbols = [s for s in views.keys() if s in self.symbols]
        k = len(view_symbols)

        if k == 0:
            # Fall back to prior mean-variance
            posterior_mu = pi
            posterior_cov = self.cov
        else:
            P = np.zeros((k, self.num_assets))
            Q = np.zeros(k)
            omega_diag = []

            for row_idx, sym in enumerate(view_symbols):
                asset_idx = self.symbols.index(sym)
                P[row_idx, asset_idx] = 1.0
                Q[row_idx] = views[sym]
                
                # Confidence scale
                conf = view_confidences.get(sym, 0.5) if view_confidences else 0.5
                conf = np.clip(conf, 0.1, 0.99)
                # Uncertainty inversely proportional to confidence
                var_view = (1.0 - conf) / conf * (tau * self.cov[asset_idx, asset_idx])
                omega_diag.append(max(var_view, 1e-6))

            Omega = np.diag(omega_diag)

            # Master Black-Litterman equations
            tau_cov = tau * self.cov
            tau_cov_inv = np.linalg.pinv(tau_cov)
            omega_inv = np.linalg.pinv(Omega)

            # Posterior precision and mean
            precision = tau_cov_inv + P.T @ omega_inv @ P
            posterior_cov_m = np.linalg.pinv(precision)
            posterior_mu = posterior_cov_m @ (tau_cov_inv @ pi + P.T @ omega_inv @ Q)
            posterior_cov = self.cov + posterior_cov_m

        # Convex QP with posterior parameters
        w = cp.Variable(self.num_assets)
        ret = posterior_mu @ w
        risk = cp.quad_form(w, posterior_cov)
        objective = cp.Maximize(ret - (risk_aversion / 2.0) * risk)
        constraints = [
            cp.sum(w) == 1.0,
            w >= 0.0,
            w <= effective_max
        ]
        prob = cp.Problem(objective, constraints)
        try:
            prob.solve(solver=cp.OSQP)
            weights = np.array(w.value).flatten()
        except Exception as e:
            logger.warning(f"BL optimization solver fallback: {e}")
            weights = np.ones(self.num_assets) / self.num_assets

        weights = self._clean_and_normalize_weights(weights)
        result = self._format_result("Black-Litterman", weights)
        result["posterior_expected_returns"] = {
            self.symbols[i]: round(float(posterior_mu[i]), 4) for i in range(self.num_assets)
        }
        return result

    def optimize_cvar(self, alpha: float = 0.95) -> Dict[str, Any]:
        """
        Conditional Value at Risk (CVaR / Expected Shortfall) Optimization:
        Rockafellar & Uryasev (2000) Convex Formulation
        min zeta + 1 / ((1 - alpha) * T) * sum(u_t)
        s.t. u_t >= -r_t^T w - zeta, u_t >= 0, sum(w) = 1, 0 <= w_i <= max_weight
        """
        R = self.returns.values  # (T, N)
        T, N = R.shape
        effective_max = max(self.max_weight, 1.0 / self.num_assets)

        w = cp.Variable(N)
        zeta = cp.Variable()  # VaR threshold
        u = cp.Variable(T)    # Excess losses

        loss = - R @ w
        constraints = [
            u >= loss - zeta,
            u >= 0.0,
            cp.sum(w) == 1.0,
            w >= 0.0,
            w <= effective_max
        ]

        cvar_objective = cp.Minimize(zeta + (1.0 / ((1.0 - alpha) * T)) * cp.sum(u))
        prob = cp.Problem(cvar_objective, constraints)

        try:
            prob.solve(solver=cp.CLARABEL)
            if w.value is None:
                prob.solve(solver=cp.OSQP)
            weights = np.array(w.value).flatten()
            cvar_value = float(prob.value)
        except Exception as e:
            logger.warning(f"CVaR solver error: {e}. Fallback to min variance.")
            return self.optimize_minimum_variance()

        weights = self._clean_and_normalize_weights(weights)
        result = self._format_result("CVaR (Expected Shortfall)", weights)
        result["cvar_95"] = round(cvar_value * np.sqrt(252), 4)
        return result

    def _clean_and_normalize_weights(self, weights: np.ndarray) -> np.ndarray:
        """Ensure no NaNs, negative values, and sum exactly equals 1.0"""
        w = np.nan_to_num(weights, nan=0.0)
        w = np.maximum(w, 0.0)
        total = np.sum(w)
        if total > 1e-7:
            w = w / total
        else:
            w = np.ones(self.num_assets) / self.num_assets
        return w

    def _format_result(self, name: str, weights: np.ndarray) -> Dict[str, Any]:
        """Compute portfolio expected return, volatility, Sharpe ratio, and risk contributions"""
        port_return = float(weights @ self.mu)
        port_variance = float(weights @ self.cov @ weights)
        port_vol = float(np.sqrt(max(port_variance, 1e-8)))
        sharpe = float((port_return - self.rf) / port_vol) if port_vol > 1e-8 else 0.0

        # Marginal and percentage risk contributions
        marginal_risk = (self.cov @ weights) / port_vol if port_vol > 1e-8 else np.zeros(self.num_assets)
        risk_contributions = weights * marginal_risk
        pct_risk_contributions = risk_contributions / port_vol if port_vol > 1e-8 else np.zeros(self.num_assets)

        weights_dict = {self.symbols[i]: round(float(weights[i]), 5) for i in range(self.num_assets)}
        risk_contrib_dict = {
            self.symbols[i]: round(float(pct_risk_contributions[i]), 5) for i in range(self.num_assets)
        }

        return {
            "optimizer": name,
            "weights": weights_dict,
            "expected_annual_return": round(port_return, 4),
            "annual_volatility": round(port_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "risk_contributions": risk_contrib_dict
        }

    @classmethod
    def run_optimizer(
        cls,
        name: str,
        returns: pd.DataFrame,
        covariance: np.ndarray,
        rf: float = settings.DEFAULT_RISK_FREE_RATE,
        max_asset_weight: float = settings.DEFAULT_MAX_ASSET_WEIGHT,
        views: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Unified dispatch for all optimizers"""
        opt = cls(returns=returns, covariance=covariance, rf=rf, max_asset_weight=max_asset_weight)
        key = name.lower().replace("-", "_").replace(" ", "_")

        if key in ["min_variance", "minimum_variance", "min_var"]:
            return opt.optimize_minimum_variance()
        elif key in ["max_sharpe", "maximum_sharpe", "tangency"]:
            return opt.optimize_maximum_sharpe()
        elif key in ["risk_parity", "equal_risk_contribution", "erc"]:
            return opt.optimize_risk_parity()
        elif key in ["hrp", "hierarchical_risk_parity", "hierarchical"]:
            return opt.optimize_hierarchical_risk_parity()
        elif key in ["black_litterman", "bl"]:
            return opt.optimize_black_litterman(views=views)
        elif key in ["cvar", "expected_shortfall"]:
            return opt.optimize_cvar()
        else:
            return opt.optimize_maximum_sharpe()
