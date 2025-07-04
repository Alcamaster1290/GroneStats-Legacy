import os
import pandas as pd

def procesar_shotmaps(carpeta):
    """
    Lee todos los archivos XLSX en una carpeta y concatena las hojas 'Shotmap'
    
    Args:
        carpeta (str): Ruta a la carpeta con los archivos XLSX
        
    Returns:
        pd.DataFrame: DataFrame con todos los disparos concatenados
    """
    # Lista para almacenar todos los DataFrames de shotmap
    shotmaps = []
    
    # Recorrer todos los archivos en la carpeta
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.xlsx'):
            try:
                # Leer el archivo Excel
                ruta_completa = os.path.join(carpeta, archivo)
                
                # Extraer información del nombre del archivo
                nombre_partido = os.path.splitext(archivo)[0]
                partes_nombre = nombre_partido.split('_')
                jornada = partes_nombre[0][1:]  # Eliminar la 'J' inicial
                equipos = partes_nombre[1].split('vs')
                equipo_local = equipos[0]
                equipo_visitante = equipos[1]
                
                # Leer la hoja Shotmap
                df_shotmap = pd.read_excel(ruta_completa, sheet_name='Shotmap')
                
                # Añadir metadatos del partido
                df_shotmap['Jornada'] = jornada
                df_shotmap['Equipo Local'] = equipo_local
                df_shotmap['Equipo Visitante'] = equipo_visitante
                df_shotmap['Archivo'] = archivo
                
                # Agregar a la lista
                shotmaps.append(df_shotmap)
                
            except Exception as e:
                print(f"Error procesando {archivo}: {str(e)}")
                continue
    
    # Concatenar todos los DataFrames
    if shotmaps:
        df_final = pd.concat(shotmaps, ignore_index=True)
        
        # Procesar columnas relevantes
        if 'player' in df_final.columns:
            # Extraer información del diccionario de jugador
            df_final['Jugador'] = df_final['player'].apply(lambda x: x.get('name', '') if isinstance(x, dict) else '')
            df_final['Posicion'] = df_final['player'].apply(lambda x: x.get('position', '') if isinstance(x, dict) else '')
            df_final['Dorsal'] = df_final['player'].apply(lambda x: x.get('jerseyNumber', '') if isinstance(x, dict) else '')
        
        return df_final
    else:
        return pd.DataFrame()

# Ejemplo de uso
if __name__ == "__main__":
    carpeta_partidos = r'Partidos Gaspar Gentile'
    df_disparos = procesar_shotmaps(carpeta_partidos)
    
    if not df_disparos.empty:
        
        # Mostrar un resumen de los datos
        print("\nResumen de disparos:")
        print(df_disparos[['Jornada', 'name', 'shotType', 'situation', 'id_1']].head())

        id_seleccionado = 895364 # ID de Gaspar Gentile

        # Filtrar por el ID del jugador
        df_disparos = df_disparos[df_disparos['id_1'] == id_seleccionado]

        # Crea columna 'Oponente' para identificar al rival distinto a 'Cienciano' entre Equipo Local y Equipo Visitante
        df_disparos['Oponente'] = df_disparos.apply(
            lambda row: row['Equipo Visitante'] if row['Equipo Local'] == 'Cienciano' else row['Equipo Local'],
            axis=1
        )
        
        # Guardar en un nuevo archivo Excel si se desea
        df_disparos.to_excel('Todos_Disparos_Gaspar_Gentile.xlsx', index=False)
        print("\nDatos guardados en 'Todos_Disparos_Gaspar_Gentile.xlsx'")
    else:
        print("No se encontraron archivos con datos de Shotmap.")