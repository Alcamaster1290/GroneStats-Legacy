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
    #"J11": "Apertura - J11 - Local vs Atletico Grau",
    #"J12": "Apertura - J12 - Local vs Sport Boys",
    #"J13": "Apertura - J13 - Visita vs Melgar",
    #"J14": "Apertura - J14 - Local vs UTC",
    "C1": "Copa Libertadores - J1 - Local vs Fluminense", 
    #"C2": "Copa Libertadores - J2 - Visita vs Cerro Porteño",
    #"C3": "Copa Libertadores - J3 - Visita vs Colo Colo"
}

posiciones_map = {
    'G': 'Portero',
    'D': 'Defensa',
    'M': 'Mediocampista',
    'F': 'Delantero'
}

nombres_pos_map = {
    # Portero
    'POR': 'Portero',
    # Defensa
    'DFI': 'Defensa izquierdo',
    'DFD': 'Defensa derecho',
    'DFC': 'Defensa central',
    'LIB': 'Defensa libero',
    'LD': 'Lateral derecho',
    'LI': 'Lateral izquierdo',
    'CRI': 'Carrilero izquierdo',
    'CRD': 'Carrilero derecho',
    # Mediocampista
    'MCD': 'Mediocampista central def.',
    'MCC': 'Mediocampista contencion',
    'VLX': 'Volante mixto',
    'VLD': 'Volante derecho',
    'VLI': 'Volante izquierdo',
    'MCO': 'Mediocampista enganche',
    # Delantero
    'EXI': 'Extremo izquierdo',
    'EXD': 'Extremo derecho',
    'SDC': 'Segundo delantero centro',
    'DLC': 'Delantero centro'
}

Pos_Prim_Map = {
    'POR': 'G',
    'DFI': 'D',
    'DFD': 'D',
    'DFC': 'D',
    'LIB': 'D',
    'LD': 'D',
    'LI': 'D',
    'CRI': 'D',
    'CRD': 'D',
    'MCD': 'D',
    'MCC': 'M',
    'VLX': 'M',
    'VLD': 'M',
    'VLI': 'M',
    'MCO': 'M',
    'EXI': 'F',
    'EXD': 'F',
    'SDC': 'F',
    'DLC': 'F'
}

Pos_Secu_Map = {
    'POR': '0',
    'DFI': '0',
    'DFD': '0',
    'DFC': '0',
    'LIB': '0',
    'LD': 'M',
    'LI': 'M',
    'CRI': 'M',
    'CRD': 'M',
    'MCD': 'M',
    'MCC': 'D',
    'VLX': '0',
    'VLD': '0',
    'VLI': '0',
    'MCO': 'F',
    'EXI': 'M',
    'EXD': 'M',
    'SDC': '0',
    'DLC': '0'
}

stats_base = {
    "substitute": "Suplente",
    "minutesPlayed": "Minutos jugados",
    "goals": "Goles",
    "goalAssist": "Asistencias",
    "bigChanceCreated": "Gran chance de gol creada",
    "bigChanceMissed": "Gran chance de gol fallada",
    "accuratePass": "Pases precisos",
    "totalPass": "Pases intentados",
    "accurateLongBalls": "Pases largos precisos",
    "totalLongBalls": "Pases largos intentados",
    "possessionLostCtrl": "Posesión controlada perdida",
    "touches": "Toques de balón",
    "aerialWon": "Duelos Aereos ganados",
    "aerialLost": "Duelos Aereos perdidos",
    "duelWon": "Duelos ganados",
    "duelLost": "Duelos perdidos",
    "penaltyWon": "Penal ganado",
    "penaltyMiss": "Penal fallado",    
}

stats_concentracion = {
    "fouls": "Faltas",
    "wasFouled": "Recibió falta",
    "totalOffside": "Fuera de juego",
    "dispossessed": "Desposesiones",
    "errorLeadToAShot": "Error que lleva a tiro",
    "penaltyConceded": "Penal concedido"
}

stats_delanteros = {
    "onTargetScoringAttempt": "Tiro al arco",
    "shotOffTarget": "Tiros fuera",
    "blockedScoringAttempt": "Tiro bloqueado",
    "hitWoodwork": "Tiro al poste",
}

