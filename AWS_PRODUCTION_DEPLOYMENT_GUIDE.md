# AWS Production Deployment Guide - Farm2Fork

Complete step-by-step guide to deploy Farm2Fork application to AWS with real-time production setup.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   Route 53   │────────▶│  CloudFront  │                  │
│  │     DNS      │         │     CDN      │                  │
│  └──────────────┘         └──────┬───────┘                  │
│                                   │                          │
│                          ┌────────▼────────┐                 │
│                          │   S3 Bucket     │                 │
│                          │   (Frontend)    │                 │
│                          └─────────────────┘                 │
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │   API GW     │────────▶│   Lambda     │                  │
│  │  (REST API)  │         │  (Backend)   │                  │
│  └──────────────┘         └──────┬───────┘                  │
│                                   │                          │
│                          ┌────────▼────────┐                 │
│                          │   RDS MySQL     │                 │
│                          │   (Database)    │                 │
│                          └─────────────────┘                 │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │           AWS Services (Already Setup)          │        │
│  ├─────────────────────────────────────────────────┤        │
│  │  • S3 (Images)      • Cognito (Auth)            │        │
│  │  • Textract (OCR)   • Bedrock (AI)              │        │
│  │  • Rekognition      • Translate                 │        │
│  │  • SNS (SMS)        • Lambda (Cognito)          │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### 1. AWS Account Setup
- AWS Account with billing enabled
- AWS CLI installed and configured
- IAM user with Administrator access

### 2. Domain Name (Optional but Recommended)
- Purchase domain from Route 53 or external provider
- Example: `farm2fork.com`

### 3. Local Tools
- Node.js 18+ and npm
- Python 3.9+
- Git
- AWS CLI v2

---

## Part 1: Database Setup (RDS MySQL)

### Step 1.1: Create RDS MySQL Instance

1. **Go to AWS Console → RDS**

2. **Click "Create database"**

3. **Choose settings:**
   ```
   Engine: MySQL 8.0
   Template: Production (or Dev/Test for lower cost)
   DB Instance Identifier: farm2fork-db
   Master Username: admin
   Master Password: [Create strong password - save it!]
   
   Instance Configuration:
   - DB Instance Class: db.t3.micro (Free tier) or db.t3.small
   
   Storage:
   - Storage Type: General Purpose SSD (gp3)
   - Allocated Storage: 20 GB
   - Enable Storage Autoscaling: Yes
   - Maximum Storage: 100 GB
   
   Connectivity:
   - VPC: Default VPC
   - Public Access: Yes (for initial setup)
   - VPC Security Group: Create new
   - Security Group Name: farm2fork-db-sg
   
   Database Authentication:
   - Password authentication
   
   Additional Configuration:
   - Initial Database Name: farm2fork
   - Backup Retention: 7 days
   - Enable Encryption: Yes
   ```

4. **Click "Create database"** (takes 5-10 minutes)

5. **Note down the endpoint:**
   ```
   Example: farm2fork-db.xxxxxx.us-east-1.rds.amazonaws.com
   ```

### Step 1.2: Configure Security Group

1. **Go to EC2 → Security Groups**

2. **Find `farm2fork-db-sg`**

3. **Edit Inbound Rules:**
   ```
   Type: MySQL/Aurora
   Protocol: TCP
   Port: 3306
   Source: 0.0.0.0/0 (for testing - restrict later)
   Description: Allow MySQL access
   ```

4. **Save rules**

### Step 1.3: Test Database Connection

```bash
# Install MySQL client (if not installed)
# Windows: Download from MySQL website
# Mac: brew install mysql-client
# Linux: sudo apt-get install mysql-client

# Test connection
mysql -h farm2fork-db.xxxxxx.us-east-1.rds.amazonaws.com -u admin -p

# Enter password when prompted
# If connected successfully, you'll see: mysql>

# Exit
exit
```

### Step 1.4: Initialize Database Schema

1. **Update backend/.env with RDS credentials:**
   ```env
   DATABASE_URL=mysql+pymysql://admin:[PASSWORD]@farm2fork-db.xxxxxx.us-east-1.rds.amazonaws.com:3306/farm2fork
   ```

