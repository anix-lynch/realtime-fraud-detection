# Real-Time Feature Engineering for Fraud Detection

A complete take-home project demonstrating real-time feature engineering for fraud detection using streaming transaction data.

## Project Overview

This project implements a real-time fraud detection system that processes transaction events and calculates fraud scores using engineered features. The system is designed to handle streaming data efficiently with memory-safe state management.

## Architecture

### Core Components

- **RealTimeFeatureEngine**: Processes events and calculates real-time features
- **StateStore**: In-memory storage with TTL and cleanup for user state
- **FastAPI Service**: REST API for fraud scoring and health checks
- **Synthetic Data Generator**: Creates realistic transaction events for testing

### Key Features

#### Real-Time Feature Engineering
- **Transaction Velocity**: Transactions per hour in the last hour
- **Amount Deviation**: Z-score of transaction amount vs user history
- **Location Anomaly**: Detection of unusual transaction locations
- **Time Pattern Analysis**: Unusual timing patterns (hour/day)
- **Behavioral Features**: Merchant diversity, payment method consistency

#### Memory Management
- Rolling time windows (1 hour, 24 hours, 1 week)
- Automatic cleanup of old state data
- Bounded data structures to prevent memory leaks

#### Scoring Model
- Weighted combination of features with sigmoid transformation
- Deterministic scoring (no external ML models)
- Real-time feature updates after each transaction

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)

### 🚀 Unified Deployment (Recommended)

**One-command deployment:**
```bash
./deploy.sh
```
This starts both the API and Streamlit UI automatically.

**Access points:**
- 🎨 **Web UI**: http://localhost:8501
- 📊 **API**: http://localhost:8001
- 📋 **API Docs**: http://localhost:8001/docs

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit UI:**
   ```bash
   ./scripts/run_streamlit.sh
   ```
   UI will be available at `http://localhost:8501`

3. **Run the API (separate terminal):**
   ```bash
   ./scripts/run_api.sh
   ```
   API will be available at `http://localhost:8001`

4. **Simulate streaming events:**
   ```bash
   ./scripts/simulate_stream.sh
   ```
   This sends 500 synthetic transactions to the API

5. **Run tests:**
   ```bash
   ./scripts/run_tests.sh
   ```

6. **Demo script:**
   ```bash
   python demo.py
   ```
   Direct demonstration of the fraud detection engine

### Docker Deployment

**Full stack (API + UI):**
```bash
docker-compose up --build
```

**Individual services:**
```bash
# API only
docker-compose up fraud_api --build

# UI only
docker-compose up fraud_ui --build
```

## API Endpoints

### Health Check
```http
GET /health
```
Returns system status and state store statistics.

### Fraud Scoring
```http
POST /fraud_score
Content-Type: application/json

{
  "user_id": "user_00001",
  "transaction_id": "txn_000001",
  "amount": 150.00,
  "timestamp": "2025-01-15T14:30:00Z",
  "merchant": "Amazon",
  "location": "New York",
  "payment_method": "credit_card"
}
```

**Response:**
```json
{
  "score": 0.234,
  "features": {
    "transaction_velocity_1h": 2.0,
    "amount_zscore": 1.5,
    "location_anomaly": 0,
    "time_pattern_score": 0.3,
    "merchant_diversity": 0.8,
    "payment_method_consistency": 0.9,
    "amount_volatility": 0.25,
    "location_consistency": 0.95
  },
  "model_version": "v0",
  "processing_time_ms": 12.5
}
```

### Get User Features
```http
GET /features/{user_id}
```
Returns the current feature vector for a specific user.

## Feature Definitions

| Feature | Description | Range |
|---------|-------------|-------|
| `transaction_velocity_1h` | Transactions in last hour | 0+ |
| `amount_zscore` | Deviation from user's amount history | -∞ to +∞ |
| `location_anomaly` | Binary flag for unusual locations | 0 or 1 |
| `time_pattern_score` | Unusual timing patterns | 0.0 to 1.0 |
| `merchant_diversity` | Unique merchants / total transactions | 0.0 to 1.0 |
| `payment_method_consistency` | Primary payment method ratio | 0.0 to 1.0 |
| `amount_volatility` | Amount variation coefficient | 0.0+ |
| `location_consistency` | Primary location ratio | 0.0 to 1.0 |

## Data Flow

1. **Event Ingestion**: Transaction events received via POST /fraud_score
2. **Validation**: Event structure and required fields validated
3. **State Update**: Event added to user's rolling time window
4. **Feature Calculation**: Real-time features computed from recent history
5. **Scoring**: Weighted combination produces fraud probability
6. **Response**: Score and feature vector returned

## Memory Strategy

### State Management
- **User Isolation**: Each user has independent state
- **Time Windows**: Features calculated over different time horizons
- **Bounded Storage**: Deques with max length prevent unbounded growth
- **TTL Cleanup**: Old user states automatically removed
- **Periodic Cleanup**: Background cleanup prevents memory leaks

### Performance Characteristics
- O(1) event processing (bounded history)
- O(n) feature calculation (n = events in window)
- Automatic memory bounds (configurable windows)
- No external dependencies for state storage

## Testing

The test suite covers:
- Event processing and state updates
- Feature vector consistency and ranges
- Velocity, amount, location, and time pattern calculations
- Memory cleanup functionality
- API endpoint validation

Run tests with:
```bash
./scripts/run_tests.sh
```

## Limitations & Next Steps

### Current Limitations
- Single-threaded processing
- In-memory only (no persistence)
- Simple rule-based scoring
- No horizontal scaling

### Production Considerations
- **Kafka Integration**: Replace local simulation with event streaming
- **Redis/MongoDB**: Persistent state storage for user history
- **Model Serving**: Integrate trained ML models (XGBoost, TensorFlow)
- **Monitoring**: Add metrics collection (Prometheus, Grafana)
- **Load Balancing**: Multiple API instances with shared state
- **Feature Stores**: Feast or custom feature store integration

### Scaling Architecture
```
Events → Kafka → Feature Engine → Redis → API → Scoring Model → Response
```

## Project Structure

```
├── streamlit_app.py            # 🎨 Interactive web UI
├── demo.py                     # 🎯 Direct engine demo
├── deploy.sh                   # 🚀 Unified deployment script
├── package.json                # 📦 Deployment config
├── src/
│   ├── streaming_features.py    # Core feature engineering
│   ├── api.py                   # FastAPI endpoints
│   └── utils/
│       ├── state_store.py       # State management
│       ├── time_utils.py        # Time handling
│       ├── validation_utils.py  # Data validation
│       └── logging_utils.py     # Structured logging
├── data/
│   └── synthetic_events.jsonl   # Test data (500 events)
├── tests/
│   └── test_realtime_engine.py  # Test suite (9/9 passing)
├── docker/
│   ├── Dockerfile              # Container config
│   └── docker-compose.yml      # Multi-service deployment
├── scripts/
│   ├── run_api.sh             # API runner
│   ├── run_streamlit.sh       # 🎨 UI runner
│   ├── simulate_stream.sh     # Stream simulator
│   └── run_tests.sh          # Test runner
├── .streamlit/
│   └── config.toml            # 🎨 UI configuration
└── requirements.txt           # Dependencies
```
