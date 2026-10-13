"""
contexto_liga.py

Módulo para ajustar probabilidades y lambdas según el contexto de liga.

- Calcula percentiles de cada equipo dentro de su liga.
- Clasifica perfiles ofensivos y defensivos.
- Ajusta mercados de una sola línea.
- Ajusta lambdas de remates y tiros a puerta.
- Genera una tabla de contexto y ajuste final.
"""
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


RUTA_STATS = "new-stats"
RUTA_EQUIPOS_LIGAS = "enlaces_equipos.xlsx"

def normalizar_columnas_basicas(df):
    """
    Normaliza nombres de columnas.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def obtener_division_equipo(equipo_archivo):
    """
    Devuelve la división de un equipo según enlaces_equipos.xlsx.

    Ejemplos:
    - manchester-united-fc -> england
    - birmingham-city-fc -> england_b
    """

    if not os.path.exists(RUTA_EQUIPOS_LIGAS):
        return None

    df = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    df = normalizar_columnas_basicas(df)

    if "equipo" not in df.columns or "division" not in df.columns:
        return None

    fila = df[df["equipo"] == equipo_archivo]

    if fila.empty:
        return None

    return str(fila["division"].iloc[0])


def st_cache_data(func):
    """
    Cache simple en memoria para no leer repetidamente el Excel.
    """
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]

        resultado = func(*args)
        cache[args] = resultado
        return resultado

    return wrapper


def cargar_equipos_division(division):
    """
    Devuelve los equipos de una división que están marcados
    para analizar.
    """

    if division is None:
        return []

    if not os.path.exists(RUTA_EQUIPOS_LIGAS):
        return []

    df = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    df = normalizar_columnas_basicas(df)

    columnas_requeridas = ["equipo", "division", "analizar"]

    for col in columnas_requeridas:
        if col not in df.columns:
            return []

    df_filtrado = df[
        (df["division"].str.lower() == division.lower())
        & (df["analizar"].astype(str).str.upper() == "SI")
    ]

    return df_filtrado["equipo"].tolist()


def cargar_resumen_division(division, n_partidos=10):
    """
    Carga los Excel de todos los equipos de una división
    y crea un resumen con una fila por equipo.

    Cada fila contiene el promedio de:
    - shots_favor
    - shots_contra
    - a_puerta_favor
    - a_puerta_contra
    """

    equipos = cargar_equipos_division(division)

    resumenes = []

    for equipo in equipos:

        ruta = os.path.join(RUTA_STATS, f"{equipo}.xlsx")

        if not os.path.exists(ruta):
            continue

        try:
            df = pd.read_excel(ruta)
        except Exception:
            continue

        df = normalizar_columnas_basicas(df)

        columnas = [
            "shots_favor",
            "shots_contra",
            "a_puerta_favor",
            "a_puerta_contra"
        ]

        for col in columnas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.tail(n_partidos)

        resumenes.append({
            "equipo": equipo,
            "shots_favor": df["shots_favor"].mean()
            if "shots_favor" in df.columns else np.nan,

            "shots_contra": df["shots_contra"].mean()
            if "shots_contra" in df.columns else np.nan,

            "a_puerta_favor": df["a_puerta_favor"].mean()
            if "a_puerta_favor" in df.columns else np.nan,

            "a_puerta_contra": df["a_puerta_contra"].mean()
            if "a_puerta_contra" in df.columns else np.nan
        })

    return pd.DataFrame(resumenes)

def calcular_puntos_equipo(df_equipo):
    """
    Calcula los puntos de un equipo a partir de la columna Resultado.

    W = 3 puntos
    D = 1 punto
    L u otro valor = 0 puntos
    """

    if df_equipo is None or df_equipo.empty:
        return 0

    if "resultado" not in df_equipo.columns:
        return 0

    resultados = (
        df_equipo["resultado"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    puntos = 0
    puntos += (resultados == "W").sum() * 3
    puntos += (resultados == "D").sum() * 1

    return int(puntos)


def calcular_tabla_division(division, n_partidos=10):
    """
    Calcula una tabla general para una división.

    Lee todos los partidos de cada equipo, suma puntos y ordena
    de mayor a menor. La posición 1 es el equipo con más puntos.
    """

    equipos = cargar_equipos_division(division)

    tabla = []

    for equipo in equipos:

        ruta = os.path.join(RUTA_STATS, f"{equipo}.xlsx")

        if not os.path.exists(ruta):
            continue

        try:
            df = pd.read_excel(ruta)
        except Exception:
            continue

        df = normalizar_columnas_basicas(df)

        if n_partidos is not None:
            df = df.tail(n_partidos)

        puntos = calcular_puntos_equipo(df)

        tabla.append({
            "equipo": equipo,
            "puntos": puntos
        })

    if not tabla:
        return pd.DataFrame()

    df_tabla = pd.DataFrame(tabla)

    df_tabla = df_tabla.sort_values(
        by="puntos",
        ascending=False
    ).reset_index(drop=True)

    df_tabla["posicion"] = df_tabla.index + 1

    return df_tabla


def obtener_posicion_equipo(equipo_archivo, n_partidos=10):
    """
    Devuelve la posición general de un equipo dentro de su división.
    """

    division = obtener_division_equipo(equipo_archivo)

    if division is None:
        return None

    df_tabla = calcular_tabla_division(
        division,
        n_partidos
    )

    if df_tabla.empty:
        return None

    fila = df_tabla[
        df_tabla["equipo"] == equipo_archivo
    ]

    if fila.empty:
        return None

    return int(fila["posicion"].iloc[0])

# ==========================================================
# 1. PERCENTILES Y PERFILES
# ==========================================================

def calcular_percentil_liga(valor, valores_liga):
    """
    Calcula el percentil de un equipo dentro de su liga.

    Retorna un valor entre 0 y 100.
    """
    valores = pd.to_numeric(
        pd.Series(valores_liga),
        errors="coerce"
    ).dropna().values

    if pd.isna(valor) or len(valores) < 3:
        return None

    valor = float(valor)

    percentil = (valores < valor).sum() / len(valores) * 100

    return round(percentil, 1)


def clasificar_perfil(percentil):
    """
    Clasifica un percentil en Bajo, Medio o Alto.
    """
    if percentil is None:
        return "Sin datos"

    if percentil < 34:
        return "Bajo"

    if percentil <= 66:
        return "Medio"

    return "Alto"


def obtener_factor_enfrentamiento(perfil_atacante, perfil_defensivo):
    """
    Define el factor de contexto según el cruce entre:
    - Perfil ofensivo del equipo atacante.
    - Perfil defensivo del rival.

    El factor se aplica al lambda.
    """
    mapa = {
        ("Alto", "Alto"): 1.10,
        ("Alto", "Medio"): 1.05,
        ("Alto", "Bajo"): 1.00,
        ("Medio", "Alto"): 1.05,
        ("Medio", "Medio"): 1.00,
        ("Medio", "Bajo"): 0.96,
        ("Bajo", "Alto"): 1.00,
        ("Bajo", "Medio"): 0.96,
        ("Bajo", "Bajo"): 0.90,
    }

    return mapa.get(
        (perfil_atacante, perfil_defensivo),
        1.00
    )
    
def convertir_tabla_a_imagen(df, titulo):
    """
    Convierte un DataFrame en una figura de Matplotlib
    para mostrarla en Streamlit como imagen estática.
    """

    if df is None or df.empty:
        return None

    fig, ax = plt.subplots(
        figsize=(16, max(3, 0.55 * (len(df) + 1))),
        dpi=150
    )

    ax.axis("off")

    tabla = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        loc="center"
    )

    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    tabla.scale(1, 1.6)

    # Encabezado
    for j in range(len(df.columns)):
        celda = tabla[(0, j)]
        celda.set_facecolor("#1f4e79")
        celda.set_text_props(color="white", weight="bold")

    # Filas alternadas
    for i in range(1, len(df) + 1):
        color = "#ffffff" if i % 2 != 0 else "#eaf2f8"

        for j in range(len(df.columns)):
            tabla[(i, j)].set_facecolor(color)

    ax.set_title(
        titulo,
        fontsize=14,
        fontweight="bold",
        pad=20
    )

    plt.tight_layout()

    return fig

def ajustar_mercado_1x2(
    prob_local,
    prob_empate,
    prob_visitante,
    factor_local,
    factor_visitante
):
    """
    Ajusta el mercado 1X2 de forma coherente.

    Sube o baja la probabilidad de cada resultado según el factor
    de contexto y luego normaliza para que la suma sea 100.
    """

    if None in [prob_local, prob_empate, prob_visitante]:
        return None, None, None

    prob_local_ajustada = prob_local * factor_local
    prob_visitante_ajustada = prob_visitante * factor_visitante

    prob_empate_ajustada = prob_empate

    total = (
        prob_local_ajustada
        + prob_empate_ajustada
        + prob_visitante_ajustada
    )

    if total <= 0:
        return None, None, None

    prob_local_final = prob_local_ajustada / total * 100
    prob_empate_final = prob_empate_ajustada / total * 100
    prob_visitante_final = prob_visitante_ajustada / total * 100

    return (
        round(prob_local_final, 1),
        round(prob_empate_final, 1),
        round(prob_visitante_final, 1)
    )



# ==========================================================
# 2. PERCENTILES DEL PARTIDO
# ==========================================================

def obtener_percentiles_partido(
    metricas,
    equipo_local_archivo,
    equipo_visitante_archivo,
    n_partidos = 10
):
    """
    Calcula los percentiles de liga para local y visitante.
    """

    division_local = obtener_division_equipo(equipo_local_archivo)
    division_visitante = obtener_division_equipo(equipo_visitante_archivo)

    df_liga_local = cargar_resumen_division(
        division_local,
        n_partidos
    )

    df_liga_visitante = cargar_resumen_division(
        division_visitante,
        n_partidos
    )

    if df_liga_local.empty or df_liga_visitante.empty:
        return {}

    df_liga_local = df_liga_local.copy()
    df_liga_visitante = df_liga_visitante.copy()

    for df in [df_liga_local, df_liga_visitante]:
        for col in [
            "shots_favor",
            "shots_contra",
            "a_puerta_favor",
            "a_puerta_contra"
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    percentiles = {}

    # ------------------------------------------------------
    # Local
    # ------------------------------------------------------

    percentiles["remates_local"] = calcular_percentil_liga(
        metricas.get("Remates_att_local"),
        df_liga_local["shots_favor"]
    )

    percentiles["remates_concede_local"] = calcular_percentil_liga(
        metricas.get("Remates_contra_local"),
        df_liga_local["shots_contra"]
    )

    percentiles["sot_local"] = calcular_percentil_liga(
        metricas.get("SoT_local"),
        df_liga_local["a_puerta_favor"]
    )

    sot_contra_local = metricas.get("SoT_contra_local")

    if sot_contra_local is None:
        fila_local = df_liga_local[
            df_liga_local["equipo"] == equipo_local_archivo
        ]

        if not fila_local.empty:
            sot_contra_local = fila_local["a_puerta_contra"].iloc[0]

    percentiles["sot_concede_local"] = calcular_percentil_liga(
        sot_contra_local,
        df_liga_local["a_puerta_contra"]
    )

    # ------------------------------------------------------
    # Visitante
    # ------------------------------------------------------

    percentiles["remates_visitante"] = calcular_percentil_liga(
        metricas.get("Remates_att_vis"),
        df_liga_visitante["shots_favor"]
    )

    percentiles["remates_concede_visitante"] = calcular_percentil_liga(
        metricas.get("Remates_contra_vis"),
        df_liga_visitante["shots_contra"]
    )

    percentiles["sot_visitante"] = calcular_percentil_liga(
        metricas.get("SoT_vis"),
        df_liga_visitante["a_puerta_favor"]
    )

    sot_contra_vis = metricas.get("SoT_contra_vis")

    if sot_contra_vis is None:
        fila_vis = df_liga_visitante[
            df_liga_visitante["equipo"] == equipo_visitante_archivo
        ]

        if not fila_vis.empty:
            sot_contra_vis = fila_vis["a_puerta_contra"].iloc[0]

    percentiles["sot_concede_visitante"] = calcular_percentil_liga(
        sot_contra_vis,
        df_liga_visitante["a_puerta_contra"]
    )

    return percentiles



def obtener_perfiles_partido(percentiles):
    """
    Convierte percentiles en perfiles Bajo, Medio o Alto.
    """

    perfiles = {}

    claves = [
        "remates_local",
        "remates_concede_local",
        "sot_local",
        "sot_concede_local",
        "remates_visitante",
        "remates_concede_visitante",
        "sot_visitante",
        "sot_concede_visitante"
    ]

    for clave in claves:
        perfiles[clave] = clasificar_perfil(
            percentiles.get(clave)
        )

    return perfiles


# ==========================================================
# 3. FACTORES DE CONTEXTO
# ==========================================================

def obtener_factores_contexto(perfiles):
    """
    Calcula los factores de contexto para cada mercado.

    Los factores se aplican sobre los lambdas.
    """

    perfil_remates_local = perfiles["remates_local"]
    perfil_remates_concede_local = perfiles["remates_concede_local"]
    perfil_sot_local = perfiles["sot_local"]
    perfil_sot_concede_local = perfiles["sot_concede_local"]

    perfil_remates_visitante = perfiles["remates_visitante"]
    perfil_remates_concede_visitante = perfiles["remates_concede_visitante"]
    perfil_sot_visitante = perfiles["sot_visitante"]
    perfil_sot_concede_visitante = perfiles["sot_concede_visitante"]

    # ------------------------------------------------------
    # Remates
    # ------------------------------------------------------

    factor_remates_local = obtener_factor_enfrentamiento(
        perfil_remates_local,
        perfil_remates_concede_visitante
    )

    factor_remates_visitante = obtener_factor_enfrentamiento(
        perfil_remates_visitante,
        perfil_remates_concede_local
    )

    factor_remates_totales = round(
        (factor_remates_local + factor_remates_visitante) / 2,
        3
    )

    factor_sot_local = obtener_factor_enfrentamiento(
        perfil_sot_local,
        perfil_sot_concede_visitante
    )

    factor_sot_visitante = obtener_factor_enfrentamiento(
        perfil_sot_visitante,
        perfil_sot_concede_local
    )

    factor_sot_totales = round(
        (factor_sot_local + factor_sot_visitante) / 2,
        3
    )

    factor_peligro_local = factor_sot_local
    factor_peligro_visitante = factor_sot_visitante

    factor_btts = round(
        (factor_peligro_local + factor_peligro_visitante) / 2,
        3
    )

    factor_over_goles = factor_btts

    return {
        "remates_local": factor_remates_local,
        "remates_visitante": factor_remates_visitante,
        "remates_totales": factor_remates_totales,
        "sot_local": factor_sot_local,
        "sot_visitante": factor_sot_visitante,
        "sot_totales": factor_sot_totales,
        "peligro_local": factor_peligro_local,
        "peligro_visitante": factor_peligro_visitante,
        "btts": factor_btts,
        "over_goles": factor_over_goles
    }


# ==========================================================
# 4. AJUSTE DE MERCADOS DE UNA LÍNEA
# ==========================================================

def ajustar_probabilidad_simple(prob_base, factor_contexto):
    """
    Ajusta una probabilidad de una sola línea.

    Convierte el factor de contexto en un ajuste limitado.
    """

    if prob_base is None:
        return None, 0

    ajuste = (factor_contexto - 1) * 100

    # Limitamos el ajuste entre -6% y +6%
    ajuste = max(-6, min(6, ajuste))

    prob_final = prob_base + ajuste
    prob_final = max(1, min(99, prob_final))

    return round(prob_final, 1), round(ajuste, 1)


# ==========================================================
# 5. AJUSTE DE LAMBDAS
# ==========================================================

def ajustar_lambda_contexto(lambda_base, factor_contexto):
    """
    Aplica el factor de contexto a un lambda.

    El resultado se usa para recalcular Poisson
    en todas las líneas del mercado.
    """

    if lambda_base is None:
        return None, 1.00

    lambda_ajustado = float(lambda_base) * float(factor_contexto)

    return round(lambda_ajustado, 3), round(factor_contexto, 3)


# ==========================================================
# 6. CONTEXTO ESPECÍFICO
# ==========================================================

def generar_contexto_texto(perfiles, division_local, division_visitante):
    """
    Genera un texto específico del enfrentamiento.
    """

    texto = (
        f"División local: {division_local or 'Sin datos'}. "
        f"División visitante: {division_visitante or 'Sin datos'}. "
        f"Local: remates {perfiles['remates_local']}, "
        f"concede remates {perfiles['remates_concede_local']}, "
        f"tiros a puerta {perfiles['sot_local']}, "
        f"concede tiros a puerta {perfiles['sot_concede_local']}. "
        f"Visitante: remates {perfiles['remates_visitante']}, "
        f"concede remates {perfiles['remates_concede_visitante']}, "
        f"tiros a puerta {perfiles['sot_visitante']}, "
        f"concede tiros a puerta {perfiles['sot_concede_visitante']}."
    )
    return texto


# ==========================================================
# 7. TABLA RESUMEN DE CONTEXTO
# ==========================================================

def generar_tabla_contexto(
    prob_base,
    metricas,
    equipo_local_archivo,
    equipo_visitante_archivo,
    n_partidos=10,
    posicion_local=None,
    posicion_visitante=None
):
    """
    Genera la tabla final de contexto y ajuste.

    prob_base debe ser un diccionario con claves similares a:
    - Local Gana
    - Empate
    - Visitante Gana
    - Prob. Local marca
    - Prob. Visitante marca
    - Prob. BTTS
    - Prob. Over 1.5 Goles
    - Prob. Over 2.5 Goles
    """

    if prob_base is None or metricas is None:
        return pd.DataFrame()

    division_local = obtener_division_equipo(equipo_local_archivo)
    division_visitante = obtener_division_equipo(equipo_visitante_archivo)

    percentiles = obtener_percentiles_partido(
        metricas,
        equipo_local_archivo,
        equipo_visitante_archivo,
        n_partidos
    )

    if not percentiles:
        return pd.DataFrame()

    perfiles = obtener_perfiles_partido(percentiles)

    factores = obtener_factores_contexto(perfiles)

    contexto_texto = generar_contexto_texto(
        perfiles,
        division_local,
        division_visitante
    )

    ajuste_tabla = 0

    posicion_local = obtener_posicion_equipo(
        equipo_local_archivo,
        n_partidos
    )

    posicion_visitante = obtener_posicion_equipo(
        equipo_visitante_archivo,
        n_partidos
    )

    diferencia_posiciones = None

    if posicion_local is not None and posicion_visitante is not None:
        diferencia_posiciones = abs(
            posicion_local - posicion_visitante
        )

    ajuste_tabla = 0

    if diferencia_posiciones is not None:

        if diferencia_posiciones >= 10:
            ajuste_tabla = 1
        elif diferencia_posiciones <= 3:
            ajuste_tabla = -1

    posicion_texto = (
        f"Posición local: {posicion_local if posicion_local is not None else 'Sin datos'}. "
        f"Posición visitante: {posicion_visitante if posicion_visitante is not None else 'Sin datos'}. "
        f"Diferencia: {diferencia_posiciones if diferencia_posiciones is not None else 'Sin datos'}. "
        f"Ajuste tabla: {ajuste_tabla}."
    )
    
    prob_local_1x2, prob_empate_1x2, prob_visitante_1x2 = ajustar_mercado_1x2(
        prob_base.get("Local_gana"),
        prob_base.get("Empate"),
        prob_base.get("Visitante_gana"),
        factores["peligro_local"],
        factores["peligro_visitante"]
    )

    mercados = [
        (
            "Gana Local",
            prob_base.get("Local_gana"),
            prob_local_1x2,
            factores["peligro_local"]
        ),
        (
            "Empate",
            prob_base.get("Empate"),
            prob_empate_1x2,
            1.00
        ),
        (
            "Gana visitante",
            prob_base.get("Visitante_gana"),
            prob_visitante_1x2,
            factores["peligro_visitante"]
        ),
        (
            "Marca local",
            prob_base.get("Marca Local"),
            None,
            factores["peligro_local"]
        ),
        (
            "Marca visitante",
            prob_base.get("Marca Visitante"),
            None,
            factores["peligro_visitante"]
        ),
        (
            "BTTS",
            prob_base.get("BTTS"),
            None,
            factores["btts"]
        ),
        (
            "Over 1.5 goles",
            prob_base.get("Over 1.5 Goles"),
            None,
            factores["over_goles"]
        ),
        (
            "Over 2.5 goles",
            prob_base.get("Over 2.5 Goles"),
            None,
            factores["over_goles"]
        )
    ]
    filas = []

    for mercado, prob, prob_1x2_ajustada, factor in mercados:

        if mercado in ["Gana Local", "Empate", "Gana visitante"]:

            if prob_1x2_ajustada is None:
                continue

            prob_final = prob_1x2_ajustada
            ajuste = round(prob_final - prob, 1)

        else:
            prob_final, ajuste = ajustar_probabilidad_simple(
                prob,
                factor
            )

            if prob_final is None:
                continue

        diferencia = round(prob_final - prob, 1)

        if diferencia >= 2:
            senal = "Favorable"
        elif diferencia <= -2:
            senal = "Desfavorable"
        else:
            senal = "Neutra"

        filas.append({
            "Mercado": mercado,
            "Prob. base": round(prob, 1),
            "Factor contexto": factor,
            "Ajuste": ajuste,
            "Ajuste tabla": ajuste_tabla,
            "Prob. final": prob_final,
            "Diferencia": diferencia,
            "Señal": senal,
            "Contexto": contexto_texto
        })

    lambdas_contexto = [
        (
            "Remates totales",
            metricas.get("Remates_att_local", 0)
            + metricas.get("Remates_att_vis", 0),
            factores["remates_totales"]
        ),
        (
            "Remates local",
            metricas.get("Remates_att_local"),
            factores["remates_local"]
        ),
        (
            "Remates visitante",
            metricas.get("Remates_att_vis"),
            factores["remates_visitante"]
        ),
        (
            "A puerta totales",
            metricas.get("SoT_local", 0)
            + metricas.get("SoT_vis", 0),
            factores["sot_totales"]
        ),
        (
            "A puerta local",
            metricas.get("SoT_local"),
            factores["sot_local"]
        ),
        (
            "A puerta visitante",
            metricas.get("SoT_vis"),
            factores["sot_visitante"]
        )
    ]

    for mercado, lambda_base, factor in lambdas_contexto:

        lambda_ajustado, factor_final = ajustar_lambda_contexto(
            lambda_base,
            factor
        )

        if lambda_ajustado is None:
            continue

        diferencia_porcentual = round(
            (factor_final - 1) * 100,
            1
        )

        if diferencia_porcentual >= 2:
            senal = "Favorable"
        elif diferencia_porcentual <= -2:
            senal = "Desfavorable"
        else:
            senal = "Neutra"

        filas.append({
            "Mercado": mercado,
            "Lambda base": round(lambda_base, 2),
            "Factor contexto": factor_final,
            "Lambda ajustado": lambda_ajustado,
            "Ajuste": f"{diferencia_porcentual}%",
            "Ajuste tabla": ajuste_tabla,
            "Señal": senal,
            "Contexto": contexto_texto + " " + posicion_texto
        })

    return pd.DataFrame(filas)