# 🚀 AWS Production Deployment Guide
# This file has been moved to aws/deployment/README.md

**⚠️ This file has been moved to `aws/deployment/README.md`**

Please refer to the new location for the complete AWS deployment guide.

## 📋 Prerequisites

### 1. AWS Account Setup
- ✅ AWS Account with appropriate permissions
- ✅ AWS CLI installed and configured
- ✅ IAM user with Lambda, S3, SQS, and ElastiCache permissions

### 2. Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# For Windows, download from: https://aws.amazon.com/cli/
```

### 3. API Keys Required
- 🔑 **OpenAI API Key** (for script generation)
- 📧 **SendGrid API Key** (for email notifications)
- ☁️ **Google Cloud Service Account** (for text-to-speech)

## 🔧 Configuration

### 1. Environment Variables
```bash
# Copy template and fill in your values
cp aws/deployment/.env.aws.template .env.aws

# Edit with your actual API keys
nano .env.aws
```

### 2. AWS Credentials
```bash
# Configure AWS CLI
aws configure

# Test connection
aws sts get-caller-identity
```

## 🚀 Deployment Steps

### 1. Quick Deployment
```bash
# Make deployment script executable
chmod +x aws/deployment/deploy.sh

# Deploy to production
./aws/deployment/deploy.sh prod us-east-1

# Deploy to development
./aws/deployment/deploy.sh dev us-east-1
```

### 2. Manual Deployment
```bash
# Navigate to deployment directory
cd aws/deployment

# Deploy with Serverless
serverless deploy --stage prod --region us-east-1
```

## 🏗️ AWS Architecture

### Lambda Functions
- **API Handler** (`preboarding-service-prod-api`)
  - Handles webhook endpoints
  - Memory: 512 MB
  - Timeout: 30 seconds
  
- **Video Worker** (`preboarding-service-prod-videoWorker`)
  - Processes video generation
  - Memory: 3008 MB (maximum)
  - Timeout: 15 minutes

### Storage & Queuing
- **S3 Bucket** (`preboarding-videos-prod`)
  - Stores generated videos
  - Public read access for video URLs
  
- **SQS Queue** (`preboarding-jobs-prod`)
  - Queues video generation jobs
  - Dead letter queue for failed jobs
  
- **ElastiCache Redis** (optional)
  - Job status tracking
  - Can use external Redis service

### Networking
- **API Gateway** - REST API endpoints
- **CloudWatch** - Logging and monitoring
- **IAM Roles** - Secure service permissions

## 🧪 Testing Deployment

### 1. Health Check
```bash
# Test API health
curl https://your-api-gateway-url/health

# Expected response:
{
  "status": "healthy",
  "service": "preboarding-service",
  "environment": "production"
}
```

### 2. Webhook Test
```bash
# Send test webhook
curl -X POST https://your-api-gateway-url/webhooks/user-onboarding \
     -H "Content-Type: application/json" \
     -d @data/mock_data.json

# Expected response:
{
  "success": true,
  "job_id": "uuid-here",
  "message": "User onboarding webhook processed"
}
```

### 3. Monitor Processing
```bash
# Watch Lambda logs
aws logs tail /aws/lambda/preboarding-service-prod-api --follow
aws logs tail /aws/lambda/preboarding-service-prod-videoWorker --follow

# Check S3 for generated videos
aws s3 ls s3://preboarding-videos-prod/videos/

# Monitor SQS queue
aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/ACCOUNT/preboarding-jobs-prod \
    --attribute-names All
```

## 📊 Monitoring & Debugging

### CloudWatch Dashboards
- Lambda function metrics
- S3 storage usage
- SQS queue depth
- Error rates and latency

### Common Issues & Solutions

#### 1. Lambda Timeout
```yaml
# Increase timeout in serverless.yml
functions:
  videoWorker:
    timeout: 900  # 15 minutes max
```

#### 2. Memory Issues
```yaml
# Increase memory for video processing
functions:
  videoWorker:
    memorySize: 3008  # Maximum available
```

#### 3. S3 Permissions
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket preboarding-videos-prod

# Fix permissions if needed
aws s3api put-bucket-policy --bucket preboarding-videos-prod --policy file://bucket-policy.json
```

## 🔒 Security Best Practices

### 1. IAM Roles
- ✅ Least privilege principle
- ✅ Separate roles for API and Worker
- ✅ No hardcoded credentials

### 2. Environment Variables
- ✅ Store sensitive data in AWS Systems Manager
- ✅ Use KMS encryption for secrets
- ✅ Rotate API keys regularly

### 3. Network Security
- ✅ VPC configuration for Redis
- ✅ Security groups with minimal access
- ✅ HTTPS only for API endpoints

## 💰 Cost Optimization

### Lambda Pricing
- **API Handler**: ~$0.20 per 1M requests
- **Video Worker**: ~$0.0000166667 per GB-second
- **Typical video generation**: ~$0.05 per video

### S3 Storage
- **Standard storage**: ~$0.023 per GB/month
- **Data transfer**: First 1 GB free per month

### Optimization Tips
- ✅ Use S3 lifecycle policies for old videos
- ✅ Monitor CloudWatch for unused resources
- ✅ Set up billing alerts

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - name: Deploy to AWS
        run: |
          npm install -g serverless
          serverless deploy --stage prod
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 📞 Support & Troubleshooting

### Useful Commands
```bash
# View function logs
serverless logs -f api --stage prod --tail

# Invoke function directly
serverless invoke -f videoWorker --stage prod --data '{"test": true}'

# Remove deployment
serverless remove --stage prod
```

### Getting Help
- 📖 [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- 📖 [Serverless Framework Docs](https://www.serverless.com/framework/docs/)
- 🐛 Check CloudWatch logs for detailed error messages
- 💬 AWS Support for infrastructure issues

## 🎯 Production Checklist

Before going live:

- [ ] ✅ All API keys configured and tested
- [ ] ✅ SendGrid sender verification completed
- [ ] ✅ S3 bucket permissions configured
- [ ] ✅ CloudWatch monitoring set up
- [ ] ✅ Error handling and notifications working
- [ ] ✅ Load testing completed
- [ ] ✅ Backup and disaster recovery plan
- [ ] ✅ Security review completed
- [ ] ✅ Cost monitoring alerts configured

## 🚀 Go Live!

Your preboarding service is now ready for production use on AWS! 🎉