"""
Journal Page - List view of all production stoppages.
Supports filtering, searching, editing, and deletion.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
from config import SITES, SERVICES, STATUTS, ITEMS_PER_PAGE
from data.repository import ArretRepository, ClientRepository, ServiceRepository
from core.calculations import calculate_duration, calculate_impact, get_iso_week, get_month_string


def render_journal_page():
    """Render the journal (list view) page."""
    
    st.markdown("## Historique des arrêts")
    st.markdown("*Consultez et recherchez tous les arrêts enregistrés*")
    st.markdown("---")
    
    # === FILTERS SECTION ===
    with st.expander("Filtres", expanded=True):
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Date range filter
            date_from = st.date_input(
                "Date début",
                value=date.today() - timedelta(days=30),
                key="filter_date_from"
            )
        
        with col2:
            date_to = st.date_input(
                "Date fin",
                value=date.today(),
                key="filter_date_to"
            )
        
        with col3:
            # Site filter
            site_filter = st.selectbox(
                "Site",
                options=["Tous"] + SITES,
                key="filter_site"
            )
        
        with col4:
            # Service filter
            services = ServiceRepository.get_all_from_arrets()
            service_filter = st.selectbox(
                "Service",
                options=["Tous"] + services,
                key="filter_service"
            )
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            # Client filter
            clients = ClientRepository.get_all_from_arrets()
            client_filter = st.selectbox(
                "Client",
                options=["Tous"] + clients,
                key="filter_client"
            )
        
        with col6:
            # Status filter
            statut_filter = st.selectbox(
                "Statut",
                options=["Tous"] + STATUTS,
                key="filter_statut"
            )
        
        with col7:
            # Text search
            search_text = st.text_input(
                "Recherche",
                placeholder="Description, référence...",
                key="filter_search"
            )
        
        with col8:
            st.markdown("<br>", unsafe_allow_html=True)
            col_reset, col_apply = st.columns(2)
            with col_reset:
                if st.button("Reset", use_container_width=True):
                    st.rerun()
    
    # Build filters dictionary
    filters = {
        'date_from': date_from,
        'date_to': date_to
    }
    
    if site_filter != "Tous":
        filters['site'] = site_filter
    if service_filter != "Tous":
        filters['service'] = service_filter
    if client_filter != "Tous":
        filters['client'] = client_filter
    if statut_filter != "Tous":
        filters['statut'] = statut_filter
    if search_text:
        filters['search'] = search_text
    
    # === RESULTS SUMMARY ===
    stats = ArretRepository.get_stats(filters)
    total_count = ArretRepository.count(filters)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total arrêts", total_count)
    with col2:
        st.metric("Heures totales", f"{stats['total_heures']:.1f}h")
    with col3:
        st.metric("Moyenne/arrêt", f"{stats['moyenne_heures']:.2f}h")
    with col4:
        st.metric("Impact total", f"{stats['total_impact']*100:.2f}%")
    
    st.markdown("---")
    
    # === DATA TABLE ===
    # Pagination
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0
    
    total_pages = max(1, (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    
    # Get paginated data
    arrets = ArretRepository.get_all(
        filters=filters,
        limit=ITEMS_PER_PAGE,
        offset=st.session_state.page_number * ITEMS_PER_PAGE
    )
    
    if not arrets:
        st.info("Aucun arrêt trouvé avec les filtres sélectionnés.")
    else:
        # Convert to DataFrame for display
        df = pd.DataFrame(arrets)
        
        # Select and rename columns for display
        display_columns = {
            'id': 'ID',
            'date': 'Date',
            'site': 'Site',
            'batiment': 'Bât',
            'client': 'Client',
            'service': 'Service',
            'duree_heures': 'Durée (h)',
            'impact_pct': 'Impact %',
            'statut': 'Statut',
            'description': 'Description'
        }
        
        df_display = df[[col for col in display_columns.keys() if col in df.columns]].copy()
        df_display.columns = [display_columns.get(col, col) for col in df_display.columns]
        
        # Format columns
        if 'Date' in df_display.columns:
            df_display['Date'] = pd.to_datetime(df_display['Date']).dt.strftime('%d/%m/%Y')
        if 'Durée (h)' in df_display.columns:
            df_display['Durée (h)'] = df_display['Durée (h)'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "-")
        if 'Impact %' in df_display.columns:
            df_display['Impact %'] = df_display['Impact %'].apply(lambda x: f"{x*100:.3f}%" if pd.notna(x) else "-")
        if 'Description' in df_display.columns:
            df_display['Description'] = df_display['Description'].apply(
                lambda x: (x[:50] + "...") if x and len(x) > 50 else x
            )
        
        # Display table with selection
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ Précédent", disabled=st.session_state.page_number == 0):
                st.session_state.page_number -= 1
                st.rerun()
        
        with col2:
            st.markdown(
                f"<div style='text-align: center'>Page {st.session_state.page_number + 1} sur {total_pages}</div>",
                unsafe_allow_html=True
            )
        
        with col3:
            if st.button("Suivant ▶", disabled=st.session_state.page_number >= total_pages - 1):
                st.session_state.page_number += 1
                st.rerun()
    
    st.markdown("---")
    
    # === EDIT/DELETE SECTION ===
    st.markdown("### ✏️ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select arrêt to edit/delete
        arret_ids = [a['id'] for a in arrets] if arrets else []
        selected_id = st.selectbox(
            "Sélectionner un arrêt (ID)",
            options=[""] + [str(id) for id in arret_ids],
            key="selected_arret_id"
        )
    
    if selected_id:
        arret = ArretRepository.get_by_id(int(selected_id))
        
        if arret:
            # Show details
            st.markdown(f"**Arrêt #{arret['id']}** - {arret['date']} - {arret['client']}")
            
            with st.expander("📝 Modifier cet arrêt", expanded=False):
                render_edit_form(arret)
            
            # Delete button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("🗑️ Supprimer", type="secondary", key="delete_btn"):
                    st.session_state.confirm_delete = True
            
            if st.session_state.get('confirm_delete'):
                with col2:
                    if st.button("⚠️ Confirmer", type="primary", key="confirm_delete_btn"):
                        ArretRepository.delete(int(selected_id))
                        st.success(f"Arrêt #{selected_id} supprimé.")
                        st.session_state.confirm_delete = False
                        st.session_state.page_number = 0
                        st.rerun()
    
    # === EXPORT SECTION ===
    st.markdown("---")
    st.markdown("### 📥 Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Exporter Excel", use_container_width=True):
            export_to_excel(filters)
    
    with col2:
        if st.button("Exporter CSV", use_container_width=True):
            export_to_csv(filters)


def render_edit_form(arret: dict):
    """Render the edit form for an arrêt."""
    from config import BATIMENTS_PAR_SITE, EQUIPES, PROCESSUS, NBR_EQUIPES_OPTIONS
    
    with st.form(f"edit_form_{arret['id']}"):
        
        col1, col2 = st.columns(2)
        
        with col1:
            site = st.selectbox(
                "Site",
                options=SITES,
                index=SITES.index(arret['site']) if arret['site'] in SITES else 0,
                key=f"edit_site_{arret['id']}"
            )
        
        with col2:
            batiments = BATIMENTS_PAR_SITE.get(site, [])
            bat_index = batiments.index(arret['batiment']) if arret['batiment'] in batiments else 0
            batiment = st.selectbox(
                "Bâtiment",
                options=batiments,
                index=bat_index,
                key=f"edit_batiment_{arret['id']}"
            )
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            date_val = arret['date']
            if isinstance(date_val, str):
                date_val = datetime.strptime(date_val, '%Y-%m-%d').date()
            date_arret = st.date_input(
                "Date",
                value=date_val,
                key=f"edit_date_{arret['id']}"
            )
        
        with col4:
            heure_debut_str = arret['heure_debut']
            if isinstance(heure_debut_str, str):
                heure_debut_val = datetime.strptime(heure_debut_str, '%H:%M:%S').time()
            else:
                heure_debut_val = heure_debut_str
            heure_debut = st.time_input(
                "Heure début",
                value=heure_debut_val,
                key=f"edit_heure_debut_{arret['id']}"
            )
        
        with col5:
            heure_fin_str = arret['heure_fin']
            if isinstance(heure_fin_str, str):
                heure_fin_val = datetime.strptime(heure_fin_str, '%H:%M:%S').time()
            else:
                heure_fin_val = heure_fin_str
            heure_fin = st.time_input(
                "Heure fin",
                value=heure_fin_val,
                key=f"edit_heure_fin_{arret['id']}"
            )
        
        col6, col7 = st.columns(2)
        
        with col6:
            clients = ClientRepository.get_all_from_arrets()
            client_index = clients.index(arret['client']) if arret['client'] in clients else 0
            client = st.selectbox(
                "Client",
                options=clients,
                index=client_index,
                key=f"edit_client_{arret['id']}"
            )
        
        with col7:
            services = ServiceRepository.get_all_from_arrets()
            service_index = services.index(arret['service']) if arret['service'] in services else 0
            service = st.selectbox(
                "Service",
                options=services,
                index=service_index,
                key=f"edit_service_{arret['id']}"
            )
        
        description = st.text_area(
            "Description",
            value=arret['description'] or "",
            key=f"edit_description_{arret['id']}"
        )
        
        col8, col9 = st.columns(2)
        
        with col8:
            statut_index = STATUTS.index(arret['statut']) if arret['statut'] in STATUTS else 0
            statut = st.selectbox(
                "Statut",
                options=STATUTS,
                index=statut_index,
                key=f"edit_statut_{arret['id']}"
            )
        
        with col9:
            traite_par = st.text_input(
                "Traité par",
                value=arret['traite_par'] or "",
                key=f"edit_traite_par_{arret['id']}"
            )
        
        submitted = st.form_submit_button("💾 Sauvegarder les modifications")
        
        if submitted:
            # Calculate new duration and impact
            duree = calculate_duration(heure_debut, heure_fin)
            impact = calculate_impact(duree, site, client, arret['nbr_equipes'] or 1)
            
            update_data = {
                'site': site,
                'batiment': batiment,
                'date': date_arret,
                'semaine': get_iso_week(date_arret),
                'mois': get_month_string(date_arret),
                'heure_debut': heure_debut.strftime('%H:%M:%S'),
                'heure_fin': heure_fin.strftime('%H:%M:%S'),
                'duree_heures': duree,
                'client': client,
                'impact_pct': impact,
                'service': service,
                'description': description,
                'statut': statut,
                'traite_par': traite_par
            }
            
            ArretRepository.update(arret['id'], update_data)
            st.success("✅ Modifications enregistrées!")
            st.rerun()


def export_to_excel(filters: dict):
    """Export filtered data to Excel."""
    import io
    
    arrets = ArretRepository.get_all(filters=filters)
    if not arrets:
        st.warning("Aucune donnée à exporter.")
        return
    
    df = pd.DataFrame(arrets)
    
    # Create Excel file in memory
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Arrêts')
    
    buffer.seek(0)
    
    st.download_button(
        label="📥 Télécharger Excel",
        data=buffer,
        file_name=f"arrets_export_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def export_to_csv(filters: dict):
    """Export filtered data to CSV."""
    arrets = ArretRepository.get_all(filters=filters)
    if not arrets:
        st.warning("Aucune donnée à exporter.")
        return
    
    df = pd.DataFrame(arrets)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="Télécharger CSV",
        data=csv,
        file_name=f"arrets_export_{date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
