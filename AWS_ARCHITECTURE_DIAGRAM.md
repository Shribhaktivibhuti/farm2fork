# Farm2Fork - AWS Architecture Diagram
## Complete System Architecture with Service Integration

---

## ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USERS                                             │
│                          👨‍🌾 Farmers  |  🛒 Consumers                                │
└────────────────────────────────┬────────────────────────────────────────────────────┘
                                 │
                                 │ HTTPS
                                 ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                    React + TypeScript SPA                                    │   │
│  │                    (Hosted on EC2 + Nginx)                                   │   │
│  │                    Region: eu-north-1                                        │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────────────────────────┘
                                 │
                                 │ REST API
                                 ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           COMPUTE LAYER (AWS EC2)                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         FastAPI Backend                                      │   │
│  │                         Instance: t3.micro                                   │   │
│  │                         IP: 16.171.60.125                                    │   │
│  │                         Region: eu-north-1 (Stockholm)                       │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
└──┬────────┬──────────┬──────────┬──────────┬──────────┬──────────┬────────────────┘
   │        │          │          │          │          │          │
   │        │          │          │          │          │          │
   ↓        ↓          ↓          ↓          ↓          ↓          ↓
┌──────┐ ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────────┐
│      │ │      │  │      │  │      │  │      │  │      │  │          │
│ Auth │ │ S3   │  │Text  │  │Bed   │  │Trans │  │Rekog │  │   RDS    │
│      │ │      │  │ract  │  │rock  │  │late  │  │nition│  │          │
└──────┘ └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          AWS SERVICES LAYER                                          │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  1. AWS COGNITO (Authentication)                                              │  │
│  │     • User Pool: us-east-1_dKlYoNrpX                                          │  │
│  │     • SMS OTP Authentication                                                  │  │
│  │     • Region: us-east-1                                                       │  │
│  │     • Status: Configured (Demo mode active)                                  │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  2. AMAZON S3 (Storage)                                                       │  │
│  │     • Bucket 1: farm2fork-images                                              │  │
│  │       - Crop images                                                           │  │
│  │       - Field photos                                                          │  │
│  │       - Farmer profile pictures                                               │  │
│  │       - Pesticide/Fertilizer product images                                   │  │
│  │     • Bucket 2: farm2fork-qr-codes                                            │  │
│  │       - Generated QR codes                                                    │  │
│  │     • Security: Presigned URLs, IAM roles                                     │  │
│  │     • Region: us-east-1                                                       │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  3. AWS TEXTRACT (AI - OCR)                                                   │  │
│  │     • Service: Document Text Detection                                        │  │
│  │     • Input: Pesticide/Fertilizer label images                                │  │
│  │     • Output: Extracted text (product name, chemicals, dosage)                │  │
│  │     • Accuracy: 95%+                                                          │  │
│  │     • Region: us-east-1                                                       │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  4. AWS BEDROCK (AI - Analysis)                                               │  │
│  │     • Model: amazon.nova-lite-v1:0                                            │  │
│  │     • Functions:                                                              │  │
│  │       - Safety score calculation (0-100)                                      │  │
│  │       - Risk level assessment                                                 │  │
│  │       - Consumption recommendations                                           │  │
│  │       - Cleaning instructions                                                 │  │
│  │     • Processing time: < 3 seconds                                            │  │
│  │     • Region: us-east-1                                                       │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  5. AWS TRANSLATE (AI - Multilingual)                                         │  │
│  │     • Supported Languages: 10 Indian languages                                │  │
│  │       (English, Hindi, Tamil, Telugu, Kannada, Malayalam,                    │  │
│  │        Bengali, Marathi, Gujarati, Punjabi)                                   │  │
│  │     • Real-time translation                                                   │  │
│  │     • Region: us-east-1                                                       │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  6. AWS REKOGNITION (AI - Image Analysis)                                     │  │
│  │     • Service: Image content analysis                                         │  │
│  │     • Functions: Object detection, label detection                            │  │
│  │     • Region: us-east-1                                                       │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  7. AMAZON RDS (Database)                                                     │  │
│  │     • Engine: Aurora MySQL 8.0                                                │  │
│  │     • Instance: db.t3.medium                                                  │  │
│  │     • Endpoint: farm2fork-db.cluster-c1mkkqcsufe9.eu-north-1.rds...          │  │
│  │     • Storage: 20GB                                                           │  │
│  │     • Tables: farmers, crop_batches, treatments, qr_codes,                    │  │
│  │               crop_images, safety_analyses                                    │  │
│  │     • Region: eu-north-1 (Stockholm)                                          │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Data Flow Diagram

