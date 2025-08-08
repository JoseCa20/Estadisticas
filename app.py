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
    "aberdeen-fc": "aberdeen",
"ac-milan": "ac milan",
"ac-monza": "monza",
"acf-fiorentina": "fiorentina",
"adana-demirspor": "adana demirspor",
"adc-juan-pablo-ii-college": "juan pablo ii",
"adelaide-united-fc": "adelaide united",
"aek-athens-fc": "aek",
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
"aris-thessaloniki-fc": "aris",
"arsenal-fc": "arsenal",
"as-monaco-fc": "monaco",
"as-roma": "as roma",
"as-saint-etienne": "st. etienne",
"asociacion-deportiva-tarma": "ad tarma",
"asteras-tripolis-fc": "asteras t.",
"aston-villa-fc": "aston villa",
"atalanta-bc": "atalanta",
"athens-kallithea-fc": "athens kallithea",
"athletic-bilbao": "ath. bilbao",
"atlanta-united-fc": "atlanta united",
"atlas-fc": "atlas",
"atletico-bucaramanga": "bucaramanga",
"atletico-grau": "grau",
"atletico-junior": "junior",
"atletico-madrid": "atl. madrid",
"atletico-nacional": "atl. nacional",
"atletico-san-luis": "atl. san luis",
"atromitos-fc": "atromitos",
"auckland-fc": "auckland fc",
"audax-italiano": "a. italiano",
"austin-fc": "austin fc",
"austria-vienna": "austria vienna",
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
"bohemians-1905": "bohemians",
"bologna-fc-1909": "bologna",
"borussia-dortmund": "dortmund",
"borussia-monchengladbach": "monchengladbach",
"boston-river": "boston river",
"botafogo-de-futebol-e-regatas": "botafogo rj",
"boyaca-chico-fc": "chico",
"braga": "braga",
"brentford-fc": "brentford",
"brighton-hove-albion-fc": "brighton",
"brisbane-roar-fc": "brisbane roar",
"bristol-city-fc": "bristol city",
"bryne-fk": "bryne",
"bsc-young-boys": "young boys",
"burgos-cf": "burgos cf",
"burnley-fc": "burnley",
"bw-linz": "bw linz",
"ca-osasuna": "osasuna",
"cadiz-cf": "cadiz",
"cagliari-calcio": "cagliari",
"cardiff-city-fc": "cardiff",
"casa-pia-ac": "casa pia",
"caykur-rizespor": "rizespor",
"cd-castellon": "castellon",
"cd-cobresal": "cobresal",
"cd-eldense": "eldense",
"cd-guadalajara": "guadalajara",
"cd-huachipato": "huachipato",
"cd-la-equidad": "la equidad",
"cd-leganes": "leganes",
"cd-mirandes": "mirandes",
"cd-nacional": "nacional",
"cd-palestino": "palestino",
"cd-tenerife": "tenerife",
"cd-universidad-catolica": "u. catolica",
"ceara-sporting-club": "ceara",
"celta-vigo": "celta vigo",
"celtic-fc": "celtic",
"central-coast-mariners-fc": "central coast mariners",
"cercle-brugge-ksv": "cercle brugge",
"ceske-budejovice": "ceske budejovice",
"cf-estrela-da-amadora": "estrela",
"cf-monterrey": "monterrey",
"cf-pachuca": "pachuca",
"charlotte-fc": "charlotte",
"chelsea-fc": "chelsea",
"chicago-fire-fc": "chicago fire",
"club-america": "club america",
"club-atletico-aldosivi": "aldosivi",
"club-atletico-banfield": "banfield",
"club-atletico-barracas-central": "barracas central",
"club-atletico-belgrano": "belgrano",
"club-atletico-boca-juniors": "boca juniors",
"club-atletico-central-cordoba": "central cordoba",
"club-atletico-cerro": "cerro ca",
"club-atletico-huracan": "huracan",
"club-atletico-independiente": "independiente",
"club-atletico-lanus": "lanus",
"club-atletico-newells-old-boys": "newells old boys",
"club-atletico-platense": "platense",
"club-atletico-progreso": "progreso",
"club-atletico-river-plate": "river plate",
"club-atletico-rosario-central": "rosario",
"club-atletico-sarmiento-junin": "sarmiento junin",
"club-atletico-talleres": "talleres cordoba",
"club-atletico-tigre": "tigre",
"club-atletico-tucuman": "atl. tucuman",
"club-atletico-union-de-santa-fe": "union santa fe",
"club-atletico-velez-sarsfield": "velez sarsfield",
"club-brugge-kv": "club brugge",
"club-de-foot-montreal": "cf montreal",
"club-de-gimnasia-la-plata": "gimnasia l.p.",
"club-estudiantes-de-la-plata": "estudiantes",
"club-leon": "leon",
"club-nacional-de-football": "nacional",
"club-necaxa": "necaxa",
"club-plaza-colonia-de-deportes": "plaza colonia",
"club-puebla": "puebla",
"club-sportivo-cienciano": "cienciano",
"club-sportivo-independiente-rivadavia": "ind. rivadavia",
"club-tijuana": "tijuana",
"club-universidad-de-chile": "u. de chile",
"club-universitario-de-deportes": "u. de deportes",
"clube-atletico-mineiro": "atletico-mg",
"clube-de-regatas-do-flamengo": "flamengo",
"colo-colo": "colo colo",
"colorado-rapids": "colorado rapids",
"columbus-crew-sc": "columbus crew",
"comerciantes-unidos": "comerciantes unidos",
"como-1907": "como",
"coquimbo-unido": "coquimbo",
"cordoba-cf": "cordoba",
"coventry-city-fc": "coventry",
"cr-vasco-da-gama": "vasco",
"cruz-azul": "cruz azul",
"cruzeiro-esporte-clube": "cruzeiro",
"crystal-palace-fc": "crystal palace",
"cusco-fc": "cusco",
"damac-fc": "damac",
"danubio-fc": "danubio",
"darmstadt-98": "darmstadt",
"dc-united": "dc united",
"defensa-y-justicia": "defensa y justicia",
"defensor-sporting": "defensor sp.",
"deportes-iquique": "deportes iquique",
"deportes-la-serena": "la serena",
"deportes-limache": "limache",
"deportes-tolima": "tolima",
"deportivo-alaves": "alaves",
"deportivo-binacional": "binacional",
"deportivo-cali": "dep. cali",
"deportivo-de-la-coruna": "la coruna",
"deportivo-garcilaso": "deportivo garcilaso",
"deportivo-independiente-medellin": "ind. medellin",
"deportivo-nublense": "nublense",
"deportivo-pasto": "pasto",
"deportivo-pereira": "pereira",
"deportivo-riestra": "dep. riestra",
"deportivo-toluca-fc": "toluca",
"derby-county-fc": "derby",
"dundee-fc": "dundee fc",
"dundee-united-fc": "dundee utd",
"eintracht-braunschweig": "braunschweig",
"eintracht-frankfurt": "frankfurt",
"elche-cf": "elche",
"empoli-fc": "empoli",
"envigado-fc": "envigado",
"esporte-clube-bahia": "bahia",
"esporte-clube-juventude": "juventude",
"esporte-clube-vitoria": "vitoria",
"everton-de-vina-del-mar": "everton",
"everton-fc": "everton",
"eyupspor": "eyupspor",
"famalicao": "famalicao",
"fbc-melgar": "melgar",
"fc-arouca": "arouca",
"fc-augsburg": "augsburg",
"fc-banik-ostrava": "ostrava",
"fc-barcelona": "barcelona",
"fc-basel": "basel",
"fc-cartagena": "cartagena",
"fc-cincinnati": "cincinnati",
"fc-dallas": "fc dallas",
"fc-groningen": "groningen",
"fc-heidenheim": "heidenheim",
"fc-hradec-kralove": "hradec kralove",
"fc-juarez": "juarez",
"fc-kaiserslautern": "kaiserslautern",
"fc-koln": "fc koln",
"fc-lausanne-sport": "lausanne",
"fc-lugano": "lugano",
"fc-luzern": "luzern",
"fc-magdeburg": "magdeburg",
"fc-nantes": "nantes",
"fc-nurnberg": "nurnberg",
"fc-porto": "fc porto",
"fc-sion": "sion",
"fc-slovacko": "slovacko",
"fc-slovan-liberec": "liberec",
"fc-st-gallen": "st. gallen",
"fc-st-pauli": "st. pauli",
"fc-twente": "twente",
"fc-utrecht": "utrecht",
"fc-viktoria-plzen": "plzen",
"fc-winterthur": "winterthur",
"fc-zurich": "zurich",
"fcv-dender-eh": "dender",
"fenerbahce-sk": "fenerbahce",
"feyenoord-rotterdam": "feyenoord",
"fk-bodo-glimt": "bodo/glimt",
"fk-dukla-prague": "dukla prague",
"fk-haugesund": "haugesund",
"fk-jablonec": "jablonec",
"fk-mlada-boleslav": "mlada boleslav",
"fk-pardubice": "pardubice",
"fk-teplice": "teplice",
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
"grasshopper-club-zurich": "grasshoppers",
"grazer-ak": "grazer ak",
"gremio-football-porto-alagrense": "gremio",
"greuther-furth": "furth",
"ham-kam": "hamkam",
"hamburger-sv": "hamburger sv",
"hannover-96": "hannover",
"hatayspor": "hatayspor",
"heart-of-midlothian-fc": "hearts",
"hellas-verona-fc": "verona",
"heracles-almelo": "heracles",
"hertha-berlin": "hertha",
"hibernian-fc": "hibernian",
"hoffenheim": "hoffenheim",
"holstein-kiel": "kiel",
"houston-dynamo": "houston dynamo",
"hull-city-fc": "hull",
"independiente-santa-fe": "santa fe",
"instituto-atletico-central-cordoba": "instituto",
"inter-miami-cf": "inter miami",
"inter-milan": "inter",
"ipswich-town-fc": "ipswich",
"istanbul-basaksehir-fk": "basaksehir",
"jahn-regensburg": "regensburg",
"juventud-de-las-piedras": "juventud",
"juventus-fc": "juventus",
"k-beerschot-va": "beerschot va",
"kaa-gent": "gent",
"karlsruher-sc": "karlsruher",
"kasimpasa-sk": "kasimpasa",
"kayserispor": "kayserispor",
"kfum-kameratene-oslo": "kfum oslo",
"khaleej-fc": "al khaleej",
"kilmarnock-fc": "kilmarnock",
"konyaspor": "konyaspor",
"krc-genk": "genk",
"kristiansund-bk": "kristiansund",
"kv-kortrijk": "kortrijk",
"kv-mechelen": "kv mechelen",
"kvc-westerlo": "westerlo",
"lamia-fc": "lamia",
"lask": "lask",
"le-havre-ac": "le havre",
"leeds-united-fc": "leeds",
"leicester-city-fc": "leicester",
"levadiakos-fc": "levadiakos",
"levante-ud": "levante",
"lille-osc": "lille",
"liverpool-fc-montevideo": "liverpool m.",
"liverpool-fc": "liverpool",
"llaneros-fc": "llaneros",
"los-angeles-fc": "los angeles fc",
"los-angeles-galaxy": "los angeles galaxy",
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
"mfk-karvina": "karvina",
"middlesbrough-fc": "middlesbrough",
"millonarios-fc": "millonarios",
"millwall-fc": "millwall",
"minnesota-united-fc": "minnesota",
"miramar-misiones": "miramar",
"mirassol-fc": "mirassol",
"molde-fk": "molde",
"montevideo-city-torque": "montevideo city",
"montevideo-wanderers-fc": "wanderers",
"montpellier-hsc": "montpellier",
"moreirense-fc": "moreirense",
"motherwell-fc": "motherwell",
"nac-breda": "nac breda",
"nashville-sc": "nashville sc",
"nec-nijmegen": "nijmegen",
"new-england-revolution": "new england revolution",
"new-york-city-fc": "new york city",
"new-york-red-bulls": "new york red bulls",
"newcastle-jets-fc": "newcastle jets",
"newcastle-united-fc": "newcastle",
"norwich-city-fc": "norwich",
"nottingham-forest-fc": "nottm forest",
"o-higgins-fc": "o'higgins",
"ofi-crete-fc": "ofi crete",
"ogc-nice": "nice",
"oh-leuven": "leuven",
"olympiacos-fc": "olympiacos",
"olympique-de-marseille": "marseille",
"olympique-lyonnais": "lyon",
"once-caldas": "once caldas",
"orlando-city-sc": "orlando city",
"oxford-united-fc": "oxford utd",
"panathinaikos-fc": "panathinaikos",
"panetolikos-fc": "panetolikos",
"panserraikos-fc": "panserraikos",
"paok-fc": "paok",
"paris-saint-germain-fc": "psg",
"parma-calcio-1913": "parma",
"pec-zwolle": "zwolle",
"penarol": "penarol",
"perth-glory-fc": "perth glory",
"philadelphia-union": "philadelphia union",
"plymouth-argyle-fc": "plymouth",
"portland-timbers": "portland timbers",
"portsmouth-fc": "portsmouth",
"preston-north-end-fc": "preston",
"preussen-munster": "munster",
"psv-eindhoven": "psv",
"queens-park-rangers-fc": "qpr",
"queretaro-fc": "queretaro",
"racing-club-de-avellaneda": "racing club",
"racing-club-de-montevideo": "racing montevideo",
"racing-de-ferrol": "racing club ferrol",
"racing-de-santander": "racing santander",
"rangers-fc": "rangers",
"rapid-vienna": "sk rapid",
"rayo-vallecano": "rayo vallecano",
"rb-leipzig": "rb leipzig",
"rc-lens": "lens",
"rc-strasbourg-alsace": "strasbourg",
"rcd-espanyol": "espanyol",
"rcd-mallorca": "mallorca",
"real-betis-balompie": "betis",
"real-madrid-cf": "real madrid",
"real-oviedo": "r. oviedo",
"real-salt-lake": "real salt lake",
"real-sociedad": "real sociedad",
"real-valladolid": "valladolid",
"real-zaragoza": "zaragoza",
"red-bull-bragantino": "bragantino",
"red-bull-salzburg": "salzburg",
"rheindorf-altach": "altach",
"rio-ave-fc": "rio ave",
"rionegro-aguilas": "aguilas",
"rkc-waalwijk": "waalwijk",
"rosenborg-bk": "rosenborg",
"ross-county-fc": "ross county",
"royal-antwerp-fc": "antwerp",
"royal-charleroi-sc": "charleroi",
"rsc-anderlecht": "anderlecht",
"ru-saint-gilloise": "union sg",
"samsunspor": "samsunspor",
"san-diego-fc": "san diego fc",
"san-jose-earthquakes": "san jose earthquakes",
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
"seattle-sounders-fc": "seattle sounders",
"servette-fc": "servette",
"sevilla-fc": "sevilla",
"sheffield-united-fc": "sheff utd",
"sheffield-wednesday-fc": "sheff wed",
"sint-truidense-vv": "st. truiden",
"sivasspor": "sivasspor",
"sk-austria-klagenfurt": "a. klagenfurt",
"sk-brann": "brann",
"sk-sigma-olomouc": "sigma olomouc",
"slavia-prague": "slavia prague",
"sociedade-esportiva-palmeiras": "palmeiras",
"southampton-fc": "southampton",
"sparta-prague": "sparta prague",
"sparta-rotterdam": "sparta rotterdam",
"sport-boys": "sport boys",
"sport-club-corinthians-paulista": "corinthians",
"sport-club-do-recife": "sport recife",
"sport-club-internacional": "internacional",
"sport-huancayo": "huancayo",
"sporting-cp": "sporting",
"sporting-cristal": "sporting cristal",
"sporting-de-gijon": "gijon",
"sporting-kansas-city": "sporting kansas city",
"ss-lazio": "lazio",
"ssc-napoli": "napoli",
"ssv-ulm-1846": "ulm",
"st-johnstone-fc": "st. johnstone",
"st-louis-city-sc": "st. louis city",
"st-mirren-fc": "st. mirren",
"stade-brestois-29": "brest",
"stade-de-reims": "reims",
"stade-rennais-fc": "rennes",
"standard-liege": "st. liege",
"stoke-city-fc": "stoke",
"stromsgodset": "stromsgodset",
"sturm-graz": "sturm graz",
"sunderland-afc": "sunderland",
"sv-elversberg": "elversberg",
"swansea-city-afc": "swansea",
"sydney-fc": "sydney fc",
"tigres-uanl": "tigres",
"torino-fc": "torino",
"toronto-fc": "toronto fc",
"tottenham-hotspur-fc": "tottenham",
"toulouse-fc": "toulouse",
"trabzonspor": "trabzonspor",
"tromso-il": "tromso",
"tsv-hartberg": "hartberg",
"ud-almeria": "almeria",
"ud-las-palmas": "las palmas",
"udinese-calcio": "udinese",
"unam": "u.n.a.m.",
"union-berlin": "union berlin",
"union-espanola": "u. espanola",
"union-la-calera": "u. calera",
"union-magdalena": "u. magdalena",
"universidad-tecnica-de-cajamarca": "cajamarca",
"us-lecce": "lecce",
"valencia-cf": "valencia",
"valerenga-fotball": "valerenga",
"vancouver-whitecaps-fc": "vancouver whitecaps",
"venezia-fc": "venezia",
"vfb-stuttgart": "stuttgart",
"vfl-bochum": "bochum",
"vfl-wolfsburg": "wolfsburg",
"viking-fk": "viking",
"villarreal-cf": "villarreal",
"vitoria-de-guimaraes": "guimaraes",
"volos-fc": "volos",
"watford-fc": "watford",
"wellington-phoenix-fc": "wellington phoenix",
"werder-bremen": "bremen",
"west-bromwich-albion-fc": "west brom",
"west-ham-united-fc": "west ham",
"western-sydney-wanderers-fc": "ws wanderers",
"western-united-fc": "western united",
"willem-ii": "willem ii",
"wolfsberger-ac": "wolfsberger",
"wolverhampton-wanderers-fc": "wolves",
"wsg-swarovski-tirol": "tirol",
"yverdon-sport-fc": "yverdon"
}

