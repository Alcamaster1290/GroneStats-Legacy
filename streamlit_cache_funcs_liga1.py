import pandas as pd
import re
import streamlit as st
import os

@st.cache_data
def load_data():
    """
    Carga los datos de los partidos y equipos desde archivos de Excel.
    """
    matches = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\2_Matches_Detailed.xlsx")
    teams = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\1_Teams.xlsx")
    return matches, teams
@st.cache_data
def get_team_id(team_name):
    """
    Obtiene el nombre del equipo en base al 'team_name'.
    """
    teams_df = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\1_Teams.xlsx")
    team_name = teams_df.loc[teams_df['team'] == team_name, 'team_id'].values
    return team_name[0] if team_name else None

def extract_year_from_season(season):
    """
    Extrae el año de una cadena de texto que representa la temporada.
    """
    match = re.search(r'\d{4}', season)  # Buscar un año de 4 dígitos
    return int(match.group(0)) if match else None

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
    
# Función para aplicar colores basados en el tipo de tiro
def apply_color_based_on_shot_type(shot_type):
    if shot_type == 'block':
        return 'coral'
    elif shot_type == 'miss':
        return 'darkred'
    elif shot_type == 'goal':
        return 'darkgreen'
    elif shot_type in ['save', 'post']:
        return 'darkgoldenrod'
    else:
        return 'gray'

@st.cache_data
def load_round_average_positions(year_selected, torneo_selected, round_number):
    """
    Carga las estadísticas por equipo de un archivo Excel basado en el año, torneo y jornada.
    """
    file_path = f"GRONESTATS 1.0/Liga 1 Peru/{year_selected}/{torneo_selected}/{round_number}_AveragePositions.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
        return data
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {file_path}")
        return None

@st.cache_data
def load_match_momentum (year_selected, torneo_selected, round_number):
    """
    Carga los datos de momentum de un archivo Excel basado en el año, torneo, jornada y match_id.
    """
    file_path = f"GRONESTATS 1.0/Liga 1 Peru/{year_selected}/{torneo_selected}/{round_number}_Momentum.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
        return data
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {file_path}")
        return None

@st.cache_data
def load_shotmaps (year_selected, torneo_selected, round_number):
    """
    Carga los datos de shotmap de un archivo Excel basado en el año, torneo, jornada y match_id.
    """
    file_path = f"GRONESTATS 1.0/Liga 1 Peru/{year_selected}/{torneo_selected}/{round_number}_Shotmap.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        data = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
        return data
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {file_path}")
        return None

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
@st.cache_data
def get_match_details(selected_match, selected_team):
    """
    Obtiene detalles del partido seleccionado y genera la información necesaria para renderizar en Streamlit.

    Parameters:
        selected_match (pd.Series): Información del partido seleccionado.
        selected_team (str): Nombre del equipo seleccionado.

    Returns:
        dict: Diccionario con los datos del partido, incluyendo condición, resultado, colores y más.
    """
    match_id = selected_match['match_id']
    round_number = selected_match['round_number']
    home_id = selected_match['home_id']
    home = selected_match['home']
    away = selected_match['away']
    away_id = selected_match['away_id']
    home_score = selected_match['home_score']
    away_score = selected_match['away_score']
    pain_points = selected_match['pain_points']
    home_team_colors = selected_match['home_team_colors']
    away_team_colors = selected_match['away_team_colors']

    # Determinar la condición del equipo seleccionado
    if selected_team == selected_match['home']:
        condicion_selected = "Local"
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
        selected_id = None
        opponent_team = None

    # Determinar el color del texto según el resultado
    if resultado_selected == "Victoria":
        color_texto = "#28a745"  # Verde para victoria
    elif resultado_selected == "Empate":
        color_texto = "#ffc107"  # Amarillo para empate
    else:
        color_texto = "#dc3545"  # Rojo para derrota

    # Ruta de la imagen
    image_path = r"GRONESTATS 1.0\Liga 1 Peru\images\teams"
    image_filename = f"{selected_id}.png" 
    image_url = os.path.join(image_path, image_filename)

    return {
        "match_id": match_id,
        "home": home,
        "away": away,
        "round_number": round_number,
        "home_id": home_id,
        "away_id": away_id,
        "condicion_selected": condicion_selected,
        "resultado_selected": resultado_selected,
        "color_texto": color_texto,
        "selected_id": selected_id,
        "opponent_team": opponent_team,
        "image_url": image_url,
        "home_score": home_score ,
        "away_score" :away_score ,
        "pain_points" : pain_points,
        "home_team_colors": home_team_colors,
        "away_team_colors": away_team_colors,
    }

