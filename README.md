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

### Créer son propre client

```python
import requests

# Rejoindre
response = requests.post("https://devhubcommunity.duckdns.org/api/api/join", 
                         json={"username": "MyBot"})
player_id = response.json()['player_id']

# Boucle de jeu
while True:
    # Récupérer état
    state = requests.get("https://devhubcommunity.duckdns.org/api/api/state").json()
    
    # Décider action...
    
    # Bouger
    requests.post("https://devhubcommunity.duckdns.org/api/api/move", json={
        "player_id": player_id,
        "direction_x": 1.0,
        "direction_y": 0.0
    })
    
    # Tirer
    requests.post("hhttps://devhubcommunity.duckdns.org/api/api/shoot", json={
        "player_id": player_id,
        "direction_x": 0.0,
        "direction_y": -1.0
    })
    
    time.sleep(0.2)
```


## 📄 Licence

Libre d'utilisation pour notre serveur Discord DevHub

## 🤝 Contribution

Pull requests bienvenues!

---

**Bon jeu! 🎮🔫**
