import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
import matplotlib.patheffects as path_effects
from mplsoccer import VerticalPitch
import plotly.express as px


# Diccionario de traducción de términos en inglés a español
translation_dict = {
    'save': 'Atajada',
    'goal': 'Gol',
    'miss': 'Fuera',
    'post': 'Palo',
    'block': 'Bloqueo',
    'penalty': 'Penal',
    'own': 'Autogol',
    'right-foot': 'Pie derecho',
    'left-foot': 'Pie izquierdo',
    'head':'Cabeza',
    'corner':'T.Esquina',
    'regular': 'Regular',
    'assisted': 'Asistido',
    'fast-break': 'Contraataque',
    'throw-in-set-piece': 'Jugada tras saque de banda',
    'free-kick' : 'Tiro libre',
    'set-piece' : 'Jugada a balon parado',
    'other' : 'Otro',
}

def translate_term(term):
    return translation_dict.get(term, term)


def graficar_tiros_en_campo(df_tiros):
    """
    Grafica todos los tiros en una mitad de la cancha tipo Opta.
    
    Parámetros:
        df_tiros (pd.DataFrame): DataFrame con todos los tiros del partido.
    """
    # Crear el campo de juego con color azul oscuro
    pitch = VerticalPitch(
        pitch_type='opta',
        pitch_color='#112548',  # Color de la cancha en formato hexadecimal (azul oscuro)
        goal_type='box',
        linewidth=2,
        line_color='white',
        pitch_length=105,
        pitch_width=68,
        half=True,
        corner_arcs=True,
    )

    # Configuración de la figura
    fig, axs = pitch.grid(
        figheight=10, title_height=0, endnote_space=0,
        title_space=0, axis=False, grid_height=0.82,
        endnote_height=0.01, grid_width=0.8,
    )

    # Cambiar el fondo de la figura y el área del gráfico a negro
    fig.patch.set_facecolor('black')  # Fondo de la figura
    axs['pitch'].set_facecolor('black')  # Fondo del área del gráfico

    # Aplicar traducciones a las columnas relevantes
    df_tiros['shotType'] = df_tiros['shotType'].apply(translate_term)
    df_tiros['situation'] = df_tiros['situation'].apply(translate_term)
    df_tiros['bodyPart'] = df_tiros['bodyPart'].apply(translate_term)
    df_tiros['goalType'] = df_tiros['goalType'].apply(translate_term)

    # Ajustar el tamaño de los puntos según el tipo de tiro
    df_tiros['size'] = df_tiros['shotType'].apply(lambda x: 300 if x == 'Gol' else 200)

    # Dibujar hexbin y scatter
    hexmap = pitch.hexbin(
        x=100-df_tiros['x'],
        y=df_tiros['y'],
        ax=axs['pitch'],
        edgecolors='none',
        gridsize=(15, 8),
        cmap='PuBu',
        alpha=0.4
    )
    
    scatter = pitch.scatter(
        x=100-df_tiros['x'],
        y=df_tiros['y'],
        ax=axs['pitch'],
        color=df_tiros['color'],
        s=df_tiros['size'],  # Usar el tamaño definido en la columna 'size'
        edgecolors='black',
        zorder=2,
        alpha=.9
    )

    # Título del gráfico
    fig.suptitle(
        'Mapa de tiros del jugador Gaspar Gentile',
        fontsize=18,
        color='yellow',
        y=0.95,
        fontweight='bold',
        path_effects=[
            path_effects.withStroke(linewidth=3, foreground='black')
        ]
    )

    # ordenar df_tiros por tiempo
    df_tiros = df_tiros.sort_values(by='time')

    # Crear leyenda
    legend_patches = []
    for _, row in df_tiros.iterrows():
        color = row['color']
        jersey_number = int(row['jerseyNumber']) if not pd.isna(row['jerseyNumber']) else 'N/A'
        patch = mpatches.Patch(
            facecolor=color,
            edgecolor='black',
            label=f"{row['time']}' {row['Oponente']} - {row['bodyPart']} | {row['situation']} | {row['shotType']}"
        )
        legend_patches.append(patch)

    # Mostrar leyenda
    axs['pitch'].legend(
        handles=legend_patches,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),
        ncol=2,
        fontsize=8,
        facecolor='black',
        edgecolor='white',
        labelcolor='white'
    )

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    return fig

# Configuración de la página
st.set_page_config(layout="wide")