# === CARGAR DATOS DEL EQUIPO ===
def cargar_datos(equipo_archivo, condicion="local", n=10):
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
    ult_3 = df.tail(3)
    ult_5 = df.tail(5)
    total = df

    def tendencia(df_set):
        return df_set['goles_local'].mean() + df_set['goles_visitante'].mean()

    sets = [(ult_3, tendencia(ult_3)), (ult_5, tendencia(ult_5)), (total, tendencia(total))]
    sets.sort(key=lambda x: -x[1])  # Mayor tendencia ofensiva
    return sets[0][0]

# === CÁLCULO DE ESTADÍSTICAS Y RACHAS ===
def calcular_estadisticas_y_rachas(df, equipo_nombre, tipo_partido):
    if df.empty:
        return None

    df_calculo = df.copy()

    # Columnas de goles según si el equipo es local o visitante
    goles_a_favor = f"goles_{tipo_partido}"
    goles_en_contra = "goles_visitante" if tipo_partido == "local" else "goles_local"
    goles_ht_favor = f"1t_goles_{tipo_partido}"
    goles_ht_contra = "1t_goles_visitante" if tipo_partido == "local" else "1t_goles_local"

    # Promedio de goles
    media_gol = round(df_calculo[goles_a_favor].mean(), 2)

    # BTTS
    btts = (
        (
            (df_calculo[goles_a_favor] > 0)
            & (df_calculo[goles_en_contra] > 0)
        ).mean()
        * 100
    )
    racha_btts = 0
    for i in range(len(df_calculo) - 1, -1, -1):
        if (df_calculo.iloc[i][goles_a_favor] > 0) and (df_calculo.iloc[i][goles_en_contra] > 0):
            racha_btts += 1
        else:
            break

    # Gol HT
    gol_ht = (
        (
            (df_calculo[goles_ht_favor] + df_calculo[goles_ht_contra]) > 0
        ).mean()
        * 100
    )
    racha_gol_ht = 0
    for i in range(len(df_calculo) - 1, -1, -1):
        if (df_calculo.iloc[i][goles_ht_favor] + df_calculo.iloc[i][goles_ht_contra]) > 0:
            racha_gol_ht += 1
        else:
            break

    # Over 2.5 Goles
    over_2_5_goles = (
        (
            (df_calculo[goles_a_favor] + df_calculo[goles_en_contra]) > 2
        ).mean()
        * 100
    )
    racha_over_2_5 = 0
    for i in range(len(df_calculo) - 1, -1, -1):
        if (df_calculo.iloc[i][goles_a_favor] + df_calculo.iloc[i][goles_en_contra]) > 2:
            racha_over_2_5 += 1
        else:
            break

    # Over 1.5 HT
    over_1_5_ht = (
        (
            (df_calculo[goles_ht_favor] + df_calculo[goles_ht_contra]) > 1
        ).mean()
        * 100
    )
    racha_over_1_5_ht = 0
    for i in range(len(df_calculo) - 1, -1, -1):
        if (df_calculo.iloc[i][goles_ht_favor] + df_calculo.iloc[i][goles_ht_contra]) > 1:
            racha_over_1_5_ht += 1
        else:
            break

    return {
        "Estadística": ["Media Gol", "BTTS", "Gol HT", "Over 2.5 Goles", "Over 1.5 HT"],
        f"{equipo_nombre} {tipo_partido.title()}": [
            media_gol,
            f"{btts:.1f}%",
            f"{gol_ht:.1f}%",
            f"{over_2_5_goles:.1f}%",
            f"{over_1_5_ht:.1f}%",
        ],
        "Racha": [
            "",
            racha_btts,
            racha_gol_ht,
            racha_over_2_5,
            racha_over_1_5_ht,
        ],
    }

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