stats_mediocentros = {
    "keyPass": "Pases clave",
    "accurateCross": "Centros precisos",
    "totalCross": "Centros totales",
    "wonContest": "Regates con éxito",
    "totalContest": "Regates totales",
}

stats_defensores = {
    "totalTackle": "Entradas totales",
    "totalClearance": "Despejes totales",
    "challengeLost": "Desafios perdidos",
    "interceptionWon": "Intercepciones ganadas",
    "outfielderBlock": "Bloqueos con el cuerpo",
}

stats_porteros = {
    "punches": "Salidas con puños",
    "goodHighClaim": "Centros atrapados",
    "accurateKeeperSweeper": "Salidas del área con éxito",
    "totalKeeperSweeper": "Salidas del área",
    "savedShotsFromInsideTheBox": "Salvadas dentro del área",
    "saves": "Salvadas"
}

# GRAPH FUNCTIONS

def obtener_grafico_match_momentum( df, es_local = True):
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

def mostrar_pos_media_equipo(jugadores_disponibles,nombre_jornada,df_posiciones_medias, df_posiciones_medias_oponentes, df_datos_oponentes):
    #Eliminar columna 'jerseyNumber' de df_datos_oponentes
    df_datos_oponentes = df_datos_oponentes.drop(columns='jerseyNumber')
    #Hacer join de df_posiciones_medias_oponentes con df_datos_oponentes por la columna 'shortName'
    df_posiciones_medias_oponentes = df_posiciones_medias_oponentes.merge(df_datos_oponentes, left_on='shortName', right_on='shortName', how='left')
    #Filtrar a los jugadores titulares
    df_posiciones_medias_oponentes = df_posiciones_medias_oponentes[df_posiciones_medias_oponentes['substitute'] == False]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch = VerticalPitch(pitch_type='opta', pitch_color='grass', line_color='white')
    pitch.draw(ax=ax)

    for jugador in jugadores_disponibles:
        fila_jugador = df_posiciones_medias[(df_posiciones_medias['name'] == jugador) & (df_posiciones_medias['Jornada'] == nombre_jornada) ]
        if not fila_jugador.empty:
            pitch.scatter(fila_jugador['averageX'], fila_jugador['averageY'], ax=ax, s=200, color='blue', edgecolors='black', linewidth=2.5, zorder=1)
            ax.text(fila_jugador['averageY'].values[0], fila_jugador['averageX'].values[0], fila_jugador['jerseyNumber'].values[0], color='white', ha='center', va='center', fontsize=12, zorder=2)
            ax.set_title(f"Posicion promedio del 11 titular de ambos equipos", fontsize=14)
            # Mostrar las posiciones medias de todos los oponentes
    for index, fila_oponente in df_posiciones_medias_oponentes.iterrows():
        pitch.scatter(100 - fila_oponente['averageX'], 100 - fila_oponente['averageY'], ax=ax, s=200, color='red', edgecolors='black', linewidth=2.5, zorder=1)
        ax.text(100 - fila_oponente['averageY'], 100 - fila_oponente['averageX'], fila_oponente['jerseyNumber'], color='white', ha='center', va='center', fontsize=12, zorder=2)
                
    plt.tight_layout()
    st.pyplot(fig)

