#!/bin/bash
# EC2 Setup Script for Farm2Fork Backend
# Run these commands on your EC2 instance

echo "=========================================="
echo "Farm2Fork Backend - EC2 Setup"
echo "=========================================="
echo ""

# Step 1: Update system
echo "Step 1: Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Step 2: Install Python 3.11
echo ""
echo "Step 2: Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip

# Step 3: Install system dependencies
echo ""
echo "Step 3: Installing system dependencies..."
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
sudo apt install -y pkg-config default-libmysqlclient-dev

# Step 4: Install Nginx
echo ""
echo "Step 4: Installing Nginx..."
sudo apt install -y nginx

# Step 5: Create application directory
echo ""
echo "Step 5: Creating application directory..."
sudo mkdir -p /var/www/farm2fork
sudo chown -R ubuntu:ubuntu /var/www/farm2fork

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Upload your backend code"
echo "2. Setup Python environment"
echo "3. Configure environment variables"
echo ""
