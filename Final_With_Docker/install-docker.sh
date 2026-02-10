#!/bin/bash
# Universal Docker bootstrap script for Amazon Linux 2 & 2023

set -e

echo "[*] Detecting Amazon Linux version..."
if [ -f /etc/system-release ]; then
    RELEASE=$(cat /etc/system-release)
else
    echo "Cannot detect OS version. Exiting."
    exit 1
fi

echo "[*] OS detected: $RELEASE"

if [[ "$RELEASE" == *"Amazon Linux 2"* ]]; then
    echo "[*] Installing Docker for Amazon Linux 2..."
    sudo yum update -y
    sudo amazon-linux-extras enable docker
    sudo yum install -y docker
elif [[ "$RELEASE" == *"Amazon Linux"* ]]; then
    echo "[*] Installing Docker for Amazon Linux 2023..."
    sudo dnf update -y
    sudo dnf install -y docker
else
    echo "Unsupported OS. Exiting."
    exit 1
fi

echo "[*] Enabling Docker service at boot..."
sudo systemctl enable docker

echo "[*] Starting Docker service..."
sudo systemctl start docker

echo "[*] Adding ec2-user to docker group..."
sudo usermod -aG docker ec2-user

echo "[*] Docker installation complete!"
echo ">> Run 'newgrp docker' or re-login to use Docker without sudo."

