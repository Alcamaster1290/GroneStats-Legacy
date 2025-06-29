import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import VerticalPitch
from LanusStats import SofaScore
from matplotlib.colors import LinearSegmentedColormap
import math

# Configuración inicial
st.set_page_config(layout="wide")
st.title("Zonas de Influencia - Gaspar Gentile (Peru Liga 1)")

# Inicialización
sofa = SofaScore()
player_id = 895364
temporadas = ["2025", "2024", "2023", "2022"]

# Colormaps
liga1_cmap = LinearSegmentedColormap.from_list("Liga1", ["#e09aa3", "#e42d44"])
kde_base_cmap = LinearSegmentedColormap.from_list("Base", ["#ffffcc", "#fcfc00"])

# Acumulador para todas las temporadas válidas
all_seasons_df = pd.DataFrame()
temporadas_validas = []  # para contar solo las temporadas con datos

# Cargar datos y filtrar temporadas con datos
data_por_temporada = {}
for season in temporadas:
    try:
        heatmap_df = sofa.get_player_season_heatmap("Peru Liga 1", season, player_id)
        if not heatmap_df.empty:
            data_por_temporada[season] = heatmap_df
            all_seasons_df = pd.concat([all_seasons_df, heatmap_df], ignore_index=True)
            temporadas_validas.append(season)
        else:
            st.warning(f"{season}: No se encontraron datos")
    except Exception as e:
        st.error(f"Error en {season}: {e}")

# Verifica si hay temporadas válidas
if temporadas_validas:
    num_temp = len(temporadas_validas)
    cols = 2
    rows = math.ceil(num_temp / cols)
    fig, axs = plt.subplots(rows, cols, figsize=(8 * cols, 4 * rows))
    axs = axs.flatten()
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    fig.suptitle("Zonas por temporada - Gaspar Gentile", fontsize=18)

    for i, season in enumerate(temporadas_validas):
        df = data_por_temporada[season]
        ax = axs[i]
        pitch.draw(ax=ax)

        pitch.kdeplot(
            x=df['x'],
            y=df['y'],
            ax=ax,
            cmap=kde_base_cmap,
            fill=True,
            levels=30,
            alpha=0.2,
            zorder=1
        )

        pitch.hexbin(
            x=df['x'],
            y=df['y'],
            ax=ax,
            gridsize=30,
            cmap=liga1_cmap,
            edgecolors='white',
            linewidths=0.5,
            zorder=2
        )

        ax.set_title(f"{season} - {len(df)} acciones", fontsize=14)
        st.success(f"{season}: {len(df)} puntos registrados")

    # Ocultar subplots vacíos si hay más ejes que temporadas
    for j in range(len(temporadas_validas), len(axs)):
        fig.delaxes(axs[j])

    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("No hay temporadas con datos para mostrar los gráficos individuales.")

# Gráfico combinado
st.subheader("Acumulado: 2022 - 2025")
fig_total, ax_total = plt.subplots(figsize=(10, 7))
pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
pitch.draw(ax=ax_total)

if not all_seasons_df.empty:
    pitch.kdeplot(
        x=all_seasons_df['x'],
        y=all_seasons_df['y'],
        ax=ax_total,
        cmap=kde_base_cmap,
        fill=True,
        levels=30,
        alpha=0.5,
        zorder=1
    )

    pitch.hexbin(
        x=all_seasons_df['x'],
        y=all_seasons_df['y'],
        ax=ax_total,
        gridsize=30,
        cmap=liga1_cmap,
        edgecolors='white',
        linewidths=0.5,
        alpha=0.6,
        zorder=2
    )

    st.success(f"Total acumulado: {len(all_seasons_df)} acciones")
    st.pyplot(fig_total)
else:
    st.warning("No se pudo generar el gráfico acumulado.")
