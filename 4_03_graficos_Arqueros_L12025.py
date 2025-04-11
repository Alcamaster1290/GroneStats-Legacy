import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import io

def load_player_stats(input_dir):
    player_stats_list = []
    columns = ["id", "shortName", "minutesPlayed", "position", "goodHighClaim",
               "saves", "punches", "accuratePass", "totalLongBalls", "savedShotsFromInsideTheBox", "teamName"]
    
    for file in os.listdir(input_dir):
        if file.endswith(".xlsx"):  
            file_path = os.path.join(input_dir, file)
            try:
                df = pd.read_excel(file_path, sheet_name="Player Stats")
                df["source_file"] = file  

                # Intentar seleccionar columnas disponibles
                selected_columns = [col for col in columns if col in df.columns]
                df_filtered = df[selected_columns].copy()

                # Renombrar equipo
                if "teamName" in df_filtered.columns:
                    df_filtered.rename(columns={"teamName": "Equipo"}, inplace=True)
                    df_filtered["Equipo"].replace("Universidad Técnica de Cajamarca", "UTC", inplace=True)

                player_stats_list.append(df_filtered)
            except Exception as e:
                st.error(f"Error leyendo {file}: {e}")
    
    if player_stats_list:
        return pd.concat(player_stats_list, ignore_index=True).fillna(0)
    else:
        st.error("No se encontraron archivos Excel con la hoja 'Player Stats'.")
        st.stop()

@st.cache_data
def preprocess_data_gk(df, min_minutes_played):
    df = df.groupby(["id", "shortName", "position", "Equipo"], as_index=False).sum()
    df = df[df["minutesPlayed"] >= min_minutes_played]
    return df[df["position"] == "G"].copy()

@st.cache_data
def normalize_per_90(df, metrics):
    df = df.copy()
    for metric in metrics:
        try:
            df[f"{metric}_per90"] = (df[metric] / df["minutesPlayed"]) * 90
        except ZeroDivisionError:
            df[f"{metric}_per90"] = 0
    return df

def plot_metrics(df, metrics, metric_labels, min_minutes_played, per90=True):
    sns.set_theme(style="dark", rc={"axes.facecolor": "#121212", 
                                    "figure.facecolor": "#121212", 
                                    "axes.edgecolor": "none"})
    fig, axes = plt.subplots(len(metrics), 1, figsize=(20, 12))
    fig.patch.set_alpha(0)
    
    for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
        column = f"{metric}_per90" if per90 else metric
        if column not in df.columns:
            continue

        cmap = sns.color_palette("Blues_r", as_cmap=True)
        sns.swarmplot(
            x=df[column], 
            y=[label] * len(df),  
            ax=axes[i],
            hue=df[column],
            palette=cmap,
            hue_norm=(df[column].min(), df[column].max()),
            alpha=0.7,
            size=13,
            legend=None
        )
        
        mean_value = df[column].mean()
        axes[i].axvline(mean_value, color="yellow", linestyle="dashed", linewidth=2, label="Promedio")
        axes[i].text(mean_value, -0.4, f"{mean_value:.2f}", color="yellow", weight='bold',
                     fontsize=14, ha='center', va='bottom', transform=axes[i].get_xaxis_transform())
        axes[i].set_title(label, fontsize=14, color="white", loc="left", weight='bold')
        axes[i].set_ylabel("")
        axes[i].set_yticks([])
        axes[i].set_xlabel("")
        axes[i].set_xlim(left=0, right=df[column].max() + 1)
        axes[i].tick_params(axis='x', colors='white')
        axes[i].patch.set_alpha(0)

        # Agregar tabla con el top 5
        top5 = df.nlargest(5, column)[["shortName", "Equipo", column]]
        top5[column] = top5[column].round(2)  # Redondear a dos decimales
        table_data = top5.values.tolist()
        table = axes[i].table(
            cellText=table_data,
            colLabels=["Jugador", "Equipo", label[:25]],
            colColours=["#444444"] * 3,
            cellLoc='center',
            loc='right',
            bbox=[1.05, 0, 0.5, 1.4]
        )

        for key, cell in table.get_celld().items():
            cell.set_edgecolor("black")
            font_size = 15 if key[0] == 0 else 12
            cell.set_fontsize(font_size)
            if key[0] == 0:
                cell.set_text_props(weight='bold', color='yellow', fontsize=font_size)
            else:
                cell.set_text_props(weight='bold', color='black', fontsize=font_size)
    
    title_text = "por 90 minutos jugados" if per90 else "valores totales"
    plt.suptitle(
        f"TOP 5 ARQUEROS | Estadísticas {title_text} | LIGA 1 PERÚ\nJugadores con al menos {min_minutes_played} minutos jugados",
        fontsize=30, color="white", weight="bold", x=0.7
    )
    fig.subplots_adjust(hspace=0.8)
    return fig
st.set_page_config(
        layout='wide')
st.title("Análisis de Arqueros | Liga 1 Perú 2025")
input_dir = "Sofascore_2025/Liga 1 2025"

with st.form(key="filter_form"):
    num_semanas = 4
    max_minutes_played = 90 * num_semanas
    half_max_minutes_played = int(round(max_minutes_played / 2, 1))
    min_minutes_played = st.slider("Selecciona el mínimo de minutos jugados", 90, max_minutes_played, half_max_minutes_played, step=5)
    metric_choice = st.radio("Selecciona el tipo de métrica:", ["Totales", "Por 90 minutos"])
    submit_button = st.form_submit_button(label="Imprimir gráfico")

if submit_button:
    metrics = ["saves", "savedShotsFromInsideTheBox","goodHighClaim", "punches"]
    metric_labels = ["Atajadas", "Atajadas en área", "Salidas altas exitosas", "Despejes con puños"]
    
    df = load_player_stats(input_dir)
    goalkeepers = preprocess_data_gk(df, min_minutes_played)
    
    if metric_choice == "Por 90 minutos":
        goalkeepers = normalize_per_90(goalkeepers, metrics)
        fig = plot_metrics(goalkeepers, metrics, metric_labels, min_minutes_played, per90=True)
    else:
        fig = plot_metrics(goalkeepers, metrics, metric_labels, min_minutes_played, per90=False)
    
    st.pyplot(fig)
    
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    st.download_button(
        label="Descargar gráfico",
        data=buf,
        file_name="top5_arqueros_L1.png",
        mime="image/png"
    )

st.markdown(
    "<p style='font-size: 12px; text-align: center; color: gray;'>"
    "Sígueme en mis redes: <a href='https://lnk.bio/alvarocc' target='_blank' style='color: lightblue;'>lnk.bio/alvarocc</a>"
    "</p>",
    unsafe_allow_html=True
)
