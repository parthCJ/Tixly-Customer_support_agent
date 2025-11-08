# Oracle Cloud Deployment Guide for Tixly Customer Support Copilot

## 🎯 What You'll Get

- **24GB RAM** + **4 CPU cores** (ARM) - **FOREVER FREE**
- No cold starts, no sleep mode
- Full control over your infrastructure
- Professional deployment with Docker + Nginx

## 📋 Prerequisites

- Oracle Cloud account (free)
- Credit/debit card for verification (won't be charged)
- Your GROQ API key

---

## Part 1: Oracle Cloud Account Setup (10 minutes)

### Step 1: Create Oracle Cloud Account

1. Go to: https://www.oracle.com/cloud/free/
2. Click **"Start for free"**
3. Fill in details:
   - Email address
   - Country
   - Cloud account name (choose something unique)
4. Verify email
5. Add payment method (for verification only - won't be charged for Always Free resources)
6. Complete verification (may take a few minutes)

### Step 2: Create Virtual Cloud Network (VCN)

1. Login to Oracle Cloud Console
2. Navigate to: **Menu** → **Networking** → **Virtual Cloud Networks**
3. Click **"Start VCN Wizard"**
4. Select **"Create VCN with Internet Connectivity"**
5. Click **"Start VCN Wizard"**
6. Enter name: `tixly-vcn`
7. Keep default settings
8. Click **"Next"** → **"Create"**
9. Wait for creation (1-2 minutes)

### Step 3: Configure Security List (Firewall Rules)

1. In your VCN, click **"Security Lists"**
2. Click on **"Default Security List for tixly-vcn"**
3. Click **"Add Ingress Rules"**
4. Add these rules one by one:

**Rule 1 - HTTP:**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `80`
- Description: `HTTP`

**Rule 2 - HTTPS:**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `443`
- Description: `HTTPS`

**Rule 3 - Backend API (temporary for testing):**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `8000`
- Description: `Backend API`

**Rule 4 - Frontend (temporary for testing):**
- Source CIDR: `0.0.0.0/0`
- IP Protocol: `TCP`
- Destination Port Range: `3000`
- Description: `Frontend`

---

## Part 2: Create ARM VM Instance (5 minutes)

### Step 1: Launch Instance

1. Navigate to: **Menu** → **Compute** → **Instances**
2. Click **"Create Instance"**

### Step 2: Configure Instance

**Name:** `tixly-server`

**Placement:**
- Keep default (usually first availability domain)

**Image and shape:**
1. Click **"Change Image"**
   - Select: **Canonical Ubuntu 22.04** (recommended)
   - Click **"Select Image"**

2. Click **"Change Shape"**
   - Select: **Ampere (ARM-based processor)**
   - Select: **VM.Standard.A1.Flex**
   - Set OCPUs: `4` (all free tier)
   - Set Memory: `24 GB` (all free tier)
   - Click **"Select Shape"**

**Networking:**
- Select your VCN: `tixly-vcn`
- Select public subnet
- Check: **"Assign a public IPv4 address"**

**Add SSH keys:**
- Select: **"Generate a key pair for me"**
- Click **"Save Private Key"** (save this file - you'll need it!)
- Click **"Save Public Key"** (optional)

**Boot volume:**
- Keep default (50GB is enough, max free is 200GB total)

### Step 3: Create Instance

1. Click **"Create"**
2. Wait 2-3 minutes for provisioning
3. **Copy your Public IP address** once instance is running

---

## Part 3: Connect to Your VM (2 minutes)

### Windows (using PowerShell):

```powershell
# Set permissions on private key
icacls "path\to\ssh-key.key" /inheritance:r
icacls "path\to\ssh-key.key" /grant:r "%username%:R"

# Connect
ssh -i "path\to\ssh-key.key" ubuntu@YOUR_PUBLIC_IP
```

### Mac/Linux:

```bash
# Set permissions
chmod 400 ~/path/to/ssh-key.key

# Connect
ssh -i ~/path/to/ssh-key.key ubuntu@YOUR_PUBLIC_IP
```

---

## Part 4: Deploy Application (5 minutes)

### Once connected to your VM:

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/parthCJ/Tixly-Customer_support_agent/baseline-localhost-2025-11-08/oracle-setup.sh | bash

# Wait for script to complete (3-5 minutes)

# After script finishes, add your GROQ API key
nano .env
# Replace 'your_groq_api_key_here' with your actual key
# Press Ctrl+X, then Y, then Enter to save

# Start the application
docker-compose up -d

# Check if containers are running
docker-compose ps

# View logs (optional)
docker-compose logs -f backend
```

---

## Part 5: Access Your Application

### Your application will be available at:

- **Frontend:** `http://YOUR_PUBLIC_IP:3000`
- **Backend API:** `http://YOUR_PUBLIC_IP:8000`
- **API Docs:** `http://YOUR_PUBLIC_IP:8000/docs`
- **Health Check:** `http://YOUR_PUBLIC_IP:8000/health`

### With Nginx (production):

- **Application:** `http://YOUR_PUBLIC_IP`
- **API:** `http://YOUR_PUBLIC_IP/api/`

---

## 🔧 Common Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild after code changes
git pull
docker-compose up -d --build

# Check disk space
df -h

# Check memory usage
free -h

# Check running containers
docker ps
```

---

## 🛡️ Security Recommendations

### 1. Change Default Ports (Production)

Edit `docker-compose.yml` to use nginx on port 80 only, remove direct access to 8000 and 3000.

### 2. Set Up SSL Certificate (Free with Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com
```

### 3. Configure Firewall

```bash
# Once nginx is working, close direct access to backend/frontend
sudo iptables -D INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -D INPUT -p tcp --dport 3000 -j ACCEPT
sudo netfilter-persistent save
```

---

## 🚨 Troubleshooting

### Issue: Can't connect to VM

**Solution:**
- Check security list has port 22 (SSH) open
- Verify you're using correct private key
- Check instance is in "Running" state

### Issue: Containers won't start

**Solution:**
```bash
# Check logs
docker-compose logs

# Check if ports are in use
sudo netstat -tulpn | grep -E ':(80|443|3000|8000)'

# Restart Docker
sudo systemctl restart docker
docker-compose up -d
```

### Issue: Out of memory

**Solution:**
```bash
# Check memory
free -h

# Check which container is using memory
docker stats

# Reduce workers (edit Dockerfile or docker-compose)
```

### Issue: Oracle threatening to delete VM

**Solution:**
- The keep-alive cron job should prevent this
- Verify it's running: `crontab -l`
- Manually trigger: `~/keep-alive.sh`

---

## 📊 Monitoring

### Check application health:

```bash
# Backend health
curl http://localhost:8000/health

# Check if services_ready
curl http://localhost:8000/health | jq '.services_ready'
```

### Resource monitoring:

```bash
# Install htop
sudo apt-get install htop

# Monitor in real-time
htop
```

---

## 🔄 Updates and Maintenance

### Update application code:

```bash
cd ~/Tixly-Customer_support_agent
git pull
docker-compose down
docker-compose up -d --build
```

### Update system:

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo reboot  # if kernel updated
```

---

## 💰 Cost Verification

Always Free resources used:
- ✅ VM.Standard.A1.Flex: 4 OCPUs, 24GB RAM
- ✅ Block Storage: <200GB
- ✅ Network egress: <10TB/month

**Your bill should show $0.00 for these resources.**

Check your billing: **Menu** → **Billing & Cost Management** → **Cost Analysis**

---

## 🎓 Next Steps

1. **Add a domain name:**
   - Point your domain to Oracle IP
   - Configure SSL with Let's Encrypt
   - Update nginx.conf with your domain

2. **Set up monitoring:**
   - Install Prometheus + Grafana
   - Set up alerts for downtime

3. **Add CI/CD:**
   - GitHub Actions to auto-deploy on push
   - Automated testing before deployment

4. **Optimize performance:**
   - Add Redis for caching
   - Set up PostgreSQL for persistent data
   - Configure CDN for static assets

---

## 📞 Support

If you encounter issues:

1. Check logs: `docker-compose logs -f`
2. Verify firewall rules in Oracle Console
3. Check Docker status: `sudo systemctl status docker`
4. Review this guide's troubleshooting section

---

**Congratulations! You now have a production-grade deployment on Oracle Cloud's Always Free tier! 🎉**
