import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from mplsoccer.pitch import VerticalPitch
import os

# LOCAL VARIABLES

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

# GRAPH FUNCTIONS

def obtener_grafico_match_momentum( nombre_jornada, es_local = True):
    #df =  Obtener datos de un xlsx utilizando el nombre de la jornada
    # Procesar los datos para separar los valores positivos y negativos de momentum
    momentum_positivo = df[df['value'] > 0]
    momentum_negativo = df[df['value'] < 0]
    
    # Definir colores según si Alianza Lima es local o visitante
    color_alianza = 'blue' if es_local else 'orange'
    color_oponente = 'orange' if es_local else 'blue'

    # Crear el gráfico de Plotly
    fig = go.Figure()

    # Momentum positivo (Alianza Lima si es_local, de lo contrario Oponente)
    fig.add_trace(go.Bar(
        x=momentum_positivo['minute'],
        y=momentum_positivo['value'],
        name='Alianza Lima' if es_local else 'Oponente',
        marker_color=color_alianza
    ))

    # Momentum negativo (Oponente si es_local, de lo contrario Alianza Lima)
    fig.add_trace(go.Bar(
        x=momentum_negativo['minute'],
        y=momentum_negativo['value'],
        name='Oponente' if es_local else 'Alianza Lima',
        marker_color=color_oponente
    ))

    if not momentum_positivo.empty:
        x_positivo = momentum_positivo['minute']
        y_positivo = momentum_positivo['value']
        y_tendencia_positiva = ajuste_polinomial(x_positivo, y_positivo)
        
        fig.add_trace(go.Scatter(x=x_positivo, y=y_tendencia_positiva, mode='lines', name='Tendencia Local', line=dict(color=color_alianza, width=2)))

    # Añadir línea de tendencia polinomial para el Oponente (MATH FUNCTION)
    if not momentum_negativo.empty:
        x_negativo = momentum_negativo['minute']
        y_negativo = -momentum_negativo['value']  # Tomar valor absoluto para el ajuste
        y_tendencia_negativa = ajuste_polinomial(x_negativo, y_negativo)
        
        fig.add_trace(go.Scatter(x=x_negativo, y=-y_tendencia_negativa, mode='lines', name='Tendencia Visita', line=dict(color=color_oponente, width=2)))

    # Actualiza layout
    fig.update_layout(
        title="Momentum del partido",
        xaxis_title="Minuto",
        yaxis_title="Momentum",
        template="plotly_white",
        barmode='relative'
    )
    
    # Devuelve el gráfico de Plotly
    return fig

def mostrar_grafica_edad(df):
    cantidad_jornadas_jugadas = 6  # Actualizar

    minutos_columns = [col for col in df.columns if ' - Minutos' in col]
    for col in minutos_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[minutos_columns] = df[minutos_columns].fillna(0)

    df = df.sort_values(by='Dorsal')
    df['Total Minutos'] = df[minutos_columns].sum(axis=1)
    total_minutos_posibles = 90 * cantidad_jornadas_jugadas
    df['Porcentaje Minutos Jugados'] = (df['Total Minutos'] / total_minutos_posibles) * 100

    posiciones_unicas = df['Posición'].unique()
    colores = px.colors.qualitative.Set1
    mapeo_colores = {pos: colores[i % len(colores)] for i, pos in enumerate(posiciones_unicas)}
    # Crear el gráfico de dispersión con Plotly
    fig = go.Figure()

    for i, row in df.iterrows():
        color = mapeo_colores[row['Posición']]
        porcentaje_truncado = f"{row['Porcentaje Minutos Jugados']:.2f}"  # Formatear a dos decimales
        fig.add_trace(go.Scatter(
            x=[row['Edad 2024']], 
            y=[row['Porcentaje Minutos Jugados']],
            mode='markers',
            marker=dict(size=10, color=color),
            hoverinfo='text',
            text=f"{row['Jugador']}: {porcentaje_truncado}%",  # Usar el valor truncado
            name=row['Jugador']))

    fig.update_layout(
        title='Edad vs % de Minutos Jugados por Jugador',
        xaxis_title='Edad',
        yaxis_title='% de Minutos Jugados',
        template='plotly_dark',
        font=dict(color='white'),
        legend=dict(x=1.05, y=1),
        xaxis=dict(range=[15, 42], color='white'),
        yaxis=dict(color='white'),
        height=600  # Ajustar según necesidad
    )
    fig.add_shape(type="rect", x0=30, y0=-6, x1=45, y1=106,
              line=dict(width=0), fillcolor="red", opacity=0.2)

    # Jugadores de alta competencia (24 a 29 años), en morado
    fig.add_shape(type="rect", x0=24, y0=-6, x1=29, y1=106,
              line=dict(width=0), fillcolor="purple", opacity=0.3)

    #    Jugadores jóvenes (21 a 24 años), en rojo claro
    fig.add_shape(type="rect", x0=21, y0=-6, x1=24, y1=106,
              line=dict(width=0), fillcolor="blue", opacity=0.15)

    # Potrillos (menos de 20 años), en verde
    fig.add_shape(type="rect", x0=15, y0=-6, x1=20, y1=106,
              line=dict(width=0), fillcolor="green", opacity=0.2)
    st.plotly_chart(fig, use_container_width=True)

