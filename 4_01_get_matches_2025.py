import os
import pandas as pd
import ScraperFC

sofascore = ScraperFC.Sofascore()

# Verificar si 2025 es una temporada válida para la liga
seasons = sofascore.get_valid_seasons('U20 CONMEBOL')  # Llamada a la función
if '2025' not in seasons:
    print("La temporada 2025 no está disponible para la liga.")
    exit()  # Sale del programa si la temporada no es válida
print(seasons)
# Parámetros de entrada
liga = 'U20 CONMEBOL'  # Cambia por 'Liga 1 Peru' si es necesario

# Ruta del archivo Excel
base_path = f"GroneStats/GRONESTATS 1.0/{liga}"

# Crear la carpeta para el año 2025 si no existe
anio = 2025
path = os.path.join(base_path, str(anio))
if not os.path.exists(path):
    os.makedirs(path)

# Ruta del archivo cache
cache_file = os.path.join(path, "0_Matches.xlsx")

# Crear el archivo vacío si no existe
if not os.path.exists(cache_file):
    with pd.ExcelWriter(cache_file, engine="openpyxl") as writer:
        # Crear un archivo Excel vacío con una hoja inicial
        pd.DataFrame().to_excel(writer, index=False, sheet_name='Matches')

# Definir el DataFrame para almacenar los datos del partido
matches_info_df = pd.DataFrame(columns=['match_id', 'match_url', 'home', 'home_id', 
                                        'away', 'away_id', 'home_team_colors', 'away_team_colors',
                                        'tournament', 'round_number', 'season'])

# Obtener los datos del año 2025
try:
    partidos = sofascore.get_match_dicts(str(anio), liga)
except Exception as e:
    print(f"Error al obtener los datos para {anio}:", e)
    partidos = []
print(partidos)
# Recolectar datos de cada partido
for partido in partidos:
    match_id = str(partido.get('id'))
    match_url = sofascore.get_match_url_from_id(match_id)
    tournament = partido.get('tournament', {}).get('name')
    season = partido.get('season', {}).get('name')
    round_number = partido.get('roundInfo', {}).get('round')
    hid = partido.get('homeTeam', {}).get('id')
    aid = partido.get('awayTeam', {}).get('id')
    homeTeam = partido.get('homeTeam', {}).get('name')
    awayTeam = partido.get('awayTeam', {}).get('name')
    
    # Obtener los colores de los equipos
    home_colors = partido.get('homeTeam', {}).get('teamColors', {})
    away_colors = partido.get('awayTeam', {}).get('teamColors', {})
    
    # Formatear los colores para exportarlos
    home_primary_color = home_colors.get('primary', '')
    home_secondary_color = home_colors.get('secondary', '')
    away_primary_color = away_colors.get('primary', '')
    away_secondary_color = away_colors.get('secondary', '')

    match_info = pd.DataFrame({
        'match_id': [match_id],
        'match_url': [match_url],
        'home': [homeTeam],
        'home_id': [hid],
        'away': [awayTeam],
        'away_id': [aid],
        'home_team_colors': [f"Primary: {home_primary_color}, Secondary: {home_secondary_color}"],
        'away_team_colors': [f"Primary: {away_primary_color}, Secondary: {away_secondary_color}"],
        'tournament': [tournament],
        'round_number': [round_number],
        'season': [season],
    })

    matches_info_df = pd.concat([matches_info_df, match_info], ignore_index=True)

# Guardar toda la información en una sola hoja de Excel
with pd.ExcelWriter(cache_file, engine="openpyxl", mode="a", if_sheet_exists='replace') as writer:
    matches_info_df.to_excel(writer, index=False, sheet_name='Matches')

print(f"Archivo Excel '{cache_file}' creado con éxito para el año {anio}.")
