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

def obtener_rangos(datos_jugadores, selected_metrics, jugador):
    # Obtiene el maximo y minimo valor para las metricas seleccionadas para el jugador seleccionado a lo largo de las jornadas que haya jugado mas de 20 minutos
    datos_jugador_total = datos_jugadores[datos_jugadores['name'] == jugador]
    datos_jugador_total = datos_jugador_total[datos_jugador_total['minutesPlayed'] > 20] # Solo los partidos con mas de 20 minutos
    # Obtiene el maximo y minimo valor de las jornadas seleccionadas
    ranges = [(datos_jugador_total[metric].min(), datos_jugador_total[metric].max()) for metric in selected_metrics]
    return ranges

def radar_chart(data, selected_metrics, jugador, jornada_seleccionada, ranges, minutesPlayed):
    # obtener solo los valores de data
    data = data.values.tolist()[0]
    title = dict(
        title_name= f'Radar de acciones - {jugador}\n',
        subtitle_name = f'{jornada_seleccionada} \nMinutos jugados: {minutesPlayed}',
        title_color = '#192745',
        title_fontsize = 18,
        subtitle_fontsize = 10,
        subtitle_color = 'black',
    )
    endnote = 'Alianza Lima - Data via Sofascore'

    radar = Radar(background_color="#C0C0C0", patch_color="#28252C", label_color="#FFFFFF",
              range_color="#000000",fontfamily="Times New Roman")
    fig,ax = radar.plot_radar(ranges=ranges,params=selected_metrics,values=data
                              ,title=title,endnote=endnote, radar_color=['#192745', '#C0C0C0'])
    ax.grid(True)
    st.write(ranges)
    st.write(data)
    st.write(selected_metrics)
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
    filtered_df = filtered_df.drop(columns=['name', 'shortName', 'position', 'jerseyNumber', 'country','captain',
                                            'goalsPrevented','expectedAssists','expectedGoals','rating'])
    
    # Mostrar selector de Jornada
    jornadas = filtered_df['Jornada'].unique().tolist()
    jornada_seleccionada = st.selectbox('Elige una Jornada', jornadas)
    filtered_df = filtered_df[filtered_df['Jornada'] == jornada_seleccionada]

    # Mostrar selector de Columna
    metrics_list = list(filtered_df.select_dtypes(include=np.number).columns)
    # eliminar 'minutesPlayed' de metrics_list si está presente
    if 'minutesPlayed' in metrics_list:
        metrics_list.pop(metrics_list.index('minutesPlayed'))
        minutos_jugados = filtered_df['minutesPlayed'].values[0]
    selected_metrics = st.multiselect(
                'Choose The Metrics',metrics_list)
    
    if st.button('Generar Radar Chart'):
        filtered_df = filtered_df[selected_metrics]
        ranges = obtener_rangos(datos_jugadores, selected_metrics, jugador)
        radar_chart(filtered_df, selected_metrics, jugador, jornada_seleccionada, ranges, minutos_jugados)



if __name__ == "__main__":
    main()