def mostrar_heatmap_pos_media(jugador,nombre_jornada,df_posiciones_medias,df_heatmaps):
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jornada, df_heatmap in df_heatmaps.items():
        if nombre_jornada in jornada:
            if jugador in df_heatmap:
                df_jugador = df_heatmap[jugador]
                if not df_jugador.empty:
                    pitch.kdeplot(df_jugador['x'], df_jugador['y'], ax=ax, levels=100, cmap='Blues',fill=True, shade_lowest=True, alpha=0.5)
                    fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador) & (df_posiciones_medias['Jornada'] == jornada)]
                    if not fila_jugador.empty:
                        pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
                        ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
                        ax.set_title(f"{jugador} - {nombres_jornadas[jornada]}", fontsize=14)
                
    plt.tight_layout()
    st.pyplot(fig)

def mostrar_pos_media_equipo(jugadores_disponibles,nombre_jornada,df_posiciones_medias):
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in jugadores_disponibles:
        fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador) & (df_posiciones_medias['Jornada'] == nombre_jornada) ]
        if not fila_jugador.empty:
            pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
            ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
            ax.set_title(f"Posicion media de los jugadores", fontsize=14)
    plt.tight_layout()
    st.pyplot(fig)

def generar_histograma_ofensivo(datos_jugador, nombre_jornada):
    
    datos_filtrados = datos_jugador[datos_jugador['Jornada'] == nombre_jornada]
    
    estadisticas_ofensivas = ['Contiendas Ganadas', 'Total de Contiendas', 'Tiros Fuera','Intentos de Anotacion Bloqueados', 
                                  'Intentos de Anotacion al Arco', 
                                  'Balones al Poste']
    e_o = ['Regates Ganados','Regates Intentados','Tiros Fuera','Tiros Bloqueados',
                        'Tiros al Arco', 'Balones al Poste']
    e_o_colors = ['green','blue','red','green','blue','blue']

    datos_acumulados = datos_filtrados[estadisticas_ofensivas].sum()
    # Crear el histograma con Plotly Graph Objects
    fig = go.Figure(data=[
        go.Bar(
            x=e_o,
            y=datos_acumulados.values,
            marker=dict(color=e_o_colors)
        )
    ])
    jugador_nombre = datos_filtrados.iloc[0]['Jugador'] if not datos_filtrados.empty else "Jugador desconocido"
    # Actualizar el diseño del gráfico
    fig.update_layout(
        title=f"Acciones Ofensivas de<br>{jugador_nombre}",
        xaxis_title="Estadística ofensiva",
        xaxis=dict(
            tickangle=-45
        ),
        yaxis=dict(
            title="Cantidad total",
            tickmode='array',
            tickvals=list(range(int(min(datos_acumulados.values)), int(max(datos_acumulados.values)) + 1)),
        ),
        template='plotly_dark',
        height=350,
    )
    # Devuelve la figura en plotly
    return fig

# MATH FUNCTIONS

def ajuste_polinomial(x, y, grado=8):
    """Realiza un ajuste polinomial de los datos y retorna valores ajustados."""
    coeficientes = np.polyfit(x, y, grado)
    polinomio = np.poly1d(coeficientes)
    return polinomio(x)

# INITIAL CONFIG AND LOAD 
def configurar_pagina():
    st.set_page_config(
        page_title="Análisis de jugadores de Alianza Lima Temporada 2024",
        layout='wide',
        page_icon=r'Imagenes\AL.png',
        initial_sidebar_state="expanded")

