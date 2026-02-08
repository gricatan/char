#!/bin/bash
#
# Script de déploiement pour VPS Debian (Hostinger)
# Usage: ./deploy.sh
#

set -e

echo "🚀 Déploiement Battle Arena Game Server"
echo "========================================"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
APP_DIR="/opt/battle-arena"
SERVICE_NAME="battle-arena"
PYTHON_VERSION="3.11"

echo -e "${YELLOW}📦 Installation des dépendances système...${NC}"
sudo apt-get update
sudo apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip

echo -e "${YELLOW}📁 Création du répertoire application...${NC}"
sudo mkdir -p ${APP_DIR}
sudo chown $(whoami):$(whoami) ${APP_DIR}

echo -e "${YELLOW}📋 Copie des fichiers...${NC}"
cp -r ./* ${APP_DIR}/

echo -e "${YELLOW}🐍 Création environnement virtuel Python...${NC}"
cd ${APP_DIR}
python${PYTHON_VERSION} -m venv venv

echo -e "${YELLOW}📦 Installation des packages Python...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}⚙️ Création du service systemd...${NC}"
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Battle Arena Game Server
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/main.py
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=battle-arena

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}🔄 Rechargement systemd...${NC}"
sudo systemctl daemon-reload

echo -e "${YELLOW}✅ Activation du service...${NC}"
sudo systemctl enable ${SERVICE_NAME}

echo -e "${YELLOW}▶️ Démarrage du service...${NC}"
sudo systemctl start ${SERVICE_NAME}

echo ""
echo -e "${GREEN}✅ Déploiement terminé!${NC}"
echo ""
echo "📊 Commandes utiles:"
echo "  • Statut:     sudo systemctl status ${SERVICE_NAME}"
echo "  • Logs:       sudo journalctl -u ${SERVICE_NAME} -f"
echo "  • Restart:    sudo systemctl restart ${SERVICE_NAME}"
echo "  • Stop:       sudo systemctl stop ${SERVICE_NAME}"
echo ""
echo "🌐 Le serveur devrait être accessible sur:"
echo "   http://$(hostname -I | awk '{print $1}'):8000"
echo ""

# Afficher le statut
sleep 2
sudo systemctl status ${SERVICE_NAME} --no-pager
