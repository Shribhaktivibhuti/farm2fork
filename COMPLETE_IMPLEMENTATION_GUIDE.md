# FARM2FORK Complete Implementation Guide

## Executive Summary
This guide provides the complete implementation for rebuilding FARM2FORK as a production-ready AWS-native system. All AWS services are already implemented in the codebase - we just need to wire them together properly.

## Current Status
✅ **Already Implemented:**
- All AWS service classes (S3, Textract, Rekognition, Bedrock, Translate)
- Database models (PostgreSQL/SQLite compatible)
- Authentication (JWT-based)
- Basic CRUD operations

❌ **Needs Implementation:**
- Multi-step batch creation wizard
- Presigned URL endpoints for direct S3 upload
- Frontend wizard components
- QR scanner with html5-qrcode
- Language selector and translation
- Deployment scripts

## Implementation Roadmap

### STEP 1: Backend API Enhancements (2-3 hours)

#### 1.1 Add Presigned URL Endpoint
```python
# Add to backend/main.py

@app.post("/api/upload/presigned-url")
async def get_presigned_url(
    file_type: str = Query(..., regex="^(pesticide|fertilizer|crop|seed_packet)$"),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Generate presigned URL for direct S3 upload from frontend"""
    s3_service = S3Service()
    
    # Generate unique key
    file_key = f"{file_type}/{uuid.uuid4()}.jpg"
    
    # Generate presigned URL (valid for 1 hour)
    presigned_url = s3_service.generate_presigned_url(
        file_key=file_key,
        expiration=3600
    )
    
    # Return both presigned URL and final S3 URL
    s3_url = s3_service._get_public_url(file_key)
    
    return {
        "success": True,
        "presigned_url": presigned_url,
        "s3_url": s3_url,
        "file_key": file_key
    }
```

#### 1.2 Add Textract Extraction Endpoint
```python
@app.post("/api/extract/pesticide")
async def extract_pesticide_info(
    s3_url: str,
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Extract pesticide information from uploaded image"""
    # Parse S3 URL to get bucket and key
    bucket_name = os.getenv('S3_BUCKET_NAME')
    file_key = s3_url.split(f"{bucket_name}.s3.")[1].split("/", 1)[1]
    
    textract_service = TextractService()
    
    # Extract text
    extracted_data = textract_service.extract_from_image(bucket_name, file_key)
    
    # Parse pesticide-specific info
    pesticide_info = textract_service.extract_pesticide_info(extracted_data)
    
    return {
        "success": True,
        "extracted_data": pesticide_info,
        "raw_text": extracted_data['raw_text'],
        "confidence": extracted_data['confidence']
    }
```

#### 1.3 Add AI Analysis Endpoint
```python
@app.post("/api/batch/analyze")
async def analyze_batch(
    batch_id: str,
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Run AI analysis on batch using Rekognition and Bedrock"""
    # Get batch
    batch = db.query(CropBatch).filter(
        CropBatch.id == batch_id,
        CropBatch.farmer_id == farmer_id
    ).first()
    
    if not batch:
        raise NotFoundError("Batch not found")
    
    # Get treatments
    treatments = db.query(Treatment).filter(Treatment.batch_id == batch_id).all()
    pesticides = [t for t in treatments if t.treatment_type == 'pesticide']
    fertilizers = [t for t in treatments if t.treatment_type == 'fertilizer']
    
    # Analyze crop images with Rekognition
    rekognition_data = None
    crop_images = db.query(CropImage).filter(CropImage.batch_id == batch_id).first()
    if crop_images:
        rekognition_service = RekognitionService()
        bucket_name = os.getenv('S3_BUCKET_NAME')
        file_key = crop_images.image_url.split(f"{bucket_name}.s3.")[1].split("/", 1)[1]
        rekognition_data = rekognition_service.analyze_crop_image(bucket_name, file_key)
    
    # Generate safety analysis with Bedrock
    bedrock_service = BedrockService()
    safety_analysis = bedrock_service.generate_safety_analysis(
        crop_name=batch.crop_name,
        farming_method=batch.farming_method,
        pesticides=[{
            'name': p.name,
            'dosage_or_quantity': p.dosage_or_quantity,
            'application_date': str(p.application_date)
        } for p in pesticides],
        fertilizers=[{
            'name': f.name,
            'dosage_or_quantity': f.dosage_or_quantity,
            'application_date': str(f.application_date)
        } for f in fertilizers],
        harvest_date=str(batch.harvest_date),
        rekognition_data=rekognition_data
    )
    
    # Save to database
    analysis = SafetyAnalysis(
        batch_id=batch_id,
        safety_score=safety_analysis['safety_score'],
        risk_level=safety_analysis['risk_level'],
        explanation=safety_analysis['explanation'],
        bedrock_model='claude-3-sonnet'
    )
    db.add(analysis)
    db.commit()
    
    return {
        "success": True,
        "safety_analysis": safety_analysis,
        "rekognition_data": rekognition_data
    }
```

