# Complete Deployment Guide: kders.com Email Server on AWS EC2

## Overview
This guide will help you deploy your entire email server to AWS EC2 **without losing any local progress**. We'll use GitHub to safely push your code, then deploy on EC2.

---

## Prerequisites

### 1. AWS Account Setup
- [ ] AWS account created
- [ ] EC2 instance launched (recommended: **t3.medium** Ubuntu 22.04 LTS)
- [ ] Security Group configured (ports: 22, 25, 80, 110, 443, 587, 3000, 8000)
- [ ] Elastic IP allocated and associated

### 2. Cloudflare Setup
- [x] Domain kders.com registered on Cloudflare ✓
- [ ] DNS records configured (see CLOUDFLARE_DNS.md)

### 3. Local Requirements
- [ ] Git installed on your machine
- [ ] GitHub account created
- [ ] SSH key generated for GitHub

---

## Phase 1: Backup & GitHub Setup (30 minutes)

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create new repository:
   - Name: `kders-mail` (or any name you prefer)
   - Visibility: **Private** (recommended for production code)
   - Don't initialize with README (we have code already)

3. Copy the repository URL (looks like: `https://github.com/YOUR_USERNAME/kders-mail.git`)

### Step 2: Initialize Local Git (if not already done)

Open PowerShell in your project directory:

```powershell
cd "C:\Users\pkosh\OneDrive\Documents\Vit-sem5\CN\cp2"

# Check if git is already initialized
git status

# If not initialized:
git init
git branch -M main  # or keep "cn" branch if you prefer
```

### Step 3: Create .gitignore

```powershell
# Create .gitignore to exclude sensitive files
@"
# Environment variables
.env
.env.local
.env.production

# Node modules
frontend/node_modules/
node_modules/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
backend/.venv/
backend/venv/
*.egg-info/

# Database
*.db
*.sqlite

# Docker volumes
postgres_data/
mail_data/

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build artifacts
frontend/dist/
frontend/build/
"@ | Out-File -FilePath .gitignore -Encoding UTF8
```

### Step 4: Push to GitHub

```powershell
# Add all files
git add .

# Commit
git commit -m "Initial commit: kders.com email server"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/kders-mail.git

# Push to GitHub
git push -u origin main
```

**If you prefer the "cn" branch:**
```powershell
git branch -M cn
git push -u origin cn
```

---

## Phase 2: AWS EC2 Instance Setup (20 minutes)

### Step 1: Launch EC2 Instance

**AWS Console → EC2 → Launch Instance:**

| Setting | Value |
|---------|-------|
| Name | kders-mail-server |
| AMI | Ubuntu Server 22.04 LTS (Free tier eligible) |
| Instance Type | **t3.medium** (2 vCPU, 4GB RAM) - $30/month |
| Key Pair | Create new or use existing (save .pem file!) |
| Storage | 20 GB gp3 SSD |

**Alternative for testing**: t2.micro (1GB RAM) - Free tier, but may be slow

### Step 2: Configure Security Group

Create new security group named `kders-mail-sg`:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web |
| SMTP | TCP | 25 | 0.0.0.0/0 | Email receiving |
| Custom TCP | TCP | 587 | 0.0.0.0/0 | Email sending |
| Custom TCP | TCP | 110 | 0.0.0.0/0 | POP3 |
| Custom TCP | TCP | 3000 | 0.0.0.0/0 | Frontend (dev) |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Backend API (dev) |

**Production Note**: Remove ports 3000 and 8000 after setting up nginx.

### Step 3: Allocate Elastic IP

1. AWS Console → EC2 → Elastic IPs → Allocate
2. Select the new IP → Actions → **Associate**
3. Choose your instance: `kders-mail-server`
4. **Copy the Elastic IP** (e.g., `13.51.27.56`) - you'll need this for DNS!

### Step 4: Set Reverse DNS (PTR Record)

**CRITICAL for email delivery!**

1. Select your Elastic IP
2. Actions → **Update reverse DNS**
3. Enter: `mail.kders.com`
4. Confirm

---

## Phase 3: Cloudflare DNS Configuration (15 minutes)

### Go to Cloudflare Dashboard → kders.com → DNS

Add these records (replace `YOUR_EC2_IP` with your Elastic IP):

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | @ | YOUR_EC2_IP | 🔴 DNS only (grey cloud) |
| A | www | YOUR_EC2_IP | 🔴 DNS only |
| A | mail | YOUR_EC2_IP | 🔴 DNS only |
| MX | @ | mail.kders.com (priority 10) | - |
| TXT | @ | v=spf1 mx ip4:YOUR_EC2_IP ~all | - |
| TXT | _dmarc | v=DMARC1; p=quarantine; rua=mailto:admin@kders.com | - |

**⚠️ CRITICAL**: The orange cloud must be **OFF** (grey) for all A records! Email cannot work through Cloudflare proxy.

