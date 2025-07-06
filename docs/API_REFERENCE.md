# Enhanced Kalshi Trading Bot - API Reference

This document provides comprehensive documentation for all API endpoints, data models, and integration patterns available in the Enhanced Kalshi Trading Bot.

## Table of Contents

- [Authentication](#authentication)
- [Core Endpoints](#core-endpoints)
- [Trading Operations](#trading-operations)
- [Strategy Management](#strategy-management)
- [Portfolio Management](#portfolio-management)
- [Market Data](#market-data)
- [Risk Management](#risk-management)
- [Monitoring](#monitoring)
- [WebSocket API](#websocket-api)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [SDK Examples](#sdk-examples)

## Authentication

### Overview
The API uses JWT (JSON Web Tokens) for authentication. All requests to protected endpoints must include a valid JWT token in the Authorization header.

### Obtain Access Token

**Endpoint:** `POST /api/v1/auth/login`

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password"
  }'
```

### Refresh Token

**Endpoint:** `POST /api/v1/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Using Authentication

Include the access token in the Authorization header for all protected endpoints:

```bash
curl -X GET "http://localhost:8000/api/v1/bot/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Core Endpoints

### Health Check

**Endpoint:** `GET /api/v1/health`

**Description:** Check the health status of the application and its dependencies.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "checks": {
    "database": true,
    "kalshi_api": true,
    "redis": true,
    "disk_space": true,
    "memory": true
  },
  "version": "2.0.0"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

### System Information

**Endpoint:** `GET /api/v1/system/info`

**Description:** Get detailed system information and configuration.

**Authentication:** Required

**Response:**
```json
{
  "system": {
    "cpu_count": 4,
    "memory_total": "8GB",
    "disk_space": "50GB",
    "uptime": "2 days, 14:30:25"
  },
  "application": {
    "version": "2.0.0",
    "environment": "production",
    "started_at": "2025-01-13T20:00:00Z",
    "python_version": "3.9.7"
  },
  "trading": {
    "strategies_loaded": 3,
    "models_loaded": 4,
    "last_update": "2025-01-15T10:29:45Z"
  }
}
```

## Trading Operations

### Bot Control

#### Start Trading Bot

**Endpoint:** `POST /api/v1/bot/start`

**Description:** Start the trading bot with specified configuration.

**Authentication:** Required

**Request Body:**
```json
{
  "strategies": ["sentiment_analysis", "statistical_arbitrage"],
  "trading_mode": "live",
  "risk_level": "medium"
}
```

**Response:**
```json
{
  "status": "started",
  "bot_id": "bot_12345",
  "started_at": "2025-01-15T10:30:00Z",
  "strategies": ["sentiment_analysis", "statistical_arbitrage"],
  "message": "Trading bot started successfully"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/bot/start" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "strategies": ["sentiment_analysis"],
    "trading_mode": "live",
    "risk_level": "medium"
  }'
```

#### Stop Trading Bot

**Endpoint:** `POST /api/v1/bot/stop`

**Description:** Stop the trading bot gracefully.

**Authentication:** Required

**Request Body:**
```json
{
  "force": false,
  "close_positions": false
}
```

**Response:**
```json
{
  "status": "stopped",
  "stopped_at": "2025-01-15T10:35:00Z",
  "final_pnl": 1250.75,
  "positions_closed": 3,
  "message": "Trading bot stopped successfully"
}
```

#### Get Bot Status

**Endpoint:** `GET /api/v1/bot/status`

**Description:** Get current status and metrics of the trading bot.

**Authentication:** Required

**Response:**
```json
{
  "status": "running",
  "bot_id": "bot_12345",
  "started_at": "2025-01-15T10:30:00Z",
  "uptime": "00:05:30",
  "trading_enabled": true,
  "strategies": {
    "sentiment_analysis": {
      "status": "active",
      "trades_today": 5,
      "pnl_today": 125.50
    },
    "statistical_arbitrage": {
      "status": "active",
      "trades_today": 2,
      "pnl_today": 89.25
    }
  },
  "performance": {
    "total_pnl": 1250.75,
    "daily_pnl": 214.75,
    "win_rate": 0.785,
    "sharpe_ratio": 1.42
  },
  "risk_metrics": {
    "current_exposure": 0.65,
    "var_95": 450.00,
    "max_drawdown": 0.08
  }
}
```

### Trade Execution

#### Execute Trade

**Endpoint:** `POST /api/v1/trades/execute`

**Description:** Execute a manual trade.

**Authentication:** Required

**Request Body:**
```json
{
  "market_id": "BIDEN-APPROVAL-45",
  "side": "yes",
  "quantity": 100,
  "price": 0.48,
  "order_type": "limit",
  "strategy": "manual"
}
```

**Response:**
```json
{
  "trade_id": "trade_67890",
  "status": "executed",
  "market_id": "BIDEN-APPROVAL-45",
  "side": "yes",
  "quantity": 100,
  "executed_price": 0.48,
  "executed_at": "2025-01-15T10:30:15Z",
  "fees": 2.40,
  "total_cost": 50.40
}
```

#### Cancel Trade

**Endpoint:** `DELETE /api/v1/trades/{trade_id}`

**Description:** Cancel a pending trade order.

**Authentication:** Required

**Response:**
```json
{
  "trade_id": "trade_67890",
  "status": "cancelled",
  "cancelled_at": "2025-01-15T10:31:00Z",
  "message": "Trade cancelled successfully"
}
```

### Trade History

#### Get Trade History

**Endpoint:** `GET /api/v1/trades`

**Description:** Retrieve trade history with filtering options.

**Authentication:** Required

**Query Parameters:**
- `limit` (integer): Number of trades to return (default: 50, max: 500)
- `offset` (integer): Number of trades to skip (default: 0)
- `start_date` (string): Start date filter (ISO 8601 format)
- `end_date` (string): End date filter (ISO 8601 format)
- `strategy` (string): Filter by strategy name
- `market_id` (string): Filter by market ID
- `status` (string): Filter by trade status

**Response:**
```json
{
  "trades": [
    {
      "trade_id": "trade_67890",
      "market_id": "BIDEN-APPROVAL-45",
      "side": "yes",
      "quantity": 100,
      "executed_price": 0.48,
      "executed_at": "2025-01-15T10:30:15Z",
      "strategy": "sentiment_analysis",
      "pnl": 12.50,
      "status": "closed"
    }
  ],
  "total_count": 1250,
  "pagination": {
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/v1/trades?limit=10&strategy=sentiment_analysis" \
  -H "Authorization: Bearer <token>"
```

## Strategy Management

### List Strategies

**Endpoint:** `GET /api/v1/strategies`

**Description:** Get list of available trading strategies.

**Authentication:** Required

**Response:**
```json
{
  "strategies": [
    {
      "id": "sentiment_analysis",
      "name": "Sentiment Analysis Strategy",
      "description": "AI-powered sentiment analysis using multiple NLP models",
      "status": "active",
      "performance": {
        "total_trades": 150,
        "win_rate": 0.78,
        "total_pnl": 850.25,
        "sharpe_ratio": 1.35
      },
      "configuration": {
        "confidence_threshold": 0.7,
        "sentiment_threshold": 0.6,
        "max_position_size": 0.10
      }
    },
    {
      "id": "statistical_arbitrage",
      "name": "Statistical Arbitrage Strategy",
      "description": "Identifies pricing inefficiencies between correlated markets",
      "status": "active",
      "performance": {
        "total_trades": 89,
        "win_rate": 0.82,
        "total_pnl": 425.50,
        "sharpe_ratio": 1.58
      },
      "configuration": {
        "min_correlation": 0.7,
        "zscore_threshold": 2.0,
        "lookback_days": 30
      }
    }
  ]
}
```

### Get Strategy Details

**Endpoint:** `GET /api/v1/strategies/{strategy_id}`

**Description:** Get detailed information about a specific strategy.

**Authentication:** Required

**Response:**
```json
{
  "id": "sentiment_analysis",
  "name": "Sentiment Analysis Strategy",
  "description": "AI-powered sentiment analysis using multiple NLP models",
  "status": "active",
  "created_at": "2025-01-01T00:00:00Z",
  "last_updated": "2025-01-15T09:00:00Z",
  "configuration": {
    "models": ["bert", "roberta", "finbert"],
    "confidence_threshold": 0.7,
    "sentiment_threshold": 0.6,
    "momentum_window": 6,
    "volume_threshold": 1.5,
    "max_correlation": 0.8,
    "max_position_size": 0.10
  },
  "performance": {
    "total_trades": 150,
    "winning_trades": 117,
    "losing_trades": 33,
    "win_rate": 0.78,
    "total_pnl": 850.25,
    "average_trade_pnl": 5.67,
    "max_win": 45.80,
    "max_loss": -28.30,
    "sharpe_ratio": 1.35,
    "max_drawdown": 0.12
  },
  "recent_signals": [
    {
      "timestamp": "2025-01-15T10:25:00Z",
      "market_id": "BIDEN-APPROVAL-45",
      "signal_strength": 0.85,
      "sentiment_score": 0.72,
      "confidence": 0.89,
      "action": "buy"
    }
  ]
}
```

### Update Strategy Configuration

**Endpoint:** `PUT /api/v1/strategies/{strategy_id}/config`

**Description:** Update strategy configuration parameters.

**Authentication:** Required

**Request Body:**
```json
{
  "confidence_threshold": 0.75,
  "sentiment_threshold": 0.65,
  "max_position_size": 0.08
}
```

**Response:**
```json
{
  "strategy_id": "sentiment_analysis",
  "updated_at": "2025-01-15T10:35:00Z",
  "configuration": {
    "models": ["bert", "roberta", "finbert"],
    "confidence_threshold": 0.75,
    "sentiment_threshold": 0.65,
    "momentum_window": 6,
    "volume_threshold": 1.5,
    "max_correlation": 0.8,
    "max_position_size": 0.08
  },
  "message": "Strategy configuration updated successfully"
}
```

### Enable/Disable Strategy

**Endpoint:** `POST /api/v1/strategies/{strategy_id}/toggle`

**Description:** Enable or disable a trading strategy.

**Authentication:** Required

**Request Body:**
```json
{
  "enabled": false
}
```

**Response:**
```json
{
  "strategy_id": "sentiment_analysis",
  "status": "disabled",
  "updated_at": "2025-01-15T10:35:00Z",
  "message": "Strategy disabled successfully"
}
```

## Portfolio Management

### Get Portfolio Summary

**Endpoint:** `GET /api/v1/portfolio`

**Description:** Get comprehensive portfolio overview.

**Authentication:** Required

**Response:**
```json
{
  "summary": {
    "total_value": 12450.75,
    "cash_balance": 8320.25,
    "invested_amount": 4130.50,
    "total_pnl": 1680.75,
    "daily_pnl": 520.25,
    "unrealized_pnl": 285.50,
    "realized_pnl": 1395.25
  },
  "performance": {
    "total_return": 0.156,
    "daily_return": 0.045,
    "win_rate": 0.785,
    "sharpe_ratio": 1.42,
    "max_drawdown": 0.08,
    "volatility": 0.18
  },
  "allocation": {
    "by_strategy": {
      "sentiment_analysis": 0.65,
      "statistical_arbitrage": 0.35
    },
    "by_category": {
      "politics": 0.45,
      "economics": 0.30,
      "stocks": 0.25
    }
  },
  "risk_metrics": {
    "var_95": 450.00,
    "expected_shortfall": 620.00,
    "beta": 0.85,
    "correlation_risk": 0.25
  }
}
```

### Get Current Positions

**Endpoint:** `GET /api/v1/portfolio/positions`

**Description:** Get all current open positions.

**Authentication:** Required

**Query Parameters:**
- `status` (string): Filter by position status (open, closed, all)
- `strategy` (string): Filter by strategy
- `market_category` (string): Filter by market category

**Response:**
```json
{
  "positions": [
    {
      "position_id": "pos_12345",
      "market_id": "BIDEN-APPROVAL-45",
      "market_title": "Biden Approval Rating > 45%",
      "side": "yes",
      "quantity": 100,
      "average_price": 0.42,
      "current_price": 0.48,
      "market_value": 48.00,
      "cost_basis": 42.00,
      "unrealized_pnl": 6.00,
      "unrealized_pnl_percent": 0.143,
      "strategy": "sentiment_analysis",
      "opened_at": "2025-01-13T14:30:00Z",
      "time_held": "2 days, 20:00:00"
    }
  ],
  "summary": {
    "total_positions": 8,
    "total_market_value": 4130.50,
    "total_cost_basis": 3845.00,
    "total_unrealized_pnl": 285.50
  }
}
```

### Get Position Details

**Endpoint:** `GET /api/v1/portfolio/positions/{position_id}`

**Description:** Get detailed information about a specific position.

**Authentication:** Required

**Response:**
```json
{
  "position_id": "pos_12345",
  "market_id": "BIDEN-APPROVAL-45",
  "market_title": "Biden Approval Rating > 45%",
  "market_category": "politics",
  "side": "yes",
  "quantity": 100,
  "average_price": 0.42,
  "current_price": 0.48,
  "market_value": 48.00,
  "cost_basis": 42.00,
  "unrealized_pnl": 6.00,
  "unrealized_pnl_percent": 0.143,
  "strategy": "sentiment_analysis",
  "opened_at": "2025-01-13T14:30:00Z",
  "time_held": "2 days, 20:00:00",
  "trades": [
    {
      "trade_id": "trade_67890",
      "quantity": 100,
      "price": 0.42,
      "executed_at": "2025-01-13T14:30:00Z",
      "fees": 2.10
    }
  ],
  "risk_metrics": {
    "position_size_percent": 0.034,
    "correlation_with_portfolio": 0.15,
    "var_contribution": 25.50
  }
}
```

### Close Position

**Endpoint:** `POST /api/v1/portfolio/positions/{position_id}/close`

**Description:** Close a specific position.

**Authentication:** Required

**Request Body:**
```json
{
  "quantity": 100,
  "order_type": "market"
}
```

**Response:**
```json
{
  "position_id": "pos_12345",
  "trade_id": "trade_67891",
  "status": "closed",
  "quantity_closed": 100,
  "exit_price": 0.48,
  "realized_pnl": 6.00,
  "closed_at": "2025-01-15T10:35:00Z",
  "message": "Position closed successfully"
}
```

## Market Data

### Get Markets

**Endpoint:** `GET /api/v1/markets`

**Description:** Get list of available markets with filtering options.

**Authentication:** Required

**Query Parameters:**
- `category` (string): Filter by market category
- `status` (string): Filter by market status (open, closed, settled)
- `search` (string): Search markets by title
- `limit` (integer): Number of markets to return
- `offset` (integer): Number of markets to skip

**Response:**
```json
{
  "markets": [
    {
      "market_id": "BIDEN-APPROVAL-45",
      "title": "Biden Approval Rating > 45%",
      "category": "politics",
      "status": "open",
      "yes_price": 0.48,
      "no_price": 0.52,
      "volume_24h": 125000,
      "open_interest": 89000,
      "close_date": "2025-02-01T00:00:00Z",
      "last_updated": "2025-01-15T10:30:00Z"
    }
  ],
  "total_count": 1247,
  "pagination": {
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

### Get Market Details

**Endpoint:** `GET /api/v1/markets/{market_id}`

**Description:** Get detailed information about a specific market.

**Authentication:** Required

**Response:**
```json
{
  "market_id": "BIDEN-APPROVAL-45",
  "title": "Biden Approval Rating > 45%",
  "description": "Will President Biden's approval rating be above 45% according to FiveThirtyEight on February 1, 2025?",
  "category": "politics",
  "subcategory": "approval_ratings",
  "status": "open",
  "created_at": "2025-01-01T00:00:00Z",
  "close_date": "2025-02-01T00:00:00Z",
  "settle_date": "2025-02-01T23:59:59Z",
  "pricing": {
    "yes_price": 0.48,
    "no_price": 0.52,
    "spread": 0.04,
    "mid_price": 0.50
  },
  "volume": {
    "total_volume": 2450000,
    "volume_24h": 125000,
    "volume_7d": 680000
  },
  "open_interest": {
    "yes_shares": 45000,
    "no_shares": 44000,
    "total_shares": 89000
  },
  "price_history": [
    {
      "timestamp": "2025-01-15T10:00:00Z",
      "yes_price": 0.47,
      "no_price": 0.53,
      "volume": 5200
    }
  ],
  "related_markets": [
    "BIDEN-APPROVAL-50",
    "BIDEN-APPROVAL-40"
  ]
}
```

### Get Market Price History

**Endpoint:** `GET /api/v1/markets/{market_id}/prices`

**Description:** Get historical price data for a market.

**Authentication:** Required

**Query Parameters:**
- `start_date` (string): Start date for price history
- `end_date` (string): End date for price history
- `interval` (string): Time interval (1m, 5m, 15m, 1h, 1d)
- `limit` (integer): Maximum number of data points

**Response:**
```json
{
  "market_id": "BIDEN-APPROVAL-45",
  "interval": "1h",
  "data": [
    {
      "timestamp": "2025-01-15T10:00:00Z",
      "yes_price": 0.47,
      "no_price": 0.53,
      "volume": 5200,
      "open_interest": 89000
    },
    {
      "timestamp": "2025-01-15T11:00:00Z",
      "yes_price": 0.48,
      "no_price": 0.52,
      "volume": 3800,
      "open_interest": 89500
    }
  ],
  "total_count": 168
}
```

## Risk Management

### Get Risk Metrics

**Endpoint:** `GET /api/v1/risk/metrics`

**Description:** Get comprehensive risk metrics for the portfolio.

**Authentication:** Required

**Response:**
```json
{
  "portfolio_risk": {
    "total_exposure": 0.65,
    "var_95": 450.00,
    "var_99": 680.00,
    "expected_shortfall": 620.00,
    "max_drawdown": 0.08,
    "volatility": 0.18,
    "beta": 0.85
  },
  "position_risk": {
    "largest_position": 0.15,
    "concentration_risk": 0.25,
    "correlation_risk": 0.30,
    "sector_concentration": {
      "politics": 0.45,
      "economics": 0.30,
      "stocks": 0.25
    }
  },
  "strategy_risk": {
    "sentiment_analysis": {
      "exposure": 0.40,
      "var_95": 280.00,
      "max_drawdown": 0.06
    },
    "statistical_arbitrage": {
      "exposure": 0.25,
      "var_95": 170.00,
      "max_drawdown": 0.04
    }
  },
  "limits": {
    "max_portfolio_exposure": 0.80,
    "max_position_size": 0.15,
    "max_sector_concentration": 0.50,
    "max_daily_loss": 500.00
  },
  "alerts": [
    {
      "type": "warning",
      "message": "Portfolio exposure approaching limit (65% of 80%)",
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ]
}
```

### Update Risk Parameters

**Endpoint:** `PUT /api/v1/risk/parameters`

**Description:** Update risk management parameters.

**Authentication:** Required

**Request Body:**
```json
{
  "max_portfolio_exposure": 0.75,
  "max_position_size": 0.12,
  "stop_loss_enabled": true,
  "stop_loss_percentage": 0.15,
  "max_daily_loss": 600.00
}
```

**Response:**
```json
{
  "updated_at": "2025-01-15T10:35:00Z",
  "parameters": {
    "max_portfolio_exposure": 0.75,
    "max_position_size": 0.12,
    "stop_loss_enabled": true,
    "stop_loss_percentage": 0.15,
    "max_daily_loss": 600.00,
    "var_confidence": 0.95,
    "max_drawdown": 0.20
  },
  "message": "Risk parameters updated successfully"
}
```

### Get Risk Alerts

**Endpoint:** `GET /api/v1/risk/alerts`

**Description:** Get current risk alerts and warnings.

**Authentication:** Required

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_123",
      "type": "warning",
      "severity": "medium",
      "message": "Portfolio exposure approaching limit (65% of 80%)",
      "category": "exposure",
      "triggered_at": "2025-01-15T10:30:00Z",
      "acknowledged": false
    },
    {
      "id": "alert_124",
      "type": "info",
      "severity": "low",
      "message": "New correlation detected between BIDEN-APPROVAL-45 and FED-RATE-CUT",
      "category": "correlation",
      "triggered_at": "2025-01-15T09:15:00Z",
      "acknowledged": true
    }
  ],
  "summary": {
    "total_alerts": 2,
    "unacknowledged": 1,
    "by_severity": {
      "high": 0,
      "medium": 1,
      "low": 1
    }
  }
}
```

## Monitoring

### Get Performance Metrics

**Endpoint:** `GET /api/v1/monitoring/performance`

**Description:** Get detailed performance metrics and analytics.

**Authentication:** Required

**Query Parameters:**
- `period` (string): Time period for metrics (1d, 7d, 30d, 90d, 1y, all)
- `strategy` (string): Filter by specific strategy

**Response:**
```json
{
  "period": "30d",
  "summary": {
    "total_return": 0.156,
    "annualized_return": 1.892,
    "volatility": 0.18,
    "sharpe_ratio": 1.42,
    "max_drawdown": 0.08,
    "win_rate": 0.785
  },
  "daily_returns": [
    {
      "date": "2025-01-15",
      "return": 0.045,
      "pnl": 520.25,
      "trades": 7
    }
  ],
  "strategy_performance": {
    "sentiment_analysis": {
      "return": 0.189,
      "sharpe_ratio": 1.35,
      "win_rate": 0.78,
      "trades": 150
    },
    "statistical_arbitrage": {
      "return": 0.112,
      "sharpe_ratio": 1.58,
      "win_rate": 0.82,
      "trades": 89
    }
  },
  "benchmarks": {
    "market_return": 0.089,
    "risk_free_rate": 0.045,
    "alpha": 0.067,
    "beta": 0.85
  }
}
```

### Get System Metrics

**Endpoint:** `GET /api/v1/monitoring/system`

**Description:** Get system performance and resource utilization metrics.

**Authentication:** Required

**Response:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 68.5,
    "disk_usage": 32.1,
    "network_io": {
      "bytes_sent": 1024000,
      "bytes_received": 2048000
    }
  },
  "application": {
    "active_connections": 25,
    "requests_per_minute": 120,
    "response_time_avg": 150,
    "error_rate": 0.002
  },
  "database": {
    "connections": 8,
    "query_time_avg": 25,
    "cache_hit_rate": 0.95,
    "size": "2.5GB"
  },
  "trading": {
    "strategies_running": 2,
    "models_loaded": 4,
    "api_calls_per_minute": 15,
    "last_trade": "2025-01-15T10:25:30Z"
  }
}
```

## WebSocket API

### Connection

**Endpoint:** `ws://localhost:8000/ws`

**Authentication:** Include JWT token as query parameter: `ws://localhost:8000/ws?token=<jwt_token>`

### Message Format

All WebSocket messages follow this format:

```json
{
  "type": "message_type",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {}
}
```

### Subscription Messages

#### Subscribe to Real-time Updates

```json
{
  "type": "subscribe",
  "channels": ["trades", "positions", "market_data", "alerts"]
}
```

#### Unsubscribe from Updates

```json
{
  "type": "unsubscribe",
  "channels": ["market_data"]
}
```

### Real-time Data Messages

#### Trade Execution

```json
{
  "type": "trade_executed",
  "timestamp": "2025-01-15T10:30:15Z",
  "data": {
    "trade_id": "trade_67890",
    "market_id": "BIDEN-APPROVAL-45",
    "side": "yes",
    "quantity": 100,
    "price": 0.48,
    "strategy": "sentiment_analysis",
    "pnl": 12.50
  }
}
```

#### Position Update

```json
{
  "type": "position_updated",
  "timestamp": "2025-01-15T10:30:15Z",
  "data": {
    "position_id": "pos_12345",
    "market_id": "BIDEN-APPROVAL-45",
    "unrealized_pnl": 6.00,
    "current_price": 0.48
  }
}
```

#### Market Data Update

```json
{
  "type": "market_data",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "market_id": "BIDEN-APPROVAL-45",
    "yes_price": 0.48,
    "no_price": 0.52,
    "volume": 1250,
    "change_24h": 0.02
  }
}
```

#### Risk Alert

```json
{
  "type": "risk_alert",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "alert_id": "alert_125",
    "type": "warning",
    "severity": "medium",
    "message": "Position size limit exceeded for BIDEN-APPROVAL-45",
    "category": "position_size"
  }
}
```

## Data Models

### Trade Model

```json
{
  "trade_id": "string",
  "market_id": "string",
  "side": "yes|no",
  "quantity": "integer",
  "price": "number",
  "executed_price": "number",
  "order_type": "market|limit",
  "strategy": "string",
  "status": "pending|executed|cancelled|failed",
  "created_at": "datetime",
  "executed_at": "datetime",
  "fees": "number",
  "pnl": "number"
}
```

### Position Model

```json
{
  "position_id": "string",
  "market_id": "string",
  "side": "yes|no",
  "quantity": "integer",
  "average_price": "number",
  "current_price": "number",
  "market_value": "number",
  "cost_basis": "number",
  "unrealized_pnl": "number",
  "realized_pnl": "number",
  "strategy": "string",
  "opened_at": "datetime",
  "closed_at": "datetime|null",
  "status": "open|closed"
}
```

### Market Model

```json
{
  "market_id": "string",
  "title": "string",
  "description": "string",
  "category": "string",
  "subcategory": "string",
  "status": "open|closed|settled",
  "yes_price": "number",
  "no_price": "number",
  "volume_24h": "integer",
  "open_interest": "integer",
  "created_at": "datetime",
  "close_date": "datetime",
  "settle_date": "datetime"
}
```

### Strategy Model

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "status": "active|inactive",
  "configuration": "object",
  "performance": {
    "total_trades": "integer",
    "win_rate": "number",
    "total_pnl": "number",
    "sharpe_ratio": "number",
    "max_drawdown": "number"
  },
  "created_at": "datetime",
  "last_updated": "datetime"
}
```

## Error Handling

### Error Response Format

All API errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `INSUFFICIENT_BALANCE` | 400 | Insufficient account balance |
| `MARKET_CLOSED` | 400 | Market is closed for trading |
| `INVALID_STRATEGY` | 400 | Strategy not found or invalid |
| `RISK_LIMIT_EXCEEDED` | 400 | Risk management limit exceeded |

### Error Examples

#### Validation Error

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Validation failed",
    "details": {
      "quantity": ["Must be a positive integer"],
      "price": ["Must be between 0.01 and 0.99"]
    },
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

#### Authentication Error

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": "Token has expired",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_12346"
  }
}
```

#### Rate Limit Error

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "details": "Maximum 100 requests per minute allowed",
    "timestamp": "2025-01-15T10:30:00Z",
    "request_id": "req_12347",
    "retry_after": 60
  }
}
```

## Rate Limiting

### Default Limits

| Endpoint Category | Requests per Minute | Burst Limit |
|------------------|-------------------|-------------|
| Authentication | 10 | 20 |
| Trading Operations | 60 | 100 |
| Market Data | 120 | 200 |
| Portfolio | 60 | 100 |
| Strategy Management | 30 | 50 |
| Risk Management | 30 | 50 |
| Monitoring | 120 | 200 |

### Rate Limit Headers

All responses include rate limiting headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642248600
X-RateLimit-Retry-After: 15
```

## SDK Examples

### Python SDK

```python
import requests
from datetime import datetime

class KalshiBotAPI:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.token = self._authenticate(username, password)
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _authenticate(self, username, password):
        response = requests.post(
            f'{self.base_url}/api/v1/auth/login',
            json={'username': username, 'password': password}
        )
        response.raise_for_status()
        return response.json()['access_token']
    
    def start_bot(self, strategies=None, trading_mode='live', risk_level='medium'):
        data = {
            'strategies': strategies or ['sentiment_analysis'],
            'trading_mode': trading_mode,
            'risk_level': risk_level
        }
        response = requests.post(
            f'{self.base_url}/api/v1/bot/start',
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_portfolio(self):
        response = requests.get(
            f'{self.base_url}/api/v1/portfolio',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def execute_trade(self, market_id, side, quantity, price, order_type='limit'):
        data = {
            'market_id': market_id,
            'side': side,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'strategy': 'manual'
        }
        response = requests.post(
            f'{self.base_url}/api/v1/trades/execute',
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

# Usage example
api = KalshiBotAPI('http://localhost:8000', 'admin', 'password')

# Start the bot
result = api.start_bot(strategies=['sentiment_analysis', 'statistical_arbitrage'])
print(f"Bot started: {result['status']}")

# Get portfolio summary
portfolio = api.get_portfolio()
print(f"Total P&L: ${portfolio['summary']['total_pnl']}")

# Execute a manual trade
trade = api.execute_trade(
    market_id='BIDEN-APPROVAL-45',
    side='yes',
    quantity=100,
    price=0.48
)
print(f"Trade executed: {trade['trade_id']}")
```

### JavaScript SDK

```javascript
class KalshiBotAPI {
    constructor(baseUrl, username, password) {
        this.baseUrl = baseUrl;
        this.token = null;
        this.authenticate(username, password);
    }
    
    async authenticate(username, password) {
        const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            throw new Error('Authentication failed');
        }
        
        const data = await response.json();
        this.token = data.access_token;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error.message);
        }
        
        return response.json();
    }
    
    async startBot(strategies = ['sentiment_analysis'], tradingMode = 'live', riskLevel = 'medium') {
        return this.request('/api/v1/bot/start', {
            method: 'POST',
            body: JSON.stringify({
                strategies,
                trading_mode: tradingMode,
                risk_level: riskLevel
            })
        });
    }
    
    async getPortfolio() {
        return this.request('/api/v1/portfolio');
    }
    
    async executeTrade(marketId, side, quantity, price, orderType = 'limit') {
        return this.request('/api/v1/trades/execute', {
            method: 'POST',
            body: JSON.stringify({
                market_id: marketId,
                side,
                quantity,
                price,
                order_type: orderType,
                strategy: 'manual'
            })
        });
    }
    
    // WebSocket connection for real-time updates
    connectWebSocket() {
        const ws = new WebSocket(`ws://localhost:8000/ws?token=${this.token}`);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            // Subscribe to real-time updates
            ws.send(JSON.stringify({
                type: 'subscribe',
                channels: ['trades', 'positions', 'market_data', 'alerts']
            }));
        };
        
        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
        
        return ws;
    }
    
    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'trade_executed':
                console.log('Trade executed:', message.data);
                break;
            case 'position_updated':
                console.log('Position updated:', message.data);
                break;
            case 'market_data':
                console.log('Market data:', message.data);
                break;
            case 'risk_alert':
                console.warn('Risk alert:', message.data);
                break;
        }
    }
}

// Usage example
const api = new KalshiBotAPI('http://localhost:8000', 'admin', 'password');

// Start the bot
api.startBot(['sentiment_analysis', 'statistical_arbitrage'])
    .then(result => console.log('Bot started:', result.status))
    .catch(error => console.error('Error starting bot:', error));

// Get portfolio
api.getPortfolio()
    .then(portfolio => console.log('Total P&L:', portfolio.summary.total_pnl))
    .catch(error => console.error('Error getting portfolio:', error));

// Connect to WebSocket for real-time updates
const ws = api.connectWebSocket();
```

This comprehensive API reference provides detailed documentation for all endpoints, data models, and integration patterns available in the Enhanced Kalshi Trading Bot. The API is designed to be RESTful, well-documented, and easy to integrate with various programming languages and frameworks.

