"""
Enhanced Kalshi API Client for Trading Bot

This module provides a comprehensive interface to the Kalshi API with
advanced features like rate limiting, caching, error handling, and retry logic.
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..core.config import get_api_config
from ..core.database import db_manager

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                
        # Record this request
        self.requests.append(now)

class KalshiAPIClient:
    """
    Enhanced Kalshi API client with comprehensive features for trading bot operations.
    """
    
    def __init__(self):
        self.config = get_api_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.kalshi_api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'KalshiTradingBot/2.0'
        })
        
        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=self.config.rate_limit_requests_per_minute,
            time_window=60
        )
        
        # Cache for market data
        self.market_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Authentication status
        self.authenticated = False
        self.auth_expires = None
        
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, use_cache: bool = True) -> Optional[Dict]:
        """
        Make authenticated API request with rate limiting and error handling.
        """
        # Check cache first for GET requests
        if method.upper() == 'GET' and use_cache:
            cache_key = f"{endpoint}_{json.dumps(params or {}, sort_keys=True)}"
            if cache_key in self.market_cache:
                cached_data, timestamp = self.market_cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_data
                    
        # Apply rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Ensure authentication
        if not self._ensure_authenticated():
            self.logger.error("Failed to authenticate with Kalshi API")
            return None
            
        url = f"{self.config.kalshi_api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.timeout_seconds
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                self.logger.warning(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, data, use_cache)
                
            response.raise_for_status()
            result = response.json()
            
            # Cache GET requests
            if method.upper() == 'GET' and use_cache:
                cache_key = f"{endpoint}_{json.dumps(params or {}, sort_keys=True)}"
                self.market_cache[cache_key] = (result, time.time())
                
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {method} {url} - {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode API response: {e}")
            return None
            
    def _ensure_authenticated(self) -> bool:
        """Ensure API authentication is valid"""
        if self.authenticated and self.auth_expires and datetime.now(timezone.utc) < self.auth_expires:
            return True
            
        return self._authenticate()
        
    def _authenticate(self) -> bool:
        """Authenticate with Kalshi API"""
        try:
            # For Kalshi API, authentication is typically done via API key in headers
            # Test authentication by making a simple request
            response = self._make_request('GET', '/markets', use_cache=False)
            
            if response is not None:
                self.authenticated = True
                self.auth_expires = datetime.now(timezone.utc) + timedelta(hours=1)
                self.logger.info("Successfully authenticated with Kalshi API")
                return True
            else:
                self.logger.error("Authentication failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
            
    def get_markets(self, status: Optional[str] = None, category: Optional[str] = None,
                   limit: int = 100, cursor: Optional[str] = None) -> Optional[Dict]:
        """
        Get list of markets with optional filtering.
        
        Args:
            status: Market status filter ('active', 'closed', etc.)
            category: Market category filter
            limit: Maximum number of markets to return
            cursor: Pagination cursor
            
        Returns:
            Dictionary containing markets data
        """
        params = {'limit': limit}
        if status:
            params['status'] = status
        if category:
            params['category'] = category
        if cursor:
            params['cursor'] = cursor
            
        return self._make_request('GET', '/markets', params=params)
        
    def get_market(self, market_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific market.
        
        Args:
            market_id: Market identifier
            
        Returns:
            Dictionary containing market data
        """
        return self._make_request('GET', f'/markets/{market_id}')
        
    def get_market_orderbook(self, market_id: str, depth: int = 10) -> Optional[Dict]:
        """
        Get market orderbook data.
        
        Args:
            market_id: Market identifier
            depth: Number of price levels to return
            
        Returns:
            Dictionary containing orderbook data
        """
        params = {'depth': depth}
        return self._make_request('GET', f'/markets/{market_id}/orderbook', params=params)
        
    def get_market_history(self, market_id: str, start_ts: Optional[int] = None,
                          end_ts: Optional[int] = None, limit: int = 100) -> Optional[Dict]:
        """
        Get market price history.
        
        Args:
            market_id: Market identifier
            start_ts: Start timestamp (Unix timestamp)
            end_ts: End timestamp (Unix timestamp)
            limit: Maximum number of records
            
        Returns:
            Dictionary containing price history
        """
        params = {'limit': limit}
        if start_ts:
            params['start_ts'] = start_ts
        if end_ts:
            params['end_ts'] = end_ts
            
        return self._make_request('GET', f'/markets/{market_id}/history', params=params)
        
    def get_portfolio(self) -> Optional[Dict]:
        """
        Get current portfolio information.
        
        Returns:
            Dictionary containing portfolio data
        """
        return self._make_request('GET', '/portfolio')
        
    def get_positions(self, market_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get current positions.
        
        Args:
            market_id: Optional market filter
            
        Returns:
            Dictionary containing positions data
        """
        params = {}
        if market_id:
            params['market_id'] = market_id
            
        return self._make_request('GET', '/portfolio/positions', params=params)
        
    def get_orders(self, market_id: Optional[str] = None, status: Optional[str] = None) -> Optional[Dict]:
        """
        Get order history.
        
        Args:
            market_id: Optional market filter
            status: Optional status filter ('open', 'filled', 'cancelled')
            
        Returns:
            Dictionary containing orders data
        """
        params = {}
        if market_id:
            params['market_id'] = market_id
        if status:
            params['status'] = status
            
        return self._make_request('GET', '/portfolio/orders', params=params)
        
    def place_order(self, market_id: str, side: str, quantity: int, 
                   price: Optional[float] = None, order_type: str = 'market') -> Optional[Dict]:
        """
        Place a trading order.
        
        Args:
            market_id: Market identifier
            side: 'yes' or 'no'
            quantity: Number of contracts
            price: Limit price (for limit orders)
            order_type: 'market' or 'limit'
            
        Returns:
            Dictionary containing order confirmation
        """
        order_data = {
            'market_id': market_id,
            'side': side,
            'quantity': quantity,
            'type': order_type
        }
        
        if order_type == 'limit' and price is not None:
            order_data['price'] = price
            
        return self._make_request('POST', '/portfolio/orders', data=order_data, use_cache=False)
        
    def cancel_order(self, order_id: str) -> Optional[Dict]:
        """
        Cancel an existing order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Dictionary containing cancellation confirmation
        """
        return self._make_request('DELETE', f'/portfolio/orders/{order_id}', use_cache=False)
        
    def get_balance(self) -> Optional[Dict]:
        """
        Get account balance information.
        
        Returns:
            Dictionary containing balance data
        """
        return self._make_request('GET', '/portfolio/balance')
        
    def get_fills(self, market_id: Optional[str] = None, limit: int = 100) -> Optional[Dict]:
        """
        Get trade fills (executed orders).
        
        Args:
            market_id: Optional market filter
            limit: Maximum number of fills to return
            
        Returns:
            Dictionary containing fills data
        """
        params = {'limit': limit}
        if market_id:
            params['market_id'] = market_id
            
        return self._make_request('GET', '/portfolio/fills', params=params)
        
    def sync_market_data(self) -> bool:
        """
        Synchronize market data with local database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting market data synchronization")
            
            # Get all active markets
            markets_response = self.get_markets(status='active', limit=1000)
            if not markets_response or 'markets' not in markets_response:
                self.logger.error("Failed to fetch markets data")
                return False
                
            markets = markets_response['markets']
            self.logger.info(f"Fetched {len(markets)} active markets")
            
            # Update database
            for market_data in markets:
                try:
                    # Convert API response to database format
                    db_market_data = {
                        'id': market_data['id'],
                        'title': market_data['title'],
                        'subtitle': market_data.get('subtitle'),
                        'category': market_data.get('category'),
                        'status': market_data.get('status'),
                        'yes_price': market_data.get('yes_price'),
                        'no_price': market_data.get('no_price'),
                        'volume': market_data.get('volume'),
                        'open_interest': market_data.get('open_interest'),
                        'close_date': datetime.fromisoformat(market_data['close_date'].replace('Z', '+00:00')) if market_data.get('close_date') else None
                    }
                    
                    # Update market in database
                    db_manager.update_market(db_market_data)
                    
                    # Record price history
                    if db_market_data['yes_price'] is not None and db_market_data['no_price'] is not None:
                        db_manager.record_price_history(
                            market_data['id'],
                            db_market_data['yes_price'],
                            db_market_data['no_price'],
                            db_market_data.get('volume')
                        )
                        
                except Exception as e:
                    self.logger.error(f"Error updating market {market_data.get('id', 'unknown')}: {e}")
                    continue
                    
            self.logger.info("Market data synchronization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Market data synchronization failed: {e}")
            return False
            
    def sync_portfolio_data(self) -> bool:
        """
        Synchronize portfolio data with local database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting portfolio data synchronization")
            
            # Get current positions
            positions_response = self.get_positions()
            if positions_response and 'positions' in positions_response:
                for position_data in positions_response['positions']:
                    try:
                        db_manager.update_position(
                            position_data['market_id'],
                            position_data['quantity'],
                            position_data['average_price']
                        )
                    except Exception as e:
                        self.logger.error(f"Error updating position: {e}")
                        
            # Get recent fills and record as trades
            fills_response = self.get_fills(limit=100)
            if fills_response and 'fills' in fills_response:
                for fill_data in fills_response['fills']:
                    try:
                        trade_data = {
                            'market_id': fill_data['market_id'],
                            'strategy_name': 'Manual',  # Assume manual trades for API fills
                            'action': 'buy' if fill_data['side'] == 'yes' else 'sell',
                            'quantity': fill_data['quantity'],
                            'price': fill_data['price'],
                            'total_cost': fill_data['quantity'] * fill_data['price'],
                            'executed_at': datetime.fromisoformat(fill_data['created_at'].replace('Z', '+00:00'))
                        }
                        
                        # Check if trade already exists (simple duplicate prevention)
                        # In a production system, you'd want more sophisticated duplicate detection
                        db_manager.record_trade(trade_data)
                        
                    except Exception as e:
                        self.logger.error(f"Error recording trade: {e}")
                        
            self.logger.info("Portfolio data synchronization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Portfolio data synchronization failed: {e}")
            return False
            
    def clear_cache(self):
        """Clear the market data cache"""
        self.market_cache.clear()
        self.logger.info("Market data cache cleared")
        
    def get_api_status(self) -> Dict[str, Any]:
        """
        Get API client status information.
        
        Returns:
            Dictionary containing status information
        """
        return {
            'authenticated': self.authenticated,
            'auth_expires': self.auth_expires.isoformat() if self.auth_expires else None,
            'cache_size': len(self.market_cache),
            'rate_limit_requests': len(self.rate_limiter.requests),
            'api_url': self.config.kalshi_api_url
        }

# Global API client instance
kalshi_client = KalshiAPIClient()

# Convenience functions
def get_markets(**kwargs) -> Optional[Dict]:
    """Get markets data"""
    return kalshi_client.get_markets(**kwargs)

def get_market(market_id: str) -> Optional[Dict]:
    """Get specific market data"""
    return kalshi_client.get_market(market_id)

def place_order(market_id: str, side: str, quantity: int, **kwargs) -> Optional[Dict]:
    """Place trading order"""
    return kalshi_client.place_order(market_id, side, quantity, **kwargs)

def sync_data() -> bool:
    """Synchronize all data"""
    market_sync = kalshi_client.sync_market_data()
    portfolio_sync = kalshi_client.sync_portfolio_data()
    return market_sync and portfolio_sync