def obtener_posiciones(df_jugador):
    # Hace join para obtener unicamente las columnas POS_1, POS_2 y POS_3 de df_maestro
    posiciones_jugador_seleccionado = df_jugador[['name','position','Pos_1', 'Pos_2', 'Pos_3']]
    posiciones_jugador_seleccionado['position'] = posiciones_jugador_seleccionado['position'].map(posiciones_map)
    # Haz un join con los diccionarios Pos_Prim_Map y Pos_Secu_Map
    posiciones_jugador_seleccionado['P1'] = posiciones_jugador_seleccionado['Pos_1'].map(Pos_Prim_Map)
    posiciones_jugador_seleccionado['P2'] = posiciones_jugador_seleccionado['Pos_2'].map(Pos_Prim_Map)
    posiciones_jugador_seleccionado['P3'] = posiciones_jugador_seleccionado['Pos_3'].map(Pos_Prim_Map)
    posiciones_jugador_seleccionado['S1'] = posiciones_jugador_seleccionado['Pos_1'].map(Pos_Secu_Map)
    posiciones_jugador_seleccionado['S2'] = posiciones_jugador_seleccionado['Pos_2'].map(Pos_Secu_Map)
    posiciones_jugador_seleccionado['S3'] = posiciones_jugador_seleccionado['Pos_3'].map(Pos_Secu_Map)

    for col in ['Pos_1', 'Pos_2', 'Pos_3']:
        posiciones_jugador_seleccionado[col] = posiciones_jugador_seleccionado[col].map(nombres_pos_map)

    # Extraer las columnas relevantes para el cálculo
    columnas_pos = posiciones_jugador_seleccionado[['Pos_1', 'Pos_2', 'Pos_3']]
    columnas_radares = posiciones_jugador_seleccionado[['P1', 'P2', 'P3', 'S1', 'S2', 'S3']]

    columnas_pos = columnas_pos.stack().reset_index(drop=True)
    columnas_radares = columnas_radares.stack().reset_index(drop=True)
    # eliminar duplicados y ceros
    columnas_radares = columnas_radares.drop_duplicates().replace('0', np.nan).dropna()

    columnas_radares = columnas_radares.tolist()
    columnas_pos = columnas_pos.tolist()

    return posiciones_jugador_seleccionado['name'].values[0],posiciones_jugador_seleccionado['position'].values[0], columnas_pos , columnas_radares 

def obtener_rendimiento(posiciones_jugador_seleccionado,df):
    # Obtenemos las posiciones en formato 'position' , Lista de variantes de posicion (max 3) , Lista de influencia (G,D,M,F)
    # Hacer join de posiciones_jugador_seleccionado con df por la columna 'name'
    posiciones_jugador_seleccionado = pd.DataFrame(posiciones_jugador_seleccionado).T
    posiciones_jugador_seleccionado.columns = ['name','position','Posiciones','Radares']

    # Agrupar df por 'name' y sumar las estadísticas
    df_totales = df.groupby('name').sum().reset_index()

    # Elimina columna 'position' y 'Jornada'
    df_totales = df_totales.drop(columns=['position', 'Jornada','country','rating','captain'])

    # Hacer join solo con los que coincidan
    df_rendimiento = posiciones_jugador_seleccionado.merge(df_totales ,left_on='name', right_on='name', how='left')
    
    return df_rendimiento

def obtener_stats_base(df_rendimiento):
    # Extrae las columnas de df_rendimiento que estan en la primera columna del diccionario stats_base
    df_stats_base = df_rendimiento[stats_base.keys()]
    # Pasar df_stats_base a formato largo
    df_stats_base = df_stats_base.melt(var_name='Estadística', value_name='Valor')
    # Traduce utilizando los valores del diccionario stats_base
    df_stats_base['Estadística'] = df_stats_base['Estadística'].map(stats_base)
    # Pasa los valores a enteros
    df_stats_base['Valor'] = df_stats_base['Valor'].astype(int)
    # Extrae la primera fila y guardala en una variable 'suplente'
    suplente = df_stats_base[df_stats_base['Estadística'] == 'Suplente']
    # Elimina la fila 'suplente' de df_stats_base
    df_stats_base = df_stats_base[df_stats_base['Estadística'] != 'Suplente']
    # Variable suplente en caso columna Valor sea 0 imprimir: 'Titular' en Streamlit
    suplente['Valor'] = suplente['Valor'].apply(lambda x: 'Titular' if x == 0 else 'Suplente')
    st.subheader(f"Inicia: {suplente['Valor'].values[0]}")
    # En caso los dos ultimos valores sean 0, eliminar ambas filas
    if df_stats_base['Valor'].iloc[-2] == 0 and df_stats_base['Valor'].iloc[-1] == 0:
        df_stats_base = df_stats_base.iloc[:-2]
    # Separa el df en dos a partir del quinto elemento
    df_stats_criticas = df_stats_base.iloc[:5]
    df_stats_base = df_stats_base.iloc[5:]

    # En caso los dos ultimos valores de df_stats_criticas sean 0, eliminar ambas filas
    if df_stats_criticas['Valor'].iloc[-2] == 0 and df_stats_criticas['Valor'].iloc[-1] == 0:
        df_stats_criticas = df_stats_criticas.iloc[:-2]
    
    # Imprimir en tarjetas de streamlit cada elemento de df_stats_criticas
    for index, row in df_stats_criticas.iterrows():
        st.write(f"<div style='text-align: center;'>{row['Estadística']}: {row['Valor']}</div>", unsafe_allow_html=True)
    
    df_ratios_base = pd.DataFrame(columns=['Ratio', 'Valor'])
    # Calcular los ratios y agregarlos como nuevas filas
    df_ratios_base.loc[0] = ['Ratio Pases precisos', df_stats_base.loc[6, 'Valor'] / df_stats_base.loc[7, 'Valor']]
    df_ratios_base.loc[1] = ['Ratio Pases largos precisos', df_stats_base.loc[8, 'Valor'] / df_stats_base.loc[9, 'Valor']]
    df_ratios_base.loc[2] = ['Ratio Toques por pérdida', df_stats_base.loc[11, 'Valor'] / df_stats_base.loc[10, 'Valor']]
    df_ratios_base.loc[3] = ['Ratio Duelos ganados', (df_stats_base.loc[12, 'Valor']
                                                        + df_stats_base.loc[14, 'Valor'] )  / 
                                                        (df_stats_base.loc[13, 'Valor'] 
                                                        + df_stats_base.loc[15, 'Valor'])]
    # Redondear los valores a dos decimales
    df_ratios_base['Valor'] = df_ratios_base['Valor'].round(2)
    # Eliminar ratios vacios
    df_ratios_base = df_ratios_base.dropna()
    return df_stats_base, df_ratios_base

