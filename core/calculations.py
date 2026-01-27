"""
Business logic calculations for production stoppages.
Handles duration, ISO week, and productivity impact calculations.
"""
from datetime import datetime, date, time, timedelta
from typing import Optional, Tuple
from data.repository import MatriceRepository


def calculate_duration(heure_debut: time, heure_fin: time) -> float:
    """
    Calculate the duration between two times in hours.
    Handles overnight stops (when end time is before start time).
    
    Args:
        heure_debut: Start time of the stoppage
        heure_fin: End time of the stoppage
        
    Returns:
        Duration in hours as a float (e.g., 6.5 for 6 hours 30 minutes)
    """
    # Convert times to datetime for calculation (using a reference date)
    ref_date = date(2000, 1, 1)
    dt_debut = datetime.combine(ref_date, heure_debut)
    dt_fin = datetime.combine(ref_date, heure_fin)
    
    # Handle overnight stops (end time is "before" start time)
    if dt_fin <= dt_debut:
        # Add one day to end time
        dt_fin += timedelta(days=1)
    
    # Calculate difference
    delta = dt_fin - dt_debut
    hours = delta.total_seconds() / 3600
    
    return round(hours, 2)


def is_overnight_stop(heure_debut: time, heure_fin: time) -> bool:
    """Check if a stop crosses midnight."""
    ref_date = date(2000, 1, 1)
    dt_debut = datetime.combine(ref_date, heure_debut)
    dt_fin = datetime.combine(ref_date, heure_fin)
    return dt_fin <= dt_debut


def get_iso_week(dt: date) -> str:
    """
    Get ISO week string in format 'YYYY-SWW'.
    
    Args:
        dt: Date to convert
        
    Returns:
        String like '2026-S04' for week 4 of 2026
    """
    iso_cal = dt.isocalendar()
    return f"{iso_cal[0]}-S{iso_cal[1]:02d}"


def get_month_string(dt: date) -> str:
    """
    Get month string in format 'YYYY-MMM'.
    
    Args:
        dt: Date to convert
        
    Returns:
        String like '2026-M01' for January 2026
    """
    return f"{dt.year}-M{dt.month:02d}"


def calculate_impact(
    duree_heures: float,
    site: str,
    client: str,
    nbr_equipes: int
) -> Optional[float]:
    """
    Calculate productivity impact percentage.
    
    The formula is: Impact% = Duration(h) / Facteur
    where Facteur comes from the productivity matrix lookup.
    
    Args:
        duree_heures: Duration of stoppage in hours
        site: Site name (Berrechid or Temara)
        client: Client name
        nbr_equipes: Number of teams/shifts
        
    Returns:
        Impact percentage as a float, or None if no matrix entry exists
    """
    facteur = MatriceRepository.get_facteur(site, client, nbr_equipes)
    
    if facteur is None or facteur == 0:
        return None
    
    impact = duree_heures / facteur
    return round(impact, 6)


def prepare_arret_data(
    site: str,
    batiment: str,
    date_arret: date,
    heure_debut: time,
    heure_fin: time,
    client: str,
    nbr_equipes: int,
    service: str,
    description: str,
    processus: Optional[str] = None,
    poste_machine: Optional[str] = None,
    reference: Optional[str] = None,
    demandeur: Optional[str] = None,
    equipe: Optional[str] = None,
    traite_par: Optional[str] = None,
    statut: str = "Ouvert"
) -> dict:
    """
    Prepare complete arrêt data with all calculated fields.
    
    This function takes raw input and enriches it with:
    - Calculated duration
    - ISO week string
    - Month string  
    - Year
    - Impact percentage (if matrix entry exists)
    
    Args:
        All the fields from the input form
        
    Returns:
        Dictionary ready for database insertion
    """
    # Calculate derived fields
    duree = calculate_duration(heure_debut, heure_fin)
    semaine = get_iso_week(date_arret)
    mois = get_month_string(date_arret)
    annee = date_arret.year
    impact = calculate_impact(duree, site, client, nbr_equipes)
    
    return {
        'site': site,
        'batiment': batiment,
        'date': date_arret,
        'semaine': semaine,
        'mois': mois,
        'annee': annee,
        'heure_debut': heure_debut.strftime('%H:%M:%S'),
        'heure_fin': heure_fin.strftime('%H:%M:%S'),
        'duree_heures': duree,
        'client': client,
        'nbr_equipes': nbr_equipes,
        'impact_pct': impact,
        'processus': processus,
        'poste_machine': poste_machine,
        'service': service,
        'description': description,
        'reference': reference,
        'demandeur': demandeur,
        'equipe': equipe,
        'traite_par': traite_par,
        'statut': statut
    }


def get_week_boundaries(semaine: str) -> Tuple[date, date]:
    """
    Get the start and end dates for an ISO week string.
    
    Args:
        semaine: ISO week string like '2026-S04'
        
    Returns:
        Tuple of (start_date, end_date) for that week
    """
    # Parse the week string
    parts = semaine.split('-S')
    year = int(parts[0])
    week = int(parts[1])
    
    # Get first day of the week (Monday)
    first_day = datetime.strptime(f'{year}-W{week:02d}-1', '%G-W%V-%u').date()
    last_day = first_day + timedelta(days=6)
    
    return first_day, last_day


def get_current_week() -> str:
    """Get the current ISO week string."""
    return get_iso_week(date.today())


def get_previous_week() -> str:
    """Get the previous ISO week string."""
    last_week = date.today() - timedelta(days=7)
    return get_iso_week(last_week)
