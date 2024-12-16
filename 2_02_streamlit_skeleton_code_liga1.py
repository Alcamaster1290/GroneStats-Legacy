import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go

# Título de la aplicación
st.title('GRONESTATS 1.0')

# Función para cargar archivos de Excel con cacheo de datos
@st.cache_data
def load_data():
    """
    Carga los datos de los partidos y equipos desde archivos de Excel.
    """
    matches = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\2_Matches_Detailed.xlsx")
    teams = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\1_Teams.xlsx")
    return matches, teams

# Función para extraer el año de una columna con formato de texto
def extract_year_from_season(season):
    """
    Extrae el año de una cadena de texto que representa la temporada.
    """
    match = re.search(r'\d{4}', season)  # Buscar un año de 4 dígitos
    return int(match.group(0)) if match else None

# Función para procesar la columna 'years' de los equipos
def parse_years(x):
    """
    Convierte la columna 'years' en una lista de años.
    """
    if isinstance(x, str):
        return [int(year.strip()) for year in x.split(",")]
    elif isinstance(x, int):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        return []

# Cargar y preparar los datos
matches, teams = load_data()

# Preparar los años disponibles en la columna 'season'
matches['season_year'] = matches['season'].apply(extract_year_from_season)
years = sorted(matches['season_year'].unique())  # Lista de años ordenados

# Procesar y filtrar los equipos por año
teams['parsed_years'] = teams['years'].apply(parse_years)

# Sidebar para filtros
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

# Filtro adicional por torneo
tournaments = sorted(matches_for_team['tournament'].unique())
selected_tournament = st.sidebar.selectbox("Selecciona un torneo", tournaments)

# Filtrar partidos por torneo
matches_for_team_tournament = matches_for_team[matches_for_team['tournament'] == selected_tournament]
matches_for_team_tournament = matches_for_team_tournament.sort_values(by=['round_number'], ascending=True)

# Selección del partido
match_names_list = matches_for_team_tournament['match_name'].tolist()
selected_match_name = st.selectbox(f"Selecciona el partido de {selected_team}", match_names_list)

# Obtener datos del partido seleccionado
selected_match = matches_for_team_tournament[matches_for_team_tournament['match_name'] == selected_match_name].iloc[0]
round_number = selected_match['round_number']
home_id = selected_match['home_id']
away_id = selected_match['away_id']

# Función para cargar estadísticas por jornada desde un archivo
@st.cache_data
def load_round_statistics(year_selected, torneo_selected, round_number):
    """
    Carga las estadísticas por equipo de un archivo Excel basado en el año, torneo y jornada.
    """
    file_path = f"GRONESTATS 1.0/Liga 1 Peru/{year_selected}/{torneo_selected}/{round_number}_Teams.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
        return data
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {file_path}")
        return None

# Función para cargar estadísticas de jugadores por jornada desde un archivo
@st.cache_data
def load_round_player_statistics(year_selected, torneo_selected, round_number):
    """
    Carga las estadísticas por jugador de un archivo Excel basado en el año, torneo y jornada.
    """
    file_path = f"GRONESTATS 1.0/Liga 1 Peru/{year_selected}/{torneo_selected}/{round_number}_Players.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
        return data
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {file_path}")
        return None

# Función para obtener los detalles del partido
def get_match_details(round_number, home_id, away_id):
    """
    Filtra los detalles del partido basado en round_number, home_id y away_id.
    """
    match_details = matches_for_team_tournament[(matches_for_team_tournament['round_number'] == round_number) & 
                                                (matches_for_team_tournament['home_id'] == home_id) & 
                                                (matches_for_team_tournament['away_id'] == away_id)]
    return match_details

# Obtener los detalles del partido seleccionado
match_details = get_match_details(round_number, home_id, away_id)

# Crear pestañas con Streamlit
tabs = st.tabs(["Detalles del Partido", "Análisis de Jugadores", "Análisis de Torneo"])

