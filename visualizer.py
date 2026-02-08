#!/usr/bin/env python3
"""
Visualiseur Pygame de Battle Arena
Affiche la game en temps réel avec graphismes
"""
import pygame
import requests
import sys
import math
from typing import Dict, List, Optional


class GameVisualizer:
    """Visualiseur graphique du jeu avec Pygame"""
    
    def __init__(self, api_url: str = "http://localhost:8000", window_size: int = 800):
        self.api_url = api_url.rstrip('/')
        self.window_size = window_size
        
        # Dimensions du jeu
        self.map_width = 100.0
        self.map_height = 100.0
        self.scale = window_size / self.map_width  # pixels par unité
        
        # Initialiser Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Battle Arena - Spectator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Couleurs
        self.colors = {
            'background': (20, 20, 30),
            'grid': (40, 40, 50),
            'obstacle': (100, 100, 120),
            'player': [(255, 100, 100), (100, 255, 100), (100, 100, 255),
                      (255, 255, 100), (255, 100, 255), (100, 255, 255)],
            'bullet': (255, 255, 100),
            'health_bg': (60, 60, 60),
            'health': (0, 255, 0),
            'text': (255, 255, 255),
            'shadow': (0, 0, 0)
        }
        
        self.running = True
        self.show_grid = True
        self.show_names = True
        self.show_health = True
        
        print("🎮 Battle Arena Visualizer (Pygame)")
        print(f"   API: {api_url}")
        print(f"   Window: {window_size}x{window_size}")
        print("\nControls:")
        print("  G - Toggle grid")
        print("  N - Toggle names")
        print("  H - Toggle health bars")
        print("  ESC - Quit\n")
    
    def get_state(self) -> Optional[Dict]:
        """Récupérer l'état du jeu"""
        try:
            response = requests.get(f"{self.api_url}/api/state", timeout=2)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Connection error: {e}")
        return None
    
    def get_stats(self) -> Optional[Dict]:
        """Récupérer les stats"""
        try:
            response = requests.get(f"{self.api_url}/api/stats", timeout=2)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def world_to_screen(self, x: float, y: float) -> tuple:
        """Convertir coordonnées monde en coordonnées écran"""
        screen_x = int(x * self.scale)
        screen_y = int(y * self.scale)
        return screen_x, screen_y
    
    def draw_grid(self):
        """Dessiner la grille"""
        if not self.show_grid:
            return
        
        grid_spacing = 10 * self.scale  # Grille tous les 10 unités
        
        # Lignes verticales
        for i in range(0, self.window_size, int(grid_spacing)):
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (i, 0), (i, self.window_size), 1)
        
        # Lignes horizontales
        for i in range(0, self.window_size, int(grid_spacing)):
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (0, i), (self.window_size, i), 1)
    
    def draw_obstacles(self, obstacles: List[Dict]):
        """Dessiner les obstacles"""
        for obs in obstacles:
            x, y = self.world_to_screen(obs['x'], obs['y'])
            width = int(obs['width'] * self.scale)
            height = int(obs['height'] * self.scale)
            
            # Ombre
            shadow_offset = 3
            pygame.draw.rect(self.screen, self.colors['shadow'],
                           (x + shadow_offset, y + shadow_offset, width, height))
            
            # Obstacle
            pygame.draw.rect(self.screen, self.colors['obstacle'],
                           (x, y, width, height))
            
            # Bordure
            pygame.draw.rect(self.screen, (150, 150, 170),
                           (x, y, width, height), 2)
    
    def draw_bullets(self, bullets: List[Dict]):
        """Dessiner les balles"""
        for bullet in bullets:
            x, y = self.world_to_screen(bullet['x'], bullet['y'])
            
            # Traînée (effet de mouvement)
            vx, vy = bullet['vx'], bullet['vy']
            mag = math.sqrt(vx*vx + vy*vy)
            if mag > 0:
                trail_len = 10
                trail_x = x - int((vx/mag) * trail_len)
                trail_y = y - int((vy/mag) * trail_len)
                
                for i in range(5):
                    alpha = 255 - (i * 50)
                    t_x = int(x + (trail_x - x) * (i/5))
                    t_y = int(y + (trail_y - y) * (i/5))
                    color = (255, 255, 100, alpha)
                    pygame.draw.circle(self.screen, self.colors['bullet'], 
                                     (t_x, t_y), 2)
            
            # Balle principale
            pygame.draw.circle(self.screen, self.colors['bullet'], (x, y), 4)
            pygame.draw.circle(self.screen, (255, 255, 200), (x, y), 2)
    
    def draw_health_bar(self, x: int, y: int, health: int, max_health: int = 100):
        """Dessiner barre de vie"""
        if not self.show_health:
            return
        
        bar_width = 40
        bar_height = 6
        bar_x = x - bar_width // 2
        bar_y = y - 25
        
        # Background
        pygame.draw.rect(self.screen, self.colors['health_bg'],
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((health / max_health) * bar_width)
        
        # Couleur selon santé
        if health > 70:
            color = (0, 255, 0)
        elif health > 30:
            color = (255, 165, 0)
        else:
            color = (255, 0, 0)
        
        pygame.draw.rect(self.screen, color,
                        (bar_x, bar_y, health_width, bar_height))
        
        # Bordure
        pygame.draw.rect(self.screen, (200, 200, 200),
                        (bar_x, bar_y, bar_width, bar_height), 1)
    
    def draw_players(self, players: List[Dict]):
        """Dessiner les joueurs"""
        for i, player in enumerate(players):
            x, y = self.world_to_screen(player['x'], player['y'])
            color = self.colors['player'][i % len(self.colors['player'])]
            
            # Radius
            radius = int(0.5 * self.scale)  # PLAYER_RADIUS = 0.5
            
            # Ombre
            shadow_offset = 3
            pygame.draw.circle(self.screen, self.colors['shadow'],
                             (x + shadow_offset, y + shadow_offset), radius)
            
            # Corps du joueur
            pygame.draw.circle(self.screen, color, (x, y), radius)
            
            # Bordure
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), radius, 2)
            
            # Point au centre
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)
            
            # Barre de vie
            self.draw_health_bar(x, y, player['health'])
            
            # Nom et stats
            if self.show_names:
                # Nom
                name_text = self.small_font.render(player['username'], True, 
                                                   self.colors['text'])
                name_rect = name_text.get_rect(center=(x, y - 35))
                
                # Ombre du texte
                shadow_text = self.small_font.render(player['username'], True, 
                                                     self.colors['shadow'])
                shadow_rect = shadow_text.get_rect(center=(x + 1, y - 34))
                self.screen.blit(shadow_text, shadow_rect)
                self.screen.blit(name_text, name_rect)
                
                # Kills
                kills_text = self.small_font.render(f"Kills: {player['kills']}", True,
                                                    (255, 215, 0))
                kills_rect = kills_text.get_rect(center=(x, y + 20))
                self.screen.blit(kills_text, kills_rect)
    
    def draw_hud(self, state: Dict, stats: Optional[Dict]):
        """Dessiner HUD (info en haut)"""
        # Fond semi-transparent
        hud_surface = pygame.Surface((self.window_size, 60))
        hud_surface.set_alpha(200)
        hud_surface.fill((30, 30, 40))
        self.screen.blit(hud_surface, (0, 0))
        
        # Titre
        title = self.font.render("BATTLE ARENA - SPECTATOR", True, (255, 255, 100))
        self.screen.blit(title, (10, 10))
        
        # Stats
        players_count = len(state.get('players', []))
        bullets_count = len(state.get('bullets', []))
        
        info_text = f"Players: {players_count}  |  Bullets: {bullets_count}"
        info = self.small_font.render(info_text, True, self.colors['text'])
        self.screen.blit(info, (10, 35))
        
        # Stats globales
        if stats:
            total_kills = stats['game'].get('total_kills_all_time', 0)
            global_info = self.small_font.render(f"Total Kills: {total_kills}", 
                                                 True, (255, 100, 100))
            self.screen.blit(global_info, (self.window_size - 150, 35))
        
        # FPS
        fps = int(self.clock.get_fps())
        fps_text = self.small_font.render(f"FPS: {fps}", True, (100, 255, 100))
        self.screen.blit(fps_text, (self.window_size - 80, 10))
    
    def draw_leaderboard(self, players: List[Dict]):
        """Dessiner leaderboard sur le côté"""
        if not players:
            return
        
        # Trier par kills
        sorted_players = sorted(players, key=lambda p: p['kills'], reverse=True)[:5]
        
        # Fond
        board_width = 200
        board_height = 30 + len(sorted_players) * 25
        board_x = self.window_size - board_width - 10
        board_y = 70
        
        board_surface = pygame.Surface((board_width, board_height))
        board_surface.set_alpha(180)
        board_surface.fill((20, 20, 30))
        self.screen.blit(board_surface, (board_x, board_y))
        
        # Bordure
        pygame.draw.rect(self.screen, (100, 100, 150),
                        (board_x, board_y, board_width, board_height), 2)
        
        # Titre
        title = self.small_font.render("TOP PLAYERS", True, (255, 215, 0))
        self.screen.blit(title, (board_x + 10, board_y + 5))
        
        # Joueurs
        for i, player in enumerate(sorted_players):
            y_pos = board_y + 30 + i * 25
            
            # Rang
            rank_text = self.small_font.render(f"{i+1}.", True, (200, 200, 200))
            self.screen.blit(rank_text, (board_x + 10, y_pos))
            
            # Nom (tronqué si trop long)
            name = player['username'][:12]
            name_text = self.small_font.render(name, True, (255, 255, 255))
            self.screen.blit(name_text, (board_x + 35, y_pos))
            
            # Kills
            kills = self.small_font.render(str(player['kills']), True, (255, 100, 100))
            self.screen.blit(kills, (board_x + 160, y_pos))
    
    def handle_events(self):
        """Gérer les événements"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                    print(f"Grid: {'ON' if self.show_grid else 'OFF'}")
                elif event.key == pygame.K_n:
                    self.show_names = not self.show_names
                    print(f"Names: {'ON' if self.show_names else 'OFF'}")
                elif event.key == pygame.K_h:
                    self.show_health = not self.show_health
                    print(f"Health bars: {'ON' if self.show_health else 'OFF'}")
    
    def run(self, fps: int = 30):
        """Boucle principale"""
        print("🎬 Starting visualizer...")
        
        frame_count = 0
        
        while self.running:
            self.handle_events()
            
            # Récupérer état toutes les frames
            state = self.get_state()
            
            # Récupérer stats toutes les 30 frames
            stats = None
            if frame_count % 30 == 0:
                stats = self.get_stats()
            
            if state is None:
                # Afficher message d'erreur
                self.screen.fill(self.colors['background'])
                error_text = self.font.render("Connection lost...", True, (255, 0, 0))
                error_rect = error_text.get_rect(center=(self.window_size//2, 
                                                         self.window_size//2))
                self.screen.blit(error_text, error_rect)
                
                retry_text = self.small_font.render("Retrying...", True, (200, 200, 200))
                retry_rect = retry_text.get_rect(center=(self.window_size//2, 
                                                         self.window_size//2 + 30))
                self.screen.blit(retry_text, retry_rect)
            else:
                # Dessiner tout
                self.screen.fill(self.colors['background'])
                self.draw_grid()
                self.draw_obstacles(state.get('obstacles', []))
                self.draw_bullets(state.get('bullets', []))
                self.draw_players(state.get('players', []))
                self.draw_hud(state, stats)
                self.draw_leaderboard(state.get('players', []))
            
            pygame.display.flip()
            self.clock.tick(fps)
            frame_count += 1
        
        pygame.quit()
        print("\n👋 Visualizer closed")


if __name__ == "__main__":
    # URL de l'API depuis args ou localhost par défaut
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Taille fenêtre
    window_size = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    
    try:
        viz = GameVisualizer(api_url, window_size)
        viz.run(fps=30)
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