def obtener_stats_concentracion(df_rendimiento):
    st.subheader(f"Concentración y mentalidad")
    # Extrae las columnas de df_rendimiento que estan en la primera columna del diccionario
    df_stats_c = df_rendimiento[stats_concentracion.keys()]
    df_stats_c = df_stats_c.melt(var_name='Estadística', value_name='Valor')
    df_stats_c['Estadística'] = df_stats_c['Estadística'].map(stats_concentracion)
    # Pasa los valores a enteros
    df_stats_c['Valor'] = df_stats_c['Valor'].astype(int)
    if df_stats_c['Valor'].iloc[-2] == 0 and df_stats_c['Valor'].iloc[-1] == 0:
        df_stats_c = df_stats_c.iloc[:-2]
    for index, row in df_stats_c.iterrows():
        st.write(f"<div style='text-align: center;'>{row['Estadística']}: {row['Valor']}</div>", unsafe_allow_html=True)
    return df_stats_c

def completar_datos(df_stats, df_jugador , lista_radares):
    # Agregar al dataframe df_stats, las estadisticas que se encuentran en la lista_radares
    # Agrega una columna a df_stats llamada 'Pos' que indique de qué diccionario se extrajo la stat
    df_stats['Pos'] = 'B'
    # Filtrar df_jugador segun la letra de la posicion de lista_radares
    for pos in lista_radares:
        if pos == 'G':
            # Filtra df_jugador con las columnas que esten en el diccionario stats_porteros
            df_filtrado = df_jugador[stats_porteros.keys()]
            # Pasa las columnas a formato largo
            df_filtrado = df_filtrado.melt(var_name='Estadística', value_name='Valor')
            # Traduce las columnas a los valores del diccionario stats_porteros
            df_filtrado['Estadística'] = df_filtrado['Estadística'].map(stats_porteros)
            # Pasa los valores a enteros
            df_filtrado['Valor'] = df_filtrado['Valor'].astype(int)
            # Agrega las filas a df_stats
            df_stats = pd.concat([df_stats, df_filtrado])
            # Ordena df_stats por indice
            df_stats = df_stats.sort_index()
            # Llenar columna 'Pos' con 'G'
            df_stats.loc[df_stats['Pos'].isnull(), 'Pos'] = 'G'
        elif pos == 'D':
            # Filtra df_jugador con las columnas que esten en el diccionario stats_porteros
            df_filtrado = df_jugador[stats_defensores.keys()]
            # Pasa las columnas a formato largo
            df_filtrado = df_filtrado.melt(var_name='Estadística', value_name='Valor')
            # Traduce las columnas a los valores del diccionario stats_porteros
            df_filtrado['Estadística'] = df_filtrado['Estadística'].map(stats_defensores)
            # Pasa los valores a enteros
            df_filtrado['Valor'] = df_filtrado['Valor'].astype(int)
            # Agrega las filas a df_stats
            df_stats = pd.concat([df_stats, df_filtrado])
            # Ordena df_stats por indice
            df_stats = df_stats.sort_index()
            # Llenar columna 'Pos' con 'D'
            df_stats.loc[df_stats['Pos'].isnull(), 'Pos'] = 'D'
        elif pos == 'M':
            # Filtra df_jugador con las columnas que esten en el diccionario stats_mediocentros
            df_filtrado = df_jugador[stats_mediocentros.keys()]
            # Pasa las columnas a formato largo
            df_filtrado = df_filtrado.melt(var_name='Estadística', value_name='Valor')
            # Traduce las columnas a los valores del diccionario stats_mediocentros
            df_filtrado['Estadística'] = df_filtrado['Estadística'].map(stats_mediocentros)
            # Pasa los valores a enteros
            df_filtrado['Valor'] = df_filtrado['Valor'].astype(int)
            # Agrega las filas a df_stats
            df_stats = pd.concat([df_stats, df_filtrado])
            # Ordena df_stats por indice
            df_stats = df_stats.sort_index()
            # Llenar columna 'Pos' con 'M'
            df_stats.loc[df_stats['Pos'].isnull(), 'Pos'] = 'M'
        elif pos == 'F':
           # Filtra df_jugador con las columnas que esten en el diccionario stats_delanteros
            df_filtrado = df_jugador[stats_delanteros.keys()]
            # Pasa las columnas a formato largo
            df_filtrado = df_filtrado.melt(var_name='Estadística', value_name='Valor')
            # Traduce las columnas a los valores del diccionario stats_delanteros
            df_filtrado['Estadística'] = df_filtrado['Estadística'].map(stats_delanteros)
            # Pasa los valores a enteros
            df_filtrado['Valor'] = df_filtrado['Valor'].astype(int)
            # Agrega las filas a df_stats
            df_stats = pd.concat([df_stats, df_filtrado])
            # Ordena df_stats por indice
            df_stats = df_stats.sort_index()
            # Llenar columna 'Pos' con 'F'
            df_stats.loc[df_stats['Pos'].isnull(), 'Pos'] = 'F'
            
    # Ordenar df_stats por 'Pos'
    df_stats = df_stats.sort_values(by='Pos')
    return df_stats

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

