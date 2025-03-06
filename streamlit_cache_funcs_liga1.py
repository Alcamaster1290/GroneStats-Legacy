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

def procesar_tiros(df_shotmaps, condicion):
    df_shotmaps['color'] = df_shotmaps['shotType'].apply(apply_color_based_on_shot_type)
    shots_on_target = ['save', 'goal']
    shots_off_target = ['miss', 'post', 'block']
    df_shots_on_target = df_shotmaps[df_shotmaps['shotType'].isin(shots_on_target)]
    df_shots_off_target = df_shotmaps[df_shotmaps['shotType'].isin(shots_off_target)]
    if condicion == 'Local':
        df_shots_on_target_local = df_shots_on_target[df_shots_on_target['isHome']]
        df_shots_on_target_away = df_shots_on_target[~df_shots_on_target['isHome']]
        df_shots_off_target_local = df_shots_off_target[df_shots_off_target['isHome']]
        df_shots_off_target_away = df_shots_off_target[~df_shots_off_target['isHome']]
    else:
        df_shots_on_target_local = df_shots_on_target[~df_shots_on_target['isHome']]
        df_shots_on_target_away = df_shots_on_target[df_shots_on_target['isHome']]
        df_shots_off_target_local = df_shots_off_target[~df_shots_off_target['isHome']]
        df_shots_off_target_away = df_shots_off_target[df_shots_off_target['isHome']]
    
    return df_shots_on_target_local, df_shots_on_target_away, df_shots_off_target_local, df_shots_off_target_away

def mostrar_tiros_y_goles(df_shotmaps, condicion, selected_team, opponent_team):
    # Procesar los tiros y obtener los DataFrames
    df_shots_on_target_local, df_shots_on_target_away, df_shots_off_target_local, df_shots_off_target_away = procesar_tiros(
        df_shotmaps, condicion)

    # Determinar los DataFrames según la condición
    if condicion == 'Local':
        df_shots_on_target_selected = df_shots_on_target_local
        df_shots_on_target_opponent = df_shots_on_target_away
        df_shots_off_target_selected = df_shots_off_target_local
        df_shots_off_target_opponent = df_shots_off_target_away
    else:
        df_shots_on_target_selected = df_shots_on_target_away
        df_shots_on_target_opponent = df_shots_on_target_local
        df_shots_off_target_selected = df_shots_off_target_away
        df_shots_off_target_opponent = df_shots_off_target_local
    
    import pandas as pd
import streamlit as st

