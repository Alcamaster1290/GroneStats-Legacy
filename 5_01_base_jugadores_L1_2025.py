import os
import pandas as pd
import streamlit as st

st.set_page_config(layout='wide')
st.title("Carga de Datos | Liga 1 Perú 2025")

# DataFrame de partidos con IDs numéricos
data = [
    (13352931, "Alianza Lima vs Cusco FC", "Alianza Lima", "Cusco FC", 1),
    (13352939, "Sport Huancayo vs AAS", "Sport Huancayo", "AAS", 1),
    (13352933, "Melgar vs UTC", "Melgar", "UTC", 1),
    (13352937, "Grau vs Ayacucho", "Grau", "Ayacucho", 1),
    (13352938, "AUDH vs Cristal", "AUDH", "Cristal", 1),
    (13352936, "Sport Boys vs JPII", "Sport Boys", "JPII", 1),
    (13352932, "Comerciantes vs U", "Comerciantes", "U", 1),
    (13352934, "Cienciano vs ADT", "Cienciano", "ADT", 1),
    (13352935, "Chankas vs Garcilaso", "Chankas", "Garcilaso", 1),
    (13387751, "AAS vs Alianza Lima", "AAS", "Alianza Lima", 2),
    (13387758, "Cusco FC vs Melgar", "Cusco FC", "Melgar", 2),
    (13387752, "UTC vs Binacional", "UTC", "Binacional", 2),
    (13387755, "ADT vs Grau", "ADT", "Grau", 2),
    (13387756, "U vs Cienciano", "U", "Cienciano", 2),
    (13387757, "Cristal vs Sport Boys", "Cristal", "Sport Boys", 2),
    (13387753, "JPII vs Huancayo", "JPII", "Huancayo", 2),
    (13387754, "Garcilaso vs Comerciantes", "Garcilaso", "Comerciantes", 2),
    (13387759, "Ayacucho vs AUDH", "Ayacucho", "AUDH", 2),
    (13387774, "Alianza Lima vs JPII", "Alianza Lima", "JPII", 3),
    (13387770, "Sport Boys vs Ayacucho", "Sport Boys", "Ayacucho", 3),
    (13387767, "Cienciano vs Garcilaso", "Cienciano", "Garcilaso", 3),
    (13387766, "Sport Huancayo vs Cristal", "Sport Huancayo", "Cristal", 3),
    (13387772, "Binacional vs Cusco FC", "Binacional", "Cusco FC", 3),
    (13387773, "AUDH vs ADT", "AUDH", "ADT", 3),
    (13387769, "Melgar vs AAS", "Melgar", "AAS", 3),
    (13387771, "Comerciantes vs Chankas", "Comerciantes", "Chankas", 3),
    (13523624, "Ayacucho vs Sp. Huancayo", "Ayacucho", "Sport Huancayo", 4),
    (13523626, "Cristal vs Alianza Lima", "Cristal", "Alianza Lima", 4),
    (13523644, "AAS vs Binacional", "AAS", "Binacional", 4),
    (13523647, "Cusco FC vs UTC", "Cusco FC", "UTC", 4),
    (13523648, "Garcilaso vs Grau", "Garcilaso", "Grau", 4),
    (13523646, "ADT vs Sport Boys", "ADT", "Sport Boys", 4),
    (13523625, "U vs AUDH", "U", "AUDH", 4),
    (13565846, "AUDH vs Garcilaso", "AUDH", "Garcilaso", 5),
    (13565847, "Alianza Lima vs Ayacucho", "Alianza Lima", "Ayacucho", 5),
    (13565842, "UTC vs AAS", "UTC", "AAS", 5),
    (13565844, "Sport Huancayo vs ADT", "Sport Huancayo", "ADT", 5),
    (13565845, "Melgar vs Cristal", "Melgar", "Cristal", 5),
    (13565843, "Sport Boys vs U", "Sport Boys", "U", 5),
    (13565841, "Cienciano vs Comerciantes", "Cienciano", "Comerciantes", 5),
    (13565883, "Grau vs Los Chankas", "Grau", "Los Chankas", 5),
    (13565884, "Binacional vs JPII", "Binacional", "JPII", 5),
]

df_matches = pd.DataFrame(data, columns=["ID_Sofascore", "Nombre Partido", "home", "away", "# Jornada"])
df_matches["ID_Sofascore"] = pd.to_numeric(df_matches["ID_Sofascore"], errors='coerce')

