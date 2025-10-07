# 🚀 Deploy DataWise AI to Streamlit Cloud

Complete guide to deploying your DataWise AI application to Streamlit Cloud for free!

---

## 📋 Prerequisites

Before deploying, make sure you have:

- ✅ GitHub account
- ✅ Your code pushed to GitHub repository
- ✅ Google Gemini API key
- ✅ PostgreSQL database (see options below)

---

## 🗄️ Database Options for Deployment

### Option 1: Neon PostgreSQL (Recommended - FREE)

**Why Neon?**

- 💰 Free tier with 3GB storage
- ⚡ Serverless PostgreSQL
- 🚀 Easy setup
- 🔗 Works perfectly with Streamlit Cloud

**Setup Steps:**

1. **Create Neon Account**

   - Go to: https://neon.tech/
   - Sign up with GitHub
   - Create new project

2. **Get Connection String**

   ```
   postgresql://username:password@ep-xxx.neon.tech/datawise_ai?sslmode=require
   ```

3. **Initialize Database**
   - Copy your `database/schema.sql`
   - Use Neon SQL Editor to run it
   - Or use this command locally:
   ```bash
   psql "postgresql://username:password@ep-xxx.neon.tech/datawise_ai?sslmode=require" -f database/schema.sql
   ```

### Option 2: ElephantSQL (FREE)

1. Go to: https://www.elephantsql.com/
2. Sign up and create "Tiny Turtle" (FREE)
3. Get connection URL
4. Run schema.sql using their browser console

### Option 3: Railway (FREE with GitHub Student Pack)

1. Go to: https://railway.app/
2. Connect GitHub
3. Deploy PostgreSQL
4. Get connection string

---

## 🚀 Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

1. **Ensure these files exist:**

   ```
   ✅ requirements.txt
   ✅ app.py
   ✅ config.py
   ✅ .gitignore (must exclude .env)
   ```

2. **Update `.gitignore`:**

   ```gitignore
   # MUST be in .gitignore
   .env
   *.pyc
   __pycache__/
   venv/
   uploads/
   logs/
   chroma_data/
   ```

3. **Remove any sensitive data:**

   ```bash
   # Check no secrets in git
   git log --all --full-history -- .env

   # If .env is tracked, remove it:
   git rm --cached .env
   git commit -m "Remove .env from tracking"
   ```

4. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

---

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**

   - Visit: https://share.streamlit.io/
   - Click "Sign in" with GitHub
   - Authorize Streamlit

2. **Create New App**

   - Click "New app"
   - Select your repository: `Kishor129129/datawise_ai`
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy!"

3. **Configure Secrets**

   Click "Advanced settings" > "Secrets" and add:

   ```toml
   # Gemini AI Configuration
   GEMINI_API_KEY = "your_gemini_api_key_here"
   GEMINI_MODEL = "gemini-2.0-flash-exp"

   # Database Configuration
   DATABASE_URL = "postgresql://user:pass@host:5432/datawise_ai"
   DB_HOST = "your-neon-host.neon.tech"
   DB_PORT = "5432"
   DB_NAME = "datawise_ai"
   DB_USER = "your_username"
   DB_PASSWORD = "your_password"

   # App Configuration
   UPLOAD_DIR = "uploads"
   LOG_LEVEL = "INFO"
   ```

4. **Deploy!**
   - Click "Deploy"
   - Wait 2-5 minutes
   - Your app will be live at: `https://your-app-name.streamlit.app`

---

## ⚙️ Configuration Adjustments for Cloud

### 1. Update `config.py` for Cloud Environment

Modify `config.py` to handle Streamlit Cloud secrets:

```python
import streamlit as st
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Try Streamlit secrets first, then environment variables
    def __init__(self):
        super().__init__()

        # Load from Streamlit secrets if available
        if hasattr(st, 'secrets'):
            try:
                self.gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
                self.database_url = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", ""))
                self.db_host = st.secrets.get("DB_HOST", os.getenv("DB_HOST", "localhost"))
                self.db_password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD", ""))
            except:
                pass  # Fall back to .env
```

### 2. Modify File Upload Handling

Since Streamlit Cloud is stateless, use these directories:

```python
# In config.py
upload_dir: str = "uploads"  # Will be created in container
chroma_dir: str = "chroma_data"
```

### 3. Handle ChromaDB Persistence

ChromaDB data won't persist between restarts on free tier. Consider:

**Option A:** Disable ChromaDB for cloud (conversation history only in memory)

**Option B:** Use external vector store (Pinecone, Weaviate)

**Option C:** Accept that chat history resets on restart

---

## 🐛 Troubleshooting

### Issue 1: ModuleNotFoundError

**Problem:** `No module named 'package_name'`

**Solution:**

1. Check `requirements.txt` includes all packages
2. Make sure versions are compatible
3. Redeploy

### Issue 2: Database Connection Error

**Problem:** `could not connect to server`

**Solution:**

1. Check DATABASE_URL is correct
2. Ensure database allows external connections
3. Check SSL mode: `?sslmode=require`
4. Verify database is running (Neon should be always on)

### Issue 3: Gemini API Errors

**Problem:** `Invalid API key` or `404 model not found`

**Solution:**

1. Verify API key in Secrets
2. Try different model: `gemini-1.5-flash`
3. Check API quota

