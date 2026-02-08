"""
Client Exemple - Bot avec IA simple
"""
import requests
import time
import random
import math
from typing import Optional, List, Dict


class GameClient:
    """Client pour se connecter à l'API du jeu"""
    
    def __init__(self, api_url: str, username: str):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.player_id: Optional[str] = None
        self.my_state: Optional[Dict] = None
        
        print(f"🎮 Client {username} initialisé")
        print(f"   API: {api_url}")
    
    def join(self) -> bool:
        """Rejoindre la partie"""
        try:
            response = requests.post(
                f"{self.api_url}/api/join",
                json={'username': self.username},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.player_id = data['player_id']
                print(f"✅ Connecté! ID: {self.player_id}")
                print(f"   Position: {data['position']}")
                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print(f"❌ Erreur join: {error}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def move(self, direction_x: float, direction_y: float) -> bool:
        """Déplacer le joueur"""
        if not self.player_id:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/move",
                json={
                    'player_id': self.player_id,
                    'direction_x': direction_x,
                    'direction_y': direction_y
                },
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"⚠️ Erreur move: {e}")
            return False
    
    def shoot(self, direction_x: float, direction_y: float) -> bool:
        """Tirer une balle"""
        if not self.player_id:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/shoot",
                json={
                    'player_id': self.player_id,
                    'direction_x': direction_x,
                    'direction_y': direction_y
                },
                timeout=5
            )
            
            if response.status_code == 200:
                return True
            else:
                # Silencieux pour les cooldowns
                return False
                
        except Exception as e:
            print(f"⚠️ Erreur shoot: {e}")
            return False
    
    def get_state(self) -> Optional[Dict]:
        """Récupérer l'état du jeu"""
        try:
            response = requests.get(f"{self.api_url}/api/state", timeout=5)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            print(f"⚠️ Erreur get_state: {e}")
            return None
    
    def find_my_player(self, state: Dict) -> Optional[Dict]:
        """Trouver mon joueur dans l'état du jeu"""
        if not self.player_id:
            return None
        
        for player in state.get('players', []):
            if player['id'] == self.player_id:
                return player
        
        return None
    
    def find_enemies(self, state: Dict) -> List[Dict]:
        """Trouver les ennemis"""
        if not self.player_id:
            return []
        
        return [p for p in state.get('players', []) if p['id'] != self.player_id]
    
    def distance_to(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculer distance entre deux points"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    def simple_ai(self):
        """
        IA simple:
        1. Récupérer état du jeu
        2. Trouver l'ennemi le plus proche
        3. Se déplacer vers lui et tirer
        """
        # Récupérer état
        state = self.get_state()
        if not state:
            return
        
        # Trouver mon joueur
        me = self.find_my_player(state)
        if not me:
            print("💀 Je suis mort ou déconnecté")
            return
        
        self.my_state = me
        
        # Afficher stats
        print(f"❤️ HP: {me['health']} | 🎯 Kills: {me['kills']} | 📍 Pos: ({me['x']:.1f}, {me['y']:.1f})")
        
        # Trouver ennemis
        enemies = self.find_enemies(state)
        
        if not enemies:
            # Pas d'ennemis, mouvement aléatoire
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
            self.move(dx, dy)
            return
        
        # Trouver l'ennemi le plus proche
        closest = min(
            enemies,
            key=lambda e: self.distance_to(me['x'], me['y'], e['x'], e['y'])
        )
        
        # Vecteur vers l'ennemi
        dx = closest['x'] - me['x']
        dy = closest['y'] - me['y']
        dist = self.distance_to(me['x'], me['y'], closest['x'], closest['y'])
        
        print(f"🎯 Ennemi: {closest['username']} à {dist:.1f} unités")
        
        # Stratégie: maintenir distance ~15-20 unités
        if dist > 25:
            # Trop loin, se rapprocher
            self.move(dx, dy)
            print("   ➡️ Se rapproche")
        elif dist < 10:
            # Trop proche, reculer
            self.move(-dx, -dy)
            print("   ⬅️ Recule")
        else:
            # Bonne distance, strafing
            # Mouvement perpendiculaire
            perp_x = -dy
            perp_y = dx
            self.move(perp_x, perp_y)
            print("   ↔️ Strafe")
        
        # Toujours tirer vers l'ennemi
        if self.shoot(dx, dy):
            print("   🔫 Tir!")
    
    def aggressive_ai(self):
        """
        IA agressive:
        - Fonce directement sur l'ennemi
        - Tire en continu
        """
        state = self.get_state()
        if not state:
            return
        
        me = self.find_my_player(state)
        if not me:
            print("💀 Mort")
            return
        
        enemies = self.find_enemies(state)
        
        if enemies:
            # Foncer sur le plus proche
            closest = min(
                enemies,
                key=lambda e: self.distance_to(me['x'], me['y'], e['x'], e['y'])
            )
            
            dx = closest['x'] - me['x']
            dy = closest['y'] - me['y']
            
            self.move(dx, dy)
            self.shoot(dx, dy)
            print(f"⚔️ CHARGE! HP:{me['health']} Kills:{me['kills']}")
        else:
            # Mouvement aléatoire
            self.move(random.uniform(-1, 1), random.uniform(-1, 1))
    
    def defensive_ai(self):
        """
        IA défensive:
        - Garde ses distances
        - Tire avec précision
        """
        state = self.get_state()
        if not state:
            return
        
        me = self.find_my_player(state)
        if not me:
            return
        
        enemies = self.find_enemies(state)
        
        if enemies:
            closest = min(
                enemies,
                key=lambda e: self.distance_to(me['x'], me['y'], e['x'], e['y'])
            )
            
            dx = closest['x'] - me['x']
            dy = closest['y'] - me['y']
            dist = self.distance_to(me['x'], me['y'], closest['x'], closest['y'])
            
            # Maintenir distance ~30 unités
            if dist < 25:
                self.move(-dx, -dy)  # Fuir
                print(f"🛡️ FUITE! HP:{me['health']}")
            else:
                # Tir de sniper
                self.shoot(dx, dy)
                print(f"🎯 SNIPE! HP:{me['health']} Kills:{me['kills']}")
    
    def play(self, ai_type: str = "simple", action_delay: float = 0.3):
        """
        Boucle de jeu principale
        
        ai_type: 'simple', 'aggressive', 'defensive'
        action_delay: délai entre actions (secondes)
        """
        # Rejoindre
        if not self.join():
            print("❌ Impossible de rejoindre")
            return
        
        # Choisir IA
        ai_function = {
            'simple': self.simple_ai,
            'aggressive': self.aggressive_ai,
            'defensive': self.defensive_ai
        }.get(ai_type, self.simple_ai)
        
        print(f"🤖 IA: {ai_type}")
        print(f"⏱️ Action delay: {action_delay}s")
        print("🎮 Démarrage du jeu!\n")
        
        consecutive_errors = 0
        
        while True:
            try:
                ai_function()
                consecutive_errors = 0
                time.sleep(action_delay)
                
            except KeyboardInterrupt:
                print("\n👋 Arrêt du client")
                break
                
            except Exception as e:
                consecutive_errors += 1
                print(f"❌ Erreur: {e}")
                
                if consecutive_errors > 10:
                    print("💀 Trop d'erreurs, arrêt")
                    break
                
                time.sleep(2)
        
        print(f"📊 Stats finales:")
        if self.my_state:
            print(f"   HP: {self.my_state.get('health', 0)}")
            print(f"   Kills: {self.my_state.get('kills', 0)}")


# ==================== USAGE ====================

if __name__ == "__main__":
    import sys
    
    # Configuration
    API_URL = "http://localhost:8000"
    
    # Récupérer username depuis args ou générer aléatoire
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = f"Bot{random.randint(1000, 9999)}"
    
    # Récupérer type IA depuis args
    ai_type = sys.argv[2] if len(sys.argv) > 2 else "simple"
    
    # Créer et lancer client
    client = GameClient(API_URL, username)
    client.play(ai_type=ai_type, action_delay=0.2)
