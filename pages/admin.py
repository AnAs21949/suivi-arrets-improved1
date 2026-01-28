"""
Admin Page - Administration and configuration.
Manage productivity matrix, clients, services, and other reference data.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from config import SITES, NBR_EQUIPES_OPTIONS
from data.repository import MatriceRepository, ClientRepository, ArretRepository
from data.database import get_db
from core.validators import validate_matrice_entry


def render_admin_page():
    """Render the administration page."""
    
    st.markdown("## Administration")
    st.markdown("Gérez les données de référence et la configuration du système.")
    st.markdown("---")
    
    # Check if user is admin
    if st.session_state.get('current_user') != 'Admin':
        st.warning("⚠️ Certaines fonctionnalités sont réservées aux administrateurs.")
    
    # Create tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Matrice Productivité",
        "Clients",
        "Statistiques",
        "Maintenance"
    ])
    
    # === TAB 1: MATRICE PRODUCTIVITÉ ===
    with tab1:
        render_matrice_tab()
    
    # === TAB 2: CLIENTS ===
    with tab2:
        render_clients_tab()
    
    # === TAB 3: STATISTIQUES ===
    with tab3:
        render_stats_tab()
    
    # === TAB 4: MAINTENANCE ===
    with tab4:
        render_maintenance_tab()


def render_matrice_tab():
    """Render the productivity matrix management tab."""
    
    st.markdown("### Matrice de Productivité")
    st.markdown("""
    Le **Facteur** représente le nombre d'heures d'arrêt équivalent à 1% de perte de productivité 
    pour chaque combinaison Site/Client/Équipes.
    
    **Formule:** `Impact% = Durée(h) ÷ Facteur`
    """)
    
    st.markdown("---")
    
    # Display current matrix
    matrice = MatriceRepository.get_all(actif_only=False)
    
    if matrice:
        df = pd.DataFrame(matrice)
        df_display = df[['id', 'site', 'client', 'nbr_equipes', 'facteur', 'actif']].copy()
        df_display.columns = ['ID', 'Site', 'Client', 'Équipes', 'Facteur', 'Actif']
        df_display['Actif'] = df_display['Actif'].apply(lambda x: '✅' if x else '❌')
        df_display['Facteur'] = df_display['Facteur'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune entrée dans la matrice. Ajoutez-en une ci-dessous.")
    
    st.markdown("---")
    
    # Add new matrix entry
    st.markdown("#### ➕ Ajouter une entrée")
    
    with st.form("add_matrice_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            new_site = st.selectbox("Site", options=SITES, key="new_matrice_site")
        
        with col2:
            new_client = st.text_input("Client", placeholder="Nom du client", key="new_matrice_client")
        
        with col3:
            new_nbr_equipes = st.selectbox("Équipes", options=NBR_EQUIPES_OPTIONS, key="new_matrice_equipes")
        
        with col4:
            new_facteur = st.number_input("Facteur", min_value=0.01, value=10.0, step=0.1, key="new_matrice_facteur")
        
        submitted = st.form_submit_button("➕ Ajouter", use_container_width=True)
        
        if submitted:
            if not new_client:
                st.error("Le nom du client est obligatoire.")
            else:
                data = {
                    'site': new_site,
                    'client': new_client,
                    'nbr_equipes': new_nbr_equipes,
                    'facteur': new_facteur
                }
                
                is_valid, errors = validate_matrice_entry(data)
                
                if not is_valid:
                    for error in errors:
                        st.error(error)
                else:
                    try:
                        MatriceRepository.create(data)
                        st.success(f"Entrée ajoutée: {new_site}/{new_client}/{new_nbr_equipes}")
                        st.rerun()
                    except Exception as e:
                        if "UNIQUE constraint" in str(e):
                            st.error("Cette combinaison Site/Client/Équipes existe déjà.")
                        else:
                            st.error(f"Erreur: {e}")
    
    st.markdown("---")
    
    # Edit/Delete matrix entries
    st.markdown("#### Modifier/Supprimer")
    
    if matrice:
        matrix_options = {f"{m['id']}: {m['site']}/{m['client']}/{m['nbr_equipes']}": m['id'] for m in matrice}
        
        selected = st.selectbox(
            "Sélectionner une entrée",
            options=[""] + list(matrix_options.keys()),
            key="edit_matrice_select"
        )
        
        if selected:
            selected_id = matrix_options[selected]
            selected_entry = next(m for m in matrice if m['id'] == selected_id)
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("edit_matrice_form"):
                    edit_facteur = st.number_input(
                        "Nouveau facteur",
                        min_value=0.01,
                        value=float(selected_entry['facteur']),
                        step=0.1
                    )
                    
                    if st.form_submit_button("💾 Mettre à jour"):
                        MatriceRepository.update(selected_id, {
                            'site': selected_entry['site'],
                            'client': selected_entry['client'],
                            'nbr_equipes': selected_entry['nbr_equipes'],
                            'facteur': edit_facteur
                        })
                        st.success("Facteur mis à jour!")
                        st.rerun()
            
            with col2:
                if st.button("Désactiver cette entrée", type="secondary"):
                    MatriceRepository.delete(selected_id)
                    st.success("Entrée désactivée.")
                    st.rerun()


def render_clients_tab():
    """Render the clients management tab."""
    
    st.markdown("### Gestion des Clients")
    
    # List all clients from arrêts
    clients = ClientRepository.get_all_from_arrets()
    
    st.markdown(f"**{len(clients)} clients** dans le système:")
    
    if clients:
        # Show as a nice list with stats
        col1, col2 = st.columns(2)
        
        half = len(clients) // 2
        
        with col1:
            for client in clients[:half+1]:
                count = ArretRepository.count({'client': client}) if client else 0
                st.markdown(f"• **{client}** ({count} arrêts)")
        
        with col2:
            for client in clients[half+1:]:
                count = ArretRepository.count({'client': client}) if client else 0
                st.markdown(f"• **{client}** ({count} arrêts)")
    
    st.markdown("---")
    
    # Add new client
    st.markdown("#### ➕ Ajouter un client")
    
    with st.form("add_client_form"):
        new_client = st.text_input("Nom du client", placeholder="Ex: ACME Corp")
        
        if st.form_submit_button("➕ Ajouter"):
            if new_client and new_client.strip():
                ClientRepository.create(new_client.strip())
                st.success(f"✅ Client '{new_client}' ajouté!")
                st.rerun()
            else:
                st.error("Le nom du client est obligatoire.")


def render_stats_tab():
    """Render the statistics tab."""
    
    st.markdown("### Statistiques Globales")
    
    # Overall stats
    all_stats = ArretRepository.get_stats({})
    total_count = ArretRepository.count({})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total arrêts", total_count)
    
    with col2:
        st.metric("Total heures", f"{all_stats['total_heures']:.1f}h")
    
    with col3:
        st.metric("Moyenne/arrêt", f"{all_stats['moyenne_heures']:.2f}h")
    
    with col4:
        st.metric("Impact total", f"{all_stats['total_impact']*100:.2f}%")
    
    st.markdown("---")
    
    # Stats by site
    st.markdown("#### Par Site")
    
    for site in SITES:
        site_stats = ArretRepository.get_stats({'site': site})
        site_count = ArretRepository.count({'site': site})
        
        with st.expander(f"{site}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Arrêts", site_count)
            with col2:
                st.metric("Heures", f"{site_stats['total_heures']:.1f}h")
            with col3:
                st.metric("Impact", f"{site_stats['total_impact']*100:.2f}%")
    
    st.markdown("---")
    
    # Stats by year
    st.markdown("#### Par Année")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT annee, COUNT(*) as count, SUM(duree_heures) as heures
            FROM arrets
            WHERE annee IS NOT NULL
            GROUP BY annee
            ORDER BY annee DESC
        """)
        
        for row in cursor.fetchall():
            st.markdown(f"• **{row['annee']}**: {row['count']} arrêts, {row['heures']:.1f}h")


