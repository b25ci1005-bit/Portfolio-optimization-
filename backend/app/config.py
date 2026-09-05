import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Quant Portfolio Optimization & Paper Trading"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quant_platform.db")
    
    # Upstox API v2 Configuration
    UPSTOX_API_KEY: str = os.getenv("UPSTOX_API_KEY", "")
    UPSTOX_API_SECRET: str = os.getenv("UPSTOX_API_SECRET", "")
    UPSTOX_REDIRECT_URI: str = os.getenv("UPSTOX_REDIRECT_URI", "http://localhost:8000/api/upstox/callback")
    UPSTOX_AUTH_URL: str = "https://api.upstox.com/v2/login/authorization/dialog"
    UPSTOX_TOKEN_URL: str = "https://api.upstox.com/v2/login/authorization/token"
    UPSTOX_BASE_API: str = "https://api.upstox.com/v2"
    
    # Financial constants
    DEFAULT_RISK_FREE_RATE: float = 0.065  # 6.5% Indian sovereign / repo benchmark
    DEFAULT_INITIAL_CASH: float = 1_000_000.0  # ₹10,00,000 INR
    DEFAULT_MAX_ASSET_WEIGHT: float = 0.25
    DEFAULT_MAX_SECTOR_WEIGHT: float = 0.35
    DEFAULT_CASH_BUFFER: float = 0.02
    
    # Indian Brokerage & Fee Structure
    BROKERAGE_RATE: float = 0.0003  # 0.03%
    MAX_BROKERAGE_PER_ORDER: float = 20.0  # ₹20 max
    STT_SELL_DELIVERY: float = 0.001  # 0.1% STT on delivery sell
    EXCHANGE_TURNOVER_FEE: float = 0.0000345  # 0.00345% NSE
    GST_RATE: float = 0.18  # 18% GST on (brokerage + exchange fee)
    SEBI_TURNOVER_CHARGES: float = 0.000001  # ₹10 per crore
    STAMP_DUTY_BUY: float = 0.00015  # 0.015% on buy delivery
    MARKET_IMPACT_GAMMA: float = 0.1  # Square root market impact parameter
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
