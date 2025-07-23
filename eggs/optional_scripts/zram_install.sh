#!/bin/bash
set -e

echo "=== ZRAM Setup Script for Arch Linux ==="

# Prompt for zram size
read -rp "Enter zram size (e.g., 'ram * 0.5', '4GiB', '1024MiB') [default: ram * 0.5]: " ZRAM_SIZE
ZRAM_SIZE=${ZRAM_SIZE:-"ram * 0.5"}

# Prompt for compression algorithm
read -rp "Enter compression algorithm (e.g., zstd, lz4, lzo) [default: zstd]: " ZRAM_ALGO
ZRAM_ALGO=${ZRAM_ALGO:-"zstd"}

echo -e "\n==> Configuring zram with:"
echo "    Size:      $ZRAM_SIZE"
echo "    Algorithm: $ZRAM_ALGO"

# Install zram-generator
echo "==> Installing zram-generator..."
sudo pacman -Sy --noconfirm zram-generator

# Create config
echo "==> Writing config to /etc/systemd/zram-generator.conf.d/zram.conf..."
sudo mkdir -p /etc/systemd/zram-generator.conf.d

sudo tee /etc/systemd/zram-generator.conf.d/zram.conf > /dev/null << EOF
[zram0]
zram-size = $ZRAM_SIZE
compression-algorithm = $ZRAM_ALGO
EOF

# Link systemd service
echo "==> Linking zram setup service to boot target..."
sudo ln -sf /usr/lib/systemd/system/systemd-zram-setup@.service \
  /etc/systemd/system/sysinit.target.wants/systemd-zram-setup@zram0.service

# Start immediately
echo "==> Reloading systemd and starting zram..."
sudo systemctl daemon-reexec
sudo systemctl start systemd-zram-setup@zram0.service

# Show result
echo -e "\n==> zram setup complete. Current swap status:"
swapon --show

