#!/usr/bin/env bash
# Sets up Gemma on a fresh Ubuntu GPU server (DigitalOcean GPU Droplet, AI/ML-ready image).
# Run it once as root:   bash gpu-droplet-setup.sh [model]        (default model: gemma3)
#
# What it does:
#   1. Installs Ollama and keeps it listening on localhost only (it has no login of its own).
#   2. Pulls the model and keeps it loaded in the GPU.
#   3. Puts Caddy in front: HTTPS (free certificate for <ip>.sslip.io) and a random key.
#   4. Opens only SSH, 80 and 443 in the firewall.
# At the end it prints OLLAMA_URL and OLLAMA_API_KEY: set both in Render.
set -euo pipefail

MODEL="${1:-gemma3}"

if [ "$(id -u)" -ne 0 ]; then echo "Run as root." >&2; exit 1; fi

apt-get update -y
apt-get install -y curl gpg openssl ufw debian-keyring debian-archive-keyring apt-transport-https

# --- Ollama -------------------------------------------------------------------
curl -fsSL https://ollama.com/install.sh | sh
mkdir -p /etc/systemd/system/ollama.service.d
cat > /etc/systemd/system/ollama.service.d/override.conf <<'CONF'
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_KEEP_ALIVE=24h"
CONF
systemctl daemon-reload
systemctl enable --now ollama
systemctl restart ollama
sleep 3
ollama pull "$MODEL"

# --- Public address and key ---------------------------------------------------
IP="$(curl -fsS http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address || curl -fsS https://ifconfig.me)"
HOST="${IP//./-}.sslip.io"
KEY="$(openssl rand -hex 24)"
umask 077
printf '%s\n' "$KEY" > /root/ollama-api-key

# --- Caddy: HTTPS + key -------------------------------------------------------
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
apt-get update -y
apt-get install -y caddy

cat > /etc/caddy/Caddyfile <<CADDY
${HOST} {
	@nokey not header Authorization "Bearer ${KEY}"
	respond @nokey "Unauthorized" 401
	reverse_proxy 127.0.0.1:11434 {
		flush_interval -1
	}
}
CADDY
chown root:caddy /etc/caddy/Caddyfile
chmod 640 /etc/caddy/Caddyfile
systemctl enable caddy
systemctl restart caddy

# --- Firewall -----------------------------------------------------------------
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# --- Warm the model so the first real request is fast -------------------------
curl -fsS http://127.0.0.1:11434/api/generate -d "{\"model\":\"${MODEL}\",\"prompt\":\"hola\",\"stream\":false,\"options\":{\"num_predict\":1}}" > /dev/null || true

cat <<DONE

Ready. Set these two variables in Render (Environment tab):

  OLLAMA_URL=https://${HOST}
  OLLAMA_API_KEY=${KEY}
  OLLAMA_MODEL=${MODEL}

Check it from anywhere (should print the model list; without the key it answers 401):
  curl -s -H "Authorization: Bearer ${KEY}" https://${HOST}/api/tags

The key is also saved in /root/ollama-api-key. Remember: the Droplet bills while it exists. Destroy it when the demo is over.
DONE
