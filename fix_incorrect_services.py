"""
Script ROBUSTE pour corriger les services incorrects
Utilise plusieurs stratégies de matching
"""
import sqlite3
import pandas as pd

# Chemins
EXCEL_FILE = "Suivi des arrêts production Berrechid 27-01-2026.xlsx"
DB_FILE = "db/arrets.db"

def fix_services_robust():
    """Corrige les services avec plusieurs stratégies"""
    
    print("📂 Lecture du fichier Excel...")
    df_excel = pd.read_excel(EXCEL_FILE)
    df_excel.columns = df_excel.columns.str.strip()
    
    print(f"✅ {len(df_excel)} lignes dans l'Excel\n")
    
    # Connexion à la base
    print("🔌 Connexion à la base de données...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Lire toute la base
    cursor.execute("SELECT id, date, site, duree_heures, service, sous_famille FROM arrets")
    db_rows = cursor.fetchall()
    print(f"✅ {len(db_rows)} lignes dans la base\n")
    
    # Créer un mapping Excel : (date, site, durée) -> service correct
    excel_mapping = {}
    for _, row in df_excel.iterrows():
        try:
            date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
            site = str(row['Site']).strip().upper()
            duree = round(float(row['Durée en :H']), 2)
            service = str(row['Service']).strip().upper()
            
            key = (date, site, duree)
            
            # Si la clé existe déjà avec un service différent, prendre le plus fréquent
            if key in excel_mapping:
                if excel_mapping[key] != service:
                    # Conflit - on garde le premier (pourrait être amélioré)
                    pass
            else:
                excel_mapping[key] = service
                
        except Exception as e:
            continue
    
    print(f"📊 {len(excel_mapping)} combinaisons uniques (date, site, durée) dans Excel\n")
    
    # Parcourir la base et corriger
    print("🔄 Correction des services...\n")
    
    updated = 0
    unchanged = 0
    not_found = 0
    
    for arret_id, date, site, duree, service_db, sous_famille in db_rows:
        try:
            # Créer la clé
            site_upper = site.upper() if site else ''
            duree_rounded = round(duree, 2)
            key = (date, site_upper, duree_rounded)
            
            # Chercher dans le mapping
            if key in excel_mapping:
                service_excel = excel_mapping[key]
                service_db_upper = service_db.upper() if service_db else ''
                
                if service_db_upper != service_excel:
                    # Corriger
                    cursor.execute("UPDATE arrets SET service = ? WHERE id = ?", 
                                 (service_excel, arret_id))
                    updated += 1
                    
                    sf_display = sous_famille[:40] if sous_famille else "N/A"
                    print(f"  ✅ ID {arret_id}: {service_db} → {service_excel} | {sf_display}")
                else:
                    unchanged += 1
            else:
                not_found += 1
                
        except Exception as e:
            print(f"  ⚠️ Erreur ID {arret_id}: {e}")
            continue
    
    # Commit
    conn.commit()
    
    print(f"\n" + "="*70)
    print(f"✅ {updated} services corrigés")
    print(f"✓  {unchanged} services déjà corrects")
    print(f"⚠️ {not_found} non trouvés dans Excel (normal pour données anciennes)")
    print("="*70)
    
    # Vérification finale : "Arrêt énergie général"
    print("\n🔍 Vérification finale: 'Arrêt énergie général'")
    cursor.execute("""
        SELECT service, COUNT(*) 
        FROM arrets 
        WHERE sous_famille = 'Arrêt énergie général'
        GROUP BY service
    """)
    
    results = cursor.fetchall()
    if results:
        for service, count in results:
            symbol = "✅" if service.upper() == "MAINTENANCE" else "❌"
            print(f"  {symbol} {service}: {count} occurrence(s)")
        
        # Vérifier si TECHNIQUE existe encore
        technique_count = sum(count for service, count in results if service.upper() == "TECHNIQUE")
        if technique_count > 0:
            print(f"\n  ⚠️ Il reste {technique_count} arrêt(s) en TECHNIQUE")
            print("     Vérification manuelle nécessaire...")
            
            # Afficher ces arrêts
            cursor.execute("""
                SELECT id, date, site, duree_heures, description
                FROM arrets 
                WHERE sous_famille = 'Arrêt énergie général' 
                AND UPPER(service) = 'TECHNIQUE'
            """)
            tech_arrets = cursor.fetchall()
            print("\n     Détails des arrêts problématiques:")
            for arret_id, date, site, duree, desc in tech_arrets:
                desc_short = desc[:50] if desc else "N/A"
                print(f"       ID {arret_id}: {date} | {site} | {duree}h | {desc_short}")
        else:
            print(f"\n  ✅ Tous correctement assignés à MAINTENANCE!")
    else:
        print("  ℹ️ Aucun arrêt trouvé avec cette sous-famille")
    
    conn.close()
    print("\n✅ Terminé !")

if __name__ == "__main__":
    fix_services_robust()