#!/usr/bin/env python3
"""
Bot Exemple Simple - Battle Arena
Un bot basique pour comprendre comment jouer
"""
import requests
import time
import random


# ============ CONFIGURATION ============
API_URL = "http://localhost:8000"  # Adresse du serveur
USERNAME = "SimpleBot"              # Ton nom


# ============ FONCTIONS DE BASE ============

def rejoindre():
    """Rejoindre la partie"""
    response = requests.post(f"{API_URL}/api/join", 
                            json={"username": USERNAME})
    
    if response.status_code == 200:
        data = response.json()
        player_id = data['player_id']
        print(f"✅ Connecté! ID: {player_id}")
        print(f"   Position de départ: {data['position']}")
        return player_id
    else:
        print(f"❌ Erreur: {response.json()}")
        return None


def bouger(player_id, direction_x, direction_y):
    """
    Déplacer le joueur
    
    direction_x: -1 (gauche) à 1 (droite)
    direction_y: -1 (haut) à 1 (bas)
    """
    response = requests.post(f"{API_URL}/api/move", json={
        "player_id": player_id,
        "direction_x": direction_x,
        "direction_y": direction_y
    })
    
    return response.status_code == 200


def tirer(player_id, direction_x, direction_y):
    """
    Tirer une balle
    
    direction_x: direction horizontale
    direction_y: direction verticale
    """
    response = requests.post(f"{API_URL}/api/shoot", json={
        "player_id": player_id,
        "direction_x": direction_x,
        "direction_y": direction_y
    })
    
    return response.status_code == 200


def voir_etat():
    """Voir l'état complet du jeu"""
    response = requests.get(f"{API_URL}/api/state")
    
    if response.status_code == 200:
        return response.json()
    return None


def trouver_moi(state, player_id):
    """Trouver mes informations dans l'état du jeu"""
    for player in state.get('players', []):
        if player['id'] == player_id:
            return player
    return None


def trouver_ennemis(state, player_id):
    """Trouver tous les ennemis"""
    ennemis = []
    for player in state.get('players', []):
        if player['id'] != player_id:
            ennemis.append(player)
    return ennemis


def distance(x1, y1, x2, y2):
    """Calculer la distance entre deux points"""
    import math
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# ============ STRATÉGIES ============

def strategie_aleatoire(player_id):
    """
    Stratégie 1: Mouvement et tir aléatoires
    Le bot le plus simple possible
    """
    # Bouger dans une direction aléatoire
    dir_x = random.uniform(-1, 1)
    dir_y = random.uniform(-1, 1)
    bouger(player_id, dir_x, dir_y)
    
    # Tirer dans une direction aléatoire
    tir_x = random.uniform(-1, 1)
    tir_y = random.uniform(-1, 1)
    tirer(player_id, tir_x, tir_y)
    
    print("🎲 Mouvement aléatoire")


def strategie_chasseur(player_id):
    """
    Stratégie 2: Chasser l'ennemi le plus proche
    Un peu plus intelligent
    """
    # Récupérer l'état du jeu
    state = voir_etat()
    if not state:
        return
    
    # Me trouver
    moi = trouver_moi(state, player_id)
    if not moi:
        print("💀 Je suis mort!")
        return
    
    # Trouver les ennemis
    ennemis = trouver_ennemis(state, player_id)
    
    if not ennemis:
        # Pas d'ennemi, bouger aléatoirement
        bouger(player_id, random.uniform(-1, 1), random.uniform(-1, 1))
        print("🔍 Recherche d'ennemis...")
        return
    
    # Trouver l'ennemi le plus proche
    ennemi_proche = None
    distance_min = float('inf')
    
    for ennemi in ennemis:
        dist = distance(moi['x'], moi['y'], ennemi['x'], ennemi['y'])
        if dist < distance_min:
            distance_min = dist
            ennemi_proche = ennemi
    
    # Direction vers l'ennemi
    dir_x = ennemi_proche['x'] - moi['x']
    dir_y = ennemi_proche['y'] - moi['y']
    
    # Se déplacer vers lui
    bouger(player_id, dir_x, dir_y)
    
    # Tirer vers lui
    tirer(player_id, dir_x, dir_y)
    
    print(f"🎯 Chasse {ennemi_proche['username']} (dist: {distance_min:.1f})")
    print(f"   Ma vie: {moi['health']} HP | Mes kills: {moi['kills']}")


