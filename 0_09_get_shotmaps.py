import LanusStats as ls
import pandas as pd
import os

sofascore = ls.SofaScore()
league_name = 'Liga 1 Peru'  # 'Copa Libertadores'

for year in range(2022, 2025):
    # Definir la ruta de matches y el directorio de salida
    matches_file_path = f"GRONESTATS 1.0/{league_name}/{year}/0_Matches.xlsx"
    output_directory = f"GRONESTATS 1.0/{league_name}/{year}/"

    # Crear el directorio de salida si no existe
    os.makedirs(output_directory, exist_ok=True)

    # Verificar si el archivo de partidos existe
    if not os.path.exists(matches_file_path):
        print(f"El archivo {matches_file_path} no existe para el año {year}.")
        continue  # Pasar al siguiente año si el archivo no existe

    # Leer los datos de los partidos
    matches_info_df = pd.read_excel(matches_file_path)

    # Obtener los torneos únicos
    unique_tournaments = matches_info_df['tournament'].unique()

    # Procesar cada torneo por separado
    for tournament in unique_tournaments:
        tournament_matches_df = matches_info_df[matches_info_df['tournament'] == tournament]

        # Crear un directorio para cada torneo
        tournament_output_directory = os.path.join(output_directory, tournament)
        os.makedirs(tournament_output_directory, exist_ok=True)

        # Iterar por cada partido en el torneo
        for index, match_row in tournament_matches_df.iterrows():
            match_url = match_row['match_url']
            match_id = match_row['match_id']
            round_number = match_row['round_number']

            try:
                match_shotmap_df = sofascore.get_match_shotmap(match_url)

                # Verificar si el DataFrame no está vacío
                if match_shotmap_df.empty:
                    print(f"Advertencia: No se obtuvieron datos para {match_id}")
                    continue
                
                output_file_path = os.path.join(tournament_output_directory, f"{round_number}_Shotmap.xlsx")
                
                # Escribir en el archivo Excel
                with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a' if os.path.exists(output_file_path) else 'w') as writer:
                    match_shotmap_df.to_excel(writer, sheet_name=str(match_id), index=False)

                print(f"Datos de equipos guardados para el partido {match_id} en {output_file_path} para el año {year}.")

            except Exception as e:
                print(f"Error al obtener datos para el partido {match_id} en {tournament} - Ronda {round_number}, año {year}: {e}")
                continue