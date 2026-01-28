"""
Script pour identifier le dernier arrêt problématique
"""
import sqlite3
import pandas as pd

DB_FILE = "db/arrets.db"
EXCEL_FILE = "Suivi des arrêts production Berrechid 27-01-2026.xlsx"

def find_last_problematic_arret():
    """Trouve l'arrêt SUPPLY avec 'Arrêt énergie général'"""
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("🔍 Recherche de l'arrêt SUPPLY restant...\n")
    
    # Trouver l'arrêt SUPPLY
    cursor.execute("""
        SELECT id, date, site, duree_heures, description, service
        FROM arrets 
        WHERE sous_famille = 'Arrêt énergie général'
        AND UPPER(service) = 'SUPPLY'
    """)
    
    result = cursor.fetchone()
    
    if result:
        arret_id, date, site, duree, description, service = result
        print(f"❌ Arrêt trouvé:")
        print(f"   ID: {arret_id}")
        print(f"   Date: {date}")
        print(f"   Site: {site}")
        print(f"   Durée: {duree}h")
        print(f"   Service: {service}")
        print(f"   Description: {description}")
        print()
        
        # Chercher dans l'Excel
        print("📂 Recherche dans l'Excel...\n")
        df = pd.read_excel(EXCEL_FILE)
        df.columns = df.columns.str.strip()
        
        # Convertir la date
        date_obj = pd.to_datetime(date).date()
        
        # Chercher les arrêts du même jour avec durée similaire
        df['Date_obj'] = pd.to_datetime(df['Date']).dt.date
        matches = df[(df['Date_obj'] == date_obj) & 
                     (abs(df['Durée en :H'] - duree) < 0.1)]
        
        if len(matches) > 0:
            print(f"✅ Trouvé {len(matches)} arrêt(s) correspondant(s) dans l'Excel:\n")
            for idx, row in matches.iterrows():
                print(f"   Service: {row['Service']}")
                print(f"   Sous-Famille: {row['Sous-Famille Précise']}")
                print(f"   Durée: {row['Durée en :H']}h")
                print(f"   Description: {row['Description'][:60]}")
                print()
            
            # Déterminer la correction
            correct_row = matches.iloc[0]
            correct_service = correct_row['Service']
            correct_sf = correct_row['Sous-Famille Précise']
            
            print("="*70)
            print("💡 CORRECTION NÉCESSAIRE:")
            print(f"   ID {arret_id} devrait être:")
            print(f"   Service: {correct_service}")
            print(f"   Sous-Famille: {correct_sf}")
            print("="*70)
            
            # Proposer la correction
            response = input("\n❓ Appliquer cette correction ? (o/n): ")
            if response.lower() == 'o':
                cursor.execute("""
                    UPDATE arrets 
                    SET service = ?, sous_famille = ?
                    WHERE id = ?
                """, (correct_service, correct_sf, arret_id))
                conn.commit()
                print(f"\n✅ ID {arret_id} corrigé!")
            else:
                print("\n⏭️ Correction annulée")
        else:
            print(f"❌ Aucun arrêt correspondant trouvé dans l'Excel")
            print(f"   Vérification manuelle nécessaire")
    else:
        print("✅ Aucun arrêt SUPPLY trouvé avec 'Arrêt énergie général'")
        print("   Tout est correct!")
    
    conn.close()

if __name__ == "__main__":
    find_last_problematic_arret()
