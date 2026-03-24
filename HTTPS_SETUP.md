# HTTPS/SSL Setup Guide - KimiClaw

This guide helps you set up HTTPS with automatic SSL certificates using Traefik and Let's Encrypt.

---

## 🚀 Quick Start

### 1. Configure Your Domain

Edit `.env` and set your domain:

```bash
# Required: Your domain name
DOMAIN=kimiclaw.yourdomain.com

# Required: Email for SSL certificate notifications
ACME_EMAIL=admin@yourdomain.com

# Add your real API keys
OPENAI_API_KEY=sk-your-real-api-key
```

### 2. Start with HTTPS

```bash
# Start with HTTPS enabled
docker-compose -f docker-compose.https.yml up -d
```

### 3. Access Your Secure Site

- **Main Application:** https://kimiclaw.yourdomain.com
- **Agent0:** https://agent0.yourdomain.com
- **Traefik Dashboard:** http://localhost:8080 (development only)

---

## 📋 Prerequisites

### A. Domain Name
You need a domain name pointing to your server:

```
Type: A Record
Name: kimiclaw
Value: YOUR_SERVER_IP
```

And for Agent0 (optional):
```
Type: A Record
Name: agent0
Value: YOUR_SERVER_IP
```

### B. Open Ports
Ensure these ports are open in your firewall:
- `80/tcp` - HTTP (auto-redirects to HTTPS)
- `443/tcp` - HTTPS

---

## 🔒 Security Features

### Automatic HTTPS Redirection
All HTTP traffic is automatically redirected to HTTPS with a 301 permanent redirect.

### SSL/TLS Configuration
- **Provider:** Let's Encrypt (free, auto-renewing)
- **Challenge Type:** TLS-ALPN-01
- **Auto-Renewal:** 30 days before expiry
- **Encryption:** TLS 1.2+

### Security Headers
The following headers are automatically added:

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload | HSTS |
| X-Content-Type-Options | nosniff | MIME sniffing protection |
| X-XSS-Protection | 1; mode=block | XSS protection |

---

## 🔧 Configuration Options

### Using Self-Signed Certificates (Local Development)

For local testing without a domain:

```bash
# Generate self-signed certificate
mkdir -p letsencrypt
cd letsencrypt
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout localhost.key -out localhost.crt \
  -subj "/CN=localhost"

# Use http only for local development
docker-compose -f docker-compose.yml up -d
```

### Custom SSL Certificate

If you have your own SSL certificate:

```yaml
# docker-compose.custom-ssl.yml
services:
  traefik:
    volumes:
      - ./certs:/certs:ro
    command:
      - "--entrypoints.websecure.http.tls.certificates.certFile=/certs/cert.pem"
      - "--entrypoints.websecure.http.tls.certificates.keyFile=/certs/key.pem"
```

### Multiple Domains (SAN Certificates)

Add multiple domains to your router:

```yaml
labels:
  - "traefik.http.routers.kimiclaw.rule=Host(`kimiclaw.com`, `www.kimiclaw.com`, `app.kimiclaw.com`)"
```

---

## 📊 Monitoring

### View Traefik Dashboard
```bash
# Access dashboard (development only)
open http://localhost:8080
```

### Check SSL Certificate Status
```bash
# View certificate details
docker exec kimiclaw-traefik cat /letsencrypt/acme.json | jq

# Check certificate expiry
echo | openssl s_client -servername kimiclaw.yourdomain.com -connect kimiclaw.yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### View Logs
```bash
# Traefik logs
docker logs -f kimiclaw-traefik

# Application logs
docker logs -f kimiclaw-app
```

---

## 🛠️ Troubleshooting

### Certificate Not Issued

**Problem:** SSL certificate not generated

**Solutions:**
1. Check domain DNS is pointing to server
2. Verify ports 80/443 are open
3. Check Traefik logs: `docker logs kimiclaw-traefik`
4. Ensure ACME_EMAIL is set in `.env`

```bash
# Test Let's Encrypt connectivity
curl -I http://kimiclaw.yourdomain.com/.well-known/acme-challenge/test
```

### HTTPS Redirect Loop

**Problem:** Too many redirects

**Solution:** Clear browser cache or test with curl:
```bash
curl -I -L http://kimiclaw.yourdomain.com
```

### Certificate Expired

**Problem:** SSL certificate expired

**Solution:**
```bash
# Force certificate renewal
docker exec kimiclaw-traefik traefik certificateResolver --resolverName letsencrypt

# Or restart Traefik
docker-compose -f docker-compose.https.yml restart traefik
```

### Rate Limit Exceeded

Let's Encrypt has rate limits:
- **50 certificates per domain per week**
- **5 duplicate certificates per week**

**Solution:** Wait or use staging server:
```yaml
command:
  - "--certificatesresolvers.letsencrypt.acme.caserver=https://acme-staging-v02.api.letsencrypt.org/directory"
```

---

## 🔄 Maintenance

### Update SSL Certificates
Certificates auto-renew 30 days before expiry. To force renewal:

```bash
docker-compose -f docker-compose.https.yml restart traefik
```

### Backup Certificates
```bash
# Backup
cp -r letsencrypt letsencrypt.backup.$(date +%Y%m%d)

# Restore
cp -r letsencrypt.backup.20260324 letsencrypt
```

### Renew Manually
```bash
# Delete certificate to force renewal
rm letsencrypt/acme.json
docker-compose -f docker-compose.https.yml restart traefik
```

---

## 📝 Docker Compose Commands

```bash
# Start with HTTPS
docker-compose -f docker-compose.https.yml up -d

# Stop
docker-compose -f docker-compose.https.yml down

# Restart
docker-compose -f docker-compose.https.yml restart

# View logs
docker-compose -f docker-compose.https.yml logs -f

# Update images
docker-compose -f docker-compose.https.yml pull
docker-compose -f docker-compose.https.yml up -d
```

---

## 🔐 Security Checklist

- [ ] Domain points to server IP
- [ ] Firewall allows ports 80/443
- [ ] `.env` file secured (chmod 600)
- [ ] Real API keys configured
- [ ] Traefik dashboard disabled in production
- [ ] SSL certificate successfully issued
- [ ] HTTPS redirect working
- [ ] HSTS headers present

---

## 📞 Support

For issues with:
- **Let's Encrypt:** https://letsencrypt.org/docs/
- **Traefik:** https://doc.traefik.io/
- **Docker:** https://docs.docker.com/

---

**Note:** Replace `kimiclaw.yourdomain.com` with your actual domain name in all examples.
