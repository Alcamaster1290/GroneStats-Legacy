import os
import pandas as pd
import ScraperFC

sofascore = ScraperFC.Sofascore()

# Parámetros de entrada
liga = 'Copa Libertadores' # 'Liga 1 Peru'

# Ruta del archivo Excel
base_path = f"GroneStats/GRONESTATS 1.0/{liga}"

# Definir el DataFrame para almacenar los datos del partido
matches_info_df = pd.DataFrame(columns=['match_id', 'match_url', 'home', 'home_id', 'home_score',
                                        'away', 'away_id', 'away_score', 'home_team_colors', 'away_team_colors',
                                        'tournament', 'round_number', 'season'])

# Iterar sobre los años de 2022 a 2024
for anio in range(2022, 2025):
    matches_info_df = None
    # Crear la ruta para cada año
    path = os.path.join(base_path, str(anio))
    if not os.path.exists(path):
        os.makedirs(path)

    cache_file = os.path.join(path, "0_Matches.xlsx")

    try:
        partidos = sofascore.get_match_dicts(str(anio), liga)
    except Exception as e:
        print(f"Error al obtener los datos para {anio}:", e)
        partidos = []

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
        homeScore = partido.get('homeScore', {}).get('current')
        awayScore = partido.get('awayScore', {}).get('current')
        
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
            'home_score': [homeScore],
            'away': [awayTeam],
            'away_id': [aid],
            'away_score': [awayScore],
            'home_team_colors': [f"Primary: {home_primary_color}, Secondary: {home_secondary_color}"],
            'away_team_colors': [f"Primary: {away_primary_color}, Secondary: {away_secondary_color}"],
            'tournament': [tournament],
            'round_number': [round_number],
            'season': [season],
        })

        matches_info_df = pd.concat([matches_info_df, match_info], ignore_index=True)

    # Guardar toda la información en una sola hoja de Excel por año
    with pd.ExcelWriter(cache_file, engine="openpyxl", mode="a", if_sheet_exists='replace') as writer:
        matches_info_df.to_excel(writer, index=False)

    print(f"Archivo Excel '{cache_file}' creado con éxito para el año {anio}.")

print("Proceso completado para los años 2022 a 2024.")