def procesar_tiros_y_goles(df_shotmap, df_average_positions, selected_team, opponent_team, condicion):
    """
    Procesa los tiros y goles, y los muestra en Streamlit.
    
    Parámetros:
        df_shotmap (pd.DataFrame): DataFrame con los datos de los tiros.
        df_average_positions (pd.DataFrame): DataFrame con las posiciones promedio de los jugadores.
        selected_team (str): Nombre del equipo seleccionado.
        opponent_team (str): Nombre del equipo oponente.
        condicion (str): Condición del equipo seleccionado ("Local" o "Visitante").
    
    Retorna:
        dict: Diccionario con los DataFrames de tiros al arco y fuera del arco para ambos equipos.
    """
    # Aplicar colores basados en el tipo de tiro
    df_shotmap['color'] = df_shotmap['shotType'].apply(apply_color_based_on_shot_type)
    
    # Definir categorías de tiros
    shots_on_target = ['save', 'goal']  # Tiros al arco
    shots_off_target = ['miss', 'post', 'block']  # Tiros fuera del arco
    
    # Filtrar tiros al arco y fuera del arco
    df_shots_on_target = df_shotmap[df_shotmap['shotType'].isin(shots_on_target)]
    df_shots_off_target = df_shotmap[df_shotmap['shotType'].isin(shots_off_target)]
    
    # Separar tiros al arco y fuera del arco por equipo local y visitante
    df_shots_on_target_selected = df_shots_on_target[df_shots_on_target['isHome'] == (condicion == "Local")]
    df_shots_on_target_opponent = df_shots_on_target[df_shots_on_target['isHome'] != (condicion == "Local")]
    df_shots_off_target_selected = df_shots_off_target[df_shots_off_target['isHome'] == (condicion == "Local")]
    df_shots_off_target_opponent = df_shots_off_target[df_shots_off_target['isHome'] != (condicion == "Local")]
    
    # Procesar goles
    goals_df = df_shotmap[df_shotmap['shotType'] == 'goal']
    
    if not goals_df.empty:
        # Extraer y mostrar los goles
        st.subheader("Goles")
        goals_df = goals_df.sort_values(by='time')
        goles_por_equipo = {selected_team: [], opponent_team: []}

        for _, row in goals_df.iterrows():
            minute = f"{row['time']}'"
            if 'addedTime' in row and not pd.isna(row["addedTime"]):  # Verificar si hay tiempo añadido
                minute = f"{row['time']}+{int(row['addedTime'])}'"
            if row['situation'] == 'penalty':
                minute += " (Penal)"
            if row['goalType'] == 'own':
                minute += " (AG)"
            
            # Determinar el equipo según las condiciones
            if row["isHome"]:
                equipo = selected_team if condicion == "Local" else opponent_team
            else:
                equipo = opponent_team if condicion == "Local" else selected_team
            
            # Agregar al equipo correspondiente
            goles_por_equipo[equipo].append(f"{row['name']} - {minute}")
        
        e1, e2 = st.columns(2)
        
        # Mostrar goles en columnas
        equipos = [(selected_team if condicion == "Local" else opponent_team, e1), 
                   (opponent_team if condicion == "Local" else selected_team, e2)]

        for equipo, column in equipos:
            with column:
                for gol in goles_por_equipo[equipo]:
                    st.markdown(f"- {gol}")

    st.divider()

    # Devolver los DataFrames de tiros al arco y fuera para ambos equipos
    return {
        'tiros_al_arco_local': df_shots_on_target_selected,
        'tiros_al_arco_away': df_shots_on_target_opponent,
        'tiros_fuera_local': df_shots_off_target_selected,
        'tiros_fuera_away': df_shots_off_target_opponent
    }

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

# Código para cargar el archivo Excel en Streamlit
uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        xls = pd.ExcelFile(uploaded_file)

        # Asignar cada hoja a un DataFrame
        df_team_stats = pd.read_excel(xls, sheet_name='Team Stats')
        df_player_stats = pd.read_excel(xls, sheet_name='Player Stats')
        df_average_positions = pd.read_excel(xls, sheet_name='Average Positions')
        df_shotmap = pd.read_excel(xls, sheet_name='Shotmap')
        df_match_momentum = pd.read_excel(xls, sheet_name='Match Momentum')
        
        # Verificar si la hoja 'Heatmap' existe antes de intentar leerla
        if 'Heatmap' in xls.sheet_names:
            df_heatmaps = pd.read_excel(xls, sheet_name='Heatmap')
        else:
            df_heatmaps = pd.DataFrame()  # DataFrame vacío si no existe la hoja

        # Ejemplo de uso de la función procesar_tiros_y_goles
        selected_team = "Equipo Local"  # Cambiar por el nombre del equipo seleccionado
        opponent_team = "Equipo Visitante"  # Cambiar por el nombre del equipo oponente
        condicion = "Local"  # Cambiar por "Local" o "Visitante"

        resultados = procesar_tiros_y_goles(df_shotmap, df_average_positions, selected_team, opponent_team, condicion)

        # Mostrar resultados adicionales si es necesario
        st.write("Tiros al arco (Local):")
        st.dataframe(resultados['tiros_al_arco_local'])
        st.write("Tiros al arco (Visitante):")
        st.dataframe(resultados['tiros_al_arco_away'])
        st.write("Tiros fuera del arco (Local):")
        st.dataframe(resultados['tiros_fuera_local'])
        st.write("Tiros fuera del arco (Visitante):")
        st.dataframe(resultados['tiros_fuera_away'])

    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")

