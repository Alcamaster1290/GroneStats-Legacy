import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_graphs_liga1 import graficar_pos_tiros_a_puerta


# Configuración de la página
st.set_page_config(layout="wide")

def apply_color_based_on_shot_type(shot_type):
    color_map = {
        'block': 'coral',
        'miss': 'darkred',
        'goal': 'darkgreen',
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

def procesar_tiros(df_shotmap, condicion):
    if df_shotmap is None:
        return None
        
    # Aplicar colores basados en el tipo de tiro
    df_shotmap['color'] = df_shotmap['shotType'].apply(apply_color_based_on_shot_type)

    # Categorías de tiros
    shots_on_target = ['save', 'goal']
    shots_off_target = ['miss', 'post', 'block']

    # Filtrar
    df_shots_on_target = df_shotmap[df_shotmap['shotType'].isin(shots_on_target)]
    df_shots_off_target = df_shotmap[df_shotmap['shotType'].isin(shots_off_target)]

    # Condición booleana
    es_local = condicion == "VERDADERO"

    return {
        "tiros_al_arco_local": df_shots_on_target[df_shots_on_target['isHome'] == es_local],
        "tiros_al_arco_away": df_shots_on_target[df_shots_on_target['isHome'] != es_local],
        "tiros_fuera_local": df_shots_off_target[df_shots_off_target['isHome'] == es_local],
        "tiros_fuera_away": df_shots_off_target[df_shots_off_target['isHome'] != es_local],
        "goles": df_shotmap[df_shotmap['shotType'] == 'goal']
    }

def graficar_tiros_al_arco(df_shots_on_target, condicion, titulo):
    if df_shots_on_target.empty:
        st.warning(f"No hay tiros al arco para mostrar ({condicion})")
        return
        
    try:
        # Procesar coordenadas del DataFrame
        df_goalzone = pd.DataFrame(
            [eval(coord) for coord in df_shots_on_target['goalMouthCoordinates']],
            columns=['y', 'z']
        )
        
        # Añadir columnas relevantes
        for col in ['shotType', 'situation', 'bodyPart', 'goalMouthLocation', 
                    'time', 'name', 'position', 'color', 'goalType']:
            if col in df_shots_on_target.columns:
                df_goalzone[col] = df_shots_on_target[col].values

        # Crear scatter plot
        fig = px.scatter(
            df_goalzone,
            x='y', 
            y='z', 
            color='color',
            color_discrete_map={
                'darkgreen': 'darkgreen', 
                'darkgoldenrod': 'darkgoldenrod', 
                'coral': 'coral', 
                'darkred': 'darkred'
            },
            hover_data={
                'name': True, 
                'shotType': True, 
                'time': True, 
                'situation': True, 
                'bodyPart': True,
                'y': False,
                'z': False,
                'color': False
            },
            size_max=20,
            title=titulo,
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
    st.title("Análisis de Tiros a Puerta")
    
    # Widget fuera de la función cacheada
    uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])
    
    # Cargar y procesar datos
    df_shotmap = procesar_datos(uploaded_file)
    
    if df_shotmap is not None:
        # Procesar tiros para ambos equipos
        tiros_local = procesar_tiros(df_shotmap, "Local")
        tiros_visitante = procesar_tiros(df_shotmap, "Visitante")
        
        # Mostrar resumen de tiros
        col1, col2 = st.columns(2)
        
        with col1:
            if tiros_local:
                st.subheader("Local")
                st.write(f"Tiros al arco: {len(tiros_local['tiros_al_arco_local'])}")
                st.write(f"Tiros fuera: {len(tiros_local['tiros_fuera_local'])}")
                st.write(f"Goles: {len(tiros_local['goles'][tiros_local['goles']['isHome'] == True])}")
                
        with col2:
            if tiros_visitante:
                st.subheader("Visitante")
                st.write(f"Tiros al arco: {len(tiros_visitante['tiros_al_arco_away'])}")
                st.write(f"Tiros fuera: {len(tiros_visitante['tiros_fuera_away'])}")
                st.write(f"Goles: {len(tiros_visitante['goles'][tiros_visitante['goles']['isHome'] == False])}")
        
        # Mostrar gráficos de tiros al arco
        st.subheader("Mapa de Tiros al Arco")
        
        if tiros_local and not tiros_local['tiros_al_arco_local'].empty:
            graficar_tiros_al_arco(
                tiros_local['tiros_al_arco_local'], 
                "Local", 
                "Tiros al arco - Local"
            )
        
        if tiros_visitante and not tiros_visitante['tiros_al_arco_away'].empty:
            graficar_tiros_al_arco(
                tiros_visitante['tiros_al_arco_away'], 
                "Visitante", 
                "Tiros al arco - Visitante"
            )
    

if __name__ == "__main__":
    main()