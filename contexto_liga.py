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
        
    def factor_total_ponderado(base_local, base_vis, factor_local, factor_vis):
        if base_local is None or base_vis is None:
            return 1.0

        base_local = float(base_local)
        base_vis = float(base_vis)

        total_base = base_local + base_vis

        if total_base <= 0:
            return 1.0

        total_ajustado = (
            base_local * factor_local
            + base_vis * factor_vis
        )

        return total_ajustado / total_base


    factor_remates_total = factor_total_ponderado(
        metricas.get("Remates_att_local"),
        metricas.get("Remates_att_vis"),
        factores["remates_local"],
        factores["remates_visitante"]
    )

    factor_sot_total = factor_total_ponderado(
        metricas.get("SoT_local"),
        metricas.get("SoT_vis"),
        factores["sot_local"],
        factores["sot_visitante"]
    )

    lambdas_contexto = [
        (
            "Remates totales",
            metricas.get("Remates_att_local", 0)
            + metricas.get("Remates_att_vis", 0),
            factor_remates_total
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
            factor_sot_total
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

# ==========================================================
# 8. CONTEXTO DE GOLES PARA EL MODELO MARCA / RECIBE
# ==========================================================

from scipy.stats import poisson, skellam


def _numero_contexto(valor):
    try:
        numero = float(valor)
        return numero if np.isfinite(numero) else None
    except (TypeError, ValueError):
        return None


def _leer_catalogo_contexto():
    df = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    df = normalizar_columnas_basicas(df)

    requeridas = {"equipo", "division", "analizar"}
    faltantes = requeridas - set(df.columns)

    if faltantes:
        raise ValueError(
            f"Faltan columnas en {RUTA_EQUIPOS_LIGAS}: "
            f"{', '.join(sorted(faltantes))}"
        )

    for columna in requeridas:
        df[columna] = (
            df[columna]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    return df


def _resumen_goles_contexto(df, condicion, n_partidos):
    """
    df debe contener exclusivamente partidos del equipo
    en la condición indicada.
    """
    if df is None or df.empty:
        return None

    df = normalizar_columnas_basicas(df.copy())

    favor_col = (
        "goles_local" if condicion == "local"
        else "goles_visitante"
    )
    contra_col = (
        "goles_visitante" if condicion == "local"
        else "goles_local"
    )

    if not {favor_col, contra_col}.issubset(df.columns):
        return None

    if "fecha" in df.columns:
        df["_fecha_contexto"] = pd.to_datetime(
            df["fecha"], dayfirst=True, errors="coerce"
        )
        df = df.sort_values(
            "_fecha_contexto", na_position="first"
        )

    if n_partidos is not None:
        df = df.tail(n_partidos)

    favor = pd.to_numeric(df[favor_col], errors="coerce")
    contra = pd.to_numeric(df[contra_col], errors="coerce")

    validos = (
        favor.notna() & contra.notna()
        & (favor >= 0) & (contra >= 0)
    )

    favor = favor[validos]
    contra = contra[validos]

    if favor.empty:
        return None

    return {
        "marca": float((favor > 0).mean()),
        "recibe": float((contra > 0).mean()),
        "no_marca": float((favor == 0).mean()),
        "no_recibe": float((contra == 0).mean()),
        "muestra": len(favor),
    }


def _referencia_goles_division(
    catalogo, division, condicion, n_partidos, excluir_equipo
):
    """
    Una observación por equipo, en su condición correspondiente.
    Se excluye al equipo evaluado de su referencia.
    """
    equipos = catalogo.loc[
        (catalogo["division"] == division)
        & (catalogo["analizar"] == "si")
        & (catalogo["equipo"] != excluir_equipo),
        "equipo"
    ].dropna().drop_duplicates()

    resumenes = []

    for equipo in equipos:
        ruta = os.path.join(RUTA_STATS, f"{equipo}.xlsx")

        if not os.path.exists(ruta):
            continue

        try:
            df = normalizar_columnas_basicas(
                pd.read_excel(ruta)
            )

            # En cada archivo están los partidos de ese equipo.
            # Resultado y métricas Favor se refieren a él.
            if not {"resultado", "equipo_local", "visitante"}.issubset(
                df.columns
            ):
                continue

            resultado = (
                df["resultado"]
                .astype("string")
                .str.strip()
                .str.upper()
            )

            goles_local = pd.to_numeric(
                df["goles_local"], errors="coerce"
            )
            goles_vis = pd.to_numeric(
                df["goles_visitante"], errors="coerce"
            )

            # Identificar la condición mediante goles por tiempos
            # del propio equipo, cuando están disponibles.
            if {
                "1t_goles_favor", "2t_goles_favor",
                "1t_goles_contra", "2t_goles_contra"
            }.issubset(df.columns):
                gf = (
                    pd.to_numeric(df["1t_goles_favor"], errors="coerce")
                    + pd.to_numeric(df["2t_goles_favor"], errors="coerce")
                )
                gc = (
                    pd.to_numeric(df["1t_goles_contra"], errors="coerce")
                    + pd.to_numeric(df["2t_goles_contra"], errors="coerce")
                )

                local_seguro = (
                    (gf == goles_local) & (gc == goles_vis)
                    & (goles_local != goles_vis)
                )
                vis_seguro = (
                    (gf == goles_vis) & (gc == goles_local)
                    & (goles_local != goles_vis)
                )
            else:
                local_seguro = (
                    ((resultado == "W") & (goles_local > goles_vis))
                    | ((resultado == "L") & (goles_local < goles_vis))
                )
                vis_seguro = (
                    ((resultado == "W") & (goles_vis > goles_local))
                    | ((resultado == "L") & (goles_vis < goles_local))
                )

            # El nombre que más aparece en ambas columnas es
            # el candidato a equipo dueño del archivo.
            nombres = pd.concat([
                df.loc[local_seguro, "equipo_local"],
                df.loc[vis_seguro, "visitante"],
            ]).dropna().astype(str).str.strip().str.casefold()

            if nombres.empty:
                continue

            nombre = nombres.value_counts().idxmax()
            columna = (
                "equipo_local" if condicion == "local"
                else "visitante"
            )

            filtro = (
                df[columna].astype("string")
                .str.strip().str.casefold() == nombre
            )

            resumen = _resumen_goles_contexto(
                df.loc[filtro], condicion, n_partidos
            )

            if resumen is not None and resumen["muestra"] >= 3:
                resumenes.append(resumen)

        except (OSError, ValueError, KeyError):
            continue

    if len(resumenes) < 3:
        return None

    return pd.DataFrame(resumenes)[
        ["marca", "recibe", "no_marca", "no_recibe"]
    ].mean().to_dict()


def _mercados_poisson_contexto(lambda_local, lambda_vis):
    total = lambda_local + lambda_vis

    local = float(skellam.sf(0, lambda_local, lambda_vis))
    empate = float(skellam.pmf(0, lambda_local, lambda_vis))
    visita = float(skellam.cdf(-1, lambda_local, lambda_vis))

    marca_local = float(poisson.sf(0, lambda_local))
    marca_vis = float(poisson.sf(0, lambda_vis))

    return {
        "Gana Local": 100 * local,
        "Empate": 100 * empate,
        "Gana Visitante": 100 * visita,
        "Marca Local": 100 * marca_local,
        "Marca Visitante": 100 * marca_vis,
        "BTTS": 100 * marca_local * marca_vis,
        "Over 1.5": 100 * float(poisson.sf(1, total)),
        "Over 2.5": 100 * float(poisson.sf(2, total)),
    }


def aplicar_contexto_goles(
    prediccion,
    df_local,
    df_visitante,
    equipo_local,
    equipo_visitante,
    n_partidos=10,
    intensidad=0.10,
):
    """
    Devuelve (prediccion_final, estado).

    No modifica prediccion.
    intensidad=0.10 limita cada factor a aproximadamente ±10%.
    Las rachas ya están incorporadas en prediccion.
    """
    base = dict(prediccion)
    final = dict(prediccion)

    try:
        catalogo = _leer_catalogo_contexto()
    except (OSError, ValueError) as error:
        return final, f"Sin contexto: {error}"

    equipo_local = str(equipo_local).strip().lower()
    equipo_visitante = str(equipo_visitante).strip().lower()

    def division_equipo(equipo):
        filas = catalogo.loc[
            (catalogo["equipo"] == equipo)
            & (catalogo["analizar"] == "si"),
            "division"
        ].dropna()

        return filas.iloc[0] if not filas.empty else None

    division_local = division_equipo(equipo_local)
    division_vis = division_equipo(equipo_visitante)

    if division_local is None or division_vis is None:
        return final, "Sin contexto: equipo sin división analizable."

    resumen_local = _resumen_goles_contexto(
        df_local, "local", n_partidos
    )
    resumen_vis = _resumen_goles_contexto(
        df_visitante, "visitante", n_partidos
    )

    referencia_local = _referencia_goles_division(
        catalogo, division_local, "local",
        n_partidos, equipo_local
    )
    referencia_vis = _referencia_goles_division(
        catalogo, division_vis, "visitante",
        n_partidos, equipo_visitante
    )

    resumenes = [resumen_local, resumen_vis]
    referencias = [referencia_local, referencia_vis]

    if any(valor is None for valor in resumenes + referencias):
        return final, "Sin contexto: referencia de liga insuficiente."

    if min(resumen_local["muestra"], resumen_vis["muestra"]) < 3:
        return final, "Sin contexto: menos de 3 partidos por equipo."

    claves = [
        "Gana Local", "Empate", "Gana Visitante",
        "Marca Local", "Marca Visitante", "BTTS",
        "Over 1.5", "Over 2.5"
    ]

    numeros = {clave: _numero_contexto(base.get(clave)) for clave in claves}

    if any(valor is None for valor in numeros.values()):
        return final, "Sin contexto: faltan probabilidades base."

    def ataque(resumen, referencia):
        return 0.5 * (
            (resumen["marca"] - referencia["marca"])
            - (resumen["no_marca"] - referencia["no_marca"])
        )

    def concesion(resumen, referencia):
        return 0.5 * (
            (resumen["recibe"] - referencia["recibe"])
            - (resumen["no_recibe"] - referencia["no_recibe"])
        )

    señal_local = 0.5 * (
        ataque(resumen_local, referencia_local)
        + concesion(resumen_vis, referencia_vis)
    )
    señal_vis = 0.5 * (
        ataque(resumen_vis, referencia_vis)
        + concesion(resumen_local, referencia_local)
    )

    confianza = min(
        1.0,
        min(resumen_local["muestra"], resumen_vis["muestra"]) / 10
    )

    intensidad = float(np.clip(intensidad, 0, 0.20))

    factor_local = 1 + intensidad * confianza * señal_local
    factor_vis = 1 + intensidad * confianza * señal_vis

    p_local = np.clip(numeros["Marca Local"] / 100, 0.001, 0.999)
    p_vis = np.clip(numeros["Marca Visitante"] / 100, 0.001, 0.999)

    lambda_local = -np.log1p(-p_local)
    lambda_vis = -np.log1p(-p_vis)

    antes = _mercados_poisson_contexto(lambda_local, lambda_vis)
    despues = _mercados_poisson_contexto(
        lambda_local * factor_local,
        lambda_vis * factor_vis
    )

    for clave in claves:
        cambio = despues[clave] - antes[clave]
        final[clave] = float(np.clip(numeros[clave] + cambio, 0, 100))

    claves_1x2 = ["Gana Local", "Empate", "Gana Visitante"]
    total_1x2 = sum(final[clave] for clave in claves_1x2)

    if total_1x2 <= 0:
        return base, "Sin contexto: mercado 1X2 inválido."

    for clave in claves_1x2:
        final[clave] = 100 * final[clave] / total_1x2

    final["1X"] = final["Gana Local"] + final["Empate"]
    final["X2"] = final["Gana Visitante"] + final["Empate"]
    final["12"] = final["Gana Local"] + final["Gana Visitante"]

    final["BTTS"] = min(
        final["BTTS"],
        final["Marca Local"],
        final["Marca Visitante"],
        final["Over 1.5"]
    )
    final["Over 2.5"] = min(
        final["Over 2.5"], final["Over 1.5"]
    )

    estado = (
        f"Contexto aplicado. "
        f"Factor local: {factor_local:.3f}; "
        f"factor visitante: {factor_vis:.3f}."
    )

    return final, estado


# ==========================================================
# CONTEXTO PARA PROYECCIONES DE REMATES Y TIROS A PUERTA
# ==========================================================

def preparar_contexto_remates_sot(
    equipo_local,
    equipo_visitante,
    mapa_equipos,
    n_partidos=10,
    fuerza=0.50,
):
    """
    Carga referencias por división y condición.

    fuerza=0.50 aplica la mitad del ajuste del mapa de perfiles:
    1.10 -> 1.05
    0.90 -> 0.95

    No modifica métricas, históricos ni probabilidades base.
    """
    factores = {
        "remates_local": 1.0,
        "remates_visitante": 1.0,
        "sot_local": 1.0,
        "sot_visitante": 1.0,
    }
    avisos = []

    try:
        catalogo = normalizar_columnas_basicas(
            pd.read_excel(RUTA_EQUIPOS_LIGAS)
        )

        requeridas = {"equipo", "division", "analizar"}

        if not requeridas.issubset(catalogo.columns):
            return factores, "Sin contexto: faltan columnas del catálogo."

        for col in requeridas:
            catalogo[col] = (
                catalogo[col].astype("string")
                .str.strip().str.lower()
            )

        mapa = {
            str(clave).strip().lower(): str(valor).strip().casefold()
            for clave, valor in mapa_equipos.items()
        }

        equipo_local = str(equipo_local).strip().lower()
        equipo_visitante = str(equipo_visitante).strip().lower()

        def obtener_division(equipo):
            filas = catalogo.loc[
                (catalogo["equipo"] == equipo)
                & (catalogo["analizar"] == "si"),
                "division"
            ].dropna()

            return filas.iloc[0] if not filas.empty else None

        division_local = obtener_division(equipo_local)
        division_vis = obtener_division(equipo_visitante)

        if division_local is None or division_vis is None:
            return factores, "Sin contexto: falta división analizable."

        cache_archivos = {}
        cache_referencias = {}

        columnas = [
            "shots_favor", "shots_contra",
            "a_puerta_favor", "a_puerta_contra",
        ]

        def leer_equipo(equipo, condicion):
            if equipo not in cache_archivos:
                ruta = os.path.join(RUTA_STATS, f"{equipo}.xlsx")

                try:
                    df = normalizar_columnas_basicas(
                        pd.read_excel(ruta)
                    )
                except (OSError, ValueError):
                    cache_archivos[equipo] = None
                else:
                    cache_archivos[equipo] = df

            df = cache_archivos[equipo]

            if df is None:
                return None

            # Exigimos el nombre del mapa para no confundir
            # equipos con nombres parcialmente coincidentes.
            nombre = mapa.get(equipo)

            if nombre is None:
                return None

            col_condicion = (
                "equipo_local" if condicion == "local"
                else "visitante"
            )

            if col_condicion not in df.columns:
                return None

            nombres = (
                df[col_condicion].astype("string")
                .str.strip().str.casefold()
            )

            filtrado = df.loc[nombres == nombre].copy()

            if "fecha" in filtrado.columns:
                filtrado["_fecha_contexto"] = pd.to_datetime(
                    filtrado["fecha"],
                    dayfirst=True,
                    errors="coerce",
                )
                filtrado = filtrado.sort_values(
                    "_fecha_contexto", na_position="first"
                )

            if n_partidos is not None:
                filtrado = filtrado.tail(n_partidos)

            resumen = {"equipo": equipo}

            for col in columnas:
                if col not in filtrado.columns:
                    resumen[col] = np.nan
                    continue

                valores = pd.to_numeric(
                    filtrado[col], errors="coerce"
                )
                valores = valores[
                    valores.notna() & np.isfinite(valores)
                    & (valores >= 0)
                ]

                resumen[col] = (
                    float(valores.mean())
                    if len(valores) >= 3 else np.nan
                )

            return resumen

        def referencia(division, condicion):
            clave = (division, condicion)

            if clave not in cache_referencias:
                equipos = catalogo.loc[
                    (catalogo["division"] == division)
                    & (catalogo["analizar"] == "si"),
                    "equipo"
                ].dropna().drop_duplicates()

                filas = []

                for equipo in equipos:
                    resumen = leer_equipo(equipo, condicion)

                    if resumen is not None:
                        filas.append(resumen)

                cache_referencias[clave] = pd.DataFrame(
                    filas, columns=["equipo"] + columnas
                )

            return cache_referencias[clave]

        liga_local = referencia(division_local, "local")
        liga_vis = referencia(division_vis, "visitante")

        propio_local = leer_equipo(equipo_local, "local")
        propio_vis = leer_equipo(equipo_visitante, "visitante")

        if propio_local is None or propio_vis is None:
            return factores, "Sin contexto: no se pudo cargar un equipo."

        fuerza = float(np.clip(fuerza, 0.0, 1.0))

        def factor_cruce(
            propio_ataque,
            propio_defensa,
            liga_ataque,
            liga_defensa,
            col_favor,
            col_contra,
            etiqueta,
        ):
            ataque = propio_ataque.get(col_favor)
            concede = propio_defensa.get(col_contra)

            if pd.isna(ataque) or pd.isna(concede):
                avisos.append(f"{etiqueta}: datos insuficientes")
                return 1.0

            pct_ataque = calcular_percentil_liga(
                ataque, liga_ataque[col_favor]
            )
            pct_concede = calcular_percentil_liga(
                concede, liga_defensa[col_contra]
            )

            if pct_ataque is None or pct_concede is None:
                avisos.append(f"{etiqueta}: referencia insuficiente")
                return 1.0

            factor = obtener_factor_enfrentamiento(
                clasificar_perfil(pct_ataque),
                clasificar_perfil(pct_concede),
            )

            return 1.0 + fuerza * (factor - 1.0)

        for prefijo, favor, contra in [
            ("remates", "shots_favor", "shots_contra"),
            ("sot", "a_puerta_favor", "a_puerta_contra"),
        ]:
            factores[f"{prefijo}_local"] = factor_cruce(
                propio_local, propio_vis,
                liga_local, liga_vis,
                favor, contra, f"{prefijo} local",
            )

            factores[f"{prefijo}_visitante"] = factor_cruce(
                propio_vis, propio_local,
                liga_vis, liga_local,
                favor, contra, f"{prefijo} visitante",
            )

        estado = (
            "Contexto parcial: " + "; ".join(avisos)
            if avisos else
            "Contexto de remates y tiros a puerta aplicado."
        )

        return factores, estado

    except (OSError, ValueError, KeyError, TypeError) as error:
        return factores, f"Sin contexto: {error}"