@st.cache_data
def cargar_general():
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/ALIANZA LIMA 2024.xlsx')
    return df

@st.cache_data
def cargar_datos_jugadores():
    # Carga de datos de los jugadores y estadísticas de pases
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/Archivos para el tablero final/Resumen_AL_Jugadores.xlsx')
    return df

def cargar_datos_mapas(df_maestro):
    df_posiciones_medias_total = pd.DataFrame()
    heatmaps_total = {}
    for jornada, nombre_jornada in nombres_jornadas.items():
        try:
            df_temp = pd.read_csv(f'Archivos para el tablero final/{jornada}_AL_posicionesprom.csv')
            df_temp['Jornada'] = jornada
            df_posiciones_medias_total = pd.concat([df_posiciones_medias_total, df_temp])
            df_heatmap = pd.read_excel(f'Archivos para el tablero final/{jornada}_heatmaps_jugadores.xlsx', sheet_name=None)
            heatmaps_total[jornada] = {sheet: df for sheet, df in df_heatmap.items() if sheet in df_maestro['Jugador'].values}
        except FileNotFoundError as e:
            st.error(f"No se encontró el archivo para {nombre_jornada}: {e}")
    return df_posiciones_medias_total.sort_values(by='position'), heatmaps_total

def main():
    configurar_pagina()
    #df = cargar_datos_jugadores() # Se cargan los datos de Resumen_AL_Jugadores.xlsx
    df_maestro = cargar_general() # Se cargan los datos de ALIANZA LIMA 2024.xlsx
    df_posiciones_medias, df_heatmaps = cargar_datos_mapas(df_maestro) # Se cargan los datos de las posiciones medias y mapa de calor
    titulo, alianza = st.columns([2,1])
    with titulo:
        st.title('Alianza Lima Temporada 2024')
    with alianza:
        st.image(f'Imagenes\AL.png', width=80)
    selectores, imagenes =  st.columns([4,1])

    with selectores:
        #Seleccion de jornada
        jornadas_disponibles = [value for key, value in nombres_jornadas.items()]
        jornada_seleccionada = st.selectbox('Selecciona una jornada:', jornadas_disponibles, key='jornada_selector')
        if jornada_seleccionada in nombres_jornadas.values():
            df = None
            df = cargar_datos_jugadores() # Se cargan los datos de Resumen_AL_Jugadores.xlsx
            jornada = [key for key, value in nombres_jornadas.items() if value == jornada_seleccionada][0]
            nombre_jornada = [value for key, value in nombres_jornadas.items() if value == jornada_seleccionada][0]
            df = df[(df['Jornada'] == nombre_jornada) & (df['minutesPlayed'] > 0)]
            df_titulares = df[df['substitute'] == False]
            nombres_titulares = df_titulares['name'].unique()
            nombres_jugadores_disponibles = df['name'].unique()
            nombres_jugadores_disponibles = nombres_jugadores_disponibles.tolist()
            nombres_jugadores_disponibles = sorted(nombres_jugadores_disponibles, key=lambda x: df[df['name'] == x]['minutesPlayed'].values[0],reverse=True)
            jugador_selector = st.selectbox('Selecciona un jugador:', nombres_jugadores_disponibles, key='jugador_selector')
            ruta_imagen_jugador = f"Imagenes/Jugadores/{jugador_selector}.png"
            if jugador_selector:
                pantalla_heatmap , pantalla_datos, pantalla_otros = st.columns([2,3,1])
                with pantalla_heatmap:
                    mostrar_heatmap_pos_media(jugador_selector,jornada,df_posiciones_medias,df_heatmaps)
                with pantalla_datos:
                    mostrar_pos_media_equipo(nombres_titulares,jornada,df_posiciones_medias)

    with imagenes:
        ruta_imagen_oponente = f"Imagenes/Oponentes/{jornada}.png"
        # Verificamos si el archivo existe antes de intentar mostrarlo
        if os.path.exists(ruta_imagen_oponente):
            st.image(ruta_imagen_oponente, width=90)
        else:
            st.markdown(f"No se encontró la imagen del oponente para {jornada}")
        if jugador_selector:
                if os.path.exists(ruta_imagen_jugador):
                    st.image(ruta_imagen_jugador, width=90)
                else:
                    st.markdown(f"No se encontró la imagen para {jugador_selector}")



if __name__ == "__main__":
    main()