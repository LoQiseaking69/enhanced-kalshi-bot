"""
Statistical Arbitrage Strategy for Kalshi Trading Bot

This strategy identifies and exploits pricing inefficiencies between related markets
using statistical analysis and correlation modeling.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from ..core.config import get_trading_config
from ..core.database import db_manager
from .base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class StatisticalArbitrageStrategy(BaseStrategy):
    """
    Statistical arbitrage strategy that identifies mispricings between correlated markets.
    
    The strategy looks for:
    1. Pairs of markets with historical correlation
    2. Temporary divergences from expected price relationships
    3. Mean reversion opportunities
    4. Cross-market arbitrage opportunities
    """
    
    def __init__(self):
        super().__init__("StatisticalArbitrage")
        self.trading_config = get_trading_config()
        
        # Strategy parameters
        self.min_correlation = 0.7
        self.min_cointegration_score = 0.05
        self.zscore_entry_threshold = 2.0
        self.zscore_exit_threshold = 0.5
        self.lookback_days = 30
        self.min_data_points = 20
        
        # Market pair cache
        self.market_pairs = {}
        self.correlation_cache = {}
        self.last_analysis_time = None
        
    def find_correlated_markets(self, markets: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        """Find pairs of markets with significant correlation"""
        correlated_pairs = []
        
        # Get price history for all markets
        market_prices = {}
        for market in markets:
            market_id = market['id']
            price_history = db_manager.get_price_history(market_id, limit=100)
            
            if len(price_history) >= self.min_data_points:
                prices = [(ph.timestamp, ph.yes_price) for ph in price_history if ph.yes_price is not None]
                if len(prices) >= self.min_data_points:
                    market_prices[market_id] = prices
                    
        # Calculate correlations between all pairs
        market_ids = list(market_prices.keys())
        for i, market_a in enumerate(market_ids):
            for market_b in market_ids[i+1:]:
                try:
                    correlation = self._calculate_correlation(
                        market_prices[market_a], 
                        market_prices[market_b]
                    )
                    
                    if abs(correlation) >= self.min_correlation:
                        correlated_pairs.append((market_a, market_b, correlation))
                        
                except Exception as e:
                    self.logger.debug(f"Error calculating correlation for {market_a}-{market_b}: {e}")
                    continue
                    
        # Sort by correlation strength
        correlated_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        self.logger.info(f"Found {len(correlated_pairs)} correlated market pairs")
        return correlated_pairs
        
    def _calculate_correlation(self, prices_a: List[Tuple], prices_b: List[Tuple]) -> float:
        """Calculate correlation between two price series"""
        # Convert to aligned time series
        df_a = pd.DataFrame(prices_a, columns=['timestamp', 'price_a'])
        df_b = pd.DataFrame(prices_b, columns=['timestamp', 'price_b'])
        
        # Merge on timestamp with tolerance
        df_a['timestamp'] = pd.to_datetime(df_a['timestamp'])
        df_b['timestamp'] = pd.to_datetime(df_b['timestamp'])
        
        # Use nearest timestamp matching
        merged = pd.merge_asof(
            df_a.sort_values('timestamp'),
            df_b.sort_values('timestamp'),
            on='timestamp',
            tolerance=pd.Timedelta('1 hour')
        ).dropna()
        
        if len(merged) < self.min_data_points:
            return 0.0
            
        return merged['price_a'].corr(merged['price_b'])
        
    def test_cointegration(self, prices_a: List[float], prices_b: List[float]) -> Tuple[bool, float]:
        """Test for cointegration between two price series"""
        if len(prices_a) != len(prices_b) or len(prices_a) < self.min_data_points:
            return False, 0.0
            
        try:
            # Perform Engle-Granger cointegration test
            # Step 1: Run regression
            X = np.array(prices_a).reshape(-1, 1)
            y = np.array(prices_b)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Step 2: Test residuals for stationarity
            residuals = y - model.predict(X)
            
            # Augmented Dickey-Fuller test on residuals
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(residuals)
            
            # Check if residuals are stationary (p-value < 0.05)
            is_cointegrated = adf_result[1] < self.min_cointegration_score
            p_value = adf_result[1]
            
            return is_cointegrated, p_value
            
        except Exception as e:
            self.logger.debug(f"Cointegration test error: {e}")
            return False, 1.0
            
    def calculate_spread_zscore(self, market_a_id: str, market_b_id: str, 
                               current_price_a: float, current_price_b: float) -> Optional[float]:
        """Calculate z-score of current spread relative to historical spread"""
        try:
            # Get historical prices
            history_a = db_manager.get_price_history(market_a_id, limit=100)
            history_b = db_manager.get_price_history(market_b_id, limit=100)
            
            if len(history_a) < self.min_data_points or len(history_b) < self.min_data_points:
                return None
                
            # Align price series
            prices_a = []
            prices_b = []
            
            # Create timestamp-aligned series
            history_a_dict = {ph.timestamp: ph.yes_price for ph in history_a if ph.yes_price is not None}
            history_b_dict = {ph.timestamp: ph.yes_price for ph in history_b if ph.yes_price is not None}
            
            common_timestamps = set(history_a_dict.keys()) & set(history_b_dict.keys())
            
            for ts in sorted(common_timestamps):
                prices_a.append(history_a_dict[ts])
                prices_b.append(history_b_dict[ts])
                
            if len(prices_a) < self.min_data_points:
                return None
                
            # Calculate historical spreads
            spreads = np.array(prices_a) - np.array(prices_b)
            
            # Calculate current spread
            current_spread = current_price_a - current_price_b
            
            # Calculate z-score
            spread_mean = np.mean(spreads)
            spread_std = np.std(spreads)
            
            if spread_std == 0:
                return None
                
            zscore = (current_spread - spread_mean) / spread_std
            
            return zscore
            
        except Exception as e:
            self.logger.error(f"Error calculating spread z-score: {e}")
            return None
            
    def identify_arbitrage_opportunities(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify statistical arbitrage opportunities"""
        opportunities = []
        
        # Find correlated market pairs
        correlated_pairs = self.find_correlated_markets(markets)
        
        for market_a_id, market_b_id, correlation in correlated_pairs:
            try:
                # Get current market data
                market_a = next((m for m in markets if m['id'] == market_a_id), None)
                market_b = next((m for m in markets if m['id'] == market_b_id), None)
                
                if not market_a or not market_b:
                    continue
                    
                price_a = market_a.get('yes_price')
                price_b = market_b.get('yes_price')
                
                if price_a is None or price_b is None:
                    continue
                    
                # Calculate spread z-score
                zscore = self.calculate_spread_zscore(market_a_id, market_b_id, price_a, price_b)
                
                if zscore is None:
                    continue
                    
                # Check for arbitrage opportunity
                if abs(zscore) >= self.zscore_entry_threshold:
                    
                    # Determine trade direction
                    if zscore > 0:
                        # Spread is too high: sell A, buy B
                        primary_action = 'sell'
                        primary_market = market_a_id
                        secondary_action = 'buy'
                        secondary_market = market_b_id
                    else:
                        # Spread is too low: buy A, sell B
                        primary_action = 'buy'
                        primary_market = market_a_id
                        secondary_action = 'sell'
                        secondary_market = market_b_id
                        
                    # Calculate confidence based on z-score magnitude and correlation
                    confidence = min(abs(zscore) / 4.0, 1.0) * abs(correlation)
                    
                    opportunity = {
                        'type': 'pairs_trade',
                        'primary_market': primary_market,
                        'primary_action': primary_action,
                        'secondary_market': secondary_market,
                        'secondary_action': secondary_action,
                        'zscore': zscore,
                        'correlation': correlation,
                        'confidence': confidence,
                        'spread': price_a - price_b,
                        'expected_reversion': True
                    }
                    
                    opportunities.append(opportunity)
                    
            except Exception as e:
                self.logger.error(f"Error analyzing pair {market_a_id}-{market_b_id}: {e}")
                continue
                
        return opportunities
        
    def identify_cross_market_arbitrage(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify cross-market arbitrage opportunities"""
        opportunities = []
        
        # Group markets by category or related events
        market_groups = {}
        for market in markets:
            category = market.get('category', 'unknown')
            if category not in market_groups:
                market_groups[category] = []
            market_groups[category].append(market)
            
        # Look for arbitrage within each group
        for category, group_markets in market_groups.items():
            if len(group_markets) < 2:
                continue
                
            # Check for probability sum violations
            total_yes_prob = sum(m.get('yes_price', 0) for m in group_markets)
            
            # For mutually exclusive events, total probability should not exceed 1
            if self._are_mutually_exclusive(group_markets) and total_yes_prob > 1.1:
                
                # Find the most overpriced market
                overpriced_markets = sorted(
                    group_markets, 
                    key=lambda m: m.get('yes_price', 0), 
                    reverse=True
                )
                
                opportunity = {
                    'type': 'probability_arbitrage',
                    'markets': [m['id'] for m in overpriced_markets],
                    'total_probability': total_yes_prob,
                    'arbitrage_amount': total_yes_prob - 1.0,
                    'confidence': min((total_yes_prob - 1.0) * 2, 1.0),
                    'suggested_action': 'sell_overpriced'
                }
                
                opportunities.append(opportunity)
                
        return opportunities
        
    def _are_mutually_exclusive(self, markets: List[Dict[str, Any]]) -> bool:
        """Determine if markets represent mutually exclusive events"""
        # Simple heuristic: check if titles suggest mutual exclusivity
        titles = [m.get('title', '').lower() for m in markets]
        
        # Look for election-style markets
        if any('election' in title or 'winner' in title or 'president' in title for title in titles):
            return True
            
        # Look for categorical outcomes
        if any('will' in title and ('yes' in title or 'no' in title) for title in titles):
            return False  # These are typically independent
            
        return False  # Default to not mutually exclusive
        
    def generate_signals(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate statistical arbitrage trading signals"""
        signals = []
        markets = market_data.get('markets', [])
        
        if len(markets) < 2:
            return signals
            
        try:
            # Identify arbitrage opportunities
            pairs_opportunities = self.identify_arbitrage_opportunities(markets)
            cross_market_opportunities = self.identify_cross_market_arbitrage(markets)
            
            # Convert opportunities to trading signals
            for opportunity in pairs_opportunities:
                try:
                    # Create signals for pairs trade
                    primary_signal = {
                        'market_id': opportunity['primary_market'],
                        'strategy_name': self.name,
                        'signal_type': opportunity['primary_action'],
                        'confidence_score': opportunity['confidence'],
                        'target_price': None,  # Use market price
                        'position_size_percentage': self.trading_config.max_position_size_percentage * 0.5,  # Half size for pairs
                        'reasoning': f"Pairs trade: z-score={opportunity['zscore']:.2f}, correlation={opportunity['correlation']:.2f}",
                        'features': {
                            'arbitrage_type': 'pairs_trade',
                            'zscore': opportunity['zscore'],
                            'correlation': opportunity['correlation'],
                            'paired_market': opportunity['secondary_market'],
                            'paired_action': opportunity['secondary_action']
                        },
                        'generated_at': datetime.now(timezone.utc)
                    }
                    
                    secondary_signal = {
                        'market_id': opportunity['secondary_market'],
                        'strategy_name': self.name,
                        'signal_type': opportunity['secondary_action'],
                        'confidence_score': opportunity['confidence'],
                        'target_price': None,  # Use market price
                        'position_size_percentage': self.trading_config.max_position_size_percentage * 0.5,  # Half size for pairs
                        'reasoning': f"Pairs trade: z-score={opportunity['zscore']:.2f}, correlation={opportunity['correlation']:.2f}",
                        'features': {
                            'arbitrage_type': 'pairs_trade',
                            'zscore': opportunity['zscore'],
                            'correlation': opportunity['correlation'],
                            'paired_market': opportunity['primary_market'],
                            'paired_action': opportunity['primary_action']
                        },
                        'generated_at': datetime.now(timezone.utc)
                    }
                    
                    signals.extend([primary_signal, secondary_signal])
                    
                except Exception as e:
                    self.logger.error(f"Error creating pairs trade signals: {e}")
                    continue
                    
            for opportunity in cross_market_opportunities:
                try:
                    # Create signals for cross-market arbitrage
                    if opportunity['type'] == 'probability_arbitrage':
                        # Sell the most overpriced markets
                        overpriced_markets = opportunity['markets'][:2]  # Top 2 overpriced
                        
                        for market_id in overpriced_markets:
                            signal = {
                                'market_id': market_id,
                                'strategy_name': self.name,
                                'signal_type': 'sell',
                                'confidence_score': opportunity['confidence'],
                                'target_price': None,  # Use market price
                                'position_size_percentage': self.trading_config.max_position_size_percentage * 0.3,
                                'reasoning': f"Probability arbitrage: total_prob={opportunity['total_probability']:.2f}",
                                'features': {
                                    'arbitrage_type': 'probability_arbitrage',
                                    'total_probability': opportunity['total_probability'],
                                    'arbitrage_amount': opportunity['arbitrage_amount'],
                                    'related_markets': opportunity['markets']
                                },
                                'generated_at': datetime.now(timezone.utc)
                            }
                            
                            signals.append(signal)
                            
                except Exception as e:
                    self.logger.error(f"Error creating cross-market arbitrage signals: {e}")
                    continue
                    
            self.logger.info(f"Generated {len(signals)} statistical arbitrage signals")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error in statistical arbitrage strategy: {e}")
            return []
            
    def validate_signal(self, signal: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
        """Validate statistical arbitrage signal"""
        if not super().validate_signal(signal, market_data):
            return False
            
        try:
            # Additional validation for arbitrage signals
            features = signal.get('features', {})
            arbitrage_type = features.get('arbitrage_type')
            
            if arbitrage_type == 'pairs_trade':
                # Validate paired market exists
                paired_market = features.get('paired_market')
                if not paired_market:
                    return False
                    
                # Check correlation is still valid
                correlation = features.get('correlation', 0)
                if abs(correlation) < self.min_correlation:
                    return False
                    
                # Check z-score is still significant
                zscore = features.get('zscore', 0)
                if abs(zscore) < self.zscore_entry_threshold:
                    return False
                    
            elif arbitrage_type == 'probability_arbitrage':
                # Validate probability sum is still violated
                total_prob = features.get('total_probability', 0)
                if total_prob <= 1.05:  # Small tolerance
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating arbitrage signal: {e}")
            return False
            
    def get_strategy_performance(self) -> Dict[str, Any]:
        """Get strategy-specific performance metrics"""
        base_performance = super().get_strategy_performance()
        
        # Add arbitrage-specific metrics
        try:
            with db_manager.get_session() as session:
                from ..core.database import Trade
                recent_trades = session.query(Trade).filter(
                    Trade.strategy_name == self.name,
                    Trade.executed_at >= datetime.now(timezone.utc) - timedelta(days=30)
                ).all()
                
            if recent_trades:
                # Calculate arbitrage-specific metrics
                pairs_trades = [t for t in recent_trades if 'pairs_trade' in (t.reasoning or '')]
                arbitrage_trades = [t for t in recent_trades if 'arbitrage' in (t.reasoning or '')]
                
                base_performance.update({
                    'pairs_trades': len(pairs_trades),
                    'arbitrage_trades': len(arbitrage_trades),
                    'avg_confidence': np.mean([t.confidence_score for t in recent_trades if t.confidence_score]),
                    'correlation_cache_size': len(self.correlation_cache)
                })
                
        except Exception as e:
            self.logger.error(f"Error calculating strategy performance: {e}")
            
        return base_performance

