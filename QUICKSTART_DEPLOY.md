# Quick Start: Deploy kders.com to EC2

## Pre-Deployment Checklist (Do This First!)

### 1. Push Your Code to GitHub
```powershell
cd "C:\Users\pkosh\OneDrive\Documents\Vit-sem5\CN\cp2"

# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: kders.com email server"

# Add remote (create repo on GitHub first!)
git remote add origin https://github.com/YOUR_USERNAME/kders-mail.git
git push -u origin main
```

### 2. Update deploy-ec2.sh
Edit `deploy-ec2.sh` line 15:
```bash
GITHUB_REPO="https://github.com/YOUR_USERNAME/kders-mail.git"
```

---

## AWS EC2 Setup (15 minutes)

### Launch Instance
- **AMI**: Ubuntu 22.04 LTS
- **Type**: t3.medium (or t2.micro for free tier)
- **Storage**: 20 GB
- **Security Group**: Allow ports 22, 25, 80, 110, 443, 587, 3000, 8000

### Get Elastic IP
1. Allocate Elastic IP
2. Associate with instance
3. Copy IP: `___.___.___.___ ` ← Write it here!
4. Set PTR record: `mail.kders.com`

---

## Cloudflare DNS (5 minutes)

**Replace `YOUR_EC2_IP` with actual IP!**

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | @ | YOUR_EC2_IP | OFF ⚫ |
| A | www | YOUR_EC2_IP | OFF ⚫ |
| A | mail | YOUR_EC2_IP | OFF ⚫ |
| MX | @ | mail.kders.com | - |
| TXT | @ | v=spf1 mx ip4:YOUR_EC2_IP ~all | - |
| TXT | _dmarc | v=DMARC1; p=quarantine; rua=mailto:admin@kders.com | - |

⚠️ **Orange cloud must be OFF (grey) for email to work!**

---

## Deploy to EC2 (10 minutes)

### SSH into EC2
```powershell
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

### Download & Run Deploy Script
```bash
# Download script from your GitHub repo
wget https://raw.githubusercontent.com/YOUR_USERNAME/kders-mail/main/deploy-ec2.sh

# Make executable
chmod +x deploy-ec2.sh

# Run deployment
sudo ./deploy-ec2.sh
```

**Wait 10-15 minutes for installation...**

---

## Post-Deployment (5 minutes)

### 1. Check Services
```bash
sudo docker ps
```
Should see: db, backend, frontend, smtp, pop3, nginx

### 2. Setup DKIM
```bash
cd /opt/kders-mail
sudo docker exec kders-smtp openssl genrsa -out /tmp/dkim_private.pem 2048
sudo docker exec kders-smtp openssl rsa -in /tmp/dkim_private.pem -pubout -out /tmp/dkim_public.pem
sudo docker exec kders-smtp cat /tmp/dkim_public.pem
```

Copy public key → Cloudflare DNS:
```
Type: TXT
Name: default._domainkey
Content: v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY
```

### 3. Test Web UI
Open browser: `https://kders.com`

You should see your WhatsApp-style email app! 🎉

---

## Testing Email

### Send Test Email
```bash
telnet mail.kders.com 587
```

### Check Spam Score
1. Go to [mail-tester.com](https://www.mail-tester.com/)
2. Send email to the address they provide
3. Aim for 8/10 or higher

---

## Troubleshooting

### Can't SSH?
```powershell
# Fix .pem permissions
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "$($env:USERNAME):(R)"
```

### DNS not working?
- Wait 15 minutes
- Check grey cloud is ON (not orange)
- Run: `nslookup kders.com`

### Emails to spam?
1. Check PTR: `nslookup -type=PTR YOUR_EC2_IP`
2. Verify SPF/DKIM in Cloudflare
3. Request AWS port 25 unlock: [AWS Form](https://aws.amazon.com/forms/ec2-email-limit-rdns-request)

### Container not starting?
```bash
sudo docker logs kders-backend
sudo docker logs kders-frontend
```

---

## Your Email Server URLs

- **Web UI**: https://kders.com
- **API**: https://kders.com/api
- **SMTP** (send): mail.kders.com:587
- **POP3** (receive): mail.kders.com:110

---

## Cost: ~$30/month

- EC2 t3.medium: $30/month
- Elastic IP: Free (if attached)
- SSL: Free (Let's Encrypt)
- Domain: Already paid ✓

**Free tier option**: Use t2.micro for $0/month (first 12 months)

---

## Need Help?

Read full guide: `DEPLOYMENT_GUIDE.md`

**Your local code is safe! It's on your machine + GitHub. Deploy with confidence!** 🚀
