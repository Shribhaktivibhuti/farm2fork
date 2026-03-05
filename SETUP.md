# FARM2FORK Setup Instructions

## ✅ Project Structure Created

The following directory structure has been successfully created:

```
farm2fork-traceability/
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   ├── pytest.ini          # Pytest configuration
│   └── __init__.py         # Package initialization
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── main.tsx       # React entry point
│   │   ├── App.tsx        # Main App component
│   │   ├── index.css      # Global styles with Tailwind
│   │   ├── vite-env.d.ts  # TypeScript environment definitions
│   │   └── test/
│   │       └── setup.ts   # Test configuration
│   ├── package.json       # Node dependencies
│   ├── vite.config.ts     # Vite configuration with PWA
│   ├── tsconfig.json      # TypeScript configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── postcss.config.js  # PostCSS configuration
│   ├── .eslintrc.cjs      # ESLint configuration
│   ├── index.html         # HTML entry point
│   └── .env.example       # Environment variables template
├── infrastructure/         # AWS infrastructure scripts
│   └── README.md
├── deployment/            # Deployment scripts
│   └── README.md
├── docs/                  # Documentation
│   ├── README.md
│   └── development-guide.md
├── .gitignore            # Git ignore rules
├── README.md             # Project README
├── LICENSE               # MIT License
└── SETUP.md              # This file
```

## 🚀 Next Steps

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Test the backend
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000` to see the health check endpoint.
Visit `http://localhost:8000/docs` for interactive API documentation.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API URL

# Start development server
npm run dev
```

Visit `http://localhost:5173` to see the frontend.

## 📋 Configuration Checklist

### Backend Configuration (backend/.env)

- [ ] Set `DATABASE_URL` with PostgreSQL connection string
- [ ] Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- [ ] Set `AWS_REGION` (default: us-east-1)
- [ ] Set `S3_BUCKET_NAME` for image storage
- [ ] Set `JWT_SECRET_KEY` (generate a secure random string)
- [ ] Set `CORS_ORIGINS` to include your frontend URL

### Frontend Configuration (frontend/.env)

- [ ] Set `VITE_API_BASE_URL` to your backend URL (default: http://localhost:8000/api)
- [ ] Verify other settings match your requirements

## 🧪 Verify Installation

### Backend Verification

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
python -c "import boto3; print('Boto3:', boto3.__version__)"
```

### Frontend Verification

```bash
cd frontend
npm run lint
npm run build
```

## 📚 Key Features Configured

### Backend
- ✅ FastAPI with CORS middleware
- ✅ Mangum adapter for AWS Lambda deployment
- ✅ Environment variable management with python-dotenv
- ✅ Testing setup with pytest and hypothesis
- ✅ AWS SDK (boto3) for AI services integration

### Frontend
- ✅ React 18 with TypeScript
- ✅ Vite for fast development and building
- ✅ Tailwind CSS with custom farmer/consumer themes
- ✅ PWA configuration with service workers
- ✅ React Router for navigation
- ✅ Testing setup with Vitest and React Testing Library
- ✅ ESLint for code quality

## 🎨 Theme Configuration

The project includes pre-configured themes:

- **Farmer Mode**: Green color palette (`farmer-*` classes)
- **Consumer Mode**: Blue color palette (`consumer-*` classes)

Both themes are defined in `frontend/tailwind.config.js`.

## 📖 Documentation

- [Development Guide](docs/development-guide.md) - Detailed setup and development instructions
- [Requirements](.kiro/specs/farm2fork-traceability/requirements.md) - Complete requirements
- [Design Document](.kiro/specs/farm2fork-traceability/design.md) - System design and architecture
- [Tasks](.kiro/specs/farm2fork-traceability/tasks.md) - Implementation plan

## 🔧 System Requirements

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- AWS Account (for production deployment)

## ⚠️ Important Notes

1. **Environment Files**: Never commit `.env` files to version control
2. **AWS Credentials**: Keep AWS credentials secure and never expose them
3. **Database**: Create a PostgreSQL database before running the backend
4. **Dependencies**: Install all dependencies before running the application

## 🎯 Current Status

✅ **Task 1 Complete**: Project structure and infrastructure foundation set up

**Next Task**: Task 2 - Implement database models and migrations

## 💡 Tips

- Use the development guide for detailed instructions
- Check the requirements and design documents before implementing features
- Follow the task list in sequential order
- Run tests frequently during development
- Use the demo OTP "0000" for farmer authentication during development

## 🆘 Need Help?

Refer to:
- [Development Guide](docs/development-guide.md) for common issues
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

---

**Ready to start development!** 🚀

Follow the implementation tasks in `.kiro/specs/farm2fork-traceability/tasks.md`
