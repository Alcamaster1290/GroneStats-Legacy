import streamlit as st
import pandas as pd
from LanusStats import SofaScore

st.title("Estadísticas de Liga 1 Perú 2025")

# Intentar obtener datos desde SofaScore
try:
    sofascore = SofaScore()
    df_liga1_2025 = sofascore.scrape_league_stats(
        league="Peru Liga 1",
        season="2025",
        accumulation="total",
        selected_positions=['Goalkeepers', 'Defenders', 'Midfielders', 'Forwards']
    )
    
    st.success("Datos de SofaScore obtenidos correctamente.")
    st.write("### Vista previa de los datos")
    st.dataframe(df_liga1_2025)

    st.write("### Columnas disponibles:")
    st.write(df_liga1_2025.columns.tolist())

    # Verificar que la columna 'player' exista antes de usarla
    if 'player' in df_liga1_2025.columns:
        jugadores_liga1 = df_liga1_2025['player'].unique().tolist()
        st.write("### Jugadores de Liga 1 2025:")
        st.write(jugadores_liga1)
    else:
        st.warning("La columna 'player' no existe en el DataFrame.")
except Exception as e:
    st.error(f"Error al obtener datos de SofaScore: {e}")
    df_liga1_2025 = pd.DataFrame()  # Creamos un DataFrame vacío para evitar errores después

# Intentar leer el archivo Excel
try:
    path_excel = r"BD Jugadores 2025.xlsx"
    df_jugadores = pd.read_excel(path_excel, sheet_name="Jugadores")
    st.success("Archivo Excel leído correctamente.")
    st.write("### Datos de jugadores:")
    st.dataframe(df_jugadores)

    if 'Nombre_Completo' in df_jugadores.columns:
        jugadores_excel = df_jugadores['Nombre_Completo'].unique().tolist()
        st.write("### Jugadores del archivo Excel:")
        st.write(jugadores_excel)

except Exception as e:
    st.error(f"No se pudo leer el archivo Excel: {e}")

# Intentar mezclar los dataframes de df_jugadores y df_liga1_2025 por columna 'Nombre_Completo' y 'player' 
try:
    if not df_jugadores.empty and not df_liga1_2025.empty:
        df_combinado = pd.merge(df_jugadores, df_liga1_2025, left_on='Nombre_Completo', right_on='player', how='outer')
        st.success("DataFrames combinados correctamente.")
        st.write("### DataFrame combinado:")
        st.dataframe(df_combinado)
    else:
        st.warning("Uno o ambos DataFrames están vacíos, no se puede combinar.")
except Exception as e:
    st.error(f"Error al combinar los DataFrames: {e}")
    df_combinado = pd.DataFrame()  