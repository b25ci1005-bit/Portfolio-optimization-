"""
Covariance & Risk Estimation Engine.
Implements 4 robust institutional estimators:
1. Sample Covariance (Annualized)
2. Ledoit-Wolf Shrinkage
3. Random Matrix Theory (RMT) Cleaning (Marchenko-Pastur eigenvalue filtering)
4. 3-Factor Structured Covariance (Statistical / Factor-based Decomposition)
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA

class CovarianceEstimator:
    @staticmethod
    def sample_covariance(returns: pd.DataFrame, annualize: bool = True) -> np.ndarray:
        """
        Compute standard empirical sample covariance matrix.
        Annualized by 252 trading days.
        """
        cov = returns.cov().values
        if annualize:
            cov = cov * 252.0
        return CovarianceEstimator._ensure_psd(cov)

    @staticmethod
    def ledoit_wolf_shrinkage(returns: pd.DataFrame, annualize: bool = True) -> Tuple[np.ndarray, float]:
        """
        Compute Ledoit-Wolf shrinkage covariance matrix.
        Shrinks sample covariance toward constant correlation target.
        Returns (shrinkage_covariance, shrinkage_intensity).
        """
        lw = LedoitWolf()
        lw.fit(returns.values)
        cov = lw.covariance_
        shrinkage = float(lw.shrinkage_)
        if annualize:
            cov = cov * 252.0
        return CovarianceEstimator._ensure_psd(cov), shrinkage

    @staticmethod
    def rmt_cleaned_covariance(returns: pd.DataFrame, annualize: bool = True) -> np.ndarray:
        """
        Random Matrix Theory (RMT) Cleaning using Marchenko-Pastur distribution.
        Filters out noise eigenvalues of the correlation matrix and replaces
        them with their average to preserve the matrix trace.
        """
        T, N = returns.shape
        q = float(T) / float(N)

        # Correlation matrix
        corr = returns.corr().values
        stds = returns.std().values

        # Eigen-decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(corr)

        # Theoretical bounds from Marchenko-Pastur theorem
        # sigma^2 estimated as variance of residuals / average eigenvalue outside pure market mode
        # In financial return matrices, the largest eigenvalue lambda_N is the market mode.
        # We estimate noise variance using non-market eigenvalues.
        non_market_evals = eigenvalues[:-1] if N > 1 else eigenvalues
        sigma2 = float(np.mean(non_market_evals)) if len(non_market_evals) > 0 else 1.0

        lambda_max = sigma2 * (1.0 + np.sqrt(1.0 / q)) ** 2
        lambda_min = sigma2 * (1.0 - np.sqrt(1.0 / q)) ** 2

        # Identify noise eigenvalues
        cleaned_evals = eigenvalues.copy()
        noise_idx = np.where(cleaned_evals < lambda_max)[0]

        if len(noise_idx) > 0:
            # Replace noise eigenvalues with their mean to preserve trace
            noise_mean = float(np.mean(cleaned_evals[noise_idx]))
            cleaned_evals[noise_idx] = noise_mean

        # Reconstruct cleaned correlation matrix
        cleaned_corr = eigenvectors @ np.diag(cleaned_evals) @ eigenvectors.T

        # Normalize diagonal to 1.0
        d_inv = 1.0 / np.sqrt(np.diag(cleaned_corr))
        cleaned_corr = d_inv[:, None] * cleaned_corr * d_inv[None, :]
        np.fill_diagonal(cleaned_corr, 1.0)
        cleaned_corr = np.clip(cleaned_corr, -1.0, 1.0)

        # Convert back to covariance matrix
        D = np.diag(stds)
        cleaned_cov = D @ cleaned_corr @ D

        if annualize:
            cleaned_cov = cleaned_cov * 252.0

        return CovarianceEstimator._ensure_psd(cleaned_cov)

    @staticmethod
    def three_factor_covariance(
        returns: pd.DataFrame,
        factor_returns: Optional[pd.DataFrame] = None,
        annualize: bool = True
    ) -> np.ndarray:
        """
        3-Factor Structured Covariance.
        Decomposes asset returns into 3 systematic factors (Market, Size, Value / PCA proxies)
        plus diagonal idiosyncratic noise:
        Sigma = B * Sigma_F * B^T + D
        """
        X = returns.values
        T, N = X.shape

        if factor_returns is not None and factor_returns.shape[1] >= 3:
            # Use explicit factor returns
            F = factor_returns.iloc[:, :3].values
            # OLS regression: X = F * B^T + E
            F_with_const = np.column_stack([np.ones(T), F])
            beta_matrix = np.linalg.lstsq(F_with_const, X, rcond=None)[0]
            B = beta_matrix[1:, :].T  # Shape: (N, 3)
            residuals = X - (F_with_const @ beta_matrix)
            cov_F = np.cov(F, rowvar=False)
            idio_var = np.var(residuals, axis=0, ddof=4)
        else:
            # Statistical 3-Factor Model via Principal Component Analysis
            pca = PCA(n_components=min(3, N, T))
            F = pca.fit_transform(X)  # Systematic factor time series (T x 3)
            B = pca.components_.T     # Factor loadings (N x 3)
            reconstructed = F @ B.T
            residuals = X - reconstructed
            cov_F = np.cov(F, rowvar=False)
            idio_var = np.var(residuals, axis=0)

        # Structured Covariance: B * Cov(F) * B^T + diag(idio_var)
        structured_cov = (B @ cov_F @ B.T) + np.diag(idio_var)

        if annualize:
            structured_cov = structured_cov * 252.0

        return CovarianceEstimator._ensure_psd(structured_cov)

    @staticmethod
    def _ensure_psd(matrix: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
        """
        Ensure symmetric positive semi-definiteness via eigenvalue clipping.
        """
        sym = (matrix + matrix.T) / 2.0
        evals, evecs = np.linalg.eigh(sym)
        clipped_evals = np.maximum(evals, epsilon)
        psd = evecs @ np.diag(clipped_evals) @ evecs.T
        return (psd + psd.T) / 2.0

    @classmethod
    def estimate(
        cls,
        returns: pd.DataFrame,
        method: str = "ledoit_wolf",
        annualize: bool = True
    ) -> np.ndarray:
        """Unified dispatch for covariance estimators"""
        m = method.lower().replace("-", "_").replace(" ", "_")
        if m == "sample":
            return cls.sample_covariance(returns, annualize=annualize)
        elif m in ["ledoit_wolf", "shrinkage"]:
            cov, _ = cls.ledoit_wolf_shrinkage(returns, annualize=annualize)
            return cov
        elif m in ["rmt", "random_matrix_theory", "marchenko_pastur"]:
            return cls.rmt_cleaned_covariance(returns, annualize=annualize)
        elif m in ["three_factor", "factor", "3_factor"]:
            return cls.three_factor_covariance(returns, annualize=annualize)
        else:
            cov, _ = cls.ledoit_wolf_shrinkage(returns, annualize=annualize)
            return cov
