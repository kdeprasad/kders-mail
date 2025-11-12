# Cloudflare DNS Configuration for kders.com

## Prerequisites
- Domain: `kders.com` on Cloudflare
- EC2 Instance public IP: `YOUR_EC2_IP` (get from AWS console)

---

## Step 1: Get Your EC2 Public IP

```bash
# SSH into your EC2 instance and run:
curl ifconfig.me
```

Copy this IP address - you'll need it for DNS records.

---

## Step 2: Configure Cloudflare DNS Records

Log in to [Cloudflare Dashboard](https://dash.cloudflare.com) → Select `kders.com` → DNS → Records

### Add These DNS Records:

| Type  | Name | Content | TTL | Proxy Status |
|-------|------|---------|-----|--------------|
| A     | @    | YOUR_EC2_IP | Auto | ⚠️ **DNS only** (orange cloud OFF) |
| A     | www  | YOUR_EC2_IP | Auto | ⚠️ **DNS only** |
| A     | mail | YOUR_EC2_IP | Auto | ⚠️ **DNS only** |
| MX    | @    | mail.kders.com | Auto | - |
| TXT   | @    | v=spf1 mx ip4:YOUR_EC2_IP ~all | Auto | - |
| TXT   | _dmarc | v=DMARC1; p=quarantine; rua=mailto:admin@kders.com | Auto | - |

**CRITICAL**: For mail server, the orange cloud (Cloudflare proxy) must be **OFF** (grey cloud). Email protocols require direct connection to your server.

---

## Step 3: SPF Record Details

Replace the SPF TXT record with your actual EC2 IP:

```
Type: TXT
Name: @
Content: v=spf1 mx ip4:YOUR_EC2_IP ~all
TTL: Auto
```

**Example**: If your EC2 IP is `54.123.45.67`:
```
v=spf1 mx ip4:54.123.45.67 ~all
```

---

## Step 4: MX Record Priority

When adding the MX record:
- **Priority**: `10` (lower = higher priority)
- **Mail server**: `mail.kders.com`
- Leave proxy OFF

---

## Step 5: DKIM Setup (After Deployment)

After running `deploy-ec2.sh`, SSH into your EC2 instance:

```bash
# Generate DKIM keys
cd /opt/kders-mail
sudo docker exec cp2-smtp-1 openssl genrsa -out /tmp/dkim_private.pem 2048
sudo docker exec cp2-smtp-1 openssl rsa -in /tmp/dkim_private.pem -pubout -out /tmp/dkim_public.pem

# Get public key
sudo docker exec cp2-smtp-1 cat /tmp/dkim_public.pem
```

Copy the output (everything between `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----`, removing line breaks).

### Add DKIM TXT Record in Cloudflare:

```
Type: TXT
Name: default._domainkey
Content: v=DKIM1; k=rsa; p=YOUR_PUBLIC_KEY_HERE
TTL: Auto
```

---

## Step 6: Reverse DNS (PTR Record)

**Important**: PTR records are set in AWS, not Cloudflare.

### AWS EC2 Console:
1. Go to EC2 → Elastic IPs
2. Allocate a new Elastic IP
3. Associate it with your EC2 instance
4. Select the Elastic IP → Actions → **Update reverse DNS**
5. Set reverse DNS to: `mail.kders.com`

**Why?** Many mail servers reject emails without proper PTR records (anti-spam measure).

---

## Step 7: Verify DNS Propagation

Wait 5-15 minutes after adding records, then test:

```bash
# Check A records
nslookup kders.com
nslookup mail.kders.com

# Check MX record
nslookup -type=MX kders.com

# Check SPF record
nslookup -type=TXT kders.com

# Check DKIM
nslookup -type=TXT default._domainkey.kders.com
```

Or use online tools:
- [MXToolbox](https://mxtoolbox.com/SuperTool.aspx?action=mx%3akders.com)
- [DNS Checker](https://dnschecker.org/)

---

## Step 8: Cloudflare Settings

### SSL/TLS Settings
1. Cloudflare Dashboard → SSL/TLS
2. Set SSL mode to: **Full** (not "Full (strict)" for now)
3. Later upgrade to "Full (strict)" after setting up SSL on EC2

### Email Routing (OPTIONAL)
If you want Cloudflare Email Routing as a backup:
1. Go to Email → Email Routing
2. Enable it as a fallback MX record (priority 20-30)

---

## Troubleshooting

### DNS Not Updating?
- Cloudflare DNS updates are instant, but your local DNS cache may be old
- Clear DNS cache:
  - Windows: `ipconfig /flushdns`
  - Mac/Linux: `sudo dscacheutil -flushcache` or `sudo systemd-resolve --flush-caches`

### Orange Cloud Icon Issues?
- **Must be grey (DNS only)** for: kders.com, www.kders.com, mail.kders.com
- Email servers cannot work through Cloudflare proxy
- Only use orange cloud for web-only subdomains (like `admin.kders.com` if you add one)

### MX Record Priority?
- Lower number = higher priority
- Standard: 10 for primary mail server
- If using backup: 20, 30, etc.

---

## Final Checklist

Before testing email:
- [ ] A record for @ (kders.com) pointing to EC2 IP - **grey cloud**
- [ ] A record for mail.kders.com pointing to EC2 IP - **grey cloud**
- [ ] MX record pointing to mail.kders.com (priority 10)
- [ ] SPF TXT record with your EC2 IP
- [ ] DMARC TXT record
- [ ] DKIM TXT record (after running deploy script)
- [ ] PTR record set in AWS (reverse DNS for Elastic IP)
- [ ] DNS propagation verified (nslookup shows correct IPs)
- [ ] Cloudflare SSL set to "Full" mode

---

## Quick Reference

**Your Email Addresses Format**: `username@kders.com`

**SMTP Server** (for sending): `mail.kders.com:587` (with STARTTLS)

**POP3 Server** (for receiving): `mail.kders.com:110`

**Web UI**: `http://kders.com:3000` (initially) or setup nginx for port 80/443

---

## Need Help?

If emails are being rejected:
1. Test SPF: `nslookup -type=TXT kders.com`
2. Test MX: `nslookup -type=MX kders.com`
3. Check spam score: [Mail-tester.com](https://www.mail-tester.com/)
4. Verify PTR: `nslookup -type=PTR YOUR_EC2_IP` (should return mail.kders.com)

**Common issue**: No PTR record = emails marked as spam. Always set up Elastic IP with reverse DNS in AWS.
