"""
Physique et détection de collisions
"""
import math
from typing import Tuple, Optional, List
from entities import Player, Bullet, Obstacle
import config


def normalize_vector(x: float, y: float) -> Tuple[float, float]:
    """Normaliser un vecteur (retourne vecteur unitaire)"""
    magnitude = math.sqrt(x * x + y * y)
    if magnitude == 0:
        return 0.0, 0.0
    return x / magnitude, y / magnitude


def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Distance euclidienne entre deux points"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def circle_circle_collision(x1: float, y1: float, r1: float,
                            x2: float, y2: float, r2: float) -> bool:
    """Détection collision cercle-cercle"""
    dist = distance(x1, y1, x2, y2)
    return dist < (r1 + r2)


def circle_rect_collision(cx: float, cy: float, radius: float,
                          rx: float, ry: float, width: float, height: float) -> bool:
    """Détection collision cercle-rectangle (AABB)"""
    # Trouver le point le plus proche du cercle sur le rectangle
    closest_x = max(rx, min(cx, rx + width))
    closest_y = max(ry, min(cy, ry + height))
    
    # Distance entre ce point et le centre du cercle
    dist = distance(cx, cy, closest_x, closest_y)
    
    return dist < radius


def check_player_obstacle_collision(player: Player, obstacle: Obstacle) -> bool:
    """Vérifier collision joueur-obstacle"""
    return circle_rect_collision(
        player.x, player.y, config.PLAYER_RADIUS,
        obstacle.x, obstacle.y, obstacle.width, obstacle.height
    )


def check_bullet_player_collision(bullet: Bullet, player: Player) -> bool:
    """Vérifier collision balle-joueur"""
    return circle_circle_collision(
        bullet.x, bullet.y, config.BULLET_RADIUS,
        player.x, player.y, config.PLAYER_RADIUS
    )


def check_player_player_collision(p1: Player, p2: Player) -> bool:
    """Vérifier collision joueur-joueur"""
    return circle_circle_collision(
        p1.x, p1.y, config.PLAYER_RADIUS,
        p2.x, p2.y, config.PLAYER_RADIUS
    )


def find_valid_spawn_position(obstacles: List[Obstacle], players: List[Player]) -> Tuple[float, float]:
    """
    Trouver une position de spawn valide
    - Loin des obstacles
    - Loin des autres joueurs
    - Dans la zone de spawn sécurisée
    """
    import random
    
    max_attempts = 100
    spawn_x_min, spawn_x_max, spawn_y_min, spawn_y_max = config.SPAWN_SAFE_ZONE
    
    for _ in range(max_attempts):
        x = random.uniform(spawn_x_min, spawn_x_max)
        y = random.uniform(spawn_y_min, spawn_y_max)
        
        # Vérifier collision avec obstacles
        valid = True
        for obs in obstacles:
            if circle_rect_collision(x, y, config.PLAYER_RADIUS, obs.x, obs.y, obs.width, obs.height):
                valid = False
                break
        
        if not valid:
            continue
        
        # Vérifier distance avec autres joueurs
        for player in players:
            if distance(x, y, player.x, player.y) < config.PLAYER_SPAWN_MIN_DISTANCE:
                valid = False
                break
        
        if valid:
            return x, y
    
    # Fallback: centre exact si rien ne marche
    return 50.0, 50.0


def is_position_valid(x: float, y: float, obstacles: List[Obstacle], 
                      players: List[Player], exclude_player_id: Optional[str] = None) -> bool:
    """
    Vérifier si une position est valide (pas de collision)
    """
    # Vérifier limites map
    if x < config.PLAYER_RADIUS or x > config.MAP_WIDTH - config.PLAYER_RADIUS:
        return False
    if y < config.PLAYER_RADIUS or y > config.MAP_HEIGHT - config.PLAYER_RADIUS:
        return False
    
    # Vérifier collision avec obstacles
    for obs in obstacles:
        if circle_rect_collision(x, y, config.PLAYER_RADIUS, obs.x, obs.y, obs.width, obs.height):
            return False
    
    # Vérifier collision avec autres joueurs
    for player in players:
        if exclude_player_id and player.entity_id == exclude_player_id:
            continue
        if circle_circle_collision(x, y, config.PLAYER_RADIUS, player.x, player.y, config.PLAYER_RADIUS):
            return False
    
    return True


def clamp_to_map(x: float, y: float) -> Tuple[float, float]:
    """Restreindre une position aux limites de la map"""
    x = max(0, min(config.MAP_WIDTH, x))
    y = max(0, min(config.MAP_HEIGHT, y))
    return x, y
