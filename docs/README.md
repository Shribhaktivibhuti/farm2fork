# FARM2FORK Documentation

This directory contains comprehensive documentation for the FARM2FORK AI-Powered Traceability Platform.

## Documentation Structure

- `architecture.md` - System architecture and design decisions
- `api-reference.md` - Complete API endpoint documentation
- `user-guide.md` - User guide for farmers and consumers
- `deployment-guide.md` - Deployment and infrastructure setup
- `development-guide.md` - Local development setup and guidelines
- `testing-guide.md` - Testing strategy and guidelines

## Quick Links

- [Requirements](.kiro/specs/farm2fork-traceability/requirements.md)
- [Design Document](.kiro/specs/farm2fork-traceability/design.md)
- [Implementation Tasks](.kiro/specs/farm2fork-traceability/tasks.md)

## Project Overview

FARM2FORK is an AWS-native platform that bridges the trust gap between farmers and consumers through AI-powered food traceability. The system uses QR codes as the linking mechanism, with two distinct user experiences:

- **Farmer Mode** (Green Theme): For farmers to create and manage crop batches
- **Consumer Mode** (Blue Theme): For consumers to scan and verify food safety

### Key Features

1. **QR Code Traceability**: Link physical produce to digital records
2. **AI Safety Analysis**: AWS Bedrock generates safety scores (0-100)
3. **OCR Extraction**: Amazon Textract extracts data from package images
4. **Image Analysis**: Amazon Rekognition analyzes crop quality
5. **Multi-Language Support**: 10 Indian languages via Amazon Translate
6. **Progressive Web App**: Mobile-first, offline-capable interface
7. **Serverless Architecture**: AWS Lambda + API Gateway + S3 + RDS

### Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (routing)
- PWA capabilities

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (database)
- Boto3 (AWS SDK)
- Mangum (Lambda adapter)

**AWS Services:**
- Lambda, API Gateway, S3, RDS, CloudFront
- Bedrock, Textract, Rekognition, Translate

## Getting Started

See the [Development Guide](development-guide.md) for local setup instructions.

## Contributing

This is a production-ready platform. All changes should follow the implementation plan in the tasks document.
