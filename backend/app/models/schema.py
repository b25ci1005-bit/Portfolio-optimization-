import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.app.models.database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="Default Indian Paper Portfolio")
    initial_capital = Column(Float, nullable=False, default=1_000_000.0)
    current_cash = Column(Float, nullable=False, default=1_000_000.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="portfolio", cascade="all, delete-orphan")
    nav_history = relationship("DailyNAV", back_populates="portfolio", cascade="all, delete-orphan")
    rebalance_logs = relationship("RebalanceLog", back_populates="portfolio", cascade="all, delete-orphan")

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    ticker = Column(String(30), nullable=False)
    shares = Column(Float, nullable=False, default=0.0)
    avg_price = Column(Float, nullable=False, default=0.0)
    current_price = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="positions")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    ticker = Column(String(30), nullable=False)
    order_type = Column(String(10), nullable=False)  # BUY / SELL
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)            # Intended execution price
    fill_price = Column(Float, nullable=False)       # Price after slippage
    slippage = Column(Float, nullable=False, default=0.0)
    fees = Column(Float, nullable=False, default=0.0)
    status = Column(String(20), nullable=False, default="FILLED")  # PENDING, FILLED, REJECTED
    executed_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="orders")

class DailyNAV(Base):
    __tablename__ = "daily_nav"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    date = Column(String(20), nullable=False, index=True)
    nav = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    invested_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="nav_history")

class RebalanceLog(Base):
    __tablename__ = "rebalance_log"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    optimizer_used = Column(String(50), nullable=False)
    covariance_used = Column(String(50), nullable=False)
    target_weights_json = Column(Text, nullable=False)
    realized_turnover = Column(Float, default=0.0)
    total_fees_paid = Column(Float, default=0.0)
    
    portfolio = relationship("Portfolio", back_populates="rebalance_logs")

class UpstoxToken(Base):
    __tablename__ = "upstox_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    user_id = Column(String(50), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
