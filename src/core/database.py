"""
Enhanced Database Management for Kalshi Trading Bot

This module provides comprehensive database management with SQLAlchemy ORM,
connection pooling, migrations, and data models.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Boolean, Text, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .config import get_database_config

logger = logging.getLogger(__name__)

# Database base class
Base = declarative_base()

class Market(Base):
    """Market data model"""
    __tablename__ = 'markets'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    subtitle = Column(String)
    category = Column(String)
    status = Column(String)
    yes_price = Column(Float)
    no_price = Column(Float)
    volume = Column(Float)
    open_interest = Column(Float)
    close_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    trades = relationship("Trade", back_populates="market")
    price_history = relationship("PriceHistory", back_populates="market")
    
    __table_args__ = (
        Index('idx_market_category', 'category'),
        Index('idx_market_status', 'status'),
        Index('idx_market_close_date', 'close_date'),
    )

class Trade(Base):
    """Trade execution model"""
    __tablename__ = 'trades'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(String, ForeignKey('markets.id'), nullable=False)
    strategy_name = Column(String, nullable=False)
    action = Column(String, nullable=False)  # 'buy' or 'sell'
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    confidence_score = Column(Float)
    executed_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relationships
    market = relationship("Market", back_populates="trades")
    
    __table_args__ = (
        Index('idx_trade_market_id', 'market_id'),
        Index('idx_trade_strategy', 'strategy_name'),
        Index('idx_trade_executed_at', 'executed_at'),
    )

class Position(Base):
    """Current position model"""
    __tablename__ = 'positions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(String, ForeignKey('markets.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    current_value = Column(Float)
    unrealized_pnl = Column(Float)
    opened_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    market = relationship("Market")
    
    __table_args__ = (
        UniqueConstraint('market_id', name='uq_position_market'),
        Index('idx_position_market_id', 'market_id'),
    )

class PriceHistory(Base):
    """Historical price data model"""
    __tablename__ = 'price_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(String, ForeignKey('markets.id'), nullable=False)
    yes_price = Column(Float, nullable=False)
    no_price = Column(Float, nullable=False)
    volume = Column(Float)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relationships
    market = relationship("Market", back_populates="price_history")
    
    __table_args__ = (
        Index('idx_price_history_market_timestamp', 'market_id', 'timestamp'),
    )

class NewsArticle(Base):
    """News article model for sentiment analysis"""
    __tablename__ = 'news_articles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text)
    source = Column(String)
    url = Column(String)
    published_at = Column(DateTime(timezone=True))
    sentiment_score = Column(Float)
    relevance_score = Column(Float)
    keywords = Column(JSON)
    processed_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_news_published_at', 'published_at'),
        Index('idx_news_source', 'source'),
        Index('idx_news_sentiment', 'sentiment_score'),
    )

class TradingSignal(Base):
    """Trading signal model"""
    __tablename__ = 'trading_signals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(String, ForeignKey('markets.id'), nullable=False)
    strategy_name = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # 'buy', 'sell', 'hold'
    confidence_score = Column(Float, nullable=False)
    reasoning = Column(Text)
    features = Column(JSON)
    generated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    executed = Column(Boolean, default=False)
    
    # Relationships
    market = relationship("Market")
    
    __table_args__ = (
        Index('idx_signal_market_strategy', 'market_id', 'strategy_name'),
        Index('idx_signal_generated_at', 'generated_at'),
        Index('idx_signal_executed', 'executed'),
    )

class PerformanceMetrics(Base):
    """Performance tracking model"""
    __tablename__ = 'performance_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime(timezone=True), nullable=False)
    total_value = Column(Float, nullable=False)
    daily_pnl = Column(Float)
    total_pnl = Column(Float)
    win_rate = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    total_trades = Column(Integer)
    successful_trades = Column(Integer)
    
    __table_args__ = (
        Index('idx_performance_date', 'date'),
    )

class MLModel(Base):
    """Machine learning model metadata"""
    __tablename__ = 'ml_models'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    file_path = Column(String)
    parameters = Column(JSON)
    performance_metrics = Column(JSON)
    training_data_size = Column(Integer)
    trained_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_active = Column(Boolean, default=False)
    
    __table_args__ = (
        UniqueConstraint('name', 'version', name='uq_model_name_version'),
        Index('idx_model_name', 'name'),
        Index('idx_model_active', 'is_active'),
    )

class DatabaseManager:
    """
    Enhanced database manager with connection pooling, session management,
    and utility methods for common operations.
    """
    
    def __init__(self):
        self.config = get_database_config()
        self.engine = None
        self.SessionLocal = None
        self.logger = logging.getLogger(__name__)
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize database engine with connection pooling"""
        self.engine = create_engine(
            self.config.url,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            echo=False  # Set to True for SQL debugging
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        self.logger.info("Database tables created successfully")
        
    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(bind=self.engine)
        self.logger.info("Database tables dropped successfully")
        
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
            
    def get_market(self, market_id: str) -> Optional[Market]:
        """Get market by ID"""
        with self.get_session() as session:
            return session.query(Market).filter(Market.id == market_id).first()
            
    def update_market(self, market_data: Dict[str, Any]) -> Market:
        """Update or create market"""
        with self.get_session() as session:
            market = session.query(Market).filter(Market.id == market_data['id']).first()
            
            if market:
                # Update existing market
                for key, value in market_data.items():
                    if hasattr(market, key):
                        setattr(market, key, value)
                market.updated_at = datetime.now(timezone.utc)
            else:
                # Create new market
                market = Market(**market_data)
                session.add(market)
                
            session.commit()
            session.refresh(market)
            return market
            
    def record_trade(self, trade_data: Dict[str, Any]) -> Trade:
        """Record a new trade"""
        with self.get_session() as session:
            trade = Trade(**trade_data)
            session.add(trade)
            session.commit()
            session.refresh(trade)
            return trade
            
    def update_position(self, market_id: str, quantity: int, average_price: float) -> Position:
        """Update or create position"""
        with self.get_session() as session:
            position = session.query(Position).filter(Position.market_id == market_id).first()
            
            if position:
                # Update existing position
                total_quantity = position.quantity + quantity
                if total_quantity == 0:
                    # Close position
                    session.delete(position)
                    session.commit()
                    return None
                else:
                    # Update position
                    total_cost = (position.quantity * position.average_price) + (quantity * average_price)
                    position.quantity = total_quantity
                    position.average_price = total_cost / total_quantity
                    position.updated_at = datetime.now(timezone.utc)
            else:
                # Create new position
                position = Position(
                    market_id=market_id,
                    quantity=quantity,
                    average_price=average_price
                )
                session.add(position)
                
            session.commit()
            session.refresh(position)
            return position
            
    def get_active_positions(self) -> List[Position]:
        """Get all active positions"""
        with self.get_session() as session:
            return session.query(Position).filter(Position.quantity != 0).all()
            
    def record_price_history(self, market_id: str, yes_price: float, no_price: float, volume: float = None):
        """Record price history"""
        with self.get_session() as session:
            price_record = PriceHistory(
                market_id=market_id,
                yes_price=yes_price,
                no_price=no_price,
                volume=volume
            )
            session.add(price_record)
            session.commit()
            
    def get_price_history(self, market_id: str, limit: int = 100) -> List[PriceHistory]:
        """Get price history for a market"""
        with self.get_session() as session:
            return (session.query(PriceHistory)
                   .filter(PriceHistory.market_id == market_id)
                   .order_by(PriceHistory.timestamp.desc())
                   .limit(limit)
                   .all())
                   
    def record_news_article(self, article_data: Dict[str, Any]) -> NewsArticle:
        """Record a news article"""
        with self.get_session() as session:
            article = NewsArticle(**article_data)
            session.add(article)
            session.commit()
            session.refresh(article)
            return article
            
    def get_recent_news(self, hours: int = 24, min_relevance: float = 0.5) -> List[NewsArticle]:
        """Get recent relevant news articles"""
        with self.get_session() as session:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            return (session.query(NewsArticle)
                   .filter(NewsArticle.published_at >= cutoff_time)
                   .filter(NewsArticle.relevance_score >= min_relevance)
                   .order_by(NewsArticle.published_at.desc())
                   .all())
                   
    def record_trading_signal(self, signal_data: Dict[str, Any]) -> TradingSignal:
        """Record a trading signal"""
        with self.get_session() as session:
            signal = TradingSignal(**signal_data)
            session.add(signal)
            session.commit()
            session.refresh(signal)
            return signal
            
    def get_pending_signals(self, strategy_name: str = None) -> List[TradingSignal]:
        """Get pending trading signals"""
        with self.get_session() as session:
            query = session.query(TradingSignal).filter(TradingSignal.executed == False)
            if strategy_name:
                query = query.filter(TradingSignal.strategy_name == strategy_name)
            return query.order_by(TradingSignal.confidence_score.desc()).all()
            
    def record_performance_metrics(self, metrics_data: Dict[str, Any]) -> PerformanceMetrics:
        """Record daily performance metrics"""
        with self.get_session() as session:
            metrics = PerformanceMetrics(**metrics_data)
            session.add(metrics)
            session.commit()
            session.refresh(metrics)
            return metrics
            
    def get_performance_history(self, days: int = 30) -> List[PerformanceMetrics]:
        """Get performance history"""
        with self.get_session() as session:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            return (session.query(PerformanceMetrics)
                   .filter(PerformanceMetrics.date >= cutoff_date)
                   .order_by(PerformanceMetrics.date.desc())
                   .all())
                   
    def save_ml_model(self, model_data: Dict[str, Any]) -> MLModel:
        """Save ML model metadata"""
        with self.get_session() as session:
            # Deactivate previous versions
            session.query(MLModel).filter(
                MLModel.name == model_data['name'],
                MLModel.is_active == True
            ).update({'is_active': False})
            
            # Save new model
            model = MLModel(**model_data)
            session.add(model)
            session.commit()
            session.refresh(model)
            return model
            
    def get_active_model(self, model_name: str) -> Optional[MLModel]:
        """Get active ML model by name"""
        with self.get_session() as session:
            return (session.query(MLModel)
                   .filter(MLModel.name == model_name)
                   .filter(MLModel.is_active == True)
                   .first())

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db_session():
    """Get database session"""
    return db_manager.get_session()

def init_database():
    """Initialize database tables"""
    db_manager.create_tables()

from datetime import timedelta