def calcular_probabilidad_over_equipo(lmbda, threshold):
    prob = 1 - poisson.cdf(threshold, lmbda)
    return round(prob * 100, 1)

def calcular_probabilidades_resultado(lambda_local, lambda_visitante, max_goals=6):
    """
    Calcula las probabilidades de victoria local, empate y victoria visitante
    """
    prob_local = prob_empate = prob_visitante = 0.0
    
    for goles_local in range(0, max_goals + 1):
        for goles_visitante in range(0, max_goals + 1):
            p = poisson.pmf(goles_local, lambda_local) * poisson.pmf(goles_visitante, lambda_visitante)
            if goles_local > goles_visitante:
                prob_local += p
            elif goles_local == goles_visitante:
                prob_empate += p
            else:
                prob_visitante += p

    return {
        "Local Gana": round(prob_local * 100, 2),
        "Empate": round(prob_empate * 100, 2),
        "Visitante Gana": round(prob_visitante * 100, 2)
    }

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

    prob_resultados = calcular_probabilidades_resultado(lambda_local, lambda_visitante)

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
        "Prob. Over 2.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 2.5),

        "Prob. Local Over 1.5 Goles": calcular_probabilidad_over_equipo(lambda_local, 1.5),
        "Prob. Visitante Over 1.5 Goles": calcular_probabilidad_over_equipo(lambda_local, 1.5),


        **prob_resultados
    }

    return resultados

