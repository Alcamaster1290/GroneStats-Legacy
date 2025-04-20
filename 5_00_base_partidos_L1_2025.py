import os
import pandas as pd
import logging
import ScraperFC

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scraper_liga1.log"),
        logging.StreamHandler()
    ]
)

sofascore = ScraperFC.Sofascore()

# Parámetros de entrada
liga = 'Liga 1 Peru'
base_path = f"GRONESTATS 1.0/{liga}"

# Iterar sobre los años de 2022 a 2024
for anio in range(2024, 2026):
    path = os.path.join(base_path, str(anio))
    cache_file = os.path.join(path, "0_Matches.xlsx")

    if os.path.exists(cache_file):
        logging.info(f"Archivo ya existe para {anio}, se omite scraping.")
        continue

    matches_info_df = pd.DataFrame(columns=[
        'match_id', 'match_url', 'home', 'home_id', 'home_score',
        'away', 'away_id', 'away_score', 'home_team_colors', 'away_team_colors',
        'tournament', 'tournament_id', 'round_number', 'season', 'season_id'
    ])

    try:
        partidos = sofascore.get_match_dicts(str(anio), liga)
        logging.info(f"{len(partidos)} partidos encontrados para {liga} en {anio}")
    except Exception as e:
        logging.error(f"Error al obtener los datos para {anio}: {e}")
        continue

    for partido in partidos:
        try:
            match_id = str(partido.get('id'))
            match_url = sofascore.get_match_url_from_id(match_id)
            tournament = partido.get('tournament', {}).get('name')
            tournament_id = partido.get('tournament', {}).get('id')
            season = partido.get('season', {}).get('name')
            season_id = partido.get('season', {}).get('id')
            round_number = partido.get('roundInfo', {}).get('round')
            hid = partido.get('homeTeam', {}).get('id')
            aid = partido.get('awayTeam', {}).get('id')
            homeTeam = partido.get('homeTeam', {}).get('name')
            awayTeam = partido.get('awayTeam', {}).get('name')
            homeScore = partido.get('homeScore', {}).get('current')
            awayScore = partido.get('awayScore', {}).get('current')

            home_colors = partido.get('homeTeam', {}).get('teamColors', {})
            away_colors = partido.get('awayTeam', {}).get('teamColors', {})
            home_primary_color = home_colors.get('primary', '')
            home_secondary_color = home_colors.get('secondary', '')
            away_primary_color = away_colors.get('primary', '')
            away_secondary_color = away_colors.get('secondary', '')

            # Verificar si ambos puntajes están vacíos, y si es así, eliminarlo y logearlo
            if not homeScore and not awayScore:
                logging.info(f"Partido con ID {match_id} entre {homeTeam} y {awayTeam} no tiene puntajes. Se omite.")
                continue

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
                'tournament_id': [tournament_id],
                'round_number': [round_number],
                'season': [season],
                'season_id': [season_id]
            })

            matches_info_df = pd.concat([matches_info_df, match_info], ignore_index=True)

        except Exception as e:
            logging.warning(f"Error al procesar partido con ID {partido.get('id')}: {e}")
            continue
    
    # Verifica si el archivo existe
    if not os.path.exists(cache_file):
        writer_mode = "w"  # Escribir nuevo archivo
    else:
        writer_mode = "a"  # Agregar a archivo existente

    # Al momento de escribir, si el archivo existe, usa el parámetro 'if_sheet_exists'
    with pd.ExcelWriter(cache_file, engine="openpyxl", mode=writer_mode) as writer:
        if writer_mode == "a":
            # Solo cuando el archivo ya existe, puedes reemplazar hojas
            matches_info_df.to_excel(writer, index=False, sheet_name='Partidos', if_sheet_exists='replace')
        else:
            # Si es nuevo, no se necesita 'if_sheet_exists'
            matches_info_df.to_excel(writer, index=False, sheet_name='Partidos')

logging.info(f"Archivo Excel '{cache_file}' creado con éxito para el año {anio}.")