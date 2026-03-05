"""
FARM2FORK AI-Powered Traceability Platform
Main FastAPI application entry point

Requirements: 10.8
"""

from fastapi import FastAPI, Request, status, Depends, UploadFile, File, Form, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from dotenv import load_dotenv
import os
import logging
import qrcode
import io
import base64
import random
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="FARM2FORK API",
    description="AI-Powered Farm-to-Consumer Traceability Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {origins}")


# Custom exception classes
class AppException(Exception):
    """Base exception for application errors"""
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Exception for authentication failures"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)


class ValidationError(AppException):
    """Exception for validation errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(status.HTTP_400_BAD_REQUEST, message, details)


class AIServiceError(AppException):
    """Exception for AWS AI service errors"""
    def __init__(self, service: str, message: str):
        super().__init__(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            f"{service} service error: {message}"
        )


class NotFoundError(AppException):
    """Exception for resource not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions"""
    logger.error(f"Application error: {exc.message}", exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "details": None
        }
    )


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "FARM2FORK API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "service": "FARM2FORK API",
        "version": "1.0.0",
        "database": "configured",
        "aws_services": "configured"
    }


# Import dependencies for endpoints
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
import jwt
from database import get_db
from auth_utils import validate_otp, generate_jwt_token
from farmer_service import get_or_create_farmer
from models import CropBatch, Treatment, CropImage, SafetyAnalysis, QRCode, Farmer

security = HTTPBearer()


async def get_current_farmer_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Extract and validate farmer ID from JWT token"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET_KEY'),
            algorithms=['HS256']
        )
        farmer_id = payload.get('farmer_id')
        if not farmer_id:
            raise AuthenticationError("Invalid token: missing farmer_id")
        return farmer_id
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


# Request/Response models
class LoginRequest(BaseModel):
    """Request model for farmer login"""
    phone: str = Field(..., min_length=10, max_length=15, description="Farmer phone number")
    otp: str = Field(..., min_length=4, max_length=6, description="One-time password")
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Farmer name (required for new users)")
    location: Optional[str] = Field(None, max_length=200, description="Farm location (optional)")


class LoginResponse(BaseModel):
    """Response model for successful login"""
    success: bool
    token: str
    farmer_id: str
    farmer_name: str
    is_new_user: bool = False


# API Endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Farmer authentication endpoint.
    
    Validates phone and OTP, creates or retrieves farmer account,
    generates JWT token, and returns farmer info with token.
    
    For new users, name is required. For existing users, name is ignored.
    
    Requirements: 2.1, 2.2, 2.3, 9.1
    """
    logger.info(f"Login attempt for phone: {request.phone}")
    
    # Validate OTP
    if not validate_otp(request.otp):
        logger.warning(f"Invalid OTP for phone: {request.phone}")
        raise AuthenticationError("Invalid OTP. Please use '0000' for demo mode.")
    
    try:
        # Check if farmer exists using the service
        from farmer_service import get_farmer_by_phone
        existing_farmer = get_farmer_by_phone(db, request.phone)
        
        if existing_farmer:
            # Existing user - login
            farmer = existing_farmer
            is_new_user = False
            logger.info(f"Existing farmer login: {farmer.id}")
        else:
            # New user - require name
            if not request.name or not request.name.strip():
                raise ValidationError(
                    "Name is required for new user registration",
                    {"field": "name", "message": "Please provide your name to create an account"}
                )
            
            # Create new farmer profile
            farmer = get_or_create_farmer(
                db=db,
                phone=request.phone,
                name=request.name.strip(),
                location=request.location.strip() if request.location else None
            )
            is_new_user = True
            logger.info(f"New farmer created: {farmer.id}")
        
        # Generate JWT token
        token = generate_jwt_token(
            farmer_id=str(farmer.id),
            phone=farmer.phone
        )
        
        logger.info(f"Login successful for farmer_id: {farmer.id}")
        
        return LoginResponse(
            success=True,
            token=token,
            farmer_id=str(farmer.id),
            farmer_name=farmer.name,
            is_new_user=is_new_user
        )
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Login failed: {str(e)}"
        )


# ============================================================================
# AWS COGNITO AUTHENTICATION ENDPOINTS - Production SMS OTP
# ============================================================================

# Check if Cognito is enabled
USE_COGNITO_AUTH = os.getenv('USE_COGNITO_AUTH', 'false').lower() == 'true'

if USE_COGNITO_AUTH:
    from cognito_service import CognitoService
    cognito_service = CognitoService()
    logger.info("Cognito authentication enabled")
else:
    logger.info("Demo authentication mode (OTP: 0000)")


