#!/bin/bash
# AWS Deployment Script for Preboarding Service

set -e  # Exit on any error

echo "🚀 Deploying Preboarding Service to AWS"
echo "========================================"

# Configuration
STAGE=${1:-prod}
REGION=${2:-us-east-1}

echo "📋 Deployment Configuration:"
echo "   Stage: $STAGE"
echo "   Region: $REGION"
echo ""

# Check prerequisites
echo "🔍 Checking Prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check if Serverless Framework is installed
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework not found. Installing..."
    npm install -g serverless
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Install Serverless plugins
echo "📦 Installing Serverless Plugins..."
npm install serverless-python-requirements serverless-iam-roles-per-function
echo ""

# Create S3 bucket if it doesn't exist
BUCKET_NAME="preboarding-videos-$STAGE"
echo "🪣 Creating S3 Bucket: $BUCKET_NAME"

if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://$BUCKET_NAME" --region $REGION
    echo "✅ S3 bucket created: $BUCKET_NAME"
else
    echo "✅ S3 bucket already exists: $BUCKET_NAME"
fi

# Set up environment variables
echo "🔧 Setting up Environment Variables..."

# Check if .env.aws exists
if [ ! -f ".env.aws" ]; then
    echo "⚠️  .env.aws file not found. Creating template..."
    cat > .env.aws << EOF
# AWS Production Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=your_verified_email@domain.com
REDIS_CLUSTER_ENDPOINT=your_redis_cluster_endpoint
EOF
    echo "📝 Please update .env.aws with your actual values"
    echo "❌ Deployment stopped. Update .env.aws and run again."
    exit 1
fi

# Source environment variables
source .env.aws
echo "✅ Environment variables loaded"
echo ""

# Validate required environment variables
echo "🔍 Validating Environment Variables..."
REQUIRED_VARS=("OPENAI_API_KEY" "SENDGRID_API_KEY" "FROM_EMAIL")

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ All required environment variables are set"
echo ""

# Deploy with Serverless Framework
echo "🚀 Deploying to AWS Lambda..."
echo "   This may take several minutes..."
echo ""

serverless deploy \
    --stage $STAGE \
    --region $REGION \
    --verbose

echo ""
echo "✅ Deployment completed successfully!"
echo ""

# Get deployment information
echo "📊 Deployment Information:"
echo "========================="

# Get API Gateway URL
API_URL=$(serverless info --stage $STAGE --region $REGION | grep "endpoint:" | awk '{print $2}')
echo "🌐 API Gateway URL: $API_URL"

# Get S3 bucket info
echo "🪣 S3 Bucket: $BUCKET_NAME"
echo "   Region: $REGION"

# Get function names
echo "⚡ Lambda Functions:"
echo "   API Handler: preboarding-service-$STAGE-api"
echo "   Video Worker: preboarding-service-$STAGE-videoWorker"

echo ""
echo "🧪 Testing Deployment:"
echo "====================="

# Test health endpoint
echo "🔍 Testing health endpoint..."
HEALTH_URL="$API_URL/health"

if curl -s "$HEALTH_URL" | grep -q "healthy"; then
    echo "✅ Health check passed: $HEALTH_URL"
else
    echo "⚠️  Health check failed. Check CloudWatch logs."
fi

echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Test the webhook endpoint:"
echo "   curl -X POST $API_URL/webhooks/user-onboarding \\"
echo "        -H 'Content-Type: application/json' \\"
echo "        -d @data/mock_data.json"
echo ""
echo "2. Monitor CloudWatch logs:"
echo "   aws logs tail /aws/lambda/preboarding-service-$STAGE-api --follow"
echo ""
echo "3. Check S3 bucket for generated videos:"
echo "   aws s3 ls s3://$BUCKET_NAME/videos/"
echo ""
echo "🎉 Deployment Complete!"