def strategie_fuyard(player_id):
    """
    Stratégie 3: Fuir et tirer de loin
    Bot défensif
    """
    state = voir_etat()
    if not state:
        return
    
    moi = trouver_moi(state, player_id)
    if not moi:
        return
    
    ennemis = trouver_ennemis(state, player_id)
    
    if not ennemis:
        bouger(player_id, random.uniform(-1, 1), random.uniform(-1, 1))
        return
    
    # Trouver l'ennemi le plus proche
    ennemi_proche = min(ennemis, 
                       key=lambda e: distance(moi['x'], moi['y'], e['x'], e['y']))
    
    dist = distance(moi['x'], moi['y'], ennemi_proche['x'], ennemi_proche['y'])
    
    # Direction vers l'ennemi
    dir_x = ennemi_proche['x'] - moi['x']
    dir_y = ennemi_proche['y'] - moi['y']
    
    if dist < 20:
        # Trop proche! FUIR!
        bouger(player_id, -dir_x, -dir_y)  # Direction opposée
        print(f"🏃 FUITE! Ennemi trop proche ({dist:.1f})")
    else:
        # Bonne distance, tirer
        tirer(player_id, dir_x, dir_y)
        print(f"🎯 Tir de loin ({dist:.1f})")
    
    print(f"   HP: {moi['health']} | Kills: {moi['kills']}")


def strategie_sniper(player_id):
    """
    Stratégie 4: Rester immobile et tirer
    Sniper statique
    """
    state = voir_etat()
    if not state:
        return
    
    moi = trouver_moi(state, player_id)
    if not moi:
        return
    
    ennemis = trouver_ennemis(state, player_id)
    
    if ennemis:
        # Tirer sur l'ennemi le plus proche
        ennemi = min(ennemis,
                    key=lambda e: distance(moi['x'], moi['y'], e['x'], e['y']))
        
        dir_x = ennemi['x'] - moi['x']
        dir_y = ennemi['y'] - moi['y']
        
        if tirer(player_id, dir_x, dir_y):
            print(f"🎯 SNIPE sur {ennemi['username']}")
    
    print(f"   HP: {moi['health']} | Kills: {moi['kills']}")


def strategie_kamikaze(player_id):
    """
    Stratégie 5: Foncer droit sur l'ennemi
    Très agressif
    """
    state = voir_etat()
    if not state:
        return
    
    moi = trouver_moi(state, player_id)
    if not moi:
        return
    
    ennemis = trouver_ennemis(state, player_id)
    
    if ennemis:
        # Foncer sur l'ennemi le plus proche
        ennemi = min(ennemis,
                    key=lambda e: distance(moi['x'], moi['y'], e['x'], e['y']))
        
        dir_x = ennemi['x'] - moi['x']
        dir_y = ennemi['y'] - moi['y']
        
        # FONCE!
        bouger(player_id, dir_x, dir_y)
        tirer(player_id, dir_x, dir_y)
        
        print(f"⚔️ CHARGE sur {ennemi['username']}!")
    else:
        bouger(player_id, random.uniform(-1, 1), random.uniform(-1, 1))
    
    print(f"   HP: {moi['health']} | Kills: {moi['kills']}")


# ============ BOUCLE PRINCIPALE ============

def jouer(strategie="chasseur", delai=0.3):
    """
    Lancer le bot
    
    strategie: 'aleatoire', 'chasseur', 'fuyard', 'sniper', 'kamikaze'
    delai: temps entre chaque action (en secondes)
    """
    print("=" * 50)
    print(f"🤖 Bot: {USERNAME}")
    print(f"🎯 Stratégie: {strategie}")
    print(f"⏱️ Délai: {delai}s")
    print("=" * 50)
    print()
    
    # Rejoindre la partie
    player_id = rejoindre()
    if not player_id:
        print("❌ Impossible de rejoindre")
        return
    
    print()
    print("🎮 Début du jeu!")
    print("   (Ctrl+C pour arrêter)")
    print()
    
    # Choisir la stratégie
    strategies = {
        'aleatoire': strategie_aleatoire,
        'chasseur': strategie_chasseur,
        'fuyard': strategie_fuyard,
        'sniper': strategie_sniper,
        'kamikaze': strategie_kamikaze
    }
    
    strategie_fn = strategies.get(strategie, strategie_chasseur)
    
    # Boucle de jeu
    erreurs_consecutives = 0
    
    while True:
        try:
            strategie_fn(player_id)
            erreurs_consecutives = 0
            time.sleep(delai)
            
        except KeyboardInterrupt:
            print("\n")
            print("=" * 50)
            print("👋 Arrêt du bot")
            print("=" * 50)
            break
            
        except Exception as e:
            erreurs_consecutives += 1
            print(f"⚠️ Erreur: {e}")
            
            if erreurs_consecutives > 5:
                print("❌ Trop d'erreurs, arrêt")
                break
            
            time.sleep(2)


# ============ LANCEMENT ============

if __name__ == "__main__":
    import sys
    
    # Récupérer la stratégie depuis les arguments
    if len(sys.argv) > 1:
        strategie = sys.argv[1]
    else:
        strategie = "chasseur"
    
    # Récupérer le délai
    if len(sys.argv) > 2:
        delai = float(sys.argv[2])
    else:
        delai = 0.3
    
    # LANCER!
    print()
    print("🎮 BATTLE ARENA - BOT EXEMPLE")
    print()
    
    jouer(strategie=strategie, delai=delai)
