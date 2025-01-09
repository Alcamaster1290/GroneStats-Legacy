# =======================
# Importar librerías y módulos
# =======================
import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
from streamlit_cache_funcs_liga1 import (
    load_data, extract_year_from_season, parse_years, 
    load_round_statistics, load_round_player_statistics, load_round_average_positions, 
    get_match_details, 
)
from streamlit_graphs_liga1 import (
    crear_grafico_score, 
    generar_grafico_lineas,
    imprimir_tarjetas,
    get_follow_up_graph,
    get_accumulated_graph,
    mostrar_tarjeta_pain_points,
    generar_html_equipo
)

st.set_page_config(
        page_title="GRONESTATS by AlvaroCC",
        layout='wide',
        page_icon=r'GRONESTATS 1.0\AL.png',
        initial_sidebar_state="expanded")

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
# Obtener datos del partido seleccionado selected_match_name
# =======================

selected_match = matches_for_team_tournament[matches_for_team_tournament['match_name'] == selected_match_name].iloc[0]
match_details = get_match_details(selected_match, selected_team)

# =======================
# Crear e imprimir las tarjetas
# =======================
imprimir_tarjetas(match_details, selected_team)
st.divider()

# =======================
# Imprimir escudo del equipo seleccionado
# =======================
image_url = match_details['image_url']

if os.path.exists(match_details['image_url']):
    st.sidebar.image(image_url)
else:
    st.sidebar.warning("Imagen no disponible para el equipo seleccionado.")

# Extraer valores únicos como escalares
home_score = match_details['home_score']
away_score = match_details['away_score']

home_team_color = match_details['home_team_colors']
home_primary_color = match_details['home_team_colors'].split(',')[0].split(':')[1].strip()
home_secondary_color = match_details['home_team_colors'].split(',')[1].split(':')[1].strip()

away_team_color = match_details['away_team_colors']
away_primary_color = match_details['away_team_colors'].split(',')[0].split(':')[1].strip()
away_secondary_color = match_details['away_team_colors'].split(',')[1].split(':')[1].strip()

pain_points = match_details['pain_points']
opponent_team = match_details['opponent_team']
round_number = match_details['round_number']

if match_details['condicion_selected'] == "Local":
    fig = crear_grafico_score(home_score, away_score, selected_team,opponent_team,pain_points)
elif match_details['condicion_selected'] == "Visitante":
    fig = crear_grafico_score(away_score, home_score, selected_team,opponent_team,pain_points)
with st.container():
    st.plotly_chart(fig, use_container_width= True)

# =======================
# Crear pestañas con Streamlit
# =======================
tabs = st.tabs(["Detalles del Partido", "Análisis de Jugadores", "Análisis de Torneo"])
# =======================
# Obtener posiciones promedio
# =======================
average_positions = load_round_average_positions(selected_year, selected_tournament, round_number)
if average_positions:
    selected_match_id = str(selected_match['match_id'])
    if selected_match_id in average_positions:
        average_position_df = average_positions[selected_match_id]
        # seleccionar id averageX averageY pointsCount
        average_position_df = average_position_df[['id', 'averageX', 'averageY', 'pointsCount', 'team']]
        selected_average_position_df = average_position_df[average_position_df['team'] == selected_team]
        opponent_average_position_df = average_position_df[average_position_df['team'] == opponent_team]
