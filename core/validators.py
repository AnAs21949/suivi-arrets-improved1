"""
Validation logic for production stoppage data.
Ensures data quality before database insertion.
"""
from datetime import date, time
from typing import Dict, List, Optional, Tuple
from config import SITES, BATIMENTS_PAR_SITE, SERVICES, STATUTS


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_arret(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate arrêt data before insertion.
    
    Args:
        data: Dictionary containing arrêt fields
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['site', 'date', 'heure_debut', 'heure_fin', 'client', 'service']
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Le champ '{field}' est obligatoire.")
    
    # Site validation
    if data.get('site') and data['site'] not in SITES:
        errors.append(f"Site invalide: {data['site']}. Valeurs acceptées: {SITES}")
    
    # Batiment validation (must match site)
    if data.get('site') and data.get('batiment'):
        valid_batiments = BATIMENTS_PAR_SITE.get(data['site'], [])
        if data['batiment'] not in valid_batiments:
            errors.append(
                f"Bâtiment '{data['batiment']}' invalide pour le site '{data['site']}'. "
                f"Valeurs acceptées: {valid_batiments}"
            )
    
    # Time validation
    if data.get('heure_debut') and data.get('heure_fin'):
        # Both must be time objects or strings
        try:
            debut = data['heure_debut']
            fin = data['heure_fin']
            
            # Convert strings to time if needed
            if isinstance(debut, str):
                debut = time.fromisoformat(debut)
            if isinstance(fin, str):
                fin = time.fromisoformat(fin)
            
            # Note: We allow overnight stops, so we don't error if fin < debut
            # But we might want to warn the user
            
        except (ValueError, TypeError) as e:
            errors.append(f"Format d'heure invalide: {e}")
    
    # Nombre d'équipes validation
    if data.get('nbr_equipes'):
        try:
            nbr = int(data['nbr_equipes'])
            if nbr < 1 or nbr > 3:
                errors.append("Le nombre d'équipes doit être entre 1 et 3.")
        except (ValueError, TypeError):
            errors.append("Le nombre d'équipes doit être un entier.")
    
    # Status validation
    if data.get('statut') and data['statut'] not in STATUTS:
        errors.append(f"Statut invalide: {data['statut']}. Valeurs acceptées: {STATUTS}")
    
    # Date validation (not in the future)
    if data.get('date'):
        try:
            arret_date = data['date']
            if isinstance(arret_date, str):
                arret_date = date.fromisoformat(arret_date)
            
            if arret_date > date.today():
                errors.append("La date ne peut pas être dans le futur.")
        except (ValueError, TypeError) as e:
            errors.append(f"Format de date invalide: {e}")
    
    return len(errors) == 0, errors


def validate_matrice_entry(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate productivity matrix entry.
    
    Args:
        data: Dictionary containing matrix fields
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    if not data.get('site'):
        errors.append("Le site est obligatoire.")
    
    if not data.get('client'):
        errors.append("Le client est obligatoire.")
    
    if not data.get('nbr_equipes'):
        errors.append("Le nombre d'équipes est obligatoire.")
    
    if not data.get('facteur'):
        errors.append("Le facteur est obligatoire.")
    
    # Site validation
    if data.get('site') and data['site'] not in SITES:
        errors.append(f"Site invalide: {data['site']}")
    
    # Facteur validation (must be positive)
    if data.get('facteur'):
        try:
            facteur = float(data['facteur'])
            if facteur <= 0:
                errors.append("Le facteur doit être un nombre positif.")
        except (ValueError, TypeError):
            errors.append("Le facteur doit être un nombre valide.")
    
    return len(errors) == 0, errors


def sanitize_string(value: Optional[str]) -> Optional[str]:
    """Clean and sanitize string input."""
    if value is None:
        return None
    return str(value).strip() if value else None
