"""
Game Engine - Moteur de jeu principal
"""
import threading
import time
import random
import uuid
import json
import os
from typing import Dict, List, Optional, Tuple
from entities import Player, Bullet, Obstacle, GameStats
from physics import (
    normalize_vector, check_bullet_player_collision,
    check_bullet_obstacle_collision,
    find_valid_spawn_position, is_position_valid, clamp_to_map
)
import config


class GameEngine:
    """Moteur de jeu - État autoritaire en RAM"""
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.bullets: Dict[str, Bullet] = {}
        self.obstacles: List[Obstacle] = []
        self.death_cooldowns: Dict[str, float] = {}  # {username: timestamp_mort}
        self.stats = GameStats()
        
        self.running = False
        self.game_thread: Optional[threading.Thread] = None
        self.start_time = time.time()
        
        # Générer obstacles
        self._generate_obstacles()
        
        # Charger stats persistantes
        self._load_stats()
        
        print(f"🎮 Game Engine initialisé")
        print(f"   Map: {config.MAP_WIDTH}×{config.MAP_HEIGHT}")
        print(f"   Obstacles: {len(self.obstacles)}")
        print(f"   Tick rate: {config.TICK_RATE} FPS")
    
    def _generate_obstacles(self):
        """Générer obstacles aléatoires au démarrage"""
        spawn_x_min, spawn_x_max, spawn_y_min, spawn_y_max = config.SPAWN_SAFE_ZONE
        
        for i in range(config.OBSTACLE_COUNT):
            # Taille aléatoire
            width = random.uniform(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE)
            height = random.uniform(config.OBSTACLE_MIN_SIZE, config.OBSTACLE_MAX_SIZE)
            
            # Position aléatoire
            max_attempts = 50
            for _ in range(max_attempts):
                x = random.uniform(0, config.MAP_WIDTH - width)
                y = random.uniform(0, config.MAP_HEIGHT - height)
                
                # Éviter la zone de spawn
                if (spawn_x_min < x + width < spawn_x_max and 
                    spawn_y_min < y + height < spawn_y_max):
                    continue
                
                # Obstacle valide
                self.obstacles.append(Obstacle(i, x, y, width, height))
                break
        
        print(f"✅ {len(self.obstacles)} obstacles générés")
    
    def _load_stats(self):
        """Charger stats depuis fichier JSON"""
        if os.path.exists(config.STATS_FILE):
            try:
                with open(config.STATS_FILE, 'r') as f:
                    data = json.load(f)
                    self.stats = GameStats(**data)
                print(f"📊 Stats chargées: {self.stats.total_kills_all_time} kills all-time")
            except Exception as e:
                print(f"⚠️ Erreur chargement stats: {e}")
    
    def _save_stats(self):
        """Sauvegarder stats dans fichier JSON"""
        try:
            with open(config.STATS_FILE, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde stats: {e}")
    
    def start(self):
        """Démarrer le game loop"""
        if self.running:
            return
        
        self.running = True
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.game_thread.start()
        print("▶️ Game loop démarré")
    
    def stop(self):
        """Arrêter le game loop"""
        if not self.running:
            return
        
        self.running = False
        if self.game_thread:
            self.game_thread.join(timeout=2.0)
        
        # Sauvegarder stats
        self._save_stats()
        print("⏹️ Game loop arrêté")
    
    def _game_loop(self):
        """Boucle principale - 60 FPS"""
        while self.running:
            tick_start = time.time()
            
            try:
                self._update_physics()
                self._check_collisions()
                self._cleanup()
            except Exception as e:
                print(f"❌ Erreur game loop: {e}")
            
            # Maintenir tick rate
            elapsed = time.time() - tick_start
            sleep_time = max(0, config.TICK_DURATION - elapsed)
            time.sleep(sleep_time)
    
    def _update_physics(self):
        """Mise à jour physique - déplacement des balles"""
        bullets_to_remove = []
        
        for bullet_id, bullet in self.bullets.items():
            # Déplacer balle
            bullet.x += bullet.vx * config.TICK_DURATION
            bullet.y += bullet.vy * config.TICK_DURATION

            # Vérifier rebonds sur obstacles
            for obstacle in self.obstacles:
                if check_bullet_obstacle_collision(bullet, obstacle):
                    if bullet.bounces >= 3:
                        bullets_to_remove.append(bullet_id)
                        break
                    # Déterminer côté touché
                    overlap_x = min(abs(bullet.x - obstacle.x), abs(bullet.x - (obstacle.x + obstacle.width)))
                    overlap_y = min(abs(bullet.y - obstacle.y), abs(bullet.y - (obstacle.y + obstacle.height)))
                    if overlap_x < overlap_y:
                        bullet.vx *= -1
                    else:
                        bullet.vy *= -1
                    bullet.bounces += 1
                    break


            
            # Vérifier limites map
            if (bullet.x < 0 or bullet.x > config.MAP_WIDTH or
                bullet.y < 0 or bullet.y > config.MAP_HEIGHT):
                bullets_to_remove.append(bullet_id)
                continue
            
            # Lifetime max 10 secondes
            if time.time() - bullet.created_at > 10:
                bullets_to_remove.append(bullet_id)
        
        # Supprimer balles
        for bullet_id in bullets_to_remove:
            del self.bullets[bullet_id]
    
    def _check_collisions(self):
        """Détection collisions balles-joueurs"""
        bullets_to_remove = []
        
        for bullet_id, bullet in self.bullets.items():
            hit = False
            
            for player_id, player in self.players.items():
                # Pas se tirer dessus soi-même
                if bullet.owner_id == player_id:
                    continue
                
                # Check collision
                if check_bullet_player_collision(bullet, player):
                    # Appliquer dégâts
                    player.health -= bullet.damage
                    
                    # Mort?
                    if player.health <= 0:
                        self._handle_player_death(player_id, bullet.owner_id)
                    
                    hit = True
                    bullets_to_remove.append(bullet_id)
                    break
            
            if hit:
                continue
        
        # Supprimer balles
        for bullet_id in bullets_to_remove:
            if bullet_id in self.bullets:
                del self.bullets[bullet_id]
    
    def _handle_player_death(self, player_id: str, killer_id: str):
        """Gérer la mort d'un joueur"""
        player = self.players.get(player_id)
        if not player:
            return
        
        # Incrémenter kill du tueur
        killer = self.players.get(killer_id)
        if killer:
            killer.kills += 1
        
        # Stats globales
        self.stats.total_kills_all_time += 1
        self.stats.total_deaths_all_time += 1
        self._save_stats()
        
        # Cooldown respawn
        self.death_cooldowns[player.username] = time.time()
        
        # Supprimer joueur
        del self.players[player_id]
        
        print(f"💀 {player.username} tué par {killer.username if killer else 'unknown'}")
    
    def _cleanup(self):
        """Nettoyage - joueurs inactifs"""
        current_time = time.time()
        players_to_remove = []
        
        for player_id, player in self.players.items():
            # Kick si inactif trop longtemps
            if current_time - player.last_activity > config.INACTIVITY_TIMEOUT:
                players_to_remove.append(player_id)
        
        for player_id in players_to_remove:
            username = self.players[player_id].username
            del self.players[player_id]
            print(f"⏱️ {username} kick (inactivité)")
        
        # Nettoyer death cooldowns expirés
        expired = [username for username, death_time in self.death_cooldowns.items()
                   if current_time - death_time > config.DEATH_COOLDOWN]
        for username in expired:
            del self.death_cooldowns[username]
    
    # ==================== API PUBLIQUE ====================
    
    def join_game(self, username: str) -> dict:
        """Un joueur rejoint la partie"""
        current_time = time.time()
        
        # Vérifier cooldown mort
        if username in self.death_cooldowns:
            elapsed = current_time - self.death_cooldowns[username]
            if elapsed < config.DEATH_COOLDOWN:
                remaining = config.DEATH_COOLDOWN - elapsed
                return {
                    'success': False,
                    'error': f'Death cooldown: wait {remaining:.1f}s'
                }
            else:
                del self.death_cooldowns[username]
        
        # Vérifier limite joueurs
        if len(self.players) >= config.MAX_PLAYERS:
            return {'success': False, 'error': 'Server full'}
        
        # Générer ID unique
        player_id = f"{username}_{uuid.uuid4().hex[:8]}"
        
        # Trouver position spawn
        spawn_x, spawn_y = find_valid_spawn_position(
            self.obstacles, 
            list(self.players.values())
        )
        
        # Créer joueur
        player = Player(
            entity_id=player_id,
            username=username,
            x=spawn_x,
            y=spawn_y,
            health=config.PLAYER_MAX_HEALTH,
            last_move=current_time,
            last_shoot=current_time,
            last_activity=current_time
        )
        
        self.players[player_id] = player
        
        print(f"✅ {username} rejoint ({player_id}) à ({spawn_x:.1f}, {spawn_y:.1f})")
        
        return {
            'success': True,
            'player_id': player_id,
            'position': [round(spawn_x, 2), round(spawn_y, 2)],
            'health': config.PLAYER_MAX_HEALTH
        }
    
    def player_move(self, player_id: str, direction_x: float, direction_y: float) -> dict:
        """Déplacer un joueur"""
        current_time = time.time()
        
        # Vérifier joueur existe
        if player_id not in self.players:
            return {'success': False, 'error': 'Player not found'}
        
        player = self.players[player_id]
        
        # Rate limiting
        if current_time - player.last_move < config.MOVE_RATE_LIMIT:
            return {'success': False, 'error': 'Move too fast'}
        
        # Normaliser direction
        norm_x, norm_y = normalize_vector(direction_x, direction_y)
        
        if norm_x == 0 and norm_y == 0:
            # Pas de mouvement
            player.update_activity()
            return {'success': True, 'position': [round(player.x, 2), round(player.y, 2)]}
        
        # Calculer nouvelle position
        distance = config.PLAYER_SPEED * config.MOVE_RATE_LIMIT  # Distance parcourue
        new_x = player.x + norm_x * distance
        new_y = player.y + norm_y * distance
        
        # Clamp aux limites
        new_x, new_y = clamp_to_map(new_x, new_y)
        
        # Vérifier si position valide (pas de collision)
        if is_position_valid(new_x, new_y, self.obstacles, 
                            list(self.players.values()), player_id):
            player.x = new_x
            player.y = new_y
        # Sinon, on reste à l'ancienne position (bloqué)
        
        player.last_move = current_time
        player.update_activity()
        
        return {
            'success': True,
            'position': [round(player.x, 2), round(player.y, 2)]
        }
    
    def player_shoot(self, player_id: str, direction_x: float, direction_y: float) -> dict:
        """Tirer une balle"""
        current_time = time.time()
        
        # Vérifier joueur existe
        if player_id not in self.players:
            return {'success': False, 'error': 'Player not found'}
        
        player = self.players[player_id]
        
        # Cooldown tir
        if current_time - player.last_shoot < config.SHOOT_RATE_LIMIT:
            remaining = config.SHOOT_RATE_LIMIT - (current_time - player.last_shoot)
            return {'success': False, 'error': f'Cooldown: {remaining:.2f}s'}
        
        # Normaliser direction
        norm_x, norm_y = normalize_vector(direction_x, direction_y)
        
        if norm_x == 0 and norm_y == 0:
            return {'success': False, 'error': 'Invalid direction'}
        
        # Vérifier limite balles
        player_bullets = [b for b in self.bullets.values() if b.owner_id == player_id]
        if len(player_bullets) >= config.MAX_BULLETS_PER_PLAYER:
            return {'success': False, 'error': 'Too many bullets'}
        
        # Créer balle
        bullet_id = f"bullet_{uuid.uuid4().hex[:12]}"
        bullet = Bullet(
            entity_id=bullet_id,
            owner_id=player_id,
            x=player.x,
            y=player.y,
            vx=norm_x * config.BULLET_SPEED,
            vy=norm_y * config.BULLET_SPEED,
            damage=config.BULLET_DAMAGE
        )
        
        self.bullets[bullet_id] = bullet
        player.last_shoot = current_time
        player.update_activity()
        
        # Stats
        self.stats.total_shots_all_time += 1
        
        return {'success': True, 'bullet_id': bullet_id}
    
    def get_state(self) -> dict:
        """Récupérer l'état complet du jeu"""
        return {
            'players': [p.to_dict() for p in self.players.values()],
            'bullets': [b.to_dict() for b in self.bullets.values()],
            'obstacles': [o.to_dict() for o in self.obstacles],
            'map': {
                'width': config.MAP_WIDTH,
                'height': config.MAP_HEIGHT
            }
        }
    
    def get_stats(self) -> dict:
        """Récupérer statistiques du jeu"""
        current_time = time.time()
        
        # Top joueurs actuels
        top_players = sorted(self.players.values(), key=lambda p: p.kills, reverse=True)[:10]
        
        return {
            'server': {
                'uptime_seconds': int(current_time - self.start_time),
                'tick_rate': config.TICK_RATE
            },
            'game': {
                'players_online': len(self.players),
                'bullets_active': len(self.bullets),
                'obstacles_count': len(self.obstacles),
                'total_kills_all_time': self.stats.total_kills_all_time,
                'total_deaths_all_time': self.stats.total_deaths_all_time,
                'total_shots_all_time': self.stats.total_shots_all_time
            },
            'top_players_current': [
                {
                    'username': p.username,
                    'kills': p.kills,
                    'health': p.health
                } for p in top_players
            ]
        }
