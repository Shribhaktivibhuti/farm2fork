# FARM2FORK Deployment Guide

## Prerequisites
- AWS Account with access to: S3, RDS, EC2, Textract, Rekognition, Bedrock, Translate
- Docker installed
- AWS CLI configured
- Node.js 18+ and Python 3.11+

## Local Development Setup

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials:
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=us-east-1
# S3_BUCKET_NAME=farm2fork-images
# DATABASE_URL=sqlite:///./farm2fork.db

# Initialize database
python init_db.py

# Start server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Install QR scanner
npm install html5-qrcode

# Start development server
npm run dev
```

### 3. Test Locally
- Backend: http://localhost:8000
- Frontend: http://localhost:5174
- API Docs: http://localhost:8000/docs

## AWS Infrastructure Setup

### 1. S3 Bucket for Images
```bash
# Create bucket
aws s3 mb s3://farm2fork-images --region us-east-1

# Configure CORS
aws s3api put-bucket-cors --bucket farm2fork-images --cors-configuration file://cors.json
```

**cors.json:**
```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

### 2. RDS PostgreSQL Database
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier farm2fork-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourSecurePassword123 \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-name farm2fork \
  --backup-retention-period 7 \
  --publicly-accessible

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier farm2fork-db \
  --query 'DBInstances[0].Endpoint.Address'
```

### 3. Enable AWS Services
```bash
# Bedrock (Claude 3 Sonnet)
# Go to AWS Console → Bedrock → Model access
# Request access to: anthropic.claude-3-sonnet-20240229-v1:0

# Textract, Rekognition, Translate are enabled by default
```

## Production Deployment

### Backend to EC2

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

#### 2. Build and Push to ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name farm2fork-backend

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t farm2fork-backend .

# Tag image
docker tag farm2fork-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/farm2fork-backend:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/farm2fork-backend:latest
```

#### 3. Deploy to EC2
```bash
# Launch EC2 instance (t3.medium recommended)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Role \
  --user-data file://user-data.sh

# SSH into instance
ssh -i your-key.pem ec2-user@your-ec2-ip

# Pull and run container
docker pull YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/farm2fork-backend:latest

docker run -d \
  --name farm2fork-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://admin:password@rds-endpoint:5432/farm2fork" \
  -e AWS_REGION="us-east-1" \
  -e S3_BUCKET_NAME="farm2fork-images" \
  -e JWT_SECRET_KEY="your-production-secret-key" \
  -e CORS_ORIGINS="https://farm2fork.com" \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/farm2fork-backend:latest
```

**user-data.sh:**
```bash
#!/bin/bash
yum update -y
yum install -y docker
service docker start
usermod -a -G docker ec2-user

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install
```

#### 4. Setup API Gateway
```bash
# Create REST API
aws apigateway create-rest-api \
  --name "FARM2FORK API" \
  --description "Production API for FARM2FORK" \
  --endpoint-configuration types=REGIONAL

# Create resource and methods
# Configure proxy integration to EC2 endpoint
# Deploy to stage: production
```

### Frontend to S3 + CloudFront

#### 1. Build Frontend
```bash
cd frontend

# Update API URL in .env
echo "VITE_API_URL=https://api.farm2fork.com" > .env.production

# Build
npm run build
```

#### 2. Create S3 Bucket for Frontend
```bash
# Create bucket
aws s3 mb s3://farm2fork-frontend

# Configure for static website hosting
aws s3 website s3://farm2fork-frontend \
  --index-document index.html \
  --error-document index.html

# Set bucket policy
aws s3api put-bucket-policy \
  --bucket farm2fork-frontend \
  --policy file://bucket-policy.json
```