### Wait for DNS Propagation
DNS updates can take 5-15 minutes. Test with:
```powershell
nslookup kders.com
nslookup mail.kders.com
```

---

## Phase 4: Deploy to EC2 (30 minutes)

### Step 1: Connect to EC2

Using PowerShell:
```powershell
# Navigate to where you saved your .pem key
cd C:\path\to\your\key

# Connect (replace with your Elastic IP)
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

### Step 2: Update deploy-ec2.sh

Before running, update the script with your GitHub repo:

```bash
# On EC2, download the deploy script
wget https://raw.githubusercontent.com/YOUR_USERNAME/kders-mail/main/deploy-ec2.sh

# Make it executable
chmod +x deploy-ec2.sh

# Edit it to add your GitHub repo URL
nano deploy-ec2.sh
# Change line: GITHUB_REPO="https://github.com/YOUR_USERNAME/kders-mail.git"
```

### Step 3: Run Deployment Script

```bash
# Run the deployment
sudo ./deploy-ec2.sh
```

This script will:
1. ✅ Update system packages
2. ✅ Install Docker & Docker Compose
3. ✅ Configure firewall (UFW)
4. ✅ Clone your GitHub repository
5. ✅ Generate secure environment variables
6. ✅ Obtain SSL certificates from Let's Encrypt
7. ✅ Start all Docker containers

**Expected time**: 10-15 minutes

### Step 4: Verify Deployment

```bash
# Check running containers
sudo docker ps

# You should see:
# - kders-db (PostgreSQL)
# - kders-backend (FastAPI)
# - kders-frontend (React)
# - kders-smtp (Email server)
# - kders-pop3 (POP3 server)
# - kders-nginx (Web server)

# Check logs
sudo docker-compose -f /opt/kders-mail/docker-compose.prod.yml logs --tail 50

# Test web access
curl localhost:3000  # Should return HTML
```

---

## Phase 5: DKIM Configuration (10 minutes)

DKIM (DomainKeys Identified Mail) proves your emails are legitimate.

### Generate DKIM Keys

```bash
# SSH into EC2
cd /opt/kders-mail

# Generate private key
sudo docker exec kders-smtp openssl genrsa -out /tmp/dkim_private.pem 2048

# Generate public key
sudo docker exec kders-smtp openssl rsa -in /tmp/dkim_private.pem -pubout -out /tmp/dkim_public.pem

# Display public key
sudo docker exec kders-smtp cat /tmp/dkim_public.pem
```

### Add DKIM to Cloudflare

Copy the public key (remove `-----BEGIN/END-----` and newlines):

**Cloudflare DNS → Add Record:**
```
Type: TXT
Name: default._domainkey
Content: v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE
TTL: Auto
```

---

## Phase 6: Testing (15 minutes)

### Test 1: Web UI Access

Open browser: `https://kders.com`

You should see your WhatsApp-style email UI with blue theme!

### Test 2: Register User

1. Click "Register"
2. Create account: `test@kders.com`
3. Login

### Test 3: Send Internal Email

1. Click "Compose" button
2. To: `admin@kders.com`
3. Subject: "Test email"
4. Send

### Test 4: Send External Email

**From your EC2 instance:**
```bash
# Test SMTP
telnet mail.kders.com 587

# If telnet works, send test email:
EHLO mail.kders.com
MAIL FROM:<test@kders.com>
RCPT TO:<your-personal-email@gmail.com>
DATA
Subject: Test from kders.com

This is a test email from my kders.com server!
.
QUIT
```

### Test 5: Receive External Email

Send an email **from Gmail** to `test@kders.com`

Check if it appears in your inbox!

### Test 6: Spam Score Check

