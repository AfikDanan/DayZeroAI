#!/bin/bash
# Native AWS Deployment Script for Preboarding Service
# Uses AWS CLI and CloudFormation directly (no Serverless Framework)

set -e  # Exit on any error

echo "🚀 Deploying Preboarding Service to AWS (Native)"
echo "================================================"

# Configuration
STAGE=${1:-prod}
REGION=${2:-us-east-1}
STACK_NAME="preboarding-service-$STAGE"

echo "📋 Deployment Configuration:"
echo "   Stage: $STAGE"
echo "   Region: $REGION"
echo "   Stack: $STACK_NAME"
echo ""

# Check prerequisites
echo "🔍 Checking Prerequisites..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install AWS CLI first."
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ Prerequisites check passed"
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

# Package Lambda functions
echo "📦 Packaging Lambda Functions..."

# Create deployment package
PACKAGE_DIR="lambda-package"
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

# Copy application code
cp -r ../../app $PACKAGE_DIR/
cp -r ../*.py $PACKAGE_DIR/
cp google_credencial.json $PACKAGE_DIR/ 2>/dev/null || echo "⚠️ Google credentials file not found"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-aws.txt -t $PACKAGE_DIR/

# Create ZIP package
cd $PACKAGE_DIR
zip -r ../lambda-deployment.zip . -x "*.pyc" "*/__pycache__/*"
cd ..

echo "✅ Lambda package created: lambda-deployment.zip"
echo ""

# Deploy using AWS CLI and CloudFormation
echo "🚀 Deploying to AWS..."

# Create CloudFormation template
cat > cloudformation-template.yaml << EOF
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Preboarding Service - Native AWS Deployment'

Parameters:
  Stage:
    Type: String
    Default: $STAGE
  
  OpenAIApiKey:
    Type: String
    NoEcho: true
    Default: $OPENAI_API_KEY
  
  SendGridApiKey:
    Type: String
    NoEcho: true
    Default: $SENDGRID_API_KEY
  
  FromEmail:
    Type: String
    Default: $FROM_EMAIL

Resources:
  # Lambda Execution Role
  LambdaExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: S3Access
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                  - s3:ListBucket
                Resource:
                  - !Sub "arn:aws:s3:::preboarding-videos-\${Stage}"
                  - !Sub "arn:aws:s3:::preboarding-videos-\${Stage}/*"

  # API Lambda Function
  ApiLambdaFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: !Sub "preboarding-api-\${Stage}"
      Runtime: python3.10
      Handler: lambda_handler.api_handler
      Code:
        ZipFile: |
          def api_handler(event, context):
              return {"statusCode": 200, "body": "Placeholder"}
      Role: !GetAtt LambdaExecutionRole.Arn
      Timeout: 30
      MemorySize: 512
      Environment:
        Variables:
          ENVIRONMENT: !Ref Stage
          S3_BUCKET_NAME: !Sub "preboarding-videos-\${Stage}"
          OPENAI_API_KEY: !Ref OpenAIApiKey
          SENDGRID_API_KEY: !Ref SendGridApiKey
          FROM_EMAIL: !Ref FromEmail

  # API Gateway
  ApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "preboarding-api-\${Stage}"
      Description: "Preboarding Service API"

  # API Gateway Deployment
  ApiGatewayDeployment:
    Type: AWS::ApiGateway::Deployment
    DependsOn: ApiGatewayMethod
    Properties:
      RestApiId: !Ref ApiGateway
      StageName: !Ref Stage

  # API Gateway Resource
  ApiGatewayResource:
    Type: AWS::ApiGateway::Resource
    Properties:
      RestApiId: !Ref ApiGateway
      ParentId: !GetAtt ApiGateway.RootResourceId
      PathPart: "{proxy+}"

  # API Gateway Method
  ApiGatewayMethod:
    Type: AWS::ApiGateway::Method
    Properties:
      RestApiId: !Ref ApiGateway
      ResourceId: !Ref ApiGatewayResource
      HttpMethod: ANY
      AuthorizationType: NONE
      Integration:
        Type: AWS_PROXY
        IntegrationHttpMethod: POST
        Uri: !Sub "arn:aws:apigateway:\${AWS::Region}:lambda:path/2015-03-31/functions/\${ApiLambdaFunction.Arn}/invocations"

  # Lambda Permission for API Gateway
  ApiGatewayLambdaPermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ApiLambdaFunction
      Action: lambda:InvokeFunction
      Principal: apigateway.amazonaws.com
      SourceArn: !Sub "arn:aws:execute-api:\${AWS::Region}:\${AWS::AccountId}:\${ApiGateway}/*/*"

Outputs:
  ApiGatewayUrl:
    Description: "API Gateway URL"
    Value: !Sub "https://\${ApiGateway}.execute-api.\${AWS::Region}.amazonaws.com/\${Stage}"
  
  S3BucketName:
    Description: "S3 bucket for video storage"
    Value: !Sub "preboarding-videos-\${Stage}"
EOF

# Deploy CloudFormation stack
echo "🚀 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Stage=$STAGE \
        OpenAIApiKey="$OPENAI_API_KEY" \
        SendGridApiKey="$SENDGRID_API_KEY" \
        FromEmail="$FROM_EMAIL" \
    --capabilities CAPABILITY_IAM \
    --region $REGION

echo "✅ CloudFormation stack deployed successfully!"
echo ""

# Update Lambda function code
echo "📦 Updating Lambda function code..."
aws lambda update-function-code \
    --function-name "preboarding-api-$STAGE" \
    --zip-file fileb://lambda-deployment.zip \
    --region $REGION

echo "✅ Lambda function code updated!"
echo ""

# Get deployment information
echo "📊 Deployment Information:"
echo "========================="

# Get API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
    --output text)

echo "🌐 API Gateway URL: $API_URL"
echo "🪣 S3 Bucket: preboarding-videos-$STAGE"
echo "⚡ Lambda Function: preboarding-api-$STAGE"

echo ""
echo "🧪 Testing Deployment:"
echo "====================="

# Test health endpoint
echo "🔍 Testing health endpoint..."
HEALTH_URL="$API_URL/health"

sleep 5  # Wait for deployment to propagate

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
echo "        -d @../../data/mock_data.json"
echo ""
echo "2. Monitor CloudWatch logs:"
echo "   aws logs tail /aws/lambda/preboarding-api-$STAGE --follow"
echo ""
echo "3. Check S3 bucket for generated videos:"
echo "   aws s3 ls s3://preboarding-videos-$STAGE/videos/"
echo ""
echo "🎉 Native AWS Deployment Complete!"