import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from mplsoccer.pitch import VerticalPitch
import ScraperFC as sfc
from scipy import stats

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




def main():
    st.title('Alianza Lima Temporada 2024')
    jornada_seleccionada = st.selectbox('Selecciona una jornada', list(nombres_jornadas.keys()), format_func=lambda x: nombres_jornadas[x])
    jornada_url = URLs_jornadas[jornada_seleccionada]
    momentum = obtener_grafico_match_momentum(jornada_url, True if "Local" in nombres_jornadas[jornada_seleccionada] else False)
    st.plotly_chart(momentum, use_container_width=True)
    # Cargar datos de mapas y heatmaps
    df_posiciones_medias, heatmaps_total = cargar_datos_mapas()
    archivo_excel_heatmap = heatmaps_total.get(jornada_seleccionada)

    jugadores_disponibles = df_posiciones_medias[df_posiciones_medias['Jornada'] == jornada_seleccionada]['name'].unique()
    jugador_seleccionado = st.selectbox("Selecciona un jugador:", jugadores_disponibles)

    # Mostrar heatmap si se ha seleccionado un jugador
    if jugador_seleccionado and archivo_excel_heatmap:
        with pd.ExcelFile(archivo_excel_heatmap) as xls:
            if jugador_seleccionado in xls.sheet_names:
                df_heatmap = pd.read_excel(xls, sheet_name=jugador_seleccionado)
            if not df_heatmap.empty:
                pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
                fig, ax = pitch.draw(figsize=(10, 7))
                pitch.kdeplot(df_heatmap['x'], df_heatmap['y'], ax=ax, levels=100, cmap='Blues', fill=True, shade_lowest=True, alpha=0.5)
                fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador_seleccionado) & (df_posiciones_medias['Jornada'] == jornada_seleccionada)]
                if not fila_jugador.empty:
                    pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
                    ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
                    ax.set_title(f"{jugador_seleccionado} - {nombres_jornadas[jornada_seleccionada]}", fontsize=14)
                st.pyplot(fig)

if __name__ == "__main__":
    main()