def render_maintenance_tab():
    """Render the maintenance tab."""
    
    st.markdown("### Maintenance du Système")
    
    st.warning("Ces actions peuvent modifier ou supprimer des données. Utilisez avec précaution.")
    
    st.markdown("---")
    
    # Database info
    st.markdown("#### Informations Base de Données")
    
    from config import DB_PATH
    import os
    
    if DB_PATH.exists():
        db_size = os.path.getsize(DB_PATH)
        st.markdown(f"• **Chemin:** `{DB_PATH}`")
        st.markdown(f"• **Taille:** {db_size / 1024:.1f} KB")
    
    st.markdown("---")
    
    # Recalculate impacts
    st.markdown("#### Recalculer les Impacts")
    st.markdown("""
    Cette fonction recalcule l'impact productivité de tous les arrêts en utilisant 
    la matrice actuelle. Utile après avoir modifié les facteurs de la matrice.
    """)
    
    if st.button("Recalculer tous les impacts", type="secondary"):
        with st.spinner("Recalcul en cours..."):
            recalculate_all_impacts()
        st.success("Tous les impacts ont été recalculés!")
    
    st.markdown("---")
    
    # Import from Excel
    st.markdown("#### Importer depuis Excel")
    
    uploaded_file = st.file_uploader(
        "Sélectionner un fichier Excel",
        type=['xlsx', 'xls'],
        help="Importez des données depuis un fichier Excel formaté"
    )
    
    if uploaded_file:
        if st.button("Lancer l'import", type="primary"):
            with st.spinner("Import en cours..."):
                # Save uploaded file temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    from utils.data_import import import_all_from_excel
                    stats = import_all_from_excel(tmp_path)
                    st.success(f"""
                    ✅ Import terminé!
                    - Entrées matrice: {stats['matrice_count']}
                    - Arrêts: {stats['arrets_count']}
                    """)
                except Exception as e:
                    st.error(f"Erreur lors de l'import: {e}")
                finally:
                    os.unlink(tmp_path)
    
    st.markdown("---")
    
    # Data cleanup
    st.markdown("#### 🧹 Nettoyage des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Supprimer les doublons", type="secondary"):
            st.info("Fonctionnalité en cours de développement.")
    
    with col2:
        if st.button("🔧 Corriger les incohérences", type="secondary"):
            st.info("Fonctionnalité en cours de développement.")


def recalculate_all_impacts():
    """Recalculate impact_pct for all arrêts using current matrix."""
    from core.calculations import calculate_impact
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all arrêts
        cursor.execute("SELECT id, site, client, nbr_equipes, duree_heures FROM arrets")
        arrets = cursor.fetchall()
        
        updated = 0
        for arret in arrets:
            new_impact = calculate_impact(
                arret['duree_heures'] or 0,
                arret['site'],
                arret['client'],
                arret['nbr_equipes'] or 1
            )
            
            cursor.execute(
                "UPDATE arrets SET impact_pct = ?, updated_at = ? WHERE id = ?",
                (new_impact, datetime.now(), arret['id'])
            )
            updated += 1
        
        conn.commit()
        return updated
