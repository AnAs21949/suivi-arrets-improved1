"""
Saisie Page - Data entry form for new production stoppages.
Implements cascading dropdowns and automatic calculations.
"""
import streamlit as st
from datetime import datetime, date, time
from config import (
    SITES, BATIMENTS_PAR_SITE, SERVICES, EQUIPES, 
    PROCESSUS, NBR_EQUIPES_OPTIONS, STATUTS
)
from data.repository import ArretRepository, MatriceRepository, ClientRepository
from core.calculations import (
    calculate_duration, calculate_impact, is_overnight_stop, prepare_arret_data
)
from core.validators import validate_arret


def get_clients_for_site(site: str) -> list:
    """Get clients that have matrix entries for a given site."""
    matrice = MatriceRepository.get_all()
    clients = set()
    for entry in matrice:
        if entry['site'] == site:
            clients.add(entry['client'])
    
    # Also add clients from existing arrêts
    all_clients = ClientRepository.get_all_from_arrets()
    clients.update(all_clients)
    
    return sorted(list(clients))


def render_saisie_page():
    """Render the data entry page."""
    
    st.markdown("## Nouvel Arrêt Production")
    st.markdown("*Saisissez les détails de l'arrêt de production*")
    st.markdown("---")
    
    # Initialize form state
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    # Create the form
    with st.form("arret_form", clear_on_submit=True):
        
        # === SECTION: LOCALISATION ===
        st.markdown("### Localisation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            site = st.selectbox(
                "Site *",
                options=SITES,
                help="Sélectionnez le site de production"
            )
        
        with col2:
            # Cascading dropdown - batiments depend on site
            batiments_disponibles = BATIMENTS_PAR_SITE.get(site, [])
            batiment = st.selectbox(
                "Bâtiment",
                options=batiments_disponibles,
                help="Bâtiment où s'est produit l'arrêt"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            processus = st.selectbox(
                "Processus",
                options=[""] + PROCESSUS,
                help="Type de processus de production"
            )
        
        with col4:
            poste_machine = st.text_input(
                "Poste / Machine",
                placeholder="Ex: LIGNE2, T4662-01",
                help="Identifiant du poste ou de la machine"
            )
        
        st.markdown("---")
        
        # === SECTION: TEMPS ===
        st.markdown("### Temps")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_arret = st.date_input(
                "Date *",
                value=date.today(),
                max_value=date.today(),
                help="Date de l'arrêt (ne peut pas être dans le futur)"
            )
        
        with col2:
            heure_debut = st.time_input(
                "Heure début *",
                value=time(6, 0),
                help="Heure de début de l'arrêt"
            )
        
        with col3:
            heure_fin = st.time_input(
                "Heure fin *",
                value=time(10, 0),
                help="Heure de fin de l'arrêt"
            )
        
        # Show calculated duration
        duree = calculate_duration(heure_debut, heure_fin)
        overnight = is_overnight_stop(heure_debut, heure_fin)
        
        if overnight:
            st.info(f"**Durée calculée:** {duree:.2f} heures (arrêt traversant minuit)")
        else:
            st.success(f"**Durée calculée:** {duree:.2f} heures")
        
        st.markdown("---")
        
        # === SECTION: CONTEXTE PRODUCTION ===
        st.markdown("### Contexte Production")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get clients for the selected site
            clients_disponibles = get_clients_for_site(site)
            if not clients_disponibles:
                clients_disponibles = ["EDMI", "ABB", "EMS", "SOWEE", "Leclanché", "Le reste"]
            
            client = st.selectbox(
                "Client *",
                options=clients_disponibles,
                help="Client concerné par l'arrêt"
            )
        
        with col2:
            nbr_equipes = st.selectbox(
                "Nombre d'équipes",
                options=NBR_EQUIPES_OPTIONS,
                index=0,
                help="Nombre d'équipes/shifts en production"
            )
        
        # Calculate and show impact
        impact = calculate_impact(duree, site, client, nbr_equipes)
        
        if impact is not None:
            st.success(f"**Impact Productivité:** {impact*100:.4f}% (Durée ÷ Facteur matrice)")
        else:
            st.warning("Combinaison Site/Client/Équipes non trouvée dans la matrice. Impact non calculable.")
        
        st.markdown("---")
        
        # === SECTION: DÉTAILS ===
        st.markdown("### Détails")
        
        col1, col2 = st.columns(2)
        
        with col1:
            service = st.selectbox(
                "Service responsable *",
                options=[""] + SERVICES,
                help="Département responsable ou impliqué"
            )
        
        with col2:
            reference = st.text_input(
                "Référence produit",
                placeholder="Ex: EDM830-010-107",
                help="Code référence du produit concerné"
            )
        
        description = st.text_area(
            "Description *",
            placeholder="Décrivez l'arrêt: cause, actions prises, résolution...",
            height=120,
            help="Description détaillée de l'arrêt"
        )
        
        st.markdown("---")
        
        # === SECTION: SUIVI ===
        st.markdown("### Suivi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            demandeur = st.text_input(
                "Demandeur",
                value=st.session_state.get('current_user', ''),
                help="Personne qui signale l'arrêt"
            )
        
        with col2:
            equipe = st.selectbox(
                "Équipe",
                options=[""] + EQUIPES,
                help="Équipe/shift concernée"
            )
        
        with col3:
            traite_par = st.text_input(
                "Traité par",
                placeholder="Nom du technicien",
                help="Personne qui a résolu l'arrêt"
            )
        
        statut = st.radio(
            "Statut",
            options=STATUTS,
            horizontal=True,
            help="État actuel de l'arrêt"
        )
        
        st.markdown("---")
        
        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "Enregistrer l'arrêt",
                use_container_width=True,
                type="primary"
            )
    
    # Handle form submission
    if submitted:
        # Prepare data for validation
        form_data = {
            'site': site,
            'batiment': batiment,
            'date': date_arret,
            'heure_debut': heure_debut,
            'heure_fin': heure_fin,
            'client': client,
            'nbr_equipes': nbr_equipes,
            'service': service,
            'description': description,
            'processus': processus if processus else None,
            'poste_machine': poste_machine if poste_machine else None,
            'reference': reference if reference else None,
            'demandeur': demandeur if demandeur else None,
            'equipe': equipe if equipe else None,
            'traite_par': traite_par if traite_par else None,
            'statut': statut
        }
        
        # Validate
        is_valid, errors = validate_arret(form_data)
        
        if not is_valid:
            st.error("**Erreurs de validation:**")
            for error in errors:
                st.error(f"• {error}")
        else:
            try:
                # Prepare complete data with calculations
                arret_data = prepare_arret_data(
                    site=site,
                    batiment=batiment,
                    date_arret=date_arret,
                    heure_debut=heure_debut,
                    heure_fin=heure_fin,
                    client=client,
                    nbr_equipes=nbr_equipes,
                    service=service,
                    description=description,
                    processus=processus if processus else None,
                    poste_machine=poste_machine if poste_machine else None,
                    reference=reference if reference else None,
                    demandeur=demandeur if demandeur else None,
                    equipe=equipe if equipe else None,
                    traite_par=traite_par if traite_par else None,
                    statut=statut
                )
                
                # Save to database
                new_id = ArretRepository.create(arret_data)
                
                st.success(f"**Arrêt #{new_id} enregistré avec succès!**")
                
                # Show summary
                st.markdown(f"""
                **Résumé:**
                - Site: {site} / {batiment}
                - Date: {date_arret.strftime('%d/%m/%Y')}
                - Durée: {duree:.2f}h
                - Client: {client}
                - Impact: {impact*100:.4f}% si disponible
                """)
                
                st.balloons()
                
            except Exception as e:
                st.error(f"Erreur lors de l'enregistrement: {str(e)}")
    
    # Quick stats in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Stats du jour")
    
    today_filters = {'date_from': date.today(), 'date_to': date.today()}
    today_stats = ArretRepository.get_stats(today_filters)
    
    st.sidebar.metric("Arrêts aujourd'hui", today_stats['total_arrets'])
    st.sidebar.metric("Heures totales", f"{today_stats['total_heures']:.1f}h")