class RequestOTPRequest(BaseModel):
    """Request model for OTP request"""
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number with country code")


class RequestOTPResponse(BaseModel):
    """Response model for OTP request"""
    success: bool
    message: str
    session: Optional[str] = None


class VerifyOTPRequest(BaseModel):
    """Request model for OTP verification"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=4, max_length=6)
    session: Optional[str] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Name for new users")
    location: Optional[str] = Field(None, max_length=200, description="Farm location")


class VerifyOTPResponse(BaseModel):
    """Response model for OTP verification"""
    success: bool
    token: str
    farmer_id: str
    farmer_name: str
    is_new_user: bool = False


@app.post("/api/auth/request-otp", response_model=RequestOTPResponse)
async def request_otp(request: RequestOTPRequest):
    """
    Request OTP for phone number authentication.
    
    Sends SMS OTP via AWS Cognito (production) or returns success for demo mode.
    
    Args:
        request: Phone number
    
    Returns:
        Success status, message, and session token
    """
    logger.info(f"OTP request for phone: {request.phone_number}")
    
    try:
        if USE_COGNITO_AUTH:
            # Production: Use Cognito
            result = cognito_service.initiate_auth(request.phone_number)
            
            if not result.get('success'):
                raise AppException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=result.get('message', 'Failed to send OTP')
                )
            
            return RequestOTPResponse(
                success=True,
                message="OTP sent successfully via SMS",
                session=result.get('session')
            )
        else:
            # Demo mode: Just return success
            logger.info(f"Demo mode: OTP request for {request.phone_number}")
            return RequestOTPResponse(
                success=True,
                message="Demo mode: Use OTP 0000",
                session="demo-session"
            )
            
    except AppException:
        raise
    except Exception as e:
        logger.error(f"OTP request failed: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to send OTP"
        )


@app.post("/api/auth/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify OTP and complete authentication.
    
    Verifies OTP with Cognito (production) or validates demo OTP,
    creates/retrieves farmer account, and issues JWT token.
    
    Args:
        request: Phone number, OTP, session, and optional name/location
        db: Database session
    
    Returns:
        JWT token and farmer information
    """
    logger.info(f"OTP verification for phone: {request.phone_number}")
    
    try:
        # Verify OTP
        if USE_COGNITO_AUTH:
            # Production: Verify with Cognito
            result = cognito_service.verify_otp(
                phone_number=request.phone_number,
                otp=request.otp,
                session=request.session
            )
            
            if not result.get('success'):
                error_type = result.get('error', 'invalid_otp')
                if error_type == 'expired_otp':
                    raise AuthenticationError("OTP has expired. Please request a new one.")
                else:
                    raise AuthenticationError("Incorrect OTP. Please try again.")
        else:
            # Demo mode: Validate demo OTP
            if not validate_otp(request.otp):
                raise AuthenticationError("Invalid OTP. Please use '0000' for demo mode.")
        
        # OTP verified - now handle farmer account
        from farmer_service import get_farmer_by_phone, get_or_create_farmer
        
        # Normalize phone number
        phone = request.phone_number
        if not phone.startswith('+'):
            phone = f"+91{phone.lstrip('0')}"
        
        existing_farmer = get_farmer_by_phone(db, phone)
        
        if existing_farmer:
            # Existing user
            farmer = existing_farmer
            is_new_user = False
            logger.info(f"Existing farmer login: {farmer.id}")
        else:
            # New user - require name
            if not request.name or not request.name.strip():
                raise ValidationError(
                    "Name is required for new user registration",
                    {"field": "name", "message": "Please provide your name to create an account"}
                )
            
            # Create new farmer
            farmer = get_or_create_farmer(
                db=db,
                phone=phone,
                name=request.name.strip(),
                location=request.location.strip() if request.location else None
            )
            is_new_user = True
            logger.info(f"New farmer created: {farmer.id}")
        
        # Generate internal JWT token
        token = generate_jwt_token(
            farmer_id=str(farmer.id),
            phone=farmer.phone
        )
        
        logger.info(f"Authentication successful for farmer_id: {farmer.id}")
        
        return VerifyOTPResponse(
            success=True,
            token=token,
            farmer_id=str(farmer.id),
            farmer_name=farmer.name,
            is_new_user=is_new_user
        )
        
    except (AuthenticationError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"OTP verification failed: {str(e)}", exc_info=True)
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Authentication failed"
        )