def generar_sugerencias(resultados):
    sugerencias = []

    def formato(prob):
        cuota = 100 / prob if prob > 0 else 0
        return f"{prob:.1f}% (cuota {cuota:.2f})"

    if resultados.get("Prob. Gol 1T total", 0) > 80:
        sugerencias.append((f"Over 0.5 goles en 1T", formato(resultados["Prob. Gol 1T total"])))
    if resultados.get("Prob. Gol 2T total", 0) > 80:
        sugerencias.append((f"Over 0.5 goles en 2T", formato(resultados["Prob. Gol 2T total"])))
    if resultados.get("Prob. BTTS", 0) > 70:
        sugerencias.append((f"Ambos equipos marcan (BTTS)", formato(resultados["Prob. BTTS"])))
    if resultados.get("Prob. Local marca", 0) > 80:
        sugerencias.append((f"Local marca al menos un gol", formato(resultados["Prob. Local marca"])))
    if resultados.get("Prob. Visitante marca", 0) > 80:
        sugerencias.append((f"Visitante marca al menos un gol", formato(resultados["Prob. Visitante marca"])))
    if resultados.get("Prob. Over 1.5 Goles", 0) > 80:
        sugerencias.append((f"Over 1.5 goles en el partido", formato(resultados["Prob. Over 1.5 Goles"])))
    if resultados.get("Prob. Over 2.5 Goles", 0) > 70:
        sugerencias.append((f"Over 2.5 goles en el partido", formato(resultados["Prob. Over 2.5 Goles"])))

    if resultados.get("Prob. Local Over 1.5", 0) > 60:
        sugerencias.append((f"Local Over 1.5 goles", formato(resultados["Prob. Local Over 1.5"])))
    if resultados.get("Prob. Visitante Over 1.5", 0) > 60:
        sugerencias.append((f"Visitante Over 1.5 goles", formato(resultados["Prob. Visitante Over 1.5"])))

    if resultados.get("Local Gana", 0) > 70:
        sugerencias.append((f"Victoria del Local", formato(resultados["Local Gana"])))
    elif resultados.get("Visitante Gana", 0) > 70:
        sugerencias.append((f"Victoria del Visitante", formato(resultados["Visitante Gana"])))
    elif resultados.get("Empate", 0) > 45:
        sugerencias.append((f"Empate", formato(resultados["Empate"])))

    return [f"{texto} — {valor}" for texto, valor in sugerencias]



