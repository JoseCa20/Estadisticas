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
    lambda_local = float(lambda_local)
    lambda_vis = float(lambda_vis)

    if (
        not np.isfinite(lambda_local)
        or not np.isfinite(lambda_vis)
        or lambda_local < 0
        or lambda_vis < 0
    ):
        raise ValueError(
            "Los lambdas deben ser finitos y no negativos."
        )

    if lambda_local == 0 and lambda_vis == 0:
        p_local = 0.0
        p_empate = 1.0
        p_vis = 0.0

    elif lambda_local == 0:
        p_local = 0.0
        p_empate = float(poisson.pmf(0, lambda_vis))
        p_vis = float(poisson.sf(0, lambda_vis))

    elif lambda_vis == 0:
        p_local = float(poisson.sf(0, lambda_local))
        p_empate = float(poisson.pmf(0, lambda_local))
        p_vis = 0.0

    else:
        p_local = float(
            skellam.sf(0, lambda_local, lambda_vis)
        )
        p_empate = float(
            skellam.pmf(0, lambda_local, lambda_vis)
        )
        p_vis = float(
            skellam.cdf(-1, lambda_local, lambda_vis)
        )

    probabilidades = np.clip(
        np.array([p_local, p_empate, p_vis], dtype=float),
        0.0,
        1.0,
    )

    probabilidades /= probabilidades.sum()
    p_local, p_empate, p_vis = probabilidades

    p_marca_local = float(poisson.sf(0, lambda_local))
    p_marca_vis = float(poisson.sf(0, lambda_vis))

    lambda_total = lambda_local + lambda_vis

    return {
        "Gana Local": 100.0 * p_local,
        "Empate": 100.0 * p_empate,
        "Gana Visitante": 100.0 * p_vis,

        "1X": 100.0 * (p_local + p_empate),
        "X2": 100.0 * (p_empate + p_vis),
        "12": 100.0 * (p_local + p_vis),

        "Marca Local": 100.0 * p_marca_local,
        "Marca Visitante": 100.0 * p_marca_vis,

        "BTTS": 100.0 * p_marca_local * p_marca_vis,

        "Over 1.5": 100.0 * float(
            poisson.sf(1, lambda_total)
        ),
        "Over 2.5": 100.0 * float(
            poisson.sf(2, lambda_total)
        ),
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
    Aplica contexto una sola vez sobre los lambdas base.

    Mantiene el criterio existente de marca/recibe de liga.
    No altera el diccionario original.
    """
    base = dict(prediccion)

    lambda_local = _numero_contexto(
        base.get("_lambda_local_base")
    )
    lambda_vis = _numero_contexto(
        base.get("_lambda_visitante_base")
    )

    if (
        lambda_local is None
        or lambda_vis is None
        or lambda_local < 0
        or lambda_vis < 0
    ):
        return (
            base,
            "Sin contexto: faltan lambdas base válidos."
        )

    try:
        if int(base.get("_rango", n_partidos)) != n_partidos:
            return (
                base,
                "Sin contexto: el rango no coincide con el modelo base."
            )

        catalogo = _leer_catalogo_contexto()

        equipo_local = str(equipo_local).strip().lower()
        equipo_visitante = str(equipo_visitante).strip().lower()

        def division_equipo(equipo):
            divisiones = (
                catalogo.loc[
                    (catalogo["equipo"] == equipo)
                    & (catalogo["analizar"] == "si"),
                    "division"
                ]
                .dropna()
                .drop_duplicates()
            )

            if len(divisiones) != 1:
                return None

            return divisiones.iloc[0]

        division_local = division_equipo(equipo_local)
        division_vis = division_equipo(equipo_visitante)

        if division_local is None or division_vis is None:
            return (
                base,
                "Sin contexto: falta una división analizable única."
            )

        # Usa las mismas filas válidas que alimentaron el núcleo.
        # Se guardan como argumentos explícitos al llamar a esta función.
        resumen_local = _resumen_goles_contexto(
            df_local,
            "local",
            n_partidos,
        )

        resumen_vis = _resumen_goles_contexto(
            df_visitante,
            "visitante",
            n_partidos,
        )

        referencia_local = _referencia_goles_division(
            catalogo,
            division_local,
            "local",
            n_partidos,
            equipo_local,
        )

        referencia_vis = _referencia_goles_division(
            catalogo,
            division_vis,
            "visitante",
            n_partidos,
            equipo_visitante,
        )

        if any(
            valor is None
            for valor in [
                resumen_local,
                resumen_vis,
                referencia_local,
                referencia_vis,
            ]
        ):
            return (
                base,
                "Sin contexto: referencia de liga insuficiente."
            )

        if min(
            resumen_local["muestra"],
            resumen_vis["muestra"],
        ) < 3:
            return (
                base,
                "Sin contexto: menos de tres partidos válidos "
                "en alguna condición."
            )

        def ataque(resumen, referencia):
            return 0.5 * (
                resumen["marca"] - referencia["marca"]
                - resumen["no_marca"] + referencia["no_marca"]
            )

        def concesion(resumen, referencia):
            return 0.5 * (
                resumen["recibe"] - referencia["recibe"]
                - resumen["no_recibe"] + referencia["no_recibe"]
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
            min(
                resumen_local["muestra"],
                resumen_vis["muestra"],
            ) / 10.0,
        )

        intensidad = float(np.clip(intensidad, 0.0, 0.20))

        factor_local = (
            1.0 + intensidad * confianza * señal_local
        )
        factor_vis = (
            1.0 + intensidad * confianza * señal_vis
        )

        lambda_local_final = lambda_local * factor_local
        lambda_vis_final = lambda_vis * factor_vis

        final = dict(base)

        final.update(
            _mercados_poisson_contexto(
                lambda_local_final,
                lambda_vis_final,
            )
        )

        final.update({
            "_lambda_local_contexto": lambda_local_final,
            "_lambda_visitante_contexto": lambda_vis_final,
            "_factor_contexto_local": factor_local,
            "_factor_contexto_visitante": factor_vis,
        })

        estado = (
            f"Contexto aplicado. "
            f"Factor local: {factor_local:.3f}; "
            f"factor visitante: {factor_vis:.3f}. "
            f"Lambda local: {lambda_local:.3f} "
            f"→ {lambda_local_final:.3f}; "
            f"lambda visitante: {lambda_vis:.3f} "
            f"→ {lambda_vis_final:.3f}."
        )

        return final, estado

    except (OSError, ValueError, KeyError, TypeError) as error:
        return base, f"Sin contexto: {error}"

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


# ==========================================================
# ANÁLISIS INDEPENDIENTE POR CUARTOS DE LA CLASIFICACIÓN
# ==========================================================

import unicodedata


def _texto_cuartos(valor):
    """Normaliza nombres para comparar sin coincidencias parciales."""
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().casefold()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caracter for caracter in texto
        if not unicodedata.combining(caracter)
    )

    return " ".join(texto.split())


def _cargar_division_cuartos(division, catalogo, mapa_equipos):
    """
    Lee todos los archivos completos de una división.

    Devuelve:
        {
            "clasificacion": DataFrame,
            "partidos": {equipo: DataFrame},
            "rangos": {cuarto: texto},
            "avisos": [...]
        }

    No modifica los cálculos anteriores.
    """
    equipos = (
        catalogo.loc[
            catalogo["division"] == division,
            "equipo"
        ]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if len(equipos) < 4:
        raise ValueError(
            f"{division}: hay menos de cuatro equipos registrados."
        )

    mapa = {
        str(clave).strip().lower(): _texto_cuartos(valor)
        for clave, valor in mapa_equipos.items()
    }

    sin_mapa = [
        equipo for equipo in equipos
        if not mapa.get(equipo)
    ]

    if sin_mapa:
        raise ValueError(
            f"{division}: faltan nombres en mapa_equipos para: "
            + ", ".join(sin_mapa)
        )

    # Los nombres se resuelven dentro de la división,
    # no globalmente entre países diferentes.
    inverso = {}

    for equipo in equipos:
        nombre = mapa[equipo]

        if nombre in inverso and inverso[nombre] != equipo:
            raise ValueError(
                f"{division}: nombre ambiguo '{nombre}' para "
                f"{inverso[nombre]} y {equipo}."
            )

        inverso[nombre] = equipo

    requeridas = {
        "fecha",
        "equipo_local",
        "visitante",
        "resultado",
        "goles_local",
        "goles_visitante",
        "shots_favor",
        "shots_contra",
        "a_puerta_favor",
        "a_puerta_contra",
    }

    columnas_metricas = [
        "shots_favor",
        "shots_contra",
        "a_puerta_favor",
        "a_puerta_contra",
    ]

    partidos = {}
    filas_tabla = []
    avisos = []

    for equipo in equipos:
        ruta = os.path.join(RUTA_STATS, f"{equipo}.xlsx")

        try:
            df = normalizar_columnas_basicas(
                pd.read_excel(ruta)
            ).copy()
        except (OSError, ValueError) as error:
            raise ValueError(
                f"{division}: no se pudo leer {equipo}.xlsx. "
                f"No se construye una clasificación parcial. "
                f"Detalle: {error}"
            ) from error

        faltantes = requeridas - set(df.columns)

        if faltantes:
            raise ValueError(
                f"{equipo}: faltan columnas: "
                + ", ".join(sorted(faltantes))
            )

        # Omitir filas completamente vacías.
        df = df.dropna(how="all").copy()

        nombre = mapa[equipo]
        nombres_local = df["equipo_local"].map(_texto_cuartos)
        nombres_vis = df["visitante"].map(_texto_cuartos)

        es_local = nombres_local == nombre
        es_visitante = nombres_vis == nombre

        pertenece = es_local ^ es_visitante
        descartadas = int((~pertenece).sum())

        if descartadas:
            avisos.append(
                f"{equipo}: {descartadas} filas no identificadas "
                "como partidos propios."
            )

        df = df.loc[pertenece].copy()
        es_local = es_local.loc[df.index]

        df["_condicion"] = np.where(
            es_local, "local", "visitante"
        )

        for columna in [
            "goles_local", "goles_visitante"
        ] + columnas_metricas:
            df[columna] = pd.to_numeric(
                df[columna], errors="coerce"
            )

        # No sumar puntos ni estadísticas de partidos sin marcador.
        jugados = (
            np.isfinite(df["goles_local"])
            & np.isfinite(df["goles_visitante"])
            & (df["goles_local"] >= 0)
            & (df["goles_visitante"] >= 0)
        )

        no_jugados = int((~jugados).sum())

        if no_jugados:
            avisos.append(
                f"{equipo}: {no_jugados} filas sin marcador válido "
                "excluidas."
            )

        df = df.loc[jugados].copy()

        df["_fecha"] = pd.to_datetime(
            df["fecha"], dayfirst=True, errors="coerce"
        )
        df = df.sort_values("_fecha", na_position="first")

        # No sumar dos veces el mismo partido dentro de un archivo.
        clave_partido = [
            "_fecha", "equipo_local", "visitante"
        ]

        duplicados = (
            df["_fecha"].notna()
            & df.duplicated(clave_partido, keep=False)
        )

        if duplicados.any():
            raise ValueError(
                f"{equipo}: hay partidos duplicados por "
                "fecha, local y visitante. Revisá el archivo."
            )

        resultado = (
            df["resultado"].astype("string")
            .str.strip().str.upper()
        )

        df["_puntos"] = (
            resultado.map({"W": 3, "D": 1})
            .fillna(0)
            .astype(int)
        )

        local = df["_condicion"] == "local"

        df["_gf"] = np.where(
            local, df["goles_local"], df["goles_visitante"]
        )
        df["_gc"] = np.where(
            local, df["goles_visitante"], df["goles_local"]
        )

        df["_nombre_rival"] = np.where(
            local, df["visitante"], df["equipo_local"]
        )

        df["_rival_id"] = (
            df["_nombre_rival"]
            .map(_texto_cuartos)
            .map(inverso)
        )

        sin_rival = int(df["_rival_id"].isna().sum())

        if sin_rival:
            avisos.append(
                f"{equipo}: {sin_rival} partidos con rival "
                "sin correspondencia en el catálogo/mapa; "
                "suman puntos, pero no entran en los cuartos."
            )

        # Un dato de remates faltante no se convierte en cero.
        for columna in columnas_metricas:
            valores = df[columna]

            df[columna] = valores.where(
                np.isfinite(valores) & (valores >= 0)
            )

        df["_remates_total"] = (
            df["shots_favor"] + df["shots_contra"]
        )
        df["_sot_total"] = (
            df["a_puerta_favor"] + df["a_puerta_contra"]
        )

        fila = {"equipo": equipo}

        selecciones = {
            "general": df,
            "local": df.loc[df["_condicion"] == "local"],
            "visitante": df.loc[df["_condicion"] == "visitante"],
        }

        for condicion, muestra in selecciones.items():
            gf = float(muestra["_gf"].sum())
            gc = float(muestra["_gc"].sum())

            fila[f"pj_{condicion}"] = len(muestra)
            fila[f"puntos_{condicion}"] = int(
                muestra["_puntos"].sum()
            )
            fila[f"dg_{condicion}"] = gf - gc
            fila[f"gf_{condicion}"] = gf

        filas_tabla.append(fila)
        partidos[equipo] = df

    clasificacion = pd.DataFrame(filas_tabla)

    # Regla técnica de desempate:
    # puntos, diferencia de goles, goles a favor y equipo.
    for condicion in ["general", "local", "visitante"]:
        orden = clasificacion.sort_values(
            [
                f"puntos_{condicion}",
                f"dg_{condicion}",
                f"gf_{condicion}",
                "equipo",
            ],
            ascending=[False, False, False, True],
            kind="stable",
        )

        posiciones = pd.Series(
            np.arange(1, len(orden) + 1),
            index=orden["equipo"],
        )

        clasificacion[f"posicion_{condicion}"] = (
            clasificacion["equipo"]
            .map(posiciones)
            .astype(int)
        )

    clasificacion = clasificacion.sort_values(
        "posicion_general"
    ).reset_index(drop=True)

    clasificacion["cuarto"] = 0
    rangos = {}

    for cuarto, indices in enumerate(
        np.array_split(np.arange(len(clasificacion)), 4),
        start=1,
    ):
        clasificacion.loc[indices, "cuarto"] = cuarto

        inicio = int(
            clasificacion.loc[indices[0], "posicion_general"]
        )
        fin = int(
            clasificacion.loc[indices[-1], "posicion_general"]
        )

        rangos[cuarto] = f"{inicio}–{fin}"

    return {
        "clasificacion": clasificacion,
        "partidos": partidos,
        "rangos": rangos,
        "avisos": avisos,
    }


def _tabla_rendimiento_cuartos(equipo, condicion, datos):
    clasificacion = datos["clasificacion"]

    cuarto_por_equipo = clasificacion.set_index(
        "equipo"
    )["cuarto"]

    df = datos["partidos"][equipo].copy()
    df = df.loc[df["_condicion"] == condicion].copy()

    df["_cuarto_rival"] = df["_rival_id"].map(
        cuarto_por_equipo
    )

    metricas = {
        "Rem. favor": "shots_favor",
        "Rem. contra": "shots_contra",
        "Rem. totales": "_remates_total",
        "A puerta favor": "a_puerta_favor",
        "A puerta contra": "a_puerta_contra",
        "A puerta totales": "_sot_total",
    }

    filas = []

    for cuarto in range(1, 5):
        muestra = df.loc[df["_cuarto_rival"] == cuarto]

        fila = {
            "Cuarto": cuarto,
            "Puestos": datos["rangos"][cuarto],
            "PJ": len(muestra),
        }

        conteos = []

        for etiqueta, columna in metricas.items():
            valores = muestra[columna].dropna()

            fila[etiqueta] = (
                float(valores.mean())
                if not valores.empty else np.nan
            )
            conteos.append(len(valores))

        minimo = min(conteos)

        if muestra.empty:
            fila["Muestra"] = "Sin partidos"
        elif minimo == 0:
            fila["Muestra"] = "Faltan estadísticas"
        elif minimo < 3:
            fila["Muestra"] = "Muy pequeña"
        else:
            fila["Muestra"] = "3+ datos por métrica"

        # Hace visible si las medias usan menos datos que los PJ.
        fila["N mín. métricas"] = minimo

        filas.append(fila)

    no_clasificados = int(df["_cuarto_rival"].isna().sum())

    return pd.DataFrame(filas), no_clasificados


def generar_analisis_cuartos(
    equipo_local,
    equipo_visitante,
    mapa_equipos,
):
    """
    Nueva sección descriptiva.

    Usa la temporada completa y no altera predicciones existentes.
    Los rivales se agrupan por su clasificación general actual.
    """
    catalogo = _leer_catalogo_contexto()

    equipo_local = str(equipo_local).strip().lower()
    equipo_visitante = str(equipo_visitante).strip().lower()

    def division_de(equipo):
        divisiones = (
            catalogo.loc[
                catalogo["equipo"] == equipo,
                "division"
            ]
            .dropna()
            .drop_duplicates()
        )

        if len(divisiones) != 1:
            raise ValueError(
                f"{equipo}: debe tener una única división "
                "en enlaces_equipos.xlsx."
            )

        return divisiones.iloc[0]

    division_local = division_de(equipo_local)
    division_vis = division_de(equipo_visitante)

    datos_divisiones = {}

    for division in dict.fromkeys([division_local, division_vis]):
        datos_divisiones[division] = _cargar_division_cuartos(
            division, catalogo, mapa_equipos
        )

    datos_local = datos_divisiones[division_local]
    datos_vis = datos_divisiones[division_vis]

    tablas_resumen = []

    for equipo, condicion, division, datos in [
        (equipo_local, "local", division_local, datos_local),
        (equipo_visitante, "visitante", division_vis, datos_vis),
    ]:
        fila = (
            datos["clasificacion"]
            .set_index("equipo")
            .loc[equipo]
        )

        tablas_resumen.append({
            "Equipo": mapa_equipos.get(equipo, equipo),
            "División": division,
            "Condición": condicion.capitalize(),
            "PJ general": int(fila["pj_general"]),
            "Puntos general": int(fila["puntos_general"]),
            "Pos. general": int(fila["posicion_general"]),
            "Cuarto general": int(fila["cuarto"]),
            "PJ condición": int(fila[f"pj_{condicion}"]),
            "Puntos condición": int(fila[f"puntos_{condicion}"]),
            "Pos. condición": int(fila[f"posicion_{condicion}"]),
        })

    tabla_local, sin_clasificar_local = _tabla_rendimiento_cuartos(
        equipo_local, "local", datos_local
    )
    tabla_vis, sin_clasificar_vis = _tabla_rendimiento_cuartos(
        equipo_visitante, "visitante", datos_vis
    )

    avisos = []

    for datos in datos_divisiones.values():
        avisos.extend(datos["avisos"])

    if sin_clasificar_local:
        avisos.append(
            f"Local: {sin_clasificar_local} partidos de casa "
            "sin cuarto de rival."
        )

    if sin_clasificar_vis:
        avisos.append(
            f"Visitante: {sin_clasificar_vis} partidos fuera "
            "sin cuarto de rival."
        )

    misma_division = division_local == division_vis

    # Entre divisiones distintas mostramos los históricos,
    # pero no equiparamos automáticamente sus cuartos.
    cuarto_objetivo_local = None
    cuarto_objetivo_vis = None

    if misma_division:
        posiciones = datos_local["clasificacion"].set_index(
            "equipo"
        )

        cuarto_objetivo_local = int(
            posiciones.loc[equipo_visitante, "cuarto"]
        )
        cuarto_objetivo_vis = int(
            posiciones.loc[equipo_local, "cuarto"]
        )
    else:
        avisos.append(
            "Equipos de divisiones distintas: se muestran sus "
            "históricos por separado, sin resaltar un cuarto "
            "equivalente del próximo rival."
        )

    return {
        "resumen": pd.DataFrame(tablas_resumen),
        "local": tabla_local,
        "visitante": tabla_vis,
        "cuarto_objetivo_local": cuarto_objetivo_local,
        "cuarto_objetivo_visitante": cuarto_objetivo_vis,
        "avisos": list(dict.fromkeys(avisos)),
    }
    
def predecir_goles_desde_entradas(
    entrada_local,
    entrada_visitante,
):
    """
    Modelo de referencia basado en volumen de goles.

    Usa exclusivamente la ventana y condición de cada entrada.
    No añade bonos por rachas ni ajustes de probabilidad posteriores.
    """
    if entrada_local["condicion"] != "local":
        raise ValueError(
            "La entrada local debe corresponder a partidos en casa."
        )

    if entrada_visitante["condicion"] != "visitante":
        raise ValueError(
            "La entrada visitante debe corresponder a partidos fuera."
        )

    if (
        entrada_local["rango_solicitado"]
        != entrada_visitante["rango_solicitado"]
    ):
        raise ValueError(
            "Ambas entradas deben utilizar el mismo rango solicitado."
        )

    n_local = int(entrada_local["n_partidos"])
    n_vis = int(entrada_visitante["n_partidos"])

    if n_local < 1 or n_vis < 1:
        raise ValueError(
            "Se necesita al menos un partido válido por equipo."
        )

    valores = {
        "gf_local": entrada_local["media_goles_favor"],
        "gc_local": entrada_local["media_goles_contra"],
        "gf_vis": entrada_visitante["media_goles_favor"],
        "gc_vis": entrada_visitante["media_goles_contra"],

        "xg_local": entrada_local["media_xg_favor"],
        "xgc_local": entrada_local["media_xg_contra"],
        "xg_vis": entrada_visitante["media_xg_favor"],
        "xgc_vis": entrada_visitante["media_xg_contra"],

        "sot_local": entrada_local["media_tiros_puerta_favor"],
        "sotc_local": entrada_local["media_tiros_puerta_contra"],
        "sot_vis": entrada_visitante["media_tiros_puerta_favor"],
        "sotc_vis": entrada_visitante["media_tiros_puerta_contra"],
    }

    for nombre, valor in valores.items():
        numero = _numero_contexto(valor)

        if numero is None or numero < 0:
            raise ValueError(
                f"Media de goles inválida: {nombre}."
            )

        valores[nombre] = numero  

    # lambda_local = 0.50 * (
    #     valores["gf_local"] + valores["gc_vis"]
    # )

    # lambda_vis = 0.50 * (
    #     valores["gf_vis"] + valores["gc_local"]
    # )
    
    PESO_ATAQUE = 0.6
    PESO_DEFENSA = 0.4

    lambda_local = (
        PESO_ATAQUE * valores["gf_local"]
        + PESO_DEFENSA * valores["gc_vis"]
    )

    lambda_vis = (
        PESO_ATAQUE * valores["gf_vis"]
        + PESO_DEFENSA * valores["gc_local"]
    )

    lambda_local_base_60_40 = lambda_local
    lambda_vis_base_60_40 = lambda_vis

    # --- MEZCLA LAMBDA GOLES 60/40 + LAMBDA xG 60/40 ---
    PESO_LAMBDA_GOLES = 0.70
    PESO_LAMBDA_XG = 0.30

    lambda_xg_local = (
        0.60 * valores["xg_local"]
        + 0.40 * valores["xgc_vis"]
    )

    lambda_xg_vis = (
        0.60 * valores["xg_vis"]
        + 0.40 * valores["xgc_local"]
    )

    lambda_local = (
        PESO_LAMBDA_GOLES * lambda_local_base_60_40
        + PESO_LAMBDA_XG * lambda_xg_local
    )

    lambda_vis = (
        PESO_LAMBDA_GOLES * lambda_vis_base_60_40
        + PESO_LAMBDA_XG * lambda_xg_vis
    )

    prediccion = _mercados_poisson_contexto(
        lambda_local,
        lambda_vis,
    )

    prediccion.update({
        "_modelo": "goles_60_40_xg_30",
        "_lambda_local_base": lambda_local,
        "_lambda_visitante_base": lambda_vis,
        "_lambda_local_base_60_40": lambda_local_base_60_40,
        "_lambda_visitante_base_60_40": lambda_vis_base_60_40,
        "_lambda_xg_local": lambda_xg_local,
        "_lambda_xg_visitante": lambda_xg_vis,
        "_n_local": n_local,
        "_n_visitante": n_vis,
        "_rango": int(entrada_local["rango_solicitado"]),

        "_media_gf_local": valores["gf_local"],
        "_media_gc_local": valores["gc_local"],
        "_media_gf_visitante": valores["gf_vis"],
        "_media_gc_visitante": valores["gc_vis"],
    })
        
    return prediccion