import os
import pandas as pd
import ScraperFC

sofascore = ScraperFC.Sofascore()

# Parámetros
liga = 'Copa Libertadores'  # 'Liga 1 Peru'

for anio in range(2022, 2025):
    # Definir rutas con base en liga y año
    base_path = f"GroneStats/GRONESTATS 1.0/{liga}/{anio}"
    players_path = f"{base_path}/0_Players.xlsx"
    matches_path = f"{base_path}/0_Matches.xlsx"
    teams_path = f"{base_path}/0_Teams.xlsx"

    if not os.path.exists(players_path):
        print(f"El archivo {players_path} no existe.")
        continue  

    # Leer la información de jugadores y partidos
    players_info_df = pd.read_excel(players_path)
    matches_info_df = pd.read_excel(matches_path)

    # Obtener 'team_id' únicos de players_info_df
    team_ids_from_players = players_info_df['team_id'].unique()

    # Obtener 'home' y 'away' de matches_info_df
    home_teams = matches_info_df[['home_id', 'home']].drop_duplicates()
    away_teams = matches_info_df[['away_id', 'away']].drop_duplicates()

    # Unir los IDs de equipos de jugadores y partidos
    all_team_ids = pd.Series(pd.concat([pd.Series(team_ids_from_players), home_teams['home_id'], away_teams['away_id']])).unique()
    
    # Crear un DataFrame para los equipos
    teams_data = pd.DataFrame(all_team_ids, columns=['team_id'])

    # Asignar nombres de equipos utilizando los DataFrames de partidos
    teams_data = teams_data.merge(home_teams, how='left', left_on='team_id', right_on='home_id')
    teams_data = teams_data.merge(away_teams, how='left', left_on='team_id', right_on='away_id')

    # Extraer el nombre del equipo, prefiriendo el nombre de 'home' si existe
    teams_data['team_name'] = teams_data['home'].combine_first(teams_data['away'])

    # Limpiar el DataFrame para conservar solo las columnas necesarias
    teams_data = teams_data[['team_id', 'team_name']].drop_duplicates()

    # Guardar el DataFrame en un archivo Excel
    teams_data.to_excel(teams_path, index=False)
    print(f"Archivo Excel '{teams_path}' creado con éxito.")
