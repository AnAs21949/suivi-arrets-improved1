"""
Repository pattern implementation for database operations.
Provides clean CRUD interface for all entities.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from data.database import get_db


class ArretRepository:
    """CRUD operations for arrêts (production stoppages)."""
    
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """Create a new arrêt and return its ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Set timestamps
            now = datetime.now()
            data['created_at'] = now
            data['updated_at'] = now
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            
            cursor.execute(
                f"INSERT INTO arrets ({columns}) VALUES ({placeholders})",
                list(data.values())
            )
            
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(arret_id: int) -> Optional[Dict]:
        """Get a single arrêt by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM arrets WHERE id = ?", (arret_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_all(
        filters: Optional[Dict] = None,
        order_by: str = "date DESC, heure_debut DESC",
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict]:
        """Get all arrêts with optional filtering and pagination."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM arrets WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('site'):
                    query += " AND site = ?"
                    params.append(filters['site'])
                
                if filters.get('client'):
                    query += " AND client = ?"
                    params.append(filters['client'])
                
                if filters.get('service'):
                    query += " AND service = ?"
                    params.append(filters['service'])
                
                if filters.get('statut'):
                    query += " AND statut = ?"
                    params.append(filters['statut'])
                
                if filters.get('date_from'):
                    query += " AND date >= ?"
                    params.append(filters['date_from'])
                
                if filters.get('date_to'):
                    query += " AND date <= ?"
                    params.append(filters['date_to'])
                
                if filters.get('semaine'):
                    query += " AND semaine = ?"
                    params.append(filters['semaine'])
                
                if filters.get('search'):
                    query += " AND (description LIKE ? OR reference LIKE ? OR poste_machine LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term, search_term])
            
            query += f" ORDER BY {order_by}"
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update(arret_id: int, data: Dict[str, Any]) -> bool:
        """Update an arrêt by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            data['updated_at'] = datetime.now()
            
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [arret_id]
            
            cursor.execute(
                f"UPDATE arrets SET {set_clause} WHERE id = ?",
                values
            )
            
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(arret_id: int) -> bool:
        """Delete an arrêt by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM arrets WHERE id = ?", (arret_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def count(filters: Optional[Dict] = None) -> int:
        """Count arrêts with optional filtering."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) as count FROM arrets WHERE 1=1"
            params = []
            
            if filters:
                if filters.get('site'):
                    query += " AND site = ?"
                    params.append(filters['site'])
                if filters.get('date_from'):
                    query += " AND date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    query += " AND date <= ?"
                    params.append(filters['date_to'])
            
            cursor.execute(query, params)
            return cursor.fetchone()['count']
    
    @staticmethod
    def get_stats(filters: Optional[Dict] = None) -> Dict:
        """Get aggregate statistics for arrêts."""
        with get_db() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_arrets,
                    COALESCE(SUM(duree_heures), 0) as total_heures,
                    COALESCE(AVG(duree_heures), 0) as moyenne_heures,
                    COALESCE(SUM(impact_pct), 0) as total_impact
                FROM arrets WHERE 1=1
            """
            params = []
            
            if filters:
                if filters.get('site'):
                    query += " AND site = ?"
                    params.append(filters['site'])
                if filters.get('date_from'):
                    query += " AND date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    query += " AND date <= ?"
                    params.append(filters['date_to'])
                if filters.get('semaine'):
                    query += " AND semaine = ?"
                    params.append(filters['semaine'])
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row)


class MatriceRepository:
    """CRUD operations for the productivity matrix."""
    
    @staticmethod
    def get_facteur(site: str, client: str, nbr_equipes: int) -> Optional[float]:
        """Get the productivity factor for a specific combination."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT facteur FROM matrice_productivite 
                   WHERE site = ? AND client = ? AND nbr_equipes = ? AND actif = 1""",
                (site, client, nbr_equipes)
            )
            row = cursor.fetchone()
            return row['facteur'] if row else None
    
    @staticmethod
    def get_all(actif_only: bool = True) -> List[Dict]:
        """Get all entries in the productivity matrix."""
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM matrice_productivite"
            if actif_only:
                query += " WHERE actif = 1"
            query += " ORDER BY site, client, nbr_equipes"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """Create a new matrix entry."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO matrice_productivite (site, client, nbr_equipes, facteur, actif)
                   VALUES (?, ?, ?, ?, ?)""",
                (data['site'], data['client'], data['nbr_equipes'], data['facteur'], True)
            )
            return cursor.lastrowid
    
    @staticmethod
    def update(matrix_id: int, data: Dict[str, Any]) -> bool:
        """Update a matrix entry."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE matrice_productivite 
                   SET site = ?, client = ?, nbr_equipes = ?, facteur = ?, updated_at = ?
                   WHERE id = ?""",
                (data['site'], data['client'], data['nbr_equipes'], data['facteur'], 
                 datetime.now(), matrix_id)
            )
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(matrix_id: int) -> bool:
        """Soft delete a matrix entry."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE matrice_productivite SET actif = 0 WHERE id = ?",
                (matrix_id,)
            )
            return cursor.rowcount > 0


class ClientRepository:
    """CRUD operations for clients."""
    
    @staticmethod
    def get_all(actif_only: bool = True) -> List[str]:
        """Get all client names."""
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT nom FROM clients"
            if actif_only:
                query += " WHERE actif = 1"
            query += " ORDER BY nom"
            cursor.execute(query)
            return [row['nom'] for row in cursor.fetchall()]
    
    @staticmethod
    def get_all_from_arrets() -> List[str]:
        """Get all unique clients from existing arrêts."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT client FROM arrets WHERE client IS NOT NULL ORDER BY client")
            return [row['client'] for row in cursor.fetchall()]
    
    @staticmethod
    def create(nom: str) -> int:
        """Create a new client."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO clients (nom) VALUES (?)", (nom,))
            return cursor.lastrowid


class ServiceRepository:
    """CRUD operations for services."""
    
    @staticmethod
    def get_all(actif_only: bool = True) -> List[str]:
        """Get all service names."""
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT nom FROM services"
            if actif_only:
                query += " WHERE actif = 1"
            query += " ORDER BY nom"
            cursor.execute(query)
            return [row['nom'] for row in cursor.fetchall()]
    
    @staticmethod
    def get_all_from_arrets() -> List[str]:
        """Get all unique services from existing arrêts."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT service FROM arrets WHERE service IS NOT NULL ORDER BY service")
            return [row['service'] for row in cursor.fetchall()]
