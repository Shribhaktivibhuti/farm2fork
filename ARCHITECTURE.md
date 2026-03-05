# FARM2FORK System Architecture

## Overview
FARM2FORK is an AWS-native, production-ready traceability platform built with modern microservices architecture.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         End Users                                │
│                  (Farmers & Consumers)                           │
└────────────┬────────────────────────────────┬───────────────────┘
             │                                │
             │ HTTPS                          │ HTTPS
             ▼                                ▼
┌────────────────────────┐        ┌──────────────────────────────┐
│   React Frontend       │        │    Mobile App (Future)       │
│   - TypeScript         │        │    - React Native            │
│   - Tailwind CSS       │        │    - Native Camera           │
│   - html5-qrcode       │        │    - Offline Support         │
└────────────┬───────────┘        └──────────────┬───────────────┘
             │                                   │
             │ REST API                          │ REST API
             ▼                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Amazon CloudFront                           │
│                    (CDN + SSL/TLS)                              │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon API Gateway                            │
│              (Rate Limiting, Auth, Monitoring)                   │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                    (Python 3.11 + Uvicorn)                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Auth Service │  │Batch Service │  │  QR Service  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  S3 Service  │  │Textract Svc  │  │Rekognition   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │Bedrock Svc   │  │Translate Svc │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────────────┬──────────────────┬──────────────┐
             │                  │                  │              │
             ▼                  ▼                  ▼              ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  ┌──────────┐
