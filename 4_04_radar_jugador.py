import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import colorsys

# Configuración de visualización
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Diccionario de traducción mejorado
TRADUCCIONES = {
    'goals': 'Goles',
    'assists': 'Asistencias',
    'keyPasses': 'Pases clave',
    'groundDuelsWonPercentage': '% Duelo ganado',
    'totalShots': 'Tiros totales',
    'shotsOnTarget': 'Tiros al arco',
    'goalConversionPercentage': '% Conversión',
    'successfulDribbles': 'Regates exitosos',
    'accuratePasses': 'Pases precisos',
    'accurateCrosses': 'Centros precisos',
    'accurateFinalThirdPasses': 'Pases último tercio',
    'wasFouled': 'Faltas recibidas',
    'minutesPlayed': 'Minutos jugados',
    'dispossessed': 'Pérdidas de balón',
    'offsides': 'Offsides'
}

UNIDADES = {
    'goals': '',
    'assists': '',
    'groundDuelsWonPercentage': '%',
    'keyPasses': '',
    'totalShots': '',
    'shotsOnTarget': '',
    'goalConversionPercentage': '%',
    'successfulDribbles': '',
    'accuratePasses': '',
    'accurateCrosses': '',
    'accurateFinalThirdPasses': '',
    'wasFouled': '',
    'minutesPlayed': ' min',
    'dispossessed': '',
    'offsides': ''
}

def cargar_datos():
    try:
        df = pd.read_csv("Datos al J17.csv", sep=';')
        numeric_cols = list(TRADUCCIONES.keys())
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        df['player'] = df['player'].str.strip()
        return df
    except Exception as e:
        print(f"Error al cargar datos: {str(e)}")
        return None

def filtrar_jugadores_referencia(df, min_minutos=500):
    posiciones = ['EXD', 'EXI']
    return df[
        (df['minutesPlayed'] >= min_minutos) & 
        (
            df['Posicion'].isin(posiciones) |
            df['Posicion S_1'].isin(posiciones) |
            df['Posicion S_2'].isin(posiciones)
        )
    ].copy()

def calcular_percentiles(df, jugador_nombre, variables, min_minutos=500, per90=False):
    df_ref = filtrar_jugadores_referencia(df, min_minutos)
    jugador_mask = df['player'].str.lower() == jugador_nombre.lower()
    if not jugador_mask.any():
        raise ValueError(f"Jugador {jugador_nombre} no encontrado")

    jugador_data = df[jugador_mask].iloc[0]
    resultados = {
        'jugador': jugador_data['player'],
        'equipo': jugador_data.get('team', 'Desconocido'),
        'percentiles': {},
        'valores_jugador': {},
        'valores_referencia': {},
        'top_jugadores': {}
    }

    for var in variables:
        if var not in df.columns:
            continue

        if per90:
            valores_ref = df_ref[var] / (df_ref['minutesPlayed'] / 90)
            valor_jugador = jugador_data[var] / (jugador_data['minutesPlayed'] / 90)
        else:
            valores_ref = df_ref[var]
            valor_jugador = jugador_data[var]

        percentiles = np.linspace(0, 100, 101)
        valores_percentiles = np.percentile(valores_ref.dropna(), percentiles)
        percentil_jugador = np.interp(valor_jugador, valores_percentiles, percentiles)

        top_players = df_ref[['player', 'team', var]].sort_values(var, ascending=False).head(50)

        resultados['percentiles'][var] = percentil_jugador
        resultados['valores_jugador'][var] = valor_jugador
        resultados['valores_referencia'][var] = {
            'min': np.min(valores_ref.dropna()),
            'max': np.max(valores_ref.dropna()),
            'media': np.mean(valores_ref.dropna()),
            'mediana': np.median(valores_ref.dropna())
        }
        resultados['top_jugadores'][var] = top_players

    return resultados

def get_color_for_percentile(percentile, line=False):
    if percentile <= 40:
        color = (255, 0, 0)  # Rojo
    elif percentile <= 60:
        color = (255, 165, 0)  # Naranja
    elif percentile <= 70:
        color = (255, 255, 0)  # Amarillo
    elif percentile >=70:
        color = (144, 238, 144)  # Verde claro
    else:
        color = (0, 100, 0)  # Verde oscuro
    
    # Ajustamos la opacidad
    if line:
        return f'rgba({color[0]}, {color[1]}, {color[2]}, 1.0)'  # Líneas más opacas
    else:
        return f'rgba({color[0]}, {color[1]}, {color[2]}, 0.6)'  # Relleno más transparente

