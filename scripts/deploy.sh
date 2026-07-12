#!/bin/bash
# Deploy the legislation website to Raspberry Pi
# Usage: ./deploy.sh
#
# Requires:
#   - SSH access configured to pi (add key to ~/.ssh/)
#   - Caddy running on Pi at port 8083
#   - HTML file generated and ready at ./index.html

set -e

PI_HOST="192.168.x.x"     # Replace with your Pi's IP
PI_USER="pi"              # Replace with your Pi username
PI_PATH="/home/$PI_USER/legislation-site"
SSH_KEY="~/.ssh/id_rsa_pi"

echo "→ Deploying legislation site to Pi..."

# Copy the HTML
scp -i "$SSH_KEY" ./index.html "$PI_USER@$PI_HOST:$PI_PATH/index.html"

# Copy state file for change detection history
scp -i "$SSH_KEY" ./state.json "$PI_USER@$PI_HOST:$PI_PATH/state.json" 2>/dev/null || true

echo "✓ Deployed to http://$PI_HOST:8083"