│   Amazon RDS    │  │   Amazon S3     │  │AWS Bedrock   │  │  Other   │
│  PostgreSQL     │  │  Image Storage  │  │Claude 3      │  │AWS Svcs  │
│                 │  │                 │  │Sonnet        │  │          │
│ - Farmers       │  │ - Pesticide     │  │              │  │Textract  │
│ - Batches       │  │ - Fertilizer    │  │Safety Score  │  │Rekognition│
│ - Treatments    │  │ - Crop Images   │  │Risk Level    │  │Translate │
│ - QR Codes      │  │ - QR Codes      │  │Advice        │  │          │
│ - Analysis      │  │                 │  │              │  │          │
└─────────────────┘  └─────────────────┘  └──────────────┘  └──────────┘
```

## Component Details

### 1. Frontend Layer

#### React Application
- **Technology**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **State Management**: React Hooks + localStorage
- **Routing**: React Router v6
- **QR Scanning**: html5-qrcode library

#### Key Features
- Dual-mode interface (Farmer/Consumer)
- JWT token management
- Responsive design
- Camera integration
- Real-time updates

#### Deployment
- **Development**: Vite dev server (port 5174)
- **Production**: S3 static hosting + CloudFront CDN
- **Build**: `npm run build` → dist/
- **CDN**: CloudFront for global distribution

### 2. API Gateway Layer

#### Amazon API Gateway
- **Type**: REST API
- **Features**:
  - Rate limiting (1000 req/min per IP)
  - Request/response transformation
  - CORS handling
  - API key management
  - Usage plans

#### Endpoints
- `/api/auth/*` - Authentication
- `/api/batch/*` - Batch operations
- `/api/qr/*` - QR code operations
- `/api/upload/*` - File upload
- `/api/extract/*` - OCR extraction
- `/api/public/*` - Public verification

### 3. Backend Layer

#### FastAPI Application
- **Framework**: FastAPI 0.104+
- **Server**: Uvicorn with 4 workers
- **Language**: Python 3.11
- **ORM**: SQLAlchemy 2.0

#### Architecture Pattern
- **Service Layer**: Business logic separation
- **Repository Pattern**: Database abstraction
- **Dependency Injection**: FastAPI's Depends()
- **Error Handling**: Custom exception hierarchy

#### Services

##### Auth Service
```python
- validate_otp()
- generate_jwt_token()
- verify_token()
- get_current_farmer()
```

##### Batch Service
```python
- create_batch()
- get_farmer_batches()
- update_batch()
- delete_batch()
```

##### S3 Service
```python
- upload_file()
- generate_presigned_url()
- delete_file()
- configure_cors()
```

##### Textract Service
```python
- extract_from_image()
- extract_pesticide_info()
- extract_fertilizer_info()
- extract_seed_packet_info()
```

##### Rekognition Service
```python
- analyze_crop_image()
- extract_crop_indicators()
- detect_quality_issues()
```

##### Bedrock Service
```python
- generate_safety_analysis()
- generate_consumption_advice()
- invoke_model()
```

##### Translate Service
```python
- translate_text()
- translate_batch()
- translate_verification_data()
```

### 4. Data Layer

#### Amazon RDS PostgreSQL
- **Version**: PostgreSQL 14
- **Instance**: db.t3.micro (dev) / db.t3.small (prod)
- **Storage**: 20GB SSD with auto-scaling
- **Backup**: 7-day retention
- **Multi-AZ**: Enabled in production

#### Database Schema
```sql
farmers
  - id (UUID PK)
  - phone (VARCHAR UNIQUE)
  - name (VARCHAR)
  - location (VARCHAR)
  - created_at (TIMESTAMP)

crop_batches
  - id (UUID PK)
  - farmer_id (UUID FK)
  - crop_name (VARCHAR)
  - crop_variety (VARCHAR)
  - farming_method (VARCHAR)
  - harvest_date (DATE)
  - created_at (TIMESTAMP)

treatments
  - id (UUID PK)
  - batch_id (UUID FK)
  - treatment_type (VARCHAR)
  - name (VARCHAR)
  - dosage_or_quantity (VARCHAR)
  - application_date (DATE)

crop_images
  - id (UUID PK)
  - batch_id (UUID FK)
  - image_url (TEXT)
  - rekognition_labels (JSONB)
  - uploaded_at (TIMESTAMP)

safety_analyses
  - id (UUID PK)
  - batch_id (UUID FK UNIQUE)
  - safety_score (DECIMAL)
  - risk_level (VARCHAR)
  - explanation (TEXT)
  - analyzed_at (TIMESTAMP)

qr_codes
  - id (UUID PK)
  - qr_id (VARCHAR UNIQUE)
  - batch_id (UUID FK UNIQUE)
  - qr_code_url (TEXT)
  - scan_count (INTEGER)
  - generated_at (TIMESTAMP)
```

#### Indexes
- `idx_farmers_phone` on farmers(phone)
- `idx_batches_farmer` on crop_batches(farmer_id)
- `idx_treatments_batch` on treatments(batch_id)
- `idx_images_batch` on crop_images(batch_id)
- `idx_qr_codes_qr_id` on qr_codes(qr_id)

### 5. AWS Services Layer

#### Amazon S3
- **Bucket**: farm2fork-images
- **Structure**:
  - `/pesticide/` - Pesticide package images
  - `/fertilizer/` - Fertilizer package images
  - `/crop/` - Crop images
  - `/seed_packet/` - Seed packet images
  - `/qr_code/` - Generated QR codes
- **Features**:
  - Versioning enabled
  - Lifecycle policies (30 days → Glacier)
  - CORS configured for frontend
  - Presigned URLs for direct upload

#### AWS Textract
- **API**: analyze_document
- **Features**: FORMS, TABLES
- **Use Cases**:
  - Pesticide package OCR
  - Fertilizer package OCR
  - Seed packet information
- **Confidence**: 70%+ threshold

#### AWS Rekognition
- **API**: detect_labels
- **MinConfidence**: 70%
- **MaxLabels**: 20
- **Use Cases**:
  - Crop quality assessment
  - Freshness detection
  - Disease identification

#### AWS Bedrock
- **Model**: Claude 3 Sonnet
- **Model ID**: anthropic.claude-3-sonnet-20240229-v1:0
- **Use Cases**:
  - Safety score generation (0-100)
  - Risk level classification
  - Consumption advice
  - Multi-language explanations

#### AWS Translate
- **Languages**: 10 Indian languages
- **Use Cases**:
  - UI translation
  - Safety explanation translation
  - Consumption advice translation

## Data Flow

### Farmer Flow: Create Batch

```
1. Farmer logs in
   Frontend → API Gateway → Backend → RDS
   ← JWT Token

2. Farmer creates batch
   Frontend → API Gateway → Backend → RDS
   ← Batch ID

3. Farmer uploads pesticide image
   Frontend → S3 (presigned URL)
   Frontend → Backend → Textract → Backend
   ← Extracted data

4. Farmer uploads crop images
   Frontend → S3 (presigned URL)
   Frontend → Backend → Rekognition → Backend
   ← Quality indicators

5. Backend runs AI analysis
   Backend → Bedrock (Claude 3)
   ← Safety score, risk level, explanation
   Backend → RDS (save analysis)

6. Farmer generates QR
   Backend → Generate QR ID
   Backend → Create QR image
   Backend → S3 (upload QR)
   Backend → RDS (save QR record)
   ← QR code image + ID
```

### Consumer Flow: Verify Product

```
1. Consumer scans QR
   Frontend (camera) → Decode QR ID

2. Fetch verification data
   Frontend → API Gateway → Backend → RDS
   ← Batch data, farmer info, safety analysis

3. (Optional) Translate
   Frontend → Backend → Translate
   ← Translated content

4. Display verification
   Frontend renders:
   - Crop information
   - Farmer details
   - Safety score
   - Risk level
   - Consumption advice
```

## Security Architecture

### Authentication & Authorization
- **Method**: JWT tokens
- **Storage**: localStorage (frontend)
- **Expiration**: 7 days
- **Refresh**: Manual re-login
- **Algorithm**: HS256

### API Security
- **CORS**: Configured origins only
- **Rate Limiting**: API Gateway (1000/min)
- **Input Validation**: Pydantic models
- **SQL Injection**: SQLAlchemy ORM
- **XSS**: React auto-escaping

### Data Security
- **Encryption at Rest**: RDS encryption
- **Encryption in Transit**: TLS 1.2+
- **S3 Encryption**: AES-256
- **Secrets**: AWS Secrets Manager
- **IAM**: Least privilege principle

### Network Security
- **VPC**: Private subnets for RDS
- **Security Groups**: Minimal ports
- **WAF**: API Gateway protection
- **DDoS**: CloudFront + Shield

## Scalability

### Horizontal Scaling
- **Backend**: Auto Scaling Group (2-10 instances)
- **Database**: Read replicas
- **S3**: Unlimited storage
- **CloudFront**: Global edge locations

### Vertical Scaling
- **RDS**: Upgrade instance class
- **EC2**: Upgrade instance type
- **Lambda**: Increase memory/timeout

### Caching Strategy
- **CloudFront**: Static assets (1 year)
- **API Gateway**: Response caching (5 min)
- **Application**: Redis (future)

## Monitoring & Observability

### CloudWatch Metrics
- API request count
- Error rate
- Response time (p50, p95, p99)
- Database connections
- S3 upload success rate

### CloudWatch Logs
- Application logs
- Access logs
- Error logs
- Audit logs

### Alarms
- High error rate (>1%)
- Slow response time (>1s)
- Database CPU (>80%)
- Failed health checks

### Tracing
- X-Ray for request tracing
- Distributed tracing across services

## Disaster Recovery

### Backup Strategy
- **RDS**: Automated daily backups (7 days)
- **S3**: Versioning enabled
- **Code**: Git repository

### Recovery Objectives
- **RTO**: 1 hour
- **RPO**: 24 hours

### Failover
- **Multi-AZ**: RDS automatic failover
- **Multi-Region**: CloudFront (future)

## Cost Optimization

### Current Costs (Monthly)
- EC2 t3.medium: $30
- RDS db.t3.micro: $15
- S3 (100GB): $2.30
- CloudFront: $1-5
- Bedrock: $10-50
- Textract/Rekognition: $5-20
- **Total**: ~$65-125/month

### Optimization Strategies
1. Reserved Instances (30-50% savings)
2. S3 Intelligent-Tiering
3. CloudFront caching
4. Lambda for sporadic workloads
5. Spot Instances for batch jobs

## Future Enhancements

### Phase 2
- [ ] Mobile app (React Native)
- [ ] Real-time notifications (SNS)
- [ ] Analytics dashboard
- [ ] Batch predictions (SageMaker)

### Phase 3
- [ ] Blockchain integration
- [ ] IoT sensor data
- [ ] Marketplace
- [ ] Multi-tenant support

### Phase 4
- [ ] Global expansion
- [ ] Regulatory compliance (FSSAI, FDA)
- [ ] Supply chain integration
- [ ] B2B API

## Technology Decisions

### Why FastAPI?
- High performance (async)
- Auto-generated docs
- Type safety
- Easy AWS integration

### Why PostgreSQL?
- ACID compliance
- JSON support
- Mature ecosystem
- AWS RDS support

### Why React?
- Component reusability
- Large ecosystem
- TypeScript support
- Performance

### Why AWS?
- Comprehensive AI services
- Global infrastructure
- Managed services
- Cost-effective

## Deployment Architecture

### Development
```
Local Machine
├── Backend (uvicorn)
├── Frontend (vite)
└── Database (SQLite)
```

### Staging
```
AWS
├── EC2 (t3.small)
├── RDS (db.t3.micro)
├── S3 (staging bucket)
└── CloudFront (staging dist)
```

### Production
```
AWS
├── Auto Scaling Group (2-10 x t3.medium)
├── Application Load Balancer
├── RDS Multi-AZ (db.t3.small)
├── S3 (production bucket)
├── CloudFront (production dist)
└── Route 53 (DNS)
```

## Conclusion

FARM2FORK is built with:
- ✅ Modern architecture
- ✅ AWS best practices
- ✅ Security first
- ✅ Scalability in mind
- ✅ Cost optimization
- ✅ Production-ready code

The system is ready for deployment and can scale from 100 to 1M+ users.