#### 1.4 Add Translation Endpoint
```python
@app.post("/api/public/translate")
async def translate_verification(
    qr_id: str,
    target_language: str = Query(..., regex="^(en|hi|ta|te|kn|ml|bn|mr|gu|pa)$"),
    db: Session = Depends(get_db)
):
    """Translate verification data to target language"""
    # Get verification data
    qr_code = db.query(QRCode).filter(QRCode.qr_id == qr_id).first()
    if not qr_code:
        raise NotFoundError("QR code not found")
    
    batch = db.query(CropBatch).filter(CropBatch.id == qr_code.batch_id).first()
    safety = db.query(SafetyAnalysis).filter(SafetyAnalysis.batch_id == batch.id).first()
    
    # Build verification data
    verification_data = {
        'safety_analysis': {
            'explanation': safety.explanation if safety else "No analysis available"
        }
    }
    
    # Translate
    translate_service = TranslateService()
    translated_data = translate_service.translate_verification_data(
        verification_data,
        target_language
    )
    
    return {
        "success": True,
        "translated_data": translated_data,
        "language": target_language
    }
```

### STEP 2: Frontend Wizard Implementation (3-4 hours)

#### 2.1 Install Required Packages
```bash
cd frontend
npm install html5-qrcode axios
```

#### 2.2 Create API Service with Interceptor
```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/farmer/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### 2.3 Create Batch Wizard Component
```typescript
// frontend/src/components/BatchWizard.tsx
import React, { useState } from 'react';
import apiClient from '../services/api';

const CROPS = {
  "Tomato": ["Cherry", "Beefsteak", "Roma", "Heirloom"],
  "Potato": ["Russet", "Red", "Yukon Gold", "Fingerling"],
  "Onion": ["Red", "White", "Yellow", "Sweet"],
  "Rice": ["Basmati", "Jasmine", "Arborio", "Brown"],
  "Wheat": ["Hard Red", "Soft White", "Durum", "Spelt"],
  "Carrot": ["Nantes", "Imperator", "Chantenay", "Baby"]
};

export default function BatchWizard() {
  const [step, setStep] = useState(1);
  const [batchData, setBatchData] = useState({
    crop_name: '',
    crop_variety: '',
    farming_method: 'organic',
    harvest_date: '',
    quantity: '',
    location: '',
    pesticides: [],
    crop_images: []
  });

  // Step 1: Crop Selection
  const renderStep1 = () => (
    <div>
      <h2>Step 1: Select Crop</h2>
      <select onChange={(e) => setBatchData({...batchData, crop_name: e.target.value})}>
        <option value="">Select Crop</option>
        {Object.keys(CROPS).map(crop => (
          <option key={crop} value={crop}>{crop}</option>
        ))}
      </select>
      
      {batchData.crop_name && (
        <select onChange={(e) => setBatchData({...batchData, crop_variety: e.target.value})}>
          <option value="">Select Variety</option>
          {CROPS[batchData.crop_name].map(variety => (
            <option key={variety} value={variety}>{variety}</option>
          ))}
        </select>
      )}
      
      <button onClick={() => setStep(2)}>Next</button>
    </div>
  );

  // Step 2: Harvest Details
  const renderStep2 = () => (
    <div>
      <h2>Step 2: Harvest Details</h2>
      <input 
        type="date" 
        value={batchData.harvest_date}
        onChange={(e) => setBatchData({...batchData, harvest_date: e.target.value})}
      />
      <input 
        type="text" 
        placeholder="Quantity (kg)"
        value={batchData.quantity}
        onChange={(e) => setBatchData({...batchData, quantity: e.target.value})}
      />
      <input 
        type="text" 
        placeholder="Farm Location"
        value={batchData.location}
        onChange={(e) => setBatchData({...batchData, location: e.target.value})}
      />
      <button onClick={() => setStep(1)}>Back</button>
      <button onClick={() => setStep(3)}>Next</button>
    </div>
  );

  // Step 3: Pesticide Upload
  const renderStep3 = () => {
    const handlePesticideUpload = async (file: File) => {
      // Get presigned URL
      const { data } = await apiClient.post('/api/upload/presigned-url', {
        file_type: 'pesticide'
      });
      
      // Upload to S3
      await axios.put(data.presigned_url, file, {
        headers: { 'Content-Type': 'image/jpeg' }
      });
      
      // Extract text
      const extractResult = await apiClient.post('/api/extract/pesticide', {
        s3_url: data.s3_url
      });
      
      // Add to batch data
      setBatchData({
        ...batchData,
        pesticides: [...batchData.pesticides, extractResult.data.extracted_data]
      });
    };

    return (
      <div>
        <h2>Step 3: Upload Pesticide Packages</h2>
        <input type="file" accept="image/*" onChange={(e) => {
          if (e.target.files?.[0]) handlePesticideUpload(e.target.files[0]);
        }} />
        
        {batchData.pesticides.map((p, i) => (
          <div key={i}>
            <p>Name: {p.name}</p>
            <p>Dosage: {p.dosage}</p>
          </div>
        ))}
        
        <button onClick={() => setStep(2)}>Back</button>
        <button onClick={() => setStep(4)}>Next</button>
      </div>
    );
  };

  // Render current step
  return (
    <div className="wizard">
      {step === 1 && renderStep1()}
      {step === 2 && renderStep2()}
      {step === 3 && renderStep3()}
      {/* Add steps 4, 5, 6 similarly */}
    </div>
  );
}
```

#### 2.4 Create QR Scanner Component
```typescript
// frontend/src/components/QRScanner.tsx
import React, { useEffect } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { useNavigate } from 'react-router-dom';

