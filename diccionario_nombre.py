import pandas as pd
import os
from collections import Counter

def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

carpeta = "C:/Users/jose-/OneDrive - MSFT/web scraping/statsFutbol/new-stats/"
archivos = [f for f in os.listdir(carpeta) if f.endswith(".xlsx")]

mapa_equipos = {}

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    nombre_archivo = archivo.replace(".xlsx", "")

    try:
        df = pd.read_excel(ruta)
        df = normalizar_columnas(df)

        # Tomar primeras apariciones del equipo desde 'equipo_local' y 'visitante'
        posibles_nombres = list(df['equipo_local'].head(10).str.lower()) + list(df['visitante'].head(10).str.lower())

        # Contar ocurrencias
        nombre_comun = Counter(posibles_nombres).most_common(1)[0][0]

        # Guardar en el diccionario
        mapa_equipos[nombre_archivo] = nombre_comun.strip()

    except Exception as e:
        print(f"❌ Error en archivo {archivo}: {e}")

# Mostrar resultado
print("\n✅ Diccionario generado:\n")
for k, v in mapa_equipos.items():
    print(f'"{k}": "{v}",')
