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

# === MAPA DE EQUIPOS ===
mapa_equipos = {
    "aarhus": "aarhus",
    "aberdeen-fc": "hearts",
    "ac-milan": "ac milan",
    "ac-monza": "monza",
    "academia-del-balompie-boliviano": "abb",
    "acf-fiorentina": "fiorentina",
    "adc-juan-pablo-ii-college": "juan pablo ii",
    "adelaide-united-fc": "adelaide united",
    "afc-unirea-slobozia": "unirea slobozia",
    "aik": "aik stockholm",
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
    "albacete-balompie": "albacete",
    "alianza-atletico": "alianza atl.",
    "alianza-fc": "alianza",
    "alianza-lima": "a. lima",
    "alianza-universidad-de-huanuco": "alianza huanuco",
    "america-de-cali": "america de cali",
    "angers-sco": "angers",
    "arda-kardzhali": "arda",
    "argentinos-juniors": "argentinos jrs",
    "arka-gdynia": "arka",
    "arminia-bielefeld": "bielefeld",
    "as-monaco-fc": "monaco",
    "as-roma": "as roma",
    "asc-otelul-galati": "otelul",
    "asociacion-deportiva-tarma": "ad tarma",
    "atalanta-bc": "atalanta",
    "athletic-bilbao": "ath. bilbao",
    "atlanta-united-fc": "atlanta united",
    "atlas-fc": "atlas",
    "atletico-bucaramanga": "bucaramanga",
    "atletico-grau": "grau",
    "atletico-junior": "junior",
    "atletico-madrid": "atl. madrid",
    "atletico-nacional": "atl. nacional",
    "atletico-san-luis": "atl. san luis",
    "auckland-fc": "auckland fc",
    "audax-italiano": "a. italiano",
    "austin-fc": "austin fc",
    "austria-vienna": "grazer ak",
    "ayacucho-fc": "ayacucho",
    "bayer-leverkusen": "leverkusen",
    "bayern-munich": "bayern",
    "beroe": "beroe",
    "bk-hacken": "hacken",
    "bohemians-1905": "bohemians",
    "bologna-fc-1909": "bologna",
    "borussia-dortmund": "dortmund",
    "borussia-monchengladbach": "monchengladbach",
    "botafogo-de-futebol-e-regatas": "botafogo rj",
    "botev-plovdiv": "botev plovdiv",
    "botev-vratsa": "botev vratsa",
    "boyaca-chico-fc": "chico",
    "brisbane-roar-fc": "brisbane roar",
    "brondby": "brondby",
    "bruk-bet-termalica-nieciecza": "termalica b-b.",
    "bryne-fk": "bryne",
    "bsc-young-boys": "young boys",
    "burgos-cf": "burgos cf",
    "bw-linz": "sk rapid",
    "ca-osasuna": "osasuna",
    "cadiz-cf": "cadiz",
    "cagliari-calcio": "cagliari",
    "cardiff-city-fc": "cardiff",
    "cd-castellon": "castellon",
    "cd-cobresal": "cobresal",
    "cd-eldense": "eldense",
    "cd-guadalajara": "guadalajara",
    "cd-huachipato": "huachipato",
    "cd-la-equidad": "la equidad",
    "cd-leganes": "leganes",
    "cd-mirandes": "mirandes",
    "cd-palestino": "palestino",
    "cd-tenerife": "tenerife",
    "cd-universidad-catolica": "u. catolica",
    "cdt-real-oruro": "real oruro",
    "ceara-sporting-club": "ceara",
    "celta-vigo": "celta vigo",
    "celtic-fc": "celtic",
    "central-coast-mariners-fc": "central coast mariners",
    "cercle-brugge-ksv": "cercle brugge",
    "cf-monterrey": "monterrey",
    "cf-pachuca": "pachuca",
    "cfr-cluj": "cfr cluj",
    "charlotte-fc": "charlotte",
    "cherno-more": "cherno more",
    "chicago-fire-fc": "chicago fire",
    "club-always-ready": "always ready",
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
    "club-atletico-nacional-potosi": "nacional potosi",
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
    "club-aurora": "aurora",
    "club-bolivar": "bolivar",
    "club-brugge-kv": "club brugge",
    "club-de-foot-montreal": "cf montreal",
    "club-de-gimnasia-la-plata": "gimnasia l.p.",
    "club-deportivo-blooming": "blooming",
    "club-deportivo-guabira": "guabira",
    "club-deportivo-jorge-wilstermann": "wilstermann",
    "club-deportivo-oriente-petrolero": "oriente petrolero",
    "club-deportivo-real-tomayapo": "tomayapo",
    "club-deportivo-san-antonio-bulo-bulo": "sa bulo bulo",
    "club-estudiantes-de-la-plata": "estudiantes",
    "club-gv-san-jose": "gv san jose",
    "club-independiente-petrolero": "independiente",
    "club-leon": "leon",
    "club-necaxa": "necaxa",
    "club-puebla": "puebla",
    "club-sportivo-cienciano": "cienciano",
    "club-sportivo-independiente-rivadavia": "ind. rivadavia",
    "club-the-strongest": "the strongest",
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
    "cr-vasco-da-gama": "vasco",
    "cracovia": "cracovia",
    "cruz-azul": "cruz azul",
    "cruzeiro-esporte-clube": "cruzeiro",
    "cs-universitatea-craiova": "univ. craiova",
    "cska-sofia": "cska sofia",
    "cusco-fc": "cusco",
    "damac-fc": "damac",
    "darmstadt-98": "darmstadt",
    "dc-united": "dc united",
    "defensa-y-justicia": "defensa y justicia",
    "degerfors-if": "degerfors",
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
    "dinamo-zagreb": "osijek",
    "djurgardens-if": "djurgarden",
    "dundee-fc": "dundee fc",
    "dundee-united-fc": "falkirk",
    "dynamo-dresden": "furth",
    "eintracht-braunschweig": "magdeburg",
    "eintracht-frankfurt": "frankfurt",
    "elche-cf": "elche",
    "empoli-fc": "empoli",
    "envigado-fc": "envigado",
    "esporte-clube-bahia": "bahia",
    "esporte-clube-juventude": "juventude",
    "esporte-clube-vitoria": "vitoria",
    "everton-de-vina-del-mar": "everton",
    "falkirk-fc": "falkirk",
    "fbc-melgar": "melgar",
    "fc-arges-pitesti": "fc arges",
    "fc-augsburg": "augsburg",
    "fc-banik-ostrava": "ostrava",
    "fc-barcelona": "barcelona",
    "fc-basel": "basel",
    "fc-botosani": "botosani",
    "fc-cartagena": "cartagena",
    "fc-cincinnati": "cincinnati",
    "fc-copenhagen": "fc copenhagen",
    "fc-cska-1948-sofia": "cska 1948 sofia",
    "fc-dallas": "fc dallas",
    "fc-dinamo-bucuresti": "din. bucuresti",
    "fc-dobrudzha-dobrich": "dobrudzha",
    "fc-farul-constanta": "farul constanta",
    "fc-fastav-zlin": "zlin",
    "fc-fredericia": "fredericia",
    "fc-heidenheim": "heidenheim",
    "fc-hermannstadt": "fc hermannstadt",
    "fc-hradec-kralove": "hradec kralove",
    "fc-juarez": "juarez",
    "fc-kaiserslautern": "hannover",
    "fc-koln": "furth",
    "fc-lausanne-sport": "lausanne",
    "fc-lokomotiv-1929-sofia": "lok. sofia",
    "fc-lugano": "lugano",
    "fc-luzern": "luzern",
    "fc-magdeburg": "magdeburg",
    "fc-metaloglobus-bucuresti": "metaloglobus bucharest",
    "fc-midtjylland": "midtjylland",
    "fc-montana": "montana",
    "fc-nantes": "nantes",
    "fc-nordsjaelland": "nordsjaelland",
    "fc-nurnberg": "elversberg",
    "fc-petrolul-ploiesti": "petrolul",
    "fc-rapid-bucuresti": "fc rapid bucuresti",
    "fc-sion": "sion",
    "fc-slovacko": "slovacko",
    "fc-slovan-liberec": "liberec",
    "fc-spartak-varna": "spartak varna",
    "fc-st-gallen": "st. gallen",
    "fc-st-pauli": "st. pauli",
    "fc-thun": "thun",
    "fc-universitario-de-vinto": "universitario de vinto",
    "fc-universitatea-cluj": "u. cluj",
    "fc-uta-arad": "uta arad",
    "fc-viktoria-plzen": "plzen",
    "fc-winterthur": "winterthur",
    "fc-zurich": "zurich",
    "fcsb": "fcsb",
    "fcv-dender-eh": "dender",
    "fk-bodo-glimt": "bodo/glimt",
    "fk-dukla-prague": "dukla prague",
    "fk-haugesund": "haugesund",
    "fk-jablonec": "jablonec",
    "fk-miercurea-ciuc": "csikszereda m. ciuc",
    "fk-mlada-boleslav": "mlada boleslav",
    "fk-pardubice": "pardubice",
    "fk-teplice": "teplice",
    "fluminense-fc": "fluminense",
    "fortaleza-ceif": "fortaleza",
    "fortaleza-esporte-clube": "fortaleza",
    "fortuna-dusseldorf": "bielefeld",
    "fredrikstad-fk": "fredrikstad",
    "gais": "gais",
    "genoa-cfc": "genoa",
    "getafe-cf": "getafe",
    "girona-fc": "girona",
    "gks-katowice": "katowice",
    "godoy-cruz": "godoy cruz",
    "gorica": "varazdin",
    "gornik-zabrze": "gornik zabrze",
    "granada-cf": "granada",
    "grasshopper-club-zurich": "grasshoppers",
    "grazer-ak": "grazer ak",
    "gremio-football-porto-alagrense": "gremio",
    "greuther-furth": "furth",
    "hajduk-split": "hajduk split",
    "halmstads-bk": "halmstad",
    "ham-kam": "hamkam",
    "hamburger-sv": "elversberg",
    "hammarby-if": "hammarby",
    "hannover-96": "hannover",
    "heart-of-midlothian-fc": "hearts",
    "hellas-verona-fc": "verona",
    "hertha-berlin": "schalke",
    "hibernian-fc": "dundee fc",
    "hnk-vukovar-1991": "lok. zagreb",
    "hoffenheim": "hoffenheim",
    "holstein-kiel": "paderborn",
    "houston-dynamo": "houston dynamo",
    "if-brommapojkarna": "brommapojkarna",
    "if-elfsborg": "elfsborg",
    "ifk-goteborg": "goteborg",
    "ifk-norrkoping": "norrkoping",
    "ifk-varnamo": "varnamo",
    "ik-sirius": "sirius",
    "independiente-santa-fe": "santa fe",
    "instituto-atletico-central-cordoba": "instituto",
    "inter-miami-cf": "inter miami",
    "inter-milan": "inter",
    "istra-1961": "hajduk split",
    "jagiellona-bialystok": "jagiellonia",
    "jahn-regensburg": "ingolstadt",
    "juventus-fc": "juventus",
    "kaa-gent": "gent",
    "karlsruher-sc": "karlsruher",
    "kfum-kameratene-oslo": "kfum oslo",
    "khaleej-fc": "al khaleej",
    "kilmarnock-fc": "kilmarnock",
    "korona-kielce": "korona",
    "krc-genk": "genk",
    "kristiansund-bk": "kristiansund",
    "kv-mechelen": "kv mechelen",
    "kvc-westerlo": "westerlo",
    "lask": "lask",
    "le-havre-ac": "le havre",
    "lech-poznan": "lech",
    "lechia-gdansk": "lechia",
    "legia-warsaw": "legia",
    "levante-ud": "levante",
    "levski-sofia": "levski",
    "lille-osc": "lille",
    "livingston-fc": "kilmarnock",
    "llaneros-fc": "llaneros",
    "lokomotiv-plovdiv": "lok. plovdiv",
    "lokomotiva-zagreb": "lok. zagreb",
    "los-angeles-fc": "los angeles fc",
    "los-angeles-galaxy": "los angeles galaxy",
    "los-chankas-cyc": "los chankas",
    "ludogorets": "ludogorets",
    "luton-town-fc": "luton",
    "macarthur-fc": "macarthur fc",
    "mainz-05": "mainz",
    "malaga-cf": "malaga",
    "malmo-ff": "malmo ff",
    "mazatlan-fc": "mazatlan fc",
    "melbourne-city-fc": "melbourne city",
    "melbourne-victory-fc": "melbourne victory",
    "mfk-karvina": "karvina",
    "millonarios-fc": "millonarios",
    "minnesota-united-fc": "minnesota",
    "mirassol-fc": "mirassol",
    "mjallby-aif": "mjallby",
    "mks-pogon-szczecin": "pogon szczecin",
    "molde-fk": "molde",
    "motherwell-fc": "motherwell",
    "motor-lublin": "motor lublin",
    "nashville-sc": "nashville sc",
    "new-england-revolution": "new england revolution",
    "new-york-city-fc": "new york city",
    "new-york-red-bulls": "new york red bulls",
    "newcastle-jets-fc": "newcastle jets",
    "o-higgins-fc": "o'higgins",
    "odense-boldklub": "odense",
    "ogc-nice": "nice",
    "oh-leuven": "leuven",
    "olympique-de-marseille": "marseille",
    "olympique-lyonnais": "lyon",
    "once-caldas": "once caldas",
    "orlando-city-sc": "orlando city",
    "osijek": "osijek",
    "osters-if": "oster",
    "paris-saint-germain-fc": "psg",
    "parma-calcio-1913": "parma",
    "perth-glory-fc": "perth glory",
    "pfc-septemvri-sofia": "septemvri sofia",
    "philadelphia-union": "philadelphia union",
    "piast-gliwice": "piast",
    "plymouth-argyle-fc": "plymouth",
    "portland-timbers": "portland timbers",
    "preussen-munster": "karlsruher",
    "queretaro-fc": "queretaro",
    "raal-la-louviere": "raal la louviere",
    "racing-club-de-avellaneda": "racing club",
    "racing-de-ferrol": "racing club ferrol",
    "racing-de-santander": "racing santander",
    "radomiak-radom": "radomiak radom",
    "rakow-czestochowa": "rakow",
    "randers-fc": "randers",
    "rangers-fc": "motherwell",
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
    "red-bull-salzburg": "ried",
    "rheindorf-altach": "wolfsberger",
    "rijeka": "rijeka",
    "rionegro-aguilas": "aguilas",
    "rosenborg-bk": "rosenborg",
    "royal-antwerp-fc": "antwerp",
    "royal-charleroi-sc": "charleroi",
    "rsc-anderlecht": "anderlecht",
    "rts-widzew-lodz": "widzew lodz",
    "ru-saint-gilloise": "union sg",
    "san-diego-fc": "san diego fc",
    "san-jose-earthquakes": "san jose earthquakes",
    "san-lorenzo-de-almagro": "san lorenzo",
    "san-martin-de-san-juan": "san martin s.j.",
    "sandefjord-fotball": "sandefjord",
    "santos-fc": "santos",
    "santos-laguna": "santos laguna",
    "sao-paulo-fc": "sao paulo",
    "sarpsborg-08-ff": "sarpsborg 08",
    "sc-freiburg": "freiburg",
    "sc-paderborn": "paderborn",
    "schalke-04": "schalke",
    "sd-eibar": "eibar",
    "sd-huesca": "huesca",
    "seattle-sounders-fc": "seattle sounders",
    "servette-fc": "servette",
    "sevilla-fc": "sevilla",
    "silkeborg-if": "silkeborg",
    "sint-truidense-vv": "st. truiden",
    "sk-brann": "brann",
    "sk-sigma-olomouc": "sigma olomouc",
    "slaven-belupo": "rijeka",
    "slavia-prague": "slavia prague",
    "slavia-sofia": "slavia sofia",
    "sociedade-esportiva-palmeiras": "palmeiras",
    "sonderjyske": "sonderjyske",
    "sparta-prague": "sparta prague",
    "sport-boys": "sport boys",
    "sport-club-corinthians-paulista": "corinthians",
    "sport-club-do-recife": "sport recife",
    "sport-club-internacional": "internacional",
    "sport-huancayo": "huancayo",
    "sporting-cristal": "sporting cristal",
    "sporting-de-gijon": "gijon",
    "sporting-kansas-city": "sporting kansas city",
    "ss-lazio": "lazio",
    "ssc-napoli": "napoli",
    "ssv-ulm-1846": "wehen",
    "st-louis-city-sc": "st. louis city",
    "st-mirren-fc": "celtic",
    "stade-brestois-29": "brest",
    "stade-rennais-fc": "rennes",
    "standard-liege": "st. liege",
    "stromsgodset": "stromsgodset",
    "sturm-graz": "lask",
    "sv-elversberg": "elversberg",
    "sv-ried": "ried",
    "sv-zulte-waregem": "waregem",
    "sydney-fc": "sydney fc",
    "tigres-uanl": "tigres",
    "torino-fc": "torino",
    "toronto-fc": "toronto fc",
    "toulouse-fc": "toulouse",
    "tromso-il": "tromso",
    "tsv-hartberg": "tirol",
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
    "varazdin": "varazdin",
    "vejle-bk": "vejle",
    "venezia-fc": "venezia",
    "vfb-stuttgart": "stuttgart",
    "vfl-bochum": "darmstadt",
    "vfl-wolfsburg": "wolfsburg",
    "viborg-ff": "viborg",
    "viking-fk": "viking",
    "villarreal-cf": "villarreal",
    "wellington-phoenix-fc": "wellington phoenix",
    "werder-bremen": "bremen",
    "western-sydney-wanderers-fc": "ws wanderers",
    "western-united-fc": "western united",
    "wisla-plock": "wisla plock",
    "wolfsberger-ac": "wolfsberger",
    "wsg-swarovski-tirol": "tirol",
    "zaglebie-lubin": "zaglebie"
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
        
        # Filtra por el nombre del equipo, no por el nombre del archivo
        nombre_equipo = mapa_equipos.get(equipo_archivo, equipo_archivo.replace("-", " ").lower())
        if condicion == "local":
            df_filtrado = df[df["equipo_local"].str.lower().str.contains(nombre_equipo, na=False)]
        else:
            df_filtrado = df[df["visitante"].str.lower().str.contains(nombre_equipo, na=False)]

        return df_filtrado.tail(n)

    except Exception as e:
        st.error(f"❌ Error al cargar datos para {equipo_archivo}: {e}")
        return pd.DataFrame()

# === CÁLCULO AJUSTADO POISSON ===
def calcular_lambda(df, col_goles, col_xg, partidos_recientes = 5):
    if df.empty:
        return 0

    xg_prom = df[col_xg].mean()
    efectividad = (df[col_goles].sum() / df[col_xg].sum()) if df[col_xg].sum() > 0 else 1

    df_recientes = df.sort_values(by="fecha", ascending=False).head(partidos_recientes)
    xg_forma = df_recientes[col_xg].mean()
    goles_forma = df_recientes[col_goles].mean()
    efectividad_forma = (df_recientes[col_goles].sum() / df_recientes[col_xg].sum()) if df_recientes[col_xg].sum() > 0 else 1

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
    if lmbda <= 0:
        return 0
    return round(1 - poisson.cdf(min_goles - 1, lmbda), 3)

# === DECISIÓN AUTOMÁTICA ===
def seleccionar_df(df):
    if len(df) < 5:
        return df
    
    ult_3 = df.tail(3)
    ult_5 = df.tail(5)
    total = df

    def tendencia(df_set):
        if df_set.empty:
            return 0
        return df_set['goles_local'].mean() + df_set['goles_visitante'].mean()

    sets = [(ult_3, tendencia(ult_3)), (ult_5, tendencia(ult_5)), (total, tendencia(total))]
    sets.sort(key=lambda x: -x[1])
    return sets[0][0]

# === CALCULAR ESTADÍSTICAS ===
def calcular_estadisticas(df, tipo):
    if df.empty:
        return {}
    stats = {
        "Prom. Goles": round(df["goles_local"].mean(), 2) if tipo == "local" else round(df["goles_visitante"].mean(), 2),
        "Prom. xG": round(df["xg_favor"].mean(), 2),
        "Prom. Remates": round(df["shots_favor"].mean(), 1),
        "A puerta": round(df["a_puerta_favor"].mean(), 1),
    }
    return stats

def probabilidad_over_total(lambda_local, lambda_visitante, limite):
    lambda_total = lambda_local + lambda_visitante
    if lambda_total <= 0:
        return 0
    return round((1 - sum(poisson.pmf(k, lambda_total) for k in range(int(limite) + 1))) * 100, 1)

def calcular_probabilidad_over_equipo(lmbda, threshold):
    if lmbda <= 0:
        return 0
    prob = 1 - poisson.cdf(threshold, lmbda)
    return round(prob * 100, 1)

def calcular_probabilidades_resultado(lambda_local, lambda_visitante, max_goals=6):
    prob_local = prob_empate = prob_visitante = 0.0
    
    if lambda_local <= 0 and lambda_visitante <= 0:
        return {"Local Gana": 0, "Empate": 100, "Visitante Gana": 0}
        
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
    if df_local.empty or df_visitante.empty:
        return None
        
    df_local_sel = seleccionar_df(df_local)
    df_visitante_sel = seleccionar_df(df_visitante)

    lambda_local = calcular_lambda(df_local_sel, "goles_local", "xg_favor")
    lambda_visitante = calcular_lambda(df_visitante_sel, "goles_visitante", "xg_favor")

    lambda_local_1t = calcular_lambda(df_local_sel, "1t_goles_favor", "xg_favor")
    lambda_visitante_1t = calcular_lambda(df_visitante_sel, "1t_goles_favor", "xg_favor")
    lambda_local_2t = calcular_lambda(df_local_sel, "2t_goles_favor", "xg_favor")
    lambda_visitante_2t = calcular_lambda(df_visitante_sel, "2t_goles_favor", "xg_favor")

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

        "Prom. Remates Local": round(df_local_sel["shots_favor"].mean(), 1),
        "Prom. Remates Visitante": round(df_visitante_sel["shots_favor"].mean(), 1),
        "Total Remates": round((df_local_sel["shots_favor"].mean() + df_visitante_sel["shots_favor"].mean()), 1),

        "A puerta Local": round(df_local_sel["a_puerta_favor"].mean(), 1),
        "A puerta Visitante": round(df_visitante_sel["a_puerta_favor"].mean(), 1),
        "Total A puerta": round((df_local_sel["a_puerta_favor"].mean() + df_visitante_sel["a_puerta_favor"].mean()), 1),

        "Prob. Over 1.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 1.5),
        "Prob. Over 2.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 2.5),

        "Prob. Local Over 1.5 Goles": calcular_probabilidad_over_equipo(lambda_local, 1.5),
        "Prob. Visitante Over 1.5 Goles": calcular_probabilidad_over_equipo(lambda_visitante, 1.5),

        **prob_resultados
    }
    return resultados

