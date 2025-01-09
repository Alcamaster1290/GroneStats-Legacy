import pandas as pd
import ast
import os

# Función para leer los archivos y extraer las coordenadas de los heatmaps
def extract_coordinates_from_excel(file_path):
    # Leer el archivo Excel
    xls = pd.ExcelFile(file_path)
    
    # Diccionario para almacenar los datos: partido -> jugador -> coordenadas
    data = {}
    
    # Recorrer cada hoja (cada partido)
    for sheet_name in xls.sheet_names:
        # Leer la hoja con el nombre 'match_id'
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Diccionario para almacenar las coordenadas por jugador
        player_coordinates = {}
        
        # Recorrer las filas para extraer el diccionario y las coordenadas
        for _, row in df.iterrows():
            # Evaluar el diccionario de la columna 'heatmap'
            heatmap_dict = ast.literal_eval(row['heatmap'])
            
            # Extraer el player_id y las coordenadas
            player_name = row['player_id']
            player_id = heatmap_dict['id']
            coordinates = heatmap_dict['heatmap']
            
            # Verificar si hay coordenadas, si es vacío, se omite
            if not coordinates:  # Si no tiene coordenadas 'x' y 'y'
                continue
            
            # Almacenar las coordenadas en el diccionario del jugador
            player_coordinates[player_id] = coordinates
        
        # Almacenar las coordenadas de los jugadores en cada partido
        data[sheet_name] = player_coordinates
    
    return data 

# Ruta donde se encuentran los archivos Excel
directory_path = 'GRONESTATS 1.0/Liga 1 Peru/2024/Primera Division, Clausura'

# Leer todos los archivos de Excel
all_data = {}
for i in range(1, 21):  # Asumimos que hay 20 archivos numerados del 1 al 20
    file_name = f'{i}_Heatmaps.xlsx'
    file_path = os.path.join(directory_path, file_name)
    
    if os.path.exists(file_path):
        all_data[i] = extract_coordinates_from_excel(file_path)
    else:
        print(f"El archivo {file_name} no se encontró.")

# Imprimir un ejemplo de las coordenadas de los primeros partidos
for round_number, match_data in all_data.items():
    print(f"Ronda {round_number}:")
    for match_id, player_data in match_data.items():
        print(f"  Partido {match_id}:")
        for player_id, coordinates in player_data.items():
            print(f"    Jugador {player_id}: {coordinates[:2]}...")  # Muestra las primeras 2 coordenadas
