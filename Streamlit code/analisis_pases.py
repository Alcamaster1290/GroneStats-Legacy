import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

import pandas as pd
import plotly.express as px
import streamlit as st

# Carga de datos
df_total = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/Aplicacion Final/2024/Datos_totales_2024.xlsx', sheet_name='total')
df_per90 = pd.read_excel('C:/Users/Alvaro/Proyectos/Proyecto Gronestats/GroneStats/Aplicacion Final/2024/Datos_totales_2024.xlsx', sheet_name='per90')

df_total = df_total[(df_total['Posicion'] == 'D') | (df_total['Posicion'] == 'M') | (df_total['Posicion'] == 'F')]
df_total = df_total[(df_total['accurateCrossesPercentage'] < 90) & (df_total['accurateCrosses'] >= 3)]

# Configurar Streamlit
st.title('Dispersión de Centros precisos - Liga 1 2024')

# Crear el slicer para filtrar por minutos jugados
min_minutes = df_total['minutesPlayed'].min()
max_minutes = df_total['minutesPlayed'].max()
selected_minutes = st.slider('Selecciona el rango de minutos jugados:', min_value=int(min_minutes), max_value=int(max_minutes), value=(45, int(max_minutes)))

# Filtrar el DataFrame según el rango seleccionado
filtered_df = df_total[(df_total['minutesPlayed'] >= selected_minutes[0]) & (df_total['minutesPlayed'] <= selected_minutes[1])]

# Crear el gráfico de dispersión
fig = px.scatter(filtered_df, y='accurateCrossesPercentage', x='accurateCrosses', color='team',
                 size='touches', hover_data=['player', 'team', 'jerseyNumber', 'country', 'accurateCrossesPercentage', 'accurateCrosses'],
                 title='Dispersión de Centros precisos - Liga 1 2024',
                 labels={'accurateCrossesPercentage': '% de Centros precisos', 'accurateCrosses': 'Centros precisos'},
                 color_discrete_map={'Alianza Lima': 'blue', 'Other': 'red'})

# Personalizar los ejes y el diseño
fig.update_layout(xaxis_title='Centros precisos', yaxis_title='% de Centros precisos',
                  legend_title_text='Equipo')

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)
