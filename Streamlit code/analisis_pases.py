import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Carga de datos
df = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/XLSX finales/Resumen_AL_Jugadores.xlsx')

# Seleccionar jugador con Streamlit
jugador_selector = st.selectbox('Jugador:', sorted(df['Nombre'].unique()))

def generar_informe(jugador_seleccionado):
    df_jugador = df[df['Nombre'] == jugador_seleccionado].copy()

    # Asegurar que los nombres de las jornadas coincidan con los esperados
    df_jugador['Jornada'] = df_jugador['Jornada'].map({
        'Jornada 1 - Local vs Universidad Cesar Vallejo': 'J1',
        'Jornada 2 - Visita vs Alianza Atlético de Sullana': 'J2',
        'Jornada 3 - Local vs Universitario de Deportes': 'J3',
        'Jornada 4 - Visita vs Unión Comercio': 'J4',
        'Jornada 5 - Local vs Comerciantes Unidos': 'J5'
    })

    # Calcula promedios
    promedios = {
        'Pases Acertados': df['Pases Acertados'].mean(),
        'Balones Largos Acertados': df['Balones Largos Acertados'].mean(),
        'Centros Acertados': df['Centros Acertados'].mean()
    }

    fig = go.Figure()

    # Definir el ancho de las barras
    bar_width = 0.3

    for i, (estadistica, promedio, total_estadistica) in enumerate([
        ('Pases Acertados', promedios['Pases Acertados'], 'Total de Pases'),
        ('Balones Largos Acertados', promedios['Balones Largos Acertados'], 'Total de Balones Largos'),
        ('Centros Acertados', promedios['Centros Acertados'], 'Total de Centros')
    ]):
        # Agregar las barras para cada estadística
        fig.add_trace(go.Bar(x=df_jugador['Jornada'], y=df_jugador[estadistica], name=estadistica,
                             offsetgroup=i, marker_color='lightblue'))
        fig.add_trace(go.Bar(x=df_jugador['Jornada'], y=df_jugador[total_estadistica], name=total_estadistica,
                             offsetgroup=i, base=bar_width, marker_color='navy'))

        # Agregar línea de promedio
        fig.add_shape(type="line", x0=0, y0=promedio, x1=1, y1=promedio, line=dict(color="white", dash="dash"),
                      xref="paper", yref="y")

    # Actualizar layout
    fig.update_layout(title_text=f'Estadísticas por Jornada para {jugador_seleccionado}',
                      barmode='group',
                      plot_bgcolor='black',
                      paper_bgcolor='black',
                      font_color='white',
                      legend=dict(bgcolor='black', font_color='white'))
    
    st.plotly_chart(fig, use_container_width=True)

# Llamada a la función para generar gráficos interactivos
generar_informe(jugador_selector)