def mostrar_resultados(resultados):

    st.subheader("💡 Sugerencias de Apuesta")
    sugerencias = generar_sugerencias(resultados)    
    for sugerencia in sugerencias:
        st.success(sugerencia)

    st.subheader("ultimos 5 partidos  local")
    st.write(df_local.tail(5))

    st.subheader("ultimos 5 partidos  visitante")
    st.write(df_visitante.tail(5))
        
    st.subheader("Probabilidades de Goles")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Local Marca", f"{resultados['Prob. Local marca']:.1f}%")
        st.metric("Local Marca over 1.5", f"{resultados['Prob. Local Over 1.5 Goles']:.1f}%")
        st.metric("Local 1T", f"{resultados['Prob. Local 1T']:.1f}%")
        st.metric("Local 2T", f"{resultados['Prob. Local 2T']:.1f}%")

    with col2:
        st.metric("BTTS", f"{resultados['Prob. BTTS']:.1f}%")
        st.metric("Gol 1T Total", f"{resultados['Prob. Gol 1T total']:.1f}%")
        st.metric("Gol 2T Total", f"{resultados['Prob. Gol 2T total']:.1f}%")

    with col3:
        st.metric("Visitante Marca", f"{resultados['Prob. Visitante marca']:.1f}%")
        st.metric("Visitante Marca over 1.5", f"{resultados['Prob. Visitante Over 1.5 Goles']:.1f}%")
        st.metric("Visitante 1T", f"{resultados['Prob. Visitante 1T']:.1f}%")
        st.metric("Visitante 2T", f"{resultados['Prob. Visitante 2T']:.1f}%")

    st.subheader("Over de Goles")
    st.metric("Over 1.5 Goles", f"{resultados['Prob. Over 1.5 Goles']:.1f}%")
    st.metric("Over 2.5 Goles", f"{resultados['Prob. Over 2.5 Goles']:.1f}%")

    st.subheader("Probabilidades de Resultado")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Victoria Local", f"{resultados['Local Gana']:.1f}%")
    with col5:
        st.metric("Empate", f"{resultados['Empate']:.1f}%")
    with col6:
        st.metric("Victoria Visitante", f"{resultados['Visitante Gana']:.1f}%")

    st.subheader("Remates")
    col7, col8 = st.columns(2)
    with col7:
        st.metric("Prom. Remates Local", resultados["Prom. Remates Local"])
        st.metric("A puerta Local", resultados["A puerta Local"])        
        st.metric("Total Remates", resultados["Total Remates"])
    with col8:
        st.metric("Prom. Remates Visitante", resultados["Prom. Remates Visitante"])
        st.metric("A puerta Visitante", resultados["A puerta Visitante"])
        st.metric("Total A puerta", resultados["Total A puerta"])

    

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
# if equipo_local and equipo_visitante:
#     Cargar datos históricos
#     df_local = cargar_datos(equipo_local, "local", 5)
#     df_visitante = cargar_datos(equipo_visitante, "visitante", 5)

