import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from mplsoccer.pitch import VerticalPitch
import os
import ScraperFC as sfc
from scipy import stats

#Utilizar datos directamente de ScraperFC
sofascore = sfc.Sofascore()

URLs_jornadas = {
    "J1": "https://www.sofascore.com/universidad-cesar-vallejo-alianza-lima/lWsGfc#11967822",
    "J2": "https://www.sofascore.com/alianza-lima-alianza-atletico-de-sullana/hWslW#11981247",
    "J3": "https://www.sofascore.com/alianza-lima-universitario-de-deportes/fWslW#12005095",
    "J4": "https://www.sofascore.com/union-comercio-alianza-lima/lWsGtu#12019977",
    "J5": "https://www.sofascore.com/comerciantes-unidos-alianza-lima/lWsjxKb#12061051",
    "J6": "https://www.sofascore.com/asociacion-deportiva-tarma-alianza-lima/lWshlJc#12076348",
    "J7": "https://www.sofascore.com/alianza-lima-club-sporting-cristal/cWslW#12101149",
}

nombres_jornadas = {
        "J1": "Jornada 1 - Local vs Universidad Cesar Vallejo",
        "J2": "Jornada 2 - Visita vs Alianza Atlético de Sullana",
        "J3": "Jornada 3 - Local vs Universitario de Deportes",
        "J4": "Jornada 4 - Visita vs Unión Comercio",
        "J5": "Jornada 5 - Local vs Comerciantes Unidos",
        "J6": "Jornada 6 - Visita vs ADT",
        "J7": "Jornada 7 - Local vs Sporting Cristal"
}

def ajuste_polinomial(x, y, grado=8):
    """Realiza un ajuste polinomial de los datos y retorna valores ajustados."""
    coeficientes = np.polyfit(x, y, grado)
    polinomio = np.poly1d(coeficientes)
    return polinomio(x)

def obtener_grafico_match_momentum(url, es_local = True):
    df = sofascore.match_momentum(url)
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

    # Añadir línea de tendencia polinomial para el Oponente
    if not momentum_negativo.empty:
        x_negativo = momentum_negativo['minute']
        y_negativo = -momentum_negativo['value']  # Tomar valor absoluto para el ajuste
        y_tendencia_negativa = ajuste_polinomial(x_negativo, y_negativo)
        
        fig.add_trace(go.Scatter(x=x_negativo, y=-y_tendencia_negativa, mode='lines', name='Tendencia Visita', line=dict(color=color_oponente, width=2)))

    # Actualizar layout del gráfico
    fig.update_layout(
        title="Momentum del partido",
        xaxis_title="Minuto",
        yaxis_title="Momentum",
        template="plotly_white",
        barmode='relative'
    )
    
    # Retornar el gráfico de Plotly
    return fig

@st.cache_resource
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

@st.cache_resource
def generar_histograma_ofensivo(jugador_selector, df, estadisticas_ofensivas, e_o, e_o_colors):
    # Extraer los datos de estas estadísticas para el jugador seleccionado de df
    datos_jugador = df[df['Jugador'] == jugador_selector]
    datos_acumulados = datos_jugador[estadisticas_ofensivas].sum()
    # Crear el histograma con Plotly Graph Objects
    fig = go.Figure(data=[
        go.Bar(
            x=e_o,
            y=datos_acumulados.values,
            marker=dict(color=e_o_colors)
        )
    ])
    
    # Actualizar el diseño del gráfico
    fig.update_layout(
        title=f"Acciones Ofensivas de<br>{jugador_selector}",
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
    
    return fig

@st.cache_data
def draw_player_heatmaps(jugador,df_posiciones_medias,heatmaps):
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    num_jornadas = len(heatmaps)
    cols = 2
    rows = -(-num_jornadas // cols)  # Redondeo hacia arriba
    fig, axs = plt.subplots(rows, cols, figsize=(10 * cols, 7 * rows))
    fig.subplots_adjust(hspace=0.5, wspace=0.5)
    axs = axs.flatten()
    plot_counter = 0
    for jornada, archivo_excel in heatmaps.items():
        with pd.ExcelFile(archivo_excel) as xls:
            if jugador in xls.sheet_names:
                df_heatmap = pd.read_excel(xls, sheet_name=jugador)
                if not df_heatmap.empty:
                    ax = axs[plot_counter]
                    pitch.draw(ax=ax)
                    ax.set_facecolor((0, 0, 1, 0.5))
                    pitch.kdeplot(df_heatmap['x'], df_heatmap['y'], ax=ax, levels=100, cmap='Blues',fill=True, shade_lowest=True, alpha=0.5)
                    fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador) & (df_posiciones_medias['Jornada'] == jornada)]
                    if not fila_jugador.empty:
                        pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
                        ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
                        ax.set_title(f"{jugador} - {nombres_jornadas[jornada]}", fontsize=14)
                    plot_counter += 1
                
    for j in range(plot_counter, rows * cols):
        axs[j].axis('off')
    plt.tight_layout()
    st.pyplot(fig)