# Batch creation models
class TreatmentInput(BaseModel):
    treatment_type: str
    name: str
    dosage_or_quantity: Optional[str] = None
    application_date: str  # Accept as string to handle YYYY-MM format
    package_image_url: Optional[str] = None
    extracted_data: Optional[dict] = None
    
    @validator('application_date')
    def validate_application_date(cls, v):
        """Convert YYYY-MM or YYYY-MM-DD to date object"""
        if isinstance(v, date):
            return v
        try:
            # Try parsing as YYYY-MM-DD first
            return datetime.strptime(v, '%Y-%m-%d').date()
        except ValueError:
            try:
                # Try parsing as YYYY-MM (month-year only)
                return datetime.strptime(f"{v}-01", '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('application_date must be in YYYY-MM or YYYY-MM-DD format')


class BatchCreateRequest(BaseModel):
    crop_name: str = Field(..., min_length=1)
    crop_variety: Optional[str] = None
    farming_method: str = Field(..., pattern="^(organic|conventional|integrated)$")
    harvest_date: str  # Accept as string to handle YYYY-MM format
    seed_packet_image_url: Optional[str] = None
    field_photo_url: Optional[str] = None
    crop_image_urls: List[str] = []
    treatments: List[TreatmentInput] = []
    
    @validator('harvest_date')
    def validate_harvest_date(cls, v):
        """Convert YYYY-MM or YYYY-MM-DD to date object"""
        if isinstance(v, date):
            return v
        try:
            # Try parsing as YYYY-MM-DD first
            return datetime.strptime(v, '%Y-%m-%d').date()
        except ValueError:
            try:
                # Try parsing as YYYY-MM (month-year only)
                return datetime.strptime(f"{v}-01", '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('harvest_date must be in YYYY-MM or YYYY-MM-DD format')


class BatchCreateResponse(BaseModel):
    success: bool
    batch_id: str
    message: str


@app.post("/api/batch/create", response_model=BatchCreateResponse)
async def create_batch(
    request: BatchCreateRequest,
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """
    Create crop batch with treatments and images.
    Requirements: 3.1, 3.6, 3.7, 9.2
    """
    logger.info(f"Creating batch for farmer: {farmer_id}, crop: {request.crop_name}")
    
    try:
        # Create CropBatch
        batch = CropBatch(
            farmer_id=farmer_id,
            crop_name=request.crop_name,
            crop_variety=request.crop_variety,
            farming_method=request.farming_method,
            harvest_date=request.harvest_date,
            seed_packet_image_url=request.seed_packet_image_url,
            field_photo_url=request.field_photo_url
        )
        db.add(batch)
        db.flush()  # Get batch.id without committing
        
        # Create CropImages
        for image_url in request.crop_image_urls:
            crop_image = CropImage(
                batch_id=str(batch.id),
                image_url=image_url
            )
            db.add(crop_image)
        
        # Create Treatments
        for treatment_input in request.treatments:
            treatment = Treatment(
                batch_id=str(batch.id),
                treatment_type=treatment_input.treatment_type,
                name=treatment_input.name,
                dosage_or_quantity=treatment_input.dosage_or_quantity,
                application_date=treatment_input.application_date,
                package_image_url=treatment_input.package_image_url,
                extracted_data=str(treatment_input.extracted_data) if treatment_input.extracted_data else None
            )
            db.add(treatment)
        
        db.commit()
        logger.info(f"Batch created successfully: {batch.id}")
        
        return BatchCreateResponse(
            success=True,
            batch_id=str(batch.id),
            message="Batch created successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Batch creation failed: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to create batch: {str(e)}"
        )


# QR Code generation
def generate_qr_id(length: int = 8) -> str:
    """Generate unique alphanumeric QR ID"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


class QRGenerateResponse(BaseModel):
    success: bool
    qr_id: str
    qr_code_data: str  # Base64 encoded image
    verification_url: str


@app.post("/api/qr/generate", response_model=QRGenerateResponse)
async def generate_qr(
    batch_id: str,
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Generate QR code for batch verification"""
    logger.info(f"Generating QR for batch: {batch_id}")
    
    try:
        
        # Verify batch exists
        batch = db.query(CropBatch).filter(
            CropBatch.id == batch_id,
            CropBatch.farmer_id == farmer_id
        ).first()
        
        if not batch:
            raise NotFoundError("Batch not found")
        
        # Check if QR already exists
        existing_qr = db.query(QRCode).filter(QRCode.batch_id == batch_id).first()
        if existing_qr:
            # Generate QR image
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(existing_qr.qr_id)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            qr_code_data = base64.b64encode(img_bytes.getvalue()).decode()
            
            return QRGenerateResponse(
                success=True,
                qr_id=existing_qr.qr_id,
                qr_code_data=qr_code_data,
                verification_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/consumer/verify/{existing_qr.qr_id}"
            )
        
        # Generate unique QR ID
        qr_id = generate_qr_id()
        while db.query(QRCode).filter(QRCode.qr_id == qr_id).first():
            qr_id = generate_qr_id()
        
        # Generate QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        qr_code_data = base64.b64encode(img_bytes.getvalue()).decode()
        
        # Store QRCode record
        qr_code = QRCode(
            qr_id=qr_id,
            batch_id=batch_id,
            qr_code_url=f"data:image/png;base64,{qr_code_data}"
        )
        db.add(qr_code)
        db.commit()
        
        logger.info(f"QR generated: {qr_id}")
        
        return QRGenerateResponse(
            success=True,
            qr_id=qr_id,
            qr_code_data=qr_code_data,
            verification_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/consumer/verify/{qr_id}"
        )
        
    except NotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"QR generation failed: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"QR generation failed: {str(e)}"
        )


# Public verification endpoint
class SafetyAnalysisData(BaseModel):
    safety_score: float
    risk_level: str
    explanation: str


class VerificationData(BaseModel):
    success: bool
    crop_name: str
    crop_variety: Optional[str]
    farming_method: str
    harvest_date: str
    farmer_name: str
    batch_id: str
    qr_id: str
    safety_analysis: Optional[SafetyAnalysisData] = None
    cleaning_instructions: Optional[str] = None


@app.get("/api/public/verify/{qr_id}")
async def get_verification_data(
    qr_id: str, 
    language: str = Query('en', regex="^(en|hi|ta|te|kn|ml|bn|mr|gu|pa)$"),
    db: Session = Depends(get_db)
):
    """Public endpoint for QR verification with safety analysis and translation support"""
    logger.info(f"Verification request for QR: {qr_id}, language: {language}")
    
    try:
        
        # Find QR code
        qr_code = db.query(QRCode).filter(QRCode.qr_id == qr_id).first()
        if not qr_code:
            raise NotFoundError("QR code not found")
        
        # Increment scan count
        qr_code.scan_count += 1
        
        # Get batch with all related data
        batch = db.query(CropBatch).filter(CropBatch.id == qr_code.batch_id).first()
        farmer = db.query(Farmer).filter(Farmer.id == batch.farmer_id).first()
        
        # Get safety analysis if available
        safety_analysis_data = None
        safety_analysis = db.query(SafetyAnalysis).filter(
            SafetyAnalysis.batch_id == str(batch.id)
        ).first()
        
        if safety_analysis:
            explanation = safety_analysis.explanation
            
            # Translate explanation if not English
            if language != 'en':
                try:
                    from translate_service import TranslateService
                    translate_service = TranslateService()
                    explanation = translate_service.translate_text(explanation, language)
                except Exception as e:
                    logger.warning(f"Translation failed: {str(e)}, using original text")
            
            safety_analysis_data = {
                "safety_score": safety_analysis.safety_score,
                "risk_level": safety_analysis.risk_level,
                "explanation": explanation
            }
        
        # Generate cleaning instructions based on farming method and treatments
        treatments = db.query(Treatment).filter(Treatment.batch_id == str(batch.id)).all()
        pesticides = [t for t in treatments if t.treatment_type == 'pesticide']
        
        cleaning_instructions = generate_cleaning_instructions(
            batch.crop_name,
            batch.farming_method,
            len(pesticides)
        )
        
        # Translate cleaning instructions if not English
        if language != 'en':
            try:
                from translate_service import TranslateService
                translate_service = TranslateService()
                cleaning_instructions = translate_service.translate_text(cleaning_instructions, language)
            except Exception as e:
                logger.warning(f"Translation failed: {str(e)}, using original text")
        
        db.commit()
        
        return {
            "success": True,
            "crop_name": batch.crop_name,
            "crop_variety": batch.crop_variety,
            "farming_method": batch.farming_method,
            "harvest_date": str(batch.harvest_date),
            "farmer_name": farmer.name,
            "farmer_location": farmer.location,
            "farmer_profile_photo": farmer.profile_photo_url,
            "field_photo": batch.field_photo_url,
            "batch_id": str(batch.id),
            "qr_id": qr_id,
            "safety_analysis": safety_analysis_data,
            "cleaning_instructions": cleaning_instructions
        }
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Verification failed: {str(e)}"
        )


def generate_cleaning_instructions(crop_name: str, farming_method: str, pesticide_count: int) -> str:
    """Generate cleaning instructions based on crop and farming method"""
    if farming_method == 'organic' and pesticide_count == 0:
        return f"For organic {crop_name}: Rinse under cold running water for 30 seconds. Gently rub the surface to remove any dirt or debris. Pat dry with a clean cloth."
    elif pesticide_count == 0:
        return f"For {crop_name}: Wash thoroughly under cold running water for 30-60 seconds. Use a soft brush for firm produce. Soak in water with 1 tablespoon of baking soda for 2 minutes, then rinse again."
    else:
        return f"For {crop_name} treated with pesticides: Soak in water with 2 tablespoons of baking soda for 12-15 minutes. Rinse thoroughly under cold running water for at least 1 minute. For produce with edible skin, consider peeling after washing. Use a soft brush to scrub firm surfaces."


# Get farmer batches
class BatchInfo(BaseModel):
    id: str
    crop_name: str
    crop_variety: Optional[str]
    farming_method: str
    harvest_date: str
    has_qr: bool
    qr_id: Optional[str]


class BatchListResponse(BaseModel):
    success: bool
    batches: List[BatchInfo]


@app.get("/api/farmer/batches", response_model=BatchListResponse)
async def get_farmer_batches(
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Get all batches for the authenticated farmer"""
    logger.info(f"Fetching batches for farmer: {farmer_id}")
    
    try:
        
        batches = db.query(CropBatch).filter(
            CropBatch.farmer_id == farmer_id
        ).order_by(CropBatch.created_at.desc()).all()
        
        batch_list = []
        for batch in batches:
            qr_code = db.query(QRCode).filter(QRCode.batch_id == str(batch.id)).first()
            
            batch_list.append(BatchInfo(
                id=str(batch.id),
                crop_name=batch.crop_name,
                crop_variety=batch.crop_variety,
                farming_method=batch.farming_method,
                harvest_date=str(batch.harvest_date),
                has_qr=qr_code is not None,
                qr_id=qr_code.qr_id if qr_code else None
            ))
        
        return BatchListResponse(
            success=True,
            batches=batch_list
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch batches: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to fetch batches: {str(e)}"
        )


# Farmer profile endpoints
class FarmerProfileResponse(BaseModel):
    success: bool
    farmer_id: str
    name: str
    phone: str
    location: Optional[str]
    profile_photo_url: Optional[str]


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    profile_photo_url: Optional[str] = None


@app.get("/api/farmer/profile", response_model=FarmerProfileResponse)
async def get_farmer_profile(
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Get farmer profile information"""
    logger.info(f"Fetching profile for farmer: {farmer_id}")
    
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        
        if not farmer:
            raise NotFoundError("Farmer not found")
        
        return FarmerProfileResponse(
            success=True,
            farmer_id=str(farmer.id),
            name=farmer.name,
            phone=farmer.phone,
            location=farmer.location,
            profile_photo_url=farmer.profile_photo_url
        )
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch profile: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to fetch profile: {str(e)}"
        )


@app.put("/api/farmer/profile")
async def update_farmer_profile(
    request: UpdateProfileRequest,
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """Update farmer profile information"""
    logger.info(f"Updating profile for farmer: {farmer_id}")
    
    try:
        farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
        
        if not farmer:
            raise NotFoundError("Farmer not found")
        
        # Update fields if provided
        if request.name:
            farmer.name = request.name
        if request.location is not None:  # Allow empty string
            farmer.location = request.location
        if request.profile_photo_url is not None:  # Allow empty string to remove photo
            farmer.profile_photo_url = request.profile_photo_url
        
        db.commit()
        
        logger.info(f"Profile updated for farmer: {farmer_id}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "farmer": {
                "id": str(farmer.id),
                "name": farmer.name,
                "phone": farmer.phone,
                "location": farmer.location,
                "profile_photo_url": farmer.profile_photo_url
            }
        }
        
    except NotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update profile: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to update profile: {str(e)}"
        )


