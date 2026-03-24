# Streamlit Cloud Deployment Guide

**URL:** https://openklaw.streamlit.app

---

## 🚀 Quick Deploy

### 1. Prepare Repository

Ensure your repository has:
```
openklaw/
├── .streamlit/
│   └── config.toml          ✅ Streamlit configuration
├── interface/
│   └── app.py               ✅ Main application
├── .env                     ✅ Environment template
└── requirements.txt         ✅ Dependencies
```

### 2. Add Secrets to Streamlit Cloud

In your Streamlit Cloud dashboard:

1. Go to: **App → Settings → Secrets**
2. Add your API keys:

```toml
[secrets]
OPENAI_API_KEY = "sk-your-real-api-key-here"
OPENAI_API_BASE = "https://api.moonshot.cn/v1"
EVALUATION_API_KEY = "sk-your-real-api-key-here"
EVALUATION_API_BASE = "https://api.moonshot.cn/v1"
WEB_SEARCH_API_KEY = "tvly-your-key-here"
E2B_API_KEY = "e2b-your-key-here"
DISABLE_SIMULATION = "true"
```

### 3. Deploy

1. Visit: https://share.streamlit.io
2. Connect your GitHub repository
3. Select branch: `main`
4. Main file path: `interface/app.py`
5. Click **Deploy**

---

## 🔒 HTTPS on Streamlit Cloud

✅ **Already Enabled!**

Streamlit Cloud automatically provides:
- SSL/TLS certificates (Let's Encrypt)
- HTTPS enforcement
- Security headers
- DDoS protection
- Global CDN

No configuration needed!

---

## 📊 Streamlit Cloud Features

| Feature | Status |
|---------|--------|
| HTTPS | ✅ Automatic |
| SSL Certificates | ✅ Auto-renewed |
| Custom Domain | ✅ Supported |
| Secrets Management | ✅ Built-in |
| Version Control | ✅ GitHub integration |
| Rollback | ✅ One-click |

---

## 🔐 Security on Streamlit Cloud

### Secrets Management
Never commit real API keys to GitHub!

**Wrong:**
```python
# ❌ Don't do this!
OPENAI_API_KEY = "sk-real-key-in-code"
```

**Right:**
```python
# ✅ Use Streamlit secrets
import streamlit as st
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
```

### User Data Collection Notice

Your app currently collects user data (IP addresses, requests).

**Required for DSGVO/GDPR compliance:**
1. Add Privacy Policy
2. Add Cookie Consent
3. Data retention policy
4. User data deletion option

---

## ⚙️ Configuration

### Custom Domain (Optional)

To use your own domain:

1. Go to **Settings → Domain**
2. Enter your domain: `kimiclaw.yourdomain.com`
3. Add DNS CNAME record:
   ```
   Type: CNAME
   Name: kimiclaw
   Value: openklaw.streamlit.app
   ```
4. Wait for SSL certificate provisioning

### Environment Variables

Streamlit Cloud uses `st.secrets` instead of `.env`:

```python
import streamlit as st

# Access secrets
api_key = st.secrets["OPENAI_API_KEY"]
api_base = st.secrets.get("OPENAI_API_BASE", "https://api.moonshot.cn/v1")
```

---

## 🔄 Updating Your App

### Automatic Updates
Every push to `main` branch automatically redeploys!

```bash
git add .
git commit -m "Update feature X"
git push origin main
# App automatically redeploys!
```

### Manual Restart
In Streamlit Cloud dashboard:
**App → Settings → Reboot**

---

## 🛠️ Troubleshooting

### App Won't Start

**Check logs:**
1. Streamlit Cloud dashboard → Logs
2. Look for Python errors

**Common issues:**
- Missing `requirements.txt`
- Import errors
- Missing secrets

### Secrets Not Working

Verify in dashboard:
1. Settings → Secrets
2. Check key names match exactly
3. No extra spaces

### Rate Limiting Issues

Streamlit Cloud has limits:
- 1 GB RAM per app
- Limited CPU
- Rate limits on API calls

**Optimize:**
- Use caching: `@st.cache_data`
- Minimize API calls
- Compress data

---

## 📈 Monitoring

### Usage Analytics
Streamlit Cloud provides:
- Viewer count
- App usage stats
- Error tracking

### Custom Analytics
Add to your app:
```python
import streamlit as st

# Track page views
if 'page_views' not in st.session_state:
    st.session_state.page_views = 0
st.session_state.page_views += 1
```

---

## 📝 Files to Ignore

Add to `.gitignore`:
```
.env
*.env
__pycache__/
*.pyc
.DS_Store
```

**Never commit:**
- `.env` with real keys
- `data/` directory (user data)
- `memory/` directory
- Log files

---

## 🌐 Your App

**Production URL:**
```
https://openklaw.streamlit.app
```

**Features Active:**
- ✅ One request per user limit
- ✅ User botnet collection
- ✅ Multi-language warnings (DE/EN/ES)
- ✅ HTTPS encryption
- ✅ Rate limiting

---

## 🚨 Security Checklist

Before sharing your URL:

- [ ] Real API keys in Streamlit Secrets (not in code)
- [ ] `.env` in `.gitignore`
- [ ] Privacy policy added
- [ ] Cookie consent banner
- [ ] User data collection warning visible
- [ ] Rate limiting tested
- [ ] HTTPS working (check padlock icon)

---

## 📞 Support

- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-cloud
- **Community Forum:** https://discuss.streamlit.io
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues

---

**Your app is ready at: https://openklaw.streamlit.app** 🎉
