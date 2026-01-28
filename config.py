"""
Configuration settings for the Suivi des Arrêts Production application.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database
DB_PATH = BASE_DIR / "db" / "arrets.db"

# Application settings
APP_NAME = "CICOR - Suivi des Arrêts Production"
APP_VERSION = "1.0.0"

# Sites configuration
SITES = ["Berrechid", "Temara"]

BATIMENTS_PAR_SITE = {
    "Berrechid": ["Bât A", "Bât B"],
    "Temara": ["TEM"]
}

# Services (départements responsables) - matching actual data
SERVICES = [
    "Maintenance",
    "Technique",
    "Supply",
    "IT",
    "Production",
    "Formation",
    "Organisation",
    "Achat",
    "Qualité",
    "Visite"
]

# Colors for services (for consistent charts) - both upper and mixed case
SERVICE_COLORS = {
    # Uppercase
    "MAINTENANCE": "#FF6B35",
    "TECHNIQUE": "#3B82F6",
    "SUPPLY": "#10B981",
    "IT": "#F59E0B",
    "PRODUCTION": "#8B5CF6",
    "FORMATION": "#EC4899",
    "ORGANISATION": "#EF4444",
    "ACHAT": "#06B6D4",
    "QUALITÉ": "#6366F1",
    "VISITE": "#14B8A6",
    # Mixed case (as in database)
    "Maintenance": "#FF6B35",
    "Technique": "#3B82F6",
    "Supply": "#10B981",
    "Production": "#8B5CF6",
    "Formation": "#EC4899",
    "Organisation": "#EF4444",
    "Achat": "#06B6D4",
    "Qualité": "#6366F1",
    "Visite": "#14B8A6",
    
    "Maintenance": "#FF6B35",
    "Technique": "#3B82F6",
    "Supply": "#10B981",
    "It": "#F59E0B",           # ✅ AJOUTÉ !
    "Production": "#8B5CF6",
    "Formation": "#EC4899",
    "Organisation": "#EF4444",
    "Achat": "#06B6D4",
    "Qualité": "#6366F1",
    "Visite": "#14B8A6",
}

# Équipes (shifts)
EQUIPES = ["Matin", "APM", "Nuit", "Normale"]

# Nombre d'équipes pour la matrice
NBR_EQUIPES_OPTIONS = [1, 2, 3]

# Processus de production
PROCESSUS = [
    "CMS",
    "Traversant",
    "Insertion",
    "Test",
    "Intégration",
    "Fermeture ultrason",
    "Sertissage grosse section",
    "Autre"
]

# Statuts d'un arrêt
STATUTS = ["Ouvert", "En cours", "Résolu"]

# Date format
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Pagination
ITEMS_PER_PAGE = 20
