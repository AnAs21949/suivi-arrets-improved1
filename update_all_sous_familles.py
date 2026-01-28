"""
Script pour mettre à jour TOUTES les sous-familles depuis l'Excel vers la base de données
"""
import sqlite3
import pandas as pd
from datetime import datetime

# Chemins
EXCEL_FILE = "Suivi des arrêts production Berrechid 27-01-2026.xlsx"
DB_FILE = "db/arrets.db"

def update_all_sous_familles():
    """Met à jour toutes les sous-familles depuis l'Excel"""
    
    # Lire l'Excel
    print("📂 Lecture du fichier Excel...")
    df = pd.read_excel(EXCEL_FILE)
    
    # Nettoyer les noms de colonnes
    df.columns = df.columns.str.strip()
    
    print(f"✅ {len(df)} lignes trouvées dans l'Excel")
    
    # Connexion à la base de données
    print("\n🔌 Connexion à la base de données...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Vérifier que la colonne sous_famille existe
    cursor.execute("PRAGMA table_info(arrets)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'sous_famille' not in columns:
        print("❌ La colonne 'sous_famille' n'existe pas dans la base de données !")
        print("   Exécute d'abord: ALTER TABLE arrets ADD COLUMN sous_famille TEXT")
        conn.close()
        return
    
    # Stratégie : matcher par date + site + durée
    print("\n🔄 Mise à jour des sous-familles...")
    
    updated = 0
    not_found = 0
    
    for idx, row in df.iterrows():
        sous_famille = row.get('Sous-Famille Précise')
        
        if pd.isna(sous_famille):
            continue
        
        # Extraire les données de correspondance
        try:
            date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
            site = str(row['Site']).strip()
            duree = float(row['Durée en :H'])
            service = str(row['Service']).strip().upper()
            
            # Chercher dans la base de données
            cursor.execute("""
                SELECT id FROM arrets 
                WHERE date = ? 
                AND UPPER(site) = UPPER(?)
                AND ABS(duree_heures - ?) < 0.01
                AND UPPER(service) = ?
                AND (sous_famille IS NULL OR sous_famille = '')
            """, (date, site, duree, service))
            
            result = cursor.fetchone()
            
            if result:
                arret_id = result[0]
                cursor.execute("""
                    UPDATE arrets 
                    SET sous_famille = ? 
                    WHERE id = ?
                """, (sous_famille, arret_id))
                updated += 1
                print(f"  ✅ Ligne {idx+1}: {sous_famille[:50]} → ID {arret_id}")
            else:
                not_found += 1
                
        except Exception as e:
            print(f"  ⚠️ Erreur ligne {idx+1}: {e}")
            continue
    
    # Commit
    conn.commit()
    
    # Statistiques finales
    print(f"\n" + "="*60)
    print(f"✅ {updated} arrêts mis à jour avec leur sous-famille")
    print(f"⚠️ {not_found} arrêts non trouvés (déjà à jour ou non correspondants)")
    print("="*60)
    
    # Vérification
    cursor.execute("SELECT COUNT(*) FROM arrets WHERE sous_famille IS NOT NULL AND sous_famille != ''")
    total_with_sf = cursor.fetchone()[0]
    print(f"\n📊 Total d'arrêts avec sous-famille dans la base: {total_with_sf}")
    
    # Répartition par service
    print("\n📊 Répartition par service:")
    cursor.execute("""
        SELECT service, COUNT(*) 
        FROM arrets 
        WHERE sous_famille IS NOT NULL AND sous_famille != ''
        GROUP BY service
        ORDER BY COUNT(*) DESC
    """)
    for service, count in cursor.fetchall():
        print(f"  - {service}: {count} arrêts")
    
    conn.close()
    print("\n✅ Terminé !")

if __name__ == "__main__":
    update_all_sous_familles()
