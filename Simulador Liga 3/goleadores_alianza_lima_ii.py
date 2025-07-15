import streamlit as st
import pandas as pd
import plotly.express as px

# Datos partidos actualizados
df = pd.DataFrame({
    "Fecha": [f"J{i}" for i in range(1, 16)],
    "Rival": [
        "Juventud SD", "Dep. Municipal", "Universitario", "Pacífico FC",
        "CS Pariacoto", "Unión Huaral", "Estudiantil CNI", "Amazon Callao",
        "Sport Boys", "Juventud SD", "Dep. Municipal", "Universitario",
        "Pacífico FC", "Pariacoto", "Unión Huaral"
    ],
    "Goles_AF": [6, 0, 2, 2, 5, 3, 0, 2, 0, 1, 1, 1, 0, 4, 1],
    "Goles_RC": [0, 1, 1, 2, 1, 4, 0, 0, 4, 1, 1, 0, 2, 0, 0]
})

# Localía
df["Localía"] = ["Local", "Visita", "Visita", "Local", "Visita", "Local", "Visita",
                 "Local", "Visita", "Visita", "Local", "Local", "Visita", "Local", "Visita"]

# Resultado y puntos
df["Resultado"] = df.apply(lambda r: "Victoria" if r["Goles_AF"] > r["Goles_RC"] 
                                        else "Empate" if r["Goles_AF"] == r["Goles_RC"] 
                                        else "Derrota", axis=1)
df["Puntos"] = df["Resultado"].map({"Victoria":3, "Empate":1, "Derrota":0})

# Etiqueta combinada fecha + rival para eje X
df["Fecha_Rival"] = df["Fecha"] + " - " + df["Rival"]

# Puntos acumulados (global)
df["Puntos Acumulados"] = df["Puntos"].cumsum()

# Goleadores
goleadores = {
    "Jugador": ["Víctor Guzmán", "Said Peralta", "Mauricio Arrasco", "Brian Arias",
                "Angelo Gironda", "Edú Sánchez", "Jefferson Muñoz", "Jhosenffer Yllescas",
                "Jussepi García", "Braidy Paz", "Donato Reynaldo"],
    "Goles_Local": [6, 3, 2, 1, 2, 1, 1, 0, 0, 1, 1],
    "Goles_Visita": [3, 0, 1, 2, 0, 0, 0, 1, 1, 1, 0]
}
df_goleadores = pd.DataFrame(goleadores)
df_goleadores["Total"] = df_goleadores["Goles_Local"] + df_goleadores["Goles_Visita"]
df_goleadores = df_goleadores.sort_values(by="Total", ascending=False)

st.title("Análisis actualizado Alianza Lima II - Liga 3 y Copa Federación")

tab1, tab2 = st.tabs(["Resumen Localía", "Goleadores por Localía"])

with tab1:
    st.header("Rendimiento según Localía")
    resumen = df.groupby("Localía").agg(
        Partidos=("Fecha", "count"),
        Goles_Favor=("Goles_AF", "sum"),
        Goles_Contra=("Goles_RC", "sum"),
        Victorias=("Resultado", lambda x: (x=="Victoria").sum()),
        Empates=("Resultado", lambda x: (x=="Empate").sum()),
        Derrotas=("Resultado", lambda x: (x=="Derrota").sum()),
        Puntos=("Puntos", "sum")
    )
    resumen["Prom_Goles"] = (resumen["Goles_Favor"]/resumen["Partidos"]).round(2)
    resumen["Prom_Puntos"] = (resumen["Puntos"]/resumen["Partidos"]).round(2)
    st.dataframe(resumen)

    # Separar por localía y calcular acumulados
    df_local = df[df["Localía"] == "Local"].copy()
    df_local["Goles a Favor Acumulados"] = df_local["Goles_AF"].cumsum()
    df_local["Goles en Contra Acumulados"] = df_local["Goles_RC"].cumsum()

    df_visita = df[df["Localía"] == "Visita"].copy()
    df_visita["Goles a Favor Acumulados"] = df_visita["Goles_AF"].cumsum()
    df_visita["Goles en Contra Acumulados"] = df_visita["Goles_RC"].cumsum()

    # Gráfico para Local
    fig_local = px.line(title="Goles Acumulados a Favor y en Contra - Local")
    fig_local.add_scatter(x=df_local["Fecha_Rival"], y=df_local["Goles a Favor Acumulados"],
                          mode='lines+markers', name="Goles a Favor (Local)", line=dict(color='blue'))
    fig_local.add_scatter(x=df_local["Fecha_Rival"], y=df_local["Goles en Contra Acumulados"],
                          mode='lines+markers', name="Goles en Contra (Local)", line=dict(color='lightblue'))
    fig_local.update_layout(
        xaxis_title="Partido (Fecha - Rival)",
        yaxis_title="Goles Acumulados",
        legend_title="Tipo de Gol (Local)"
    )

    # Gráfico para Visita
    fig_visita = px.line(title="Goles Acumulados a Favor y en Contra - Visita")
    fig_visita.add_scatter(x=df_visita["Fecha_Rival"], y=df_visita["Goles a Favor Acumulados"],
                           mode='lines+markers', name="Goles a Favor (Visita)", line=dict(color='red'))
    fig_visita.add_scatter(x=df_visita["Fecha_Rival"], y=df_visita["Goles en Contra Acumulados"],
                           mode='lines+markers', name="Goles en Contra (Visita)", line=dict(color='pink'))
    fig_visita.update_layout(
        xaxis_title="Partido (Fecha - Rival)",
        yaxis_title="Goles Acumulados",
        legend_title="Tipo de Gol (Visita)"
    )

    st.plotly_chart(fig_local, use_container_width=True)
    st.plotly_chart(fig_visita, use_container_width=True)

with tab2:
    st.header("Máximos goleadores según localía")
    fig2 = px.bar(df_goleadores.melt(id_vars="Jugador", 
                                    value_vars=["Goles_Local", "Goles_Visita"]),
                 x="Jugador", y="value", color="variable", barmode="group",
                 labels={"value":"Goles", "variable":"Localía"},
                 title="Goles anotados en casa vs visita")
    fig2.update_traces(texttemplate='%{y}', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df_goleadores[["Jugador", "Goles_Local", "Goles_Visita", "Total"]])
