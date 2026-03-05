# Development Guide

This guide will help you set up the FARM2FORK platform for local development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or higher**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher**: [Download Node.js](https://nodejs.org/)
- **PostgreSQL 14 or higher**: [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **AWS CLI**: [Install AWS CLI](https://aws.amazon.com/cli/)

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd farm2fork-traceability
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# You'll need to set:
# - Database credentials
# - AWS credentials
# - JWT secret key
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb farm2fork

# Or using psql:
psql -U postgres
CREATE DATABASE farm2fork;
\q

# Update DATABASE_URL in backend/.env with your credentials
# Example: postgresql://username:password@localhost:5432/farm2fork
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env file
# Set VITE_API_BASE_URL to your backend URL (default: http://localhost:8000/api)
```

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn main:app --reload --port 8000
```

The backend API will be available at: `http://localhost:8000`
API documentation (Swagger): `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## Development Workflow

### Backend Development

1. **Create new endpoints**: Add routes in appropriate modules
2. **Database changes**: Create Alembic migrations
3. **Run tests**: `pytest` or `pytest --cov`
4. **Format code**: Use `black` and `isort`

### Frontend Development

1. **Create components**: Add to `src/components/`
2. **Add routes**: Update `src/App.tsx`
3. **Run tests**: `npm run test`
4. **Lint code**: `npm run lint`
5. **Build**: `npm run build`

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_auth.py

# Run property-based tests only
pytest -m property
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm run test

# Run tests with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

## AWS Services Setup (Local Development)

For local development, you can use:

1. **LocalStack**: Mock AWS services locally
   ```bash
   pip install localstack
   localstack start
   ```

2. **Moto**: Mock AWS services in tests (already in requirements.txt)

3. **AWS Free Tier**: Use actual AWS services with free tier limits

### AWS Credentials

Configure AWS credentials:

```bash
aws configure
```

Or set environment variables in `backend/.env`:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## Common Issues

### Backend Issues

**Issue**: `ModuleNotFoundError`
**Solution**: Ensure virtual environment is activated and dependencies are installed

**Issue**: Database connection error
**Solution**: Check PostgreSQL is running and DATABASE_URL is correct

**Issue**: AWS service errors
**Solution**: Verify AWS credentials are configured correctly

### Frontend Issues

**Issue**: `Cannot find module`
**Solution**: Run `npm install` to install dependencies

**Issue**: API connection error
**Solution**: Ensure backend is running and VITE_API_BASE_URL is correct

**Issue**: Build errors
**Solution**: Check TypeScript errors with `npm run lint`

## Code Style

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Use `black` for formatting
- Use `isort` for import sorting

### Frontend (TypeScript)

- Follow ESLint rules
- Use TypeScript strict mode
- Write JSDoc comments for complex functions
- Use functional components with hooks
- Follow React best practices

## Git Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "Description"`
3. Push to remote: `git push origin feature/your-feature`
4. Create pull request
5. After review, merge to main

## Environment Variables

### Backend (.env)

See `backend/.env.example` for all required variables:
- Database configuration
- AWS credentials and service configuration
- JWT settings
- CORS origins

### Frontend (.env)

See `frontend/.env.example` for all required variables:
- API base URL
- AWS configuration (if needed)
- Feature flags
- Language settings

## Next Steps

After completing the initial setup:

1. Review the [Requirements](.kiro/specs/farm2fork-traceability/requirements.md)
2. Study the [Design Document](.kiro/specs/farm2fork-traceability/design.md)
3. Follow the [Implementation Tasks](.kiro/specs/farm2fork-traceability/tasks.md)
4. Start with Task 2: Database models and migrations

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
