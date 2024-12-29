import os
import pandas as pd
import ScraperFC

# Crear una instancia de sofascore
sofascore = ScraperFC.Sofascore()

# Parámetros
liga = 'Liga 1 Peru'  # 'Copa Libertadores'

for anio in range(2022, 2025):
    # Definir la ruta de matches y el directorio de salida
    matches_path = f"GRONESTATS 1.0/{liga}/{anio}/0_Matches.xlsx"
    output_dir = f"GRONESTATS 1.0/{liga}/{anio}/"

    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Verificar si el archivo de partidos existe
    if not os.path.exists(matches_path):
        print(f"El archivo {matches_path} no existe para el año {anio}.")
        continue  # Pasar al siguiente año si el archivo no existe

    # Leer los datos de los partidos
    matches_info_df = pd.read_excel(matches_path)

    # Obtener los torneos únicos
    unique_tournaments = matches_info_df['tournament'].unique()

    # Procesar cada torneo por separado
    for tournament in unique_tournaments:
        tournament_matches = matches_info_df[matches_info_df['tournament'] == tournament]

        # Crear un directorio para cada torneo
        tournament_output_dir = os.path.join(output_dir, tournament)
        os.makedirs(tournament_output_dir, exist_ok=True)

        # Iterar por cada partido en el torneo
        for index, row in tournament_matches.iterrows():
            match_id = row['match_id']
            round_number = row['round_number']

            try:
                # Obtener los heatmaps de los jugadores para el partido
                heatmap_data = sofascore.scrape_heatmaps(match_id)

                # Verificar si se obtuvieron datos
                if not heatmap_data:
                    print(f"Advertencia: No se obtuvieron datos para el partido {match_id} en el año {anio}.")
                    continue
                
                # Convertir el diccionario de heatmaps en un DataFrame
                heatmap_list = []
                for player_id, heatmap in heatmap_data.items():
                    heatmap_list.append({'player_id': player_id, 'heatmap': heatmap})
                
                df_heatmaps = pd.DataFrame(heatmap_list)

                # Guardar los datos en un archivo Excel, con una hoja nombrada según match_id
                output_file_path = os.path.join(tournament_output_dir, f"{round_number}_Heatmaps.xlsx")
                
                # Escribir en el archivo Excel
                with pd.ExcelWriter(output_file_path, engine='openpyxl', mode='a' if os.path.exists(output_file_path) else 'w') as writer:
                    df_heatmaps.to_excel(writer, sheet_name=str(match_id), index=False)

                print(f"Datos de heatmap guardados para el partido {match_id} en {output_file_path} para el año {anio}.")

            except Exception as e:
                print(f"Error al obtener datos para el partido {match_id} en {tournament} - Ronda {round_number}, año {anio}: {e}")
                continue
