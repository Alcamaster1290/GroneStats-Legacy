import streamlit as st
import pandas as pd


data = [
    ("Sofascore_13352931", "Alianza Lima vs Cusco FC", "Alianza Lima", "Cusco FC", 1),
    ("Sofascore_13352939", "Sport Huancayo vs AAS", "Sport Huancayo", "AAS", 1),
    ("Sofascore_13352933", "Melgar vs UTC", "Melgar", "UTC", 1),
    ("Sofascore_13352937", "Grau vs Ayacucho", "Grau", "Ayacucho", 1),
    ("Sofascore_13352938", "AUDH vs Cristal", "AUDH", "Cristal", 1),
    ("Sofascore_13352936", "Sport Boys vs JPII", "Sport Boys", "JPII", 1),
    ("Sofascore_13352932", "Comerciantes vs U", "Comerciantes", "U", 1),
    ("Sofascore_13352934", "Cienciano vs ADT", "Cienciano", "ADT", 1),
    ("Sofascore_13352935", "Chankas vs Garcilaso", "Chankas", "Garcilaso", 1),
    ("Sofascore_13387751", "AAS vs Alianza Lima", "AAS", "Alianza Lima", 2),
    ("Sofascore_13387758", "Cusco FC vs Melgar", "Cusco FC", "Melgar", 2),
    ("Sofascore_13387752", "UTC vs Binacional", "UTC", "Binacional", 2),
    ("Sofascore_13387755", "ADT vs Grau", "ADT", "Grau", 2),
    ("Sofascore_13387756", "U vs Cienciano", "U", "Cienciano", 2),
    ("Sofascore_13387757", "Cristal vs Sport Boys", "Cristal", "Sport Boys", 2),
    ("Sofascore_13387753", "JPII vs Huancayo", "JPII", "Huancayo", 2),
    ("Sofascore_13387754", "Garcilaso vs Comerciantes", "Garcilaso", "Comerciantes", 2),
    ("Sofascore_13387759", "Ayacucho vs AUDH", "Ayacucho", "AUDH", 2),
    ("Sofascore_13387774", "Alianza Lima vs JPII", "Alianza Lima", "JPII", 3),
    ("Sofascore_13387770", "Sport Boys vs Ayacucho", "Sport Boys", "Ayacucho", 3),
    ("Sofascore_13387767", "Cienciano vs Garcilaso", "Cienciano", "Garcilaso", 3),
    ("Sofascore_13387766", "Sport Huancayo vs Cristal", "Sport Huancayo", "Cristal", 3),
    ("Sofascore_13387772", "Binacional vs Cusco FC", "Binacional", "Cusco FC", 3),
    ("Sofascore_13387773", "AUDH vs ADT", "AUDH", "ADT", 3),
    ("Sofascore_13387769", "Melgar vs AAS", "Melgar", "AAS", 3),
    ("Sofascore_13387771", "Comerciantes vs Chankas", "Comerciantes", "Chankas", 3),
    ("Sofascore_13523624", "Ayacucho vs Sp. Huancayo", "Ayacucho", "Sport Huancayo", 4),
    ("Sofascore_13523626", "Cristal vs Alianza Lima", "Cristal", "Alianza Lima", 4),
    ("Sofascore_13523644", "AAS vs Binacional", "AAS", "Binacional", 4),
    ("Sofascore_13523647", "Cusco FC vs UTC", "Cusco FC", "UTC", 4),
    ("Sofascore_13523648", "Garcilaso vs Grau", "Garcilaso", "Grau", 4),
    ("Sofascore_13523646", "ADT vs Sport Boys", "ADT", "Sport Boys", 4),
    ("Sofascore_13523625", "U vs AUDH", "U", "AUDH", 4),
    ("Sofascore_13565846", "AUDH vs Garcilaso", "AUDH", "Garcilaso", 5),
    ("Sofascore_13565847", "Alianza Lima vs Ayacucho", "Alianza Lima", "Ayacucho", 5),
    ("Sofascore_13565842", "UTC vs AAS", "UTC", "AAS", 5),
    ("Sofascore_13565844", "Sport Huancayo vs ADT", "Sport Huancayo", "ADT", 5),
    ("Sofascore_13565845", "Melgar vs Cristal", "Melgar", "Cristal", 5),
    ("Sofascore_13565843", "Sport Boys vs U", "Sport Boys", "U", 5),
    ("Sofascore_13565841", "Cienciano vs Comerciantes", "Cienciano", "Comerciantes", 5),
    ("Sofascore_13565883", "Grau vs Los Chankas", "Grau", "Los Chankas", 5),
    ("Sofascore_13565884", "Binacional vs JPII", "Binacional", "JPII", 5),
]

df = pd.DataFrame(data, columns=["ID_Sofascore", "Nombre Partido", "home", "away", "# Jornada"])

# Eliminar el prefijo "Sofascore_" del ID
df["ID_Sofascore"] = df["ID_Sofascore"].str.replace("Sofascore_", "", regex=False)


st.title("Lista de Partidos")
st.dataframe(df)
