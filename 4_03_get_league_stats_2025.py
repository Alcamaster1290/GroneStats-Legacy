import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from adjustText import adjust_text  
import matplotlib.patheffects as PathEffects

# Parámetro modificable para filtrar jugadores con menos de cierto número de minutos
nro_jornadas_jugadas = 2
min_minutes_played = int(90 * nro_jornadas_jugadas / 2) 

input_dir = "Sofascore_2025/Liga 1 2025"
player_stats_list = []

for file in os.listdir(input_dir):
    if file.endswith(".xlsx"):  
        file_path = os.path.join(input_dir, file)
        try:
            df = pd.read_excel(file_path, sheet_name="Player Stats")
            df["source_file"] = file  
            df_filtered = df[["id", "shortName", "minutesPlayed", "position", "goalAssist", 
                              "accuratePass", "keyPass", "accurateCross", "accurateLongBalls", "teamName"]].copy()
            player_stats_list.append(df_filtered)
        except Exception as e:
            print(f"Error leyendo {file}: {e}")

if player_stats_list:
    aggregated_player_stats = pd.concat(player_stats_list, ignore_index=True).fillna(0)
    aggregated_player_stats = aggregated_player_stats.groupby(["id", "shortName", "position", "teamName"], as_index=False).sum()
else:
    print("No se encontraron archivos Excel con la hoja 'Player Stats'.")
    exit()

# Filtrar mediocampistas y jugadores con al menos el número mínimo de minutos jugados
time_filtered_players = aggregated_player_stats[aggregated_player_stats["minutesPlayed"] >= min_minutes_played]
midfielders = time_filtered_players[time_filtered_players["position"] == "M"].copy()

# Normalizar por 90 minutos
metrics = ["keyPass", "accuratePass", "accurateLongBalls", "accurateCross"]
for metric in metrics:
    midfielders[f"{metric}_per90"] = (midfielders[metric] / midfielders["minutesPlayed"]) * 90

metric_labels = ["Pases de Gol", "Pases Precisos", "Balones Largos Precisos", "Centros Precisos"]

sns.set(style="dark", rc={"axes.facecolor": "#121212", "figure.facecolor": "#121212"})
fig, axes = plt.subplots(len(metrics), 1, figsize=(8, 10))

for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
    per90_metric = f"{metric}_per90"
    
    sns.stripplot(
        x=midfielders[per90_metric], 
        y=[label] * len(midfielders),  
        ax=axes[i],
        jitter=True,  
        color="red",
        alpha=0.7,  
        size=6  
    )

    mean_value = midfielders[per90_metric].mean()
    axes[i].axvline(mean_value, color="yellow", linestyle="dashed", linewidth=2, label="Promedio")

    text_annotations = []
    top_players = midfielders.nlargest(5, per90_metric)
    directions = [-2, 3] * (len(top_players) // 2 + 1)

    for idx, (player_idx, row_data) in enumerate(top_players.iterrows()):
        x_value = row_data[per90_metric]
        y_value = label
        y_text = 0.85 + (idx * 0.5)
        shift = directions[idx] * 0.05

        annotation = axes[i].annotate(
            row_data["shortName"], 
            xy=(x_value, y_value), 
            xytext=(x_value, y_text + shift), 
            textcoords="data",
            color="white",
            fontsize=8,
            ha="left",
            va="top",
            bbox=dict(facecolor='black', alpha=0.4, edgecolor='none', boxstyle='round,pad=0.2'),
            arrowprops=dict(arrowstyle="->", color="grey", lw=1.5, alpha=0.3)
        )
        text_annotations.append(annotation)

    adjust_text(text_annotations, ax=axes[i], only_move={"points": "y", "texts": "y"}, force_points=0.3, force_text=1.0)
    axes[i].set_title(label, fontsize=15, color="white", loc="left")
    axes[i].set_ylabel("")
    axes[i].set_yticks([])
    axes[i].set_xlabel("")
    axes[i].spines["top"].set_visible(False)
    axes[i].spines["right"].set_visible(False)
    axes[i].spines["left"].set_visible(False)
    axes[i].set_xlim(left=0, right=midfielders[per90_metric].max() + 1)
    axes[i].tick_params(axis='x', colors='white')

plt.suptitle("TOP 5 MEDIOCAMPISTAS | Estadísticas por 90 minutos | LIGA 1 PERÚ", fontsize=20, color="white")
plt.legend(loc="upper right", fontsize=15, frameon=False, labelcolor="yellow")
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)

left_text = fig.text(0.01, 0.02, "Realizado por: GroneStats", ha="left", va="bottom", color="yellow", fontsize=16)
right_text = fig.text(0.99, 0.02, "Proveedor de datos: Sofascore", ha="right", va="bottom", color="yellow", fontsize=16)
center_text = fig.text(0.5, 0.02, "Hecho en Python", ha="center", va="bottom", color="yellow", fontsize=10)

for t in [left_text, right_text, center_text]:
    t.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='black')])

plt.show()