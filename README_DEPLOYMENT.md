# AI Visual Insight Pro - Deployment Guide

## 🚀 Deployment Options

### Option 1: Streamlit Community Cloud (Recommended - FREE)

**Pros:**
- Free hosting
- Easy deployment
- Automatic updates from Git
- SSL certificate included
- Custom subdomain

**Steps:**

1. **Prepare GitHub Repository**
   ```powershell
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `app_pro.py`
   - Click "Deploy"

**Note:** Some AI models may exceed free tier limits. Consider using smaller models or deploying locally.

---

### Option 2: Local Network Deployment

**For accessing within your network (college/home):**

```powershell
# Run on specific port
.\run_project.ps1

# Access from other devices on same network
# http://YOUR_LOCAL_IP:8501
```

**Find your IP:**
```powershell
ipconfig | findstr IPv4
```

---

### Option 3: Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app_pro.py", "--server.port=8501"]
```

**Deploy:**
```powershell
docker build -t ai-visual-insight .
docker run -p 8501:8501 ai-visual-insight
```

---

### Option 4: Cloud Platform Deployment

#### **AWS EC2 / Azure VM / Google Cloud VM**

1. Create VM instance (Ubuntu 20.04+)
2. Install Python 3.10+
3. Clone repository
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run with nohup:
   ```bash
   nohup streamlit run app_pro.py --server.port 8501 &
   ```
6. Configure firewall to allow port 8501

---

## ⚠️ Important Notes

### For Production Deployment:

1. **Security:**
   - Change default ports
   - Enable authentication
   - Use HTTPS/SSL
   - Set up firewall rules

2. **Performance:**
   - Use GPU instances for AI models
   - Increase RAM (8GB+ recommended)
   - Enable caching
   - Optimize model loading

3. **Configuration:**
   - Update `.streamlit/config.toml` for production
   - Set proper CORS settings
   - Configure max upload size

### Model Requirements:

This app uses heavy AI models:
- **YOLO**: Object detection
- **BLIP**: Image captioning
- **Whisper**: Speech transcription
- **BART**: Text summarization

**Recommended Resources:**
- RAM: 8GB minimum (16GB recommended)
- Storage: 10GB+ for models
- GPU: Optional but improves performance 10x

---

## 📝 Pre-Deployment Checklist

- [ ] Test all features locally
- [ ] Remove sensitive data
- [ ] Update requirements.txt
- [ ] Configure .gitignore
- [ ] Set appropriate file size limits
- [ ] Test on target platform
- [ ] Document API keys (if any)
- [ ] Set up monitoring/logging

---

## 🔧 Troubleshooting

**Port already in use:**
```powershell
# Kill process on port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**Memory issues:**
- Use smaller models
- Reduce batch sizes
- Enable model caching
- Process videos in chunks

**Slow performance:**
- Enable GPU support
- Use multiprocessing
- Optimize video resolution
- Cache model predictions

---

## 📞 Support

For deployment issues:
1. Check Streamlit docs: https://docs.streamlit.io/deploy
2. Review error logs
3. Test dependencies individually
4. Verify system requirements

---

**Deployment Status:**
- ✅ Code optimized
- ✅ Dependencies listed
- ✅ Config files ready
- ✅ Git repository initialized
- ⏳ Choose deployment platform
