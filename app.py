import streamlit as st
import pandas as pd
import os
from collections import Counter
from scipy.stats import poisson

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Predicción de Partido", layout="wide")
st.title("⚽ Predicción Condicional - Apuestas Inteligentes")

# === NORMALIZACIÓN DE COLUMNAS ===
def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# === CREAR MAPA DE EQUIPOS ===
# def generar_mapa_equipos(carpeta="C:/Users/jose-/OneDrive - MSFT/web scraping/new-stats/"):
#     archivos = [f for f in os.listdir(carpeta) if f.endswith(".xlsx")]
#     mapa = {}
#     for archivo in archivos:
#         ruta = os.path.join(carpeta, archivo)
#         nombre_archivo = archivo.replace(".xlsx", "")

#         try:
#             df = pd.read_excel(ruta)
#             df = normalizar_columnas(df)
#             posibles = list(df["equipo_local"].head(10).str.lower()) + list(df["visitante"].head(10).str.lower())
#             nombre_comun = Counter(posibles).most_common(1)[0][0]
#             mapa[nombre_archivo] = nombre_comun.strip()
#         except Exception as e:
#             print(f"❌ Error con {archivo}: {e}")
#     return mapa

# mapa_equipos = generar_mapa_equipos()

mapa_equipos = {
    "ac-milan": "ac milan",
    "ac-monza": "monza",
    "acf-fiorentina": "fiorentina",
    "adana-demirspor": "adana demirspor",
    "adc-juan-pablo-ii-college": "juan pablo ii",
    "adelaide-united-fc": "adelaide united",
    "afc-ajax": "ajax",
    "afc-bournemouth": "bournemouth",
    "aj-auxerre": "auxerre",
    "al-ahli-saudi-fc": "al-ahli",
    "al-ettifaq-fc": "al-ettifaq",
    "al-fateh-sc": "al fateh",
    "al-fayha-fc": "al fayha",
    "al-hilal-fc": "al-hilal",
    "al-ittihad-fc": "al-ittihad",
    "al-kholood-club": "al kholood",
    "al-nassr-fc": "al-nassr",
    "al-okhdood-club": "al okhdood",
    "al-orobah-fc": "al orubah",
    "al-qadsiah-fc": "al qadisiya",
    "al-raed-fc": "al-raed",
    "al-riyadh-sc": "al riyadh",
    "al-shabab-fc": "al-shabab",
    "al-taawoun-fc": "al-taawon",
    "al-wehda": "al-wehda",
    "alanyaspor": "alanyaspor",
    "albacete-balompie": "albacete",
    "alianza-atletico": "alianza atl.",
    "alianza-fc": "alianza",
    "alianza-lima": "a. lima",
    "alianza-universidad-de-huanuco": "alianza huanuco",
    "almere-city-fc": "almere city",
    "america-de-cali": "america de cali",
    "angers-sco": "angers",
    "antalyaspor": "antalyaspor",
    "argentinos-juniors": "argentinos jrs",
    "arsenal-fc": "arsenal",
    "as-monaco-fc": "monaco",
    "as-roma": "as roma",
    "as-saint-etienne": "st. etienne",
    "asociacion-deportiva-tarma": "ad tarma",
    "aston-villa-fc": "aston villa",
    "atalanta-bc": "atalanta",
    "athletic-bilbao": "ath. bilbao",
    "atlas-fc": "atlas",
    "atletico-bucaramanga": "bucaramanga",
    "atletico-grau": "grau",
    "atletico-junior": "junior",
    "atletico-madrid": "atl. madrid",
    "atletico-nacional": "atl. nacional",
    "atletico-san-luis": "atl. san luis",
    "auckland-fc": "auckland fc",
    "avs-futebol-sad": "afs",
    "ayacucho-fc": "ayacucho",
    "az-alkmaar": "alkmaar",
    "bayer-leverkusen": "leverkusen",
    "bayern-munich": "bayern",
    "benfica": "benfica",
    "besiktas-jk": "besiktas",
    "blackburn-rovers-fc": "blackburn",
    "boavista-fc": "boavista",
    "bodrumspor": "bodrumspor",
    "bologna-fc-1909": "bologna",
    "borussia-dortmund": "dortmund",
    "borussia-monchengladbach": "monchengladbach",
    "botafogo-de-futebol-e-regatas": "botafogo rj",
    "boyaca-chico-fc": "chico",
    "braga": "braga",
    "brentford-fc": "brentford",
    "brighton-hove-albion-fc": "brighton",
    "brisbane-roar-fc": "brisbane roar",
    "bristol-city-fc": "bristol city",
    "bryne-fk": "bryne",
    "burgos-cf": "burgos cf",
    "burnley-fc": "burnley",
    "ca-osasuna": "osasuna",
    "cadiz-cf": "cadiz",
    "cagliari-calcio": "cagliari",
    "cardiff-city-fc": "cardiff",
    "casa-pia-ac": "casa pia",
    "caykur-rizespor": "rizespor",
    "cd-castellon": "castellon",
    "cd-eldense": "eldense",
    "cd-guadalajara": "guadalajara",
    "cd-la-equidad": "la equidad",
    "cd-leganes": "leganes",
    "cd-mirandes": "mirandes",
    "cd-nacional": "nacional",
    "cd-tenerife": "tenerife",
    "ceara-sporting-club": "ceara",
    "celta-vigo": "celta vigo",
    "central-coast-mariners-fc": "central coast mariners",
    "cercle-brugge-ksv": "cercle brugge",
    "cf-estrela-da-amadora": "estrela",
    "cf-monterrey": "monterrey",
    "cf-pachuca": "pachuca",
    "chelsea-fc": "chelsea",
    "club-america": "club america",
    "club-atletico-aldosivi": "aldosivi",
    "club-atletico-banfield": "banfield",
    "club-atletico-barracas-central": "barracas central",
    "club-atletico-belgrano": "belgrano",
    "club-atletico-boca-juniors": "boca juniors",
    "club-atletico-central-cordoba": "central cordoba",
    "club-atletico-huracan": "huracan",
    "club-atletico-independiente": "independiente",
    "club-atletico-lanus": "lanus",
    "club-atletico-newells-old-boys": "newells old boys",
    "club-atletico-platense": "platense",
    "club-atletico-river-plate": "river plate",
    "club-atletico-rosario-central": "rosario",
    "club-atletico-sarmiento-junin": "sarmiento junin",
    "club-atletico-talleres": "talleres cordoba",
    "club-atletico-tigre": "tigre",
    "club-atletico-tucuman": "atl. tucuman",
    "club-atletico-union-de-santa-fe": "union santa fe",
    "club-atletico-velez-sarsfield": "velez sarsfield",
    "club-brugge-kv": "club brugge",
    "club-de-gimnasia-la-plata": "gimnasia l.p.",
    "club-estudiantes-de-la-plata": "estudiantes",
    "club-leon": "leon",
    "club-necaxa": "necaxa",
    "club-puebla": "puebla",
    "club-sportivo-cienciano": "cienciano",
    "club-sportivo-independiente-rivadavia": "ind. rivadavia",
    "club-tijuana": "tijuana",
    "club-universitario-de-deportes": "u. de deportes",
    "clube-atletico-mineiro": "atletico-mg",
    "clube-de-regatas-do-flamengo": "flamengo",
    "comerciantes-unidos": "comerciantes unidos",
    "como-1907": "como",
    "cordoba-cf": "cordoba",
    "coventry-city-fc": "coventry",
    "cr-vasco-da-gama": "vasco",
    "cruz-azul": "cruz azul",
    "cruzeiro-esporte-clube": "cruzeiro",
    "crystal-palace-fc": "crystal palace",
    "cusco-fc": "cusco",
    "damac-fc": "damac",
    "darmstadt-98": "darmstadt",
    "defensa-y-justicia": "defensa y justicia",
    "deportes-tolima": "tolima",
    "deportivo-alaves": "alaves",
    "deportivo-binacional": "binacional",
    "deportivo-cali": "dep. cali",
    "deportivo-de-la-coruna": "la coruna",
    "deportivo-garcilaso": "deportivo garcilaso",
    "deportivo-independiente-medellin": "ind. medellin",
    "deportivo-pasto": "pasto",
    "deportivo-pereira": "pereira",
    "deportivo-riestra": "dep. riestra",
    "deportivo-toluca-fc": "toluca",
    "derby-county-fc": "derby",
    "eintracht-braunschweig": "braunschweig",
    "eintracht-frankfurt": "frankfurt",
    "elche-cf": "elche",
    "empoli-fc": "empoli",
    "envigado-fc": "envigado",
    "esporte-clube-bahia": "bahia",
    "esporte-clube-juventude": "juventude",
    "esporte-clube-vitoria": "vitoria",
    "everton-fc": "everton",
    "eyupspor": "eyupspor",
    "famalicao": "famalicao",
    "fbc-melgar": "melgar",
    "fc-arouca": "arouca",
    "fc-augsburg": "augsburg",
    "fc-barcelona": "barcelona",
    "fc-cartagena": "cartagena",
    "fc-groningen": "groningen",
    "fc-heidenheim": "heidenheim",
    "fc-juarez": "juarez",
    "fc-kaiserslautern": "kaiserslautern",
    "fc-koln": "fc koln",
    "fc-magdeburg": "magdeburg",
    "fc-nantes": "nantes",
    "fc-nurnberg": "nurnberg",
    "fc-porto": "fc porto",
    "fc-st-pauli": "st. pauli",
    "fc-twente": "twente",
    "fc-utrecht": "utrecht",
    "fcv-dender-eh": "dender",
    "fenerbahce-sk": "fenerbahce",
    "feyenoord-rotterdam": "feyenoord",
    "fk-bodo-glimt": "bodo/glimt",
    "fk-haugesund": "haugesund",
    "fluminense-fc": "fluminense",
    "fortaleza-ceif": "fortaleza",
    "fortaleza-esporte-clube": "fortaleza",
    "fortuna-dusseldorf": "dusseldorf",
    "fortuna-sittard": "sittard",
    "fredrikstad-fk": "fredrikstad",
    "fulham-fc": "fulham",
    "galatasaray-sk": "galatasaray",
    "gaziantep-fk": "gaziantep",
    "gd-estoril-praia": "estoril",
    "genoa-cfc": "genoa",
    "getafe-cf": "getafe",
    "gil-vicente": "gil vicente",
    "girona-fc": "girona",
    "go-ahead-eagles": "g.a. eagles",
    "godoy-cruz": "godoy cruz",
    "goztepe-sk": "goztepe",
    "granada-cf": "granada",
    "gremio-football-porto-alagrense": "gremio",
    "greuther-furth": "furth",
    "ham-kam": "hamkam",
    "hamburger-sv": "hamburger sv",
    "hannover-96": "hannover",
    "hatayspor": "hatayspor",
    "hellas-verona-fc": "verona",
    "heracles-almelo": "heracles",
    "hertha-berlin": "hertha",
    "hoffenheim": "hoffenheim",
    "holstein-kiel": "kiel",
    "hull-city-fc": "hull",
    "independiente-santa-fe": "santa fe",
    "instituto-atletico-central-cordoba": "instituto",
    "inter-milan": "inter",
    "ipswich-town-fc": "ipswich",
    "istanbul-basaksehir-fk": "basaksehir",
    "jahn-regensburg": "regensburg",
    "juventus-fc": "juventus",
    "k-beerschot-va": "beerschot va",
    "kaa-gent": "gent",
    "karlsruher-sc": "karlsruher",
    "kasimpasa-sk": "kasimpasa",
    "kayserispor": "kayserispor",
    "kfum-kameratene-oslo": "kfum oslo",
    "khaleej-fc": "al khaleej",
    "konyaspor": "konyaspor",
    "krc-genk": "genk",
    "kristiansund-bk": "kristiansund",
    "kv-kortrijk": "kortrijk",
    "kv-mechelen": "kv mechelen",
    "kvc-westerlo": "westerlo",
    "le-havre-ac": "le havre",
    "leeds-united-fc": "leeds",
    "leicester-city-fc": "leicester",
    "levante-ud": "levante",
    "lille-osc": "lille",
    "liverpool-fc": "liverpool",
    "llaneros-fc": "llaneros",
    "los-chankas-cyc": "los chankas",
    "luton-town-fc": "luton",
    "macarthur-fc": "macarthur fc",
    "mainz-05": "mainz",
    "malaga-cf": "malaga",
    "manchester-city-fc": "man city",
    "manchester-united-fc": "man utd",
    "mazatlan-fc": "mazatlan fc",
    "melbourne-city-fc": "melbourne city",
    "melbourne-victory-fc": "melbourne victory",
    "middlesbrough-fc": "middlesbrough",
    "millonarios-fc": "millonarios",
    "millwall-fc": "millwall",
    "mirassol-fc": "mirassol",
    "molde-fk": "molde",
    "montpellier-hsc": "montpellier",
    "moreirense-fc": "moreirense",
    "nac-breda": "nac breda",
    "nec-nijmegen": "nijmegen",
    "newcastle-jets-fc": "newcastle jets",
    "newcastle-united-fc": "newcastle",
    "norwich-city-fc": "norwich",
    "nottingham-forest-fc": "nottm forest",
    "ogc-nice": "nice",
    "oh-leuven": "leuven",
    "olympique-de-marseille": "marseille",
    "olympique-lyonnais": "lyon",
    "once-caldas": "once caldas",
    "oxford-united-fc": "oxford utd",
    "paris-saint-germain-fc": "psg",
    "parma-calcio-1913": "parma",
    "pec-zwolle": "zwolle",
    "perth-glory-fc": "perth glory",
    "plymouth-argyle-fc": "plymouth",
    "portsmouth-fc": "portsmouth",
    "preston-north-end-fc": "preston",
    "preussen-munster": "munster",
    "psv-eindhoven": "psv",
    "queens-park-rangers-fc": "qpr",
    "queretaro-fc": "queretaro",
    "racing-club-de-avellaneda": "racing club",
    "racing-de-ferrol": "racing club ferrol",
    "racing-de-santander": "racing santander",
    "rayo-vallecano": "rayo vallecano",
    "rb-leipzig": "rb leipzig",
    "rc-lens": "lens",
    "rc-strasbourg-alsace": "strasbourg",
    "rcd-espanyol": "espanyol",
    "rcd-mallorca": "mallorca",
    "real-betis-balompie": "betis",
    "real-madrid-cf": "real madrid",
    "real-oviedo": "r. oviedo",
    "real-sociedad": "real sociedad",
    "real-valladolid": "valladolid",
    "real-zaragoza": "zaragoza",
    "red-bull-bragantino": "bragantino",
    "rio-ave-fc": "rio ave",
    "rionegro-aguilas": "aguilas",
    "rkc-waalwijk": "waalwijk",
    "rosenborg-bk": "rosenborg",
    "royal-antwerp-fc": "antwerp",
    "royal-charleroi-sc": "charleroi",
    "rsc-anderlecht": "anderlecht",
    "ru-saint-gilloise": "union sg",
    "samsunspor": "samsunspor",
    "san-lorenzo-de-almagro": "san lorenzo",
    "san-martin-de-san-juan": "san martin s.j.",
    "sandefjord-fotball": "sandefjord",
    "santa-clara": "santa clara",
    "santos-fc": "santos",
    "santos-laguna": "santos laguna",
    "sao-paulo-fc": "sao paulo",
    "sarpsborg-08-ff": "sarpsborg 08",
    "sc-farense": "farense",
    "sc-freiburg": "freiburg",
    "sc-heerenveen": "heerenveen",
    "sc-paderborn": "paderborn",
    "schalke-04": "schalke",
    "sd-eibar": "eibar",
    "sd-huesca": "huesca",
    "sevilla-fc": "sevilla",
    "sheffield-united-fc": "sheff utd",
    "sheffield-wednesday-fc": "sheff wed",
    "sint-truidense-vv": "st. truiden",
    "sivasspor": "sivasspor",
    "sk-brann": "brann",
    "sociedade-esportiva-palmeiras": "palmeiras",
    "southampton-fc": "southampton",
    "sparta-rotterdam": "sparta rotterdam",
    "sport-boys": "sport boys",
    "sport-club-corinthians-paulista": "corinthians",
    "sport-club-do-recife": "sport recife",
    "sport-club-internacional": "internacional",
    "sport-huancayo": "huancayo",
    "sporting-cp": "sporting",
    "sporting-cristal": "sporting cristal",
    "sporting-de-gijon": "gijon",
    "ss-lazio": "lazio",
    "ssc-napoli": "napoli",
    "ssv-ulm-1846": "ulm",
    "stade-brestois-29": "brest",
    "stade-de-reims": "reims",
    "stade-rennais-fc": "rennes",
    "standard-liege": "st. liege",
    "stoke-city-fc": "stoke",
    "stromsgodset": "stromsgodset",
    "sunderland-afc": "sunderland",
    "sv-elversberg": "elversberg",
    "swansea-city-afc": "swansea",
    "sydney-fc": "sydney fc",
    "tigres-uanl": "tigres",
    "torino-fc": "torino",
    "tottenham-hotspur-fc": "tottenham",
    "toulouse-fc": "toulouse",
    "trabzonspor": "trabzonspor",
    "tromso-il": "tromso",
    "ud-almeria": "almeria",
    "ud-las-palmas": "las palmas",
    "udinese-calcio": "udinese",
    "unam": "u.n.a.m.",
    "union-berlin": "union berlin",
    "union-magdalena": "u. magdalena",
    "universidad-tecnica-de-cajamarca": "cajamarca",
    "us-lecce": "lecce",
    "valencia-cf": "valencia",
    "valerenga-fotball": "valerenga",
    "venezia-fc": "venezia",
    "vfb-stuttgart": "stuttgart",
    "vfl-bochum": "bochum",
    "vfl-wolfsburg": "wolfsburg",
    "viking-fk": "viking",
    "villarreal-cf": "villarreal",
    "vitoria-de-guimaraes": "guimaraes",
    "watford-fc": "watford",
    "wellington-phoenix-fc": "wellington phoenix",
    "werder-bremen": "bremen",
    "west-bromwich-albion-fc": "west brom",
    "west-ham-united-fc": "west ham",
    "western-sydney-wanderers-fc": "ws wanderers",
    "western-united-fc": "western united",
    "willem-ii": "willem ii",
    "wolverhampton-wanderers-fc": "wolves"
}

