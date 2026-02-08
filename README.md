# Battle Arena - Multiplayer Shooting Game

Jeu de tir multijoueur avec API REST. Les joueurs se déplacent librement sur une carte 100×100, tirent des balles et s'affrontent en temps réel.

## 🎮 Caractéristiques

- **Map:** 100×100 unités avec obstacles fixes
- **Physique:** Déplacement continu (pas de cases), 60 FPS
- **Combat:** 100 HP, 10 dégâts/balle, cooldown 0.5s
- **Collisions:** Joueurs bloqués par obstacles et autres joueurs
- **Balles:** Traversent les obstacles, max 5 simultanées par joueur
- **Respawn:** 10 secondes de cooldown après mort

## 📁 Structure

```
game-server/
├── main.py              # API FastAPI
├── engine.py            # Moteur de jeu (game loop 60 FPS)
├── entities.py          # Classes Player, Bullet, Obstacle
├── physics.py           # Collisions et mouvement
├── config.py            # Configuration (vitesses, cooldowns, etc.)
├── client_example.py    # Client bot exemple
├── requirements.txt     # Dépendances Python
├── deploy.sh            # Script déploiement VPS
└── README.md            # Ce fichier
```

## 🚀 Installation Locale (Dev)

### Prérequis
- Python 3.11+
- pip

### Installation

```bash
# Cloner/télécharger les fichiers
cd game-server

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt

# Lancer le serveur
python main.py
```

Le serveur démarre sur `http://localhost:8000`

## 🌐 Déploiement VPS (Production)

### Sur VPS Debian (Hostinger)

```bash
# 1. Téléverser tous les fichiers sur le VPS
scp -r game-server/* user@your-vps:/home/user/game-server/

# 2. Se connecter au VPS
ssh user@your-vps

# 3. Lancer le script de déploiement
cd /home/user/game-server
chmod +x deploy.sh
./deploy.sh
```

Le script:
- Installe Python 3.11
- Crée un service systemd
- Configure le démarrage automatique
- Lance le serveur

### Gestion du Service

```bash
# Voir le statut
sudo systemctl status battle-arena

# Voir les logs en temps réel
sudo journalctl -u battle-arena -f

# Redémarrer
sudo systemctl restart battle-arena

# Arrêter
sudo systemctl stop battle-arena

# Démarrer
sudo systemctl start battle-arena
```

## 📡 API Endpoints

### POST /api/join
Rejoindre la partie

**Request:**
```json
{
  "username": "alice"
}
```

**Response:**
```json
{
  "success": true,
  "player_id": "alice_a1b2c3d4",
  "position": [45.3, 52.1],
  "health": 100
}
```

### POST /api/move
Déplacer son joueur

**Request:**
```json
{
  "player_id": "alice_a1b2c3d4",
  "direction_x": 1.0,
  "direction_y": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "position": [46.1, 52.6]
}
```

### POST /api/shoot
Tirer une balle

**Request:**
```json
{
  "player_id": "alice_a1b2c3d4",
  "direction_x": 0.0,
  "direction_y": -1.0
}
```

**Response:**
```json
{
  "success": true,
  "bullet_id": "bullet_xyz123"
}
```

### GET /api/state
Récupérer l'état complet du jeu

**Response:**
```json
{
  "players": [
    {
      "id": "alice_a1b2c3d4",
      "username": "alice",
      "x": 45.3,
      "y": 67.8,
      "health": 80,
      "kills": 3
    }
  ],
  "bullets": [
    {
      "id": "bullet_xyz",
      "owner_id": "alice_a1b2c3d4",
      "x": 23.1,
      "y": 45.6,
      "vx": 10,
      "vy": 5
    }
  ],
  "obstacles": [
    {
      "id": 0,
      "x": 10,
      "y": 10,
      "width": 3,
      "height": 3
    }
  ],
  "map": {
    "width": 100,
    "height": 100
  }
}
```

### GET /api/stats
Statistiques du jeu

