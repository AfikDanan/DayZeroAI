# 🚀 Render.com Deployment Guide

This guide will help you deploy the Preboarding Service to Render.com, which provides a simple and cost-effective hosting solution.

## 📋 Prerequisites

### 1. Render.com Account
- Create a free account at [render.com](https://render.com)
- Connect your GitHub account

### 2. Required API Keys
- 🔑 **OpenAI API Key** (for script generation)
- 📧 **SendGrid API Key** (for email notifications)  
- ☁️ **Google Cloud Service Account JSON** (for text-to-speech)

## 🔧 Deployment Steps

### Step 1: Push Code to GitHub

Make sure your code is pushed to a GitHub repository that Render can access.

```bash
git add .
git commit -m "feat: add Render.com deployment configuration"
git push origin main
```

### Step 2: Create Services on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** and select **"Blueprint"**
3. **Connect your GitHub repository**
4. **Select the repository** containing your preboarding service
5. **Render will automatically detect** the `render.yaml` file

### Step 3: Configure Environment Variables

After the services are created, you need to set the sensitive environment variables:

#### For the Web Service (preboarding-api):
1. Go to the **preboarding-api** service
2. Click **"Environment"** tab
3. Add these variables:

```
OPENAI_API_KEY=sk-your-openai-api-key-here
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
FROM_EMAIL=your-verified-email@domain.com
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
```

#### For the Worker Service (preboarding-worker):
1. Go to the **preboarding-worker** service  
2. Click **"Environment"** tab
3. Add the same variables as above

### Step 4: Deploy

1. **Click "Deploy"** on each service
2. **Monitor the build logs** to ensure successful deployment
3. **Test the API** once deployment is complete

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl https://your-app-name.onrender.com/health
```

### 2. Test Webhook
```bash
curl -X POST https://your-app-name.onrender.com/webhooks/user-onboarding \
  -H "Content-Type: application/json" \
  -d @data/mock_data.json
```

## 📊 Service Configuration

### Web Service (API)
- **Type**: Web Service
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/health`
- **Plan**: Starter (free tier available)

### Worker Service
- **Type**: Background Worker
- **Environment**: Python  
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m rq worker video_generation --url redis://$REDIS_HOST:$REDIS_PORT`
- **Plan**: Starter

### Redis Service
- **Type**: Redis
- **Plan**: Starter (25MB free)
- **Memory Policy**: allkeys-lru
- **IP Allow List**: Configured with private network ranges for internal access

## 💰 Pricing

### Free Tier Limits:
- **Web Service**: 750 hours/month (always-on with paid plan)
- **Background Worker**: 750 hours/month
- **Redis**: 25MB storage
- **Bandwidth**: 100GB/month

### Paid Plans:
- **Starter**: $7/month per service
- **Standard**: $25/month per service  
- **Pro**: $85/month per service

## 🔧 Configuration Details

### Environment Variables Set Automatically:
- `PORT` - Render sets this automatically
- `REDIS_HOST` - Connected from Redis service
- `REDIS_PORT` - Connected from Redis service
- `BASE_URL` - Your app's URL

### Environment Variables You Must Set:
- `OPENAI_API_KEY` - Your OpenAI API key
- `SENDGRID_API_KEY` - Your SendGrid API key
- `FROM_EMAIL` - Verified sender email
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` - Google Cloud service account JSON (as string)

## 🚀 Going Live

### 1. Custom Domain (Optional)
1. Go to **Settings** → **Custom Domains**
2. Add your domain (e.g., `api.yourcompany.com`)
3. Configure DNS records as instructed

### 2. Scaling
- **Horizontal Scaling**: Add more instances in service settings
- **Vertical Scaling**: Upgrade to higher-tier plans
- **Auto-scaling**: Available on Standard+ plans

### 3. Monitoring
- **Logs**: Available in Render dashboard
- **Metrics**: CPU, memory, and request metrics
- **Alerts**: Set up notifications for service issues

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check `requirements.txt` for correct package versions
   - Ensure Python version compatibility

2. **Worker Not Processing Jobs**
   - Verify Redis connection
   - Check worker logs for errors
   - Ensure environment variables are set

3. **Google Cloud TTS Errors**
   - Verify `GOOGLE_APPLICATION_CREDENTIALS_JSON` is valid JSON
   - Check Google Cloud project billing is enabled
   - Ensure Text-to-Speech API is enabled

4. **Memory Issues**
   - Upgrade to higher-tier plan
   - Optimize video processing settings
   - Implement file cleanup

### Getting Help:
- **Render Docs**: https://render.com/docs
- **Support**: Available through Render dashboard
- **Community**: Render community forum

## 🎉 Success!

Once deployed, your preboarding service will be available at:
- **API**: `https://your-app-name.onrender.com`
- **Health Check**: `https://your-app-name.onrender.com/health`
- **Webhook**: `https://your-app-name.onrender.com/webhooks/user-onboarding`

The service will automatically:
- ✅ Scale based on demand
- ✅ Handle HTTPS certificates
- ✅ Provide monitoring and logs
- ✅ Process background video generation jobs
- ✅ Send email notifications to new hires