# === CARGAR DATOS DEL EQUIPO ===
def cargar_datos(equipo_archivo, condicion="local", n=5):
    archivo = f"new-stats/{equipo_archivo}.xlsx"
    try:
        df = pd.read_excel(archivo)
        df = normalizar_columnas(df)

        columnas_numericas = [
            "goles_local", "goles_visitante", "xg_favor", "shots_favor", "a_puerta_favor",
            "1t_goles_favor", "2t_goles_favor", "1t_goles_contra", "2t_goles_contra"
        ]
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        nombre_equipo = mapa_equipos.get(equipo_archivo, equipo_archivo.replace("-", " ").lower())
        if condicion == "local":
            df_filtrado = df[df["equipo_local"].str.lower().str.contains(nombre_equipo)]
        else:
            df_filtrado = df[df["visitante"].str.lower().str.contains(nombre_equipo)]

        return df_filtrado.tail(n)

    except Exception as e:
        st.error(f"❌ Error al cargar datos para {equipo_archivo}: {e}")
        return pd.DataFrame()

# === CÁLCULO AJUSTADO POISSON ===
def calcular_lambda(df, col_goles, col_xg, partidos_recientes = 5):
    # Lambda base Poisson con xG promedio
    xg_prom = df[col_xg].mean()

    # Efectividad goleadora: goles / xG
    efectividad = (df[col_goles].sum() / df[col_xg].sum()) if df[col_xg].sum() > 0 else 1

    # Forma reciente (últimos n partidos)
    df_recientes = df.sort_values(by="fecha", ascending=False).head(partidos_recientes)
    xg_forma = df_recientes[col_xg].mean()
    goles_forma = df_recientes[col_goles].mean()
    efectividad_forma = (df_recientes[col_goles].sum() / df_recientes[col_xg].sum()) if df_recientes[col_xg].sum() > 0 else 1

    # Pesos (puedes ajustar estos valores según el modelo)
    peso_xg = 0.4
    peso_efectividad = 0.3
    peso_forma = 0.3

    lambda_total = (
        peso_xg * xg_prom +
        peso_efectividad * xg_prom * efectividad +
        peso_forma * xg_forma * efectividad_forma
    )

    return lambda_total

