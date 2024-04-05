import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer.pitch import VerticalPitch
import streamlit as st

# Preparar el pitch
pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
# Diccionario con los nombres de las jornadas
nombres_jornadas = {
    "J1": "Jornada 1 - Local vs Universidad Cesar Vallejo",
    "J2": "Jornada 2 - Visita vs Alianza Atlético de Sullana",
    "J3": "Jornada 3 - Local vs Universitario de Deportes",
    "J4": "Jornada 4 - Visita vs Unión Comercio",
    "J5": "Jornada 5 - Local vs Comerciantes Unidos",
    "J6": "Jornada 6 - Visita vs ADT",
    #"J7": "Jornada 7 - Local vs Sporting Cristal",
    #"J8": "Jornada 8 - Visita vs Cienciano",
}

# Función para cargar los DataFrames de posiciones medias y heatmaps para todas las jornadas
def cargar_datos():
    df_posiciones_medias_total = pd.DataFrame()
    heatmaps_total = {}
    for jornada, nombre_jornada in nombres_jornadas.items():
        try:
            # Cargar el DataFrame de posiciones medias y agregar una columna 'Jornada'
            df_temp = pd.read_csv(f'CSV obtenidos\\{jornada}_pos_jugadores.csv')
            df_temp['Jornada'] = jornada  # Añadir columna 'Jornada' con el identificador de la jornada
            df_posiciones_medias_total = pd.concat([df_posiciones_medias_total, df_temp])
            heatmaps_total[jornada] = f'CSV obtenidos\\{jornada}_heatmaps_jugadores.xlsx'
        except FileNotFoundError as e:
            st.error(f"No se encontró el archivo para {nombre_jornada}: {e}")
    return df_posiciones_medias_total, heatmaps_total

df_posiciones_medias, heatmaps = cargar_datos()
df_posiciones_medias = df_posiciones_medias.sort_values(by='jerseyNumber')
# Streamlit widget para seleccionar el jugador
jugador_selector = st.selectbox('Jugador:', df_posiciones_medias['name'].unique())

def draw_heatmap_promedio(jugador):
    # Calculate the mean position of the player
    mean_x = df_posiciones_medias[df_posiciones_medias['name'] == jugador]['averageX'].mean()
    mean_y = df_posiciones_medias[df_posiciones_medias['name'] == jugador]['averageY'].mean()

    # Draw the heatmap with the mean position
    pitch.draw(ax=ax)
    for jornada, archivo_excel in heatmaps.items():
        with pd.ExcelFile(archivo_excel) as xls:
            if jugador in xls.sheet_names:
            # Load the data from the sheet into a DataFrame
                df_heatmap = pd.read_excel(xls, sheet_name=jugador)
            # Check if the DataFrame is not empty
                if not df_heatmap.empty:
                    # Draw a KDE plot on the pitch using the player's positions
                    pitch.kdeplot(df_heatmap['x'], df_heatmap['y'], ax=ax, levels=100, cmap='Blues', fill=True, shade_lowest=True, alpha=0.5)
                    # Plot the mean position of the player
                    pitch.scatter(mean_x, mean_y, ax=ax, s=200, color='red', edgecolors='black', linewidth=2.5, zorder=1)
                    # Label the mean position with the text 'Mean'
                    ax.text(mean_y, mean_x, 'Mean', color='white', ha='center', va='center', fontsize=12, zorder=2)

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

# Llamar a la función para dibujar los heatmaps con el jugador seleccionado
draw_player_heatmaps(jugador_selector)
