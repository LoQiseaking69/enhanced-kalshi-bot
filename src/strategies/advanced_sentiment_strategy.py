"""
Advanced Sentiment Trading Strategy for Kalshi Trading Bot

This strategy uses sophisticated sentiment analysis combined with market data
to identify trading opportunities in prediction markets.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd

from ..core.config import get_trading_config, get_ml_config
from ..core.database import db_manager
from ..ml_models.sentiment_analyzer import sentiment_analyzer
from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class AdvancedSentimentStrategy(BaseStrategy):
    """
    Advanced sentiment-based trading strategy that combines:
    - Multi-source sentiment analysis
    - Market momentum indicators
    - Volume analysis
    - Risk-adjusted position sizing
    """
    
    def __init__(self):
        super().__init__("AdvancedSentiment")
        self.trading_config = get_trading_config()
        self.ml_config = get_ml_config()
        
        # Strategy parameters
        self.min_sentiment_threshold = 0.6
        self.min_confidence_threshold = 0.7
        self.sentiment_momentum_window = 6  # hours
        self.volume_threshold_multiplier = 1.5
        self.max_position_correlation = 0.8
        
        # Sentiment tracking
        self.sentiment_history = {}
        self.market_keywords_cache = {}
        
    def extract_market_keywords(self, market_title: str, market_subtitle: str = None) -> List[str]:
        """Extract relevant keywords from market title and subtitle"""
        cache_key = f"{market_title}_{market_subtitle}"
        if cache_key in self.market_keywords_cache:
            return self.market_keywords_cache[cache_key]
            
        # Combine title and subtitle
        text = market_title
        if market_subtitle:
            text += f" {market_subtitle}"
            
        # Extract keywords using simple NLP
        import re
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        
        # Clean and tokenize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words
        stop_words = set(stopwords.words('english'))
        keywords = [
            token for token in tokens 
            if token not in stop_words and len(token) > 2
        ]
        
        # Add common variations and synonyms
        extended_keywords = keywords.copy()
        
        # Political keywords
        if any(word in text for word in ['election', 'president', 'congress', 'senate']):
            extended_keywords.extend(['politics', 'vote', 'campaign', 'poll'])
            
        # Economic keywords
        if any(word in text for word in ['economy', 'gdp', 'inflation', 'fed']):
            extended_keywords.extend(['economic', 'financial', 'market', 'rate'])
            
        # Remove duplicates and cache
        keywords = list(set(extended_keywords))
        self.market_keywords_cache[cache_key] = keywords
        
        return keywords
        
    def get_recent_sentiment_data(self, market_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent sentiment data for a market"""
        # Get market info
        market = db_manager.get_market(market_id)
        if not market:
            return []
            
        # Extract keywords
        keywords = self.extract_market_keywords(market.title, market.subtitle)
        
        # Get recent news articles
        articles = db_manager.get_recent_news(hours=hours, min_relevance=0.3)
        
        # Filter and analyze articles
        relevant_articles = []
        for article in articles:
            # Check relevance
            article_text = f"{article.title} {article.content or ''}".lower()
            relevance_score = sum(
                article_text.count(keyword.lower()) for keyword in keywords
            ) / len(keywords) if keywords else 0
            
            if relevance_score > 0.1:  # Minimum relevance threshold
                sentiment_data = sentiment_analyzer.analyze_article(
                    article.title,
                    article.content or "",
                    article.source
                )
                sentiment_data['relevance_score'] = relevance_score
                sentiment_data['published_at'] = article.published_at
                relevant_articles.append(sentiment_data)
                
        return sorted(relevant_articles, key=lambda x: x['published_at'], reverse=True)
        
    def calculate_sentiment_momentum(self, sentiment_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sentiment momentum over time"""
        if len(sentiment_data) < 2:
            return {'momentum': 0.0, 'trend': 'neutral', 'strength': 0.0}
            
        # Sort by time
        sorted_data = sorted(sentiment_data, key=lambda x: x['published_at'])
        
        # Calculate time-weighted sentiment scores
        now = datetime.now(timezone.utc)
        weighted_scores = []
        
        for data in sorted_data:
            time_diff = (now - data['published_at']).total_seconds() / 3600  # hours
            weight = max(0, 1 - (time_diff / self.sentiment_momentum_window))
            
            if weight > 0:
                weighted_score = data['sentiment_score'] * weight * data['confidence']
                weighted_scores.append((data['published_at'], weighted_score, weight))
                
        if len(weighted_scores) < 2:
            return {'momentum': 0.0, 'trend': 'neutral', 'strength': 0.0}
            
        # Calculate momentum as the slope of weighted sentiment over time
        times = [(ws[0] - weighted_scores[0][0]).total_seconds() for ws in weighted_scores]
        scores = [ws[1] for ws in weighted_scores]
        weights = [ws[2] for ws in weighted_scores]
        
        # Weighted linear regression
        if len(times) > 1:
            momentum = np.polyfit(times, scores, 1, w=weights)[0]
        else:
            momentum = 0.0
            
        # Determine trend
        if momentum > 0.01:
            trend = 'positive'
        elif momentum < -0.01:
            trend = 'negative'
        else:
            trend = 'neutral'
            
        # Calculate strength based on consistency and magnitude
        strength = min(abs(momentum) * 100, 1.0)
        
        return {
            'momentum': momentum,
            'trend': trend,
            'strength': strength,
            'data_points': len(weighted_scores)
        }
        
    def analyze_volume_pattern(self, market_id: str) -> Dict[str, float]:
        """Analyze volume patterns for the market"""
        # Get recent price history
        price_history = db_manager.get_price_history(market_id, limit=100)
        
        if len(price_history) < 10:
            return {'volume_signal': 0.0, 'volume_trend': 'neutral'}
            
        # Convert to DataFrame for analysis
        df = pd.DataFrame([
            {
                'timestamp': ph.timestamp,
                'volume': ph.volume or 0,
                'price_change': abs(ph.yes_price - (price_history[i+1].yes_price if i+1 < len(price_history) else ph.yes_price))
            }
            for i, ph in enumerate(price_history)
        ])
        
        if df['volume'].sum() == 0:
            return {'volume_signal': 0.0, 'volume_trend': 'neutral'}
            
        # Calculate volume metrics
        recent_volume = df['volume'].head(10).mean()
        historical_volume = df['volume'].tail(50).mean()
        
        volume_ratio = recent_volume / historical_volume if historical_volume > 0 else 1.0
        
        # Volume-price relationship
        correlation = df['volume'].corr(df['price_change'])
        
        # Generate volume signal
        if volume_ratio > self.volume_threshold_multiplier and correlation > 0.3:
            volume_signal = min((volume_ratio - 1) * 0.5, 1.0)
            volume_trend = 'increasing'
        elif volume_ratio < (1 / self.volume_threshold_multiplier):
            volume_signal = -min((1 - volume_ratio) * 0.5, 1.0)
            volume_trend = 'decreasing'
        else:
            volume_signal = 0.0
            volume_trend = 'neutral'
            
        return {
            'volume_signal': volume_signal,
            'volume_trend': volume_trend,
            'volume_ratio': volume_ratio,
            'volume_price_correlation': correlation
        }
        
    def calculate_position_correlation(self, market_id: str) -> float:
        """Calculate correlation with existing positions"""
        active_positions = db_manager.get_active_positions()
        
        if not active_positions:
            return 0.0
            
        # Get market category
        target_market = db_manager.get_market(market_id)
        if not target_market:
            return 0.0
            
        # Calculate correlation based on category and keywords
        correlations = []
        
        for position in active_positions:
            position_market = db_manager.get_market(position.market_id)
            if not position_market:
                continue
                
            # Category correlation
            if position_market.category == target_market.category:
                correlations.append(0.7)
                
            # Keyword correlation
            target_keywords = set(self.extract_market_keywords(target_market.title, target_market.subtitle))
            position_keywords = set(self.extract_market_keywords(position_market.title, position_market.subtitle))
            
            if target_keywords and position_keywords:
                keyword_overlap = len(target_keywords.intersection(position_keywords)) / len(target_keywords.union(position_keywords))
                correlations.append(keyword_overlap)
                
        return max(correlations) if correlations else 0.0
        
    def calculate_confidence_score(self, sentiment_data: Dict[str, Any], momentum_data: Dict[str, Any], 
                                 volume_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the trading signal"""
        
        # Base confidence from sentiment
        sentiment_confidence = sentiment_data.get('confidence', 0.0)
        sentiment_strength = abs(sentiment_data.get('sentiment_score', 0.0))
        
        # Momentum contribution
        momentum_strength = momentum_data.get('strength', 0.0)
        momentum_consistency = 1.0 if momentum_data.get('data_points', 0) >= 3 else 0.5
        
        # Volume contribution
        volume_strength = abs(volume_data.get('volume_signal', 0.0))
        
        # Weighted confidence calculation
        confidence = (
            sentiment_confidence * 0.4 +
            sentiment_strength * 0.3 +
            momentum_strength * momentum_consistency * 0.2 +
            volume_strength * 0.1
        )
        
        return min(confidence, 1.0)
        
    def generate_signals(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals based on sentiment analysis"""
        signals = []
        
        for market in market_data.get('markets', []):
            try:
                market_id = market['id']
                
                # Check position correlation
                correlation = self.calculate_position_correlation(market_id)
                if correlation > self.max_position_correlation:
                    self.logger.info(f"Skipping {market_id} due to high correlation: {correlation:.2f}")
                    continue
                    
                # Get sentiment data
                sentiment_data_list = self.get_recent_sentiment_data(market_id)
                
                if not sentiment_data_list:
                    continue
                    
                # Calculate overall market sentiment
                market_keywords = self.extract_market_keywords(market['title'], market.get('subtitle'))
                market_sentiment = sentiment_analyzer.get_market_sentiment(
                    [{'title': item['title'], 'content': '', 'source': item.get('source')} for item in sentiment_data_list],
                    market_keywords
                )
                
                # Calculate sentiment momentum
                momentum_data = self.calculate_sentiment_momentum(sentiment_data_list)
                
                # Analyze volume patterns
                volume_data = self.analyze_volume_pattern(market_id)
                
                # Calculate confidence
                confidence = self.calculate_confidence_score(market_sentiment, momentum_data, volume_data)
                
                # Generate signal if thresholds are met
                sentiment_score = market_sentiment.get('overall_sentiment', 0.0)
                
                if (abs(sentiment_score) >= self.min_sentiment_threshold and 
                    confidence >= self.min_confidence_threshold):
                    
                    # Determine action
                    if sentiment_score > 0:
                        action = 'buy'
                        target_price = market.get('yes_price', 0.5)
                    else:
                        action = 'sell'
                        target_price = market.get('no_price', 0.5)
                        
                    # Calculate position size based on confidence and risk
                    base_position_size = self.trading_config.max_position_size_percentage
                    risk_adjusted_size = base_position_size * confidence
                    
                    # Adjust for momentum
                    if momentum_data['trend'] == ('positive' if sentiment_score > 0 else 'negative'):
                        risk_adjusted_size *= (1 + momentum_data['strength'] * 0.5)
                    else:
                        risk_adjusted_size *= (1 - momentum_data['strength'] * 0.3)
                        
                    # Adjust for volume
                    volume_adjustment = 1 + (volume_data['volume_signal'] * 0.2)
                    risk_adjusted_size *= volume_adjustment
                    
                    # Cap position size
                    risk_adjusted_size = min(risk_adjusted_size, base_position_size * 1.5)
                    
                    signal = {
                        'market_id': market_id,
                        'strategy_name': self.name,
                        'signal_type': action,
                        'confidence_score': confidence,
                        'target_price': target_price,
                        'position_size_percentage': risk_adjusted_size,
                        'reasoning': f"Sentiment: {sentiment_score:.3f}, Momentum: {momentum_data['trend']}, Volume: {volume_data['volume_trend']}",
                        'features': {
                            'sentiment_score': sentiment_score,
                            'sentiment_confidence': market_sentiment.get('confidence', 0.0),
                            'momentum': momentum_data,
                            'volume': volume_data,
                            'article_count': len(sentiment_data_list),
                            'correlation': correlation
                        },
                        'generated_at': datetime.now(timezone.utc)
                    }
                    
                    signals.append(signal)
                    
                    self.logger.info(
                        f"Generated {action} signal for {market_id}: "
                        f"sentiment={sentiment_score:.3f}, confidence={confidence:.3f}"
                    )
                    
            except Exception as e:
                self.logger.error(f"Error generating signal for market {market.get('id', 'unknown')}: {e}")
                continue
                
        return signals
        
    def validate_signal(self, signal: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
        """Validate trading signal before execution"""
        try:
            market_id = signal['market_id']
            
            # Check if market still exists and is active
            market = db_manager.get_market(market_id)
            if not market or market.status != 'active':
                return False
                
            # Check confidence threshold
            if signal['confidence_score'] < self.min_confidence_threshold:
                return False
                
            # Check for recent signals to avoid over-trading
            recent_signals = db_manager.get_pending_signals(self.name)
            recent_market_signals = [s for s in recent_signals if s.market_id == market_id]
            
            if len(recent_market_signals) > 0:
                last_signal_time = max(s.generated_at for s in recent_market_signals)
                time_since_last = (datetime.now(timezone.utc) - last_signal_time).total_seconds() / 3600
                
                if time_since_last < 1:  # Wait at least 1 hour between signals
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating signal: {e}")
            return False
            
    def update_sentiment_history(self, market_id: str, sentiment_score: float, confidence: float):
        """Update sentiment history for tracking"""
        if market_id not in self.sentiment_history:
            self.sentiment_history[market_id] = []
            
        self.sentiment_history[market_id].append({
            'timestamp': datetime.now(timezone.utc),
            'sentiment_score': sentiment_score,
            'confidence': confidence
        })
        
        # Keep only recent history
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)
        self.sentiment_history[market_id] = [
            entry for entry in self.sentiment_history[market_id]
            if entry['timestamp'] > cutoff_time
        ]
        
    def get_strategy_performance(self) -> Dict[str, Any]:
        """Get strategy-specific performance metrics"""
        # Get recent trades for this strategy
        with db_manager.get_session() as session:
            from ..core.database import Trade
            recent_trades = session.query(Trade).filter(
                Trade.strategy_name == self.name,
                Trade.executed_at >= datetime.now(timezone.utc) - timedelta(days=30)
            ).all()
            
        if not recent_trades:
            return {'total_trades': 0, 'avg_confidence': 0.0, 'success_rate': 0.0}
            
        # Calculate metrics
        total_trades = len(recent_trades)
        avg_confidence = np.mean([trade.confidence_score for trade in recent_trades if trade.confidence_score])
        
        # Calculate success rate (simplified - would need actual P&L data)
        successful_trades = sum(1 for trade in recent_trades if trade.confidence_score > 0.7)
        success_rate = successful_trades / total_trades if total_trades > 0 else 0.0
        
        return {
            'total_trades': total_trades,
            'avg_confidence': avg_confidence,
            'success_rate': success_rate,
            'strategy_name': self.name
        }