1. Go to [mail-tester.com](https://www.mail-tester.com/)
2. Send email to the address they provide
3. Check your spam score (aim for 8/10 or higher)

---

## Phase 7: Production Hardening (Optional but Recommended)

### 1. Enable Firewall Logging
```bash
sudo ufw logging on
```

### 2. Configure Fail2Ban (Prevent brute force)
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Set Up Automatic SSL Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab (runs daily)
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --post-hook "docker restart kders-nginx"
```

### 4. Database Backups
```bash
# Create backup script
sudo tee /opt/backup-db.sh > /dev/null <<'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec kders-db pg_dump -U mailuser maildb > /opt/backups/db_$DATE.sql
# Keep only last 7 days
find /opt/backups -name "db_*.sql" -mtime +7 -delete
EOF

sudo chmod +x /opt/backup-db.sh
sudo mkdir -p /opt/backups

# Run daily at 2 AM
sudo crontab -e
# Add: 0 2 * * * /opt/backup-db.sh
```

### 5. Monitoring (Optional)
```bash
# Install monitoring tools
sudo apt-get install -y htop iftop

# Check resources
htop  # CPU/RAM usage
iftop # Network traffic
sudo docker stats  # Container resources
```

---

## Cost Breakdown

| Item | Cost |
|------|------|
| AWS EC2 t3.medium | $30/month |
| Elastic IP | Free (if attached) |
| Domain (Cloudflare) | $8-15/year |
| SSL Certificate | Free (Let's Encrypt) |
| **Total** | **~$30/month** |

**Cost Savings:**
- Use t2.micro (free tier) for testing: $0/month for 12 months
- GitHub Student Pack: AWS credits if you're a student
- Reserved Instances: Save 30-50% on EC2 if you commit to 1 year

---

## Troubleshooting

### Problem: Can't SSH into EC2
**Solution:**
```powershell
# Fix .pem permissions (Windows)
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "$($env:USERNAME):(R)"
```

### Problem: DNS not resolving
**Solution:**
- Wait 15 minutes for propagation
- Clear DNS cache: `ipconfig /flushdns` (Windows)
- Check Cloudflare: Make sure proxy (orange cloud) is OFF

### Problem: SSL certificate failed
**Solution:**
```bash
# Stop nginx to free port 80
sudo docker stop kders-nginx

# Re-run certbot
sudo certbot certonly --standalone -d kders.com -d mail.kders.com -d www.kders.com

# Restart nginx
sudo docker start kders-nginx
```

### Problem: Emails going to spam
**Solutions:**
1. Verify PTR record: `nslookup -type=PTR YOUR_EC2_IP`
2. Check SPF: `nslookup -type=TXT kders.com`
3. Verify DKIM: `nslookup -type=TXT default._domainkey.kders.com`
4. Test at [mail-tester.com](https://www.mail-tester.com/)
5. Warm up IP: Send 10-20 emails/day for first week

### Problem: Port 25 blocked by AWS
**Solution:**
- AWS blocks port 25 by default to prevent spam
- Request removal: [AWS EC2 Request to Remove Email Sending Limitations](https://aws.amazon.com/forms/ec2-email-limit-rdns-request)
- Approval takes 24-48 hours
- Alternative: Use port 587 for sending (already configured)

---

## Maintenance Tasks

### Weekly
- [ ] Check docker logs: `sudo docker-compose logs --tail 100`
- [ ] Monitor disk space: `df -h`
- [ ] Review fail2ban: `sudo fail2ban-client status sshd`

### Monthly
- [ ] Update packages: `sudo apt-get update && sudo apt-get upgrade`
- [ ] Review backups: `ls -lh /opt/backups/`
- [ ] Check SSL expiry: `sudo certbot certificates`

### As Needed
- [ ] Scale EC2 instance if slow
- [ ] Add monitoring (CloudWatch, Prometheus)
- [ ] Set up CDN for static assets

---

## Next Steps After Deployment

1. **Custom Domain Email Addresses**
   - Create accounts for your team: `admin@kders.com`, `support@kders.com`
   - Set up email groups for departments

2. **Email Client Setup**
   - Configure Thunderbird/Outlook to connect to `mail.kders.com:110` (POP3)
   - Or use webmail at `https://kders.com`

3. **Integrate with External Services**
   - Add SMTP settings to your applications (port 587)
   - Send automated emails from your apps

4. **Analytics & Monitoring**
   - Set up email logs dashboard
   - Track delivery rates
   - Monitor spam complaints

---

## Emergency Rollback

If something goes wrong, you can always rollback:

```bash
# On EC2
cd /opt/kders-mail
sudo docker-compose down

# Pull previous version
git log  # Find previous commit hash
git checkout <previous-commit-hash>

# Redeploy
sudo docker-compose up -d
```

**Your local code is safe** - it's on your machine AND GitHub!

---

## Support Resources

- **AWS EC2 Docs**: https://docs.aws.amazon.com/ec2/
- **Cloudflare DNS Docs**: https://developers.cloudflare.com/dns/
- **Let's Encrypt**: https://letsencrypt.org/docs/
- **Docker Compose**: https://docs.docker.com/compose/
- **Email Best Practices**: https://www.mailgun.com/blog/email/email-best-practices/

---

## Success Checklist

- [ ] GitHub repository created and code pushed
- [ ] EC2 instance running
- [ ] Elastic IP allocated and PTR record set
- [ ] Cloudflare DNS configured (A, MX, SPF, DMARC records)
- [ ] Deploy script executed successfully
- [ ] SSL certificates obtained
- [ ] DKIM configured
- [ ] Web UI accessible at https://kders.com
- [ ] Internal email working (kders.com → kders.com)
- [ ] External email sending working (kders.com → gmail.com)
- [ ] External email receiving working (gmail.com → kders.com)
- [ ] Spam score 8/10 or higher
- [ ] Database backups configured
- [ ] Automatic SSL renewal set up

---

**You're ready to deploy! Your progress is safe in Git, and you can always rollback if needed.** 🚀
