import pandas as pd
import os

# Ruta base del proyecto
base_path = r'GroneStats\GRONESTATS 1.0\Liga 1 Peru'

# Años de los archivos
years = [2022, 2023, 2024]

# Listas de team_id para las columnas booleanas
altura_team_ids = [87854, 458584, 63760, 33895, 2301, 335557, 252254, 275839, 33894]
rival_team_ids = [2311, 2302, 2308, 2305]

# Diccionario para almacenar los años por team_id
years_by_team = {}

# Leer los archivos y agregar los datos al diccionario
for year in years:
    file_path = os.path.join(base_path, str(year), '0_Teams.xlsx')
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        for team_id in df['team_id']:
            if team_id not in years_by_team:
                years_by_team[team_id] = []
            years_by_team[team_id].append(year)
    else:
        print(f"El archivo para el año {year} no existe en la ruta: {file_path}")

# Crear un DataFrame a partir del diccionario
data = []
for team_id, years_list in years_by_team.items():
    data.append({'team_id': team_id, 'years': ', '.join(map(str, years_list))})
teams_df = pd.DataFrame(data)

# Agregar team_name desde los archivos originales
for year in years:
    file_path = os.path.join(base_path, str(year), '0_Teams.xlsx')
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        teams_df = teams_df.merge(df[['team_id', 'team_name']], on='team_id', how='left')

# Combinar columnas team_name en una sola columna y eliminarlas
teams_df['team'] = teams_df[['team_name_x', 'team_name_y', 'team_name']].bfill(axis=1).iloc[:, 0]
teams_df = teams_df.drop(columns=['team_name_x', 'team_name_y', 'team_name'])

# Agregar columnas booleanas
teams_df['altura_team'] = teams_df['team_id'].isin(altura_team_ids)
teams_df['rival_team'] = teams_df['team_id'].isin(rival_team_ids)

# Guardar el resultado en un nuevo archivo Excel
output_path = os.path.join(base_path, '1_Teams.xlsx')
teams_df.to_excel(output_path, index=False)

print(f"El archivo final ha sido guardado en: {output_path}")