def probabilidad_poisson(lmbda, min_goles=1):
    return round(1 - poisson.cdf(min_goles - 1, lmbda), 3)

# === DECISIÓN AUTOMÁTICA ===
def seleccionar_df(df):
    ultimos_5 = df.tail(5)
    total = df

    precision_5 = abs(ultimos_5["goles_local"].mean() - ultimos_5["xg_favor"].mean())
    precision_total = abs(total["goles_local"].mean() - total["xg_favor"].mean())

    return ultimos_5 if precision_5 < precision_total else total

# === CALCULAR ESTADÍSTICAS ===
def calcular_estadisticas(df, tipo):
    stats = {
        "Prom. Goles": round(df["goles_local"].mean(), 2) if tipo == "local" else round(df["goles_visitante"].mean(), 2),
        "Prom. xG": round(df["xg_favor"].mean(), 2),
        "Prom. Remates": round(df["shots_favor"].mean(), 1),
        "A puerta": round(df["a_puerta_favor"].mean(), 1),
    }
    return stats

def probabilidad_over_total(lambda_local, lambda_visitante, limite):
    lambda_total = lambda_local + lambda_visitante
    return round((1 - sum(poisson.pmf(k, lambda_total) for k in range(int(limite) + 1))) * 100, 1)

# === FUNCIÓN PRINCIPAL ===
def calcular_probabilidades_equipo(df_local, df_visitante):
    df_local = seleccionar_df(df_local)
    df_visitante = seleccionar_df(df_visitante)

    # Lambdas para Poisson ajustados
    lambda_local = calcular_lambda(df_local, "goles_local", "xg_favor")
    lambda_visitante = calcular_lambda(df_visitante, "goles_visitante", "xg_favor")

    # Por tiempos
    lambda_local_1t = calcular_lambda(df_local, "1t_goles_favor", "xg_favor")
    lambda_local_2t = calcular_lambda(df_local, "2t_goles_favor", "xg_favor")
    lambda_visitante_1t = calcular_lambda(df_visitante, "1t_goles_favor", "xg_favor")
    lambda_visitante_2t = calcular_lambda(df_visitante, "2t_goles_favor", "xg_favor")

    resultados = {
        "Prob. Local marca": probabilidad_poisson(lambda_local)*100,
        "Prob. Visitante marca": probabilidad_poisson(lambda_visitante)*100,
        "Prob. BTTS": round(probabilidad_poisson(lambda_local) * probabilidad_poisson(lambda_visitante), 3)*100,

        "Prob. Local 1T": probabilidad_poisson(lambda_local_1t)*100,
        "Prob. Visitante 1T": probabilidad_poisson(lambda_visitante_1t)*100,
        "Prob. Gol 1T total": round(probabilidad_poisson(lambda_local_1t + lambda_visitante_1t), 3)*100,

        "Prob. Local 2T": probabilidad_poisson(lambda_local_2t)*100,
        "Prob. Visitante 2T": probabilidad_poisson(lambda_visitante_2t)*100,
        "Prob. Gol 2T total": round(probabilidad_poisson(lambda_local_2t + lambda_visitante_2t), 3)*100,

        "Prom. Remates Local": round(df_local["shots_favor"].mean(), 1),
        "Prom. Remates Visitante": round(df_visitante["shots_favor"].mean(), 1),
        "Total Remates": round((df_local["shots_favor"].mean() + df_visitante["shots_favor"].mean()), 1),

        "A puerta Local": round(df_local["a_puerta_favor"].mean(), 1),
        "A puerta Visitante": round(df_visitante["a_puerta_favor"].mean(), 1),
        "Total A puerta": round((df_local["a_puerta_favor"].mean() + df_visitante["a_puerta_favor"].mean()), 1),

        "Prob. Over 1.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 1.5),
        "Prob. Over 2.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 2.5)
    }

    return resultados

