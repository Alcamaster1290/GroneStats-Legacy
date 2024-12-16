import pandas as pd
import os

# Ruta base del proyecto
base_path = r'GroneStats\\GRONESTATS 1.0\\Liga 1 Peru'

# Cargar los archivos de equipos y partidos
tteams_path = os.path.join(base_path, '1_Teams.xlsx')
matches_path = os.path.join(base_path, '1_Matches_Played.xlsx')

if not os.path.exists(tteams_path):
    raise FileNotFoundError(f"El archivo {tteams_path} no existe.")
if not os.path.exists(matches_path):
    raise FileNotFoundError(f"El archivo {matches_path} no existe.")

# Leer los datos
teams_df = pd.read_excel(tteams_path)
matches_df = pd.read_excel(matches_path)

# Convertir las columnas booleanas 'altura_team' y 'rival_team' a diccionarios para acceso rápido
altura_teams = set(teams_df.loc[teams_df['altura_team'], 'team_id'])
rival_teams = set(teams_df.loc[teams_df['rival_team'], 'team_id'])

# Crear la columna 'painpoints' en el DataFrame de partidos
def calculate_importance(row):
    if row['home_id'] in altura_teams and row['away_id'] in altura_teams:
        return 2
    if row['home_id'] in altura_teams and row['away_id'] in rival_teams:
        return 4
    if row['home_id'] not in rival_teams and row['home_id'] not in altura_teams and row['away_id'] in altura_teams:
        return 4
    if row['home_id'] in rival_teams and row['away_id'] in rival_teams:
        return 5
    if row['home_id'] in altura_teams and row['away_id'] not in rival_teams:
        return 1
    if row['home_id'] in rival_teams and row['away_id'] not in altura_teams and row['away_id'] not in rival_teams:
        return 0
    return 3

matches_df['pain_points'] = matches_df.apply(calculate_importance, axis=1)

# Agregar la columna 'result' según los puntajes de los equipos
def determine_result(row):
    if row['home_score'] > row['away_score']:
        return 'home'
    elif row['home_score'] < row['away_score']:
        return 'away'
    else:
        return 'draw'

matches_df['result'] = matches_df.apply(determine_result, axis=1)

# Agregar la columna 'match_name' como "home vs away"
matches_df['match_name'] = 'Jornada #' + matches_df['round_number'].astype(str) + ' | ' + matches_df['home'] + ' vs ' + matches_df['away'] + ' ' + matches_df['home_score'].astype(str) + ' - ' + matches_df['away_score'].astype(str)

# Guardar el resultado en el archivo de salida
output_path = os.path.join(base_path, '2_Matches_Detailed.xlsx')
matches_df.to_excel(output_path, index=False)

print(f"El archivo actualizado ha sido guardado en: {output_path}")