### Issue 4: File Upload Fails

**Problem:** `Permission denied` when uploading

**Solution:**

1. Check `uploads/` directory is created
2. Use `@st.cache_resource` for directory creation
3. Consider using `tempfile` module

### Issue 5: App Keeps Restarting

**Problem:** App goes to sleep or restarts

**Solution:**

- **Free tier limitation:** App sleeps after 7 days of inactivity
- **Solution:** Visit app every few days or upgrade to paid tier
- **Workaround:** Use UptimeRobot to ping app every 5 minutes

---

## 📊 Streamlit Cloud Limits (Free Tier)

| Resource   | Free Tier Limit              |
| ---------- | ---------------------------- |
| CPU        | 1 core                       |
| Memory     | 1 GB                         |
| Storage    | Temporary only               |
| Apps       | 1 private + unlimited public |
| Sleep      | After 7 days inactivity      |
| Build Time | 10 minutes                   |

**Tips for staying within limits:**

- Optimize imports (lazy loading)
- Use `@st.cache_data` for data
- Minimize large file processing
- Use external DB (not SQLite)

---

## 🎯 Post-Deployment Checklist

- [ ] App is accessible at public URL
- [ ] File upload works
- [ ] Database connection successful
- [ ] Gemini AI responds to queries
- [ ] Charts generate correctly
- [ ] Chat interface works
- [ ] Reports can be downloaded
- [ ] No errors in logs
- [ ] Test with sample data
- [ ] Share URL with friends to test

---

## 🔐 Security Best Practices

1. **Never commit secrets:**

   ```bash
   # Add to .gitignore
   .env
   secrets.toml
   ```

2. **Use Streamlit Secrets Manager:**

   - Always configure via web UI
   - Never hardcode API keys

3. **Rotate API keys:**

   - Generate new keys for production
   - Don't use development keys

4. **Monitor usage:**
   - Check Gemini API quota
   - Monitor database size
   - Watch app logs

---

## 📈 Monitoring Your App

### View Logs

1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app" > "Logs"
4. Monitor real-time logs

### Analytics

- Streamlit Cloud shows:
  - Number of visitors
  - App uptime
  - Resource usage

### Set Up Alerts

- Use UptimeRobot: https://uptimerobot.com/
- Monitor every 5 minutes
- Get email alerts if app is down

---

## 🚀 Performance Optimization

### 1. Use Caching

```python
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

@st.cache_resource
def init_database():
    return DatabaseHandler()
```

### 2. Lazy Load Imports

```python
# Only import when needed
if st.button("Generate Chart"):
    import plotly.express as px
    fig = px.bar(...)
```

### 3. Optimize Database Queries

```python
# Limit results
SELECT * FROM data LIMIT 1000

# Use indexes
CREATE INDEX idx_date ON data(date);
```

### 4. Reduce API Calls

```python
# Cache Gemini responses
@st.cache_data(ttl=3600)
def get_ai_response(prompt):
    return gemini.generate(prompt)
```

---

## 💰 Cost Considerations

### Free Resources:

- ✅ Streamlit Cloud (1 public app)
- ✅ Neon PostgreSQL (3GB)
- ✅ Gemini API (60 requests/min)
- ✅ GitHub (unlimited public repos)

**Total Cost: $0/month** 🎉

### Paid Options (If Needed):

| Service       | Cost        | When to Upgrade    |
| ------------- | ----------- | ------------------ |
| Streamlit Pro | $20/mo      | Need private apps  |
| Neon Scale    | $19/mo      | Need >3GB storage  |
| Gemini Paid   | Usage-based | Need higher limits |

---

## 🔄 Updating Your Deployed App

1. **Make changes locally**
2. **Test thoroughly**
3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Update feature X"
   git push origin main
   ```
4. **Auto-redeploy:** Streamlit Cloud auto-detects changes
5. **Wait 2-3 minutes** for rebuild

---

## 📱 Share Your App

Once deployed, share your app:

1. **Get your URL:**

   ```
   https://datawise-ai-kishor129129.streamlit.app
   ```

2. **Add to GitHub README:**

   ```markdown
   ## 🚀 Live Demo

   Try it here: [DataWise AI](https://your-app.streamlit.app)
   ```

3. **Add to LinkedIn:**

   - Post about your project
   - Include live demo link
   - Tag #DataScience #AI #Streamlit

4. **Add to Resume:**
   - Project section: Include live link
   - Shows recruiters you can deploy!

---

## 🎉 Success!

Your app is now live and accessible worldwide! 🌍

**Next steps:**

1. Test all features thoroughly
2. Add demo URL to README
3. Share on LinkedIn
4. Add to resume/portfolio

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io/streamlit-cloud
- **Neon Docs:** https://neon.tech/docs/introduction
- **Gemini API:** https://ai.google.dev/docs
- **Deployment Checklist:** https://docs.streamlit.io/streamlit-cloud/deploy-your-app

---

## 🆘 Need Help?

- **Streamlit Community:** https://discuss.streamlit.io/
- **GitHub Issues:** https://github.com/Kishor129129/datawise_ai/issues
- **Email:** your.email@example.com

---

**Good luck with deployment! 🚀**

Your recruiters will be impressed seeing a live, working AI application!
