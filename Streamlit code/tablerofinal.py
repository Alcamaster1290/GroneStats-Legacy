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

def agregar_graficos_lineas(df, jugador_seleccionado):
    df_jugador = df[df['Nombre'] == jugador_seleccionado].copy()

    df_jugador['Jornada'] = df_jugador['Jornada'].map({
        'Jornada 1 - Local vs Universidad Cesar Vallejo': 'J1',
        'Jornada 2 - Visita vs Alianza Atlético de Sullana': 'J2',
        'Jornada 3 - Local vs Universitario de Deportes': 'J3',
        'Jornada 4 - Visita vs Unión Comercio': 'J4',
        'Jornada 5 - Local vs Comerciantes Unidos': 'J5'
    })

    # Grupos de estadísticas para graficar
    estadisticas_grupos = [
        {'Duelos Aereos Perdidos', 'Duelos Aereos Ganados'},
        {'Duelos Perdidos', 'Duelos Ganados', 'Entradas Totales'},
        {'Intercepciones Ganadas', 'Despejes Totales', 'Bloqueos de Jugadores de Campo'}
    ]
    
    fig, axs = plt.subplots(len(estadisticas_grupos), 1, figsize=(10, 6 * len(estadisticas_grupos)))
    if len(estadisticas_grupos) > 1:
        axs = axs.flatten()
    
    for i, grupo_estadisticas in enumerate(estadisticas_grupos):
        for estadistica in grupo_estadisticas:
            axs[i].plot(df_jugador['Jornada'], df_jugador[estadistica], marker='o', linestyle='-', label=estadistica)
        axs[i].set_title(f'Estadísticas por jornada para {jugador_seleccionado}')
        axs[i].set_xlabel('Jornada')
        axs[i].set_ylabel('Valor')
        axs[i].legend()
        axs[i].grid(True)

    plt.tight_layout()
    st.pyplot(fig)

def generar_informe(jugador_seleccionado):

    df_jugador = df[df['Nombre'] == jugador_seleccionado].copy()

    # Asegurar que los nombres de las jornadas coincidan con los esperados
    df_jugador['Jornada'] = df_jugador['Jornada'].map({
        'Jornada 1 - Local vs Universidad Cesar Vallejo': 'J1',
        'Jornada 2 - Visita vs Alianza Atlético de Sullana': 'J2',
        'Jornada 3 - Local vs Universitario de Deportes': 'J3',
        'Jornada 4 - Visita vs Unión Comercio': 'J4',
        'Jornada 5 - Local vs Comerciantes Unidos': 'J5'
    })

    # Calcula promedios
    promedios = {
        'Pases Acertados': df['Pases Acertados'].mean(),
        'Balones Largos Acertados': df['Balones Largos Acertados'].mean(),
        'Centros Acertados': df['Centros Acertados'].mean()
    }

    fig = go.Figure()

    # Definir el ancho de las barras
    bar_width = 0.3

    for i, (estadistica, promedio, total_estadistica) in enumerate([
        ('Pases Acertados', promedios['Pases Acertados'], 'Total de Pases'),
        ('Balones Largos Acertados', promedios['Balones Largos Acertados'], 'Total de Balones Largos'),
        ('Centros Acertados', promedios['Centros Acertados'], 'Total de Centros')
    ]):
        # Agregar las barras para cada estadística
        fig.add_trace(go.Bar(x=df_jugador['Jornada'], y=df_jugador[estadistica], name=estadistica,
                             offsetgroup=i, marker_color='lightblue'))
        fig.add_trace(go.Bar(x=df_jugador['Jornada'], y=df_jugador[total_estadistica], name=total_estadistica,
                             offsetgroup=i, base=bar_width, marker_color='navy'))

        # Agregar línea de promedio
        fig.add_shape(type="line", x0=0, y0=promedio, x1=1, y1=promedio, line=dict(color="white", dash="dash"),
                      xref="paper", yref="y")

    # Actualizar layout
    fig.update_layout(title_text=f'Estadísticas por Jornada para {jugador_seleccionado}',
                      barmode='group',
                      plot_bgcolor='black',
                      paper_bgcolor='black',
                      font_color='white',
                      legend=dict(bgcolor='black', font_color='white'))
    
    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def draw_player_heatmaps(jugador):
    num_jornadas = len(heatmaps)
    cols = 2
    rows = -(-num_jornadas // cols)  # Redondeo hacia arriba
    fig, axs = plt.subplots(rows, cols, figsize=(10 * cols, 7 * rows))
    fig.subplots_adjust(hspace=0.5, wspace=0.2)
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

# Empieza el codeo de la app

st.title('Analisis de jugadores de Alianza Lima Temporada 2024')

# Preparar el pitch para los heatmaps
pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')

df = cargar_datos_jugadores()

# Boton de Seleccion de Jugador
jugador_selector = st.selectbox('Selecciona un jugador:', sorted(df['Jugador'].unique()))

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

# Carga de datos de posiciones medias y heatmaps (ajusta las rutas de los archivos según corresponda)
df_posiciones_medias, heatmaps = cargar_datos_mapas()

# Botón para generar informe
if st.button('Generar mapas de calor'):
    draw_player_heatmaps(jugador_selector)