"""
Unit Tests for Portfolio Optimizers and Numerical Solvers.
Verifies convergence, constraints, sum to 1.0, and positive semi-definiteness.
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.portfolio.covariance import CovarianceEstimator
from backend.app.portfolio.optimizers import PortfolioOptimizer

@pytest.fixture
def sample_market_data():
    np.random.seed(42)
    dates = pd.date_range("2022-01-01", periods=252, freq="B")
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
    returns_matrix = np.random.normal(0.0005, 0.015, size=(252, len(symbols)))
    # Inject positive correlation
    returns_matrix[:, 1] = 0.6 * returns_matrix[:, 0] + 0.8 * returns_matrix[:, 1]
    returns_df = pd.DataFrame(returns_matrix, index=dates, columns=symbols)
    return returns_df

def test_covariance_estimators(sample_market_data):
    returns = sample_market_data
    
    # 1. Sample Covariance
    cov_sample = CovarianceEstimator.sample_covariance(returns)
    assert cov_sample.shape == (5, 5)
    evals = np.linalg.eigvalsh(cov_sample)
    assert np.all(evals >= 0)

    # 2. Ledoit-Wolf Shrinkage
    cov_lw, shrinkage = CovarianceEstimator.ledoit_wolf_shrinkage(returns)
    assert cov_lw.shape == (5, 5)
    assert 0.0 <= shrinkage <= 1.0
    assert np.all(np.linalg.eigvalsh(cov_lw) > 0)

    # 3. RMT Cleaning
    cov_rmt = CovarianceEstimator.rmt_cleaned_covariance(returns)
    assert cov_rmt.shape == (5, 5)
    assert np.all(np.linalg.eigvalsh(cov_rmt) > 0)

    # 4. 3-Factor Structured Covariance
    cov_3f = CovarianceEstimator.three_factor_covariance(returns)
    assert cov_3f.shape == (5, 5)
    assert np.all(np.linalg.eigvalsh(cov_3f) >= 0)

def test_minimum_variance_optimizer(sample_market_data):
    returns = sample_market_data
    cov = CovarianceEstimator.sample_covariance(returns)
    opt = PortfolioOptimizer(returns, cov, max_asset_weight=0.35)
    
    res = opt.optimize_minimum_variance()
    weights = list(res["weights"].values())
    
    assert res["optimizer"] == "Minimum Variance"
    assert pytest.approx(sum(weights), abs=1e-3) == 1.0
    for w in weights:
        assert 0.0 <= w <= 0.3501
    assert res["annual_volatility"] > 0

def test_maximum_sharpe_optimizer(sample_market_data):
    returns = sample_market_data
    cov = CovarianceEstimator.ledoit_wolf_shrinkage(returns)[0]
    opt = PortfolioOptimizer(returns, cov, max_asset_weight=0.40)
    
    res = opt.optimize_maximum_sharpe()
    weights = list(res["weights"].values())
    
    assert res["optimizer"] == "Maximum Sharpe Ratio"
    assert pytest.approx(sum(weights), abs=1e-3) == 1.0
    for w in weights:
        assert 0.0 <= w <= 0.4001

def test_risk_parity_optimizer(sample_market_data):
    returns = sample_market_data
    cov = CovarianceEstimator.sample_covariance(returns)
    opt = PortfolioOptimizer(returns, cov, max_asset_weight=0.50)
    
    res = opt.optimize_risk_parity()
    weights = list(res["weights"].values())
    rc = list(res["risk_contributions"].values())
    
    assert res["optimizer"] == "Risk Parity (ERC)"
    assert pytest.approx(sum(weights), abs=1e-3) == 1.0
    # Risk contributions should be approximately balanced
    assert np.std(rc) < 0.15

def test_hierarchical_risk_parity_optimizer(sample_market_data):
    returns = sample_market_data
    cov = CovarianceEstimator.sample_covariance(returns)
    opt = PortfolioOptimizer(returns, cov, max_asset_weight=0.50)
    
    res = opt.optimize_hierarchical_risk_parity()
    weights = list(res["weights"].values())
    
    assert res["optimizer"] == "Hierarchical Risk Parity"
    assert pytest.approx(sum(weights), abs=1e-3) == 1.0
    assert all(w >= 0.0 for w in weights)

def test_black_litterman_optimizer(sample_market_data):
    returns = sample_market_data
    cov = CovarianceEstimator.sample_covariance(returns)
    opt = PortfolioOptimizer(returns, cov, max_asset_weight=0.50)
    
    # Specify an active view: INFY outperforming
    views = {"INFY.NS": 0.25}
    res = opt.optimize_black_litterman(views=views)
    weights = res["weights"]
    
    assert res["optimizer"] == "Black-Litterman"
    assert pytest.approx(sum(weights.values()), abs=1e-3) == 1.0
    assert "posterior_expected_returns" in res
    assert weights["INFY.NS"] > 0.0

def test_cvar_optimizer(sample_market_data):
    returns = sample_market_data
    cov = CovarianceEstimator.sample_covariance(returns)
    opt = PortfolioOptimizer(returns, cov, max_asset_weight=0.50)
    
    res = opt.optimize_cvar()
    weights = list(res["weights"].values())
    
    assert "CVaR" in res["optimizer"]
    assert pytest.approx(sum(weights), abs=1e-3) == 1.0
    assert all(w >= 0.0 for w in weights)