2. **Run migrations locally to setup schema:**
   ```bash
   cd backend
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run Alembic migrations
   alembic upgrade head
   ```

3. **Verify tables created:**
   ```bash
   mysql -h farm2fork-db.xxxxxx.us-east-1.rds.amazonaws.com -u admin -p farm2fork
   
   # In MySQL prompt:
   SHOW TABLES;
   # Should show: farmers, crop_batches, treatments, crop_images, safety_analysis, qr_codes
   
   exit
   ```

---

## Part 2: Backend Deployment (AWS Lambda + API Gateway)

### Step 2.1: Prepare Backend for Lambda

1. **Create Lambda deployment package:**

```bash
cd backend

# Create deployment directory
mkdir lambda_package
cd lambda_package

# Copy application files
cp ../*.py .
cp -r ../alembic .

# Install dependencies in package directory
pip install -r ../requirements.txt -t .

# Install additional Lambda dependencies
pip install mangum -t .

# Remove unnecessary files to reduce size
rm -rf *.dist-info
rm -rf __pycache__
rm -rf tests
rm -rf .pytest_cache

# Create ZIP file
# Windows PowerShell:
Compress-Archive -Path * -DestinationPath ../farm2fork-backend.zip

# Mac/Linux:
zip -r ../farm2fork-backend.zip .

cd ..
```

### Step 2.2: Create Lambda Function

1. **Go to AWS Console → Lambda**

2. **Click "Create function"**

3. **Configure:**
   ```
   Function Name: farm2fork-backend
   Runtime: Python 3.9
   Architecture: x86_64
   
   Permissions:
   - Create new role with basic Lambda permissions
   - Role name: farm2fork-lambda-role
   ```

4. **Click "Create function"**

5. **Upload deployment package:**
   - Click "Upload from" → ".zip file"
   - Select `farm2fork-backend.zip`
   - Click "Save"

6. **Configure Lambda settings:**
   
   **General Configuration:**
   ```
   Memory: 512 MB (increase if needed)
   Timeout: 30 seconds
   ```
   
   **Environment Variables:**
   ```
   DATABASE_URL=mysql+pymysql://admin:[PASSWORD]@farm2fork-db.xxxxxx.us-east-1.rds.amazonaws.com:3306/farm2fork
   
   JWT_SECRET_KEY=[Your JWT secret from .env]
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_DAYS=7
   
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=[Your AWS Access Key]
   AWS_SECRET_ACCESS_KEY=[Your AWS Secret Key]
   
   S3_BUCKET_NAME=farm2fork-images
   S3_QR_BUCKET_NAME=farm2fork-qr-codes
   
   BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
   TEXTRACT_REGION=us-east-1
   REKOGNITION_REGION=us-east-1
   TRANSLATE_REGION=us-east-1
   
   USE_COGNITO_AUTH=true
   COGNITO_USER_POOL_ID=[Your Cognito Pool ID]
   COGNITO_CLIENT_ID=[Your Cognito Client ID]
   COGNITO_CLIENT_SECRET=[Your Cognito Client Secret]
   COGNITO_REGION=us-east-1
   
   CORS_ORIGINS=https://yourdomain.com
   FRONTEND_URL=https://yourdomain.com
   ```

7. **Update Lambda Handler:**
   - Handler: `main.handler`
   - This uses the Mangum handler in your main.py

### Step 2.3: Configure Lambda IAM Role

1. **Go to IAM → Roles**

2. **Find `farm2fork-lambda-role`**

3. **Attach additional policies:**
   - `AmazonS3FullAccess`
   - `AmazonTextractFullAccess`
   - `AmazonRekognitionFullAccess`
   - `AmazonBedrockFullAccess`
   - `TranslateFullAccess`
   - `AmazonCognitoPowerUser`
   - `AmazonSNSFullAccess`

4. **Add inline policy for RDS:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "rds:DescribeDBInstances",
           "rds:Connect"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

### Step 2.4: Create API Gateway

1. **Go to AWS Console → API Gateway**

2. **Click "Create API"**

3. **Choose "HTTP API" (simpler and cheaper)**

