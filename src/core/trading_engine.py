"""
Main Trading Engine for Enhanced Kalshi Trading Bot

This module orchestrates all trading activities including strategy execution,
risk management, order management, and performance tracking.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
import threading
import time

from .config import get_trading_config, get_monitoring_config
from .database import db_manager
from ..api.kalshi_client import kalshi_client
from ..strategies.advanced_sentiment_strategy import AdvancedSentimentStrategy
from ..strategies.statistical_arbitrage_strategy import StatisticalArbitrageStrategy
from ..risk_management.portfolio_manager import risk_manager
from ..ml_models.sentiment_analyzer import sentiment_analyzer

logger = logging.getLogger(__name__)

class TradingEngine:
    """
    Main trading engine that orchestrates all trading activities.
    
    Responsibilities:
    - Strategy execution and coordination
    - Risk management integration
    - Order execution and management
    - Performance monitoring
    - Error handling and recovery
    """
    
    def __init__(self):
        self.trading_config = get_trading_config()
        self.monitoring_config = get_monitoring_config()
        self.logger = logging.getLogger(__name__)
        
        # Engine state
        self.is_running = False
        self.is_trading_enabled = True
        self.last_execution_time = None
        self.execution_count = 0
        self.error_count = 0
        
        # Strategy management
        self.strategies = {}
        self.strategy_weights = {}
        self._initialize_strategies()
        
        # Performance tracking
        self.daily_pnl = 0.0
        self.total_trades_today = 0
        self.successful_trades_today = 0
        
        # Threading
        self.main_thread = None
        self.stop_event = threading.Event()
        
    def _initialize_strategies(self):
        """Initialize all trading strategies"""
        try:
            # Initialize strategies
            self.strategies = {
                'sentiment': AdvancedSentimentStrategy(),
                'arbitrage': StatisticalArbitrageStrategy()
            }
            
            # Set strategy weights (how much to allocate to each strategy)
            self.strategy_weights = {
                'sentiment': 0.6,
                'arbitrage': 0.4
            }
            
            self.logger.info(f"Initialized {len(self.strategies)} trading strategies")
            
        except Exception as e:
            self.logger.error(f"Error initializing strategies: {e}")
            self.strategies = {}
            
    def start(self):
        """Start the trading engine"""
        if self.is_running:
            self.logger.warning("Trading engine is already running")
            return
            
        try:
            self.is_running = True
            self.stop_event.clear()
            
            # Start main trading loop in separate thread
            self.main_thread = threading.Thread(target=self._main_loop, daemon=True)
            self.main_thread.start()
            
            self.logger.info("Trading engine started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting trading engine: {e}")
            self.is_running = False
            
    def stop(self):
        """Stop the trading engine"""
        if not self.is_running:
            self.logger.warning("Trading engine is not running")
            return
            
        try:
            self.logger.info("Stopping trading engine...")
            self.is_running = False
            self.stop_event.set()
            
            # Wait for main thread to finish
            if self.main_thread and self.main_thread.is_alive():
                self.main_thread.join(timeout=10)
                
            self.logger.info("Trading engine stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping trading engine: {e}")
            
    def _main_loop(self):
        """Main trading loop"""
        self.logger.info("Starting main trading loop")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                # Execute trading cycle
                self._execute_trading_cycle()
                
                # Update performance metrics
                self._update_performance_metrics()
                
                # Sleep until next execution
                sleep_time = self.trading_config.trade_interval_seconds
                if self.stop_event.wait(timeout=sleep_time):
                    break
                    
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Error in main trading loop: {e}", exc_info=True)
                
                # Sleep before retrying
                if self.stop_event.wait(timeout=60):
                    break
                    
        self.logger.info("Main trading loop ended")
        
    def _execute_trading_cycle(self):
        """Execute one complete trading cycle"""
        try:
            self.logger.debug("Starting trading cycle")
            
            # Check if trading is enabled
            if not self.is_trading_enabled:
                self.logger.debug("Trading is disabled, skipping cycle")
                return
                
            # Sync market data
            if not kalshi_client.sync_market_data():
                self.logger.warning("Failed to sync market data")
                return
                
            # Get current market data
            market_data = kalshi_client.get_markets(status='active', limit=100)
            if not market_data or 'markets' not in market_data:
                self.logger.warning("No market data available")
                return
                
            # Check risk limits before trading
            risk_level = risk_manager.update_risk_level()
            if risk_level == 'CRITICAL':
                self.logger.warning("Risk level is CRITICAL, suspending trading")
                return
                
            # Execute strategies
            all_signals = self._execute_strategies(market_data)
            
            # Filter and prioritize signals
            filtered_signals = self._filter_signals(all_signals)
            
            # Execute trades
            executed_trades = self._execute_trades(filtered_signals)
            
            # Update execution statistics
            self.last_execution_time = datetime.now(timezone.utc)
            self.execution_count += 1
            self.total_trades_today += len(executed_trades)
            
            self.logger.info(
                f"Trading cycle completed: {len(all_signals)} signals generated, "
                f"{len(filtered_signals)} signals filtered, {len(executed_trades)} trades executed"
            )
            
        except Exception as e:
            self.logger.error(f"Error in trading cycle: {e}", exc_info=True)
            
    def _execute_strategies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all enabled strategies and collect signals"""
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                if not strategy.enabled:
                    continue
                    
                self.logger.debug(f"Executing strategy: {strategy_name}")
                
                # Execute strategy
                signals = strategy.execute(market_data)
                
                # Add strategy weight to signals
                for signal in signals:
                    signal['strategy_weight'] = self.strategy_weights.get(strategy_name, 1.0)
                    
                all_signals.extend(signals)
                
                self.logger.debug(f"Strategy {strategy_name} generated {len(signals)} signals")
                
            except Exception as e:
                self.logger.error(f"Error executing strategy {strategy_name}: {e}")
                continue
                
        return all_signals
        
    def _filter_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and prioritize trading signals"""
        if not signals:
            return []
            
        try:
            filtered_signals = []
            
            for signal in signals:
                try:
                    # Check basic signal validity
                    if not self._is_valid_signal(signal):
                        continue
                        
                    # Check risk limits
                    market_id = signal['market_id']
                    position_size = signal.get('position_size_percentage', 0.05) * self.trading_config.bankroll
                    
                    risk_check = risk_manager.check_position_limits(market_id, position_size)
                    if not risk_check['allowed']:
                        self.logger.debug(f"Signal for {market_id} rejected due to risk limits")
                        continue
                        
                    # Adjust position size if recommended
                    if risk_check['recommended_size'] != position_size:
                        signal['position_size_percentage'] = risk_check['recommended_size'] / self.trading_config.bankroll
                        
                    # Check for duplicate signals
                    if not self._is_duplicate_signal(signal, filtered_signals):
                        filtered_signals.append(signal)
                        
                except Exception as e:
                    self.logger.error(f"Error filtering signal: {e}")
                    continue
                    
            # Sort by confidence and strategy weight
            filtered_signals.sort(
                key=lambda s: s['confidence_score'] * s.get('strategy_weight', 1.0),
                reverse=True
            )
            
            # Limit number of signals per cycle
            max_signals = 5  # Maximum signals to execute per cycle
            filtered_signals = filtered_signals[:max_signals]
            
            return filtered_signals
            
        except Exception as e:
            self.logger.error(f"Error filtering signals: {e}")
            return []
            
    def _is_valid_signal(self, signal: Dict[str, Any]) -> bool:
        """Check if signal is valid for execution"""
        try:
            # Check required fields
            required_fields = ['market_id', 'signal_type', 'confidence_score']
            for field in required_fields:
                if field not in signal:
                    return False
                    
            # Check confidence threshold
            if signal['confidence_score'] < self.trading_config.min_confidence_threshold:
                return False
                
            # Check signal type
            if signal['signal_type'] not in ['buy', 'sell']:
                return False
                
            # Check market exists and is active
            market = db_manager.get_market(signal['market_id'])
            if not market or market.status != 'active':
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating signal: {e}")
            return False
            
    def _is_duplicate_signal(self, signal: Dict[str, Any], existing_signals: List[Dict[str, Any]]) -> bool:
        """Check if signal is duplicate of existing signals"""
        market_id = signal['market_id']
        signal_type = signal['signal_type']
        
        for existing in existing_signals:
            if (existing['market_id'] == market_id and 
                existing['signal_type'] == signal_type):
                return True
                
        return False
        
    def _execute_trades(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute trades based on filtered signals"""
        executed_trades = []
        
        for signal in signals:
            try:
                trade_result = self._execute_single_trade(signal)
                if trade_result:
                    executed_trades.append(trade_result)
                    
            except Exception as e:
                self.logger.error(f"Error executing trade for signal {signal}: {e}")
                continue
                
        return executed_trades
        
    def _execute_single_trade(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a single trade based on signal"""
        try:
            market_id = signal['market_id']
            action = signal['signal_type']
            confidence = signal['confidence_score']
            
            # Calculate position size
            position_size_pct = signal.get('position_size_percentage', 0.05)
            position_value = position_size_pct * self.trading_config.bankroll
            
            # Get current market price
            market_data = kalshi_client.get_market(market_id)
            if not market_data:
                self.logger.error(f"Could not get market data for {market_id}")
                return None
                
            # Determine price and quantity
            if action == 'buy':
                price = market_data.get('yes_price', 0.5)
                side = 'yes'
            else:
                price = market_data.get('no_price', 0.5)
                side = 'no'
                
            if price <= 0 or price >= 1:
                self.logger.error(f"Invalid price for {market_id}: {price}")
                return None
                
            # Calculate quantity
            quantity = int(position_value / price)
            if quantity <= 0:
                self.logger.warning(f"Calculated quantity is 0 for {market_id}")
                return None
                
            # Record signal in database
            signal_data = {
                'market_id': market_id,
                'strategy_name': signal['strategy_name'],
                'signal_type': action,
                'confidence_score': confidence,
                'reasoning': signal.get('reasoning', ''),
                'features': signal.get('features', {}),
                'generated_at': signal.get('generated_at', datetime.now(timezone.utc))
            }
            
            db_signal = db_manager.record_trading_signal(signal_data)
            
            # Execute order (in simulation mode for now)
            if self._is_simulation_mode():
                # Simulate trade execution
                trade_result = self._simulate_trade_execution(
                    market_id, action, quantity, price, signal['strategy_name'], confidence
                )
            else:
                # Execute real trade
                order_result = kalshi_client.place_order(
                    market_id=market_id,
                    side=side,
                    quantity=quantity,
                    order_type='market'
                )
                
                if order_result:
                    trade_result = self._process_order_result(order_result, signal)
                else:
                    self.logger.error(f"Failed to place order for {market_id}")
                    return None
                    
            # Mark signal as executed
            if trade_result and db_signal:
                with db_manager.get_session() as session:
                    db_signal.executed = True
                    session.commit()
                    
            return trade_result
            
        except Exception as e:
            self.logger.error(f"Error executing single trade: {e}")
            return None
            
    def _is_simulation_mode(self) -> bool:
        """Check if running in simulation mode"""
        # For now, always run in simulation mode for safety
        return True
        
    def _simulate_trade_execution(self, market_id: str, action: str, quantity: int, 
                                price: float, strategy_name: str, confidence: float) -> Dict[str, Any]:
        """Simulate trade execution for testing"""
        try:
            total_cost = quantity * price
            
            # Record trade in database
            trade_data = {
                'market_id': market_id,
                'strategy_name': strategy_name,
                'action': action,
                'quantity': quantity,
                'price': price,
                'total_cost': total_cost,
                'confidence_score': confidence,
                'executed_at': datetime.now(timezone.utc)
            }
            
            trade = db_manager.record_trade(trade_data)
            
            # Update position
            position_quantity = quantity if action == 'buy' else -quantity
            db_manager.update_position(market_id, position_quantity, price)
            
            self.logger.info(
                f"Simulated trade executed: {action} {quantity} of {market_id} "
                f"at {price:.3f} (total: ${total_cost:.2f})"
            )
            
            return {
                'trade_id': trade.id,
                'market_id': market_id,
                'action': action,
                'quantity': quantity,
                'price': price,
                'total_cost': total_cost,
                'strategy_name': strategy_name,
                'confidence': confidence,
                'simulated': True
            }
            
        except Exception as e:
            self.logger.error(f"Error simulating trade execution: {e}")
            return None
            
    def _process_order_result(self, order_result: Dict[str, Any], signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process real order execution result"""
        # This would handle real order results from Kalshi API
        # Implementation depends on actual API response format
        pass
        
    def _update_performance_metrics(self):
        """Update daily performance metrics"""
        try:
            # Calculate current portfolio value
            positions = db_manager.get_active_positions()
            total_value = self.trading_config.bankroll
            
            for position in positions:
                if position.current_value:
                    total_value += position.unrealized_pnl or 0
                    
            # Calculate daily P&L
            today = datetime.now(timezone.utc).date()
            yesterday_metrics = db_manager.get_performance_history(days=1)
            
            if yesterday_metrics:
                yesterday_value = yesterday_metrics[0].total_value
                self.daily_pnl = total_value - yesterday_value
            else:
                self.daily_pnl = total_value - self.trading_config.bankroll
                
            # Record performance metrics
            metrics_data = {
                'date': datetime.now(timezone.utc),
                'total_value': total_value,
                'daily_pnl': self.daily_pnl,
                'total_pnl': total_value - self.trading_config.bankroll,
                'total_trades': self.total_trades_today,
                'successful_trades': self.successful_trades_today
            }
            
            db_manager.record_performance_metrics(metrics_data)
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
            
    def enable_trading(self):
        """Enable trading"""
        self.is_trading_enabled = True
        self.logger.info("Trading enabled")
        
    def disable_trading(self):
        """Disable trading"""
        self.is_trading_enabled = False
        self.logger.info("Trading disabled")
        
    def enable_strategy(self, strategy_name: str):
        """Enable specific strategy"""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].enable()
            self.logger.info(f"Strategy {strategy_name} enabled")
        else:
            self.logger.warning(f"Unknown strategy: {strategy_name}")
            
    def disable_strategy(self, strategy_name: str):
        """Disable specific strategy"""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].disable()
            self.logger.info(f"Strategy {strategy_name} disabled")
        else:
            self.logger.warning(f"Unknown strategy: {strategy_name}")
            
    def get_status(self) -> Dict[str, Any]:
        """Get trading engine status"""
        try:
            strategy_status = {
                name: strategy.get_status() 
                for name, strategy in self.strategies.items()
            }
            
            return {
                'is_running': self.is_running,
                'is_trading_enabled': self.is_trading_enabled,
                'last_execution_time': self.last_execution_time.isoformat() if self.last_execution_time else None,
                'execution_count': self.execution_count,
                'error_count': self.error_count,
                'daily_pnl': self.daily_pnl,
                'total_trades_today': self.total_trades_today,
                'successful_trades_today': self.successful_trades_today,
                'strategies': strategy_status,
                'risk_level': risk_manager.current_risk_level
            }
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {'error': str(e)}
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        try:
            # Get recent performance data
            performance_history = db_manager.get_performance_history(days=30)
            
            if not performance_history:
                return {'error': 'No performance data available'}
                
            # Calculate summary metrics
            total_pnl = performance_history[0].total_pnl if performance_history else 0
            daily_pnls = [pm.daily_pnl for pm in performance_history if pm.daily_pnl is not None]
            
            summary = {
                'total_pnl': total_pnl,
                'total_return_pct': (total_pnl / self.trading_config.bankroll) * 100,
                'daily_avg_pnl': sum(daily_pnls) / len(daily_pnls) if daily_pnls else 0,
                'daily_pnl_std': np.std(daily_pnls) if len(daily_pnls) > 1 else 0,
                'best_day': max(daily_pnls) if daily_pnls else 0,
                'worst_day': min(daily_pnls) if daily_pnls else 0,
                'trading_days': len(daily_pnls),
                'positive_days': len([pnl for pnl in daily_pnls if pnl > 0]),
                'win_rate': len([pnl for pnl in daily_pnls if pnl > 0]) / len(daily_pnls) if daily_pnls else 0
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}

# Global trading engine instance
trading_engine = TradingEngine()

# Convenience functions
def start_trading():
    """Start the trading engine"""
    trading_engine.start()

def stop_trading():
    """Stop the trading engine"""
    trading_engine.stop()

def get_trading_status() -> Dict[str, Any]:
    """Get trading engine status"""
    return trading_engine.get_status()

def enable_trading():
    """Enable trading"""
    trading_engine.enable_trading()

def disable_trading():
    """Disable trading"""
    trading_engine.disable_trading()

