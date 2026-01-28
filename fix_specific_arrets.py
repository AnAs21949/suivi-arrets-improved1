"""
Script pour corriger les 2 sous-familles incorrectes
"""
import sqlite3

DB_FILE = "db/arrets.db"

def fix_specific_arrets():
    """Corrige les sous-familles et services incorrects pour 3 arrêts spécifiques"""
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("🔧 Correction de 3 arrêts spécifiques...\n")
    
    # Arrêt 1: ID 172
    print("Arrêt ID 172 (05/01, 7.67h):")
    cursor.execute("SELECT service, sous_famille FROM arrets WHERE id = 172")
    result = cursor.fetchone()
    if result:
        print(f"  Avant: {result[0]} | {result[1]}")
        
    cursor.execute("""
        UPDATE arrets 
        SET sous_famille = 'Lancement Nouvelle Réf (Validation)'
        WHERE id = 172
    """)
    print(f"  Après: TECHNIQUE | Lancement Nouvelle Réf (Validation)")
    print()
    
    # Arrêt 2: ID 176
    print("Arrêt ID 176 (06/01, 4.0h):")
    cursor.execute("SELECT service, sous_famille FROM arrets WHERE id = 176")
    result = cursor.fetchone()
    if result:
        print(f"  Avant: {result[0]} | {result[1]}")
        
    cursor.execute("""
        UPDATE arrets 
        SET sous_famille = 'Blocage attente décision'
        WHERE id = 176
    """)
    print(f"  Après: TECHNIQUE | Blocage attente décision")
    print()
    
    # Arrêt 3: ID 178 (service incorrect)
    print("Arrêt ID 178 ('Arrêt énergie nocturne'):")
    cursor.execute("SELECT service, sous_famille FROM arrets WHERE id = 178")
    result = cursor.fetchone()
    if result:
        print(f"  Avant: {result[0]} | {result[1]}")
        
    cursor.execute("""
        UPDATE arrets 
        SET service = 'MAINTENANCE'
        WHERE id = 178
    """)
    print(f"  Après: MAINTENANCE | Arrêt énergie nocturne")
    print()
    
    conn.commit()
    
    # Vérification finale
    print("="*70)
    print("✅ Corrections appliquées\n")
    
    print("🔍 Vérification: 'Arrêt énergie général'")
    cursor.execute("""
        SELECT service, COUNT(*) 
        FROM arrets 
        WHERE sous_famille = 'Arrêt énergie général'
        GROUP BY service
    """)
    
    results = cursor.fetchall()
    for service, count in results:
        symbol = "✅" if service.upper() == "MAINTENANCE" else "❌"
        print(f"  {symbol} {service}: {count} occurrence(s)")
    
    # Compter total
    cursor.execute("""
        SELECT COUNT(*) 
        FROM arrets 
        WHERE sous_famille = 'Arrêt énergie général'
    """)
    total = cursor.fetchone()[0]
    
    if total == 7:
        print(f"\n  ✅ Parfait ! Les 7 occurrences sont bien en MAINTENANCE")
        print(f"  ✅ Les 2 arrêts TECHNIQUE ont été corrigés avec leur vraie sous-famille")
        print(f"  ✅ L'arrêt SUPPLY (ID 178) a été corrigé en MAINTENANCE")
    else:
        print(f"\n  ⚠️ Total: {total} arrêts (devrait être 7 après correction)")
    
    conn.close()
    print("\n✅ Terminé !")

if __name__ == "__main__":
    fix_specific_arrets()