def crear_visualizacion(resultados, per90=False):
    variables = list(resultados['percentiles'].keys())
    df_radar = pd.DataFrame({
        'Métrica': [TRADUCCIONES.get(v, v) for v in variables],
        'Percentil': [resultados['percentiles'][v] for v in variables],
        'Valor': [resultados['valores_jugador'][v] for v in variables],
        'Unidad': [UNIDADES.get(v, '') for v in variables]
    })

    # Creamos una figura con solo el radar (sin subplots)
    fig = go.Figure()

    # Añadimos el radar con relleno segmentado por color
    for i in range(len(variables)):
        start_idx = i
        end_idx = (i + 1) % len(variables)
        
        # Obtenemos los percentiles para este segmento
        p_start = df_radar['Percentil'].iloc[start_idx]
        p_end = df_radar['Percentil'].iloc[end_idx]
        avg_percentile = (p_start + p_end) / 2
        
        # Color para el relleno (con opacidad 0.6)
        fill_color = get_color_for_percentile(avg_percentile)
        
        # Color para la línea (más opaco)
        line_color = get_color_for_percentile(avg_percentile, line=True)
        
        # Creamos un segmento para este rango
        fig.add_trace(
            go.Scatterpolar(
                r=[0, p_start, p_end],
                theta=[
                    df_radar['Métrica'].iloc[start_idx],
                    df_radar['Métrica'].iloc[start_idx],
                    df_radar['Métrica'].iloc[end_idx]
                ],
                fill='toself',
                fillcolor=fill_color,
                line=dict(color=line_color, width=2),
                hoverinfo='none',
                showlegend=False,
                mode='lines'
            )
        )

    # Añadimos los vértices con colores según percentil
    fig.add_trace(
        go.Scatterpolar(
            r=df_radar['Percentil'],
            theta=df_radar['Métrica'],
            mode='markers',
            marker=dict(
                size=10,
                color=[get_color_for_percentile(p, line=True) for p in df_radar['Percentil']],
                line=dict(color='white', width=1)  # Cambiamos el borde a blanco para contraste
            ),
            hoverinfo='text',
            hovertext=[
                f"{row['Métrica']}: {row['Valor']:.0f}{row['Unidad']}<br>Percentil: {row['Percentil']:.0f}%"
                for _, row in df_radar.iterrows()
            ],
            showlegend=False
        )
    )

    # Configuramos el polar con fondo oscuro
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100], 
                tickvals=[0, 25, 50, 75, 100], 
                ticktext=["0%", "25%", "50%", "75%", "100%"],
                tickfont=dict(color='white'),  # Texto de ejes en blanco
                gridcolor='rgba(255, 255, 255, 0.3)',  # Líneas de grid más claras
                linecolor='rgba(255, 255, 255, 0.5)'  # Línea del eje
            ),
            angularaxis=dict(
                direction="clockwise", 
                rotation=90,
                tickfont=dict(color='white'),  # Texto angular en blanco
                linecolor='rgba(255, 255, 255, 0.5)',  # Línea del eje
                gridcolor='rgba(255, 255, 255, 0.3)'  # Líneas de grid
            ),
            bgcolor='rgba(30, 30, 30, 0.7)'  # Fondo oscuro semitransparente
        ),
        title=f"Análisis Comparativo: {resultados['jugador']} ({resultados['equipo']}) vs Extremos",
        title_font=dict(size=20, color='white'),  # Título en blanco
        showlegend=False,
        height=800,
        paper_bgcolor='rgb(20, 20, 20)',  # Fondo general oscuro
        plot_bgcolor='rgb(20, 20, 20)',  # Fondo del plot oscuro
        margin=dict(t=100, b=50, l=50, r=50),
        font=dict(color='white')  # Texto general en blanco
    )

    # Creamos la tabla de datos para incluir en el radar
    tabla_data = []
    for var in variables:
        ref = resultados['valores_referencia'][var]
        tabla_data.append([
            TRADUCCIONES.get(var, var),
            f"{resultados['valores_jugador'][var]:.0f}{UNIDADES.get(var, '')}",
            f"{resultados['percentiles'][var]:.0f}%",
            f"{ref['min']:.0f}{UNIDADES.get(var, '')}",
            f"{ref['mediana']:.0f}{UNIDADES.get(var, '')}",
            f"{ref['max']:.0f}{UNIDADES.get(var, '')}"
        ])

    # Añadimos la tabla como anotación en el centro del radar
    fig.add_annotation(
        x=1,
        y=0.8,
        xref="paper",
        yref="paper",
        text="<br>".join([
            "<b>Métrica | Valor | Percentil | Mín | Med | Máx</b>",
            *[
                f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}"
                for row in tabla_data
            ]
        ]),
        showarrow=False,
        font=dict(size=10, color='white'),  # Texto de tabla en blanco
        align="left",
        bordercolor="white",  # Borde blanco
        borderwidth=1,
        borderpad=4,
        bgcolor="rgba(40, 40, 40, 0.9)",  # Fondo oscuro para la tabla
        opacity=0.3
    )

    return fig

if __name__ == "__main__":
    df = cargar_datos()
    if df is not None:
        variables_analisis = ['goals', 'assists', 'groundDuelsWonPercentage', 'totalShots', 'shotsOnTarget', 'successfulDribbles', 'accurateCrosses']

        resultados = calcular_percentiles(df, jugador_nombre="Gaspar Gentile", variables=variables_analisis, min_minutos=400, per90=False)
        fig = crear_visualizacion(resultados, per90=False)
        fig.show()

        df_referencia = filtrar_jugadores_referencia(df, min_minutos=400)
        print(f"\n\u2794 Muestra de {len(df_referencia)} jugadores extremos (minutos mínimos: {df_referencia['minutesPlayed'].min():.0f} min)")