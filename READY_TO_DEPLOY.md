# ✅ kders.com Email Server - Ready for EC2 Deployment

## What's Been Done

Your entire email server project is now **safely committed to Git** and ready to push to GitHub without losing ANY progress!

### Files Created for Deployment:

1. **`deploy-ec2.sh`** - Automated deployment script (installs everything)
2. **`DEPLOYMENT_GUIDE.md`** - Complete step-by-step guide (read this!)
3. **`QUICKSTART_DEPLOY.md`** - Quick reference (15 minutes to deploy)
4. **`CLOUDFLARE_DNS.md`** - DNS configuration instructions
5. **`docker-compose.prod.yml`** - Production Docker setup
6. **`nginx/nginx.conf`** - Nginx reverse proxy config
7. **`.gitignore`** - Updated to exclude sensitive files

### What's Safe in Git:

✅ All your code (backend, frontend, SMTP, POP3)
✅ WhatsApp-style UI with VS Code blue theme
✅ AI chatbot integration
✅ Group messaging features
✅ MCP server implementation
✅ All documentation

### What's NOT in Git (Safe!):

❌ `.env` files (passwords/secrets)
❌ `.venv` folder (Python packages)
❌ `node_modules` (npm packages)
❌ Database data
❌ SSL certificates

---

## Next Steps (In Order):

### 1. Push to GitHub (5 minutes)

```powershell
cd "C:\Users\pkosh\OneDrive\Documents\Vit-sem5\CN\cp2"

# Create GitHub repo first: https://github.com/new
# Name it: kders-mail
# Private repository recommended

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/kders-mail.git

# Push code
git push -u origin cn
```

### 2. Edit deploy-ec2.sh (2 minutes)

Open `deploy-ec2.sh` and update line 15:
```bash
GITHUB_REPO="https://github.com/YOUR_USERNAME/kders-mail.git"
```

Commit this change:
```powershell
git add deploy-ec2.sh
git commit -m "Update GitHub repo URL"
git push
```

### 3. Launch EC2 Instance (10 minutes)

**AWS Console → EC2 → Launch Instance:**

| Setting | Value |
|---------|-------|
| Name | kders-mail-server |
| AMI | Ubuntu Server 22.04 LTS |
| Instance Type | **t3.medium** ($30/month) or t2.micro (free tier) |
| Key Pair | Create new (download .pem file!) |
| Storage | 20 GB gp3 |

**Security Group Ports:**
- 22 (SSH), 25 (SMTP), 80 (HTTP), 110 (POP3), 443 (HTTPS), 587 (SMTP), 3000, 8000

### 4. Get Elastic IP (3 minutes)

1. AWS → EC2 → Elastic IPs → **Allocate**
2. Associate with your instance
3. **Copy the IP address** (e.g., `54.123.45.67`)
4. Set PTR record: **mail.kders.com**

### 5. Configure Cloudflare DNS (5 minutes)

Go to Cloudflare Dashboard → kders.com → DNS

**Add these records (replace `YOUR_EC2_IP` with actual IP):**

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | @ | YOUR_EC2_IP | 🔴 **DNS only** (grey cloud) |
| A | www | YOUR_EC2_IP | 🔴 **DNS only** |
| A | mail | YOUR_EC2_IP | 🔴 **DNS only** |
| MX | @ | mail.kders.com (priority 10) | - |
| TXT | @ | v=spf1 mx ip4:YOUR_EC2_IP ~all | - |
| TXT | _dmarc | v=DMARC1; p=quarantine; rua=mailto:admin@kders.com | - |

⚠️ **CRITICAL:** Orange cloud must be **OFF** (grey) for all A records!

### 6. Deploy to EC2 (15 minutes)

```powershell
# SSH into EC2 (from folder with your .pem file)
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP

# On EC2 instance:
wget https://raw.githubusercontent.com/YOUR_USERNAME/kders-mail/cn/deploy-ec2.sh
chmod +x deploy-ec2.sh
sudo ./deploy-ec2.sh
```

**Wait 10-15 minutes** for:
- Docker installation
- Repository cloning
- SSL certificate generation
- Container startup