# =======================
# Pestaña: Detalles del Partido
# =======================
with tabs[0]:
    def filter_by_period(stats, period):
        return stats[stats['period'] == "ALL"] if period == "COMPLETO" else stats[stats['period'] == period]
    # Cargar y procesar datos
    round_data = load_round_statistics(selected_year, selected_tournament, round_number)
    if round_data:
        selected_match_id = str(selected_match['match_id'])

        if selected_match_id in round_data:
            match_sheet_data = round_data[selected_match_id]

            # Selección de columnas
            columns_to_show = ['key', 'name', 'homeValue', 'awayValue', 'period', 'valueType', 'group', 'statisticsType']
            home_stats = match_sheet_data[columns_to_show].rename(columns={'homeValue': 'Valor'})
            away_stats = match_sheet_data[columns_to_show].rename(columns={'awayValue': 'Valor'})

            # Selección del período con valor por defecto "COMPLETO"
            selected_period = st.segmented_control("Tiempo\n", ["COMPLETO", "1ST", "2ND"])
            selected_period = selected_period if selected_period else "COMPLETO"

            # Filtrar estadísticas por período
            home_stats = filter_by_period(home_stats, selected_period)
            away_stats = filter_by_period(away_stats, selected_period)

            # Validar tarjetas rojas
            red_cards_home = home_stats[home_stats['name'] == 'Red cards']['Valor'].sum()
            red_cards_away = away_stats[away_stats['name'] == 'Red cards']['Valor'].sum()
            # Validar tarjetas amarillas
            yellow_cards_home = home_stats[home_stats['name'] == 'Yellow cards']['Valor'].sum()
            yellow_cards_away = away_stats[away_stats['name'] == 'Yellow cards']['Valor'].sum()
            # Quita las filas de tarjetas rojas y amarillas
            home_stats = home_stats[~home_stats['name'].isin(['Red cards', 'Yellow cards'])]
            away_stats = away_stats[~away_stats['name'].isin(['Red cards', 'Yellow cards'])]

            home_stats = home_stats.sort_values(by='group')
            away_stats = away_stats.sort_values(by='group')
            
            html_local = generar_html_equipo(
                f"{selected_match['home']}",
                home_stats,
                color_primario=home_primary_color,  
                color_secundario=home_secondary_color,   
                red_cards=red_cards_home,
                yellow_cards=yellow_cards_home,
            )

            html_visitante = generar_html_equipo(
                f"{selected_match['away']}",
                away_stats,
                color_primario=away_primary_color, 
                color_secundario=away_secondary_color,   
                red_cards=red_cards_away,
                yellow_cards=yellow_cards_away,
            )

            # Contenedor principal para mostrar ambos equipos en tres columnas
            html_content = f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">{html_local}</div>
                    <div style="flex: 1;"></div>
                    <div style="flex: 1;">{html_visitante}</div>
                </div>
                """
            st.markdown(html_content, unsafe_allow_html=True)
            
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

            # Validar y limpiar la columna 'minutesPlayed'
            if 'minutesPlayed' in match_sheet_data.columns:
                match_sheet_data['minutesPlayed'] = pd.to_numeric(
                    match_sheet_data['minutesPlayed'], errors='coerce'
                ).fillna(0)  # Reemplazar valores no numéricos por 0
                match_sheet_data = match_sheet_data[
                    (match_sheet_data['minutesPlayed'] >= 0) &
                    (match_sheet_data['minutesPlayed'] <= 90)
                ]  # Filtrar valores fuera del rango [0, 90]
            else:
                match_sheet_data['minutesPlayed'] = 0

            # Filtrar datos por equipo
            try:
                team_stats = match_sheet_data[match_sheet_data['teamName'] == selected_team]
                opponent_stats = match_sheet_data[match_sheet_data['teamName'] == opponent_team]

                # Filtrar jugadores con minutos válidos - Equipo seleccionado
                players_stats = team_stats[team_stats['minutesPlayed'] > 0]
                selected_titulares = players_stats[players_stats['substitute'] == False]
                selected_ins = players_stats[players_stats['substitute'] == True]
                selected_outs = selected_titulares[selected_titulares['minutesPlayed'] < 90]

                # Filtrar jugadores con minutos válidos - Equipo rival
                opponent_players_stats = opponent_stats[opponent_stats['minutesPlayed'] > 0]
                opponent_titulares = opponent_players_stats[opponent_players_stats['substitute'] == False]
                opponent_ins = opponent_players_stats[opponent_players_stats['substitute'] == True]
                opponent_outs = opponent_titulares[opponent_titulares['minutesPlayed'] < 90]
                
                # Join con average_positions
                opponent_titulares = opponent_titulares.merge(opponent_average_position_df, on='id', how='left')
                selected_titulares = selected_titulares.merge(selected_average_position_df, on='id', how='left')
                selected_ins = selected_ins.merge(selected_average_position_df, on='id', how='left')
                selected_outs = selected_outs.merge(selected_average_position_df, on='id', how='left')
                opponent_ins = opponent_ins.merge(opponent_average_position_df, on='id', how='left')
                opponent_outs = opponent_outs.merge(opponent_average_position_df, on='id', how='left')
                
                selected_position = st.segmented_control("Posicion\n",options=["TODOS","DEFENSAS", "MEDIOCENTROS", "DELANTEROS"],default="TODOS")
                if selected_position == "DEFENSAS":
                    selected_position = "D"
                elif selected_position == "MEDIOCENTROS":
                    selected_position = "M"
                elif selected_position == "DELANTEROS":
                    selected_position = "F"
                if selected_position != "TODOS":
                    selected_titulares = selected_titulares[selected_titulares['position'] == selected_position]
                    selected_ins = selected_ins[selected_ins['position'] == selected_position]
                    selected_outs = selected_outs[selected_outs['position'] == selected_position]
                    opponent_titulares = opponent_titulares[opponent_titulares['position'] == selected_position]
                    opponent_ins = opponent_ins[opponent_ins['position'] == selected_position]
                    opponent_outs = opponent_outs[opponent_outs['position'] == selected_position]

                # Verificar si hay datos válidos
                if players_stats.empty and opponent_players_stats.empty:
                    st.warning("Sin datos a profundidad de los jugadores.")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader(f"Equipo titular {selected_team}")
                        st.dataframe(selected_titulares)
                        st.subheader(f"Ingresos")
                        st.dataframe(selected_ins)
                        st.subheader(f"Reemplazados")
                        st.dataframe(selected_outs)

                    with col2:
                        
                        st.subheader(f"Equipo titular {opponent_team}")
                        st.dataframe(opponent_titulares)
                        st.subheader(f"Ingresos")
                        st.dataframe(opponent_ins)
                        st.subheader(f"Reemplazados")
                        st.dataframe(opponent_outs)

            except Exception as e:
                st.error(f"Error procesando los datos: {str(e)}")
        else:
            st.warning(f"No se encontraron datos para el match_id: {selected_match_id}")
    else:
        st.error("No se pudo cargar la información de los jugadores.")


# =======================
# Pestaña: Análisis de Torneo
# =======================
with tabs[2]:
    st.header("Análisis de Torneo")
    # Crear un contenedor para el gráfico
    with st.container():
        if selected_tournament != "Primera Division, Grand Final" and selected_tournament != "Liga 1, Relegation/Promotion Playoffs":
            # Generar el gráfico de líneas (si es necesario)
            st.plotly_chart(generar_grafico_lineas(matches_for_team_tournament, selected_team, selected_tournament, selected_year, match_details))

            # Obtener los gráficos de seguimiento y acumulados
            seguimiento_graph = get_follow_up_graph(matches_for_team_tournament)
            acumulado_graph = get_accumulated_graph(matches_for_team_tournament)
            st.plotly_chart(seguimiento_graph, use_container_width= True)
            st.plotly_chart(acumulado_graph,  use_container_width= True)

            resultados = {
                "total_ajustado": round(matches_for_team_tournament['pain_points_ajustados'].sum()),
                "pain_points_posibles": round(matches_for_team_tournament['pain_points'].sum()*0.75),
                "total_result_selected": matches_for_team_tournament['result_selected'].sum()
            }
            st.subheader(f"Resumen de puntos para {selected_team}")
            st.write(f"Puntos Tradicionales obtenidos en {selected_tournament} {selected_year}:", resultados["total_result_selected"])
            st.write(f"Puntos de Presión obtenidos en {selected_tournament} {selected_year}:", resultados["total_ajustado"])
            st.write("Puntos de Presión necesarios para competir por el torneo:", resultados["pain_points_posibles"])
            mostrar_tarjeta_pain_points()
            st.warning(f"Próximamente: \n - Evolución de tabla de posiciones por ronda \n - Compara puntos de presión conseguidos con otros equipos")



