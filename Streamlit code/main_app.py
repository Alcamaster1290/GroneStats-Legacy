import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from mplsoccer.pitch import VerticalPitch

nombres_jornadas = {
        "J1": "Jornada 1 - Local vs Universidad Cesar Vallejo",
        "J2": "Jornada 2 - Visita vs Alianza Atlético de Sullana",
        "J3": "Jornada 3 - Local vs Universitario de Deportes",
        "J4": "Jornada 4 - Visita vs Unión Comercio",
        "J5": "Jornada 5 - Local vs Comerciantes Unidos",
        "J6": "Jornada 6 - Visita vs ADT",
}
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
def generar_histograma(jugador_selector, df, estadisticas_ofensivas, e_o, e_o_colors):
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
            df_temp = pd.read_csv(f'CSV obtenidos/{nombre_jornada}_posicion_jugadores.csv')
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
    
    df = cargar_datos_jugadores()
    df_maestro = cargar_general()  # Carga el DataFrame maestro con los detalles de los jugadores
    st.title('Alianza Lima Temporada 2024')
    # Carga de datos de posiciones medias y heatmaps
    df_posiciones_medias, heatmaps = cargar_datos_mapas()
    
    pantalla_heatmaps, pantalla_botones, pantalla_jugador = st.columns([5, 1.5, 3])
    
    with pantalla_botones:
        # Botón de Selección de Jugador
        jugador_selector = st.selectbox('Selecciona un jugador:', sorted(df['Jugador'].unique()), key='jugador_selector')
        detalles_jugador = df_maestro[df_maestro['Jugador'] == jugador_selector].iloc[0]
        # Definir estadísticas de acciones ofensivas
        estadisticas_ofensivas = ['Contiendas Ganadas', 'Total de Contiendas', 'Tiros Fuera','Intentos de Anotacion Bloqueados', 
                                  'Intentos de Anotacion al Arco', 
                                  'Balones al Poste']
        e_o = ['Regates Ganados','Regates Intentados','Tiros Fuera','Tiros Bloqueados',
               'Tiros al Arco', 'Balones al Poste']
        e_o_colors = ['green','blue','red','green','blue','blue']
        stats_ofensivas = generar_histograma(jugador_selector, df, estadisticas_ofensivas, e_o, e_o_colors)
        st.plotly_chart(stats_ofensivas, use_container_width=True) #Muestra la grafica de ofensivas

    with pantalla_heatmaps:
    
        # Dividiendo la pantalla_heatmaps en dos columnas con proporción 5:1
        col_graficos, col_minutos = st.columns([5, 1])
    
        with col_graficos:
            # Genera los mapas de calor
            if st.button('Generar mapas de calor'):
                st.subheader('Mapas de calor (mayor tonalidad de azul mayor presencia en zona de juego)')
                draw_player_heatmaps(jugador_selector, df_posiciones_medias, heatmaps)
            # Mostrar el gráfico en pantalla_heatmaps
            if st.button('Mostrar gráficas de equipo'):
                st.subheader('Edad vs % minutos jugados')
                mostrar_grafica_edad(df_maestro)
        with col_minutos:
            st.subheader("Minutos jugados por Jornada")
    
            jornadas = ['J1 - Minutos', 'J2 - Minutos', 'J3 - Minutos', 'J4 - Minutos', 
                'J5 - Minutos', 'J6 - Minutos']
            for jornada in jornadas:
                minutos = detalles_jugador.get(jornada, np.nan)  # Usar np.nan como valor por defecto para manejar adecuadamente la ausencia de datos
                # Verificar si minutos es NaN o 0
                if not np.isnan(minutos) and minutos != 0:
                    minutos = int(minutos)  # Convertir a entero si es un número válido y diferente de 0
                    st.metric(label=jornada, value=f"{minutos}")
                else:
                    st.metric(label=jornada, value="N/J")


    with pantalla_jugador:
        st.subheader('Detalles del Jugador', anchor=None)
        st.markdown(f"<span style='color: grey;'>Posición: {detalles_jugador['Posición']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: blue;'>Dorsal: {detalles_jugador['Dorsal']}</span>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2 = st.columns([3.75, 5])

        datos_jugador = df[df['Jugador'] == jugador_selector]
        datos_acumulados = datos_jugador.sum()
        datos_promedio = datos_jugador.mean(numeric_only=True,skipna=True)

        with col1:  # Mostrar Tarjetas Rojas y Amarillas
            st.metric(label="T. Rojas", value=detalles_jugador['Rojas'])
            st.metric(label="T. Amarillas", value=detalles_jugador['Amarillas'])
            st.metric(label="Faltas",value = datos_acumulados['Faltas'])
            st.metric(label="Recibió falta",value = datos_acumulados['Fue Faltado'])
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader('Concentración defensiva')
            st.metric(label=f"Penales concedidos:",value=int(datos_acumulados['Penaltis Concedidos']))
            st.metric(label=f"Balón perdido:",value=int(datos_acumulados['Desposesiones']))
            st.metric(label="Perdida de posesión:",value=int(datos_acumulados['Posesion Perdida']))
    
        with col2:  # Mostrar Goles, Asistencias y Minutos Jugados
            st.metric(label="Goles", value=detalles_jugador['Goles'])
            st.metric(label="Asistencias", value=detalles_jugador['Asistencias'])
            st.metric(label="Minutos totales", value=f"{detalles_jugador['Minutos']} mins")
            st.metric(label="Tiempo de juego promedio",value=f"{int(datos_promedio['Minutos Jugados'])} mins" )
            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader('Concentración ofensiva')
            st.metric(label=f"Fallos importantes:", value=int(datos_acumulados['Grandes Oportunidades Falladas']))
            st.metric(label=f"Fueras de juego:",value=int(datos_acumulados['Total de Fueras de Juego']))
            st.metric(label=f"Penales ganados:",value=int(datos_acumulados['Penaltis Ganados']))
            st.metric(label=f"Penales fallados:",value=int(datos_acumulados['Penaltis Fallados']))
            

if __name__ == "__main__":
    main()