def apply_color_based_on_shot_type(shot_type, is_home):
    if shot_type == 'goal':
        return 'darkgreen' if is_home else 'lightgreen'
    color_map = {
        'block': 'coral',
        'miss': 'darkred',
        'save': 'darkgoldenrod',
        'post': 'darkgoldenrod'
    }
    return color_map.get(shot_type, 'gray')

@st.cache_data
def procesar_datos(uploaded_file):
    if uploaded_file is not None:
        try:
            # Leer el archivo Excel
            xls = pd.ExcelFile(uploaded_file)
            df_shotmap = pd.read_excel(xls, sheet_name='Shotmap')
            return df_shotmap
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return None
    return None

def procesar_tiros(df_shotmap):
    if df_shotmap is None:
        return None
        
    # Aplicar colores basados en el tipo de tiro y condición de local/visitante
    df_shotmap['color'] = df_shotmap.apply(lambda x: apply_color_based_on_shot_type(x['shotType'], x['isHome']), axis=1)

    # Categorías de tiros
    shots_on_target = ['save', 'goal']
    shots_off_target = ['miss', 'post', 'block']

    # Filtrar
    df_shots_on_target = df_shotmap[df_shotmap['shotType'].isin(shots_on_target)]
    df_shots_off_target = df_shotmap[df_shotmap['shotType'].isin(shots_off_target)]

    return {
        "tiros_al_arco": df_shots_on_target,
        "tiros_fuera": df_shots_off_target,
        "goles": df_shotmap[df_shotmap['shotType'] == 'goal']
    }

