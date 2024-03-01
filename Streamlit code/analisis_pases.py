import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
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

    promedio_pases_acertados = df['Pases Acertados'].mean()
    promedio_balones_largos_acertados = df['Balones Largos Acertados'].mean()
    promedio_centros_acertados = df['Centros Acertados'].mean()
    color_fondo = 'black'
    color_linea_promedio = 'white'
    # Definir el ancho de las barras
    bar_width = 0.3  # Añade esta línea para definir el ancho de las barras

    estadisticas_y_promedios = [
        ('Pases Acertados', promedio_pases_acertados, 'Total de Pases'),
        ('Balones Largos Acertados', promedio_balones_largos_acertados, 'Total de Balones Largos'),
        ('Centros Acertados', promedio_centros_acertados, 'Total de Centros')
    ]

    # Creación de gráficos
    fig, axs = plt.subplots(3, 1, figsize=(10, 18), facecolor=color_fondo)
    for i, (estadistica, promedio, total_estadistica) in enumerate(estadisticas_y_promedios):
        ax = axs[i]
        r1 = np.arange(len(df_jugador['Jornada']))
        r2 = [x + bar_width for x in r1]

        ax.bar(r1, df_jugador[estadistica], color='lightblue', width=bar_width, edgecolor='steelblue', label=estadistica)
        ax.bar(r2, df_jugador[total_estadistica], color='navy', width=bar_width, edgecolor='lightblue', label=total_estadistica)
        # Para dibujar la línea de promedio correctamente
        ax.axhline(y=promedio, color=color_linea_promedio, linestyle='--', label=f'Promedio del equipo: {promedio:.2f}')

        ax.set_facecolor(color_fondo)
        ax.set_title(f'{estadistica} por Jornada para {jugador_seleccionado}')
        ax.set_xlabel('Jornada')
        ax.set_xticks([r + bar_width / 2 for r in range(len(r1))])
        ax.set_xticklabels(df_jugador['Jornada'])
        ax.set_ylabel(estadistica)
        ax.tick_params(colors='white')
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.legend(facecolor=color_fondo, edgecolor=color_fondo)
        for text in ax.legend().get_texts():
            text.set_color('black')

    plt.tight_layout()
    st.pyplot(fig)

# Llamar a la función para generar y mostrar los informes basados en la selección
generar_informe(jugador_selector)