**bucket-policy.json:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::farm2fork-frontend/*"
    }
  ]
}
```

#### 3. Upload to S3
```bash
# Sync build files
aws s3 sync dist/ s3://farm2fork-frontend --delete

# Set cache headers
aws s3 cp s3://farm2fork-frontend s3://farm2fork-frontend \
  --recursive \
  --metadata-directive REPLACE \
  --cache-control max-age=31536000,public \
  --exclude "index.html"
```

#### 4. Setup CloudFront
```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name farm2fork-frontend.s3.amazonaws.com \
  --default-root-object index.html

# Get distribution ID
aws cloudfront list-distributions \
  --query 'DistributionList.Items[?Comment==`FARM2FORK`].Id'

# Invalidate cache after updates
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"
```

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://admin:password@rds-endpoint:5432/farm2fork

# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3
S3_BUCKET_NAME=farm2fork-images

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# CORS
CORS_ORIGINS=https://farm2fork.com,https://www.farm2fork.com

# Frontend URL
FRONTEND_URL=https://farm2fork.com
```

### Frontend (.env.production)
```bash
VITE_API_URL=https://api.farm2fork.com
```

## Database Migration
```bash
# Run migrations on production
cd backend
alembic upgrade head
```

## Monitoring & Logging

### CloudWatch Logs
```bash
# Create log group
aws logs create-log-group --log-group-name /farm2fork/backend

# Configure EC2 to send logs
# Install CloudWatch agent on EC2
```

### Health Checks
```bash
# Backend health
curl https://api.farm2fork.com/health

# Expected response:
{
  "status": "healthy",
  "service": "FARM2FORK API",
  "version": "1.0.0",
  "database": "configured",
  "aws_services": "configured"
}
```

## SSL/TLS Certificates

### Using AWS Certificate Manager
```bash
# Request certificate
aws acm request-certificate \
  --domain-name farm2fork.com \
  --subject-alternative-names www.farm2fork.com api.farm2fork.com \
  --validation-method DNS

# Validate domain ownership
# Add CNAME records to your DNS
```

## Scaling

### Auto Scaling Group for EC2
```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name farm2fork-backend-template \
  --version-description "v1" \
  --launch-template-data file://launch-template.json

# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name farm2fork-backend-asg \
  --launch-template LaunchTemplateName=farm2fork-backend-template \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --target-group-arns arn:aws:elasticloadbalancing:... \
  --health-check-type ELB \
  --health-check-grace-period 300
```

## Backup Strategy

### Database Backups
```bash
# RDS automated backups (already configured)
# Retention: 7 days

# Manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier farm2fork-db \
  --db-snapshot-identifier farm2fork-backup-$(date +%Y%m%d)
```

### S3 Versioning
```bash
# Enable versioning on images bucket
aws s3api put-bucket-versioning \
  --bucket farm2fork-images \
  --versioning-configuration Status=Enabled
```

## Cost Optimization

### Estimated Monthly Costs (Low Traffic)
- EC2 t3.medium: $30
- RDS db.t3.micro: $15
- S3 storage (100GB): $2.30
- CloudFront: $1-5
- Bedrock API calls: $10-50
- Textract/Rekognition: $5-20
- **Total: ~$65-125/month**

### Cost Saving Tips
1. Use Reserved Instances for EC2/RDS (save 30-50%)
2. Enable S3 Intelligent-Tiering
3. Use CloudFront caching aggressively
4. Implement API rate limiting
5. Use Spot Instances for non-critical workloads

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker logs farm2fork-backend

# Common issues:
# 1. Database connection - verify RDS endpoint and credentials
# 2. AWS credentials - check IAM role/permissions
# 3. Port conflicts - ensure 8000 is available
```

### Frontend not loading
```bash
# Check S3 bucket policy
aws s3api get-bucket-policy --bucket farm2fork-frontend

# Check CloudFront distribution
aws cloudfront get-distribution --id YOUR_DIST_ID

# Invalidate cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### AWS Service Errors
```bash
# Check IAM permissions
aws iam get-role-policy --role-name EC2-Bedrock-Role --policy-name BedrockAccess

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1

# Test Textract
aws textract detect-document-text --document '{"S3Object":{"Bucket":"farm2fork-images","Name":"test.jpg"}}'
```

## Security Checklist
- [ ] Change all default passwords
- [ ] Enable MFA on AWS root account
- [ ] Use IAM roles instead of access keys where possible
- [ ] Enable CloudTrail for audit logging
- [ ] Configure Security Groups with minimal access
- [ ] Enable WAF on API Gateway
- [ ] Use Secrets Manager for sensitive data
- [ ] Enable S3 bucket encryption
- [ ] Configure VPC with private subnets for RDS
- [ ] Implement rate limiting on API endpoints

## Maintenance

### Regular Tasks
- Weekly: Review CloudWatch logs and metrics
- Monthly: Update dependencies and security patches
- Quarterly: Review and optimize AWS costs
- Annually: Rotate JWT secret keys and AWS credentials

### Update Deployment
```bash
# Backend update
docker build -t farm2fork-backend .
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/farm2fork-backend:latest
ssh ec2-user@your-ec2-ip "docker pull ... && docker restart farm2fork-backend"

# Frontend update
npm run build
aws s3 sync dist/ s3://farm2fork-frontend --delete
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

## Support & Documentation
- API Documentation: https://api.farm2fork.com/docs
- Architecture Diagram: See ARCHITECTURE.md
- Postman Collection: See postman/FARM2FORK.postman_collection.json
- GitHub Repository: [Your repo URL]

## Success Metrics
- API Response Time: < 500ms (p95)
- Uptime: > 99.9%
- Error Rate: < 0.1%
- Database Connections: < 80% of max
- S3 Upload Success Rate: > 99%
- AI Analysis Success Rate: > 95%
