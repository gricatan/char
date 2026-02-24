# Battle Arena – ROADMAP

## 1. Feature : Rebond de balle sur les blocs (obstacles)

**Objectif** : Les balles ne traversent plus les obstacles → elles rebondissent.  
Ça rend le jeu beaucoup plus stratégique (utilisation des murs, ricochets, skill shots).

**Description technique (texte)** :
- Détection collision balle ↔ obstacle
- Inversion de la vitesse horizontale OU verticale selon le côté touché
- Légère perte d’énergie optionnelle (0.95x)
- Limite max rebonds par balle (ex: 3) pour éviter les loops infinis
- Impact sur le gameplay : combat plus fluide, maps plus intéressantes


---

## 2. Système Tournoi (mode optionnel & amiable)

**Description** :
Un mode spécial "tournament" qui s’active/désactive sans casser le serveur normal.

**Fonctionnalités clés**
- Liste blanche (whitelist) de participants autorisés (usernames)
- Limitation à 10 respawns maximum par bot (au lieu d’infini)
- Une seule variable ou flag pour activer/désactiver tout le mode tournoi
- Quand le mode est OFF → serveur normal (respawns infinis, tout le monde peut rejoindre)
- Quand le mode est ON → seuls les bots de la whitelist peuvent jouer + respawns limités à 10
- Le lancement se fait via un script dédié (optionnel) ou via une variable d’environnement

**Avantages**
- Ultra simple à activer/désactiver (changer une ligne ou lancer un autre fichier)
- Aucune modification permanente du code principal
- Parfait pour les events sans perturber les joueurs lambda

**Fichiers concernés (texte)**
- Nouvelle config tournament
- Modification légère dans Player (compteur respawns)
- Check whitelist dans l’endpoint /join
- Script de lancement dédié (à la racine)

---