4. **Configure:**
   ```
   API Name: farm2fork-api
   
   Integrations:
   - Add integration: Lambda
   - Lambda function: farm2fork-backend
   - Version: 2.0
   ```

5. **Configure routes:**
   ```
   Method: ANY
   Resource path: /{proxy+}
   Integration: farm2fork-backend
   ```

6. **Configure CORS:**
   ```
   Access-Control-Allow-Origin: * (or your domain)
   Access-Control-Allow-Headers: *
   Access-Control-Allow-Methods: *
   ```

7. **Create and deploy:**
   - Stage name: `prod`
   - Click "Create"

8. **Note your API endpoint:**
   ```
   Example: https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod
   ```

### Step 2.5: Test Backend API

```bash
# Test health endpoint
curl https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod/health

# Should return:
# {"status":"healthy","service":"FARM2FORK API","version":"1.0.0"}
```

---

## Part 3: Frontend Deployment (S3 + CloudFront)

### Step 3.1: Build Frontend

```bash
cd frontend

# Update API URL in config
# Edit frontend/src/config.ts:
export const API_URL = 'https://xxxxxx.execute-api.us-east-1.amazonaws.com/prod'

# Install dependencies
npm install

# Build for production
npm run build

# This creates a 'dist' folder with optimized files
```

### Step 3.2: Create S3 Bucket for Frontend

1. **Go to AWS Console → S3**

2. **Click "Create bucket"**

3. **Configure:**
   ```
   Bucket name: farm2fork-frontend (must be globally unique)
   Region: us-east-1
   
   Block Public Access:
   - Uncheck "Block all public access"
   - Acknowledge the warning
   
   Bucket Versioning: Enable
   
   Default encryption: Enable (SSE-S3)
   ```

4. **Click "Create bucket"**

### Step 3.3: Configure S3 for Static Website Hosting

1. **Select your bucket → Properties**

2. **Scroll to "Static website hosting"**

3. **Click "Edit"**

4. **Configure:**
   ```
   Static website hosting: Enable
   Hosting type: Host a static website
   Index document: index.html
   Error document: index.html (for SPA routing)
   ```

5. **Save changes**

6. **Note the website endpoint:**
   ```
   Example: http://farm2fork-frontend.s3-website-us-east-1.amazonaws.com
   ```

### Step 3.4: Set Bucket Policy

1. **Go to Permissions tab**

2. **Edit Bucket Policy:**

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

3. **Save changes**

### Step 3.5: Upload Frontend Files

```bash
# Using AWS CLI
cd frontend/dist

aws s3 sync . s3://farm2fork-frontend/ --delete

# Or use AWS Console:
# 1. Go to S3 bucket
# 2. Click "Upload"
# 3. Drag all files from dist folder
# 4. Click "Upload"
```

### Step 3.6: Test S3 Website

Visit: `http://farm2fork-frontend.s3-website-us-east-1.amazonaws.com`

You should see your application!

### Step 3.7: Setup CloudFront CDN (Optional but Recommended)

1. **Go to AWS Console → CloudFront**

2. **Click "Create distribution"**

3. **Configure:**
   ```
   Origin Domain: farm2fork-frontend.s3-website-us-east-1.amazonaws.com
   Origin Path: (leave empty)
   Name: farm2fork-frontend
   
   Default Cache Behavior:
   - Viewer Protocol Policy: Redirect HTTP to HTTPS
   - Allowed HTTP Methods: GET, HEAD, OPTIONS
   - Cache Policy: CachingOptimized
   
   Settings:
   - Price Class: Use all edge locations (best performance)
   - Alternate Domain Names (CNAMEs): www.yourdomain.com, yourdomain.com
   - Custom SSL Certificate: Request or import certificate
   - Default Root Object: index.html
   ```

4. **Create distribution** (takes 10-15 minutes to deploy)

5. **Note CloudFront domain:**
   ```
   Example: d1234567890.cloudfront.net
   ```

### Step 3.8: Configure Custom Error Pages

1. **Go to CloudFront distribution → Error Pages**

