"""
Portfolio Risk Management System for Kalshi Trading Bot

This module provides comprehensive risk management including position sizing,
portfolio-level controls, correlation monitoring, and dynamic risk adjustment.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass

from ..core.config import get_trading_config
from ..core.database import db_manager, Position, Trade

logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    """Risk metrics for portfolio analysis"""
    total_exposure: float
    max_position_size: float
    portfolio_correlation: float
    var_95: float  # Value at Risk 95%
    expected_shortfall: float
    sharpe_ratio: float
    max_drawdown: float
    daily_pnl_volatility: float

@dataclass
class PositionRisk:
    """Risk metrics for individual position"""
    market_id: str
    current_value: float
    unrealized_pnl: float
    position_size_percentage: float
    correlation_with_portfolio: float
    var_contribution: float
    risk_score: float

class PortfolioRiskManager:
    """
    Comprehensive portfolio risk management system that monitors and controls
    risk at both position and portfolio levels.
    """
    
    def __init__(self):
        self.config = get_trading_config()
        self.logger = logging.getLogger(__name__)
        
        # Risk parameters
        self.max_portfolio_exposure = 0.8  # Maximum percentage of bankroll at risk
        self.max_single_position = self.config.max_position_size_percentage
        self.max_correlation = self.config.correlation_limit
        self.var_confidence = 0.95
        self.lookback_days = 30
        
        # Risk state
        self.current_risk_level = 'LOW'  # LOW, MEDIUM, HIGH, CRITICAL
        self.risk_budget_used = 0.0
        self.last_risk_assessment = None
        
    def calculate_portfolio_metrics(self) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        try:
            # Get current positions
            positions = db_manager.get_active_positions()
            
            if not positions:
                return RiskMetrics(
                    total_exposure=0.0,
                    max_position_size=0.0,
                    portfolio_correlation=0.0,
                    var_95=0.0,
                    expected_shortfall=0.0,
                    sharpe_ratio=0.0,
                    max_drawdown=0.0,
                    daily_pnl_volatility=0.0
                )
                
            # Calculate total exposure
            total_value = sum(abs(pos.current_value or 0) for pos in positions)
            total_exposure = total_value / self.config.bankroll
            
            # Calculate maximum position size
            max_position_size = max(
                abs(pos.current_value or 0) / self.config.bankroll 
                for pos in positions
            )
            
            # Calculate portfolio correlation
            portfolio_correlation = self._calculate_portfolio_correlation(positions)
            
            # Calculate VaR and Expected Shortfall
            var_95, expected_shortfall = self._calculate_var_and_es(positions)
            
            # Calculate performance metrics
            sharpe_ratio = self._calculate_sharpe_ratio()
            max_drawdown = self._calculate_max_drawdown()
            daily_pnl_volatility = self._calculate_daily_pnl_volatility()
            
            return RiskMetrics(
                total_exposure=total_exposure,
                max_position_size=max_position_size,
                portfolio_correlation=portfolio_correlation,
                var_95=var_95,
                expected_shortfall=expected_shortfall,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                daily_pnl_volatility=daily_pnl_volatility
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0)
            
    def _calculate_portfolio_correlation(self, positions: List[Position]) -> float:
        """Calculate average correlation between portfolio positions"""
        if len(positions) < 2:
            return 0.0
            
        try:
            correlations = []
            
            for i, pos_a in enumerate(positions):
                for pos_b in positions[i+1:]:
                    # Get price history for both positions
                    history_a = db_manager.get_price_history(pos_a.market_id, limit=50)
                    history_b = db_manager.get_price_history(pos_b.market_id, limit=50)
                    
                    if len(history_a) < 10 or len(history_b) < 10:
                        continue
                        
                    # Calculate correlation
                    prices_a = [ph.yes_price for ph in history_a if ph.yes_price is not None]
                    prices_b = [ph.yes_price for ph in history_b if ph.yes_price is not None]
                    
                    if len(prices_a) >= 10 and len(prices_b) >= 10:
                        # Align series length
                        min_length = min(len(prices_a), len(prices_b))
                        correlation = np.corrcoef(prices_a[:min_length], prices_b[:min_length])[0, 1]
                        
                        if not np.isnan(correlation):
                            correlations.append(abs(correlation))
                            
            return np.mean(correlations) if correlations else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio correlation: {e}")
            return 0.0
            
    def _calculate_var_and_es(self, positions: List[Position]) -> Tuple[float, float]:
        """Calculate Value at Risk and Expected Shortfall"""
        try:
            # Get historical P&L data
            pnl_history = self._get_historical_pnl(self.lookback_days)
            
            if len(pnl_history) < 10:
                return 0.0, 0.0
                
            # Calculate VaR at 95% confidence level
            var_95 = np.percentile(pnl_history, (1 - self.var_confidence) * 100)
            
            # Calculate Expected Shortfall (average of losses beyond VaR)
            tail_losses = [pnl for pnl in pnl_history if pnl <= var_95]
            expected_shortfall = np.mean(tail_losses) if tail_losses else 0.0
            
            return abs(var_95), abs(expected_shortfall)
            
        except Exception as e:
            self.logger.error(f"Error calculating VaR and ES: {e}")
            return 0.0, 0.0
            
    def _get_historical_pnl(self, days: int) -> List[float]:
        """Get historical daily P&L data"""
        try:
            # Get performance metrics from database
            performance_history = db_manager.get_performance_history(days)
            
            if not performance_history:
                return []
                
            return [pm.daily_pnl for pm in performance_history if pm.daily_pnl is not None]
            
        except Exception as e:
            self.logger.error(f"Error getting historical P&L: {e}")
            return []
            
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio for the portfolio"""
        try:
            pnl_history = self._get_historical_pnl(self.lookback_days)
            
            if len(pnl_history) < 10:
                return 0.0
                
            # Calculate daily returns as percentage of bankroll
            daily_returns = [pnl / self.config.bankroll for pnl in pnl_history]
            
            # Calculate Sharpe ratio (assuming risk-free rate = 0)
            mean_return = np.mean(daily_returns)
            std_return = np.std(daily_returns)
            
            if std_return == 0:
                return 0.0
                
            # Annualize (assuming 252 trading days)
            sharpe_ratio = (mean_return / std_return) * np.sqrt(252)
            
            return sharpe_ratio
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
            
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        try:
            performance_history = db_manager.get_performance_history(self.lookback_days)
            
            if not performance_history:
                return 0.0
                
            # Get cumulative P&L
            cumulative_pnl = []
            running_total = 0
            
            for pm in sorted(performance_history, key=lambda x: x.date):
                running_total += pm.daily_pnl or 0
                cumulative_pnl.append(running_total)
                
            if not cumulative_pnl:
                return 0.0
                
            # Calculate maximum drawdown
            peak = cumulative_pnl[0]
            max_drawdown = 0
            
            for value in cumulative_pnl:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / self.config.bankroll
                max_drawdown = max(max_drawdown, drawdown)
                
            return max_drawdown
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {e}")
            return 0.0
            
    def _calculate_daily_pnl_volatility(self) -> float:
        """Calculate daily P&L volatility"""
        try:
            pnl_history = self._get_historical_pnl(self.lookback_days)
            
            if len(pnl_history) < 5:
                return 0.0
                
            # Calculate volatility as percentage of bankroll
            pnl_returns = [pnl / self.config.bankroll for pnl in pnl_history]
            volatility = np.std(pnl_returns)
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"Error calculating P&L volatility: {e}")
            return 0.0
            
    def assess_position_risk(self, position: Position) -> PositionRisk:
        """Assess risk metrics for individual position"""
        try:
            # Calculate position value and P&L
            current_value = position.current_value or 0
            unrealized_pnl = position.unrealized_pnl or 0
            position_size_percentage = abs(current_value) / self.config.bankroll
            
            # Calculate correlation with rest of portfolio
            correlation_with_portfolio = self._calculate_position_portfolio_correlation(position)
            
            # Calculate VaR contribution
            var_contribution = self._calculate_position_var_contribution(position)
            
            # Calculate overall risk score
            risk_score = self._calculate_position_risk_score(
                position_size_percentage, correlation_with_portfolio, var_contribution
            )
            
            return PositionRisk(
                market_id=position.market_id,
                current_value=current_value,
                unrealized_pnl=unrealized_pnl,
                position_size_percentage=position_size_percentage,
                correlation_with_portfolio=correlation_with_portfolio,
                var_contribution=var_contribution,
                risk_score=risk_score
            )
            
        except Exception as e:
            self.logger.error(f"Error assessing position risk: {e}")
            return PositionRisk(position.market_id, 0, 0, 0, 0, 0, 0)
            
    def _calculate_position_portfolio_correlation(self, position: Position) -> float:
        """Calculate position's correlation with rest of portfolio"""
        try:
            # Get other positions
            all_positions = db_manager.get_active_positions()
            other_positions = [p for p in all_positions if p.market_id != position.market_id]
            
            if not other_positions:
                return 0.0
                
            # Calculate average correlation with other positions
            correlations = []
            position_history = db_manager.get_price_history(position.market_id, limit=30)
            
            for other_pos in other_positions:
                other_history = db_manager.get_price_history(other_pos.market_id, limit=30)
                
                if len(position_history) < 10 or len(other_history) < 10:
                    continue
                    
                # Calculate correlation
                pos_prices = [ph.yes_price for ph in position_history if ph.yes_price is not None]
                other_prices = [ph.yes_price for ph in other_history if ph.yes_price is not None]
                
                if len(pos_prices) >= 10 and len(other_prices) >= 10:
                    min_length = min(len(pos_prices), len(other_prices))
                    correlation = np.corrcoef(pos_prices[:min_length], other_prices[:min_length])[0, 1]
                    
                    if not np.isnan(correlation):
                        correlations.append(abs(correlation))
                        
            return np.mean(correlations) if correlations else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating position-portfolio correlation: {e}")
            return 0.0
            
    def _calculate_position_var_contribution(self, position: Position) -> float:
        """Calculate position's contribution to portfolio VaR"""
        try:
            # Simplified VaR contribution based on position size and volatility
            position_size = abs(position.current_value or 0) / self.config.bankroll
            
            # Get position price volatility
            price_history = db_manager.get_price_history(position.market_id, limit=30)
            
            if len(price_history) < 10:
                return position_size * 0.1  # Default assumption
                
            prices = [ph.yes_price for ph in price_history if ph.yes_price is not None]
            
            if len(prices) < 10:
                return position_size * 0.1
                
            # Calculate price volatility
            returns = [prices[i] / prices[i+1] - 1 for i in range(len(prices)-1) if prices[i+1] != 0]
            volatility = np.std(returns) if returns else 0.1
            
            # VaR contribution approximation
            var_contribution = position_size * volatility * 2.33  # 99% confidence z-score
            
            return var_contribution
            
        except Exception as e:
            self.logger.error(f"Error calculating position VaR contribution: {e}")
            return 0.0
            
    def _calculate_position_risk_score(self, size_pct: float, correlation: float, var_contrib: float) -> float:
        """Calculate overall risk score for position (0-1 scale)"""
        try:
            # Weighted risk score
            size_risk = min(size_pct / self.max_single_position, 1.0)
            correlation_risk = min(correlation / self.max_correlation, 1.0)
            var_risk = min(var_contrib / 0.05, 1.0)  # 5% VaR threshold
            
            # Weighted average
            risk_score = (size_risk * 0.4 + correlation_risk * 0.3 + var_risk * 0.3)
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating position risk score: {e}")
            return 0.0
            
    def check_position_limits(self, market_id: str, proposed_size: float) -> Dict[str, Any]:
        """Check if proposed position size violates risk limits"""
        try:
            # Get current position
            current_positions = db_manager.get_active_positions()
            current_position = next((p for p in current_positions if p.market_id == market_id), None)
            
            current_size = abs(current_position.current_value or 0) if current_position else 0
            new_total_size = current_size + abs(proposed_size)
            new_size_percentage = new_total_size / self.config.bankroll
            
            violations = []
            
            # Check single position limit
            if new_size_percentage > self.max_single_position:
                violations.append({
                    'type': 'position_size_limit',
                    'current': new_size_percentage,
                    'limit': self.max_single_position,
                    'severity': 'HIGH'
                })
                
            # Check total portfolio exposure
            total_exposure = sum(abs(p.current_value or 0) for p in current_positions) + abs(proposed_size)
            exposure_percentage = total_exposure / self.config.bankroll
            
            if exposure_percentage > self.max_portfolio_exposure:
                violations.append({
                    'type': 'portfolio_exposure_limit',
                    'current': exposure_percentage,
                    'limit': self.max_portfolio_exposure,
                    'severity': 'HIGH'
                })
                
            # Check correlation limits
            if current_positions:
                # Estimate correlation impact (simplified)
                market = db_manager.get_market(market_id)
                if market:
                    similar_positions = [
                        p for p in current_positions 
                        if self._markets_are_correlated(market_id, p.market_id)
                    ]
                    
                    if len(similar_positions) >= 3:  # Too many correlated positions
                        violations.append({
                            'type': 'correlation_limit',
                            'current': len(similar_positions),
                            'limit': 3,
                            'severity': 'MEDIUM'
                        })
                        
            return {
                'allowed': len(violations) == 0,
                'violations': violations,
                'recommended_size': self._calculate_recommended_size(market_id, proposed_size, violations)
            }
            
        except Exception as e:
            self.logger.error(f"Error checking position limits: {e}")
            return {'allowed': False, 'violations': [{'type': 'error', 'message': str(e)}], 'recommended_size': 0}
            
    def _markets_are_correlated(self, market_a: str, market_b: str, threshold: float = 0.5) -> bool:
        """Check if two markets are correlated above threshold"""
        try:
            # Get price history for both markets
            history_a = db_manager.get_price_history(market_a, limit=30)
            history_b = db_manager.get_price_history(market_b, limit=30)
            
            if len(history_a) < 10 or len(history_b) < 10:
                return False
                
            prices_a = [ph.yes_price for ph in history_a if ph.yes_price is not None]
            prices_b = [ph.yes_price for ph in history_b if ph.yes_price is not None]
            
            if len(prices_a) < 10 or len(prices_b) < 10:
                return False
                
            # Calculate correlation
            min_length = min(len(prices_a), len(prices_b))
            correlation = np.corrcoef(prices_a[:min_length], prices_b[:min_length])[0, 1]
            
            return not np.isnan(correlation) and abs(correlation) > threshold
            
        except Exception as e:
            self.logger.debug(f"Error checking market correlation: {e}")
            return False
            
    def _calculate_recommended_size(self, market_id: str, proposed_size: float, violations: List[Dict]) -> float:
        """Calculate recommended position size given violations"""
        if not violations:
            return proposed_size
            
        # Start with proposed size and adjust down for each violation
        recommended_size = abs(proposed_size)
        
        for violation in violations:
            if violation['type'] == 'position_size_limit':
                # Reduce to maximum allowed
                max_allowed = self.max_single_position * self.config.bankroll
                current_position = db_manager.get_active_positions()
                current_size = sum(
                    abs(p.current_value or 0) for p in current_position 
                    if p.market_id == market_id
                )
                recommended_size = min(recommended_size, max_allowed - current_size)
                
            elif violation['type'] == 'portfolio_exposure_limit':
                # Reduce to fit within portfolio limit
                current_total = sum(
                    abs(p.current_value or 0) for p in db_manager.get_active_positions()
                )
                max_portfolio = self.max_portfolio_exposure * self.config.bankroll
                recommended_size = min(recommended_size, max_portfolio - current_total)
                
            elif violation['type'] == 'correlation_limit':
                # Reduce size for correlated positions
                recommended_size *= 0.5
                
        return max(0, recommended_size)
        
    def update_risk_level(self) -> str:
        """Update and return current portfolio risk level"""
        try:
            metrics = self.calculate_portfolio_metrics()
            
            # Determine risk level based on multiple factors
            risk_factors = []
            
            # Exposure risk
            if metrics.total_exposure > 0.7:
                risk_factors.append('HIGH_EXPOSURE')
            elif metrics.total_exposure > 0.5:
                risk_factors.append('MEDIUM_EXPOSURE')
                
            # Concentration risk
            if metrics.max_position_size > 0.15:
                risk_factors.append('HIGH_CONCENTRATION')
            elif metrics.max_position_size > 0.1:
                risk_factors.append('MEDIUM_CONCENTRATION')
                
            # Correlation risk
            if metrics.portfolio_correlation > 0.8:
                risk_factors.append('HIGH_CORRELATION')
            elif metrics.portfolio_correlation > 0.6:
                risk_factors.append('MEDIUM_CORRELATION')
                
            # VaR risk
            if metrics.var_95 > 0.05:  # 5% of bankroll
                risk_factors.append('HIGH_VAR')
            elif metrics.var_95 > 0.03:
                risk_factors.append('MEDIUM_VAR')
                
            # Determine overall risk level
            high_risk_factors = [f for f in risk_factors if f.startswith('HIGH_')]
            medium_risk_factors = [f for f in risk_factors if f.startswith('MEDIUM_')]
            
            if len(high_risk_factors) >= 2:
                self.current_risk_level = 'CRITICAL'
            elif len(high_risk_factors) >= 1:
                self.current_risk_level = 'HIGH'
            elif len(medium_risk_factors) >= 2:
                self.current_risk_level = 'HIGH'
            elif len(medium_risk_factors) >= 1:
                self.current_risk_level = 'MEDIUM'
            else:
                self.current_risk_level = 'LOW'
                
            self.last_risk_assessment = datetime.now(timezone.utc)
            
            return self.current_risk_level
            
        except Exception as e:
            self.logger.error(f"Error updating risk level: {e}")
            self.current_risk_level = 'UNKNOWN'
            return self.current_risk_level
            
    def get_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        try:
            # Calculate portfolio metrics
            portfolio_metrics = self.calculate_portfolio_metrics()
            
            # Get position risks
            positions = db_manager.get_active_positions()
            position_risks = [self.assess_position_risk(pos) for pos in positions]
            
            # Update risk level
            risk_level = self.update_risk_level()
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(portfolio_metrics, position_risks)
            
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'risk_level': risk_level,
                'portfolio_metrics': portfolio_metrics.__dict__,
                'position_count': len(positions),
                'position_risks': [pr.__dict__ for pr in position_risks],
                'top_risk_positions': sorted(
                    [pr.__dict__ for pr in position_risks], 
                    key=lambda x: x['risk_score'], 
                    reverse=True
                )[:5],
                'recommendations': recommendations,
                'risk_budget_used': self.risk_budget_used,
                'limits': {
                    'max_portfolio_exposure': self.max_portfolio_exposure,
                    'max_single_position': self.max_single_position,
                    'max_correlation': self.max_correlation
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating risk report: {e}")
            return {'error': str(e), 'timestamp': datetime.now(timezone.utc).isoformat()}
            
    def _generate_risk_recommendations(self, portfolio_metrics: RiskMetrics, 
                                     position_risks: List[PositionRisk]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        try:
            # Portfolio-level recommendations
            if portfolio_metrics.total_exposure > 0.7:
                recommendations.append("Consider reducing overall portfolio exposure")
                
            if portfolio_metrics.max_position_size > 0.15:
                recommendations.append("Reduce size of largest position to improve diversification")
                
            if portfolio_metrics.portfolio_correlation > 0.7:
                recommendations.append("Portfolio shows high correlation - consider diversifying into uncorrelated markets")
                
            if portfolio_metrics.var_95 > 0.05:
                recommendations.append("Value at Risk is elevated - consider reducing position sizes")
                
            if portfolio_metrics.sharpe_ratio < 0.5:
                recommendations.append("Risk-adjusted returns are low - review strategy performance")
                
            # Position-level recommendations
            high_risk_positions = [pr for pr in position_risks if pr.risk_score > 0.7]
            
            if high_risk_positions:
                recommendations.append(f"Review {len(high_risk_positions)} high-risk positions")
                
            for pos_risk in high_risk_positions[:3]:  # Top 3 risky positions
                if pos_risk.position_size_percentage > 0.12:
                    recommendations.append(f"Consider reducing position size in {pos_risk.market_id}")
                    
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Error generating recommendations"]

# Global risk manager instance
risk_manager = PortfolioRiskManager()

# Convenience functions
def check_position_limits(market_id: str, proposed_size: float) -> Dict[str, Any]:
    """Check position limits for proposed trade"""
    return risk_manager.check_position_limits(market_id, proposed_size)

def get_risk_report() -> Dict[str, Any]:
    """Get comprehensive risk report"""
    return risk_manager.get_risk_report()

def get_current_risk_level() -> str:
    """Get current portfolio risk level"""
    return risk_manager.update_risk_level()