@st.cache_resource
# Función para cargar los DataFrames de posiciones medias y heatmaps para todas las jornadas
def cargar_datos_mapas():
    df_posiciones_medias_total = pd.DataFrame()
    heatmaps_total = {}
    for jornada, nombre_jornada in nombres_jornadas.items():
        try:
            df_temp = pd.read_csv(f'CSV obtenidos/{jornada}_pos_jugadores.csv')
            df_temp['Jornada'] = jornada
            df_posiciones_medias_total = pd.concat([df_posiciones_medias_total, df_temp])
            heatmaps_total[jornada] = f'CSV obtenidos/{jornada}_heatmaps_jugadores.xlsx'
        except FileNotFoundError as e:
            st.error(f"No se encontró el archivo para {nombre_jornada}: {e}")
    return df_posiciones_medias_total.sort_values(by='jerseyNumber'), heatmaps_total

def configurar_pagina():
    st.set_page_config(
        page_title="Análisis de jugadores de Alianza Lima Temporada 2024",
        layout='wide',
        page_icon=r'Imagenes\AL.png')

@st.cache_data
def cargar_general():
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/ALIANZA LIMA 2024.xlsx')
    return df

@st.cache_data
def cargar_datos_jugadores():
    # Carga de datos de los jugadores y estadísticas de pases
    df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/XLSX finales/Resumen_AL_Jugadores.xlsx')
    return df

