# Deployment

This directory contains deployment scripts and configuration for the FARM2FORK platform.

## Deployment Scripts

Scripts will be added in later tasks:
- `deploy.sh` - Main deployment script for both frontend and backend
- `deploy-frontend.sh` - Deploy frontend to S3 + CloudFront
- `deploy-backend.sh` - Deploy backend to AWS Lambda
- `rollback.sh` - Rollback to previous deployment

## Deployment Process

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Production Deployment

1. Build frontend: `npm run build` in frontend directory
2. Upload frontend build to S3
3. Invalidate CloudFront cache
4. Build Lambda deployment package
5. Deploy Lambda function
6. Update API Gateway configuration

Detailed deployment instructions will be added in Task 29.

## Environment Configuration

- Development: `.env` files in backend and frontend directories
- Production: AWS Systems Manager Parameter Store or Secrets Manager