# Función para cargar estadísticas de jugadores
def load_player_stats(input_dir):
    player_stats_list = []
    for file in os.listdir(input_dir):
        if file.endswith(".xlsx"):
            file_path = os.path.join(input_dir, file)
            try:
                df = pd.read_excel(file_path, sheet_name="Player Stats")
                # Extraer el match_id del nombre del archivo (se asume formato: 'Sofascore_{match_id}.xlsx')
                match_id_str = file.replace("Sofascore_", "").replace(".xlsx", "")
                df["ID_Sofascore"] = pd.to_numeric(match_id_str, errors='coerce')
                df["Archivo Origen"] = file
                
                # Diccionario de traducción de columnas
                column_translation = {
                    "id" : "ID_Player_Sofascore",
                    "shortName": "Nombre",
                    "minutesPlayed": "Minutos Jugados",
                    "position": "POS",
                    "goals": "Goles",
                    "goalAssist": "Asistencias",
                    "onTargetScoringAttempt": "Tiros Al Arco",
                    "shotOffTarget": "Tiros Fuera",
                    "blockedScoringAttempt": "Tiros Bloqueados",
                    "bigChanceCreated": "Grandes Ocasiones",
                    "keyPass": "Pases Clave",
                    "touches": "Toques",
                    "accuratePass": "Pases Precisos",
                    "accurateLongBalls": "Pases Largos Precisos",
                    "accurateCross": "Centros Precisos",
                    "interceptionWon": "Intercepciones",
                    "totalClearance": "Despejes",
                    "aerialWon": "Duelos Aéreos Ganados",
                    "duelWon": "Duelos Ganados",
                    "totalTackle": "Entradas Totales",
                    "wonContest": "Regates",
                    "saves": "Atajadas",
                    "savedShotsFromInsideTheBox": "Atajadas en el área",
                    "goodHighClaim": 'Reclamo Aereo',                    
                    "punches": "Salidas con puños",
                    "teamName": "Equipo"
                }
                
                # Verificar si las columnas existen, si no, asignar 0
                for col in ["goals", "goalAssist", "bigChanceCreated","goodHighClaim","punches","savedShotsFromInsideTheBox"]:
                    if col not in df.columns:
                        df[col] = 0
                        
                # Filtrar y traducir columnas (incluimos ID_Sofascore y Archivo Origen)
                df_filtered = df[list(column_translation.keys()) + ["ID_Sofascore", "Archivo Origen"]].copy()
                df_filtered.rename(columns=column_translation, inplace=True)
                
                player_stats_list.append(df_filtered)
            except Exception as e:
                st.error(f"Error leyendo {file}: {e}")
                
    if player_stats_list:
        df_stats = pd.concat(player_stats_list, ignore_index=True).fillna(0)
        # Agrupar por 'ID_Player_Sofascore', 'Nombre', 'POS' y 'Equipo'
        df_stats = df_stats.groupby(["ID_Player_Sofascore", "Nombre", "POS", "Equipo"], as_index=False).sum()
        df_stats["ID_Player_Sofascore"] = pd.to_numeric(df_stats["ID_Player_Sofascore"], errors='coerce')
        return df_stats
    else:
        st.error("No se encontraron archivos Excel con la hoja 'Player Stats'.")
        st.stop()

# Ruta de los archivos
input_dir = "Sofascore_2025/Liga 1 2025"

# Cargar estadísticas de jugadores
df_stats = load_player_stats(input_dir)

# Aseguramos que ambas columnas de ID_Sofascore sean numéricas
df_stats["ID_Sofascore"] = pd.to_numeric(df_stats["ID_Sofascore"], errors='coerce')
df_matches["ID_Sofascore"] = pd.to_numeric(df_matches["ID_Sofascore"], errors='coerce')

df_merged = df_stats.merge(df_matches, on="ID_Sofascore", how="left")

# === SELECTOR DE JORNADA ===
st.sidebar.subheader("Filtros")
jornada_options = sorted(df_matches["# Jornada"].unique().tolist())
jornada_options.insert(0, "Todos")
selected_jornada = st.sidebar.selectbox("Selecciona la jornada", jornada_options)

if selected_jornada == "Todos":
    # Agrupar para sumar estadísticas y contar partidos jugados
    df_filtered = df_stats.groupby(["ID_Player_Sofascore","Nombre", "POS", "Equipo"], as_index=True).agg({
        "Minutos Jugados": "sum",
        "Goles": "sum",
        "Asistencias": "sum",
        "Tiros Al Arco": "sum",
        "Tiros Fuera": "sum",
        "Tiros Bloqueados": "sum",
        "Grandes Ocasiones": "sum",
        "Pases Clave": "sum",
        "Toques": "sum",
        "Pases Precisos": "sum",
        "Pases Largos Precisos": "sum",
        "Centros Precisos": "sum",
        "Intercepciones": "sum",
        "Despejes": "sum",
        "Duelos Aéreos Ganados": "sum",
        "Duelos Ganados": "sum",
        "Entradas Totales": "sum",
        "Regates": "sum",
        "Atajadas": "sum",
        "Atajadas en el área": "sum",
        "Reclamo Aereo": "sum",
        "Salidas con puños": "sum",
    }).reset_index()


else:
    match_ids = df_matches[df_matches["# Jornada"] == selected_jornada]["ID_Sofascore"].tolist()
    df_filtered = df_stats[df_stats["ID_Sofascore"].isin(match_ids)]

# === SELECTOR DE POSICIÓN ===
pos_options = sorted(df_stats["POS"].unique())
selected_pos = st.sidebar.multiselect("Selecciona una posición", pos_options, default=pos_options)

if "POS" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["POS"].isin(selected_pos)]
else:
    st.error("La columna 'POS' no está presente en los datos cargados.")

# Mostrar los datos combinados filtrados
st.subheader(f"Datos Filtrados - Jornada {selected_jornada}")
st.dataframe(df_filtered)