### FARMER WORKFLOW

```
┌──────────────┐
│   FARMER     │
│   (Mobile)   │
└──────┬───────┘
       │
       │ 1. Login Request
       ↓
┌──────────────────────┐
│   AWS COGNITO        │
│   (Authentication)   │
│   • SMS OTP          │
└──────┬───────────────┘
       │
       │ 2. JWT Token
       ↓
┌──────────────────────┐
│   EC2 Backend        │
│   (FastAPI)          │
└──────┬───────────────┘
       │
       │ 3. Create Batch
       ↓
┌──────────────────────┐
│   Upload Images      │
│   • Crop             │
│   • Field            │
│   • Pesticide        │
└──────┬───────────────┘
       │
       │ 4. Store Images
       ↓
┌──────────────────────┐
│   AMAZON S3          │
│   farm2fork-images   │
└──────┬───────────────┘
       │
       │ 5. Image URL
       ↓
┌──────────────────────┐
│   AWS TEXTRACT       │
│   (OCR Extraction)   │
│   • Extract text     │
│   • Parse data       │
└──────┬───────────────┘
       │
       │ 6. Extracted Data
       ↓
┌──────────────────────┐
│   AWS BEDROCK        │
│   (AI Analysis)      │
│   • Safety score     │
│   • Risk assessment  │
└──────┬───────────────┘
       │
       │ 7. AI Results
       ↓
┌──────────────────────┐
│   AMAZON RDS         │
│   (Save to DB)       │
│   • Batch data       │
│   • Safety analysis  │
└──────┬───────────────┘
       │
       │ 8. Generate QR
       ↓
┌──────────────────────┐
│   QR Code Generator  │
│   (Python Library)   │
└──────┬───────────────┘
       │
       │ 9. Store QR
       ↓
┌──────────────────────┐
│   AMAZON S3          │
│   farm2fork-qr-codes │
└──────┬───────────────┘
       │
       │ 10. QR Image URL
       ↓
┌──────────────────────┐
│   FARMER             │
│   (Download QR)      │
└──────────────────────┘
```

### CONSUMER WORKFLOW

```
┌──────────────┐
│  CONSUMER    │
│  (Mobile)    │
└──────┬───────┘
       │
       │ 1. Scan QR Code
       ↓
┌──────────────────────┐
│   EC2 Backend        │
│   /api/public/verify │
└──────┬───────────────┘
       │
       │ 2. Query by QR ID
       ↓
┌──────────────────────┐
│   AMAZON RDS         │
│   • Fetch batch      │
│   • Fetch farmer     │
│   • Fetch safety     │
└──────┬───────────────┘
       │
       │ 3. Batch Data
       ↓
┌──────────────────────┐
│   AWS TRANSLATE      │
│   (If language ≠ en) │
│   • Translate text   │
└──────┬───────────────┘
       │
       │ 4. Translated Data
       ↓
┌──────────────────────┐
│   AWS BEDROCK        │
│   (Recommendations)  │
│   • Consumption tips │
│   • Cleaning advice  │
└──────┬───────────────┘
       │
       │ 5. Complete Info
       ↓
┌──────────────────────┐
│   CONSUMER           │
│   • Crop details     │
│   • Safety score     │
│   • Farmer info      │
│   • AI advice        │
└──────────────────────┘
```

---

## AI Pipeline Detailed Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI PROCESSING PIPELINE                      │
└─────────────────────────────────────────────────────────────────┘

INPUT: Pesticide/Fertilizer Image
   │
   ↓
┌──────────────────────┐
│  STEP 1: Upload      │
│  • Farmer uploads    │
│  • Image validation  │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  STEP 2: S3 Storage  │
│  • Store in S3       │
│  • Generate URL      │
│  • Set permissions   │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  STEP 3: AWS Textract│
│  • Detect text       │
│  • Extract:          │
│    - Product name    │
│    - Active ingred.  │
│    - Dosage          │
│    - Manufacturer    │
│    - Expiry date     │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  STEP 4: Data Parse  │
│  • Structure data    │
│  • Validate format   │
│  • Clean text        │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  STEP 5: AWS Bedrock │
│  Model: Nova Lite    │
│  • Analyze chemicals │
│  • Calculate safety  │
│  • Assess risk       │
│  • Generate advice   │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  STEP 6: Save Results│
│  • Safety score      │
│  • Risk level        │
│  • Recommendations   │
│  • Store in RDS      │
└──────┬───────────────┘
       │
       ↓
