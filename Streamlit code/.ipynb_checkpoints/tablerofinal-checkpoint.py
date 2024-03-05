import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer.pitch import VerticalPitch
import streamlit as st
import numpy as np

# Carga de datos de los jugadores y estadísticas de pases
df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/XLSX finales/Resumen_AL_Jugadores.xlsx')
nombres_jornadas = {
        "J1": "Jornada 1 - Local vs Universidad Cesar Vallejo",
        "J2": "Jornada 2 - Visita vs Alianza Atlético de Sullana",
        "J3": "Jornada 3 - Local vs Universitario de Deportes",
        "J4": "Jornada 4 - Visita vs Unión Comercio",
        "J5": "Jornada 5 - Local vs Comerciantes Unidos",
    }
# Función para cargar los DataFrames de posiciones medias y heatmaps para todas las jornadas
def cargar_datos():
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

# Preparar el pitch para los heatmaps
pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')

# Seleccionar jugador con Streamlit
jugador_selector = st.selectbox('Jugador:', sorted(df['Nombre'].unique()))

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

def agregar_graficos_lineas(df, jugador_seleccionado):
    # Filtro de datos para el jugador seleccionado
    df_jugador = df[df['Nombre'] == jugador_seleccionado].copy()

    # Mapeo de nombres de jornadas a etiquetas cortas
    df_jugador['Jornada'] = df_jugador['Jornada'].map({
        'Jornada 1 - Local vs Universidad Cesar Vallejo': 'J1',
        'Jornada 2 - Visita vs Alianza Atlético de Sullana': 'J2',
        'Jornada 3 - Local vs Universitario de Deportes': 'J3',
        'Jornada 4 - Visita vs Unión Comercio': 'J4',
        'Jornada 5 - Local vs Comerciantes Unidos': 'J5'
    })

    # Estadísticas a graficar
    estadisticas = [
        'Duelos Aereos Perdidos', 'Duelos Aereos Ganados', 
        'Duelos Perdidos', 'Duelos Ganados', 
        'Despejes Totales', 'Intercepciones Ganadas', 
        'Entradas Totales', 'Bloqueos de Jugadores de Campo'
    ]
    
    fig, axs = plt.subplots(len(estadisticas), 1, figsize=(10, 5 * len(estadisticas)))
    fig.subplots_adjust(hspace=0.4)

    for i, estadistica in enumerate(estadisticas):
        axs[i].plot(df_jugador['Jornada'], df_jugador[estadistica], marker='o', linestyle='-', label=estadistica)
        axs[i].set_title(f'{estadistica} por jornada para {jugador_seleccionado}')
        axs[i].set_xlabel('Jornada')
        axs[i].set_ylabel(estadistica)
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

    promedio_pases_acertados = df['Pases Acertados'].mean()
    promedio_balones_largos_acertados = df['Balones Largos Acertados'].mean()
    promedio_centros_acertados = df['Centros Acertados'].mean()
    color_fondo = 'black'
    color_linea_promedio = 'white'
    # Definir el ancho de las barras
    bar_width = 0.3  # Añade esta línea para definir el ancho de las barras

    estadisticas_y_promedios = [
        ('Pases Acertados', promedio_pases_acertados, 'Total de Pases'),
        ('Balones Largos Acertados', promedio_balones_largos_acertados, 'Total de Balones Largos'),
        ('Centros Acertados', promedio_centros_acertados, 'Total de Centros')
    ]

    # Creación de gráficos
    fig, axs = plt.subplots(3, 1, figsize=(10, 18), facecolor=color_fondo)
    for i, (estadistica, promedio, total_estadistica) in enumerate(estadisticas_y_promedios):
        ax = axs[i]
        r1 = np.arange(len(df_jugador['Jornada']))
        r2 = [x + bar_width for x in r1]

        ax.bar(r1, df_jugador[estadistica], color='lightblue', width=bar_width, edgecolor='steelblue', label=estadistica)
        ax.bar(r2, df_jugador[total_estadistica], color='navy', width=bar_width, edgecolor='lightblue', label=total_estadistica)
        # Para dibujar la línea de promedio correctamente
        ax.axhline(y=promedio, color=color_linea_promedio, linestyle='--', label=f'Promedio del equipo: {promedio:.2f}')

        ax.set_facecolor(color_fondo)
        ax.set_title(f'{estadistica} por Jornada para {jugador_seleccionado}')
        ax.set_xlabel('Jornada')
        ax.set_xticks([r + bar_width / 2 for r in range(len(r1))])
        ax.set_xticklabels(df_jugador['Jornada'])
        ax.set_ylabel(estadistica)
        ax.tick_params(colors='white')
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.legend(facecolor=color_fondo, edgecolor=color_fondo)
        for text in ax.legend().get_texts():
            text.set_color('black')

    plt.tight_layout()
    st.pyplot(fig)

# Carga de datos de posiciones medias y heatmaps (ajusta las rutas de los archivos según corresponda)
df_posiciones_medias, heatmaps = cargar_datos()

# Llamadas a las funciones basadas en la selección del jugador
draw_player_heatmaps(jugador_selector)
generar_informe(jugador_selector)
agregar_graficos_lineas(df, jugador_selector)