def cargar_datos_oponentes():
    df_oponentes = pd.DataFrame()
    for jornada, nombre_jornada in nombres_jornadas.items():
        try:
            df_temp = pd.read_csv(f'Archivos para el tablero final/{jornada}_stats_jugadores_op.csv')
            df_temp['Jornada'] = jornada
            df_oponentes = pd.concat([df_oponentes, df_temp])
        except FileNotFoundError as e:
            st.error(f"No se encontró el archivo para {nombre_jornada}: {e}")
    return df_oponentes

def cargar_datos_medias_oponentes():
    df_posiciones_medias_oponentes = pd.DataFrame()
    for jornada, nombre_jornada in nombres_jornadas.items():
        try:
            df_temp = pd.read_csv(f'Archivos para el tablero final/{jornada}_AL_posicionesprom_op.csv')
            df_temp['Jornada'] = jornada
            df_posiciones_medias_oponentes = pd.concat([df_posiciones_medias_oponentes, df_temp])
        except FileNotFoundError as e:
            st.error(f"No se encontró el archivo para {nombre_jornada}: {e}")
    return df_posiciones_medias_oponentes

def seleccionar_jornada(jornadas_disponibles):
    jornada_seleccionada = st.selectbox('Selecciona una jornada:', jornadas_disponibles, key='jornada_selector')
    if jornada_seleccionada in nombres_jornadas.values():
        jornada = [key for key, value in nombres_jornadas.items() if value == jornada_seleccionada][0]
        nombre_jornada = [value for key, value in nombres_jornadas.items() if value == jornada_seleccionada][0]
        return jornada, nombre_jornada
    return None, None

