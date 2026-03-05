# Infrastructure

This directory contains AWS infrastructure configuration and setup scripts for the FARM2FORK platform.

## AWS Services Used

- **AWS Lambda**: Serverless backend API hosting
- **API Gateway**: REST API endpoint management
- **RDS PostgreSQL**: Relational database for crop batch data
- **S3**: Object storage for images and QR codes
- **CloudFront**: CDN for frontend static files
- **Amazon Bedrock**: AI safety analysis and consumption advice
- **Amazon Textract**: OCR for package text extraction
- **Amazon Rekognition**: Image analysis for crop quality
- **Amazon Translate**: Multi-language support

## Setup Scripts

Infrastructure setup scripts will be added in later tasks:
- `setup-s3.sh` - Create and configure S3 buckets
- `setup-rds.sh` - Create RDS PostgreSQL instance
- `setup-lambda.sh` - Deploy Lambda function
- `setup-api-gateway.sh` - Configure API Gateway
- `setup-cloudfront.sh` - Configure CloudFront distribution

## Environment Variables

All AWS credentials and configuration should be set in the backend `.env` file.
See `backend/.env.example` for required variables.
