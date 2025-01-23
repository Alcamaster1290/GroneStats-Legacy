import pandas as pd

# Leer el archivo Excel
file_path = 'LIGA 1 2025.xlsx'
teams_df = pd.read_excel(file_path, sheet_name='teams')
matches_df = pd.read_excel(file_path, sheet_name='matches')

# Función para calcular los pain points
def calculate_pain_points(local, visitante):
    # Inicializar los puntos de presión
    pain_points = 0
    
    # Si ambos equipos son rivales directos
    if local['rival_directo'] and visitante['rival_directo']:
        pain_points = 5
    # Si el local es rival directo y el visitante es de altura
    elif local['rival_directo'] and visitante['altura']:
        pain_points = 2
    # Si el local es rival directo y el visitante es de llano (implicado como no de altura)
    elif local['rival_directo'] and not visitante['altura']:
        pain_points = 1
    # Si el local es de altura y el visitante es rival directo
    elif local['altura'] and visitante['rival_directo']:
        pain_points = 4
    # Si el local es de altura y el visitante también es de altura
    elif local['altura'] and visitante['altura']:
        pain_points = 2
    # Si el local es de altura y el visitante no es rival directo (es de llano)
    elif local['altura'] and not visitante['rival_directo']:
        pain_points = 3
    # Si el local no es rival directo y el visitante es de altura (local de llano)
    elif not local['altura'] and visitante['altura'] and not visitante['rival_directo']:
        pain_points = 4
    # Si ambos son de llano (es decir, ninguno es rival directo ni de altura)
    elif not local['rival_directo'] and visitante['rival_directo']:
        pain_points = 3
    else:
        pain_points = 4

    return pain_points

# Crear un diccionario con la información de los equipos
team_info = dict(zip(teams_df['team_id'], zip(teams_df['rival_directo'], teams_df['altura'])))

# Función para obtener los datos de los equipos (local y visitante)
def get_team_info(team_id):
    if team_id in team_info:
        return {'rival_directo': team_info[team_id][0], 'altura': team_info[team_id][1]}
    else:
        return {'rival_directo': False, 'altura': False}  # Valor por defecto si no se encuentra el equipo

# Calcular los pain points para cada partido y agregarlos a la columna 'pain_points'
pain_points_list = []
for _, row in matches_df.iterrows():
    local_info = get_team_info(row['home_id'])
    visitante_info = get_team_info(row['away_id'])
    pain_points = calculate_pain_points(local_info, visitante_info)
    pain_points_list.append(pain_points)

# Asignar los pain points calculados a la columna 'pain_points' en el DataFrame de partidos
matches_df['pain_points'] = pain_points_list

# Imprimir el DataFrame actualizado
print(matches_df[['match_id', 'home_team', 'away_team', 'pain_points']])

# Si quieres guardar los resultados en un nuevo archivo Excel
matches_df.to_excel('LIGA_1_2025_con_pain_points.xlsx', index=False)

