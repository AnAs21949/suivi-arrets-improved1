"""
Script pour ajouter la colonne sous_famille à la base de données
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Chemins - utiliser des chemins absolus basés sur la racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / 'db' / 'arrets.db'
EXCEL_PATH = PROJECT_ROOT / 'Suivi des arrêts production Berrechid 30-01-2026.xlsx'

def add_sous_famille_column():
    """Ajoute la colonne sous_famille si elle n'existe pas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Ajouter la colonne
        cursor.execute("ALTER TABLE arrets ADD COLUMN sous_famille TEXT")
        print("✅ Colonne 'sous_famille' ajoutée avec succès")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️  Colonne 'sous_famille' existe déjà")
        else:
            raise e
    
    conn.close()

def update_sous_famille_from_excel():
    """Met à jour les valeurs de sous_famille depuis l'Excel"""
    # Lire l'Excel
    df_excel = pd.read_excel(EXCEL_PATH)
    
    # Nettoyer les noms de colonnes
    df_excel.columns = df_excel.columns.str.strip()
    
    print(f"📊 Données Excel : {len(df_excel)} lignes")
    
    # Connexion à la DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Debug: afficher les colonnes disponibles
    print(f"📋 Colonnes Excel: {list(df_excel.columns)}")

    # Debug: afficher un exemple de données DB
    cursor.execute("SELECT date, heure_debut, site FROM arrets LIMIT 3")
    print(f"📋 Exemple DB: {cursor.fetchall()}")

    # Pour chaque ligne de l'Excel, mettre à jour la DB
    updated = 0
    checked = 0
    for idx, row in df_excel.iterrows():
        if pd.notna(row.get('Sous-Famille Précise')):
            checked += 1
            # Identifier la ligne par date + heure_debut + site
            date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
            heure_debut = str(row['Heure début'])
            site = str(row['Site']).strip()
            sous_famille = str(row['Sous-Famille Précise']).strip()

            # Debug: afficher les premières tentatives
            if checked <= 3:
                print(f"🔍 Recherche: date={date}, heure={heure_debut}, site={site}")

            cursor.execute("""
                UPDATE arrets
                SET sous_famille = ?
                WHERE date = ? AND heure_debut = ? AND site = ?
            """, (sous_famille, date, heure_debut, site))

            if cursor.rowcount > 0:
                updated += 1

    print(f"📊 {checked} lignes avec sous_famille dans Excel")
    
    conn.commit()
    conn.close()
    
    print(f"✅ {updated} lignes mises à jour avec sous_famille")

if __name__ == "__main__":
    print("🔧 Ajout de la colonne sous_famille...")
    add_sous_famille_column()
    
    print("\n📥 Importation des données depuis Excel...")
    update_sous_famille_from_excel()
    
    print("\n✅ Terminé ! La colonne sous_famille est prête à être utilisée.")