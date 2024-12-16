# =======================
# Importar librerías y módulos
# =======================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_cache_funcs_liga1 import (
    load_data, extract_year_from_season, parse_years, 
    load_round_statistics, load_round_player_statistics, get_match_details
)
from streamlit_graphs_liga1 import (
    crear_grafico_indicador, 
    generar_figura_resultados,
    generar_figura_pain_points
)

# =======================
# Título de la aplicación
# =======================
st.title('GRONESTATS 1.0')

# =======================
# Cargar y preparar los datos
# =======================
matches, teams = load_data()

# Preparar los años disponibles en la columna 'season'
matches['season_year'] = matches['season'].apply(extract_year_from_season)
years = sorted(matches['season_year'].unique())  

# Procesar y filtrar los equipos por año
teams['parsed_years'] = teams['years'].apply(parse_years)

# =======================
# Sidebar para filtros
# =======================
st.sidebar.header("Filtros")

# Selección del año
selected_year = st.sidebar.selectbox("Selecciona un año", years)

# Filtrar equipos disponibles en el año seleccionado
teams_in_selected_year = teams[teams['parsed_years'].apply(lambda x: selected_year in x)]

# Ordenar los equipos por criterios específicos
teams_in_selected_year = teams_in_selected_year.sort_values(by=['rival_team', 'altura_team'], ascending=False)

# Selección del equipo
selected_team = st.sidebar.selectbox(
    "Selecciona un equipo",
    teams_in_selected_year['team'].tolist()
)

# Filtrar partidos del equipo seleccionado para el año seleccionado
matches_for_team = matches[(matches['season_year'] == selected_year) & 
                            ((matches['home'] == selected_team) | (matches['away'] == selected_team))]

# Filtro por torneo
tournaments = sorted(matches_for_team['tournament'].unique())
selected_tournament = st.sidebar.selectbox("Selecciona un torneo", tournaments)

# Filtrar partidos por torneo
matches_for_team_tournament = matches_for_team[matches_for_team['tournament'] == selected_tournament]
matches_for_team_tournament = matches_for_team_tournament.sort_values(by=['round_number'], ascending=True)

# Selección del partido
match_names_list = matches_for_team_tournament['match_name'].tolist()
selected_match_name = st.selectbox(f"Selecciona el partido de {selected_team}", match_names_list)

# =======================
# Obtener datos del partido seleccionado
# =======================
selected_match = matches_for_team_tournament[matches_for_team_tournament['match_name'] == selected_match_name].iloc[0]
round_number = selected_match['round_number']
home_id = selected_match['home_id']
away_id = selected_match['away_id']

match_details = get_match_details(matches_for_team_tournament, round_number, home_id, away_id)

# =======================
# Crear pestañas con Streamlit
# =======================
tabs = st.tabs(["Detalles del Partido", "Análisis de Jugadores", "Análisis de Torneo"])

# =======================
# Pestaña: Detalles del Partido
# =======================
with tabs[0]:
    st.header(f"Detalles del partido")
    st.dataframe(match_details[['round_number', 'result', 'home', 'away', 'home_score', 'away_score', 'pain_points']])

    match_row = match_details.iloc[0]  # Seleccionar fila única

    # Extraer valores únicos como escalares
    home_score = match_row['home_score']
    away_score = match_row['away_score']
    pain_points = match_row['pain_points']

    fig = crear_grafico_indicador(home_score, away_score, pain_points)
    st.plotly_chart(fig)

    # Cargar estadísticas del partido
    round_data = load_round_statistics(selected_year, selected_tournament, round_number)
    if round_data:
        # Convertir claves a cadenas para asegurar compatibilidad
        selected_match_id = str(selected_match['match_id'])
        round_data = {str(key): value for key, value in round_data.items()}

        if selected_match_id in round_data:
            match_sheet_data = round_data[selected_match_id]
            
            # Filtrar y mostrar estadísticas diferenciadas por equipo
            home_stats = match_sheet_data[['key', 'name', 'homeValue', 'homeTotal', 'period', 'valueType', 'group', 'statisticsType']]
            away_stats = match_sheet_data[['key', 'name', 'awayValue', 'awayTotal', 'period', 'valueType', 'group', 'statisticsType']]

            st.write(f"**Estadísticas de {selected_match['home']}**")
            st.dataframe(home_stats)
            
            st.write(f"**Estadísticas de {selected_match['away']}**")
            st.dataframe(away_stats)
        else:
            st.warning(f"No se encontraron datos para el match_id: {selected_match_id}")

# =======================
# Pestaña: Análisis de Jugadores
# =======================
with tabs[1]:
    st.header("Análisis de Jugadores")
    players_data = load_round_player_statistics(selected_year, selected_tournament, round_number)
    if players_data:
        selected_match_id = str(selected_match['match_id'])  
        players_data = {str(key): value for key, value in players_data.items()}

        if selected_match_id in players_data:
            match_sheet_data = players_data[selected_match_id]
            
            # Mostrar un resumen de las estadísticas
            st.dataframe(match_sheet_data)

        else:
            st.warning(f"No se encontraron datos para el match_id: {selected_match_id}")

# =======================
# Pestaña: Análisis de Torneo
# =======================
with tabs[2]:
    st.header("Análisis de Torneo")
    # Crear un contenedor para el gráfico
    with st.container():
        if selected_tournament != "Primera Division, Grand Final":
            st.plotly_chart(generar_figura_pain_points(matches_for_team_tournament, selected_team, selected_tournament, selected_year), use_container_width=True)
            st.plotly_chart(generar_figura_resultados(matches_for_team_tournament), use_container_width=True)
