# Wallet Service

A modern, scalable wallet management API built with FastAPI, PostgreSQL, and Docker. This service provides secure wallet creation, balance management, and transaction processing capabilities.

## 🚀 Features

- **Wallet Management**: Create and manage digital wallets with unique UUIDs
- **Transaction Processing**: Support for deposits and withdrawals with balance validation
- **Real-time Balance Updates**: Automatic balance calculation and validation
- **Comprehensive API**: RESTful API with detailed documentation and examples
- **Health Monitoring**: Built-in health check endpoints for system monitoring
- **Database Integrity**: ACID-compliant transactions with PostgreSQL
- **Docker Support**: Containerized deployment with Docker Compose
- **Production Ready**: Optimized for performance with uvloop and httptools

## 🏗️ Architecture

The application follows Clean Architecture principles with clear separation of concerns:

```
app/
├── api/                    # API layer (FastAPI routers)
├── config/                 # Configuration management
├── models/                 # Database models (SQLAlchemy)
├── schemas/                # Pydantic schemas for validation
├── services/               # Business logic layer
├── repository/             # Data access layer
├── use_cases/              # Application use cases
├── healthcheck/            # Health monitoring
└── exceptions/             # Custom exception handling
```

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.119+
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0+
- **ORM**: SQLAlchemy with async support
- **Validation**: Pydantic v2
- **Dependency Injection**: Dishka
- **Database Migrations**: Alembic
- **Containerization**: Docker & Docker Compose
- **Performance**: uvloop, httptools
- **Logging**: Structlog
- **Testing**: pytest with async support

## 📋 Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Poetry (for local development)

## 🚀 Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Wallet
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start the services**
   ```bash
   make run_all
   # or
   docker-compose up -d
   ```

4. **Access the API**
   - API Documentation: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/api/v1/health

3. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start the application**
   ```bash
   make run
   # or
   uvicorn app.main:app --reload --loop uvloop --http httptools
   ```

## 📚 API Documentation

### Core Endpoints

#### Wallet Management

- **POST** `/api/v1/wallets` - Create a new wallet
- **GET** `/api/v1/wallets/{wallet_id}` - Retrieve wallet information
- **POST** `/api/v1/wallets/{wallet_id}/operation` - Process financial operations


## 🧪 Testing

Run the test suite:

```bash
make test
# or
pytest
```

The test suite includes:
- Unit tests for business logic
- Integration tests for API endpoints
- Database transaction tests
- Error handling tests

## 🔧 Configuration

Environment variables can be configured in `.env`:

```env
# Database Configuration
POSTGRES_DB=wallet_service
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Application Configuration
APP_PORT=8000
DEBUG=true

# Database Pool Settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

## 📦 Available Commands

```bash
make help              # Show available commands
make up               # Start all containers
make run              # Run FastAPI locally
make down             # Stop containers
make test             # Run tests
```

## 🏥 Health Monitoring

The service includes comprehensive health monitoring:

- **Database connectivity** checks
- **System uptime** tracking
- **Dependency status** monitoring
- **Response time** measurement

Access health status at: `GET /api/v1/health`

## 🔒 Security Features

- **Input validation** with Pydantic schemas
- **SQL injection protection** via SQLAlchemy ORM
- **Balance validation** to prevent negative balances
- **Transaction integrity** with database constraints
- **Non-root container** execution

## 🚀 Production Deployment

### Docker Production Build

```bash
# Build production image
docker build -t wallet-service .

# Run with production settings
docker run -d \
  --name wallet-service \
  -p 8000:8000 \
  -e DEBUG=false \
  wallet-service
```

### Environment Considerations

- Set `DEBUG=false` in production
- Configure proper database credentials
- Use environment-specific logging levels
- Consider using a reverse proxy (nginx) for SSL termination

## 📈 Performance Optimizations

- **uvloop**: High-performance event loop
- **httptools**: Fast HTTP parsing
- **Connection pooling**: Optimized database connections
- **Async/await**: Non-blocking I/O operations
- **Database indexing**: Optimized query performance

## 👥 Authors

- **RocketMenace** - *Initial work* - [grizzlygit777@gmail.com](mailto:grizzlygit777@gmail.com)

---

**Version**: 0.1.0  
**Python**: 3.12+  
**FastAPI**: 0.119+