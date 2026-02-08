"""
Entités du jeu
"""
from dataclasses import dataclass, field, asdict
from typing import Optional
import time
import uuid


@dataclass
class Player:
    """Joueur dans le jeu"""
    entity_id: str
    username: str
    x: float
    y: float
    health: int = 100
    kills: int = 0
    last_move: float = 0.0
    last_shoot: float = 0.0
    last_activity: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        """Convertir en dict pour l'API"""
        return {
            'id': self.entity_id,
            'username': self.username,
            'x': round(self.x, 2),
            'y': round(self.y, 2),
            'health': self.health,
            'kills': self.kills
        }
    
    def update_activity(self):
        """Mettre à jour le timestamp de dernière activité"""
        self.last_activity = time.time()


@dataclass
class Bullet:
    """Balle tirée par un joueur"""
    entity_id: str
    owner_id: str
    x: float
    y: float
    vx: float  # Vélocité X (direction normalisée × vitesse)
    vy: float  # Vélocité Y
    damage: int = 10
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        """Convertir en dict pour l'API"""
        return {
            'id': self.entity_id,
            'owner_id': self.owner_id,
            'x': round(self.x, 2),
            'y': round(self.y, 2),
            'vx': round(self.vx, 2),
            'vy': round(self.vy, 2)
        }


@dataclass
class Obstacle:
    """Obstacle rectangulaire fixe"""
    obstacle_id: int
    x: float
    y: float
    width: float
    height: float
    
    def to_dict(self) -> dict:
        """Convertir en dict pour l'API"""
        return {
            'id': self.obstacle_id,
            'x': round(self.x, 2),
            'y': round(self.y, 2),
            'width': round(self.width, 2),
            'height': round(self.height, 2)
        }


@dataclass
class GameStats:
    """Statistiques globales du jeu"""
    total_kills_all_time: int = 0
    total_deaths_all_time: int = 0
    total_shots_all_time: int = 0
    games_played: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)