def obtener_formacion(df_xi_titular):
    # Inicializar los contadores para defensores, mediocampistas y delanteros
    defensores = 0
    mediocampistas = 0
    delanteros = 0
    
    # Contar las posiciones en el dataframe
    for _, row in df_xi_titular.iterrows():
        if row['position'] == 'D':  # Defensores
            defensores += 1
        elif row['position'] == 'M':  # Mediocampistas
            mediocampistas += 1
        elif row['position'] == 'F':  # Delanteros
            delanteros += 1
        elif row['position'] == 'G':  # Arquero
            continue  # El arquero no cuenta para la formación

    # Ajustar mediocampistas y defensores si hay más de 5 mediocampistas
    if mediocampistas > 5:
        mediocampistas -= 2  # Restar 2 mediocampistas
        defensores += 2      # Sumar esos 2 al contador de defensores

    # Crear la cadena de la formación: 'D-M-F'
    formacion = f"{defensores}-{mediocampistas}-{delanteros}"
    
    return formacion

def procesar_tiros(df_shotmap, condicion):
    # Aplicar colores basados en el tipo de tiro
    df_shotmap['color'] = df_shotmap['shotType'].apply(apply_color_based_on_shot_type)

    # Categorías de tiros
    shots_on_target = ['save', 'goal']
    shots_off_target = ['miss', 'post', 'block']

    # Filtrar
    df_shots_on_target = df_shotmap[df_shotmap['shotType'].isin(shots_on_target)]
    df_shots_off_target = df_shotmap[df_shotmap['shotType'].isin(shots_off_target)]

    # Condición booleana
    es_local = condicion == "Local"

    return {
        "tiros_al_arco_local": df_shots_on_target[df_shots_on_target['isHome'] == es_local],
        "tiros_al_arco_away": df_shots_on_target[df_shots_on_target['isHome'] != es_local],
        "tiros_fuera_local": df_shots_off_target[df_shots_off_target['isHome'] == es_local],
        "tiros_fuera_away": df_shots_off_target[df_shots_off_target['isHome'] != es_local],
        "goles": df_shotmap[df_shotmap['shotType'] == 'goal']
    }


def mostrar_tiros_y_goles(df_shotmap, selected_team, opponent_team, condicion):
    resultados = procesar_tiros(df_shotmap, condicion)

    # Mostrar tiros
    #st.subheader("Tiros al arco")
    #st.dataframe(resultados["tiros_al_arco_local"], use_container_width=True)
    #st.dataframe(resultados["tiros_al_arco_away"], use_container_width=True)

    #st.subheader("Tiros fuera del arco")
    #st.dataframe(resultados["tiros_fuera_local"], use_container_width=True)
    #st.dataframe(resultados["tiros_fuera_away"], use_container_width=True)

    # Mostrar goles
    goles_df = resultados["goles"]
    if not goles_df.empty:
        st.subheader("Goles")
        goles_por_equipo = {selected_team: [], opponent_team: []}
        for _, row in goles_df.iterrows():
            minuto = f"{row['time']}'"
            if 'addedTime' in row and not pd.isna(row["addedTime"]):
                minuto = f"{row['time']}+{int(row['addedTime'])}'"
            if row['situation'] == 'penalty':
                minuto += " (Penal)"
            if row['goalType'] == 'own':
                minuto += " (AG)"

            if row["isHome"]:
                equipo = selected_team if condicion == "Local" else opponent_team
            else:
                equipo = opponent_team if condicion == "Local" else selected_team

            goles_por_equipo[equipo].append(f"{row['name']} - {minuto}")

        e1, e2 = st.columns(2)
        for equipo, col in [(selected_team if condicion == "Local" else opponent_team, e1),
                            (opponent_team if condicion == "Local" else selected_team, e2)]:
            with col:
                for gol in goles_por_equipo[equipo]:
                    st.markdown(f"- {gol}")