def main():
    configurar_pagina()
    
    df = cargar_datos_jugadores() # Se cargan los datos de Resumen_AL_Jugadores.xlsx
    df_maestro = cargar_general() # Se cargan los datos de ALIANZA LIMA 2024.xlsx
    df_posiciones_medias, df_heatmaps = cargar_datos_mapas() # Se cargan los datos de posicion y heatmaps
    
    st.title('Alianza Lima Temporada 2024')

    blank, selectores, imagenes =  st.columns([1,4,2])
    with blank:
        mostrar_datos_jugador = blank.button("Mostrar datos jugador")
        mostrar_datos_jornada = blank.button("Mostrar datos jornada")

    with selectores:
        #Seleccion de jugador y jornada
        jugadores_disponibles = df_maestro['Jugador'].unique()
        jugador_selector = st.selectbox('Selecciona un jugador:', jugadores_disponibles, key='jugador_selector')
        jornadas_disponibles = df['Jornada'].unique()
        jornada_seleccionada = st.selectbox('Selecciona una jornada:', jornadas_disponibles, key='jornada_selector')
    with imagenes:
        ruta_imagen = f"Imagenes/Jugadores/{jugador_selector}.png"
        
        # Verificamos si el archivo existe antes de intentar mostrarlo
        if os.path.exists(ruta_imagen):
            st.image(ruta_imagen, width=175)  # Puedes ajustar el ancho como lo necesites
        else:
            st.markdown(f"No se encontró la imagen para {jugador_selector}")
    
    pantalla_graficos, pantalla_botones, pantalla_detalles = st.columns([5, 2, 3])
    
    if mostrar_datos_jugador:
        with pantalla_botones:
            #Obtiene los datos de las jornadas del jugador seleccionado
            detalles_jugador = df[(df['Jugador'] == jugador_selector)]

            datos_jugador = df_maestro[(df_maestro['Jugador'] == jugador_selector )]

            datos_acumulados = detalles_jugador.sum()
            datos_promedio = detalles_jugador.mean(numeric_only=True,skipna=True)
            # Mostrar Goles, Asistencias y Minutos Jugados
            st.metric(label="Goles 2024", value=int(datos_jugador['Goles']))
            st.metric(label="Asistencias 2024", value=int(datos_jugador['Asistencias']))
            st.metric(label="Minutos totales", value=f"{int(datos_jugador['Minutos'])} mins")
        with pantalla_detalles:
            st.subheader('Detalles del Jugador', anchor=None)
        
            col1, col2 = st.columns([2.25, 5])

            with col1:  
                st.markdown(f"<span style='color: grey;'>Posición: {datos_jugador['Posición'].item()}</span>", unsafe_allow_html=True)
                st.markdown(f"<span style='color: blue;'>Dorsal: {datos_jugador['Dorsal'].item()}</span>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
                # Mostrar Tarjetas Rojas y Amarillas
                st.metric(label="T. Amarillas", value=datos_jugador['Amarillas'])
                st.metric(label="T. Rojas", value=datos_jugador['Rojas'])
                st.metric(label="Faltas",value = datos_acumulados['Faltas'].item())
                st.metric(label="Recibió falta",value = datos_acumulados['Fue Faltado'].item())
    
            with col2:

                if st.button('Estadisticas de ataque'):
                    st.header('Aspecto ofensivo')
                    # Definir estadísticas de acciones ofensivas
                    estadisticas_ofensivas = ['Contiendas Ganadas', 'Total de Contiendas', 'Tiros Fuera','Intentos de Anotacion Bloqueados', 
                                  'Intentos de Anotacion al Arco', 
                                  'Balones al Poste']
                    e_o = ['Regates Ganados','Regates Intentados','Tiros Fuera','Tiros Bloqueados',
                        'Tiros al Arco', 'Balones al Poste']
                    e_o_colors = ['green','blue','red','green','blue','blue']
                    stats_ofensivas = generar_histograma_ofensivo(jugador_selector, df, estadisticas_ofensivas, e_o, e_o_colors)
                    st.plotly_chart(stats_ofensivas, use_container_width=True) #Muestra la grafica de ofensivas
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.subheader('Concentración ofensiva')
                    st.metric(label=f"Fallos importantes:", value=int(datos_acumulados['Grandes Oportunidades Falladas']))
                    st.metric(label=f"Fueras de juego:",value=int(datos_acumulados['Total de Fueras de Juego']))
                    st.metric(label=f"Penales ganados:",value=int(datos_acumulados['Penaltis Ganados']))
                    st.metric(label=f"Penales fallados:",value=int(datos_acumulados['Penaltis Fallados']))
                if st.button('Estadisticas de generación de juego'):
                    st.header('Generación de juego')
                    estadisticas_generacion = ['Pases Acertados', 'Balones Largos Acertados', 'Centros Acertados',
                                           'Total de Pases', 'Total de Balones Largos', 'Total de Centros']
                    #stats_generacion = generar_histograma_generacion(datos_jugador, datos_acumulados, datos_promedio, estadisticas_generacion)
                
                if st.button('Estadísticas defensivas'):
                    st.header('Aspecto defensivo')
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.subheader('Concentración defensiva')
                    st.metric(label=f"Penales concedidos:",value=int(datos_acumulados['Penaltis Concedidos']))
                    st.metric(label=f"Balón perdido:",value=int(datos_acumulados['Desposesiones']))
                    st.metric(label="Perdida de posesión:",value=int(datos_acumulados['Posesion Perdida']))
        
        
    if mostrar_datos_jornada:
        # Obtener url
        nombres_jornadas_invertidos = {v: k for k, v in nombres_jornadas.items()}
        clave_jornada = nombres_jornadas_invertidos[jornada_seleccionada]
        jornada_url = URLs_jornadas[clave_jornada]
        archivo_excel_heatmap = df_heatmaps.get(jornada_seleccionada)
        
        with pantalla_graficos:
    
            # Dividiendo la pantalla_heatmaps en dos columnas con proporción 5:1
            col_graficos, col_minutos = st.columns([5, 1])
    
            with col_graficos:
            # Genera los mapas de calor
                if st.button('Generar mapas de calor'):
                    st.subheader('Mapas de calor (mayor tonalidad de azul mayor presencia en zona de juego)')
                    # Mostrar heatmap si se ha seleccionado un jugador
                    if jugador_selector and archivo_excel_heatmap:
                        with pd.ExcelFile(archivo_excel_heatmap) as xls:
                            if jugador_selector in xls.sheet_names:
                                df_heatmap = pd.read_excel(xls, sheet_name=jugador_selector)
                            if not df_heatmap.empty:
                                pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
                                fig, ax = pitch.draw(figsize=(10, 7))
                                pitch.kdeplot(df_heatmap['x'], df_heatmap['y'], ax=ax, levels=100, cmap='Blues', fill=True, shade_lowest=True, alpha=0.5)
                                fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador_selector) & (df_posiciones_medias['Jornada'] == jornada_seleccionada)]
                                if not fila_jugador.empty:
                                    pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
                                    ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
                                    ax.set_title(f"{jugador_selector} - {nombres_jornadas[jornada_seleccionada]}", fontsize=14)
                                st.pyplot(fig)
                # Mostrar el gráfico de Edad vs minutos jugados del equipo
                if st.button('Mostrar gráficas de equipo'):
                    st.subheader('Edad vs % minutos jugados')
                    mostrar_grafica_edad(df_maestro)
                    momentum = obtener_grafico_match_momentum(jornada_url, True if "Local" in nombres_jornadas[jornada_seleccionada] else False)
                    st.plotly_chart(momentum, use_container_width=True)
        #with col_minutos:
            #st.subheader("Minutos jugados por Jornada")
    
            #jornadas = ['J1 - Minutos', 'J2 - Minutos', 'J3 - Minutos', 'J4 - Minutos', 
            #    'J5 - Minutos', 'J6 - Minutos']
           # for jornada in jornadas:
            #    minutos = detalles_jugador.get(jornada, np.nan)  # Usar np.nan como valor por defecto para manejar adecuadamente la ausencia de datos
           #     # Verificar si minutos es NaN o 0
           #     if not np.isnan(minutos) and minutos != 0:
           #         minutos = int(minutos)  # Convertir a entero si es un número válido y diferente de 0
            #        st.metric(label=jornada, value=f"{minutos}")
           #     else:
           #         st.metric(label=jornada, value="N/J")


        

if __name__ == "__main__":
    main()