def seleccionar_jugador(df):
    nombres_jugadores_disponibles = df['name'].unique()
    nombres_jugadores_disponibles = nombres_jugadores_disponibles.tolist()
    nombres_jugadores_disponibles = sorted(nombres_jugadores_disponibles, key=lambda x: df[df['name'] == x]['minutesPlayed'].values[0],reverse=True)
    jugador_selector = st.selectbox('Selecciona un jugador:', nombres_jugadores_disponibles, key='jugador_selector')
    return jugador_selector




def main():
    configurar_pagina()
    #df = cargar_datos_jugadores() # Se cargan los datos de Resumen_AL_Jugadores.xlsx (MEJOR DESPUES AUNQUE MAS INEFICIENTE)
    df_maestro = cargar_general() # Se cargan los datos de ALIANZA LIMA 2024.xlsx
    df_posiciones_medias, df_heatmaps = cargar_datos_mapas(df_maestro) # Se cargan los datos de las posiciones medias y mapa de calor
    titulo, alianza = st.columns([2,1])
    with titulo:
        st.title('Alianza Lima Temporada 2024')
    with alianza:
        st.image(f'Imagenes\AL.png', width=80)
    
    df = cargar_datos_jugadores() # Se cargan los datos de Resumen_AL_Jugadores.xlsx
    df_posiciones_medias_oponentes = cargar_datos_medias_oponentes() # Se cargan los datos de las posiciones medias de los oponentes
    df_datos_oponentes = cargar_datos_oponentes() #Se cargan los datos de los oponentes de cada jornada 

    with st.container():
        st.write('-------------------')
        selectores, imagenes =  st.columns([4,1])
        with selectores:
            #Seleccion de jornada
            jornadas_disponibles = [value for key, value in nombres_jornadas.items()]
            jornada, nombre_jornada = seleccionar_jornada(jornadas_disponibles)
            if jornada and nombre_jornada:
                df = df[(df['Jornada'] == nombre_jornada) & (df['minutesPlayed'] > 0)]
                df_titulares = df[df['substitute'] == False]
                nombres_titulares = df_titulares['name'].unique()
                jugador_selector = seleccionar_jugador(df)
                ruta_imagen_jugador = f"Imagenes/Jugadores/{jugador_selector}.png"
                if jugador_selector:
                    pantalla_equipo , pantalla_heatmap, pantalla_otros = st.columns([4,5,2])
                    with pantalla_equipo:
                        st.header('Información del partido')
                        df_posiciones_medias_oponentes = df_posiciones_medias_oponentes[df_posiciones_medias_oponentes['Jornada'] == jornada]
                        df_datos_oponentes = df_datos_oponentes[df_datos_oponentes['Jornada'] == jornada]
                        mostrar_pos_media_equipo(nombres_titulares,jornada,df_posiciones_medias, df_posiciones_medias_oponentes,df_datos_oponentes)
                    with pantalla_heatmap:
                        st.header('Información del jugador')
                        st.subheader('Mapa de calor y posición promedio')
                        mostrar_heatmap_pos_media(jugador_selector,jornada,df_posiciones_medias,df_heatmaps)
                    with pantalla_otros:
                        st.header('Datos del jugador')
                        df_jugador = df[df['name'] == jugador_selector]
                        df_posicion = df_jugador.merge(df_maestro, left_on='name', right_on='Jugador', how='left')
                        posiciones_jugador_seleccionado = obtener_posiciones(df_posicion)
                        df_rendimiento = obtener_rendimiento(posiciones_jugador_seleccionado,df_jugador)
                        df_stats_base , df_ratios_base = obtener_stats_base(df_rendimiento)
                        df_concentracion = obtener_stats_concentracion(df_rendimiento)
                        # A df_concentracion se le tienen que agregar las Tarjetas Amarillas y Rojas (pendiente)
                        lista_posiciones = posiciones_jugador_seleccionado[2]
                        lista_radares = posiciones_jugador_seleccionado[3]
                        df_stats_posicion = completar_datos(df_stats_base, df_rendimiento , lista_radares)
                        st.subheader('Ratios del jugador')
                        st.table(df_ratios_base)
                        with pantalla_heatmap:
                            st.subheader('Estadísticas de posición')
                            st.write(f"{', '.join(lista_posiciones)}")
                            st.table(df_stats_posicion)

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
            with st.container():
                st.write('-------------------')
                st.header('Radares de rendimiento')
                st.table(lista_radares)
                


if __name__ == "__main__":
    main()