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
    get_match_details, load_match_momentum,
    load_shotmaps, obtener_formacion, mostrar_tiros_y_goles, 
)
from streamlit_graphs_liga1 import (
    crear_grafico_score, 
    generar_grafico_lineas,
    imprimir_tarjetas,
    get_follow_up_graph,
    get_accumulated_graph,
    mostrar_tarjeta_pain_points,
    generar_html_equipo,
    get_grafico_match_momentum,
    generar_formacion_basica,
    graficar_tiros_al_arco,
    graficar_posicion_tiros_a_puerta,
    graficar_posicion_tiros_fuera,
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
selected_match_id = str(selected_match['match_id'])

# =======================
# Imprimir escudo del equipo seleccionado
# =======================
image_url = match_details['image_url']

if os.path.exists(match_details['image_url']):
    st.sidebar.image(image_url)
else:
    st.sidebar.warning("Imagen no disponible para el equipo seleccionado.")

# =======================
# Crear e imprimir las tarjetas
# =======================
imprimir_tarjetas(match_details, selected_team)
st.divider()

# Extraer valores únicos como escalares
home_id = match_details['home_id']
away_id = match_details['away_id']

home_name = match_details['home']
away_name = match_details['away']

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
condicion = match_details['condicion_selected']

# =======================
# Crear e imprimir score 
# =======================
if condicion== "Local":
    fig = crear_grafico_score(home_score, away_score, selected_team,opponent_team,pain_points)
elif condicion == "Visitante":
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
    if selected_match_id in average_positions:
        average_position_df = average_positions[selected_match_id]
        # seleccionar id averageX averageY pointsCount
        average_position_df = average_position_df[['id', 'averageX', 'averageY', 'pointsCount', 'team']]
        selected_average_position_df = average_position_df[average_position_df['team'] == selected_team]
        opponent_average_position_df = average_position_df[average_position_df['team'] == opponent_team]
    else: 
        selected_average_position_df = pd.DataFrame()
        opponent_average_position_df = pd.DataFrame()
# =======================
# Obtener Momentum de Presion
# =======================
round_momentums = load_match_momentum(selected_year, selected_tournament, round_number)
if round_momentums:
    if selected_match_id in round_momentums:
        match_momentum = round_momentums[selected_match_id]
    else:
        match_momentum = pd.DataFrame()
# =======================
# Obtener Shotmap
# =======================
shotmaps = load_shotmaps(selected_year, selected_tournament, round_number)
if shotmaps:
    if selected_match_id in shotmaps:
        shotmap = shotmaps[selected_match_id]
    else:
        shotmap = pd.DataFrame()

# =======================
# Obtener Detalles del Partido (Estadísticas)
# =======================
round_data = load_round_statistics(selected_year, selected_tournament, round_number)
if round_data:
    match_sheet_data = round_data[selected_match_id]
    # Selección de columnas
    columns_to_show = ['key', 'name', 'homeValue', 'awayValue', 'period', 'valueType', 'group', 'statisticsType']
    home_stats = match_sheet_data[columns_to_show].rename(columns={'homeValue': 'Valor'})
    away_stats = match_sheet_data[columns_to_show].rename(columns={'awayValue': 'Valor'})
    # Diferenciar entre selected y opponnent
    home_stats['team'] = home_name
    away_stats['team'] = away_name
    if home_stats['team'].iloc[0] == selected_team:
        home_stats['team'] = selected_team
        away_stats['team'] = opponent_team


else:
    st.error("No se pudo cargar la información del partido.")

# =======================
# Obtener Analisis de Jugadores (Estadísticas)
# =======================

players_data = load_round_player_statistics(selected_year, selected_tournament, round_number)
players_data = {str(key): value for key, value in players_data.items()}

if selected_match_id in players_data:
    minutos_dectados = False
    player_sheet_data = players_data[selected_match_id]

    ini_columns = ['id', 'teamId', 'teamName', 'name', 'shirtNumber', 'position', 'substitute', 'captain'] # No todos tienen 'height'
    player_sheet_data_ini = player_sheet_data[ini_columns]

    base_columns = ['minutesPlayed', 'goals','goalAssist', 'rating',
                    'accuratePass', 'totalPass', 'keyPass', 'accurateLongBalls', 'totalLongBalls', 'accurateCross', 'totalCross', 
                    'duelWon', 'duelLost', 'dispossessed', 'wasFouled', 'touches', 'possessionLostCtrl',  
                    'aerialWon', 'aerialLost', 'wonContest', 'totalContest', 'challengeLost',
                    'totalOffside', 'totalClearance', 'interceptionWon', 'totalTackle',
                    'fouls', 'saves', 'onTargetScoringAttempt', 'shotOffTarget', 'blockedScoringAttempt']
    for column in base_columns:
        if column in player_sheet_data.columns:
            player_sheet_data_ini[column] = pd.to_numeric(player_sheet_data[column], errors='coerce').fillna(0)
            if column == 'minutesPlayed':
                minutos_dectados = True
            else:
                continue

    extra_columns = ['redCards','yellowCards','goodHighClaim', 'savedShotsFromInsideTheBox','totalKeeperSweeper', 'accurateKeeperSweeper',
                        'bigChanceMissed', 'bigChanceCreated',
                        'outfielderBlock',
                        'penaltyConceded',
                        'hitWoodwork']
    
    for column in extra_columns:
        if column in player_sheet_data.columns:
            player_sheet_data_ini[column] = pd.to_numeric(player_sheet_data[column], errors='coerce').fillna(0)
        else:
            continue

    players_stats = player_sheet_data_ini[player_sheet_data_ini['teamName'] == selected_team].reset_index(drop=True)
    opponent_players_stats = player_sheet_data_ini[player_sheet_data_ini['teamName'] == opponent_team].reset_index(drop=True)

    # Filtrar jugadores con minutos válidos - Equipo seleccionado
    selected_titulares = players_stats[players_stats['substitute'] == False]
    selected_ins = players_stats[players_stats['substitute'] == True]
    # Filtrar jugadores con minutos válidos - Equipo rival
    opponent_titulares = opponent_players_stats[opponent_players_stats['substitute'] == False]
    opponent_ins = opponent_players_stats[opponent_players_stats['substitute'] == True]

    if minutos_dectados:
        selected_ins = selected_ins[selected_ins['minutesPlayed'] > 0]
        opponent_ins = opponent_ins[opponent_ins['minutesPlayed'] > 0]
        selected_outs = selected_titulares[selected_titulares['minutesPlayed'] < 90]
        opponent_outs = opponent_titulares[opponent_titulares['minutesPlayed'] < 90]
    else:
        selected_outs = pd.DataFrame()
        opponent_outs = pd.DataFrame()

## JOINS DE JUGADORES ##

if not selected_average_position_df.empty and not opponent_average_position_df.empty:
    opponent_titulares = opponent_titulares.merge(opponent_average_position_df, on='id', how='left')
    selected_titulares = selected_titulares.merge(selected_average_position_df, on='id', how='left')
    selected_ins = selected_ins.merge(selected_average_position_df, on='id', how='left')
    selected_outs = selected_outs.merge(selected_average_position_df, on='id', how='left')
    opponent_ins = opponent_ins.merge(opponent_average_position_df, on='id', how='left')
    opponent_outs = opponent_outs.merge(opponent_average_position_df, on='id', how='left')
else:
    with tabs[1]:
        st.warning("No se registraron posiciones promedio para los jugadores en este partido.")
# =======================
# PESTAÑAS DE STREAMLIT
# =======================
# =======================
# Pestaña: Detalles del Partido
# =======================
with tabs[0]:
    @st.cache_data
    def filter_by_period(stats, period):
        return stats[stats['period'] == "ALL"] if period == "COMPLETO" else stats[stats['period'] == period]
    
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
    yellow_cards_away = away_stats[home_stats['name'] == 'Yellow cards']['Valor'].sum()
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
        color_secundario= away_secondary_color,   
        red_cards=red_cards_away,
        yellow_cards=yellow_cards_away,
    )

    # Contenedor principal para mostrar ambos equipos en tres columnas
    col1, col2, col3 = st.columns([1, 4, 1])

    # Mostrar equipo local en la primera columna
    with col1:
        st.markdown(html_local, unsafe_allow_html=True)

    with col2:

        if match_momentum.empty:
            st.empty()
        else:
            fig = get_grafico_match_momentum(
            df=match_momentum,
            color_home=home_primary_color,
            color_away=away_primary_color,
            selected_team=selected_team,
            opponent_team=opponent_team,
            condicion_selected=condicion
            )
            st.plotly_chart(fig, use_container_width=True)

        if shotmap.empty:
            st.warning('Sin datos de tiros.')
        else:
            resultados = mostrar_tiros_y_goles(shotmap, condicion, selected_team, opponent_team)
            f1, f2 = st.columns(2)

            with f1:
                df_tiros_ot_local = resultados['tiros_al_arco_local']
                df_tiros_off_local = resultados['tiros_fuera_local']
                graficar_tiros_al_arco(df_tiros_ot_local, 'local')
                graficar_posicion_tiros_a_puerta(df_tiros_ot_local, 'local')
                graficar_posicion_tiros_fuera(df_tiros_off_local, 'local')

            with f2:
                df_tiros_ot_away = resultados['tiros_al_arco_away']
                df_tiros_off_away = resultados['tiros_fuera_away']
                graficar_tiros_al_arco(df_tiros_ot_away, 'visitante')
                graficar_posicion_tiros_a_puerta(df_tiros_ot_away, 'visitante')
                graficar_posicion_tiros_fuera(df_tiros_off_away, 'visitante')
        

    # Mostrar equipo visitante en la tercera columna
    with col3:
        st.markdown(html_visitante, unsafe_allow_html=True)