export default function QRScanner() {
  const navigate = useNavigate();

  useEffect(() => {
    const scanner = new Html5QrcodeScanner(
      "qr-reader",
      { fps: 10, qrbox: 250 },
      false
    );

    scanner.render(
      (decodedText) => {
        scanner.clear();
        navigate(`/consumer/verify/${decodedText}`);
      },
      (error) => {
        console.warn(error);
      }
    );

    return () => {
      scanner.clear();
    };
  }, [navigate]);

  return (
    <div>
      <h2>Scan QR Code</h2>
      <div id="qr-reader" style={{ width: '100%' }}></div>
    </div>
  );
}
```

### STEP 3: Deployment Setup (1-2 hours)

#### 3.1 Backend Dockerfile
```dockerfile
# deployment/backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.2 Frontend Build Script
```bash
# deployment/frontend/build-deploy.sh
#!/bin/bash

cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://farm2fork-frontend --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

#### 3.3 Environment Variables
```bash
# backend/.env.production
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/farm2fork
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
S3_BUCKET_NAME=farm2fork-images
JWT_SECRET_KEY=your_production_secret
CORS_ORIGINS=https://farm2fork.com
```

### STEP 4: Testing (1 hour)

#### 4.1 Create Postman Collection
Export collection with all endpoints:
- Authentication
- Batch creation wizard (all steps)
- Dashboard endpoints
- Public verification
- Translation

#### 4.2 Manual Testing Checklist
- [ ] Login with phone + OTP
- [ ] Create batch through wizard
- [ ] Upload pesticide image
- [ ] Auto-extract pesticide info
- [ ] Upload crop images
- [ ] Run AI analysis
- [ ] Generate QR code
- [ ] Scan QR code
- [ ] View verification
- [ ] Translate to Hindi

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database
cd backend
python init_db.py

# Docker
docker build -t farm2fork-backend .
docker run -p 8000:8000 --env-file .env farm2fork-backend
```

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ├─────────────────────────────────┐
       │                                 │
┌──────▼──────┐                  ┌──────▼──────┐
│  Frontend   │                  │   Backend   │
│  (React)    │                  │  (FastAPI)  │
│  S3 + CF    │                  │     EC2     │
└─────────────┘                  └──────┬──────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
             ┌──────▼──────┐     ┌─────▼─────┐      ┌─────▼─────┐
             │     RDS     │     │    S3     │      │  Bedrock  │
             │ PostgreSQL  │     │  Images   │      │  Claude   │
             └─────────────┘     └───────────┘      └───────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
             ┌──────▼──────┐     ┌─────▼─────┐      ┌─────▼─────┐
             │  Textract   │     │Rekognition│      │ Translate │
             │     OCR     │     │   Vision  │      │10 Languages│
             └─────────────┘     └───────────┘      └───────────┘
```

## Estimated Timeline
- Backend API: 2-3 hours
- Frontend Wizard: 3-4 hours
- AWS Integration: 2 hours (already done)
- Deployment Setup: 1-2 hours
- Testing: 1 hour
- Documentation: 1 hour

**Total: 10-13 hours for complete implementation**

## Success Criteria
✅ Farmer can login and create batch through 6-step wizard
✅ Pesticide images auto-extract text using Textract
✅ Crop images analyzed with Rekognition
✅ AI generates safety score using Bedrock
✅ QR code generated and downloadable
✅ Consumer can scan QR with camera
✅ Verification shows all crop details
✅ Translation works for 10 languages
✅ System deployed on AWS
✅ Postman collection provided
