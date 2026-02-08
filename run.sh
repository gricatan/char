#!/bin/bash
#
# Script de lancement rapide (développement local)
#

echo "🎮 Battle Arena - Lancement Développement"
echo "=========================================="

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier venv
if [ ! -d "venv" ]; then
    echo "📦 Création environnement virtuel..."
    python3 -m venv venv
fi

# Activer venv
echo "🔄 Activation environnement virtuel..."
source venv/bin/activate

# Installer dépendances si nécessaire
if [ ! -f "venv/.deps_installed" ]; then
    echo "📥 Installation des dépendances..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    touch venv/.deps_installed
fi

echo "✅ Environnement prêt!"
echo ""
echo "🚀 Lancement du serveur..."
echo "   Accessible sur http://localhost:8000"
echo "   Ctrl+C pour arrêter"
echo ""

# Lancer serveur
python main.py
