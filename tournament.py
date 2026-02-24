"""
Mode Tournoi - Battle Arena
Lancer avec : python tournament.py

Ce script remplace main.py pour activer le mode tournoi.
Il patch le GameEngine pour :
- N'autoriser que les joueurs de la whitelist
- Limiter les respawns à MAX_RESPAWNS par joueur
- Sauvegarder et afficher un classement persistant
"""

import json
import os
import time
import uvicorn
from engine import GameEngine
from main import app

# ==================== CONFIG TOURNOI ====================

TOURNAMENT_FILE = "tournament_scores.json"
MAX_RESPAWNS = 10

WHITELIST = [
    "bot_alice",
    "bot_bob",
    "bot_charlie",
    # Ajoute ici les usernames autorisés
]

# ==================== PATCH DU GAME ENGINE ====================

_original_join = GameEngine.join_game
_original_death = GameEngine._handle_player_death


def _tournament_join(self, username: str) -> dict:
    # Check whitelist
    if username not in WHITELIST:
        return {"success": False, "error": "Tournament mode: username not whitelisted"}

    # Check respawns restants
    scores = _load_scores()
    respawns_used = scores.get(username, {}).get("deaths", 0)
    if respawns_used >= MAX_RESPAWNS:
        return {"success": False, "error": f"Tournament over for {username}: {MAX_RESPAWNS} respawns used"}

    return _original_join(self, username)


def _tournament_death(self, player_id: str, killer_id: str):
    player = self.players.get(player_id)
    killer = self.players.get(killer_id)

    # Appel original
    _original_death(self, player_id, killer_id)

    # Mise à jour scores tournoi
    if player:
        scores = _load_scores()

        # Victime
        if player.username not in scores:
            scores[player.username] = {"kills": 0, "deaths": 0}
        scores[player.username]["deaths"] += 1

        # Tueur
        if killer:
            if killer.username not in scores:
                scores[killer.username] = {"kills": 0, "deaths": 0}
            scores[killer.username]["kills"] += 1

        _save_scores(scores)
        _print_leaderboard(scores)


# Appliquer les patches
GameEngine.join_game = _tournament_join
GameEngine._handle_player_death = _tournament_death


# ==================== PERSISTANCE SCORES ====================

def _load_scores() -> dict:
    if os.path.exists(TOURNAMENT_FILE):
        try:
            with open(TOURNAMENT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_scores(scores: dict):
    try:
        with open(TOURNAMENT_FILE, "w") as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde tournoi: {e}")


def _print_leaderboard(scores: dict):
    print("\n🏆 CLASSEMENT TOURNOI")
    print(f"{'Joueur':<20} {'Kills':>6} {'Deaths':>8} {'Respawns restants':>18}")
    print("-" * 56)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["kills"], reverse=True)
    for username, s in sorted_scores:
        remaining = MAX_RESPAWNS - s["deaths"]
        status = "❌ ÉLIMINÉ" if remaining <= 0 else f"{remaining} restants"
        print(f"{username:<20} {s['kills']:>6} {s['deaths']:>8} {status:>18}")
    print()


# ==================== LANCEMENT ====================

if __name__ == "__main__":
    import config

    print("🏆 Mode TOURNOI activé")
    print(f"   Whitelist: {', '.join(WHITELIST)}")
    print(f"   Respawns max: {MAX_RESPAWNS}")
    print()

    scores = _load_scores()
    if scores:
        print("📊 Scores existants chargés :")
        _print_leaderboard(scores)
    else:
        print("📊 Nouveau tournoi — aucun score existant\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.SERVER_PORT,
        log_level="info"
    )
