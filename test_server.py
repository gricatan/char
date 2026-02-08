#!/usr/bin/env python3
"""
Script de test - Vérifie que le serveur fonctionne
"""
import requests
import time
import sys


def test_server(base_url="http://localhost:8000"):
    """Tester tous les endpoints"""
    
    print("🧪 Test du serveur Battle Arena")
    print(f"   URL: {base_url}\n")
    
    try:
        # Test 1: Root endpoint
        print("1️⃣ Test endpoint racine...")
        response = requests.get(f"{base_url}/", timeout=5)
        assert response.status_code == 200, "Erreur status code"
        data = response.json()
        print(f"   ✅ OK - {data['game']} v{data['version']}")
        print(f"   Joueurs en ligne: {data['players_online']}\n")
        
        # Test 2: Join
        print("2️⃣ Test JOIN...")
        response = requests.post(f"{base_url}/api/join", 
                               json={"username": "TestBot"}, 
                               timeout=5)
        assert response.status_code == 200, "Erreur join"
        data = response.json()
        player_id = data['player_id']
        print(f"   ✅ OK - Player ID: {player_id}")
        print(f"   Position: {data['position']}\n")
        
        # Test 3: State
        print("3️⃣ Test GET STATE...")
        response = requests.get(f"{base_url}/api/state", timeout=5)
        assert response.status_code == 200, "Erreur state"
        data = response.json()
        print(f"   ✅ OK")
        print(f"   Joueurs: {len(data['players'])}")
        print(f"   Balles: {len(data['bullets'])}")
        print(f"   Obstacles: {len(data['obstacles'])}\n")
        
        # Test 4: Move
        print("4️⃣ Test MOVE...")
        response = requests.post(f"{base_url}/api/move", 
                               json={
                                   "player_id": player_id,
                                   "direction_x": 1.0,
                                   "direction_y": 0.0
                               }, 
                               timeout=5)
        assert response.status_code == 200, "Erreur move"
        data = response.json()
        print(f"   ✅ OK - Nouvelle position: {data['position']}\n")
        
        # Test 5: Shoot
        print("5️⃣ Test SHOOT...")
        response = requests.post(f"{base_url}/api/shoot", 
                               json={
                                   "player_id": player_id,
                                   "direction_x": 0.0,
                                   "direction_y": -1.0
                               }, 
                               timeout=5)
        assert response.status_code == 200, "Erreur shoot"
        data = response.json()
        print(f"   ✅ OK - Bullet ID: {data['bullet_id']}\n")
        
        # Test 6: Stats
        print("6️⃣ Test STATS...")
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        assert response.status_code == 200, "Erreur stats"
        data = response.json()
        print(f"   ✅ OK")
        print(f"   Uptime: {data['server']['uptime_seconds']}s")
        print(f"   Tick rate: {data['server']['tick_rate']} FPS")
        print(f"   Total kills: {data['game']['total_kills_all_time']}\n")
        
        # Test 7: Health
        print("7️⃣ Test HEALTH...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        assert response.status_code == 200, "Erreur health"
        data = response.json()
        print(f"   ✅ OK - Status: {data['status']}")
        print(f"   Game running: {data['game_running']}\n")
        
        print("=" * 50)
        print("✅ TOUS LES TESTS PASSÉS!")
        print("=" * 50)
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter au serveur")
        print(f"   Vérifiez que le serveur tourne sur {base_url}")
        return False
        
    except AssertionError as e:
        print(f"\n❌ ERREUR DE TEST: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        return False


if __name__ == "__main__":
    # URL depuis args ou localhost par défaut
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Attendre que le serveur démarre
    print("⏳ Attente démarrage du serveur...")
    time.sleep(2)
    
    # Lancer tests
    success = test_server(url)
    
    sys.exit(0 if success else 1)