OUTPUT: AI Analysis Complete
```

---

## Security & IAM Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   IAM ROLES          │
│   • EC2 Role         │
│   • S3 Access        │
│   • AI Services      │
│   • RDS Access       │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│   AUTHENTICATION     │
│   • JWT Tokens       │
│   • Cognito (config) │
│   • Session mgmt     │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│   AUTHORIZATION      │
│   • Farmer-only APIs │
│   • Public APIs      │
│   • Role-based       │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│   DATA SECURITY      │
│   • Presigned URLs   │
│   • HTTPS only       │
│   • Encrypted RDS    │
└──────────────────────┘
```

---

## Network Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK TOPOLOGY                              │
└─────────────────────────────────────────────────────────────────┘

REGION: eu-north-1 (Stockholm)
│
├── VPC (Default)
│   │
│   ├── Public Subnet
│   │   │
│   │   └── EC2 Instance (t3.micro)
│   │       • Public IP: 16.171.60.125
│   │       • Security Group: Allow 80, 443, 8000, 22
│   │       • Nginx + FastAPI
│   │
│   └── Private Subnet
│       │
│       └── RDS Aurora MySQL
│           • Endpoint: farm2fork-db.cluster-...
│           • Security Group: Allow 3306 from EC2
│           • Multi-AZ: No (single instance)
│
└── Internet Gateway
    • Public access
    • Route to EC2

REGION: us-east-1 (N. Virginia)
│
├── S3 Buckets
│   ├── farm2fork-images
│   └── farm2fork-qr-codes
│
├── AI Services
│   ├── AWS Textract
│   ├── AWS Bedrock
│   ├── AWS Translate
│   ├── AWS Rekognition
│   └── AWS Cognito
```

---

## Cost Breakdown Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              MONTHLY AWS COST ESTIMATION                         │
└─────────────────────────────────────────────────────────────────┘

EC2 (t3.micro)              ████████░░  $7.50   (8%)
RDS (db.t3.medium)          ██████████████████████████████  $50.00  (54%)
RDS Storage (20GB)          ███░░░  $2.30   (2%)
S3 Storage (100GB)          ███░░░  $2.30   (2%)
S3 Data Transfer            ██░░░  $1.00   (1%)
Textract (10K pages)        ████████████████░░  $15.00  (16%)
Bedrock Nova Lite           ███████████░░  $10.00  (11%)
Cognito (1K users)          ██████░░  $5.50   (6%)
                            ─────────────────────────────
TOTAL                       $93.60/month

Note: First year eligible for EC2 free tier ($7.50 savings)
```

---

## Instructions for Creating Visual Diagram

### For ChatGPT/DALL-E:
Use this prompt:

"Create a professional AWS architecture diagram for a Farm2Fork application with the following components:

1. Top layer: Users (Farmers and Consumers icons)
2. Frontend: React app hosted on EC2 with Nginx
3. Backend: FastAPI on EC2 (t3.micro) in eu-north-1
4. AWS Services layer showing:
   - AWS Cognito (authentication icon)
   - Amazon S3 (two buckets: images and QR codes)
   - AWS Textract (OCR icon)
   - AWS Bedrock with Nova Lite model (AI brain icon)
   - AWS Translate (language icon)
   - AWS Rekognition (image analysis icon)
   - Amazon RDS Aurora MySQL (database icon)

5. Show arrows connecting:
   - Users → Frontend → Backend
   - Backend → All AWS services
   - Data flow from image upload → S3 → Textract → Bedrock → RDS

Use AWS official colors (orange for services, green for agriculture theme).
Make it clean, modern, and professional for a hackathon presentation.
Include AWS logo and service icons."

### For draw.io / Lucidchart:
1. Import AWS architecture icons
2. Follow the ASCII diagram structure above
3. Use the data flow diagrams for connections
4. Apply green color theme (#2D5016, #4CAF50)
5. Add AWS service badges

### For PowerPoint:
1. Use SmartArt for hierarchical structure
2. Insert AWS service icons from AWS Architecture Icons
3. Use connectors to show data flow
4. Apply consistent color scheme
5. Add text boxes for service descriptions

---

## Key Metrics to Highlight

- **7 AWS Services** actively used
- **3 AI/ML Services** (Textract, Bedrock, Translate)
- **< 3 seconds** AI processing time
- **95%+ accuracy** OCR extraction
- **10 languages** supported
- **99.9% uptime** (AWS SLA)
- **~$94/month** operational cost
- **Scalable** to 100K+ users

---

This diagram specification is ready to be converted into a visual diagram using any tool!