# Pestaña: Detalles del Partido
with tabs[0]:
    st.header(f"Detalles del partido")
    st.write(match_details[['round_number', 'result', 'home', 'away', 'home_score', 'away_score', 'pain_points']])

    match_row = match_details.iloc[0]  # Seleccionar fila única

    # Extraer valores únicos como escalares
    home_score = match_row['home_score']
    away_score = match_row['away_score']
    pain_points = match_row['pain_points']

    # Crear gráfico indicador
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=home_score,  # Asegurarte de que sea un número, no una Serie
        title={"text": "Goles Local"},
        delta={'reference': away_score, 'relative': False},
        domain={'row': 0, 'column': 0}
    ))

    fig.add_trace(go.Indicator(
        mode="number",
        value=pain_points,  # Escalar único para los pain_points
        title={"text": "Puntos Clave"},
        domain={'row': 1, 'column': 0}
    ))

    # Configurar diseño
    fig.update_layout(
        grid={'rows': 2, 'columns': 1, 'pattern': "independent"},
        template="plotly_dark"
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


    # Cargar estadísticas del partido
    round_data = load_round_statistics(selected_year, selected_tournament, round_number)
    if round_data:
        # Convertir claves a cadenas para asegurar compatibilidad
        selected_match_id = str(selected_match['match_id'])
        round_data = {str(key): value for key, value in round_data.items()}

        if selected_match_id in round_data:
            match_sheet_data = round_data[selected_match_id]
            
            # Mostrar estadísticas generales del partido
            st.dataframe(match_sheet_data)

            # Filtrar y mostrar estadísticas diferenciadas por equipo
            home_stats = match_sheet_data[['name', 'homeValue', 'homeTotal']].dropna()
            away_stats = match_sheet_data[['name', 'awayValue', 'awayTotal']].dropna()

            st.write(f"**Estadísticas de {selected_match['home']}**")
            st.dataframe(home_stats)
            
            st.write(f"**Estadísticas de {selected_match['away']}**")
            st.dataframe(away_stats)
        else:
            st.warning(f"No se encontraron datos para el match_id: {selected_match_id}")

    # Gráfico 1: Pain Points vs Round Number    
    # Crear gráfico con round_number en el eje X y pain_points en el eje Y
    fig1 = go.Figure()

    # Ordenar los datos por número de ronda
    matches_for_team_tournament = matches_for_team_tournament.sort_values(by=['round_number'], ascending=False)

    # Agregar línea de puntos para 'pain_points'
    fig1.add_trace(go.Scatter(
        x=matches_for_team_tournament['round_number'], 
        y=matches_for_team_tournament['pain_points'], 
        mode='lines+markers', 
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name='Pain Points'
    ))

    # Mejorar la presentación del gráfico
    fig1.update_layout(
        title=f"Dificultad de victoria para {selected_team} en {selected_tournament} {selected_year}",
        xaxis_title="Número de Ronda",
        yaxis_title="Pain Points",
        yaxis=dict(range=[-0.9, 5.1]),  # Fijar el rango del eje Y de 0 a 5
        template="plotly_dark",  # Estilo de fondo oscuro
        plot_bgcolor="rgb(50, 50, 50)",  # Fondo oscuro para el gráfico
        font=dict(color="white"),  # Texto en blanco para mejor contraste
        hovermode="closest"  # Mostrar solo el punto más cercano al cursor
    )

    # Gráfico 2: Resultado de los partidos vs Round Number
    
    # Asignar valores numéricos a la columna 'result'
    result_map = {'home': 1, 'draw': 0, 'away': -1}
    matches_for_team_tournament['result_numeric'] = matches_for_team_tournament['result'].map(result_map)

    # Ordenar los datos por número de ronda
    matches_df = matches_for_team_tournament.sort_values(by=['round_number'], ascending=True)

    # Crear gráfico con round_number en el eje X y 'result_numeric' en el eje Y
    fig2 = go.Figure()

    # Agregar línea de puntos para 'result_numeric'
    fig2.add_trace(go.Scatter(
        x=matches_df['round_number'], 
        y=matches_df['result_numeric'], 
        mode='lines+markers', 
        marker=dict(color='blue', size=8),
        line=dict(color='blue', width=2),
        name='Resultado'
    ))

    # Mejorar la presentación del gráfico
    fig2.update_layout(
        title="Resultados de los partidos por ronda",
        xaxis_title="Número de Ronda",
        yaxis_title="Resultado (1=Home, 0=Draw, -1=Away)",
        yaxis=dict(tickvals=[-1, 0, 1], ticktext=['Away', 'Draw', 'Home']),  # Muestra las etiquetas como 'Away', 'Draw', 'Home'
        template="plotly_dark",  # Estilo de fondo oscuro
        plot_bgcolor="rgb(50, 50, 50)",  # Fondo oscuro para el gráfico
        font=dict(color="white"),  # Texto en blanco para mejor contraste
        hovermode="closest"  # Mostrar solo el punto más cercano al cursor
    )

# Pestaña de Análisis de Jugadores
with tabs[1]:
    st.header("Análisis de Jugadores")
    players_data = load_round_player_statistics(selected_year, selected_tournament, round_number)
    if players_data:
        selected_match_id = str(selected_match['match_id'])  
        # Asegurarte de que las claves del diccionario round_data son cadenas
        players_data = {str(key): value for key, value in players_data.items()}

        if selected_match_id in players_data:
            match_sheet_data = players_data[selected_match_id]
            
            # Mostrar un resumen de las estadísticas
            st.dataframe(match_sheet_data)

        else:
            st.warning(f"No se encontraron datos para el match_id: {selected_match_id}")


# Pestaña de Análisis de Temporada
with tabs[2]:
    st.header("Análisis de Torneo")
    # Crear un contenedor para el gráfico
    with st.container():
        if selected_tournament != "Primera Division, Grand Final":
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)
