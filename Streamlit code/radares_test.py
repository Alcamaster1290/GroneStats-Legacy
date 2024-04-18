import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from soccerplots.radar_chart import Radar

nombres_jornadas = {
    "J1": "Apertura - J1 - Local vs Universidad Cesar Vallejo",
    "J2": "Apertura - J2 - Visita vs Alianza Atlético de Sullana",
    "J3": "Apertura - J3 - Local vs Universitario de Deportes",
    "J4": "Apertura - J4 - Visita vs Unión Comercio",
    "J5": "Apertura - J5 - Local vs Comerciantes Unidos",
    "J6": "Apertura - J6 - Visita vs ADT",
    "J7": "Apertura - J7 - Local vs Sporting Cristal",
    "J8": "Apertura - J8 - Visita vs Cienciano",
    "J9": "Apertura - J9 - Local vs Los Chankas",
    #"J10": "Apertura - J10 - Visita vs Carlos Manucci",
    "C1": "Copa Libertadores - J1 - Local vs Fluminense", 
    #"C2": "Copa Libertadores - J2 - Visita vs Cerro Porteño"
}

# INITIAL CONFIG AND LOAD 
def configurar_pagina():
    st.set_page_config(
        page_title="Test GroneStats",
        layout='wide',
        page_icon=r'Imagenes\AL.png',
        initial_sidebar_state="expanded")

def cargar_general():
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/ALIANZA LIMA 2024.xlsx')
    return df

def cargar_datos_jugadores():
    # Carga de datos de los jugadores y estadísticas de pases
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/Archivos para el tablero final/Resumen_AL_Jugadores.xlsx')
    return df

def radar_chart(data, selected_metrics):

    player_data = data
    ranges = []
    values = []
    for metric in selected_metrics:
        metric_data = player_data[metric]
        min_val = metric_data.min()
        max_val = metric_data.max()

        # Calcular el rango como el valor mínimo/máximo de la métrica menos/más el 10%
        ranges.append((min_val * 0.9, max_val * 1.1))
        # Agregar el valor de la métrica para el jugador a los valores
        values.append(metric_data)

    title = dict(
        title_name= "Radar de acciones",
        title_color = 'blue',
        title_fontsize = 18,
    )
    endnote = 'Soccerplots - Data via Sofascore'

    radar = Radar(fontfamily="Arial")
    fig,ax = radar.plot_radar(ranges=ranges,params=selected_metrics,values=values,
                    alphas=[.75,.6],title=title,endnote=endnote, radar_color=['#B6282F', '#FFFFFF'])
    ax.set_title(f'Radar Chart - {selected_metrics}', fontsize=14, weight='bold', color='black', loc='center')
    ax.grid(True)
    st.pyplot(fig)

def main():
    configurar_pagina()
    df_maestro = cargar_general()
    st.title("Zona de pruebas: Radar por posición")
    jugador = st.selectbox("Elige un jugador", df_maestro['Jugador'])
    filtered_df = df_maestro[df_maestro['Jugador'] == jugador]
    filtered_df = filtered_df[['Jugador', 'Pos_1', 'Pos_2', 'Pos_3']]
    
    datos_jugadores = cargar_datos_jugadores()
    filtered_df = pd.merge(filtered_df, datos_jugadores, right_on='name', left_on='Jugador', how='left')
    filtered_df = filtered_df.drop(columns=['name', 'shortName', 'position', 'jerseyNumber', 'country'])
    
    # Mostrar selector de Jornada
    jornadas = filtered_df['Jornada'].unique().tolist()
    jornada_seleccionada = st.selectbox('Elige una Jornada', jornadas)
    filtered_df = filtered_df[filtered_df['Jornada'] == jornada_seleccionada]

    # Mostrar selector de Columna
    metrics_list = list(filtered_df.columns)[1:]
    selected_metrics = st.multiselect(
                'Choose The Metrics',metrics_list)
    
    if st.button('Generar Radar Chart'):
        filtered_df = filtered_df[selected_metrics]
        st.table(filtered_df)
        #radar_chart(filtered_df, selected_metrics, jornada_seleccionada,)



if __name__ == "__main__":
    main()