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
