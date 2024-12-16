import os
import pandas as pd
import ScraperFC

sofascore = ScraperFC.Sofascore()

# Parámetros
liga = 'Copa Libertadores' # 'Liga 1 Peru'

for anio in range(2022, 2025):
    path = f"GroneStats/GRONESTATS 1.0/{liga}/{anio}/0_Matches.xlsx"
    output_path = f"GroneStats/GRONESTATS 1.0/{liga}/{anio}/0_Players.xlsx"
    errores_path = f"GroneStats/GRONESTATS 1.0/{liga}/{anio}/0_MatchesErrors.xlsx"

    # Lee archivo 0_Matches para obtener los jugadores participantes para cada año
    if not os.path.exists(path):
        print(f"El archivo {path} no existe.")
        continue
    else:
        matches_info_df = pd.read_excel(path)

    # Crear un DataFrame vacío para almacenar los datos de los jugadores
    players_data = pd.DataFrame(columns=['player_id', 'name', 'slug', 'team_id'])

    # Crear un DataFrame para almacenar errores
    errores_data = pd.DataFrame(columns=['match_id', 'match_url', 'error_message'])

    # Recorrer cada fila en matches_info_df
    for index, row in matches_info_df.iterrows():
        match_id = row['match_id']
        match_url = row['match_url']

        try:
            # Obtener estadísticas de los jugadores del encuentro
            player_stats_df = sofascore.scrape_player_match_stats(match_id)

            # Verificar si player_stats_df contiene columnas necesarias y no está vacío
            if player_stats_df.empty or not all(col in player_stats_df.columns for col in ['id', 'name', 'slug', 'teamId']):
                raise ValueError(f"Las columnas necesarias no están presentes o el DataFrame está vacío para {match_id}: {player_stats_df.columns if not player_stats_df.empty else 'DataFrame vacío'}.")

            # Seleccionar y renombrar las columnas
            selected_columns = player_stats_df[['id', 'name', 'slug', 'teamId']].rename(columns={'id': 'player_id', 'teamId': 'team_id'})

            # Concatenar al DataFrame players_data
            players_data = pd.concat([players_data, selected_columns], ignore_index=True)
        
        except Exception as e:
            error_message = str(e)
            print(f"Error al obtener datos para el partido {match_id}: {error_message}")

            # Guardar el error en el DataFrame de errores
            errores_data = pd.concat([errores_data, pd.DataFrame({'match_id': [match_id], 'match_url': [match_url], 'error_message': [error_message]})], ignore_index=True)
            continue

    # Guardar en Excel la relación de equipos y jugadores
    players_data.drop_duplicates(inplace=True)  # Eliminar filas duplicadas si existen
    players_data.to_excel(output_path, index=False)
    print(f"Archivo Excel '{output_path}' creado con éxito.")

    # Guardar los errores en un archivo Excel
    if not errores_data.empty:
        errores_data.to_excel(errores_path, index=False)
        print(f"Archivo Excel '{errores_path}' creado con éxito.")
    else:
        print("No se encontraron errores durante la ejecución.")
