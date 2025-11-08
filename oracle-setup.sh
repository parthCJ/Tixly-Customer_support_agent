#!/bin/bash

# Oracle Cloud ARM VM Setup Script for Tixly Customer Support Copilot
# Run this on a fresh Oracle Cloud ARM instance (Ubuntu 22.04 recommended)

set -e  # Exit on any error

echo "=================================="
echo "Tixly Setup Script for Oracle Cloud"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🐙 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📚 Installing Git..."
sudo apt-get install -y git

# Clone repository
echo "📥 Cloning repository..."
cd ~
if [ -d "Tixly-Customer_support_agent" ]; then
    echo "Repository already exists, pulling latest..."
    cd Tixly-Customer_support_agent
    git pull
else
    git clone https://github.com/parthCJ/Tixly-Customer_support_agent.git
    cd Tixly-Customer_support_agent
fi

# Switch to baseline branch
git checkout baseline-localhost-2025-11-08

# Create .env file
echo "⚙️  Creating environment file..."
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
ALLOWED_ORIGINS=http://$(curl -s ifconfig.me),http://localhost:3000
FRONTEND_URL=http://$(curl -s ifconfig.me):3000
NEXT_PUBLIC_API_URL=http://$(curl -s ifconfig.me):8000
EOF

echo ""
echo "⚠️  IMPORTANT: Edit .env file and add your GROQ_API_KEY"
echo "Run: nano .env"
echo ""

# Configure firewall (Oracle Cloud uses iptables)
echo "🔒 Configuring firewall..."
sudo iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 3000 -j ACCEPT

# Save iptables rules
sudo netfilter-persistent save || echo "netfilter-persistent not installed, rules not persisted"

# Setup keep-alive cron job (prevents Oracle from deleting idle VMs)
echo "⏰ Setting up keep-alive cron job..."
cat > ~/keep-alive.sh << 'KEEPALIVE'
#!/bin/bash
curl -s http://localhost:8000/health > /dev/null
KEEPALIVE

chmod +x ~/keep-alive.sh

# Add to crontab (runs every hour)
(crontab -l 2>/dev/null; echo "0 * * * * ~/keep-alive.sh") | crontab -

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your GROQ_API_KEY"
echo "3. Run: docker-compose up -d"
echo "4. Access your app at: http://$(curl -s ifconfig.me)"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop app: docker-compose down"
echo "  - Restart app: docker-compose restart"
echo ""