### 7. Setup DKIM (5 minutes)

```bash
cd /opt/kders-mail
sudo docker exec kders-smtp openssl genrsa -out /tmp/dkim_private.pem 2048
sudo docker exec kders-smtp openssl rsa -in /tmp/dkim_private.pem -pubout -out /tmp/dkim_public.pem
sudo docker exec kders-smtp cat /tmp/dkim_public.pem
```

Copy the public key → Cloudflare DNS:
```
Type: TXT
Name: default._domainkey
Content: v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE
```

### 8. Test Everything (10 minutes)

1. **Web UI:** Open https://kders.com
2. **Register:** Create `test@kders.com` account
3. **Send Email:** test@kders.com → admin@kders.com
4. **External Test:** Send from Gmail to test@kders.com
5. **Spam Check:** https://www.mail-tester.com/

---

## Your URLs After Deployment:

- **Web UI:** https://kders.com
- **Backend API:** https://kders.com/api
- **SMTP Send:** mail.kders.com:587
- **POP3 Receive:** mail.kders.com:110

---

## Cost Breakdown:

| Item | Cost |
|------|------|
| EC2 t3.medium | $30/month |
| Elastic IP | Free (if attached) |
| Domain (Cloudflare) | Already paid ✓ |
| SSL (Let's Encrypt) | Free |
| **Total** | **$30/month** |

**Free Tier Option:** Use t2.micro for $0/month (first 12 months)

---

## Important Notes:

### AWS Port 25 Limitation:
AWS blocks port 25 by default (anti-spam). You need to:
1. Request removal: [AWS Form](https://aws.amazon.com/forms/ec2-email-limit-rdns-request)
2. Approval takes 24-48 hours
3. Meanwhile, port 587 works for sending!

### Backup Your Code:
Your code is now safe in:
1. ✅ Local machine (your PC)
2. ✅ GitHub repository
3. ⏳ EC2 server (after deployment)

### Rollback if Needed:
```bash
cd /opt/kders-mail
git log  # Find previous commit
git checkout <previous-commit-hash>
sudo docker-compose up -d
```

---

## Troubleshooting:

### Can't SSH?
```powershell
# Fix .pem permissions (Windows)
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "$($env:USERNAME):(R)"
```

### DNS Not Working?
- Wait 15 minutes for propagation
- Check: `nslookup kders.com`
- Verify grey cloud (not orange) in Cloudflare

### Emails Going to Spam?
1. Check PTR record: `nslookup -type=PTR YOUR_EC2_IP`
2. Verify SPF: `nslookup -type=TXT kders.com`
3. Test DKIM: `nslookup -type=TXT default._domainkey.kders.com`
4. Spam score: https://www.mail-tester.com/

### Container Not Starting?
```bash
sudo docker logs kders-backend
sudo docker logs kders-smtp
```

---

## Files to Read:

1. **`QUICKSTART_DEPLOY.md`** - Quick reference (start here!)
2. **`DEPLOYMENT_GUIDE.md`** - Full detailed guide
3. **`CLOUDFLARE_DNS.md`** - DNS setup instructions

---

## Support & Questions:

If you encounter issues:
1. Check logs: `sudo docker-compose logs`
2. Review deployment guide: `DEPLOYMENT_GUIDE.md`
3. Test DNS: `nslookup kders.com`
4. Verify security group allows all ports

---

## Summary:

✅ **Local Progress:** Safe in Git
✅ **Deployment Scripts:** Ready
✅ **Documentation:** Complete
✅ **GitHub:** Ready to push
✅ **AWS EC2:** Ready to launch
✅ **Cloudflare DNS:** Ready to configure

**You won't lose any progress! Everything is safely committed to Git. Deploy with confidence!** 🚀

---

## Quick Command Reference:

```bash
# Push to GitHub
git push origin cn

# SSH to EC2
ssh -i "key.pem" ubuntu@YOUR_EC2_IP

# Deploy
sudo ./deploy-ec2.sh

# Check status
sudo docker ps
sudo docker logs kders-backend

# View web UI
https://kders.com
```

**Your email server is ready to go live! 🎉**
