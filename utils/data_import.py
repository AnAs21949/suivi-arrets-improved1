"""
Data import utilities for migrating from Excel to SQLite.
Handles parsing of legacy time formats and data cleaning.
"""
import pandas as pd
from datetime import datetime, time, date
from typing import Optional
from pathlib import Path

from data.database import get_db, init_db, seed_reference_data
from data.repository import ArretRepository, MatriceRepository, ClientRepository
from core.calculations import get_iso_week, get_month_string, calculate_duration, calculate_impact


def parse_excel_time(value) -> Optional[time]:
    """
    Parse time values from Excel which can come in various formats.
    
    Excel stores times as fractions of a day, often anchored to 1900-01-12.
    This function handles multiple formats:
    - datetime objects (1900-01-12 14:30:00)
    - time objects
    - strings ("14:30", "14:30:00", "6h00")
    - floats (fractional days)
    """
    if value is None or pd.isna(value):
        return None
    
    # Already a time object
    if isinstance(value, time):
        return value
    
    # Datetime object - extract time part
    if isinstance(value, datetime):
        return value.time()
    
    # String parsing
    if isinstance(value, str):
        value = value.strip()
        
        # Handle "6h00" format
        if 'h' in value.lower():
            parts = value.lower().replace('h', ':').split(':')
            try:
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 and parts[1] else 0
                return time(hour, minute)
            except (ValueError, IndexError):
                pass
        
        # Standard time formats
        for fmt in ['%H:%M:%S', '%H:%M', '%H:%M:%S.%f']:
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
    
    # Float (fraction of day)
    if isinstance(value, (int, float)):
        try:
            # Excel stores time as fraction of 24 hours
            total_seconds = float(value) * 24 * 3600
            hours = int(total_seconds // 3600) % 24
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            return time(hours, minutes, seconds)
        except (ValueError, OverflowError):
            pass
    
    return None


def parse_excel_date(value) -> Optional[date]:
    """Parse date values from Excel."""
    if value is None or pd.isna(value):
        return None
    
    # Handle pandas Timestamp
    if hasattr(value, 'date'):
        return value.date()
    
    if isinstance(value, date):
        return value
    
    if isinstance(value, datetime):
        return value.date()
    
    if isinstance(value, str):
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    
    return None


def clean_string(value) -> Optional[str]:
    """Clean string values, handling NaN and whitespace."""
    if value is None or pd.isna(value):
        return None
    return str(value).strip() if value else None


def import_matrice_from_excel(excel_path: str) -> int:
    """
    Import the productivity matrix from Excel.
    
    Args:
        excel_path: Path to the Excel file
        
    Returns:
        Number of records imported
    """
    df = pd.read_excel(excel_path, sheet_name="Matrice Productivité ")
    
    # The matrix has columns: Site, Client, Nbr d'équipe, and a factor column
    # Based on the data structure we saw, the relevant columns are:
    # Site, Client, Nbr d'équipe, and "Temps d'arrêt" (which is the factor)
    
    count = 0
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            site = clean_string(row.get('Site '))
            client = clean_string(row.get('Client '))
            nbr_equipes = row.get("Nbr d'équipe")
            
            # The factor column name in the Excel is "Temps d'arrêt"
            facteur = row.get("Temps d'arrêt")
            
            if site and client and nbr_equipes and facteur and not pd.isna(facteur):
                try:
                    cursor.execute(
                        """INSERT OR REPLACE INTO matrice_productivite 
                           (site, client, nbr_equipes, facteur, actif)
                           VALUES (?, ?, ?, ?, 1)""",
                        (site, client, int(nbr_equipes), float(facteur))
                    )
                    count += 1
                except Exception as e:
                    print(f"Error importing matrix row: {e}")
        
        conn.commit()
    
    return count


def import_arrets_from_excel(excel_path: str, filter_month: str = None) -> int:
    """
    Import production stoppages from Excel.
    
    Args:
        excel_path: Path to the Excel file
        filter_month: Optional month filter in format '2026-M01' to only import 
                     records from that month. If None, imports all records.
        
    Returns:
        Number of records imported
    """
    # Read the main journal sheet
    df = pd.read_excel(excel_path, sheet_name="  Journal de Bord des Arrêts")
    
    # Filter by month if specified
    if filter_month and 'Mois' in df.columns:
        df = df[df['Mois'] == filter_month].copy()
        print(f"Filtered to {len(df)} records for month {filter_month}")
    
    count = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Parse basic fields
            site = clean_string(row.get('Site '))
            batiment = clean_string(row.get('Bâtiment '))
            date_arret = parse_excel_date(row.get('Date'))
            
            heure_debut = parse_excel_time(row.get('Heure début'))
            heure_fin = parse_excel_time(row.get('Heure fin'))
            
            client = clean_string(row.get('Client '))
            nbr_equipes = row.get("Nbr d'équipe", 1)
            
            # Skip rows with missing critical data
            if not site or not date_arret or not heure_debut or not heure_fin:
                continue
            
            # Normalize site name to title case
            site = site.title()
            
            # Handle nbr_equipes
            try:
                nbr_equipes = int(nbr_equipes) if not pd.isna(nbr_equipes) else 1
            except (ValueError, TypeError):
                nbr_equipes = 1
            
            # Use duration from Excel if available, otherwise calculate
            duree = row.get('Durée en :H')
            if duree is None or pd.isna(duree):
                duree = calculate_duration(heure_debut, heure_fin)
            else:
                duree = float(duree)
            
            # Use semaine and mois from Excel if available
            semaine = clean_string(row.get('Semaine'))
            mois = clean_string(row.get('Mois'))
            if not semaine:
                semaine = get_iso_week(date_arret)
            if not mois:
                mois = get_month_string(date_arret)
            
            # Use impact from Excel if available, otherwise calculate
            impact = row.get('Impact Productivité par client')
            if impact is None or pd.isna(impact):
                impact = calculate_impact(duree, site, client, nbr_equipes)
            else:
                impact = float(impact)
            
            # Build the record
            arret_data = {
                'site': site,
                'batiment': batiment,
                'date': date_arret,
                'semaine': semaine,
                'mois': mois,
                'annee': date_arret.year,
                'heure_debut': heure_debut.strftime('%H:%M:%S'),
                'heure_fin': heure_fin.strftime('%H:%M:%S'),
                'duree_heures': duree,
                'client': client,
                'nbr_equipes': nbr_equipes,
                'impact_pct': impact,
                'processus': clean_string(row.get('Processus')),
                'poste_machine': clean_string(row.get('Poste/Machine')),
                'service': clean_string(row.get('Service')),
                'description': clean_string(row.get('Description')),
                'reference': clean_string(row.get('Référence')),
                'demandeur': clean_string(row.get('Demandeur ')),
                'equipe': clean_string(row.get('Équipe')),
                'traite_par': clean_string(row.get('Traité par')),
                'statut': 'Résolu'  # Historical data is assumed resolved
            }
            
            # Insert into database
            ArretRepository.create(arret_data)
            count += 1
            
            # Also ensure client exists in clients table
            if client:
                ClientRepository.create(client)
                
        except Exception as e:
            errors.append(f"Row {idx}: {e}")
            continue
    
    if errors:
        print(f"Import completed with {len(errors)} errors:")
        for err in errors[:10]:  # Show first 10 errors
            print(f"  - {err}")
    
    return count


def import_all_from_excel(excel_path: str, filter_month: str = None) -> dict:
    """
    Import all data from the Excel file.
    
    Args:
        excel_path: Path to the Excel file
        filter_month: Optional month filter (e.g., '2026-M01')
        
    Returns:
        Dictionary with import statistics
    """
    # Initialize database first
    init_db()
    seed_reference_data()
    
    stats = {
        'matrice_count': 0,
        'arrets_count': 0,
        'errors': []
    }
    
    try:
        # Import productivity matrix first (needed for impact calculations)
        stats['matrice_count'] = import_matrice_from_excel(excel_path)
        print(f"Imported {stats['matrice_count']} matrix entries")
        
        # Import arrêts
        stats['arrets_count'] = import_arrets_from_excel(excel_path, filter_month)
        print(f"Imported {stats['arrets_count']} arrêts")
        
    except Exception as e:
        stats['errors'].append(str(e))
        print(f"Import error: {e}")
    
    return stats


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_import.py <excel_file_path> [month_filter]")
        print("Example: python data_import.py data.xlsx 2026-M01")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    filter_month = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(excel_path).exists():
        print(f"File not found: {excel_path}")
        sys.exit(1)
    
    print(f"Importing from: {excel_path}")
    if filter_month:
        print(f"Filtering for month: {filter_month}")
    
    stats = import_all_from_excel(excel_path, filter_month)
    print(f"\nImport complete!")
    print(f"  - Matrix entries: {stats['matrice_count']}")
    print(f"  - Arrêts: {stats['arrets_count']}")
