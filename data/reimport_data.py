"""
Script to reimport data from Excel with sous_famille field.
Run this once after updating database.py

Usage: python reimport_data.py path/to/excel_file.xlsx
"""
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "db" / "arrets.db"

def reimport_from_excel(excel_path):
    """Reimport all data from Excel file including sous_famille."""
    
    print(f"Reading Excel file: {excel_path}")
    df = pd.read_excel(excel_path, sheet_name='  Journal de Bord des Arrêts')
    
    # Clean column names
    df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
    
    print(f"Found {len(df)} records")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add sous_famille column if missing
    try:
        cursor.execute("ALTER TABLE arrets ADD COLUMN sous_famille TEXT")
        print("Added sous_famille column")
    except sqlite3.OperationalError:
        print("sous_famille column already exists")
    
    # Clear existing data
    cursor.execute("DELETE FROM arrets")
    print("Cleared existing data")
    
    # Insert new data
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO arrets (
                    site, batiment, date, semaine, mois, annee,
                    heure_debut, heure_fin, duree_heures,
                    client, nbr_equipes, impact_pct,
                    processus, poste_machine, service, sous_famille,
                    description, reference, demandeur, equipe, traite_par, statut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get('Site', ''),
                row.get('Bâtiment', ''),
                pd.to_datetime(row.get('Date')).strftime('%Y-%m-%d') if pd.notna(row.get('Date')) else None,
                row.get('Semaine', ''),
                row.get('Mois', ''),
                row.get('Année', None),
                str(row.get('Heure début', ''))[:8] if pd.notna(row.get('Heure début')) else None,
                str(row.get('Heure fin', ''))[:8] if pd.notna(row.get('Heure fin')) else None,
                row.get('Durée en :H', 0),
                row.get('Client', ''),
                row.get("Nbr d'équipe", 1),
                row.get('Impact Productivité par client', 0),
                row.get('Processus', ''),
                row.get('Poste/Machine', ''),
                row.get('Service', ''),
                row.get('Sous-Famille Précise', ''),  # NEW FIELD
                row.get('Description', ''),
                row.get('Référence', ''),
                row.get('Demandeur', ''),
                row.get('Équipe', ''),
                row.get('Traité par', ''),
                'Résolu'
            ))
            inserted += 1
        except Exception as e:
            print(f"Error inserting row: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully imported {inserted} records with sous_famille field!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reimport_data.py path/to/excel_file.xlsx")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    reimport_from_excel(excel_path)
