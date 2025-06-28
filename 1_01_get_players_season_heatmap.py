import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from mplsoccer import VerticalPitch
from LanusStats import SofaScore
from matplotlib.colors import LinearSegmentedColormap

# Configuración inicial de la app
st.set_page_config(layout="wide")
st.title("Heatmap por competencia - Gaspar Gentile (2025)")

# Inicialización
sofa = SofaScore()
player_id = 895364
season = "2025"
ligas = ["Copa Sudamericana", "Peru Liga 1"]

# Colormaps personalizados
sudamericana_cmap = LinearSegmentedColormap.from_list("Sudamericana", ["white", "blue"])
liga1_cmap = LinearSegmentedColormap.from_list("Liga1", ["white", "#e42d44"])
custom_cmaps = [sudamericana_cmap, liga1_cmap]

# Plot
fig, axs = plt.subplots(1, 2, figsize=(18, 8))
pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
fig.suptitle(f"Heatmap temporada {season} - Gaspar Gentile (ID: {player_id})", fontsize=18)

for idx, liga in enumerate(ligas):
    try:
        heatmap_df = sofa.get_player_season_heatmap(liga, season, player_id)

        if not heatmap_df.empty:
            ax = axs[idx]
            pitch.draw(ax=ax)
            pitch.kdeplot(
                x=heatmap_df['x'],
                y=heatmap_df['y'],
                ax=ax,
                cmap=custom_cmaps[idx],
                fill=True,
                thresh=0.05,
                alpha=0.6,
                levels=100
            )
            num_puntos = len(heatmap_df)
            ax.set_title(f"{liga} - {num_puntos} puntos", fontsize=14)
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
