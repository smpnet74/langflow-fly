#!/bin/bash

# Add fly path configuration to .bashrc if not already present
if ! grep -q "FLYCTL_INSTALL" ~/.bashrc; then
    echo '# Fly CLI configuration' >> ~/.bashrc
    echo 'export FLYCTL_INSTALL="/home/$USER/.fly"' >> ~/.bashrc
    echo 'export PATH="$FLYCTL_INSTALL/bin:$PATH"' >> ~/.bashrc
fi

# Reload .bashrc for current session
source ~/.bashrc

# Verify fly is accessible
if command -v fly &> /dev/null; then
    echo "✅ Fly CLI is now permanently configured in your PATH"
    echo "Current fly version: $(fly version)"
    echo "You can now use 'fly' commands in any new terminal session"
else
    echo "❌ Failed to configure Fly CLI"
    exit 1
fi