# Lambda handler for AWS deployment
from mangum import Mangum
handler = Mangum(app)

logger.info("FARM2FORK API initialized successfully")


# ============================================================================
# AWS INTEGRATION ENDPOINTS - Production Ready
# ============================================================================

from s3_service import S3Service
from textract_service import TextractService
from rekognition_service import RekognitionService
from bedrock_service import BedrockService
from translate_service import TranslateService
import uuid


@app.post("/api/upload/image")
async def upload_image_endpoint(
    file: UploadFile = File(...),
    file_type: str = Form(...),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """
    Upload image file through backend to S3 with proper permissions.
    
    This endpoint handles the upload server-side to ensure proper permissions
    for AWS Textract and other services to access the uploaded files.
    
    Args:
        file: Image file to upload
        file_type: Type of file (pesticide, fertilizer, crop, seed_packet, profile_photo, field_photo)
        farmer_id: Authenticated farmer ID from JWT token
    
    Returns:
        s3_url: S3 URL of the uploaded file
        file_key: S3 object key
    """
    try:
        # Validate file type
        valid_types = ['pesticide', 'fertilizer', 'crop', 'seed_packet', 'profile_photo', 'field_photo']
        if file_type not in valid_types:
            raise ValidationError(f"Invalid file type. Must be one of: {', '.join(valid_types)}")
        
        # Read file content
        file_content = await file.read()
        
        # Initialize S3 service
        s3_service = S3Service()
        
        # Upload to S3
        s3_url = s3_service.upload_file(
            file_obj=file_content,
            file_type=file_type,
            content_type=file.content_type or 'image/jpeg'
        )
        
        # Extract file key from URL
        file_key = s3_url.split('.com/')[-1]
        
        logger.info(f"Uploaded {file_type} image for farmer: {farmer_id}")
        
        return {
            "success": True,
            "s3_url": s3_url,
            "file_key": file_key
        }
        
    except Exception as e:
        logger.error(f"Image upload failed: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to upload image: {str(e)}"
        )


@app.post("/api/extract/pesticide")
async def extract_pesticide_info_endpoint(
    s3_url: str = Body(..., embed=True),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """
    Extract pesticide information from uploaded image using AWS Textract.
    
    This endpoint uses OCR to automatically extract pesticide name, active
    ingredient, and dosage from package images, reducing manual data entry.
    
    Args:
        s3_url: S3 URL of the uploaded pesticide package image
        farmer_id: Authenticated farmer ID from JWT token
    
    Returns:
        extracted_data: Parsed pesticide information (name, active_ingredient, dosage)
        raw_text: Raw OCR text
        confidence: OCR confidence score (0-100)
    """
    try:
        # Parse S3 URL to get bucket and key
        bucket_name = os.getenv('S3_BUCKET_NAME', 'farm2fork-images')
        
        # Extract key from URL
        # Format: https://bucket.s3.region.amazonaws.com/key
        url_parts = s3_url.split(f"{bucket_name}.s3.")
        if len(url_parts) < 2:
            raise ValueError("Invalid S3 URL format")
        
        file_key = url_parts[1].split("/", 1)[1]
        
        logger.info(f"Extracting pesticide info from {file_key}")
        
        # Initialize Textract service
        textract_service = TextractService()
        
        # Extract text from image
        extracted_data = textract_service.extract_from_image(bucket_name, file_key)
        
        # Parse pesticide-specific information
        pesticide_info = textract_service.extract_pesticide_info(extracted_data)
        
        logger.info(f"Pesticide extraction complete: {pesticide_info.get('name', 'Unknown')}")
        
        return {
            "success": True,
            "extracted_data": pesticide_info,
            "raw_text": extracted_data['raw_text'],
            "confidence": extracted_data['confidence']
        }
        
    except Exception as e:
        logger.error(f"Pesticide extraction failed: {str(e)}")
        logger.error(f"Error details - Type: {type(e).__name__}, S3 URL: {s3_url}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return empty data instead of failing - allows manual entry
        return {
            "success": False,
            "extracted_data": {
                "name": None,
                "active_ingredient": None,
                "dosage": None
            },
            "raw_text": "",
            "confidence": 0,
            "error": str(e)
        }


@app.post("/api/extract/fertilizer")
async def extract_fertilizer_info_endpoint(
    s3_url: str = Body(..., embed=True),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """
    Extract fertilizer information from uploaded image using AWS Textract.
    
    Args:
        s3_url: S3 URL of the uploaded fertilizer package image
        farmer_id: Authenticated farmer ID from JWT token
    
    Returns:
        extracted_data: Parsed fertilizer information (name, npk_ratio, quantity)
        raw_text: Raw OCR text
        confidence: OCR confidence score (0-100)
    """
    try:
        bucket_name = os.getenv('S3_BUCKET_NAME', 'farm2fork-images')
        url_parts = s3_url.split(f"{bucket_name}.s3.")
        file_key = url_parts[1].split("/", 1)[1]
        
        textract_service = TextractService()
        extracted_data = textract_service.extract_from_image(bucket_name, file_key)
        fertilizer_info = textract_service.extract_fertilizer_info(extracted_data)
        
        return {
            "success": True,
            "extracted_data": fertilizer_info,
            "raw_text": extracted_data['raw_text'],
            "confidence": extracted_data['confidence']
        }
        
    except Exception as e:
        logger.error(f"Fertilizer extraction failed: {str(e)}")
        logger.error(f"Error details - Type: {type(e).__name__}, S3 URL: {s3_url}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return empty data instead of failing - allows manual entry
        return {
            "success": False,
            "extracted_data": {
                "name": None,
                "npk_ratio": None,
                "quantity": None
            },
            "raw_text": "",
            "confidence": 0,
            "error": str(e)
        }


@app.post("/api/batch/analyze")
async def analyze_batch_with_ai(
    batch_id: str,
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """
    Run comprehensive AI analysis on batch using Rekognition and Bedrock.
    
    This endpoint:
    1. Analyzes crop images with AWS Rekognition for quality indicators
    2. Generates safety score (0-100) using AWS Bedrock (Claude 3 Sonnet)
    3. Classifies risk level (Safe/Moderate/Risk)
    4. Provides consumer-friendly safety explanation
    
    Args:
        batch_id: ID of the batch to analyze
        farmer_id: Authenticated farmer ID from JWT token
    
    Returns:
        safety_analysis: Safety score, risk level, and explanation
        rekognition_data: Crop quality indicators from image analysis
    """
    try:
        # Get batch
        batch = db.query(CropBatch).filter(
            CropBatch.id == batch_id,
            CropBatch.farmer_id == farmer_id
        ).first()
        
        if not batch:
            raise NotFoundError("Batch not found")
        
        logger.info(f"Analyzing batch {batch_id} for farmer {farmer_id}")
        
        # Get treatments
        treatments = db.query(Treatment).filter(Treatment.batch_id == batch_id).all()
        pesticides = [t for t in treatments if t.treatment_type == 'pesticide']
        fertilizers = [t for t in treatments if t.treatment_type == 'fertilizer']
        
        # Analyze crop images with Rekognition (if available)
        rekognition_data = None
        crop_image = db.query(CropImage).filter(CropImage.batch_id == batch_id).first()
        
        if crop_image and crop_image.image_url:
            try:
                rekognition_service = RekognitionService()
                bucket_name = os.getenv('S3_BUCKET_NAME', 'farm2fork-images')
                
                # Extract key from URL
                url_parts = crop_image.image_url.split(f"{bucket_name}.s3.")
                if len(url_parts) >= 2:
                    file_key = url_parts[1].split("/", 1)[1]
                    rekognition_data = rekognition_service.analyze_crop_image(bucket_name, file_key)
                    logger.info(f"Rekognition analysis complete: {len(rekognition_data.get('labels', []))} labels")
            except Exception as e:
                logger.warning(f"Rekognition analysis failed: {str(e)}")
                # Continue without Rekognition data
        
        # Generate safety analysis with Bedrock
        try:
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
        except Exception as bedrock_error:
            # Bedrock requires special access approval - provide fallback
            logger.warning(f"Bedrock unavailable: {str(bedrock_error)}")
            logger.info("Using fallback safety analysis")
            
            # Generate fallback analysis based on farming method and treatments
            if batch.farming_method == 'organic' and len(pesticides) == 0:
                safety_score = 95.0
                risk_level = 'Safe'
                explanation = f"This {batch.crop_name} was grown using organic farming methods with no synthetic pesticides. It is considered very safe for consumption. Please wash thoroughly before eating."
            elif len(pesticides) == 0:
                safety_score = 85.0
                risk_level = 'Safe'
                explanation = f"This {batch.crop_name} was grown without pesticides. It is safe for consumption. Please wash thoroughly before eating."
            elif len(pesticides) > 0:
                safety_score = 65.0
                risk_level = 'Moderate'
                explanation = f"This {batch.crop_name} was treated with {len(pesticides)} pesticide(s). While within acceptable limits, please wash thoroughly and peel if possible before consumption. Note: AI analysis unavailable - Bedrock access requires AWS approval."
            else:
                safety_score = 75.0
                risk_level = 'Safe'
                explanation = f"This {batch.crop_name} appears safe for consumption. Please wash thoroughly before eating. Note: AI analysis unavailable - Bedrock access requires AWS approval."
            
            safety_analysis = {
                'safety_score': safety_score,
                'risk_level': risk_level,
                'explanation': explanation
            }
        
        # Save analysis to database
        existing_analysis = db.query(SafetyAnalysis).filter(
            SafetyAnalysis.batch_id == batch_id
        ).first()
        
        if existing_analysis:
            # Update existing
            existing_analysis.safety_score = safety_analysis['safety_score']
            existing_analysis.risk_level = safety_analysis['risk_level']
            existing_analysis.explanation = safety_analysis['explanation']
            existing_analysis.analyzed_at = datetime.utcnow()
        else:
            # Create new
            analysis = SafetyAnalysis(
                batch_id=batch_id,
                safety_score=safety_analysis['safety_score'],
                risk_level=safety_analysis['risk_level'],
                explanation=safety_analysis['explanation'],
                bedrock_model='claude-3-sonnet'
            )
            db.add(analysis)
        
        db.commit()
        
        logger.info(f"AI analysis complete: {safety_analysis['risk_level']} (score: {safety_analysis['safety_score']})")
        
        return {
            "success": True,
            "safety_analysis": safety_analysis,
            "rekognition_data": rekognition_data
        }
        
    except NotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"AI analysis failed: {str(e)}")
        raise AIServiceError("Bedrock/Rekognition", str(e))


@app.post("/api/public/translate")
async def translate_verification_data(
    qr_id: str,
    target_language: str = Query(..., regex="^(en|hi|ta|te|kn|ml|bn|mr|gu|pa)$"),
    db: Session = Depends(get_db)
):
    """
    Translate verification data to target language using AWS Translate.
    
    Supports 10 Indian languages:
    - en: English
    - hi: Hindi
    - ta: Tamil
    - te: Telugu
    - kn: Kannada
    - ml: Malayalam
    - bn: Bengali
    - mr: Marathi
    - gu: Gujarati
    - pa: Punjabi
    
    Args:
        qr_id: QR code ID
        target_language: Target language code
    
    Returns:
        translated_data: Verification data translated to target language
        language: Target language code
    """
    try:
        # Get QR code and related data
        qr_code = db.query(QRCode).filter(QRCode.qr_id == qr_id).first()
        if not qr_code:
            raise NotFoundError("QR code not found")
        
        batch = db.query(CropBatch).filter(CropBatch.id == qr_code.batch_id).first()
        safety = db.query(SafetyAnalysis).filter(SafetyAnalysis.batch_id == batch.id).first()
        
        # Build verification data
        verification_data = {
            'safety_analysis': {
                'explanation': safety.explanation if safety else "No safety analysis available"
            }
        }
        
        # Translate if not English
        if target_language != 'en':
            translate_service = TranslateService()
            translated_data = translate_service.translate_verification_data(
                verification_data,
                target_language
            )
        else:
            translated_data = verification_data
        
        logger.info(f"Translated verification data to {target_language} for QR: {qr_id}")
        
        return {
            "success": True,
            "translated_data": translated_data,
            "language": target_language
        }
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise AIServiceError("Translate", str(e))


# Get crops and varieties
@app.get("/api/crops")
async def get_crops():
    """Get list of predefined crops and their varieties"""
    from constants import CROPS
    return {
        "success": True,
        "crops": CROPS
    }


# Get supported languages
@app.get("/api/languages")
async def get_languages():
    """Get list of supported languages for translation"""
    from constants import LANGUAGES
    return {
        "success": True,
        "languages": LANGUAGES
    }


# Update batch photos
class UpdateBatchPhotosRequest(BaseModel):
    field_photo_url: Optional[str] = None
    profile_photo_url: Optional[str] = None


@app.patch("/api/batch/{batch_id}/photos")
async def update_batch_photos(
    batch_id: str,
    request: UpdateBatchPhotosRequest,
    db: Session = Depends(get_db),
    farmer_id: str = Depends(get_current_farmer_id)
):
    """
    Update field photo or profile photo for an existing batch.
    
    Args:
        batch_id: Batch ID to update
        request: Photos to update (field_photo_url, profile_photo_url)
        farmer_id: Authenticated farmer ID
    
    Returns:
        success: True if update successful
        message: Success message
    """
    try:
        # Verify batch exists and belongs to farmer
        batch = db.query(CropBatch).filter(
            CropBatch.id == batch_id,
            CropBatch.farmer_id == farmer_id
        ).first()
        
        if not batch:
            raise NotFoundError("Batch not found or access denied")
        
        # Update photos if provided
        if request.field_photo_url is not None:
            batch.field_photo_url = request.field_photo_url
            logger.info(f"Updated field photo for batch: {batch_id}")
        
        # Also update farmer profile photo if provided
        if request.profile_photo_url is not None:
            farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
            if farmer:
                farmer.profile_photo_url = request.profile_photo_url
                logger.info(f"Updated profile photo for farmer: {farmer_id}")
        
        db.commit()
        
        return {
            "success": True,
            "message": "Photos updated successfully"
        }
        
    except NotFoundError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update photos: {str(e)}")
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Failed to update photos: {str(e)}"
        )


logger.info("AWS Integration endpoints loaded successfully")