**Response:**
```json
{
  "server": {
    "uptime_seconds": 3600,
    "tick_rate": 60
  },
  "game": {
    "players_online": 12,
    "bullets_active": 34,
    "obstacles_count": 25,
    "total_kills_all_time": 287,
    "total_deaths_all_time": 287,
    "total_shots_all_time": 1543
  },
  "top_players_current": [
    {
      "username": "alice",
      "kills": 15,
      "health": 70
    }
  ]
}
```

## 🤖 Client Exemple

### Lancer un bot

```bash
# Bot avec IA simple
python client_example.py MonBot simple

# Bot agressif (fonce sur les ennemis)
python client_example.py Rambo aggressive

# Bot défensif (garde ses distances)
python client_example.py Sniper defensive
```

### Créer son propre client

```python
import requests

# Rejoindre
response = requests.post("http://localhost:8000/api/join", 
                         json={"username": "MyBot"})
player_id = response.json()['player_id']

# Boucle de jeu
while True:
    # Récupérer état
    state = requests.get("http://localhost:8000/api/state").json()
    
    # Décider action...
    
    # Bouger
    requests.post("http://localhost:8000/api/move", json={
        "player_id": player_id,
        "direction_x": 1.0,
        "direction_y": 0.0
    })
    
    # Tirer
    requests.post("http://localhost:8000/api/shoot", json={
        "player_id": player_id,
        "direction_x": 0.0,
        "direction_y": -1.0
    })
    
    time.sleep(0.2)
```

## ⚙️ Configuration

Modifier `config.py` pour changer:

```python
# Vitesses
PLAYER_SPEED = 5.0       # unités/seconde
BULLET_SPEED = 15.0      # unités/seconde

# Combat
PLAYER_MAX_HEALTH = 100
BULLET_DAMAGE = 10
BULLET_COOLDOWN = 0.5    # secondes

# Limites
MAX_PLAYERS = 100
MAX_BULLETS_PER_PLAYER = 5

# Map
MAP_WIDTH = 100.0
MAP_HEIGHT = 100.0
OBSTACLE_COUNT = 20
```

## 🎯 Stratégies de Jeu

### IA Simple (Équilibrée)
- Maintient distance ~15-20 unités
- Strafe autour de l'ennemi
- Tire en continu

### IA Agressive
- Fonce directement sur l'ennemi
- Combat rapproché
- Haut risque, haute récompense

### IA Défensive (Sniper)
- Maintient distance ~30 unités
- Fuit si trop proche
- Tirs précis à longue distance

## 📊 Stats Persistantes

Les statistiques sont sauvegardées dans `game_stats.json`:
- Total kills all-time
- Total deaths all-time
- Total shots all-time

Survit aux redémarrages du serveur.

## 🔧 Développement

### Tester localement

```bash
# Terminal 1: Serveur
python main.py

# Terminal 2: Client bot 1
python client_example.py Alice simple

# Terminal 3: Client bot 2
python client_example.py Bob aggressive

# Terminal 4: Observer l'état
watch -n 1 'curl -s http://localhost:8000/api/stats | jq'
```

### Debug

```bash
# Logs du serveur (si systemd)
sudo journalctl -u battle-arena -f

# Ou logs stdout si lancé manuellement
python main.py
```

## 🐛 Troubleshooting

### Port déjà utilisé
```bash
# Changer le port dans config.py
SERVER_PORT = 8001
```

### Serveur inaccessible
```bash
# Vérifier firewall
sudo ufw allow 8000/tcp

# Vérifier que le serveur écoute
netstat -tulpn | grep 8000
```

### Client ne peut pas se connecter
```bash
# Vérifier que l'API répond
curl http://localhost:8000/

# Vérifier IP du serveur
hostname -I
```

## 📝 TODO / Améliorations Futures

- [ ] Authentification (tokens)
- [ ] Teams (rouge vs bleu)
- [ ] Power-ups (santé, vitesse, dégâts)
- [ ] Dashboard web pour observer
- [ ] Replay système
- [ ] Statistiques par joueur détaillées
- [ ] Matchmaking
- [ ] Modes de jeu (capture du drapeau, etc.)

## 📄 Licence

Libre d'utilisation pour votre serveur Discord.

## 🤝 Contribution

Pull requests bienvenues!

---

**Bon jeu! 🎮🔫**
