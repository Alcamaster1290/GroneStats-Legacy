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
    }

def buscar_expulsados(ins, outs, opponent_ins, opponent_outs):
    """
    Busca jugadores expulsados y no reemplazados, y los elimina de outs y opponent_outs.
    
    Args:
        ins (DataFrame): Datos de los jugadores que ingresaron para el equipo seleccionado.
        outs (DataFrame): Datos de los jugadores que salieron para el equipo seleccionado.
        opponent_ins (DataFrame): Datos de los jugadores que ingresaron para el equipo oponente.
        opponent_outs (DataFrame): Datos de los jugadores que salieron para el equipo oponente.

    Returns:
        tuple: Lista de expulsados con minutos, outs sin expulsados, opponent_outs sin expulsados.
    """
    def expulsados_por_equipo(ins, outs):
        """
        Identifica jugadores expulsados y no reemplazados en un equipo.
        """
        expulsados = outs[~outs['minutesPlayed'].apply(
            lambda x: (90 - x) in ins['minutesPlayed'].values
        )]
        # Retorna nombres y minutos de expulsión
        return list(zip(expulsados['name'], expulsados['minutesPlayed']))

    # Verificar si las longitudes de ins y outs son distintas
    if len(ins) == len(outs):
        return [], outs, opponent_outs  # No hay expulsados si las longitudes son iguales

    # Identificar expulsados solo si las longitudes son diferentes
    local_expulsados = expulsados_por_equipo(ins, outs)
    away_expulsados = expulsados_por_equipo(opponent_ins, opponent_outs)

    # Combinar resultados
    expulsados = local_expulsados + away_expulsados

    # Eliminar expulsados de outs y opponent_outs
    outs_sin_expulsados = outs[~outs['name'].isin([e[0] for e in local_expulsados])].reset_index(drop=True)
    opponent_outs_sin_expulsados = opponent_outs[~opponent_outs['name'].isin([e[0] for e in away_expulsados])].reset_index(drop=True)

    return expulsados, outs_sin_expulsados, opponent_outs_sin_expulsados
