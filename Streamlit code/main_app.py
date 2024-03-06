import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from mplsoccer.pitch import VerticalPitch

nombres_jornadas = {
        "J1": "Jornada 1 - Local vs Universidad Cesar Vallejo",
        "J2": "Jornada 2 - Visita vs Alianza Atlético de Sullana",
        "J3": "Jornada 3 - Local vs Universitario de Deportes",
        "J4": "Jornada 4 - Visita vs Unión Comercio",
        "J5": "Jornada 5 - Local vs Comerciantes Unidos",
        "J6": "Jornada 6 - Visita vs ADT",
}

@st.cache_data
def draw_player_heatmaps(jugador,df_posiciones_medias,heatmaps):
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    num_jornadas = len(heatmaps)
    cols = 2
    rows = -(-num_jornadas // cols)  # Redondeo hacia arriba
    fig, axs = plt.subplots(rows, cols, figsize=(10 * cols, 7 * rows))
    fig.subplots_adjust(hspace=0.5, wspace=0.5)
    axs = axs.flatten()
    plot_counter = 0
    for jornada, archivo_excel in heatmaps.items():
        with pd.ExcelFile(archivo_excel) as xls:
            if jugador in xls.sheet_names:
                df_heatmap = pd.read_excel(xls, sheet_name=jugador)
                if not df_heatmap.empty:
                    ax = axs[plot_counter]
                    pitch.draw(ax=ax)
                    ax.set_facecolor((0, 0, 1, 0.5))
                    pitch.kdeplot(df_heatmap['x'], df_heatmap['y'], ax=ax, levels=100, cmap='Blues',fill=True, shade_lowest=True, alpha=0.5)
                    fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador) & (df_posiciones_medias['Jornada'] == jornada)]
                    if not fila_jugador.empty:
                        pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
                        ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
                        ax.set_title(f"{jugador} - {nombres_jornadas[jornada]}", fontsize=14)
                    plot_counter += 1
                
    for j in range(plot_counter, rows * cols):
        axs[j].axis('off')
    plt.tight_layout()
    st.pyplot(fig)

@st.cache_data
def cargar_datos_jugadores():
    # Carga de datos de los jugadores y estadísticas de pases
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/XLSX finales/Resumen_AL_Jugadores.xlsx')
    return df

@st.cache_resource
# Función para cargar los DataFrames de posiciones medias y heatmaps para todas las jornadas
def cargar_datos_mapas():
    df_posiciones_medias_total = pd.DataFrame()
    heatmaps_total = {}
    for jornada, nombre_jornada in nombres_jornadas.items():
        try:
            df_temp = pd.read_csv(f'CSV obtenidos/{nombre_jornada}_posicion_jugadores.csv')
            df_temp['Jornada'] = jornada
            df_posiciones_medias_total = pd.concat([df_posiciones_medias_total, df_temp])
            heatmaps_total[jornada] = f'CSV obtenidos/{jornada}_heatmaps_jugadores.xlsx'
        except FileNotFoundError as e:
            st.error(f"No se encontró el archivo para {nombre_jornada}: {e}")
    return df_posiciones_medias_total.sort_values(by='jerseyNumber'), heatmaps_total

def configurar_pagina():
    st.set_page_config(
        page_title="Análisis de jugadores de Alianza Lima Temporada 2024",
        layout='wide',
        page_icon=r'Imagenes\AL.png')

@st.cache_data
def cargar_general():
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/ALIANZA LIMA 2024.xlsx')
    return df

def main():
    configurar_pagina()
    
    df = cargar_datos_jugadores()
    df_maestro = cargar_general()  # Carga el DataFrame maestro con los detalles de los jugadores
    st.title('Alianza Lima Temporada 2024')
    # Carga de datos de posiciones medias y heatmaps
    df_posiciones_medias, heatmaps = cargar_datos_mapas()
    
    pantalla_heatmaps, pantalla_botones, pantalla_jugador = st.columns([4, 2, 3])
    
    with pantalla_botones:
        # Botón de Selección de Jugador
        jugador_selector = st.selectbox('Selecciona un jugador:', sorted(df['Jugador'].unique()), key='jugador_selector')
        # Encuentra los detalles del jugador en el DataFrame maestro
        detalles_jugador = df_maestro[df_maestro['Jugador'] == jugador_selector].iloc[0]

    with pantalla_heatmaps:
        st.header('Mapas de calor (mayor tonalidad de azul mayor presencia en zona de juego)')
        # Genera los mapas de calor
        if st.button('Generar mapas de calor'):
            with pantalla_heatmaps:
                draw_player_heatmaps(jugador_selector, df_posiciones_medias, heatmaps)

    with pantalla_jugador:
        st.subheader('Detalles del Jugador', anchor=None)
        st.markdown(f"<span style='color: black;'>Posición: {detalles_jugador['Posición']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: blue;'>Dorsal: {detalles_jugador['Dorsal']}</span>", unsafe_allow_html=True)
        # Crea tres columnas dentro de pantalla_jugador para centrar los datos
        col1, col2, col3 = st.columns([1, 3, 1])
    
        with col1:  # Mostrar Tarjetas Rojas y Amarillas
            st.metric(label="T. Rojas", value=detalles_jugador['Rojas'])
            st.metric(label="T. Amarillas", value=detalles_jugador['Amarillas'])
    
        with col2:  # Mostrar Goles, Asistencias y Minutos Jugados
            st.metric(label="Goles", value=detalles_jugador['Goles'])
            st.metric(label="Asistencias", value=detalles_jugador['Asistencias'])
            st.metric(label="Minutos Jugados", value=f"{detalles_jugador['Minutos']} mins")
        
if __name__ == "__main__":
    main()
