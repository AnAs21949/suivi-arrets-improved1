# Cahier de Charge
## Application Suivi des Arrêts Production

**Version:** 1.0
**Date:** 30 Janvier 2026
**Auteur:** [Votre nom]
**Société:** Eolane

---

## 1. Présentation du Projet

### 1.1 Contexte

Dans le cadre de l'amélioration continue de la production, il est nécessaire de disposer d'un outil de suivi des arrêts de production permettant d'identifier les causes, mesurer l'impact et suivre les tendances.

### 1.2 Objectif

Développement et déploiement d'une application web interne permettant :
- La saisie des arrêts de production
- Le calcul automatique de l'impact sur la productivité
- L'analyse des données via des tableaux de bord
- Le suivi historique des arrêts

### 1.3 Périmètre

| Élément | Détail |
|---------|--------|
| **Nom de l'application** | Suivi des Arrêts Production (CICOR) |
| **Sites concernés** | Berrechid, Temara |
| **Utilisateurs cibles** | Production, Maintenance, Qualité, Supply, IT |
| **Nombre d'utilisateurs estimé** | 10-30 utilisateurs |

---

## 2. Description Fonctionnelle

### 2.1 Modules de l'Application

#### Module 1 : Tableau de Bord KPI
- Affichage des indicateurs clés (heures d'arrêt, impact productivité, nombre d'arrêts, durée moyenne)
- Graphiques interactifs (Pareto par service, évolution temporelle)
- Filtres par site, période, service
- Comparaison avec périodes précédentes

#### Module 2 : Saisie des Arrêts
- Formulaire de saisie avec champs : date, site, bâtiment, client, horaires, service responsable, description
- Calcul automatique de la durée et de l'impact
- Gestion des arrêts de nuit (passage minuit)
- Validation des données

#### Module 3 : Journal de Bord
- Liste historique de tous les arrêts
- Filtres multicritères (date, site, service, client, statut)
- Recherche textuelle
- Modification et suppression des enregistrements
- Export des données

#### Module 4 : Administration
- Gestion de la matrice de productivité
- Gestion des clients
- Statistiques système
- Maintenance de la base de données

### 2.2 Flux de Données

```
Utilisateur → Saisie Arrêt → Validation → Base de Données → Tableau de Bord
                                              ↓
                                         Export Excel/PPT
```

---

## 3. Spécifications Techniques

### 3.1 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION                           │
├─────────────────────────────────────────────────────────┤
│  Interface Web (Streamlit)                              │
├─────────────────────────────────────────────────────────┤
│  Logique Métier (Python)                                │
│  - Calculs (durée, impact, semaines ISO)                │
│  - Validation des données                               │
├─────────────────────────────────────────────────────────┤
│  Couche Données (Repository Pattern)                    │
├─────────────────────────────────────────────────────────┤
│  Base de Données (SQLite)                               │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Stack Technique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| Langage | Python | 3.10+ | Langage principal |
| Framework Web | Streamlit | 1.31.0+ | Interface utilisateur |
| Base de données | SQLite | 3.x | Stockage des données |
| Visualisation | Plotly | 5.18.0+ | Graphiques interactifs |
| Manipulation données | Pandas | 2.0.0+ | Traitement des données |
| Export Excel | openpyxl | 3.1.0+ | Génération fichiers Excel |
| Export PowerPoint | python-pptx | 0.6.21+ | Génération présentations |

### 3.3 Structure du Projet

```
suivi-arrets-improved1/
├── app.py                    # Point d'entrée principal
├── config.py                 # Configuration (sites, services, couleurs)
├── requirements.txt          # Dépendances Python
├── core/                     # Logique métier
│   ├── calculations.py       # Calculs (durée, impact)
│   └── validators.py         # Validation des données
├── data/                     # Couche données
│   ├── database.py           # Initialisation base de données
│   └── repository.py         # Opérations CRUD
├── pages/                    # Pages de l'interface
│   ├── dashboard.py          # Tableau de bord KPI
│   ├── saisie.py             # Formulaire de saisie
│   ├── journal.py            # Journal historique
│   └── admin.py              # Administration
├── db/
│   └── arrets.db             # Base de données SQLite
└── .streamlit/
    └── config.toml           # Configuration thème
```

### 3.4 Modèle de Données

#### Table principale : `arrets`

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Identifiant unique (auto) |
| date | DATE | Date de l'arrêt |
| semaine | TEXT | Semaine ISO (ex: 2026-S04) |
| mois | TEXT | Mois (ex: Janvier 2026) |
| annee | INTEGER | Année |
| site | TEXT | Site (Berrechid/Temara) |
| batiment | TEXT | Bâtiment |
| client | TEXT | Client concerné |
| heure_debut | TIME | Heure de début |
| heure_fin | TIME | Heure de fin |
| duree_heures | REAL | Durée en heures |
| nbr_equipes | INTEGER | Nombre d'équipes |
| impact_pct | REAL | Impact en pourcentage |
| service | TEXT | Service responsable |
| sous_famille | TEXT | Sous-famille |
| processus | TEXT | Processus concerné |
| poste_machine | TEXT | Poste/Machine |
| description | TEXT | Description de l'arrêt |
| reference | TEXT | Référence produit |
| demandeur | TEXT | Demandeur |
| equipe | TEXT | Équipe (Matin/APM/Nuit) |
| traite_par | TEXT | Traité par |
| statut | TEXT | Statut (Ouvert/En cours/Résolu) |
| created_at | DATETIME | Date de création |
| updated_at | DATETIME | Date de modification |

