"""
Configuration du jeu - Toutes les constantes
"""

# Map
MAP_WIDTH = 100.0
MAP_HEIGHT = 100.0

# Obstacles
OBSTACLE_COUNT = 20
OBSTACLE_MIN_SIZE = 2.0
OBSTACLE_MAX_SIZE = 5.0
SPAWN_SAFE_ZONE = (40, 60, 40, 60)  # x_min, x_max, y_min, y_max

# Joueurs
PLAYER_RADIUS = 0.5
PLAYER_SPEED = 5.0  # unités/seconde
PLAYER_MAX_HEALTH = 100
PLAYER_SPAWN_MIN_DISTANCE = 5.0  # distance min entre joueurs au spawn

# Balles
BULLET_RADIUS = 0.2
BULLET_SPEED = 15.0  # unités/seconde
BULLET_DAMAGE = 10
BULLET_COOLDOWN = 0.5  # secondes
MAX_BULLETS_PER_PLAYER = 5

# Respawn
DEATH_COOLDOWN = 10.0  # secondes

# Rate Limiting
MOVE_RATE_LIMIT = 0.05  # 50ms minimum entre moves (20/sec)
SHOOT_RATE_LIMIT = 0.5  # 500ms minimum entre tirs (2/sec)
INACTIVITY_TIMEOUT = 120.0  # secondes (2 minutes)

# Game Engine
TICK_RATE = 60  # FPS
TICK_DURATION = 1.0 / TICK_RATE

# Serveur
SERVER_PORT = 8000
MAX_PLAYERS = 100  # limite joueurs simultanés

# Username
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20
USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'

# Stats persistence
STATS_FILE = "game_stats.json"
