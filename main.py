"""
API FastAPI - Point d'entrée pour les clients
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Optional
import re
import time
from collections import defaultdict
import config
from engine import GameEngine


# Modèles de requêtes
class JoinRequest(BaseModel):
    username: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < config.USERNAME_MIN_LENGTH:
            raise ValueError(f'Username too short (min {config.USERNAME_MIN_LENGTH})')
        if len(v) > config.USERNAME_MAX_LENGTH:
            raise ValueError(f'Username too long (max {config.USERNAME_MAX_LENGTH})')
        if not re.match(config.USERNAME_PATTERN, v):
            raise ValueError('Username must be alphanumeric + underscore only')
        return v


class MoveRequest(BaseModel):
    player_id: str
    direction_x: float
    direction_y: float


class ShootRequest(BaseModel):
    player_id: str
    direction_x: float
    direction_y: float


# Initialiser FastAPI
app = FastAPI(
    title="Battle Arena API",
    description="Multiplayer shooting game API",
    version="1.0.0"
)

# CORS - Autoriser tous les origins pour le dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser Game Engine
game = GameEngine()

# Rate limiting par IP (simple)
rate_limit_store = defaultdict(list)  # {ip: [timestamps]}
GLOBAL_RATE_LIMIT = 100  # requêtes/seconde
RATE_LIMIT_WINDOW = 1.0  # secondes


def check_rate_limit(ip: str) -> bool:
    """Vérifier rate limit global par IP"""
    current_time = time.time()
    
    # Nettoyer vieux timestamps
    rate_limit_store[ip] = [
        t for t in rate_limit_store[ip]
        if current_time - t < RATE_LIMIT_WINDOW
    ]
    
    # Vérifier limite
    if len(rate_limit_store[ip]) >= GLOBAL_RATE_LIMIT:
        return False
    
    # Ajouter timestamp
    rate_limit_store[ip].append(current_time)
    return True


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Middleware de rate limiting"""
    # Récupérer IP
    ip = request.client.host if request.client else "unknown"
    
    # Vérifier rate limit
    if not check_rate_limit(ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    response = await call_next(request)
    return response


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Endpoint racine - Info serveur"""
    stats = game.get_stats()
    return {
        "game": "Battle Arena",
        "version": "1.0.0",
        "status": "online",
        "players_online": stats['game']['players_online'],
        "uptime_seconds": stats['server']['uptime_seconds']
    }


@app.post("/api/join")
def join_game(request: JoinRequest):
    """
    Rejoindre la partie
    
    - **username**: Nom du joueur (3-20 caractères alphanumériques)
    
    Retourne player_id, position de spawn, et HP
    """
    result = game.join_game(request.username)
    
    if not result.get('success', False):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@app.post("/api/move")
def move_player(request: MoveRequest):
    """
    Déplacer son joueur
    
    - **player_id**: ID du joueur (obtenu via /api/join)
    - **direction_x**: Direction X (-1 à 1, sera normalisé)
    - **direction_y**: Direction Y (-1 à 1, sera normalisé)
    
    Le vecteur est automatiquement normalisé côté serveur.
    Retourne la nouvelle position.
    """
    result = game.player_move(request.player_id, request.direction_x, request.direction_y)
    
    if not result.get('success', False):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@app.post("/api/shoot")
def shoot(request: ShootRequest):
    """
    Tirer une balle
    
    - **player_id**: ID du joueur
    - **direction_x**: Direction de tir X
    - **direction_y**: Direction de tir Y
    
    Cooldown: 0.5 secondes entre tirs
    Max 5 balles simultanées par joueur
    """
    result = game.player_shoot(request.player_id, request.direction_x, request.direction_y)
    
    if not result.get('success', False):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result


@app.get("/api/state")
def get_game_state():
    """
    Récupérer l'état complet du jeu
    
    Retourne:
    - Liste de tous les joueurs (position, vie, kills)
    - Liste de toutes les balles actives
    - Liste des obstacles
    - Dimensions de la map
    
    Utilisé pour observer le jeu ou développer un client.
    """
    return game.get_state()


@app.get("/api/stats")
def get_stats():
    """
    Récupérer les statistiques du jeu
    
    Retourne:
    - Stats serveur (uptime, tick rate)
    - Stats jeu (joueurs, balles, kills all-time)
    - Top 10 joueurs actuels (par kills)
    """
    return game.get_stats()


@app.get("/api/health")
def health_check():
    """Healthcheck pour monitoring"""
    return {"status": "healthy", "game_running": game.running}


# ==================== EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Démarrer le game engine au lancement"""
    print("🚀 Démarrage du serveur...")
    game.start()
    print(f"✅ Serveur prêt sur port {config.SERVER_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Arrêter proprement le game engine"""
    print("🛑 Arrêt du serveur...")
    game.stop()
    print("✅ Serveur arrêté proprement")


# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.SERVER_PORT,
        log_level="info"
    )