def generar_sugerencias(resultados):
    if resultados is None:
        return ["No hay suficientes datos para generar sugerencias."]
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

    if resultados.get("Prob. Local Over 1.5 Goles", 0) > 60:
        sugerencias.append((f"Local Over 1.5 goles", formato(resultados["Prob. Local Over 1.5 Goles"])))
    if resultados.get("Prob. Visitante Over 1.5 Goles", 0) > 60:
        sugerencias.append((f"Visitante Over 1.5 goles", formato(resultados["Prob. Visitante Over 1.5 Goles"])))

    if resultados.get("Local Gana", 0) > 70:
        sugerencias.append((f"Victoria del Local", formato(resultados["Local Gana"])))
    elif resultados.get("Visitante Gana", 0) > 70:
        sugerencias.append((f"Victoria del Visitante", formato(resultados["Visitante Gana"])))
    elif resultados.get("Empate", 0) > 45:
        sugerencias.append((f"Empate", formato(resultados["Empate"])))

    return [f"{texto} — {valor}" for texto, valor in sugerencias]

def mostrar_resultados(resultados, df_local, df_visitante):
    if resultados is None:
        st.error("No se pudo calcular la predicción debido a datos insuficientes.")
        return

    st.subheader("💡 Sugerencias de Apuesta")
    sugerencias = generar_sugerencias(resultados)
    for sugerencia in sugerencias:
        st.success(sugerencia)

    st.subheader("Últimos 5 partidos local")
    st.write(df_local.tail(5))
    st.subheader("Últimos 5 partidos visitante")
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
        st.metric("Prom. Remates Local", resultados.get("Prom. Remates Local", "N/A"))
        st.metric("A puerta Local", resultados.get("A puerta Local", "N/A"))
        st.metric("Total Remates", resultados.get("Total Remates", "N/A"))
    with col8:
        st.metric("Prom. Remates Visitante", resultados.get("Prom. Remates Visitante", "N/A"))
        st.metric("A puerta Visitante", resultados.get("A puerta Visitante", "N/A"))
        st.metric("Total A puerta", resultados.get("Total A puerta", "N/A"))

