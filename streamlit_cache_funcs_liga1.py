import pandas as pd
import re
import streamlit as st

@st.cache_data
def load_data():
    """
    Carga los datos de los partidos y equipos desde archivos de Excel.
    """
    matches = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\2_Matches_Detailed.xlsx")
    teams = pd.read_excel(r"GRONESTATS 1.0\Liga 1 Peru\1_Teams.xlsx")
    return matches, teams

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

def get_match_details(matches_for_team_tournament, round_number, home_id, away_id):
    """
    Filtra los detalles del partido basado en round_number, home_id y away_id.
    """
    match_details = matches_for_team_tournament[
        (matches_for_team_tournament['round_number'] == round_number) &
        (matches_for_team_tournament['home_id'] == home_id) &
        (matches_for_team_tournament['away_id'] == away_id)
    ]
    return match_details