#     Calcular estadísticas de los equipos
#     stats_local = calcular_estadisticas(df_local, "local")
#     stats_visitante = calcular_estadisticas(df_visitante, "visitante")

#     Calcular probabilidades
#     resultados = calcular_probabilidades_equipo(df_local, df_visitante)

#     Mostrar los resultados en Streamlit
#     nombre_local = equipo_local.replace("-", " ").title()
#     nombre_visitante = equipo_visitante.replace("-", " ").title()

#     st.markdown("## 📊 Estadísticas Generales")
#     mostrar_resultados(resultados)
# else:
#     st.warning("Selecciona un partido para ver el análisis.")

# === CÁLCULOS Y VISUALIZACIÓN ===
if equipo_local_nombre and equipo_visitante_nombre:
    df_local = cargar_datos(equipo_local_nombre, "local", 10)
    df_visitante = cargar_datos(equipo_visitante_nombre, "visitante", 10)

    stats_local = calcular_estadisticas_y_rachas(df_local, equipo_local_nombre, "local")
    stats_visitante = calcular_estadisticas_y_rachas(df_visitante, equipo_visitante_nombre, "visitante")
    
    # Crear los DataFrames para visualización
    df_stats_local = pd.DataFrame(stats_local) if stats_local else pd.DataFrame()
    df_stats_visitante = pd.DataFrame(stats_visitante) if stats_visitante else pd.DataFrame()
    
    st.markdown("## 📊 Estadísticas Detalladas de los Últimos 10 Partidos")
    
    col_local, col_visitante = st.columns(2)
    
    with col_local:
        st.subheader("🔵 Equipo Local")
        if not df_stats_local.empty:
            st.dataframe(df_stats_local.set_index("Estadística"))
        else:
            st.warning("No se encontraron datos del equipo local.")

    with col_visitante:
        st.subheader("🔴 Equipo Visitante")
        if not df_stats_visitante.empty:
            st.dataframe(df_stats_visitante.set_index("Estadística"))
        else:
            st.warning("No se encontraron datos del equipo visitante.")

else:
    st.warning("Selecciona un partido para ver el análisis.")