# === CÁLCULO DE ESTADÍSTICAS Y RACHAS ===
def calcular_estadisticas_y_rachas(df, equipo_nombre, tipo_partido):
    if df.empty:
        return None

    df_calculo = df.copy()

    # Columnas de goles y remates según si el equipo es local o visitante
    goles_a_favor_col = "goles_local" if tipo_partido == "local" else "goles_visitante"
    goles_en_contra_col = "goles_visitante" if tipo_partido == "local" else "goles_local"
    goles_ht_favor_col = "1t_goles_favor"
    goles_ht_contra_col = "1t_goles_contra"
    goles_st_favor_col = "2t_goles_favor"
    goles_st_contra_col = "2t_goles_contra"
    remates_favor_col = "shots_favor"
    a_puerta_favor_col = "a_puerta_favor"

    # Goles y remates
    media_gol = round(df_calculo[goles_a_favor_col].mean(), 2)
    media_gol_1t = round(df_calculo[goles_ht_favor_col].mean(), 2)
    media_gol_2t = round(df_calculo[goles_st_favor_col].mean(), 2)
    promedio_remates = round(df_calculo[remates_favor_col].mean(), 1)
    promedio_tiros_puerta = round(df_calculo[a_puerta_favor_col].mean(), 1)
    
    # Rachas para las medias de goles por tiempo
    racha_media_gol = (df_calculo[goles_a_favor_col] > media_gol).sum()
    racha_media_gol_1t = (df_calculo[goles_ht_favor_col] > media_gol_1t).sum()
    racha_media_gol_2t = (df_calculo[goles_st_favor_col] > media_gol_2t).sum()
    
    # BTTS
    btts_cond = (df_calculo[goles_a_favor_col] > 0) & (df_calculo[goles_en_contra_col] > 0)
    btts = btts_cond.mean() * 100
    racha_btts = 0
    for i in range(len(btts_cond) - 1, -1, -1):
        if btts_cond.iloc[i]:
            racha_btts += 1
        else:
            break

    # Gol HT
    gol_ht_cond = (df_calculo[goles_ht_favor_col] + df_calculo[goles_ht_contra_col]) > 0
    gol_ht = gol_ht_cond.mean() * 100
    racha_gol_ht = 0
    for i in range(len(gol_ht_cond) - 1, -1, -1):
        if gol_ht_cond.iloc[i]:
            racha_gol_ht += 1
        else:
            break

    # Over 1.5 Goles Totales
    over_1_5_total_cond = (df_calculo[goles_a_favor_col] + df_calculo[goles_en_contra_col]) > 1.5
    over_1_5_total = over_1_5_total_cond.mean() * 100
    racha_over_1_5_total = 0
    for i in range(len(over_1_5_total_cond) - 1, -1, -1):
        if over_1_5_total_cond.iloc[i]:
            racha_over_1_5_total += 1
        else:
            break

    # Over 2.5 Goles
    over_2_5_cond = (df_calculo[goles_a_favor_col] + df_calculo[goles_en_contra_col]) > 2.5
    over_2_5_goles = over_2_5_cond.mean() * 100
    racha_over_2_5 = 0
    for i in range(len(over_2_5_cond) - 1, -1, -1):
        if over_2_5_cond.iloc[i]:
            racha_over_2_5 += 1
        else:
            break

    # Over 1.5 HT
    over_1_5_ht_cond = (df_calculo[goles_ht_favor_col] + df_calculo[goles_ht_contra_col]) > 1.5
    over_1_5_ht = over_1_5_ht_cond.mean() * 100
    racha_over_1_5_ht = 0
    for i in range(len(over_1_5_ht_cond) - 1, -1, -1):
        if over_1_5_ht_cond.iloc[i]:
            racha_over_1_5_ht += 1
        else:
            break
            
    # Promedio de remates
    racha_prom_remates = 0
    if len(df_calculo) > 0:
        prom_remates_ultimos = df_calculo[remates_favor_col].tail(1)
        if not prom_remates_ultimos.empty and prom_remates_ultimos.iloc[0] > df_calculo[remates_favor_col].mean():
            racha_prom_remates = sum(df_calculo[remates_favor_col].tail(10) > df_calculo[remates_favor_col].mean())

    # Promedio de tiros a puerta
    racha_prom_tiros_puerta = 0
    if len(df_calculo) > 0:
        prom_tiros_puerta_ultimos = df_calculo[a_puerta_favor_col].tail(1)
        if not prom_tiros_puerta_ultimos.empty and prom_tiros_puerta_ultimos.iloc[0] > df_calculo[a_puerta_favor_col].mean():
            racha_prom_tiros_puerta = sum(df_calculo[a_puerta_favor_col].tail(10) > df_calculo[a_puerta_favor_col].mean())


    return {
        "Estadística": [
            "Media Gol", 
            "Media Gol 1T", 
            "Media Gol 2T", 
            "BTTS", 
            "Gol HT", 
            "Over 1.5 Goles Total",
            "Over 2.5 Goles", 
            "Over 1.5 HT",
            "Promedio Remates",
            "Promedio Tiros a Puerta"
        ],
        f"{equipo_nombre} {tipo_partido.title()}": [
            media_gol,
            media_gol_1t,
            media_gol_2t,
            f"{btts:.1f}%",
            f"{gol_ht:.1f}%",
            f"{over_1_5_total:.1f}%",
            f"{over_2_5_goles:.1f}%",
            f"{over_1_5_ht:.1f}%",
            promedio_remates,
            promedio_tiros_puerta
        ],
        "Racha": [
            racha_media_gol,
            racha_media_gol_1t,
            racha_media_gol_2t,
            racha_btts,
            racha_gol_ht,
            racha_over_1_5_total,
            racha_over_2_5,
            racha_over_1_5_ht,
            racha_prom_remates,
            racha_prom_tiros_puerta
        ],
    }