#### Tables de référence

- `matrice_productivite` : Facteurs de productivité par site/client/équipes
- `sites` : Liste des sites
- `batiments` : Liste des bâtiments par site
- `clients` : Liste des clients
- `services` : Liste des services

---

## 4. Besoins Infrastructure

### 4.1 Serveur / Machine Virtuelle

| Ressource | Minimum | Recommandé |
|-----------|---------|------------|
| **Système d'exploitation** | Windows 10/11 ou Ubuntu 20.04+ | Windows Server 2019+ ou Ubuntu 22.04 |
| **Processeur** | 2 cores | 4 cores |
| **Mémoire RAM** | 4 Go | 8 Go |
| **Stockage** | 10 Go | 20 Go SSD |
| **Python** | 3.10 | 3.11+ |

### 4.2 Réseau

| Élément | Valeur |
|---------|--------|
| **Port applicatif** | 8501 (TCP) |
| **Protocole** | HTTP |
| **Accès requis** | Réseau interne uniquement |
| **IP** | Statique (recommandé) |
| **DNS interne (optionnel)** | suivi-arrets.eolane.com |

### 4.3 Pare-feu

Règle à ajouter :
- **Source** : Réseau interne (10.100.0.0/16 ou selon configuration)
- **Destination** : IP du serveur
- **Port** : 8501
- **Protocole** : TCP
- **Action** : Autoriser

---

## 5. Installation et Déploiement

### 5.1 Installation des Prérequis

```bash
# Vérifier la version de Python
python --version  # Doit être 3.10+

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 5.2 Lancement de l'Application

```bash
# Lancement standard
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Ou avec l'IP spécifique du serveur
streamlit run app.py --server.address <IP_SERVEUR> --server.port 8501
```

### 5.3 Configuration Service (Linux - systemd)

Fichier `/etc/systemd/system/suivi-arrets.service` :

```ini
[Unit]
Description=Suivi Arrets Production
After=network.target

[Service]
Type=simple
User=<utilisateur>
WorkingDirectory=/chemin/vers/suivi-arrets-improved1
ExecStart=/chemin/vers/venv/bin/python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Commandes :
```bash
sudo systemctl enable suivi-arrets
sudo systemctl start suivi-arrets
sudo systemctl status suivi-arrets
```

### 5.4 Configuration Service (Windows)

Utiliser NSSM (Non-Sucking Service Manager) ou le Planificateur de tâches Windows pour lancer l'application au démarrage.

---

## 6. Sécurité

### 6.1 Niveau de Sensibilité des Données

| Type de données | Sensibilité | Présent dans l'application |
|-----------------|-------------|---------------------------|
| Données personnelles | Haute | Non |
| Données financières | Haute | Non |
| Données de production | Moyenne | Oui |
| Données clients (noms) | Basse | Oui (noms uniquement) |

### 6.2 Mesures de Sécurité

- **Accès réseau interne uniquement** : Pas d'exposition sur Internet
- **Base de données locale** : Fichier SQLite, pas de serveur de base de données externe
- **Pas de données sensibles** : Uniquement données opérationnelles de production
- **Authentification** : Non implémentée actuellement (accès libre en interne)

### 6.3 Recommandations Futures

- Ajout d'une authentification (LDAP/Active Directory)
- Mise en place HTTPS avec certificat interne
- Journalisation des accès

---

## 7. Maintenance

### 7.1 Sauvegarde

| Élément | Fichier | Fréquence |
|---------|---------|-----------|
| Base de données | `db/arrets.db` | Quotidienne |
| Configuration | `config.py`, `.streamlit/config.toml` | Hebdomadaire |
| Code source | Dossier complet | À chaque modification |

Script de sauvegarde exemple :
```bash
# Linux
cp /chemin/vers/db/arrets.db /backup/arrets_$(date +%Y%m%d).db

# Windows (PowerShell)
Copy-Item "C:\chemin\vers\db\arrets.db" "C:\backup\arrets_$(Get-Date -Format 'yyyyMMdd').db"
```

### 7.2 Surveillance

- Vérifier que le service est actif
- Surveiller l'espace disque
- Vérifier les logs en cas d'erreur

### 7.3 Mises à Jour

| Tâche | Fréquence |
|-------|-----------|
| Mise à jour dépendances Python | Trimestrielle |
| Mise à jour OS / sécurité | Selon politique IT |
| Sauvegarde avant mise à jour | Systématique |

---

## 8. Support et Contact

| Rôle | Nom | Contact |
|------|-----|---------|
| Développeur | [Votre nom] | [Votre email] |
| Responsable métier | [Nom] | [Email] |
| Support IT | Service Informatique | [Email IT] |

---

## 9. Annexes

### Annexe A : Dépendances Python (requirements.txt)

```
streamlit>=1.31.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
python-pptx>=0.6.21
```

### Annexe B : Captures d'Écran

[Ajouter des captures d'écran de l'application]

- Tableau de bord KPI
- Formulaire de saisie
- Journal de bord
- Page administration

### Annexe C : Glossaire

| Terme | Définition |
|-------|------------|
| Arrêt de production | Interruption non planifiée de la ligne de production |
| Impact productivité | Pourcentage de perte de productivité calculé selon la matrice |
| Matrice de productivité | Table de référence des facteurs de calcul par site/client/équipes |
| Semaine ISO | Numérotation des semaines selon la norme ISO 8601 |

---

*Document généré le 30 Janvier 2026*