def graficar_tiros_en_arco(df_shots_on_target, df_shots_off_target):
    # Combinar todos los tiros
    df_all_shots = df_shots_on_target.copy()
    #df_all_shots = pd.concat([df_shots_on_target, df_shots_off_target])
    
    if df_all_shots.empty:
        st.warning("No hay tiros para mostrar")
        return
        
    try:
        # Procesar coordenadas del DataFrame
        df_goalzone = pd.DataFrame(
            [eval(coord) for coord in df_all_shots['goalMouthCoordinates']],
            columns=['y', 'z']
        )
        
        # Añadir columnas relevantes
        for col in ['shotType', 'situation', 'bodyPart', 'goalMouthLocation', 
                    'time', 'name', 'position', 'color', 'goalType', 'isHome', 'Oponente']:
            if col in df_all_shots.columns:
                df_goalzone[col] = df_all_shots[col].values

        # Crear texto para el hover
        df_goalzone['condicion'] = df_goalzone['isHome'].apply(lambda x: 'Local' if x else 'Visitante')
        df_goalzone['hover_text'] = df_goalzone.apply(
            lambda x: f"Jugador: {x['name']}<br>Tipo: {x['shotType']}<br>Minuto: {x['time']}<br>Situación: {x['situation']}<br>Pierna: {x['bodyPart']}<br>Condición: {x['condicion']}<br>Oponente: {x['Oponente']}",
            axis=1
        )

        # Crear scatter plot
        fig = px.scatter(
            df_goalzone,
            x='y', 
            y='z', 
            color='color',
            color_discrete_map={
                'darkgreen': 'darkgreen',  # Gol de local
                'lightgreen': 'lightgreen',  # Gol de visitante
                'darkgoldenrod': 'darkgoldenrod',  # Atajados
                'coral': 'coral',  # Bloqueados
                'darkred': 'darkred'  # Errados
            },
            hover_name='hover_text',
            size_max=20,
            title="Todos los Tiros",
            labels={'y': 'Ancho', 'z': 'Altura'}
        )

        # Personalizar los marcadores
        fig.update_traces(
            marker=dict(
                size=12,
                line=dict(width=2, color='black')
            ),
            selector=dict(mode='markers')
        )

        # Dimensiones del arco
        palo_exterior = 45.4
        palo_interior = 45.6
        travesaño_inferior = 0
        travesaño_superior = 35.5
        palo_opuesto_exterior = 54.6
        palo_opuesto_interior = 54.4

        # Líneas exteriores del arco
        fig.add_shape(
            type="line", 
            x0=palo_exterior, y0=travesaño_inferior, 
            x1=palo_exterior, y1=travesaño_superior, 
            line=dict(color="black", width=4)
        )
        fig.add_shape(
            type="line", 
            x0=palo_opuesto_exterior, y0=travesaño_inferior, 
            x1=palo_opuesto_exterior, y1=travesaño_superior, 
            line=dict(color="black", width=4)
        )
        fig.add_shape(
            type="line", 
            x0=palo_exterior, y0=travesaño_superior, 
            x1=palo_opuesto_exterior, y1=travesaño_superior, 
            line=dict(color="black", width=8)
        )

        # Líneas interiores del arco
        fig.add_shape(
            type="line", 
            x0=palo_interior, y0=travesaño_inferior, 
            x1=palo_interior, y1=travesaño_superior, 
            line=dict(color="black", width=4)
        )
        fig.add_shape(
            type="line", 
            x0=palo_opuesto_interior, y0=travesaño_inferior, 
            x1=palo_opuesto_interior, y1=travesaño_superior, 
            line=dict(color="black", width=4)
        )
        fig.add_shape(
            type="line", 
            x0=palo_interior, y0=travesaño_superior, 
            x1=palo_opuesto_interior, y1=travesaño_superior, 
            line=dict(color="black", width=4)
        )

        # Agregar el relleno blanco en los palos
        fig.add_shape(
            type="rect", 
            x0=palo_exterior, y0=travesaño_inferior, 
            x1=palo_interior, y1=travesaño_superior, 
            fillcolor="white", line=dict(width=0)
        )
        fig.add_shape(
            type="rect", 
            x0=palo_opuesto_interior, y0=travesaño_inferior, 
            x1=palo_opuesto_exterior, y1=travesaño_superior, 
            fillcolor="white", line=dict(width=0)
        )

        # Línea blanca en el travesaño para mejor visualización
        fig.add_shape(
            type="line", 
            x0=palo_exterior, y0=travesaño_superior, 
            x1=palo_opuesto_exterior, y1=travesaño_superior, 
            line=dict(color="white", width=10)
        )
        
        # Ajustar apariencia de los ejes
        fig.update_xaxes(
            autorange="reversed", 
            showgrid=False, 
            visible=False
        )
        fig.update_yaxes(
            showgrid=False, 
            visible=False
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        # Mostrar el gráfico
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al generar el gráfico: {e}")

def main():
    st.title("Análisis de Tiros a Puerta - Gaspar Gentile")
    
    # Widget fuera de la función cacheada
    uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])
    
    # Cargar y procesar datos
    df_shotmap = procesar_datos(uploaded_file)
    
    if df_shotmap is not None:
        # Procesar todos los tiros
        tiros = procesar_tiros(df_shotmap)
        
        # Mostrar resumen de tiros
        st.subheader("Resumen de Tiros")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Local**")
            st.write(f"Tiros al arco: {len(tiros['tiros_al_arco'][(tiros['tiros_al_arco']['isHome'] == True)])}")
            st.write(f"Tiros fuera: {len(tiros['tiros_fuera'][(tiros['tiros_fuera']['isHome'] == True)])}")
            st.write(f"Goles: {len(tiros['goles'][(tiros['goles']['isHome'] == True)])}")
                
        with col2:
            st.write("**Visitante**")
            st.write(f"Tiros al arco: {len(tiros['tiros_al_arco'][(tiros['tiros_al_arco']['isHome'] == False)])}")
            st.write(f"Tiros fuera: {len(tiros['tiros_fuera'][(tiros['tiros_fuera']['isHome'] == False)])}")
            st.write(f"Goles: {len(tiros['goles'][(tiros['goles']['isHome'] == False)])}")
        
        # Mostrar gráfico con todos los tiros
        st.subheader("Mapa de Tiros al arco")
        graficar_tiros_en_arco(tiros['tiros_al_arco'], tiros['tiros_fuera'])

        # Preparar los DataFrames esperados por la función original
        df_local = tiros['tiros_al_arco'][tiros['tiros_al_arco']['isHome'] == True].copy()
        df_visitante = tiros['tiros_al_arco'][tiros['tiros_al_arco']['isHome'] == False].copy()

        # Generar columnas 'x' y 'y' si no existen
        if 'x' not in df_local.columns or 'y' not in df_local.columns:
            df_local[['x', 'y']] = pd.DataFrame(df_local['shotCoordinates'].apply(eval).to_list(), index=df_local.index)
        if 'x' not in df_visitante.columns or 'y' not in df_visitante.columns:
            df_visitante[['x', 'y']] = pd.DataFrame(df_visitante['shotCoordinates'].apply(eval).to_list(), index=df_visitante.index)

        # Llamar a la función 
        graficar_tiros_en_campo(df_shotmap)


if __name__ == "__main__":
    main()