# === EQUIPOS DISPONIBLES ===
archivos = [f.replace(".xlsx", "") for f in os.listdir("new-stats/") if f.endswith(".xlsx")]
equipos_disponibles = sorted(archivos)

# === UI SELECCIÓN ===
col1, col2 = st.columns(2)
with col1:
    equipo_local = st.selectbox("🔵 Equipo LOCAL", equipos_disponibles)
with col2:
    equipo_visitante = st.selectbox("🔴 Equipo VISITANTE", equipos_disponibles)

# === CÁLCULOS DE PROBABILIDADES ===
if equipo_local and equipo_visitante:
    # Cargar datos históricos
    df_local = cargar_datos(equipo_local, "local", 5)
    df_visitante = cargar_datos(equipo_visitante, "visitante", 5)

    # Calcular estadísticas de los equipos
    stats_local = calcular_estadisticas(df_local, "local")
    stats_visitante = calcular_estadisticas(df_visitante, "visitante")

    # Calcular probabilidades
    resultados = calcular_probabilidades_equipo(df_local, df_visitante)

    # Mostrar los resultados en Streamlit
    nombre_local = equipo_local.replace("-", " ").title()
    nombre_visitante = equipo_visitante.replace("-", " ").title()

    st.markdown("## 📊 Estadísticas Generales")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"### 🔵 {nombre_local}")
        for key, val in stats_local.items():
            st.metric(key, f"{val}")
    with col4:
        st.markdown(f"### 🔴 {nombre_visitante}")
        for key, val in stats_visitante.items():
            st.metric(key, f"{val}")

    st.markdown("## 🔁 Probabilidades por Mitades (Condicionales)")
    colm1, colm2 = st.columns(2)
    with colm1:
        st.metric("Local marca", f"{round(resultados['Prob. Local marca'], 1)}%")
        st.metric("Local marca 1T", f"{round(resultados['Prob. Local 1T'], 1)}%")
        st.metric("Local marca 2T", f"{round(resultados['Prob. Local 2T'], 1)}%")
    with colm2:
        st.metric("Visitante marca", f"{round(resultados['Prob. Visitante marca'], 1)}%")
        st.metric("Visitante marca 1T", f"{round(resultados['Prob. Visitante 1T'], 1)}%")
        st.metric("Visitante marca 2T", f"{round(resultados['Prob. Visitante 2T'], 1)}%")

    st.markdown("## 🔥 Ambos Marcan - Probabilidad Condicional")
    st.metric("BTTS Condicional", f"{round(resultados['Prob. BTTS'], 1)}%")

    st.markdown("## 🎯 Remates Totales Condicionales")
    colm1, colm2 = st.columns(2)
    with colm1:
        st.metric("Remates totales esperados", f"{resultados['Total Remates']}")       
    with colm2:
        st.metric("Remates a puerta esperados", f"{resultados['Total A puerta']}")
    

    st.markdown("## 📈 Probabilidades de Over Goles")
    st.metric("Over 1.5 Goles", f"{round(resultados['Prob. Over 1.5 Goles'], 1)}%")
    st.metric("Over 2.5 Goles", f"{round(resultados['Prob. Over 2.5 Goles'], 1)}%")
else:
    st.warning("Selecciona un partido para ver el análisis.")
