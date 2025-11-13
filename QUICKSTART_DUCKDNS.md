# Quick Start: Deploy with DuckDNS (100% FREE!)

## Why DuckDNS?

✅ **Completely FREE** - No domain purchase needed
✅ **Quick Setup** - 5 minutes to get your domain
✅ **Perfect for Projects** - Great for assignments, learning, testing
✅ **Easy Migration** - Can upgrade to paid domain later

Your email will be: `username@yourname.duckdns.org`

---

## Part 1: DuckDNS Setup (5 minutes)

### Step 1: Get Your DuckDNS Domain

1. Go to [https://www.duckdns.org/](https://www.duckdns.org/)
2. Sign in with GitHub, Google, or Reddit
3. Enter your subdomain: `kders` (or pick any name)
4. Click **"add domain"**
5. You now have: `kders.duckdns.org` ✅

**Copy your token** (shown at top of page) - you'll need it!

### Step 2: Update deploy-ec2.sh

Edit your `deploy-ec2.sh` file:

```bash
# Line 15-16: Change to YOUR DuckDNS subdomain
DOMAIN="kders.duckdns.org"  # Replace 'kders' with YOUR subdomain
MAIL_SUBDOMAIN="kders.duckdns.org"
```

---

## Part 2: AWS EC2 Setup (15 minutes)

### Step 1: Launch EC2 Instance

**AWS Console → EC2 → Launch Instance:**

| Setting | Value |
|---------|-------|
| Name | kders-mail-server |
| AMI | Ubuntu Server 22.04 LTS |
| Type | **t2.micro** (FREE tier!) or t3.medium |
| Storage | 20 GB |
| Key Pair | Create new (.pem file) |

**Security Group** - Allow these ports:
```
22 (SSH)
25 (SMTP)
80 (HTTP)
110 (POP3)
443 (HTTPS)
587 (SMTP Submission)
3000 (Frontend Dev)
8000 (Backend Dev)
```

### Step 2: Get Elastic IP

1. EC2 → Elastic IPs → **Allocate Elastic IP**
2. Select it → Actions → **Associate Elastic IP**
3. Choose your instance
4. **Copy the IP** (e.g., `54.123.45.67`)

### Step 3: Set Reverse DNS (PTR Record)

1. Select your Elastic IP
2. Actions → **Update reverse DNS**
3. Enter: `kders.duckdns.org` (your DuckDNS domain)
4. Confirm

### Step 4: Update DuckDNS with Your IP

1. Go back to [DuckDNS.org](https://www.duckdns.org/)
2. Find your domain: `kders.duckdns.org`
3. Paste your **Elastic IP** in the "current ip" field
4. Click **"update ip"** ✅

### Step 5: Test DNS

```powershell
# Wait 2 minutes, then test:
nslookup kders.duckdns.org

# Should return your Elastic IP!
```

---

## Part 3: Push to GitHub (5 minutes)

```powershell
cd "C:\Users\pkosh\OneDrive\Documents\Vit-sem5\CN\cp2"

# If you haven't created GitHub repo yet:
# 1. Go to https://github.com/new
# 2. Name: kders-mail
# 3. Private: Yes

# Update deploy-ec2.sh with your GitHub URL (line 17)
# GITHUB_REPO="https://github.com/YOUR_USERNAME/kders-mail.git"

git add deploy-ec2.sh DUCKDNS_SETUP.md
git commit -m "Configure for DuckDNS"
git push origin cn
```

---

## Part 4: Deploy to EC2 (15 minutes)

### Step 1: SSH into EC2

```powershell
# From folder with your .pem file:
ssh -i "kders-key.pem" ubuntu@13.51.27.56
```

**If SSH fails** (Windows permissions issue):
```powershell
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "$($env:USERNAME):(R)"
```

### Step 2: Run Deployment

```bash
# Download deploy script
wget https://raw.githubusercontent.com/kdeprasad/kders-mail/cn/deploy-ec2.sh

# Make executable
chmod +x deploy-ec2.sh

# Run deployment
sudo ./deploy-ec2.sh
```

**Wait 10-15 minutes** for:
- Docker installation
- Repository cloning
- Package installation
- SSL certificate generation
- Container startup

### Step 3: Verify Deployment

```bash
# Check all containers are running:
sudo docker ps

# Should see 6 containers:
# - kders-db (PostgreSQL)
# - kders-backend (FastAPI)
# - kders-frontend (React)
# - kders-smtp (Email sending)
# - kders-pop3 (Email receiving)
# - kders-nginx (Web server)

# Check logs for errors:
sudo docker-compose logs --tail 50
```

---

## Part 5: Test Everything (10 minutes)

### Test 1: Web UI

Open browser: `http://kders.duckdns.org` (or https if SSL worked)

Should see your WhatsApp-style email UI! 🎉

### Test 2: Create Account

1. Click **"Register"**
2. Username: `test`
3. Email will be: `test@kders.duckdns.org`
4. Password: (your choice)
5. Register ✅

### Test 3: Send Internal Email

1. Login as `test@kders.duckdns.org`
2. Click **"Compose"**
3. To: `admin@kders.duckdns.org` (create this account first)
4. Subject: "Test email"
5. Send ✅

**Should work perfectly!** ✅

### Test 4: Send to Gmail (Optional)

Send email to your personal Gmail:
- **Expected:** Email arrives but may be in **Spam folder**
- **Why:** Free subdomains have lower reputation
- **Solution:** Ask recipient to mark "Not Spam"

### Test 5: Receive from Gmail

Send email from Gmail to `test@kders.duckdns.org`
- **Expected:** Should work! ✅
- Receiving is easier than sending

---

## Understanding Email Delivery with DuckDNS

### What Works Great ✅
- **Internal emails** (user@yourdomain → user2@yourdomain)
- **Web UI** (interface works perfectly)
- **Receiving emails** (from Gmail, Outlook, etc.)
- **POP3/SMTP** (all protocols work)

### What Has Limitations ⚠️
- **Outgoing emails to Gmail/Outlook** → May go to spam
- **Email reputation** → Takes time to build
- **Professional appearance** → `@kders.duckdns.org` vs `@kders.com`

### Why Free Domains Go to Spam?
1. **No SPF/DKIM/DMARC** records (DuckDNS only supports A records)
2. **Shared reputation** (many people use DuckDNS)
3. **Less trust** from email providers

### Solutions:

**Option 1: Accept It (Recommended for Projects)**
- Use for internal emails
- Great for assignments/learning
- Recipients can whitelist your address

**Option 2: Improve Reputation**
- Send emails slowly (10-20/day)
- Ask recipients to mark "Not Spam"
- Use [mail-tester.com](https://www.mail-tester.com/) to check score

**Option 3: Upgrade Later**
- Buy domain ($12/year)
- Add SPF/DKIM/DMARC records
- Keep all your code/data
- Better email delivery

---

## Cost Breakdown

| Item | DuckDNS | With Paid Domain |
|------|---------|------------------|
| Domain | **$0** ✅ | $12/year |
| EC2 t2.micro | **$0** (12 months free) | $0 (12 months free) |
| Elastic IP | **$0** (if attached) | $0 (if attached) |
| SSL Certificate | **$0** (Let's Encrypt) | $0 (Let's Encrypt) |
| **Total Year 1** | **$0** 🎉 | $12 |
| **Total Year 2+** | $96/year (EC2 after free tier) | $108/year |

**For EC2 after free tier ends:**
- t2.micro: $8/month = $96/year
- t3.medium: $30/month = $360/year

---

## Troubleshooting

### Can't access web UI?

```bash
# Check if nginx is running:
sudo docker ps | grep nginx

# Check logs:
sudo docker logs kders-nginx

# Make sure security group allows port 80/443
```

### DNS not resolving?

```bash
# Test DNS:
nslookup kders.duckdns.org

# If wrong IP, update DuckDNS:
# Go to duckdns.org and click "update ip"
```

### SSL certificate failed?

```bash
# Common issue: Port 80 not accessible
sudo ufw status  # Check firewall
sudo ufw allow 80

# Retry certbot:
sudo certbot certonly --standalone -d kders.duckdns.org
```

### Emails not sending?

```bash
# Check SMTP logs:
sudo docker logs kders-smtp

# Test SMTP manually:
telnet kders.duckdns.org 587

# Check AWS port 25 limitation (may need to request access)
```

### AWS Port 25 Blocked?

AWS blocks port 25 by default. You need to:
1. Request removal: [AWS Form](https://aws.amazon.com/forms/ec2-email-limit-rdns-request)
2. Takes 24-48 hours
3. Meanwhile, port 587 works for sending!

---

## Next Steps After Deployment

### For Class Project:
✅ Take screenshots of:
- Web UI working
- Sending internal email
- Email in inbox
- Docker containers running

✅ Document your setup:
- Architecture diagram
- Technologies used (FastAPI, React, PostgreSQL, Docker)
- Features implemented

### For Learning:
✅ Try these experiments:
- Create multiple users
- Send group messages
- Test AI chatbot
- Explore MCP server

### For Production:
✅ Consider upgrading:
- Buy domain ($12/year)
- Add email authentication (SPF/DKIM)
- Scale EC2 instance if needed
- Add monitoring

---

## Migration: DuckDNS → Paid Domain (Later)

When ready to upgrade (without losing data):

1. **Buy domain** (Namecheap, Cloudflare, etc.)
2. **Point DNS** to your EC2 IP
3. **Update .env**:
   ```bash
   MAIL_DOMAIN=yourdomain.com
   ```
4. **Restart containers**:
   ```bash
   cd /opt/kders-mail
   sudo docker-compose down
   sudo docker-compose up -d
   ```
5. **Get new SSL**:
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com
   ```

**All your data stays!** Users, emails, settings preserved.

---

## Success Checklist

- [ ] DuckDNS account created
- [ ] Subdomain registered (e.g., `kders.duckdns.org`)
- [ ] EC2 instance launched
- [ ] Elastic IP allocated and associated
- [ ] PTR record set in AWS
- [ ] DuckDNS updated with Elastic IP
- [ ] GitHub repo created and code pushed
- [ ] deploy-ec2.sh updated with DuckDNS domain
- [ ] Deployed to EC2 successfully
- [ ] All 6 containers running
- [ ] Web UI accessible
- [ ] Test account created
- [ ] Internal email working
- [ ] (Optional) External email tested

---

## Your Email Server URLs

- **Web UI:** http://kders.duckdns.org (or https)
- **API:** http://kders.duckdns.org/api
- **SMTP:** kders.duckdns.org:587
- **POP3:** kders.duckdns.org:110
- **Your emails:** `username@kders.duckdns.org`

---

## Summary

**DuckDNS = Perfect for You Because:**
- ✅ **FREE** ($0 setup, $0 ongoing)
- ✅ **Quick** (30 minutes total setup)
- ✅ **Simple** (no DNS complexity)
- ✅ **Flexible** (upgrade to paid domain anytime)
- ✅ **Educational** (learn email servers)

**You're Ready!** 🚀

Follow the steps above and you'll have a working email server in about **45 minutes**!

---

## Need Help?

Read these guides:
- `DUCKDNS_SETUP.md` - Detailed DuckDNS info
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `READY_TO_DEPLOY.md` - Overview

**Questions?** Just ask! I'm here to help. 🦆
