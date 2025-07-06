# Enhanced Kalshi Trading Bot v2.0

A sophisticated, AI-powered automated trading system for Kalshi prediction markets featuring advanced sentiment analysis, statistical arbitrage strategies, comprehensive risk management, and professional user interfaces.

## 🚀 Features

### Advanced Trading Strategies
- **Multi-Model Sentiment Analysis**: Leverages BERT, RoBERTa, and FinBERT models for comprehensive market sentiment evaluation
- **Statistical Arbitrage**: Identifies pricing inefficiencies between correlated markets using advanced statistical methods
- **Dynamic Risk Management**: Real-time portfolio monitoring with automatic position sizing and stop-loss mechanisms
- **Machine Learning Integration**: Continuous model improvement through backtesting and performance analysis

### Professional User Interfaces
- **Desktop Admin Panel**: Full-featured React-based dashboard for comprehensive bot management
- **Telegram Web App**: Mobile-optimized interface for on-the-go trading and monitoring
- **Real-time Analytics**: Live charts, performance metrics, and market data visualization
- **Responsive Design**: Optimized for both desktop and mobile experiences

### Enterprise-Grade Architecture
- **Modular Design**: Extensible plugin architecture for easy strategy development
- **Comprehensive Logging**: Detailed audit trails and performance monitoring
- **Database Integration**: SQLite with SQLAlchemy ORM for reliable data persistence
- **API-First Design**: RESTful APIs for integration with external systems

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [User Interfaces](#user-interfaces)
- [Trading Strategies](#trading-strategies)
- [Risk Management](#risk-management)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🛠 Installation

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Git
- Kalshi API credentials

### System Requirements

- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Stable internet connection for real-time market data
- **Operating System**: Linux, macOS, or Windows

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/enhanced-kalshi-bot.git
   cd enhanced-kalshi-bot
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js Dependencies**
   ```bash
   # Desktop Admin Panel
   cd desktop_admin_panel
   npm install
   
   # Telegram Web App
   cd ../telegram_webapp
   npm install
   ```

4. **Configure Environment Variables**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your Kalshi API credentials
   ```

5. **Initialize Database**
   ```bash
   python src/core/database.py
   ```

## 🚀 Quick Start

### 1. Start the Trading Engine

```bash
python src/main.py
```

### 2. Launch Desktop Admin Panel

```bash
cd desktop_admin_panel
npm run dev
```

Access the admin panel at `http://localhost:5173`

### 3. Deploy Telegram Web App

```bash
cd telegram_webapp
npm run build
# Deploy to your preferred hosting service
```

### 4. Configure Trading Strategies

1. Open the desktop admin panel
2. Navigate to "Strategies" section
3. Configure sentiment analysis and arbitrage parameters
4. Set risk management limits
5. Enable trading mode

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `config/` directory:

```env
# Kalshi API Configuration
KALSHI_API_KEY=your_api_key_here
KALSHI_API_SECRET=your_api_secret_here
KALSHI_BASE_URL=https://trading-api.kalshi.com/trade-api/v2

# Database Configuration
DATABASE_URL=sqlite:///data/trading_bot.db

# Trading Configuration
MAX_POSITION_SIZE=0.10
RISK_LEVEL=medium
TRADING_INTERVAL=300

# Sentiment Analysis Configuration
SENTIMENT_MODEL_PATH=models/sentiment/
NEWS_API_KEY=your_news_api_key
TWITTER_BEARER_TOKEN=your_twitter_token

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=your_webhook_url

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/trading_bot.log
```

### Strategy Configuration

#### Sentiment Analysis Strategy

```python
SENTIMENT_CONFIG = {
    "models": ["bert", "roberta", "finbert"],
    "confidence_threshold": 0.7,
    "sentiment_threshold": 0.6,
    "momentum_window": 6,
    "volume_threshold": 1.5,
    "max_correlation": 0.8
}
```

#### Statistical Arbitrage Strategy

```python
ARBITRAGE_CONFIG = {
    "min_correlation": 0.7,
    "zscore_threshold": 2.0,
    "lookback_days": 30,
    "min_data_points": 20,
    "max_position_correlation": 0.8
}
```

### Risk Management Configuration

```python
RISK_CONFIG = {
    "max_portfolio_exposure": 0.8,
    "max_position_size": 0.15,
    "stop_loss_enabled": True,
    "stop_loss_percentage": 0.15,
    "max_daily_trades": 50,
    "var_confidence": 0.95,
    "max_drawdown": 0.20
}
```

## 💻 User Interfaces

### Desktop Admin Panel

The desktop admin panel provides comprehensive control over your trading bot with the following features:

#### Dashboard
- Real-time P&L tracking and performance metrics
- Interactive charts showing daily performance trends
- Strategy allocation visualization
- Recent trades and system alerts
- Risk metrics monitoring

#### Trading Control
- Bot start/stop controls
- Trading mode toggle (monitoring vs. active trading)
- Emergency stop functionality
- Real-time status monitoring

#### Strategy Management
- Configure sentiment analysis parameters
- Adjust statistical arbitrage settings
- Monitor strategy performance
- Enable/disable individual strategies

#### Risk Management
- Set position size limits
- Configure stop-loss parameters
- Monitor portfolio exposure
- View correlation analysis

#### Portfolio Overview
- Current positions and P&L
- Trade history and analytics
- Performance attribution
- Risk-adjusted returns

### Telegram Web App

The Telegram web app provides mobile-optimized access to key trading functions:

#### Mobile Dashboard
- Key performance metrics
- Simplified charts and visualizations
- Quick action buttons
- Real-time status updates

#### Trading Controls
- Start/stop bot functionality
- Trading mode toggle
- Emergency controls
- Quick settings access

#### Portfolio Management
- Position overview
- Recent trades
- P&L tracking
- Performance summaries

#### Market Browser
- Trending markets
- New opportunities
- Market search and filtering
- Quick trade execution

## 📈 Trading Strategies

### Sentiment Analysis Strategy

The sentiment analysis strategy uses advanced natural language processing to evaluate market sentiment from multiple sources:

#### Data Sources
- Financial news articles
- Social media posts
- Market commentary
- Regulatory announcements

#### Model Architecture
- **BERT**: General language understanding
- **RoBERTa**: Robust optimized BERT approach
- **FinBERT**: Financial domain-specific model

#### Signal Generation
1. **Data Collection**: Gather relevant text data from configured sources
2. **Preprocessing**: Clean and tokenize text data
3. **Model Inference**: Run text through all three models
4. **Ensemble Scoring**: Combine model outputs with weighted averaging
5. **Confidence Assessment**: Calculate prediction confidence scores
6. **Signal Filtering**: Apply confidence and sentiment thresholds
7. **Position Sizing**: Determine trade size based on signal strength

#### Performance Optimization
- Dynamic model weight adjustment based on recent performance
- Momentum analysis to identify trend strength
- Volume confirmation to validate signal quality
- Correlation analysis to avoid redundant positions

### Statistical Arbitrage Strategy

The statistical arbitrage strategy identifies pricing inefficiencies between correlated markets:

#### Methodology
1. **Correlation Analysis**: Identify highly correlated market pairs
2. **Historical Analysis**: Calculate statistical relationships over lookback period
3. **Z-Score Calculation**: Measure current price deviation from historical mean
4. **Signal Generation**: Trigger trades when z-score exceeds threshold
5. **Mean Reversion**: Profit from price convergence back to historical relationship

#### Risk Controls
- Minimum correlation requirements
- Maximum position correlation limits
- Dynamic threshold adjustment
- Stop-loss mechanisms for divergent pairs

## 🛡️ Risk Management

### Portfolio-Level Controls

#### Position Sizing
- Maximum position size as percentage of portfolio
- Dynamic sizing based on volatility and correlation
- Kelly criterion optimization for bet sizing

#### Exposure Limits
- Total portfolio exposure caps
- Sector and category concentration limits
- Correlation-based position limits

#### Stop-Loss Mechanisms
- Individual position stop-losses
- Portfolio-level drawdown limits
- Time-based position exits

### Real-Time Monitoring

#### Value at Risk (VaR)
- 95% confidence interval calculations
- Monte Carlo simulation for tail risk
- Stress testing under extreme scenarios

#### Correlation Analysis
- Real-time correlation monitoring
- Dynamic correlation matrix updates
- Concentration risk alerts

#### Performance Attribution
- Strategy-level performance tracking
- Risk-adjusted return calculations
- Sharpe ratio and other metrics

## 📚 API Reference

### Core Trading Engine

#### Start Trading Bot
```python
POST /api/v1/bot/start
```

#### Stop Trading Bot
```python
POST /api/v1/bot/stop
```

#### Get Bot Status
```python
GET /api/v1/bot/status
```

### Strategy Management

#### List Strategies
```python
GET /api/v1/strategies
```

#### Update Strategy Configuration
```python
PUT /api/v1/strategies/{strategy_id}
```

#### Get Strategy Performance
```python
GET /api/v1/strategies/{strategy_id}/performance
```

### Portfolio Management

#### Get Portfolio Summary
```python
GET /api/v1/portfolio
```

#### Get Positions
```python
GET /api/v1/portfolio/positions
```

#### Get Trade History
```python
GET /api/v1/portfolio/trades
```

### Market Data

#### Get Market List
```python
GET /api/v1/markets
```

#### Get Market Details
```python
GET /api/v1/markets/{market_id}
```

#### Get Market Prices
```python
GET /api/v1/markets/{market_id}/prices
```

### Risk Management

#### Get Risk Metrics
```python
GET /api/v1/risk/metrics
```

#### Update Risk Parameters
```python
PUT /api/v1/risk/parameters
```

## 🚀 Deployment

### Production Deployment

#### Docker Deployment

1. **Build Docker Images**
   ```bash
   docker build -t kalshi-bot:latest .
   docker build -t kalshi-admin:latest ./desktop_admin_panel
   docker build -t kalshi-telegram:latest ./telegram_webapp
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

#### Cloud Deployment

##### AWS Deployment
```bash
# Deploy backend to AWS Lambda
serverless deploy

# Deploy frontend to AWS S3 + CloudFront
aws s3 sync ./desktop_admin_panel/dist s3://your-bucket
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

##### Google Cloud Deployment
```bash
# Deploy to Google Cloud Run
gcloud run deploy kalshi-bot --source .

# Deploy frontend to Google Cloud Storage
gsutil -m rsync -r -d ./desktop_admin_panel/dist gs://your-bucket
```

### Environment-Specific Configuration

#### Development
```env
NODE_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Staging
```env
NODE_ENV=staging
DEBUG=false
LOG_LEVEL=INFO
```

#### Production
```env
NODE_ENV=production
DEBUG=false
LOG_LEVEL=WARNING
```

## 🔧 Development

### Project Structure

```
enhanced-kalshi-bot/
├── src/                          # Python backend source code
│   ├── core/                     # Core trading engine
│   ├── strategies/               # Trading strategies
│   ├── ml_models/               # Machine learning models
│   ├── api/                     # API clients and endpoints
│   ├── risk_management/         # Risk management modules
│   └── utils/                   # Utility functions
├── desktop_admin_panel/         # React desktop application
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/              # Page components
│   │   └── lib/                # Utility libraries
│   └── public/                 # Static assets
├── telegram_webapp/             # Telegram web app
│   ├── src/
│   │   ├── components/          # Mobile-optimized components
│   │   └── pages/              # Mobile pages
│   └── public/                 # Static assets
├── config/                      # Configuration files
├── data/                        # Database and data files
├── logs/                        # Log files
├── tests/                       # Test files
└── docs/                        # Documentation
```

### Adding New Strategies

1. **Create Strategy Class**
   ```python
   from src.strategies.base_strategy import BaseStrategy
   
   class MyCustomStrategy(BaseStrategy):
       def __init__(self, config):
           super().__init__(config)
           
       def generate_signals(self, market_data):
           # Implement your strategy logic
           pass
   ```

2. **Register Strategy**
   ```python
   # In src/core/trading_engine.py
   from src.strategies.my_custom_strategy import MyCustomStrategy
   
   self.strategies['my_custom'] = MyCustomStrategy(config)
   ```

3. **Add Configuration**
   ```python
   # In config/strategies.py
   MY_CUSTOM_CONFIG = {
       "parameter1": value1,
       "parameter2": value2
   }
   ```

### Testing

#### Unit Tests
```bash
python -m pytest tests/unit/
```

#### Integration Tests
```bash
python -m pytest tests/integration/
```

#### End-to-End Tests
```bash
python -m pytest tests/e2e/
```

#### Frontend Tests
```bash
cd desktop_admin_panel
npm test

cd ../telegram_webapp
npm test
```

### Code Quality

#### Linting
```bash
# Python
flake8 src/
black src/

# JavaScript
cd desktop_admin_panel
npm run lint

cd ../telegram_webapp
npm run lint
```

#### Type Checking
```bash
# Python
mypy src/

# TypeScript
cd desktop_admin_panel
npm run type-check
```

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Starting
- Check API credentials in `.env` file
- Verify internet connection
- Check log files for error messages
- Ensure all dependencies are installed

#### Strategies Not Executing
- Verify strategy configuration
- Check market data connectivity
- Review risk management settings
- Monitor log files for errors

#### UI Not Loading
- Check if development server is running
- Verify Node.js dependencies are installed
- Check browser console for errors
- Ensure correct port configuration

#### Database Issues
- Check database file permissions
- Verify SQLite installation
- Review database schema migrations
- Check disk space availability

### Performance Optimization

#### Backend Optimization
- Increase worker processes for parallel execution
- Optimize database queries with indexing
- Implement caching for frequently accessed data
- Use connection pooling for API calls

#### Frontend Optimization
- Enable code splitting for faster loading
- Implement lazy loading for components
- Optimize bundle size with tree shaking
- Use service workers for offline functionality

### Monitoring and Alerting

#### System Monitoring
- CPU and memory usage tracking
- Database performance monitoring
- API response time measurement
- Error rate tracking

#### Trading Monitoring
- P&L tracking and alerts
- Position size monitoring
- Risk metric alerts
- Strategy performance tracking

## 🤝 Contributing

We welcome contributions to the Enhanced Kalshi Trading Bot! Please follow these guidelines:

### Development Workflow

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**
4. **Add Tests**
5. **Run Quality Checks**
6. **Submit Pull Request**

### Contribution Guidelines

- Follow existing code style and conventions
- Add comprehensive tests for new features
- Update documentation for any changes
- Ensure all tests pass before submitting
- Write clear commit messages

### Code Review Process

- All changes require review by maintainers
- Automated tests must pass
- Code coverage should not decrease
- Documentation must be updated

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:

- **Documentation**: Check this README and the `/docs` folder
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: support@kalshi-bot.com

## 🙏 Acknowledgments

- Kalshi for providing the prediction market platform
- The open-source community for the excellent libraries used
- Contributors who have helped improve this project

---

**Disclaimer**: This software is for educational and research purposes. Trading involves risk, and past performance does not guarantee future results. Always do your own research and consider your risk tolerance before trading.

