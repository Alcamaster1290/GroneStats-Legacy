"""
Script de Streamlit para visualizar distribuciones de estadísticas ofensivas de jugadores
con actualización dinámica de colores según el filtro de minutos jugados
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy.stats import gaussian_kde
from matplotlib.colors import LinearSegmentedColormap

# Configuración de página DEBE SER LA PRIMERA LÍNEA DE STREAMLIT
st.set_page_config(
    page_title="Análisis de Distribución - Estadísticas de Fútbol", 
    layout="wide",
    page_icon="⚽"
)

# Diccionario de traducción de variables
TRADUCCIONES = {
    'goals': 'Goles',
    'assists': 'Asistencias',
    'keyPasses': 'Pases clave',
    'totalShots': 'Tiros totales',
    'shotsOnTarget': 'Tiros al arco',
    'goalConversionPercentage': 'Porcentaje de conversión',
    'successfulDribbles': 'Regates exitosos',
    'accurateCrosses': 'Centros precisos',
    'accurateFinalThirdPasses': 'Pases precisos último tercio',
    'wasFouled': 'Faltas recibidas',
    'minutesPlayed': 'Minutos jugados',
    'dispossessed': 'Pérdidas de balón',
    'offsides': 'Offsides'
}

# Configuración inicial de la aplicación
def configurar_app():
    """Configura los elementos iniciales de la aplicación"""
    st.title("📊 Distribución de Estadísticas Ofensivas")
    st.write("Liga 1 - Temporada 2025 | Se destaca a Gaspar Gentile en rojo")

# Carga y procesamiento de datos
@st.cache_data
def cargar_datos():
    """
    Carga y procesa los datos del archivo CSV
    Returns:
        DataFrame: Datos de jugadores procesados
    """
    try:
        df = pd.read_csv("Datos al J17.csv", sep=';')
        columnas_numericas = [
            'goals', 'assists', 'keyPasses',
            'totalShots', 'shotsOnTarget', 'goalConversionPercentage', 
            'successfulDribbles', 'accurateCrosses', 'accurateFinalThirdPasses', 
            'wasFouled', 'minutesPlayed', 'dispossessed', 'offsides'
        ]
        df[columnas_numericas] = df[columnas_numericas].apply(pd.to_numeric, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

# Funciones de análisis estadístico
def crear_tabla_percentiles(datos, columna):
    """
    Crea una tabla de percentiles para una columna específica
    
    Args:
        datos (DataFrame): Datos completos
        columna (str): Columna a analizar
    
    Returns:
        DataFrame: Tabla con percentiles 0-100
    """
    percentiles = np.linspace(0, 100, 101)
    valores = np.percentile(datos[columna].dropna(), percentiles)
    return pd.DataFrame({'Percentil': percentiles, 'Valor': valores})

def calcular_percentil(valor, tabla_percentiles):
    """
    Calcula el percentil correspondiente a un valor
    
    Args:
        valor (float): Valor a evaluar
        tabla_percentiles (DataFrame): Tabla de referencia
    
    Returns:
        float: Percentil correspondiente
    """
    if pd.isna(valor):
        return np.nan
    return np.interp(valor, tabla_percentiles['Valor'], tabla_percentiles['Percentil'])

def es_variable_entera(variable):
    """Determina si una variable debe mostrarse como entero"""
    return variable in ['goals', 'assists', 'keyPasses', 'totalShots', 'shotsOnTarget', 
                       'offsides', 'wasFouled', 'dispossessed', 'minutesPlayed']

def crear_grafico_distribucion(datos, variable, min_minutos, per90=False):
    """
    Crea el gráfico de distribución con colores por percentiles dinámicos
    
    Args:
        datos (DataFrame): Datos filtrados
        variable (str): Variable a graficar
        min_minutos (int): Mínimo de minutos jugados para el filtro
        per90 (bool): Si es True, muestra los datos en formato per90
    
    Returns:
        tuple: (figura matplotlib, tabla de percentiles, datos de densidad, cantidad de jugadores)
    """
    data_var = datos[variable].dropna()
    cantidad_jugadores = len(data_var)
    
    # Convertir a per90 si es necesario
    if per90:
        data_var = data_var / (datos['minutesPlayed'] / 90)
        titulo_extra = " (por 90 minutos)"
    else:
        titulo_extra = ""
    
    # Crear tabla de percentiles con los datos filtrados (actualizados dinámicamente)
    tabla_percentiles = crear_tabla_percentiles(datos, variable)
    
    # Estimación de densidad
    kde_func = gaussian_kde(data_var)
    x_data = np.linspace(max(0, data_var.min()), data_var.max(), 500)
    y_data = kde_func(x_data)
    
    # Filtrar jugadores 'mejores' con ID_Jugador y posición EXD o EXI
    jugadores_top = datos[
        datos['ID_Jugador'].notna() &
        (
            (datos['Posicion'] == 'EXD') | (datos['Posicion'] == 'EXI') |
            (datos['Posicion S_1'] == 'EXD') | (datos['Posicion S_1'] == 'EXI') |
            (datos['Posicion S_2'] == 'EXD') | (datos['Posicion S_2'] == 'EXI')
        )
    ].copy()

    # Calcular valor de la variable (per90 o no)
    if per90:
        jugadores_top[variable] = jugadores_top[variable] / (jugadores_top['minutesPlayed'] / 90)


    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Crear colores por percentiles (azul, amarillo, verde)
    cmap = LinearSegmentedColormap.from_list('percentil', ['#1f77b4', '#ff7f0e', '#2ca02c'])
    
    # Calcular percentiles para cada punto x usando la tabla dinámica actualizada
    percentiles_x = [calcular_percentil(x, tabla_percentiles) for x in x_data]
    
    # Normalizar percentiles para el colormap (0-100 a 0-1)
    norm = plt.Normalize(0, 100)
    
    # Dibujar el área con colores por percentil (actualizados)
    for i in range(len(x_data)-1):
        ax.fill_between([x_data[i], x_data[i+1]], 
                        [y_data[i], y_data[i+1]], 
                        color=cmap(norm(percentiles_x[i])),
                        alpha=0.6)
    
    # Línea gris para el borde superior
    ax.plot(x_data, y_data, color='gray', linewidth=1, alpha=0.8)
    
    # Configurar eje Y como porcentaje
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=1))
    ax.set_ylim(bottom=0)
    
    # Graficar puntos de jugadores destacados en EXD o EXI con ID Sofascore
    for _, row in jugadores_top.iterrows():
        val = row[variable]
        if pd.notna(val):
            y_val = np.interp(val, x_data, y_data)
            ax.plot(val, y_val, 'o', color='black', alpha=0.25, markersize=6)

    # Resaltar jugador específico con percentiles actualizados
    jugador_destacado = datos[datos['player'].str.lower() == "gaspar gentile"]
    if not jugador_destacado.empty:
        valor_jugador = jugador_destacado.iloc[0][variable]
        if per90:
            valor_jugador = valor_jugador / (jugador_destacado.iloc[0]['minutesPlayed'] / 90)
        
        # Calcular percentil usando la tabla actualizada
        percentil = calcular_percentil(valor_jugador, tabla_percentiles)
        
        # Formatear valor según tipo de variable
        valor_formateado = f"{valor_jugador:.1f}"  # Siempre con 1 decimal para per90
        
        # Añadir elementos al gráfico
        y_pos = np.interp(valor_jugador, x_data, y_data)
        ax.axvline(valor_jugador, color='red', linestyle='--', alpha=0.7)
        ax.annotate(
            f"Gaspar Gentile: {valor_formateado} (Percentil {percentil:.0f}%)",
            xy=(valor_jugador, y_pos),
            xytext=(valor_jugador + 0.1*np.ptp(ax.get_xlim()), y_pos),
            color='red', ha='left', fontsize=10,
            arrowprops=dict(arrowstyle='->', color='red')
        )
    
    # Configuración estética con traducción
    ax.set_xlim(left=max(0, data_var.min() * 0.9))
    ax.set_xlabel(f"{TRADUCCIONES.get(variable, variable)}{titulo_extra}", fontsize=12)
    ax.set_ylabel("Densidad (%)", fontsize=12)
    ax.set_title(f"Distribución de {TRADUCCIONES.get(variable, variable)}{titulo_extra} con percentiles", 
                fontsize=14, pad=20)
    ax.grid(True, alpha=0.2)
    
    # Añadir barra de color para los percentiles (actualizada)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label('Percentil', rotation=270, labelpad=15)
    
    # Datos de densidad para tabla
    densidad_data = pd.DataFrame({'Valor': x_data, 'Densidad': y_data, 'Percentil': percentiles_x})
    
    return fig, tabla_percentiles, densidad_data, cantidad_jugadores

def mostrar_tablas(datos, variable, tabla_percentiles, densidad_data, per90=False, tab_id=""):
    """Muestra las tablas de datos en la interfaz con keys únicos"""
    # Tabla de percentiles (actualizada dinámicamente)
    st.subheader("📈 Tabla de Distribución (Percentiles)")
    st.write(f"Valores de referencia para {TRADUCCIONES.get(variable, variable)} (basados en el filtro actual):")
    st.dataframe(tabla_percentiles.style.format({
        'Percentil': '{:.0f}%', 
        'Valor': '{:.2f}'
    }))
    
    # Tabla de densidades con key único
    if st.checkbox("📊 Mostrar tabla de densidades del gráfico", key=f"densidades_{tab_id}"):
        st.subheader("Datos de Densidad")
        st.write("Valores exactos de la curva de distribución:")
        st.dataframe(densidad_data.style.format({
            'Valor': '{:.2f}', 
            'Densidad': '{:.4f}',
            'Percentil': '{:.1f}%'
        }))
    
    # Tabla de jugadores con key único (percentiles actualizados)
    if st.checkbox("👥 Mostrar tabla completa de jugadores", key=f"jugadores_{tab_id}"):
        df_jugadores = datos[['player', 'minutesPlayed', variable]].copy()
        
        if per90:
            df_jugadores[variable] = df_jugadores[variable] / (df_jugadores['minutesPlayed'] / 90)
        
        # Calcular percentiles usando la tabla actualizada
        df_jugadores['Percentil'] = df_jugadores[variable].apply(
            lambda x: calcular_percentil(x, tabla_percentiles))
        
        formato = {
            'Percentil': '{:.0f}%', 
            'minutesPlayed': '{:.0f}',
            variable: '{:.1f}'  # Siempre con 1 decimal para per90
        }
        
        st.dataframe(
            df_jugadores.sort_values(by=variable, ascending=False)
            .style.format(formato)
        )

# Flujo principal de la aplicación
def main():
    # Configurar elementos de la app
    configurar_app()
    
    # Cargar datos
    df = cargar_datos()
    if df is None:
        return
    
    # Crear pestañas
    tab1, tab2 = st.tabs(["Distribución Normal", "Distribución per90"])
    
    # Selector de variable con traducciones
    variables_disponibles = [
        'goals', 'assists', 'keyPasses',
        'totalShots', 'shotsOnTarget', 'goalConversionPercentage',
        'successfulDribbles', 'accurateCrosses', 'accurateFinalThirdPasses',
        'wasFouled', 'dispossessed', 'offsides'
    ]
    
    variable_seleccionada = st.sidebar.selectbox(
        "Selecciona la estadística para analizar:", 
        options=variables_disponibles,
        format_func=lambda x: TRADUCCIONES.get(x, x),
        index=0
    )
    
    # Filtro por minutos jugados
    min_minutos, max_minutos = int(df["minutesPlayed"].min()), int(df["minutesPlayed"].max())
    rango_minutos = st.sidebar.slider(
        "Filtrar por minutos jugados:", 
        min_minutos, max_minutos, 
        (min_minutos, max_minutos),
        help="Selecciona el rango de minutos jugados para filtrar los jugadores"
    )
    
    # Aplicar filtros
    df_filtrado = df[
        (df["minutesPlayed"] >= rango_minutos[0]) & 
        (df["minutesPlayed"] <= rango_minutos[1])
    ]
    
    # Validación de datos
    if df_filtrado[variable_seleccionada].dropna().empty:
        st.warning(f"No hay datos suficientes para analizar '{TRADUCCIONES.get(variable_seleccionada, variable_seleccionada)}' con los filtros actuales.")
        return
    
    with tab1:
        # Gráfico normal con percentiles dinámicos (se actualiza con el filtro)
        fig_normal, tabla_percentiles_normal, densidad_data_normal, cantidad_jugadores = crear_grafico_distribucion(
            df_filtrado, variable_seleccionada, rango_minutos[0])
        
        st.pyplot(fig_normal)
        st.caption(f"Gráfico generado en base a {cantidad_jugadores} jugadores de Liga 1 Perú con al menos {rango_minutos[0]} minutos jugados")
        mostrar_tablas(df_filtrado, variable_seleccionada, tabla_percentiles_normal, densidad_data_normal, tab_id="normal")
    
    with tab2:
        # Gráfico per90 con percentiles dinámicos (se actualiza con el filtro)
        fig_per90, tabla_percentiles_per90, densidad_data_per90, cantidad_jugadores = crear_grafico_distribucion(
            df_filtrado, variable_seleccionada, rango_minutos[0], per90=True)
        
        st.pyplot(fig_per90)
        st.caption(f"Gráfico per90 generado en base a {cantidad_jugadores} jugadores de Liga 1 Perú con al menos {rango_minutos[0]} minutos jugados")
        mostrar_tablas(df_filtrado, variable_seleccionada, tabla_percentiles_per90, densidad_data_per90, per90=True, tab_id="per90")

if __name__ == "__main__":
    main()