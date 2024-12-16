import os
import pandas as pd

# Parámetro de liga
liga = 'Liga 1 Peru'  # Liga 1 Peru
output_dir = f"GroneStats/GRONESTATS 1.0/{liga}"

# Crear una lista para almacenar los DataFrames de cada año
all_matches_df = []

# Recorrer los años 2022 a 2024
for anio in range(2022, 2025):
    # Definir la ruta de matches y errores, y el directorio de salida
    matches_path = f"GroneStats/GRONESTATS 1.0/{liga}/{anio}/0_Matches.xlsx"
    errors_path = f"GroneStats/GRONESTATS 1.0/{liga}/{anio}/0_MatchesErrors.xlsx"
    
    # Verificar que ambos archivos existen antes de proceder
    if not os.path.exists(matches_path):
        print(f"El archivo {matches_path} no existe para el año {anio}.")
        continue

    matches_df = pd.read_excel(matches_path)

    if not os.path.exists(errors_path):
        print(f"El archivo {errors_path} no existe para el año {anio}.")
        all_matches_df.append(matches_df)
        continue
    
    # Eliminar filas con valores vacíos en home_score o away_score
    matches_df = matches_df.dropna(subset=['home_score', 'away_score'])


    errors_df = pd.read_excel(errors_path)

    if 'match_id' not in matches_df.columns or 'match_id' not in errors_df.columns:
        print(f"Error: Las columnas 'match_id' no se encuentran en los archivos de {anio}.")
        continue

    # Obtener los match_ids de errores
    error_match_ids = errors_df['match_id'].values

    # Eliminar las filas de matches_df que tengan un match_id presente en error_match_ids
    matches_clean_df = matches_df[~matches_df['match_id'].isin(error_match_ids)]

    # Agregar el DataFrame limpio del año al acumulado
    all_matches_df.append(matches_clean_df)

    print(f"Partidos del año {anio} procesados.")

# Concatenar todos los DataFrames en uno solo
final_matches_df = pd.concat(all_matches_df, ignore_index=True)

# Definir la ruta de salida para el archivo con todos los partidos válidos
matches_clean_path = os.path.join(output_dir, "1_Matches_Played.xlsx")

# Asegurarse de que el directorio de salida exista
os.makedirs(os.path.dirname(matches_clean_path), exist_ok=True)

# Guardar el archivo con todos los partidos válidos
final_matches_df.to_excel(matches_clean_path, index=False)

print(f"Archivo con todos los partidos válidos guardado en: {matches_clean_path}")
