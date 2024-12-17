# =======================
# Importar librerías y módulos
# =======================
import streamlit as st
import os
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
match_id = selected_match['match_id']
round_number = selected_match['round_number']
home_id = selected_match['home_id']
away_id = selected_match['away_id']

# Determinar la condición del equipo seleccionado
if selected_team == selected_match['home']:
    condicion_selected = "Local"
    # Si el equipo seleccionado es el de casa (home), comprobamos si ganó, empató o perdió
    if selected_match['result'] == 'home':
        resultado_selected = "Victoria"
    elif selected_match['result'] == 'away':
        resultado_selected = "Derrota"
    else:
        resultado_selected = "Empate"
    selected_id = home_id
    opponent_team = selected_match['away']

elif selected_team == selected_match['away']:
    condicion_selected = "Visitante"
    # Si el equipo seleccionado es el visitante (away), comprobamos si ganó, empató o perdió
    if selected_match['result'] == 'away':
        resultado_selected = "Victoria"
    elif selected_match['result'] == 'home':
        resultado_selected = "Derrota"
    else:
        resultado_selected = "Empate"
    selected_id = away_id
    opponent_team = selected_match['home']
else:
    condicion_selected = "No encontrado"
    resultado_selected = "No disponible"

if resultado_selected == "Victoria":
        color_texto = "#28a745"  # Verde para victoria
elif resultado_selected == "Empate":
    color_texto = "#ffc107"  # Amarillo para empate
else:
    color_texto = "#dc3545"  # Rojo para derrota

# Crear dos columnas y colocar la tarjeta en la columna izquierda
col1, col2 = st.columns([2, 1])  # Ajustar proporciones de columnas

with col1:
    # Mostrar la tarjeta en la columna izquierda
    st.markdown(
        f"""
        <div style="
            display: flex; 
            align-items: left; 
            justify-content: center; 
            border: 1px solid #444; 
            border-radius: 8px; 
            padding: 10px 20px; 
            background-color: transparent; 
            color: #eee; 
            margin-top: 20px; 
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.6);"
        >
            <h2 style="font-size: 18px; margin: 0; color: #bbb;">{selected_team} en condición de {condicion_selected}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

# Crear la tarjeta para mostrar el resultado en la columna derecha
with col2:
    st.markdown(
        f"""
        <div style="
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border: 1px solid #444; 
            border-radius: 8px; 
            padding: 10px 20px; 
            background-color: transparent; 
            color: {color_texto}; 
            margin-top: 20px; 
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.6);"
        >
            <h2 style="font-size: 18px; margin: 0; color: {color_texto};">Resultado: </h2>
            <p style="font-size: 18px; font-weight: bold; margin: 0; color: {color_texto};">{resultado_selected}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

image_path = r"GRONESTATS 1.0\Liga 1 Peru\images\teams"
image_filename = f"{selected_id}.png" 
image_url = os.path.join(image_path, image_filename)

if os.path.exists(image_url):
    st.sidebar.image(image_url)
else:
    st.sidebar.warning("Imagen no disponible para el equipo seleccionado.")

match_details = get_match_details(matches_for_team_tournament, round_number, home_id, away_id)

match_row = match_details.iloc[0]  # Seleccionar fila única

# Extraer valores únicos como escalares
home_score = match_row['home_score']
away_score = match_row['away_score']
pain_points = match_row['pain_points']

if condicion_selected == "Local":
    fig = crear_grafico_indicador(home_score, away_score, selected_team,opponent_team,pain_points)
elif condicion_selected == "Visitante":
    fig = crear_grafico_indicador(away_score, home_score, selected_team,opponent_team,pain_points)
with st.container():
    st.plotly_chart(fig)

# =======================
# Crear pestañas con Streamlit
# =======================
tabs = st.tabs(["Detalles del Partido", "Análisis de Jugadores", "Análisis de Torneo"])

# =======================
# Pestaña: Detalles del Partido
# =======================
with tabs[0]:
    #st.header(f"Detalles del partido")
    #st.dataframe(match_details[['round_number', 'result', 'home', 'away', 'home_score', 'away_score', 'pain_points']])

    def filter_by_period(stats, period):
        return stats[stats['period']=="ALL"] if period == "ALL" else stats[stats['period'] == period]

    # Cargar y procesar datos
    round_data = load_round_statistics(selected_year, selected_tournament, round_number)
    if round_data:
        selected_match_id = str(selected_match['match_id'])
        
        if selected_match_id in round_data:
            match_sheet_data = round_data[selected_match_id]
            
            # Selección de columnas
            columns_to_show = ['key', 'name', 'homeValue', 'awayValue', 'period','valueType', 'group', 'statisticsType']
            home_stats = match_sheet_data[columns_to_show].rename(columns={'homeValue': 'Valor Local'})
            away_stats = match_sheet_data[columns_to_show].rename(columns={'awayValue': 'Valor Visitante'})
            # Selección del período con valor por defecto "ALL"
            selected_period = st.segmented_control(" ", ["ALL", "1ST", "2ND"])
            selected_period = selected_period if selected_period else "ALL"

            # Filtrar estadísticas por período
            home_stats = filter_by_period(home_stats, selected_period)
            away_stats = filter_by_period(away_stats, selected_period)

            home_stats = home_stats.sort_values(by='group')
            away_stats = away_stats.sort_values(by='group')

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**LOCAL : {selected_match['home']}**")
                st.table(home_stats[['name', 'Valor Local','group']])

            with col2:
                st.write(f"**VISITANTE : {selected_match['away']}**")
                st.table(away_stats[['name', 'Valor Visitante', 'group']])
        else:
            st.warning(f"No se encontraron datos para el match_id: {selected_match_id}")
    else:
        st.error("No se pudo cargar la información de la jornada seleccionada.")

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
