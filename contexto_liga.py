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
from scipy.stats import poisson, skellam

RUTA_STATS = "new-stats"
RUTA_EQUIPOS_LIGAS = "enlaces_equipos.xlsx"

def _numero_contexto(valor):
    try:
        numero = float(valor)

        if not np.isfinite(numero):
            return None

        return numero

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
# CONTEXTO DE REMATES Y TIROS A PUERTA
# ==========================================================

def preparar_contexto_remates_sot(
    equipo_local,
    equipo_visitante,
    mapa_equipos,
    n_partidos=10,
    fuerza=0.50,
):
    """
    Devuelve:
        factores, estado

    Compara cada equipo dentro de su división y condición.
    Los factores se aplican a las proyecciones, no a los
    históricos ni a las columnas de probabilidad base.
    """

    factores = {
        "remates_local": 1.0,
        "remates_visitante": 1.0,
        "sot_local": 1.0,
        "sot_visitante": 1.0,
    }

    try:
        catalogo = _leer_catalogo_contexto()

        equipo_local = str(equipo_local).strip().lower()
        equipo_visitante = str(equipo_visitante).strip().lower()

        mapa = {
            str(clave).strip().lower():
            str(valor).strip().casefold()
            for clave, valor in mapa_equipos.items()
        }

        def division_equipo(equipo):
            filas = catalogo.loc[
                (catalogo["equipo"] == equipo)
                & (catalogo["analizar"] == "si"),
                "division"
            ].dropna()

            if filas.empty:
                return None

            division = str(filas.iloc[0]).strip()

            return division if division else None

        division_local = division_equipo(equipo_local)
        division_vis = division_equipo(equipo_visitante)

        if division_local is None or division_vis is None:
            return (
                factores,
                "Sin contexto: falta división analizable."
            )

        columnas = [
            "shots_favor",
            "shots_contra",
            "a_puerta_favor",
            "a_puerta_contra",
        ]

        cache_archivos = {}
        cache_resumenes = {}
        cache_referencias = {}

        def resumen_equipo(equipo, condicion):
            clave = (equipo, condicion)

            if clave in cache_resumenes:
                return cache_resumenes[clave]

            nombre = mapa.get(equipo)

            if nombre is None:
                cache_resumenes[clave] = None
                return None

            if equipo not in cache_archivos:
                ruta = os.path.join(
                    RUTA_STATS, f"{equipo}.xlsx"
                )

                try:
                    df = pd.read_excel(ruta)
                    df = normalizar_columnas_basicas(df)

                except (OSError, ValueError):
                    df = None

                cache_archivos[equipo] = df

            df = cache_archivos[equipo]

            if df is None:
                cache_resumenes[clave] = None
                return None

            col_condicion = (
                "equipo_local"
                if condicion == "local"
                else "visitante"
            )

            if col_condicion not in df.columns:
                cache_resumenes[clave] = None
                return None

            nombres = (
                df[col_condicion]
                .astype("string")
                .str.strip()
                .str.casefold()
            )

            filtrado = df.loc[nombres == nombre].copy()

            if "fecha" in filtrado.columns:
                filtrado["_fecha_contexto"] = pd.to_datetime(
                    filtrado["fecha"],
                    dayfirst=True,
                    errors="coerce",
                )

                filtrado = filtrado.sort_values(
                    "_fecha_contexto",
                    na_position="first",
                )

            if n_partidos is not None:
                filtrado = filtrado.tail(n_partidos)

            resumen = {"equipo": equipo}

            for col in columnas:
                if col not in filtrado.columns:
                    resumen[col] = np.nan
                    continue

                valores = pd.to_numeric(
                    filtrado[col],
                    errors="coerce",
                )

                valores = valores[
                    valores.notna()
                    & np.isfinite(valores)
                    & (valores >= 0)
                ]

                resumen[col] = (
                    float(valores.mean())
                    if len(valores) >= 3
                    else np.nan
                )

            cache_resumenes[clave] = resumen

            return resumen

        def referencia_division(division, condicion):
            clave = (division, condicion)

            if clave not in cache_referencias:
                equipos = catalogo.loc[
                    (catalogo["division"] == division)
                    & (catalogo["analizar"] == "si"),
                    "equipo"
                ].dropna().drop_duplicates()

                filas = []

                for equipo in equipos:
                    resumen = resumen_equipo(
                        equipo, condicion
                    )

                    if resumen is not None:
                        filas.append(resumen)

                cache_referencias[clave] = pd.DataFrame(
                    filas,
                    columns=["equipo"] + columnas,
                )

            return cache_referencias[clave]

        liga_local = referencia_division(
            division_local, "local"
        )

        liga_vis = referencia_division(
            division_vis, "visitante"
        )

        propio_local = resumen_equipo(
            equipo_local, "local"
        )

        propio_vis = resumen_equipo(
            equipo_visitante, "visitante"
        )

        if propio_local is None or propio_vis is None:
            return (
                factores,
                "Sin contexto: no se pudo cargar un equipo "
                "o no coincide su nombre en mapa_equipos."
            )

        fuerza = float(np.clip(fuerza, 0.0, 1.0))
        avisos = []

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
                avisos.append(
                    f"{etiqueta}: datos insuficientes"
                )
                return 1.0

            pct_ataque = calcular_percentil_liga(
                ataque,
                liga_ataque[col_favor],
            )

            pct_concede = calcular_percentil_liga(
                concede,
                liga_defensa[col_contra],
            )

            if pct_ataque is None or pct_concede is None:
                avisos.append(
                    f"{etiqueta}: referencia insuficiente"
                )
                return 1.0

            factor = obtener_factor_enfrentamiento(
                clasificar_perfil(pct_ataque),
                clasificar_perfil(pct_concede),
            )

            return 1.0 + fuerza * (factor - 1.0)

        mercados = [
            ("remates", "shots_favor", "shots_contra"),
            ("sot", "a_puerta_favor", "a_puerta_contra"),
        ]

        for prefijo, col_favor, col_contra in mercados:
            factores[f"{prefijo}_local"] = factor_cruce(
                propio_local,
                propio_vis,
                liga_local,
                liga_vis,
                col_favor,
                col_contra,
                f"{prefijo} local",
            )

            factores[f"{prefijo}_visitante"] = factor_cruce(
                propio_vis,
                propio_local,
                liga_vis,
                liga_local,
                col_favor,
                col_contra,
                f"{prefijo} visitante",
            )

        if avisos:
            estado = "Contexto parcial: " + "; ".join(avisos)
        else:
            estado = (
                "Contexto de remates y tiros a puerta aplicado."
            )

        return factores, estado

    except (OSError, ValueError, KeyError, TypeError) as error:
        return factores, f"Sin contexto: {error}"

