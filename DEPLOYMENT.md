# 🚀 Streamlit Cloud Deployment Guide

## 📋 Deployment Settings for Streamlit Cloud

When deploying to Streamlit Cloud, use these settings:

### **Repository:**
```
DHARSHAN0401/AI-Powered-Visual-Insight-System-for-Automated-Video-Summarization-and-Content-Moderation
```

### **Branch:**
```
main
```

### **Main file path:**
```
project/streamlit_app.py
```

---

## 📁 Required Files (Already Created)

✅ All necessary files have been created in your repository:

1. **`requirements.txt`** (root directory)
   - Contains Python dependencies
   - Located at: `/requirements.txt`

2. **`packages.txt`** (root directory)
   - Contains system dependencies (ffmpeg, etc.)
   - Located at: `/packages.txt`

3. **`.streamlit/config.toml`**
   - Streamlit configuration
   - Located at: `/.streamlit/config.toml`

4. **`project/streamlit_app.py`**
   - Main application file
   - Located at: `/project/streamlit_app.py`

---

## 🔧 Deployment Steps

### Step 1: Commit and Push Your Code

```bash
# Navigate to your project
cd "D:\Major Final Year Project"

# Add all files
git add .

# Commit changes
git commit -m "Add Streamlit Cloud deployment files"

# Push to GitHub
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in the deployment form:
   - **Repository**: Select your repository
   - **Branch**: `main`
   - **Main file path**: `project/streamlit_app.py`
5. Click **"Deploy!"**

### Step 3: Wait for Deployment

- Streamlit Cloud will:
  - Install system packages from `packages.txt`
  - Install Python packages from `requirements.txt`
  - Start your app at `project/streamlit_app.py`
  
- Deployment typically takes 2-5 minutes

---

## 🎯 Features Available in Deployed App

### ✅ Basic Features (Working Now):
- 🎥 Video upload (MP4, AVI, MOV, MKV)
- 🔍 Automatic scene detection
- 🖼️ Keyframe extraction
- 📝 Summary generation
- 📊 Metadata export
- 💾 Download results (TXT, JSON)

### 🚀 Advanced Features (Optional):
To enable AI models, add these to `requirements.txt`:
```
torch>=2.0.0
torchvision>=0.15.0
transformers>=4.30.0
openai-whisper>=20230314
ultralytics>=8.0.0
```

**Note**: Advanced features require more memory and may exceed Streamlit Cloud's free tier limits.

---

## 📊 Expected Resource Usage

### Free Tier (1 GB RAM):
- ✅ Basic video processing
- ✅ Scene detection
- ✅ Keyframe extraction
- ✅ Videos up to ~100 MB

### Community Tier (Recommended):
- ✅ All basic features
- ✅ Larger videos (up to 200 MB)
- ⚠️ AI models may still be limited

### For Full AI Features:
- Requires: 4+ GB RAM
- Consider: Private deployment or cloud compute

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Ensure all dependencies are in `requirements.txt`

### Issue: "Out of Memory"
**Solution**: 
1. Reduce video size
2. Lower max scenes setting
3. Remove advanced AI models

### Issue: "Build Failed"
**Solution**: Check that:
- `packages.txt` is in root directory
- `requirements.txt` is in root directory
- File paths are correct

### Issue: "App is slow"
**Solution**:
1. Use smaller videos for testing
2. Enable caching (`@st.cache_data`)
3. Optimize scene detection threshold

---

## 🔗 Your App URL

After deployment, your app will be available at:
```
https://[your-app-name].streamlit.app
```

Example:
```
https://ai-video-summarization.streamlit.app
```

You can customize the subdomain in Streamlit Cloud settings.

---

## 📝 Post-Deployment Checklist

- [ ] Commit all files to GitHub
- [ ] Push to main branch
- [ ] Deploy on Streamlit Cloud
- [ ] Test with sample video
- [ ] Share app URL
- [ ] Monitor resource usage
- [ ] Update README with app link

---

## 🎉 Success!

Once deployed, users can:
1. Visit your app URL
2. Upload videos
3. Process and analyze
4. View results
5. Download summaries

No installation required! 🚀

---

## 📧 Support

For issues, check:
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Forum](https://discuss.streamlit.io)
- Your GitHub repository issues