2. **Create custom error response:**
   ```
   HTTP Error Code: 403
   Customize Error Response: Yes
   Response Page Path: /index.html
   HTTP Response Code: 200
   
   HTTP Error Code: 404
   Customize Error Response: Yes
   Response Page Path: /index.html
   HTTP Response Code: 200
   ```

This ensures SPA routing works correctly.

---

## Part 4: Domain Setup (Route 53)

### Step 4.1: Create Hosted Zone

1. **Go to AWS Console → Route 53**

2. **Click "Create hosted zone"**

3. **Configure:**
   ```
   Domain name: yourdomain.com
   Type: Public hosted zone
   ```

4. **Click "Create hosted zone"**

5. **Note the nameservers** (you'll need these for your domain registrar)

### Step 4.2: Update Domain Nameservers

If you bought domain from external registrar (GoDaddy, Namecheap, etc.):

1. **Go to your domain registrar**

2. **Find DNS/Nameserver settings**

3. **Replace nameservers with Route 53 nameservers:**
   ```
   ns-1234.awsdns-12.org
   ns-5678.awsdns-34.com
   ns-9012.awsdns-56.net
   ns-3456.awsdns-78.co.uk
   ```

4. **Save changes** (propagation takes 24-48 hours)

### Step 4.3: Create SSL Certificate

1. **Go to AWS Console → Certificate Manager**

2. **Click "Request certificate"**

3. **Configure:**
   ```
   Certificate type: Public certificate
   
   Domain names:
   - yourdomain.com
   - *.yourdomain.com (wildcard for subdomains)
   
   Validation method: DNS validation
   ```

4. **Click "Request"**

5. **Add CNAME records to Route 53:**
   - Click "Create records in Route 53"
   - This automatically adds validation records

6. **Wait for validation** (5-30 minutes)

### Step 4.4: Create DNS Records

1. **Go to Route 53 → Hosted zones → yourdomain.com**

2. **Create A record for root domain:**
   ```
   Record name: (leave empty)
   Record type: A
   Alias: Yes
   Route traffic to: CloudFront distribution
   Distribution: Select your CloudFront distribution
   ```

3. **Create A record for www:**
   ```
   Record name: www
   Record type: A
   Alias: Yes
   Route traffic to: CloudFront distribution
   Distribution: Select your CloudFront distribution
   ```

4. **Create CNAME for API (optional):**
   ```
   Record name: api
   Record type: CNAME
   Value: xxxxxx.execute-api.us-east-1.amazonaws.com
   TTL: 300
   ```

---

## Part 5: Enable Production Features

### Step 5.1: Enable Real SMS OTP (Cognito)

1. **Go to AWS Console → SNS**

2. **Request production access:**
   - Click "Text messaging (SMS)"
   - Click "Request production access"
   - Fill out form with use case details
   - Wait for approval (1-2 business days)

3. **Update Lambda environment variables:**
   ```
   USE_COGNITO_AUTH=true
   ```

4. **Test SMS OTP:**
   ```bash
   # Use your app to request OTP
   # Check if SMS is received
   ```

### Step 5.2: Configure Database Backups

1. **Go to RDS → Databases → farm2fork-db**

2. **Modify database:**
   ```
   Backup:
   - Backup retention period: 7 days
   - Backup window: Preferred time
   - Copy tags to snapshots: Yes
   
   Maintenance:
   - Enable auto minor version upgrade: Yes
   - Maintenance window: Preferred time
   ```

3. **Apply changes**

### Step 5.3: Setup Monitoring

1. **Enable CloudWatch Logs for Lambda:**
   - Lambda automatically logs to CloudWatch
   - Go to CloudWatch → Log groups
   - Find `/aws/lambda/farm2fork-backend`

2. **Create CloudWatch Alarms:**
   ```
   Alarm 1: Lambda Errors
   - Metric: Errors
   - Threshold: > 10 in 5 minutes
   - Action: Send SNS notification
   
   Alarm 2: API Gateway 5XX Errors
   - Metric: 5XXError
   - Threshold: > 5 in 5 minutes
   - Action: Send SNS notification
   
   Alarm 3: RDS CPU
   - Metric: CPUUtilization
   - Threshold: > 80% for 5 minutes
   - Action: Send SNS notification
   ```

### Step 5.4: Setup Cost Alerts

1. **Go to AWS Billing → Budgets**

2. **Create budget:**
   ```
   Budget type: Cost budget
   Budget name: farm2fork-monthly
   Period: Monthly
   Budgeted amount: $50 (adjust as needed)
   
   Alert threshold: 80% of budgeted amount
   Email recipients: your-email@example.com
   ```

---

## Part 6: Security Hardening

### Step 6.1: Restrict Database Access

1. **Go to EC2 → Security Groups → farm2fork-db-sg**

2. **Edit inbound rules:**
   ```
   Remove: 0.0.0.0/0
   Add: Lambda security group only
   ```

### Step 6.2: Enable WAF (Web Application Firewall)

1. **Go to AWS WAF**

2. **Create web ACL:**
   ```
   Name: farm2fork-waf
   Resource type: CloudFront distribution
   
   Add rules:
   - AWS Managed Rules - Core rule set
   - AWS Managed Rules - Known bad inputs
   - Rate limiting: 2000 requests per 5 minutes per IP
   ```

3. **Associate with CloudFront distribution**

### Step 6.3: Rotate Secrets

1. **Store secrets in AWS Secrets Manager:**

```bash
# Create secret for database
aws secretsmanager create-secret \
  --name farm2fork/database \
  --secret-string '{"username":"admin","password":"YOUR_PASSWORD"}'

# Create secret for JWT
aws secretsmanager create-secret \
  --name farm2fork/jwt \
  --secret-string '{"secret":"YOUR_JWT_SECRET"}'
```

2. **Update Lambda to use Secrets Manager:**
   - Add IAM permission for Secrets Manager
   - Modify code to fetch secrets at runtime

### Step 6.4: Enable MFA for AWS Account

1. **Go to IAM → Users → Your user**

2. **Security credentials tab**

3. **Assign MFA device**

4. **Follow setup wizard**

---

## Part 7: Testing Production Deployment

### Step 7.1: Test Frontend

1. **Visit your domain:** `https://yourdomain.com`

2. **Test features:**
   - ✅ Page loads correctly
   - ✅ Images load from CloudFront
   - ✅ No console errors
   - ✅ Mobile responsive

### Step 7.2: Test Backend API

```bash
# Test health endpoint
curl https://api.yourdomain.com/health

# Test authentication
curl -X POST https://api.yourdomain.com/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+919876543210"}'

# Should receive SMS OTP
```

### Step 7.3: Test Complete User Flow

1. **Farmer Registration:**
   - Request OTP
   - Verify OTP
   - Create profile

2. **Create Batch:**
   - Upload images
   - Add multiple pesticides/fertilizers
   - Submit batch

3. **Generate QR Code:**
   - Generate QR for batch
   - Download QR code

4. **Consumer Verification:**
   - Scan QR code
   - View batch details
   - Check safety analysis

### Step 7.4: Load Testing

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Mac: brew install httpd
# Linux: sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 https://api.yourdomain.com/health

# Check results:
# - Requests per second
# - Time per request
# - Failed requests (should be 0)
```

---

## Part 8: Maintenance & Updates

### Step 8.1: Update Backend

```bash
# Make code changes
cd backend

# Create new deployment package
cd lambda_package
# ... (repeat packaging steps)

# Upload to Lambda
aws lambda update-function-code \
  --function-name farm2fork-backend \
  --zip-file fileb://../farm2fork-backend.zip
```

### Step 8.2: Update Frontend

```bash
cd frontend

# Make code changes

# Build
npm run build

# Deploy to S3
cd dist
aws s3 sync . s3://farm2fork-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

### Step 8.3: Database Migrations

```bash
# Create new migration
cd backend
alembic revision -m "description of changes"

# Edit migration file in alembic/versions/

# Test locally first
alembic upgrade head

# Apply to production (connect to RDS)
DATABASE_URL=mysql+pymysql://admin:PASSWORD@farm2fork-db.xxx.rds.amazonaws.com:3306/farm2fork \
alembic upgrade head
```

---

## Cost Estimation

### Monthly Costs (Approximate)

```
RDS MySQL (db.t3.micro):        $15-20
Lambda (1M requests):           $0.20
API Gateway (1M requests):      $3.50
S3 Storage (10GB):              $0.23
CloudFront (100GB transfer):    $8.50
Route 53 (1 hosted zone):       $0.50
Certificate Manager:            FREE
Cognito (10K MAU):              FREE
SNS (1000 SMS):                 $0.60
Textract (1000 pages):          $1.50
Rekognition (1000 images):      $1.00
Bedrock (1000 requests):        $0.50
Translate (1M characters):      $15.00

TOTAL:                          ~$47/month
```

### Cost Optimization Tips

1. **Use Reserved Instances for RDS** (save 30-60%)
2. **Enable S3 Intelligent-Tiering**
3. **Use CloudFront caching** (reduce origin requests)
4. **Optimize Lambda memory** (right-size for performance)
5. **Use S3 lifecycle policies** (move old data to Glacier)

---

## Troubleshooting

### Issue: Lambda Timeout

**Solution:**
- Increase timeout to 30 seconds
- Optimize database queries
- Add connection pooling

### Issue: CORS Errors

**Solution:**
- Check API Gateway CORS settings
- Verify Lambda returns correct headers
- Update CORS_ORIGINS environment variable

### Issue: Database Connection Failed

**Solution:**
- Check security group rules
- Verify RDS is publicly accessible
- Test connection from Lambda VPC

### Issue: Images Not Loading

**Solution:**
- Check S3 bucket policy
- Verify CORS on S3 bucket
- Check CloudFront distribution status

### Issue: High Costs

**Solution:**
- Review CloudWatch metrics
- Check for unused resources
- Enable cost allocation tags
- Set up billing alerts

---

## Support & Resources

### AWS Documentation
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [RDS User Guide](https://docs.aws.amazon.com/rds/)
- [S3 User Guide](https://docs.aws.amazon.com/s3/)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)

### Monitoring
- CloudWatch Logs: `/aws/lambda/farm2fork-backend`
- CloudWatch Metrics: Lambda, API Gateway, RDS
- X-Ray Tracing: Enable for detailed request tracing

### Backup & Recovery
- RDS automated backups: 7 days retention
- Manual snapshots: Create before major changes
- S3 versioning: Enabled for frontend bucket

---

## Checklist

### Pre-Deployment
- [ ] AWS account setup
- [ ] Domain purchased
- [ ] SSL certificate requested
- [ ] All AWS services tested locally

### Database
- [ ] RDS instance created
- [ ] Security group configured
- [ ] Database schema initialized
- [ ] Connection tested

### Backend
- [ ] Lambda function created
- [ ] Environment variables set
- [ ] IAM role configured
- [ ] API Gateway created
- [ ] Health endpoint tested

### Frontend
- [ ] Production build created
- [ ] S3 bucket configured
- [ ] Files uploaded
- [ ] CloudFront distribution created
- [ ] Custom domain configured

### Security
- [ ] Database access restricted
- [ ] WAF enabled
- [ ] Secrets in Secrets Manager
- [ ] MFA enabled on AWS account

### Monitoring
- [ ] CloudWatch alarms created
- [ ] Cost budgets set
- [ ] Logging enabled
- [ ] Backup configured

### Testing
- [ ] Frontend loads correctly
- [ ] API endpoints working
- [ ] SMS OTP working
- [ ] Complete user flow tested
- [ ] Load testing completed

---

## Next Steps

1. **Monitor for 24 hours** - Check logs and metrics
2. **Test with real users** - Get feedback
3. **Optimize performance** - Based on metrics
4. **Plan scaling** - As user base grows
5. **Regular backups** - Test restore procedures

## Congratulations! 🎉

Your Farm2Fork application is now live on AWS with production-grade infrastructure!

**Your URLs:**
- Frontend: `https://yourdomain.com`
- API: `https://api.yourdomain.com`
- Admin: AWS Console

**Remember to:**
- Monitor costs daily for first week
- Check CloudWatch logs regularly
- Keep secrets secure
- Update dependencies regularly
- Backup database before changes