# === EQUIPOS DISPONIBLES ===
archivos = [f.replace(".xlsx", "") for f in os.listdir("new-stats/") if f.endswith(".xlsx")]
equipos_disponibles = sorted(archivos)

# === UI SELECCIÓN ===
col1, col2 = st.columns(2)
with col1:
    equipo_local_nombre = st.selectbox("🔵 Equipo LOCAL", equipos_disponibles)
with col2:
    equipo_visitante_nombre = st.selectbox("🔴 Equipo VISITANTE", equipos_disponibles)

# === CÁLCULOS Y VISUALIZACIÓN ===
if equipo_local_nombre and equipo_visitante_nombre:
    df_local_all = cargar_datos(equipo_local_nombre, "local", 10)
    df_visitante_all = cargar_datos(equipo_visitante_nombre, "visitante", 10)

    # Lógica para la tabla de la imagen
    stats_local = calcular_estadisticas_y_rachas(df_local_all, equipo_local_nombre, "local")
    stats_visitante = calcular_estadisticas_y_rachas(df_visitante_all, equipo_visitante_nombre, "visitante")
    
    df_stats_local = pd.DataFrame(stats_local) if stats_local else pd.DataFrame()
    df_stats_visitante = pd.DataFrame(stats_visitante) if stats_visitante else pd.DataFrame()
    
    # Función para aplicar el estilo condicional a la columna 'Estadística'
    def highlight_racha(row):
        racha = row['Racha']
        styles = [''] * len(row)
        # Asegurarse de que racha sea un número antes de comparar
        if isinstance(racha, (int, float)):
            if 2 <= racha < 5:
                # Color amarillo tenue
                styles[0] = 'background-color: #ffffcc'
            elif racha >= 5:
                # Color verde tenue
                styles[0] = 'background-color: #ccffcc'
        return styles

    st.markdown("## 📊 Estadísticas Detalladas de los Últimos 10 Partidos")
    col_local_stats, col_visitante_stats = st.columns(2)
    
    with col_local_stats:
        st.subheader("🔵 Equipo Local")
        if not df_stats_local.empty:
            st.dataframe(
                df_stats_local.style.apply(highlight_racha, axis=1),
                use_container_width=True,
                hide_index=True,
                column_config={
                    f"{equipo_local_nombre} Local": st.column_config.Column(width="medium"),
                    "Racha": st.column_config.Column(width="small")
                }
            )

    with col_visitante_stats:
        st.subheader("🔴 Equipo Visitante")
        if not df_stats_visitante.empty:
            st.dataframe(
                df_stats_visitante.style.apply(highlight_racha, axis=1),
                use_container_width=True,
                hide_index=True,
                column_config={
                    f"{equipo_visitante_nombre} Visitante": st.column_config.Column(width="medium"),
                    "Racha": st.column_config.Column(width="small")
                }
            )

    st.markdown("---")
    st.markdown("## 📈 Predicción del Partido")
    
    # Lógica de predicción y sugerencias
    resultados = calcular_probabilidades_equipo(df_local_all, df_visitante_all)
    mostrar_resultados(resultados, df_local_all, df_visitante_all)

else:
    st.warning("Selecciona un partido para ver el análisis.")