import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import VerticalPitch
from LanusStats import SofaScore
from matplotlib.colors import LinearSegmentedColormap

# Configuración inicial
st.set_page_config(layout="wide")
st.title("Hexbin + KDE por competencia - Gaspar Gentile (2025)")

# Inicialización
sofa = SofaScore()
player_id = 895364
season = "2025"
ligas = ["Copa Sudamericana", "Peru Liga 1"]

# Colormaps personalizados HEXBIN
sudamericana_cmap = LinearSegmentedColormap.from_list("Sudamericana", ["#b3a8f3", "#0404FF"])
liga1_cmap = LinearSegmentedColormap.from_list("Liga1", ["#db6b7a", "#f11432"])
custom_cmaps = [sudamericana_cmap, liga1_cmap]

# Colormaps personalizados KDE (más suaves pero acordes)
sudamericana_kde = LinearSegmentedColormap.from_list("Sud_kde", ["#e8ecff", "#020234"])  # azul claro
liga1_kde = LinearSegmentedColormap.from_list("Liga1_kde", ["#ffe3e6", "#de001e"])       # rojo claro
custom_kdes = [sudamericana_kde, liga1_kde]

# Crear el gráfico
fig, axs = plt.subplots(1, 2, figsize=(18, 8))
pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
fig.suptitle(f"Zona de influencia Gaspar Gentile - Temporada {season}", fontsize=18)

for idx, liga in enumerate(ligas):
    try:
        heatmap_df = sofa.get_player_season_heatmap(liga, season, player_id)

        if not heatmap_df.empty:
            ax = axs[idx]
            pitch.draw(ax=ax)

            # KDE como fondo, tono suave del color principal
            pitch.kdeplot(
                x=heatmap_df['x'],
                y=heatmap_df['y'],
                ax=ax,
                cmap=custom_kdes[idx],   # cmap específico por competencia
                fill=True,
                levels=30,
                alpha=0.25,
                zorder=1
            )

            # HEXBIN encima del kdeplot
            pitch.hexbin(
                x=heatmap_df['x'],
                y=heatmap_df['y'],
                ax=ax,
                gridsize=30,
                cmap=custom_cmaps[idx],
                edgecolors='white',
                linewidths=0.5,
                zorder=2
            )

            num_puntos = len(heatmap_df)
            ax.set_title(f"{liga} - {num_puntos} acciones", fontsize=14)
            st.success(f"{liga}: {num_puntos} puntos registrados")
        else:
            axs[idx].set_title(f"{liga} - Sin datos", fontsize=14)
            axs[idx].axis('off')
            st.warning(f"{liga}: No se encontraron datos")

    except Exception as e:
        axs[idx].set_title(f"{liga} - ERROR", fontsize=14)
        axs[idx].axis('off')
        st.error(f"Error con {liga}: {e}")

plt.tight_layout()
st.pyplot(fig)
