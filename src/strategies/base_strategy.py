"""
Base Strategy Class for Kalshi Trading Bot

This module provides the base class that all trading strategies must inherit from,
ensuring consistent interface and common functionality.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    
    All strategies must implement the generate_signals method and can optionally
    override other methods for custom behavior.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.enabled = True
        self.last_execution = None
        self.execution_count = 0
        self.error_count = 0
        
    @abstractmethod
    def generate_signals(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on market data.
        
        Args:
            market_data: Dictionary containing market information
            
        Returns:
            List of trading signals, each containing:
            - market_id: Market identifier
            - strategy_name: Name of this strategy
            - signal_type: 'buy', 'sell', or 'hold'
            - confidence_score: Confidence level (0.0 to 1.0)
            - target_price: Suggested execution price
            - position_size_percentage: Suggested position size as percentage of bankroll
            - reasoning: Human-readable explanation
            - features: Dictionary of features used in decision
            - generated_at: Timestamp of signal generation
        """
        pass
        
    def validate_signal(self, signal: Dict[str, Any], market_data: Dict[str, Any]) -> bool:
        """
        Validate a trading signal before execution.
        
        Args:
            signal: Trading signal to validate
            market_data: Current market data
            
        Returns:
            True if signal is valid, False otherwise
        """
        try:
            # Basic validation
            required_fields = [
                'market_id', 'strategy_name', 'signal_type', 
                'confidence_score', 'target_price'
            ]
            
            for field in required_fields:
                if field not in signal:
                    self.logger.warning(f"Signal missing required field: {field}")
                    return False
                    
            # Validate signal type
            if signal['signal_type'] not in ['buy', 'sell', 'hold']:
                self.logger.warning(f"Invalid signal type: {signal['signal_type']}")
                return False
                
            # Validate confidence score
            confidence = signal['confidence_score']
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                self.logger.warning(f"Invalid confidence score: {confidence}")
                return False
                
            # Validate target price
            price = signal['target_price']
            if not isinstance(price, (int, float)) or not 0 <= price <= 1:
                self.logger.warning(f"Invalid target price: {price}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating signal: {e}")
            return False
            
    def preprocess_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess market data before analysis.
        
        Args:
            market_data: Raw market data
            
        Returns:
            Preprocessed market data
        """
        # Default implementation - just return the data as-is
        return market_data
        
    def postprocess_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Postprocess generated signals.
        
        Args:
            signals: List of generated signals
            
        Returns:
            Processed signals
        """
        # Default implementation - add strategy name and timestamp
        for signal in signals:
            signal['strategy_name'] = self.name
            if 'generated_at' not in signal:
                signal['generated_at'] = datetime.now(timezone.utc)
                
        return signals
        
    def execute(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main execution method that orchestrates the strategy.
        
        Args:
            market_data: Market data for analysis
            
        Returns:
            List of validated trading signals
        """
        if not self.enabled:
            self.logger.debug(f"Strategy {self.name} is disabled")
            return []
            
        try:
            self.logger.debug(f"Executing strategy {self.name}")
            
            # Preprocess data
            processed_data = self.preprocess_market_data(market_data)
            
            # Generate signals
            signals = self.generate_signals(processed_data)
            
            # Postprocess signals
            signals = self.postprocess_signals(signals)
            
            # Validate signals
            valid_signals = []
            for signal in signals:
                if self.validate_signal(signal, processed_data):
                    valid_signals.append(signal)
                else:
                    self.logger.warning(f"Invalid signal generated: {signal}")
                    
            # Update execution statistics
            self.last_execution = datetime.now(timezone.utc)
            self.execution_count += 1
            
            self.logger.info(f"Strategy {self.name} generated {len(valid_signals)} valid signals")
            return valid_signals
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error executing strategy {self.name}: {e}", exc_info=True)
            return []
            
    def enable(self):
        """Enable the strategy"""
        self.enabled = True
        self.logger.info(f"Strategy {self.name} enabled")
        
    def disable(self):
        """Disable the strategy"""
        self.enabled = False
        self.logger.info(f"Strategy {self.name} disabled")
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get strategy status information.
        
        Returns:
            Dictionary containing strategy status
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(self.execution_count, 1)
        }
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get strategy performance metrics.
        
        Returns:
            Dictionary containing performance metrics
        """
        # Default implementation - subclasses should override for specific metrics
        return {
            'strategy_name': self.name,
            'execution_count': self.execution_count,
            'error_count': self.error_count,
            'success_rate': max(0, (self.execution_count - self.error_count) / max(self.execution_count, 1))
        }
        
    def reset_statistics(self):
        """Reset strategy statistics"""
        self.execution_count = 0
        self.error_count = 0
        self.last_execution = None
        self.logger.info(f"Statistics reset for strategy {self.name}")
        
    def __str__(self):
        return f"Strategy({self.name}, enabled={self.enabled})"
        
    def __repr__(self):
        return self.__str__()

