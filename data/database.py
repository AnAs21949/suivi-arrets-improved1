"""
Database connection and initialization for SQLite.
Handles schema creation and connection management.
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import DB_PATH


def get_connection():
    """Create a database connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row  # Access columns by name
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Initialize the database schema."""
    # Ensure db directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Sites table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                actif BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Batiments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                site_id INTEGER NOT NULL,
                actif BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (site_id) REFERENCES sites(id),
                UNIQUE(nom, site_id)
            )
        """)
        
        # Clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                actif BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                actif BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Matrice Productivité table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matrice_productivite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                client TEXT NOT NULL,
                nbr_equipes INTEGER NOT NULL,
                facteur REAL NOT NULL,
                actif BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(site, client, nbr_equipes)
            )
        """)
        
        # Main arrêts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                batiment TEXT,
                date DATE NOT NULL,
                semaine TEXT,
                mois TEXT,
                annee INTEGER,
                heure_debut TIME NOT NULL,
                heure_fin TIME NOT NULL,
                duree_heures REAL,
                client TEXT,
                nbr_equipes INTEGER DEFAULT 1,
                impact_pct REAL,
                processus TEXT,
                poste_machine TEXT,
                service TEXT,
                description TEXT,
                reference TEXT,
                demandeur TEXT,
                equipe TEXT,
                traite_par TEXT,
                statut TEXT DEFAULT 'Ouvert',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrets_date ON arrets(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrets_semaine ON arrets(semaine)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrets_site ON arrets(site)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrets_client ON arrets(client)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_arrets_service ON arrets(service)")
        
        conn.commit()


def seed_reference_data():
    """Populate reference tables with initial data."""
    from config import SITES, BATIMENTS_PAR_SITE, SERVICES
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Insert sites
        for site in SITES:
            cursor.execute(
                "INSERT OR IGNORE INTO sites (nom) VALUES (?)",
                (site,)
            )
        
        # Insert batiments
        for site, batiments in BATIMENTS_PAR_SITE.items():
            cursor.execute("SELECT id FROM sites WHERE nom = ?", (site,))
            site_row = cursor.fetchone()
            if site_row:
                site_id = site_row['id']
                for bat in batiments:
                    cursor.execute(
                        "INSERT OR IGNORE INTO batiments (nom, site_id) VALUES (?, ?)",
                        (bat, site_id)
                    )
        
        # Insert services
        for service in SERVICES:
            cursor.execute(
                "INSERT OR IGNORE INTO services (nom) VALUES (?)",
                (service,)
            )
        
        conn.commit()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding reference data...")
    seed_reference_data()
    print(f"Database created at: {DB_PATH}")
