#!/bin/bash

# AWS Elastic Beanstalk Deployment Script for Django LMS
# This script helps deploy the Django LMS to AWS Elastic Beanstalk

echo "🚀 Django LMS - AWS Elastic Beanstalk Deployment"
echo "================================================"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI is configured"

# Variables
APP_NAME="django-lms"
ENV_NAME="django-lms-prod"
REGION="us-east-1"
PLATFORM="64bit Amazon Linux 2 v3.4.24 running Python 3.11"

echo "📦 Preparing deployment package..."

# Create deployment directory
mkdir -p deployment
cd deployment

# Copy project files (excluding unnecessary files)
rsync -av ../ ./ --exclude='.git' --exclude='venv' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='deployment' --exclude='media' --exclude='db.sqlite3' --exclude='django.log'

# Create application version
VERSION=$(date +%Y%m%d-%H%M%S)
ZIP_FILE="${APP_NAME}-${VERSION}.zip"

echo "📁 Creating deployment package: ${ZIP_FILE}"
zip -r ${ZIP_FILE} . -x "*.git*" "venv/*" ".venv/*" "__pycache__/*" "*.pyc" "deployment/*"

echo "☁️ Creating Elastic Beanstalk application..."

# Create application if it doesn't exist
aws elasticbeanstalk describe-applications --application-names ${APP_NAME} --region ${REGION} > /dev/null 2>&1
if [ $? -ne 0 ]; then
    aws elasticbeanstalk create-application \
        --application-name ${APP_NAME} \
        --description "Django Learning Management System" \
        --region ${REGION}
    echo "✅ Created application: ${APP_NAME}"
else
    echo "✅ Application ${APP_NAME} already exists"
fi

# Upload application version to S3
S3_BUCKET="${APP_NAME}-deployments-$(aws sts get-caller-identity --query Account --output text)"
aws s3 mb s3://${S3_BUCKET} --region ${REGION} 2>/dev/null || echo "S3 bucket already exists"
aws s3 cp ${ZIP_FILE} s3://${S3_BUCKET}/${ZIP_FILE} --region ${REGION}

echo "📤 Uploaded ${ZIP_FILE} to S3"

# Create application version
aws elasticbeanstalk create-application-version \
    --application-name ${APP_NAME} \
    --version-label ${VERSION} \
    --source-bundle S3Bucket=${S3_BUCKET},S3Key=${ZIP_FILE} \
    --region ${REGION}

echo "✅ Created application version: ${VERSION}"

# Create environment if it doesn't exist
aws elasticbeanstalk describe-environments --application-name ${APP_NAME} --environment-names ${ENV_NAME} --region ${REGION} > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "🏗️ Creating new environment: ${ENV_NAME}"
    aws elasticbeanstalk create-environment \
        --application-name ${APP_NAME} \
        --environment-name ${ENV_NAME} \
        --solution-stack-name "${PLATFORM}" \
        --version-label ${VERSION} \
        --option-settings file://../eb-options.json \
        --region ${REGION}
    
    echo "⏳ Environment creation started. This may take 10-15 minutes..."
    aws elasticbeanstalk wait environment-ready --application-name ${APP_NAME} --environment-names ${ENV_NAME} --region ${REGION}
    echo "✅ Environment is ready!"
else
    echo "🔄 Updating existing environment: ${ENV_NAME}"
    aws elasticbeanstalk update-environment \
        --application-name ${APP_NAME} \
        --environment-name ${ENV_NAME} \
        --version-label ${VERSION} \
        --region ${REGION}
    
    echo "⏳ Environment update started. This may take 5-10 minutes..."
    aws elasticbeanstalk wait environment-updated --application-name ${APP_NAME} --environment-names ${ENV_NAME} --region ${REGION}
    echo "✅ Environment updated!"
fi

# Get environment URL
ENV_URL=$(aws elasticbeanstalk describe-environments --application-name ${APP_NAME} --environment-names ${ENV_NAME} --region ${REGION} --query 'Environments[0].CNAME' --output text)

echo ""
echo "🎉 Deployment Complete!"
echo "========================"
echo "Application: ${APP_NAME}"
echo "Environment: ${ENV_NAME}"
echo "Version: ${VERSION}"
echo "URL: http://${ENV_URL}"
echo ""
echo "📊 Next Steps:"
echo "1. Configure environment variables in AWS console"
echo "2. Set up RDS database"
echo "3. Configure S3 bucket for media files"
echo "4. Set up custom domain (optional)"
echo ""

cd ..
rm -rf deployment

echo "🏁 Deployment script completed!"