# =======================
# Pestaña: Análisis de Jugadores
# =======================

with tabs[1]:
    st.header("Análisis de Jugadores")
    
    selected_formacion = obtener_formacion(selected_titulares)
    equipo_titular = selected_titulares 
    st.text(f"Formación inicial de {selected_team}: {selected_formacion}")
    opponent_formacion = obtener_formacion(opponent_titulares)
    st.text(f"Formación inicial de {opponent_team}: {opponent_formacion}")
    fig = generar_formacion_basica(selected_formacion, equipo_titular)

    try:
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
            opponent_titulares = opponent_titulares[opponent_titulares['position'] == selected_position]
            opponent_ins = opponent_ins[opponent_ins['position'] == selected_position]
            if minutos_dectados:
                selected_ins = selected_ins[selected_ins['minutesPlayed'] != 0]
                opponent_ins = opponent_ins[opponent_ins['minutesPlayed'] != 0]
                selected_outs = selected_outs[selected_outs['position'] == selected_position]
                opponent_outs = opponent_outs[opponent_outs['position'] == selected_position]

        # Verificar si hay datos válidos
        if players_stats.empty and opponent_players_stats.empty:
            st.warning("Sin datos a profundidad de los jugadores.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"Equipo titular {selected_team}")
                st.dataframe(selected_titulares)
                if selected_outs.empty and not selected_ins.empty:
                    st.subheader(f"Suplentes")
                    st.dataframe(selected_ins)
                elif not selected_ins.empty:
                    st.subheader(f"Ingresos")
                    st.dataframe(selected_ins)
                if not selected_outs.empty:
                    st.subheader(f"Cambios / Expulsados")
                    st.dataframe(selected_outs)

            with col2:
                if not shotmap.empty:
                    st.warning("Aqui se mostrara el mapa del campo con las posiciones promedio y hexbins de tiros al arco")
                if selected_outs.empty and not selected_ins.empty:
                    st.write("Formación Inicial")
                    st.pyplot(fig,use_container_width=True)

            with col3:
                st.markdown(f"Equipo titular {opponent_team}")
                st.dataframe(opponent_titulares)
                if opponent_outs.empty and not opponent_ins.empty:
                    st.subheader(f"Suplentes")
                    st.dataframe(opponent_ins)
                elif not opponent_ins.empty:
                    st.subheader(f"Ingresos")
                    st.dataframe(opponent_ins)
                if not opponent_outs.empty:
                    st.subheader(f"Cambios / Expulsados")
                    st.dataframe(opponent_outs)

    except Exception as e:
        st.error(f"Error procesando los datos: {str(e)}")


# =======================
# Pestaña: Análisis de Torneo
# =======================
with tabs[2]:
    st.header("Análisis de Torneo")
    # Crear un contenedor para el gráfico
    with st.container():
        if selected_tournament != "Primera Division, Grand Final" and selected_tournament != "Liga 1, Relegation/Promotion Playoffs":

            st.plotly_chart(generar_grafico_lineas(matches_for_team_tournament, selected_team, selected_tournament, selected_year, match_details, round_number))

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