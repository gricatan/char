# 🚀 Quick Start Guide

## Installation Locale (5 minutes)

### 1. Installer le serveur

```bash
# Installer les dépendances
./run.sh
```

Le serveur démarre automatiquement sur `http://localhost:8000`

### 2. Tester

Dans un autre terminal:

```bash
# Lancer les tests
python test_server.py
```

### 3. Lancer des bots

```bash
# Terminal 1: Bot simple
python client_example.py Alice simple

# Terminal 2: Bot agressif
python client_example.py Bob aggressive

# Terminal 3: Bot défensif
python client_example.py Charlie defensive
```

### 4. Observer

```bash
# Voir l'état en temps réel
watch -n 1 'curl -s http://localhost:8000/api/stats | python -m json.tool'
```

---

## Déploiement VPS (10 minutes)

### 1. Téléverser sur le VPS

```bash
# Depuis ta machine locale
scp -r game-server/* user@your-vps-ip:/home/user/game-server/
```

### 2. Déployer

```bash
# Sur le VPS
ssh user@your-vps-ip
cd /home/user/game-server
./deploy.sh
```

### 3. Vérifier

```bash
# Status
sudo systemctl status battle-arena

# Logs
sudo journalctl -u battle-arena -f
```

### 4. Tester

```bash
# Depuis ta machine locale
python test_server.py http://your-vps-ip:8000
```

---

## Créer Ton Premier Bot

```python
# my_bot.py
import requests
import time

API = "http://localhost:8000"

# Rejoindre
resp = requests.post(f"{API}/api/join", json={"username": "MyBot"})
player_id = resp.json()['player_id']

# Boucle
while True:
    # Bouger à droite
    requests.post(f"{API}/api/move", json={
        "player_id": player_id,
        "direction_x": 1.0,
        "direction_y": 0.0
    })
    
    # Tirer vers le haut
    requests.post(f"{API}/api/shoot", json={
        "player_id": player_id,
        "direction_x": 0.0,
        "direction_y": -1.0
    })
    
    time.sleep(0.2)
```

---

## Configuration Rapide

Éditer `config.py`:

```python
# Rendre le jeu plus rapide
PLAYER_SPEED = 10.0
BULLET_SPEED = 30.0

# Rendre le jeu plus difficile
PLAYER_MAX_HEALTH = 50
BULLET_DAMAGE = 20

# Plus d'obstacles
OBSTACLE_COUNT = 50
```

---

## Commandes Utiles

```bash
# Développement local
./run.sh                    # Démarrer serveur
python test_server.py       # Tests
python client_example.py    # Bot

# Production (VPS)
sudo systemctl restart battle-arena    # Redémarrer
sudo journalctl -u battle-arena -f     # Logs
sudo systemctl stop battle-arena       # Arrêter
```

---

## URLs API

- Root: `GET /`
- Join: `POST /api/join`
- Move: `POST /api/move`
- Shoot: `POST /api/shoot`
- State: `GET /api/state`
- Stats: `GET /api/stats`

Voir `README.md` pour détails complets.

---

**Bon jeu! 🎮**
