"""
Dashboard Page - Management view with KPIs, charts, and analytics.
Provides visual insights into production stoppages matching CICOR design.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from data.repository import ArretRepository
from core.calculations import get_current_week, get_previous_week, get_week_boundaries
from config import SITES, SERVICE_COLORS


def render_dashboard_page():
    """Render the dashboard page with KPIs and visualizations."""
    
    st.markdown("## 📊 Tableau de Bord KPI")
    st.markdown("*Suivi des arrêts de production*")
    st.markdown("---")
    
    # === FILTERS ROW ===
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    
    with col1:
        site_filter = st.selectbox(
            "🏭 Site",
            options=["Total Maroc"] + SITES,
            key="dash_site_filter"
        )
    
    with col2:
        period_options = {
            "Cette semaine": "current_week",
            "Semaine dernière": "last_week",
            "Ce mois": "current_month",
            "Janvier 2026": "january_2026",
            "30 derniers jours": "last_30_days",
            "Depuis S52-2025": "since_s52"
        }
        selected_period = st.selectbox(
            "📅 Période",
            options=list(period_options.keys()),
            index=3  # Default to January 2026
        )
    
    # Calculate date range based on selection
    today = date.today()
    
    if period_options[selected_period] == "current_week":
        current_week = get_current_week()
        date_from, date_to = get_week_boundaries(current_week)
        period_label = f"Semaine {current_week}"
    elif period_options[selected_period] == "last_week":
        last_week = get_previous_week()
        date_from, date_to = get_week_boundaries(last_week)
        period_label = f"Semaine {last_week}"
    elif period_options[selected_period] == "current_month":
        date_from = today.replace(day=1)
        date_to = today
        period_label = f"{today.strftime('%B %Y')}"
    elif period_options[selected_period] == "january_2026":
        date_from = date(2026, 1, 1)
        date_to = date(2026, 1, 31)
        period_label = "Janvier 2026"
    elif period_options[selected_period] == "last_30_days":
        date_from = today - timedelta(days=30)
        date_to = today
        period_label = "30 derniers jours"
    elif period_options[selected_period] == "since_s52":
        date_from = date(2025, 12, 23)  # Start of S52-2025
        date_to = today
        period_label = "Depuis S52-2025"
    else:
        date_from = today - timedelta(days=30)
        date_to = today
        period_label = "Personnalisé"
    
    filters = {'date_from': date_from, 'date_to': date_to}
    if site_filter != "Total Maroc":
        filters['site'] = site_filter
    
    st.markdown(f"**{site_filter}** • {period_label}")
    st.markdown("---")
    
    # === KPIs SECTION ===
    current_stats = ArretRepository.get_stats(filters)
    current_count = ArretRepository.count(filters)
    
    # Previous period for comparison
    period_length = (date_to - date_from).days + 1
    prev_date_from = date_from - timedelta(days=period_length)
    prev_date_to = date_from - timedelta(days=1)
    prev_filters = {'date_from': prev_date_from, 'date_to': prev_date_to}
    if site_filter != "Total Maroc":
        prev_filters['site'] = site_filter
    prev_stats = ArretRepository.get_stats(prev_filters)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border-left: 4px solid #e53e3e;">
            <p style="color: #718096; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">
                HEURES D'ARRÊT</p>
            <p style="color: #e53e3e; font-size: 2.5rem; font-weight: 700; margin: 0;">
                {:.1f}<span style="font-size: 1rem;">h</span></p>
        </div>
        """.format(current_stats['total_heures']), unsafe_allow_html=True)
    
    with col2:
        impact_pct = current_stats['total_impact'] * 100
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border-left: 4px solid #dd6b20;">
            <p style="color: #718096; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">
                IMPACT PRODUCTIVITÉ</p>
            <p style="color: #dd6b20; font-size: 2.5rem; font-weight: 700; margin: 0;">
                {:.2f}<span style="font-size: 1rem;">%</span></p>
        </div>
        """.format(impact_pct), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border-left: 4px solid #38a169;">
            <p style="color: #718096; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">
                NOMBRE D'ARRÊTS</p>
            <p style="color: #38a169; font-size: 2.5rem; font-weight: 700; margin: 0;">
                {}</p>
        </div>
        """.format(current_count), unsafe_allow_html=True)
    
    with col4:
        avg_duration = current_stats['moyenne_heures']
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center;
                    border-left: 4px solid #3182ce;">
            <p style="color: #718096; font-size: 0.85rem; margin-bottom: 0.5rem; font-weight: 600;">
                DURÉE MOYENNE</p>
            <p style="color: #3182ce; font-size: 2.5rem; font-weight: 700; margin: 0;">
                {:.1f}<span style="font-size: 1rem;">h</span></p>
        </div>
        """.format(avg_duration), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === TABS FOR DIFFERENT VIEWS ===
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Vue d'ensemble", "🔧 Par service", "📊 Évolution", "📉 Pareto"])
    
    # Get all data for charts
    arrets = ArretRepository.get_all(filters=filters)
    
    if not arrets:
        st.info("📭 Aucune donnée disponible pour la période sélectionnée.")
        return
    
    df = pd.DataFrame(arrets)
    
    # Normalize service column to title case for consistent display
    if 'service' in df.columns:
        df['service'] = df['service'].str.title()
    
    # === TAB 1: VUE D'ENSEMBLE ===
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Hours by site
            site_hours = df.groupby('site')['duree_heures'].sum().reset_index()
            site_hours.columns = ['Site', 'Heures']
            
            fig_site_hours = px.bar(
                site_hours,
                x='Site',
                y='Heures',
                color='Site',
                title="<b>Heures d'arrêt par site</b>",
                color_discrete_map={'Berrechid': '#F6AD55', 'Temara': '#4299E1'},
                text='Heures'
            )
            fig_site_hours.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
            fig_site_hours.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Segoe UI, sans-serif"),
                title_font_size=16,
                margin=dict(t=60, b=40)
            )
            st.plotly_chart(fig_site_hours, use_container_width=True)
        
        with col2:
            # Impact by site
            site_impact = df.groupby('site')['impact_pct'].sum().reset_index()
            site_impact.columns = ['Site', 'Impact']
            site_impact['Impact'] = site_impact['Impact'] * 100
            
            fig_site_impact = px.bar(
                site_impact,
                x='Site',
                y='Impact',
                color='Site',
                title="<b>Impact productivité par site (%)</b>",
                color_discrete_map={'Berrechid': '#68D391', 'Temara': '#4FD1C5'},
                text='Impact'
            )
            fig_site_impact.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig_site_impact.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Segoe UI, sans-serif"),
                title_font_size=16,
                margin=dict(t=60, b=40)
            )
            st.plotly_chart(fig_site_impact, use_container_width=True)
        
        # Client breakdown
        st.markdown("### 👥 Répartition par Client")
        
        client_hours = df.groupby('client')['duree_heures'].sum().reset_index()
        client_hours.columns = ['Client', 'Heures']
        client_hours = client_hours.sort_values('Heures', ascending=True)
        
        fig_client = px.bar(
            client_hours,
            x='Heures',
            y='Client',
            orientation='h',
            title="<b>Heures d'arrêt par client</b>",
            color='Heures',
            color_continuous_scale='Oranges',
            text='Heures'
        )
        fig_client.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
        fig_client.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_showscale=False,
            font=dict(family="Segoe UI, sans-serif"),
            margin=dict(l=120)
        )
        st.plotly_chart(fig_client, use_container_width=True)
    
    # === TAB 2: PAR SERVICE ===
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart by service
            service_hours = df.groupby('service')['duree_heures'].sum().reset_index()
            service_hours.columns = ['Service', 'Heures']
            service_hours = service_hours.sort_values('Heures', ascending=False)
            
            fig_service_pie = px.pie(
                service_hours,
                values='Heures',
                names='Service',
                title="<b>Répartition des heures par département</b>",
                color='Service',
                color_discrete_map=SERVICE_COLORS
            )
            fig_service_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=11
            )
            fig_service_pie.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Segoe UI, sans-serif"),
                showlegend=True,
                legend=dict(orientation='h', yanchor='bottom', y=-0.2)
            )
            st.plotly_chart(fig_service_pie, use_container_width=True)
        
        with col2:
            # Bar chart by service
            fig_service_bar = px.bar(
                service_hours.sort_values('Heures', ascending=True),
                x='Heures',
                y='Service',
                orientation='h',
                title="<b>Heures d'arrêt par département</b>",
                color='Service',
                color_discrete_map=SERVICE_COLORS,
                text='Heures'
            )
            fig_service_bar.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
            fig_service_bar.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Segoe UI, sans-serif"),
                yaxis={'categoryorder': 'total ascending'},
                margin=dict(l=120)
            )
            st.plotly_chart(fig_service_bar, use_container_width=True)
        
        # Service by site breakdown
        st.markdown("### 🏭 Service par Site")
        
        service_site = df.groupby(['service', 'site'])['duree_heures'].sum().reset_index()
        service_site.columns = ['Service', 'Site', 'Heures']
        
        fig_service_site = px.bar(
            service_site,
            x='Service',
            y='Heures',
            color='Site',
            title="<b>Heures par service et par site</b>",
            barmode='group',
            color_discrete_map={'Berrechid': '#F6AD55', 'Temara': '#4299E1'},
            text='Heures'
        )
        fig_service_site.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_service_site.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI, sans-serif"),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig_service_site, use_container_width=True)
    
    # === TAB 3: ÉVOLUTION ===
    with tab3:
        # Weekly trend - Stacked bar chart like in the PDF
        if 'semaine' in df.columns:
            weekly_service = df.groupby(['semaine', 'service'])['duree_heures'].sum().reset_index()
            weekly_service.columns = ['Semaine', 'Service', 'Heures']
            
            # Sort by semaine
            weekly_service['sort_key'] = weekly_service['Semaine'].apply(
                lambda x: (int(x.split('-S')[0]), int(x.split('-S')[1])) if '-S' in str(x) else (0, 0)
            )
            weekly_service = weekly_service.sort_values('sort_key')
            
            fig_weekly_stacked = px.bar(
                weekly_service,
                x='Semaine',
                y='Heures',
                color='Service',
                title="<b>Impact Perte en Productivité par semaine</b>",
                color_discrete_map=SERVICE_COLORS,
                text='Heures'
            )
            fig_weekly_stacked.update_traces(texttemplate='%{text:.0f}', textposition='inside')
            fig_weekly_stacked.update_layout(
                barmode='stack',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Segoe UI, sans-serif"),
                xaxis_tickangle=-45,
                legend=dict(orientation='h', yanchor='bottom', y=1.02),
                margin=dict(b=100)
            )
            st.plotly_chart(fig_weekly_stacked, use_container_width=True)
        
        # Weekly trend by site
        st.markdown("### 📊 Perte en H par semaine par site")
        
        if 'semaine' in df.columns:
            weekly_site = df.groupby(['semaine', 'site'])['duree_heures'].sum().reset_index()
            weekly_site.columns = ['Semaine', 'Site', 'Heures']
            
            fig_weekly_site = px.bar(
                weekly_site,
                x='Semaine',
                y='Heures',
                color='Site',
                title="<b>Heures d'arrêt par semaine et par site</b>",
                barmode='group',
                color_discrete_map={'Berrechid': '#F6AD55', 'Temara': '#4299E1'},
                text='Heures'
            )
            fig_weekly_site.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig_weekly_site.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Segoe UI, sans-serif"),
                xaxis_tickangle=-45,
                legend=dict(orientation='h', yanchor='bottom', y=1.02)
            )
            st.plotly_chart(fig_weekly_site, use_container_width=True)
        
        # Daily trend line
        df['date'] = pd.to_datetime(df['date'])
        daily_trend = df.groupby('date').agg({
            'duree_heures': 'sum',
            'id': 'count'
        }).reset_index()
        daily_trend.columns = ['Date', 'Heures', 'Nombre']
        
        fig_daily = go.Figure()
        
        fig_daily.add_trace(go.Scatter(
            x=daily_trend['Date'],
            y=daily_trend['Heures'],
            mode='lines+markers',
            name='Heures',
            line=dict(color='#3182CE', width=3),
            marker=dict(size=8)
        ))
        
        fig_daily.add_trace(go.Bar(
            x=daily_trend['Date'],
            y=daily_trend['Nombre'],
            name="Nombre d'arrêts",
            marker_color='rgba(99, 102, 241, 0.4)',
            yaxis='y2'
        ))
        
        fig_daily.update_layout(
            title="<b>Évolution journalière des arrêts</b>",
            xaxis_title="Date",
            yaxis=dict(title="Heures", side='left', showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis2=dict(title="Nombre d'arrêts", side='right', overlaying='y', showgrid=False),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI, sans-serif"),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            hovermode='x unified'
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # === TAB 4: PARETO PAR SERVICE ===
    with tab4:
        st.markdown("### 📉 Impact par Service / Productivité")
        st.markdown("*Analyse détaillée des causes d'arrêt par département*")
        
        # Check if sous_famille column exists
        has_sous_famille = 'sous_famille' in df.columns and df['sous_famille'].notna().any()
        
        if not has_sous_famille:
            st.warning("⚠️ La colonne 'sous_famille' n'est pas disponible. Exécutez le script de réimportation pour activer l'analyse détaillée.")
            # Fallback to simple service Pareto
            category_col = 'service'
        
        # Service selector
        services_list = ['TECHNIQUE', 'SUPPLY', 'MAINTENANCE', 'ORGANISATION', 'IT']
        available_services = [s for s in services_list if s in df['service'].str.upper().unique()]
        
        selected_service = st.selectbox(
            "Sélectionner un service",
            options=["Tous les services"] + available_services,
            key="pareto_service_select"
        )
        
        if selected_service == "Tous les services":
            # Global Pareto by service
            pareto_data = df.groupby('service')['duree_heures'].sum().reset_index()
            pareto_data.columns = ['Catégorie', 'Heures']
            chart_title = "Pareto global par Service"
        else:
            # Pareto by sous_famille for selected service
            service_df = df[df['service'].str.upper() == selected_service]
            
            if has_sous_famille:
                pareto_data = service_df.groupby('sous_famille')['duree_heures'].sum().reset_index()
                pareto_data.columns = ['Catégorie', 'Heures']
                chart_title = f"Impact {selected_service} / Productivité"
            else:
                # Fallback to description or processus
                pareto_data = service_df.groupby('processus')['duree_heures'].sum().reset_index()
                pareto_data.columns = ['Catégorie', 'Heures']
                chart_title = f"Impact {selected_service} par Processus"
        
        pareto_data = pareto_data.sort_values('Heures', ascending=False)
        pareto_data = pareto_data[pareto_data['Heures'] > 0]  # Remove zeros
        
        # Calculate cumulative percentage
        total_hours = pareto_data['Heures'].sum()
        pareto_data['Cumul'] = pareto_data['Heures'].cumsum()
        pareto_data['Cumul_%'] = (pareto_data['Cumul'] / total_hours) * 100
        
        # Show total hours for selected service
        st.markdown(f"**Total: {total_hours:.1f} heures**")
        
        # Create Pareto chart
        fig_pareto = go.Figure()
        
        # Bar chart - use orange/gold color scheme like PDF
        fig_pareto.add_trace(go.Bar(
            x=pareto_data['Catégorie'],
            y=pareto_data['Heures'],
            name='Heures',
            marker_color='#F6AD55',
            text=pareto_data['Heures'].round(1),
            textposition='outside'
        ))
        
        # Cumulative line
        fig_pareto.add_trace(go.Scatter(
            x=pareto_data['Catégorie'],
            y=pareto_data['Cumul_%'],
            mode='lines+markers',
            name='Cumul %',
            line=dict(color='#1a365d', width=3),
            marker=dict(size=10, color='#1a365d'),
            yaxis='y2'
        ))
        
        # 80% reference line
        fig_pareto.add_hline(
            y=80, 
            line_dash="dash", 
            line_color="red",
            annotation_text="80%",
            annotation_position="right",
            yref='y2'
        )
        
        fig_pareto.update_layout(
            title=f"<b>{chart_title}</b>",
            xaxis_title="Catégorie",
            yaxis=dict(title="Heures", side='left'),
            yaxis2=dict(
                title="Cumul %", 
                side='right', 
                overlaying='y',
                range=[0, 105],
                ticksuffix='%'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Segoe UI, sans-serif", color='#1a202c'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02),
            xaxis_tickangle=-45,
            margin=dict(b=120),
            bargap=0.3
        )
        
        st.plotly_chart(fig_pareto, use_container_width=True)
        
        # Breakdown by site if a specific service is selected
        if selected_service != "Tous les services" and has_sous_famille:
            st.markdown(f"#### Détail par Site - {selected_service}")
            
            service_df = df[df['service'].str.upper() == selected_service]
            
            col1, col2 = st.columns(2)
            
            for idx, site in enumerate(['Berrechid', 'BERRECHID']):
                site_df = service_df[service_df['site'].str.upper() == 'BERRECHID'] if idx == 0 else service_df[service_df['site'].str.upper() == 'TEMARA']
                site_name = 'Berrechid' if idx == 0 else 'Temara'
                
                if len(site_df) > 0:
                    site_breakdown = site_df.groupby('sous_famille')['duree_heures'].sum().sort_values(ascending=False)
                    
                    with col1 if idx == 0 else col2:
                        st.markdown(f"**{site_name}: {site_breakdown.sum():.1f}h**")
                        for cause, hours in site_breakdown.items():
                            if hours > 0:
                                st.markdown(f"- {cause}: {hours:.1f}h")
        
        # Show table with percentages
        st.markdown("#### Tableau récapitulatif")
        
        display_pareto = pareto_data.copy()
        display_pareto['% du total'] = (display_pareto['Heures'] / total_hours * 100).round(1).astype(str) + '%'
        display_pareto['Cumul'] = display_pareto['Cumul_%'].round(1).astype(str) + '%'
        display_pareto = display_pareto[['Catégorie', 'Heures', '% du total', 'Cumul']]
        display_pareto['Heures'] = display_pareto['Heures'].round(1).astype(str) + 'h'
        
        st.dataframe(display_pareto, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # === TOP ARRÊTS TABLE ===
    st.markdown("### 🏆 Top 5 Arrêts de la Période")
    
    top_arrets = df.nlargest(5, 'duree_heures')[
        ['date', 'site', 'client', 'service', 'duree_heures', 'description']
    ].copy()
    
    top_arrets['date'] = pd.to_datetime(top_arrets['date']).dt.strftime('%d/%m/%Y')
    top_arrets['duree_heures'] = top_arrets['duree_heures'].apply(lambda x: f"{x:.2f}h")
    top_arrets['description'] = top_arrets['description'].apply(
        lambda x: (x[:100] + "...") if x and len(x) > 100 else x
    )
    
    top_arrets.columns = ['Date', 'Site', 'Client', 'Service', 'Durée', 'Description']
    
    st.dataframe(top_arrets, use_container_width=True, hide_index=True)
    
    # === EXPORT BUTTONS ===
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📊 Exporter Excel", use_container_width=True):
            export_dashboard_excel(df, filters, period_label)
    
    with col2:
        if st.button("📽️ Générer Rapport", use_container_width=True):
            st.info("Fonctionnalité de génération de rapport PowerPoint en cours de développement.")


def export_dashboard_excel(df: pd.DataFrame, filters: dict, period_label: str):
    """Export dashboard data to Excel."""
    import io
    
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Raw data
        df.to_excel(writer, index=False, sheet_name='Données Brutes')
        
        # Summary by service
        service_summary = df.groupby('service').agg({
            'duree_heures': ['sum', 'mean', 'count'],
            'impact_pct': 'sum'
        }).round(2)
        service_summary.columns = ['Total Heures', 'Moyenne Heures', 'Nombre Arrêts', 'Impact Total']
        service_summary.to_excel(writer, sheet_name='Par Service')
        
        # Summary by site
        site_summary = df.groupby('site').agg({
            'duree_heures': ['sum', 'mean', 'count'],
            'impact_pct': 'sum'
        }).round(2)
        site_summary.columns = ['Total Heures', 'Moyenne Heures', 'Nombre Arrêts', 'Impact Total']
        site_summary.to_excel(writer, sheet_name='Par Site')
    
    buffer.seek(0)
    
    st.download_button(
        label="📥 Télécharger le rapport Excel",
        data=buffer,
        file_name=f"rapport_arrets_{period_label.replace(' ', '_')}_{date.today().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )