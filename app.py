import streamlit as st
import pandas as pd
import os
from collections import Counter
from scipy.stats import poisson
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
"aberdeen-fc": "aberdeen",
"ac-milan": "ac milan",
"ac-monza": "monza",
"ac-pisa-1909": "pisa",
"academia-del-balompie-boliviano": "abb",
"acf-fiorentina": "fiorentina",
"ad-ceuta-fc": "ceuta",
"adc-juan-pablo-ii-college": "juan pablo ii",
"afc-ajax": "ajax",
"afc-bournemouth": "bournemouth",
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
"al-qadsiah-fc": "al qadisiya",
"al-riyadh-sc": "al riyadh",
"al-shabab-fc": "al-shabab",
"al-taawoun-fc": "al-taawon",
"alanyaspor": "alanyaspor",
"albacete-balompie": "albacete",
"alianza-atletico": "alianza atl.",
"alianza-fc": "alianza",
"alianza-lima": "a. lima",
"alianza-universidad-de-huanuco": "alianza huanuco",
"america-de-cali": "america de cali",
"angers-sco": "angers",
"antalyaspor": "antalyaspor",
"arda-kardzhali": "arda",
"argentinos-juniors": "argentinos jrs",
"arka-gdynia": "arka",
"arminia-bielefeld": "bielefeld",
"arsenal-fc": "arsenal",
"as-monaco-fc": "monaco",
"as-roma": "as roma",
"as-saint-etienne": "st. etienne",
"asc-otelul-galati": "otelul",
"asociacion-deportiva-tarma": "ad tarma",
"aston-villa-fc": "aston villa",
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
"audax-italiano": "a. italiano",
"austin-fc": "austin fc",
"austria-vienna": "austria vienna",
"avs-futebol-sad": "afs",
"ayacucho-fc": "ayacucho",
"az-alkmaar": "alkmaar",
"bayer-leverkusen": "leverkusen",
"bayern-munich": "bayern",
"benfica": "benfica",
"beroe": "beroe",
"besiktas-jk": "besiktas",
"birmingham-city-fc": "birmingham",
"bk-hacken": "hacken",
"blackburn-rovers-fc": "blackburn",
"bohemians-1905": "bohemians",
"bologna-fc-1909": "bologna",
"borussia-dortmund": "dortmund",
"borussia-monchengladbach": "monchengladbach",
"botafogo-de-futebol-e-regatas": "botafogo rj",
"botev-plovdiv": "botev plovdiv",
"botev-vratsa": "botev vratsa",
"boyaca-chico-fc": "chico",
"braga": "braga",
"brentford-fc": "brentford",
"brighton-hove-albion-fc": "brighton",
"bristol-city-fc": "bristol city",
"brondby": "brondby",
"bruk-bet-termalica-nieciecza": "termalica b-b.",
"bryne-fk": "bryne",
"bsc-young-boys": "young boys",
"burgos-cf": "burgos cf",
"burnley-fc": "burnley",
"bw-linz": "bw linz",
"ca-osasuna": "osasuna",
"cadiz-cf": "cadiz",
"cagliari-calcio": "cagliari",
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
"cd-tondela": "tondela",
"cd-universidad-catolica": "u. catolica",
"cdt-real-oruro": "real oruro",
"ceara-sporting-club": "ceara",
"celta-vigo": "celta vigo",
"celtic-fc": "celtic",
"cercle-brugge-ksv": "cercle brugge",
"cf-estrela-da-amadora": "estrela",
"cf-monterrey": "monterrey",
"cf-pachuca": "pachuca",
"cfr-cluj": "cfr cluj",
"charlotte-fc": "charlotte",
"charlton-athletic-fc": "charlton",
"chelsea-fc": "chelsea",
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
"coventry-city-fc": "coventry",
"cr-vasco-da-gama": "vasco",
"cracovia": "cracovia",
"cruz-azul": "cruz azul",
"cruzeiro-esporte-clube": "cruzeiro",
"crystal-palace-fc": "crystal palace",
"cs-universitatea-craiova": "univ. craiova",
"cska-sofia": "cska sofia",
"cultural-y-deportiva-leonesa": "cultural leonesa",
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
"deportivo-de-la-coruna": "las palmas",
"deportivo-garcilaso": "deportivo garcilaso",
"deportivo-independiente-medellin": "ind. medellin",
"deportivo-nublense": "nublense",
"deportivo-pasto": "pasto",
"deportivo-pereira": "pereira",
"deportivo-riestra": "dep. riestra",
"deportivo-toluca-fc": "toluca",
"derby-county-fc": "derby",
"dinamo-zagreb": "din. zagreb",
"djurgardens-if": "djurgarden",
"dundee-fc": "dundee fc",
"dundee-united-fc": "dundee utd",
"dynamo-dresden": "dresden",
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
"falkirk-fc": "falkirk",
"famalicao": "famalicao",
"fatih-karagumruk-sk": "karagumruk",
"fbc-melgar": "melgar",
"fc-alverca": "alverca",
"fc-andorra": "andorra",
"fc-arges-pitesti": "fc arges",
"fc-arouca": "arouca",
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
"fc-groningen": "groningen",
"fc-heidenheim": "heidenheim",
"fc-hermannstadt": "fc hermannstadt",
"fc-hradec-kralove": "hradec kralove",
"fc-juarez": "juarez",
"fc-kaiserslautern": "kaiserslautern",
"fc-koln": "fc koln",
"fc-lausanne-sport": "lausanne",
"fc-lokomotiv-1929-sofia": "lok. sofia",
"fc-lorient": "lorient",
"fc-lugano": "lugano",
"fc-luzern": "luzern",
"fc-magdeburg": "magdeburg",
"fc-metaloglobus-bucuresti": "metaloglobus bucharest",
"fc-metz": "metz",
"fc-midtjylland": "midtjylland",
"fc-montana": "montana",
"fc-nantes": "nantes",
"fc-nordsjaelland": "nordsjaelland",
"fc-nurnberg": "nurnberg",
"fc-petrolul-ploiesti": "petrolul",
"fc-porto": "fc porto",
"fc-rapid-bucuresti": "fc rapid bucuresti",
"fc-sion": "sion",
"fc-slovacko": "slovacko",
"fc-slovan-liberec": "liberec",
"fc-spartak-varna": "spartak varna",
"fc-st-gallen": "st. gallen",
"fc-st-pauli": "st. pauli",
"fc-thun": "thun",
"fc-twente": "twente",
"fc-universitario-de-vinto": "universitario de vinto",
"fc-universitatea-cluj": "u. cluj",
"fc-uta-arad": "uta arad",
"fc-utrecht": "utrecht",
"fc-viktoria-plzen": "plzen",
"fc-volendam": "fc volendam",
"fc-winterthur": "winterthur",
"fc-zurich": "zurich",
"fcsb": "fcsb",
"fcv-dender-eh": "dender",
"fenerbahce-sk": "fenerbahce",
"feyenoord-rotterdam": "feyenoord",
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
"fortuna-dusseldorf": "dusseldorf",
"fortuna-sittard": "sittard",
"fredrikstad-fk": "fredrikstad",
"fulham-fc": "fulham",
"gais": "gais",
"galatasaray-sk": "galatasaray",
"gaziantep-fk": "gaziantep",
"gd-estoril-praia": "estoril",
"genclerbirligi-sk": "genclerbirligi",
"genoa-cfc": "genoa",
"getafe-cf": "getafe",
"gil-vicente": "gil vicente",
"girona-fc": "girona",
"gks-katowice": "katowice",
"go-ahead-eagles": "g.a. eagles",
"godoy-cruz": "godoy cruz",
"gorica": "gorica",
"gornik-zabrze": "gornik zabrze",
"goztepe-sk": "goztepe",
"granada-cf": "granada",
"grasshopper-club-zurich": "grasshoppers",
"grazer-ak": "grazer ak",
"gremio-football-porto-alagrense": "gremio",
"greuther-furth": "furth",
"hajduk-split": "hajduk split",
"halmstads-bk": "halmstad",
"ham-kam": "hamkam",
"hamburger-sv": "hamburger sv",
"hammarby-if": "hammarby",
"hannover-96": "hannover",
"heart-of-midlothian-fc": "hearts",
"hellas-verona-fc": "verona",
"heracles-almelo": "heracles",
"hertha-berlin": "hertha",
"hibernian-fc": "hibernian",
"hnk-vukovar-1991": "vukovar 1991",
"hoffenheim": "hoffenheim",
"holstein-kiel": "kiel",
"houston-dynamo": "houston dynamo",
"hull-city-fc": "hull",
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
"ipswich-town-fc": "ipswich",
"istanbul-basaksehir-fk": "basaksehir",
"istra-1961": "istra 1961",
"jagiellona-bialystok": "jagiellonia",
"juventus-fc": "juventus",
"kaa-gent": "gent",
"karlsruher-sc": "karlsruher",
"kasimpasa-sk": "kasimpasa",
"kayserispor": "kayserispor",
"kfum-kameratene-oslo": "kfum oslo",
"khaleej-fc": "al khaleej",
"kilmarnock-fc": "kilmarnock",
"kocaelispor": "kocaelispor",
"konyaspor": "konyaspor",
"korona-kielce": "korona",
"krc-genk": "genk",
"kristiansund-bk": "kristiansund",
"kv-mechelen": "kv mechelen",
"kvc-westerlo": "westerlo",
"lask": "lask",
"le-havre-ac": "le havre",
"lech-poznan": "lech",
"lechia-gdansk": "lechia",
"leeds-united-fc": "leeds",
"legia-warsaw": "legia",
"leicester-city-fc": "leicester",
"levante-ud": "levante",
"levski-sofia": "levski",
"lille-osc": "lille",
"liverpool-fc": "liverpool",
"livingston-fc": "livingston",
"llaneros-fc": "llaneros",
"lokomotiv-plovdiv": "lok. plovdiv",
"lokomotiva-zagreb": "lok. zagreb",
"los-angeles-fc": "los angeles fc",
"los-angeles-galaxy": "los angeles galaxy",
"los-chankas-cyc": "los chankas",
"ludogorets": "ludogorets",
"mainz-05": "mainz",
"malaga-cf": "malaga",
"malmo-ff": "malmo ff",
"manchester-city-fc": "man city",
"manchester-united-fc": "man utd",
"mazatlan-fc": "mazatlan fc",
"mfk-karvina": "karvina",
"middlesbrough-fc": "middlesbrough",
"millonarios-fc": "millonarios",
"millwall-fc": "millwall",
"minnesota-united-fc": "minnesota",
"mirassol-fc": "mirassol",
"mjallby-aif": "mjallby",
"mks-pogon-szczecin": "pogon szczecin",
"molde-fk": "molde",
"montpellier-hsc": "montpellier",
"moreirense-fc": "moreirense",
"motherwell-fc": "motherwell",
"motor-lublin": "motor lublin",
"nac-breda": "nac breda",
"nashville-sc": "nashville sc",
"nec-nijmegen": "nijmegen",
"new-england-revolution": "new england revolution",
"new-york-city-fc": "new york city",
"new-york-red-bulls": "new york red bulls",
"newcastle-united-fc": "newcastle",
"norwich-city-fc": "norwich",
"nottingham-forest-fc": "nottm forest",
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
"oxford-united-fc": "oxford utd",
"paris-fc": "paris fc",
"paris-saint-germain-fc": "psg",
"parma-calcio-1913": "parma",
"pec-zwolle": "zwolle",
"pfc-septemvri-sofia": "septemvri sofia",
"philadelphia-union": "philadelphia union",
"piast-gliwice": "piast",
"portland-timbers": "portland timbers",
"portsmouth-fc": "portsmouth",
"preston-north-end-fc": "preston",
"preussen-munster": "munster",
"psv-eindhoven": "psv",
"queens-park-rangers-fc": "qpr",
"queretaro-fc": "queretaro",
"raal-la-louviere": "raal la louviere",
"racing-club-de-avellaneda": "racing club",
"racing-de-ferrol": "racing club ferrol",
"racing-de-santander": "racing santander",
"radomiak-radom": "radomiak radom",
"rakow-czestochowa": "rakow",
"randers-fc": "randers",
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
"real-sociedad-b": "real sociedad b",
"real-sociedad": "real sociedad",
"real-valladolid": "valladolid",
"real-zaragoza": "zaragoza",
"red-bull-bragantino": "bragantino",
"red-bull-salzburg": "salzburg",
"rheindorf-altach": "altach",
"rijeka": "rijeka",
"rio-ave-fc": "rio ave",
"rionegro-aguilas": "aguilas",
"rosenborg-bk": "rosenborg",
"royal-antwerp-fc": "antwerp",
"royal-charleroi-sc": "charleroi",
"rsc-anderlecht": "anderlecht",
"rts-widzew-lodz": "widzew lodz",
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
"sbv-excelsior": "excelsior",
"sc-freiburg": "freiburg",
"sc-heerenveen": "heerenveen",
"sc-paderborn": "paderborn",
"sc-telstar": "telstar",
"schalke-04": "schalke",
"sd-eibar": "eibar",
"sd-huesca": "huesca",
"seattle-sounders-fc": "seattle sounders",
"servette-fc": "servette",
"sevilla-fc": "sevilla",
"sheffield-united-fc": "sheff utd",
"sheffield-wednesday-fc": "sheff wed",
"silkeborg-if": "silkeborg",
"sint-truidense-vv": "st. truiden",
"sk-brann": "brann",
"sk-sigma-olomouc": "sigma olomouc",
"slaven-belupo": "slaven belupo",
"slavia-prague": "slavia prague",
"slavia-sofia": "slavia sofia",
"sociedade-esportiva-palmeiras": "palmeiras",
"sonderjyske": "sonderjyske",
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
"sv-ried": "ried",
"sv-zulte-waregem": "waregem",
"swansea-city-afc": "swansea",
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
"us-cremonese": "cremonese",
"us-lecce": "lecce",
"us-sassuolo-calcio": "sassuolo",
"valencia-cf": "valencia",
"valerenga-fotball": "valerenga",
"vancouver-whitecaps-fc": "vancouver whitecaps",
"varazdin": "varazdin",
"vejle-bk": "vejle",
"venezia-fc": "venezia",
"vfb-stuttgart": "stuttgart",
"vfl-bochum": "bochum",
"vfl-wolfsburg": "wolfsburg",
"viborg-ff": "viborg",
"viking-fk": "viking",
"villarreal-cf": "villarreal",
"vitoria-de-guimaraes": "guimaraes",
"watford-fc": "watford",
"werder-bremen": "bremen",
"west-bromwich-albion-fc": "west brom",
"west-ham-united-fc": "west ham",
"wisla-plock": "wisla plock",
"wolfsberger-ac": "wolfsberger",
"wolverhampton-wanderers-fc": "wolves",
"wrexham-afc": "wrexham",
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
            "goles_local", "goles_visitante", "xg_favor", "xg_contra", "shots_favor", "a_puerta_favor",
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

# === GRÁFICOS DE TENDENCIA (NUEVA FUNCIÓN) ===
def generar_grafico_tendencia(df, equipo_nombre, tipo_partido):
    if df.empty:
        st.warning(f"No hay datos de últimos partidos para {equipo_nombre}.")
        return

    # 1. Definir columnas de goles y rival
    if tipo_partido == "local":
        goles_favor_col = "goles_local"
        goles_contra_col = "goles_visitante"
        rival_col = "visitante"
    else: # visitante
        goles_favor_col = "goles_visitante"
        goles_contra_col = "goles_local"
        rival_col = "equipo_local"

    # Preparar el eje X (Rival y número de partido para mejor visualización)
    # Se usa el nombre del rival en mayúsculas para las etiquetas.
    x_data = [f"{rival.upper()}" for rival in df[rival_col]]

    # --- GRÁFICO DE ATAQUE (A FAVOR) ---
    fig_ataque = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Barra: Goles Anotados
    fig_ataque.add_trace(
        go.Bar(
            x=x_data, y=df[goles_favor_col], name='Goles Anotados',
            text=df[goles_favor_col], textposition='auto',
            marker_color='blue' if tipo_partido == "local" else 'red'
        ),
        secondary_y=False,
    )

    # Línea 1: xG a Favor
    fig_ataque.add_trace(
        go.Scatter(
            x=x_data, y=df["xg_favor"], name='xG', mode='lines+markers',
            line=dict(color='green', width=3),
            text=df["xg_favor"].round(2), textposition="top center"
        ),
        secondary_y=True,
    )
    
    # Línea 2: Tiros a Puerta (A Favor)
    fig_ataque.add_trace(
        go.Scatter(
            x=x_data, y=df["a_puerta_favor"], name='Tiros a Puerta', mode='lines+markers',
            line=dict(color='orange', width=3),
            text=df["a_puerta_favor"].round(1), textposition="bottom center"
        ),
        secondary_y=True,
    )
    
    mediana_goles = df[goles_favor_col].median()
    
    fig_ataque.add_hline(
        y=mediana_goles,
        line_dash="dot",
        line_color="gray",
        annotation_text=f"Mediana: {mediana_goles:.1f}",
        annotation_position="top left"
    )

    # Configuración del Eje y Título
    fig_ataque.update_layout(
        title_text=f"**{equipo_nombre}** - Tendencia de ATAQUE (vs Rivales)",
        xaxis_title="Rivales Enfrentados (Partidos Recientes)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100)
    )
    fig_ataque.update_yaxes(title_text="Goles Anotados", secondary_y=False, showgrid=False)
    fig_ataque.update_yaxes(title_text="xG / Tiros a Puerta", secondary_y=True, showgrid=True)
    st.plotly_chart(fig_ataque, use_container_width=True, config={"staticPlot": True})


    # --- GRÁFICO DE DEFENSA (EN CONTRA) ---
    # Nota: No tenemos la columna 'a_puerta_contra', por lo que usaremos 'xg_favor' como proxy de 'Presión/Control de Juego'
    # en la segunda línea para cumplir con la estructura de dos líneas, junto con xG_Contra.
    fig_defensa = make_subplots(specs=[[{"secondary_y": True}]])

    # Barra: Goles Recibidos
    fig_defensa.add_trace(
        go.Bar(
            x=x_data, y=df[goles_contra_col], name='Goles Recibidos',
            text=df[goles_contra_col], textposition='auto',
            marker_color='darkred'
        ),
        secondary_y=False,
    )

    # Línea 1: xG en Contra
    fig_defensa.add_trace(
        go.Scatter(
            x=x_data, y=df["xg_contra"], name='xG en Contra', mode='lines+markers',
            line=dict(color='purple', width=3),
            text=df["xg_contra"].round(2), textposition="top center"
        ),
        secondary_y=True,
    )
    
    # Línea 2: Tiros a Puerta *EN CONTRA* (Usando Shots Favor como PROXY/Control)
    fig_defensa.add_trace(
        go.Scatter(
            x=x_data, y=df["shots_favor"], name='Remates Totales', mode='lines+markers',
            line=dict(color='teal', width=3),
            text=df["shots_favor"].round(1), textposition="bottom center"
        ),
        secondary_y=True,
    )
    
    mediana_goles_contra = df[goles_contra_col].median()
    fig_defensa.add_hline(
        y=mediana_goles_contra,
        line_dash="dot",
        line_color="gray",
        annotation_text=f"Mediana: {mediana_goles_contra:.1f}",
        annotation_position="top left"
    )


    # Configuración del Eje y Título
    fig_defensa.update_layout(
        title_text=f"**{equipo_nombre}** - Tendencia de DEFENSA (vs Rivales)",
        xaxis_title="Rivales Enfrentados (Partidos Recientes)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100)
    )
    fig_defensa.update_yaxes(title_text="Goles Recibidos", secondary_y=False, showgrid=False)
    fig_defensa.update_yaxes(title_text="xG en Contra / Remates Totales", secondary_y=True, showgrid=True)
    st.plotly_chart(fig_defensa, use_container_width=True, config={"staticPlot": True})


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
    xg_favor_col = "xg_favor"
    xg_contra_col = "xg_contra"
    remates_favor_col = "shots_favor"
    a_puerta_favor_col = "a_puerta_favor"

    # Goles y remates
    media_gol = round(df_calculo[goles_a_favor_col].mean(), 2)
    media_gol_recibido = round(df_calculo[goles_en_contra_col].mean(), 2)
    media_gol_1t = round(df_calculo[goles_ht_favor_col].mean(), 2)
    media_gol_1t_recibido = round(df_calculo[goles_ht_contra_col].mean(), 2)
    media_gol_2t = round(df_calculo[goles_st_favor_col].mean(), 2)
    media_gol_2t_recibido = round(df_calculo[goles_st_contra_col].mean(), 2)
    promedio_remates = round(df_calculo[remates_favor_col].mean(), 1)
    promedio_tiros_puerta = round(df_calculo[a_puerta_favor_col].mean(), 1)
    media_xg_favor = round(df_calculo[xg_favor_col].mean(), 2)
    media_xg_contra = round(df_calculo[xg_contra_col].mean(), 2)

    # Eficiencias
    eficiencia_ofensiva = round((media_gol / media_xg_favor) * 100, 1) if media_xg_favor > 0 else 0
    eficiencia_defensiva = round((media_gol_recibido / media_xg_contra) * 100, 1) if media_xg_contra > 0 else 0

    # Funciones para calcular rachas genéricas
    def calcular_racha(df, col, promedio):
        racha = 0
        if df[col].empty:
            return 0
        cond = df[col] >= promedio
        for i in range(len(cond) - 1, -1, -1):
            if cond.iloc[i]:
                racha += 1
            else:
                break
        return racha

    def calcular_racha_booleana(df, cond):
        racha = 0
        if cond.empty:
            return 0
        for i in range(len(cond) - 1, -1, -1):
            if cond.iloc[i]:
                racha += 1
            else:
                break
        return racha


    # Rachas para las medias de goles por tiempo
    racha_media_gol = calcular_racha(df_calculo, goles_a_favor_col, media_gol)
    racha_media_gol_recibido = calcular_racha(df_calculo, goles_en_contra_col, media_gol_recibido)
    racha_media_gol_1t = calcular_racha(df_calculo, goles_ht_favor_col, media_gol_1t)
    racha_media_gol_1t_recibido = calcular_racha(df_calculo, goles_ht_contra_col, media_gol_1t_recibido)
    racha_media_gol_2t = calcular_racha(df_calculo, goles_st_favor_col, media_gol_2t)
    racha_media_gol_2t_recibido = calcular_racha(df_calculo, goles_st_contra_col, media_gol_2t_recibido)

    # Rachas de xG y remates
    racha_media_xg_favor = calcular_racha(df_calculo, xg_favor_col, media_xg_favor)
    racha_media_xg_contra = calcular_racha(df_calculo, xg_contra_col, media_xg_contra)
    racha_prom_remates = calcular_racha(df_calculo, remates_favor_col, promedio_remates)
    racha_prom_tiros_puerta = calcular_racha(df_calculo, a_puerta_favor_col, promedio_tiros_puerta)

    # BTTS y Over Goles
    btts_cond = (df_calculo[goles_a_favor_col] > 0) & (df_calculo[goles_en_contra_col] > 0)
    btts = btts_cond.mean() * 100
    racha_btts = calcular_racha_booleana(df_calculo, btts_cond)

    gol_ht_cond = (df_calculo[goles_ht_favor_col] + df_calculo[goles_ht_contra_col]) > 0
    gol_ht = gol_ht_cond.mean() * 100
    racha_gol_ht = calcular_racha_booleana(df_calculo, gol_ht_cond)

    over_1_5_total_cond = (df_calculo[goles_a_favor_col] + df_calculo[goles_en_contra_col]) > 1.5
    over_1_5_total = over_1_5_total_cond.mean() * 100
    racha_over_1_5_total = calcular_racha_booleana(df_calculo, over_1_5_total_cond)

    over_2_5_cond = (df_calculo[goles_a_favor_col] + df_calculo[goles_en_contra_col]) > 2.5
    over_2_5_goles = over_2_5_cond.mean() * 100
    racha_over_2_5 = calcular_racha_booleana(df_calculo, over_2_5_cond)

    over_1_5_ht_cond = (df_calculo[goles_ht_favor_col] + df_calculo[goles_ht_contra_col]) > 1.5
    over_1_5_ht = over_1_5_ht_cond.mean() * 100
    racha_over_1_5_ht = calcular_racha_booleana(df_calculo, over_1_5_ht_cond)

    return {
        "Estadística": [
            "Media Gol",
            "Media Gol Recibido",
            "Media Gol 1T",
            "Media Gol 1T Recibido",
            "Media Gol 2T",
            "Media Gol 2T Recibido",
            "Media xG",
            "Media xG Recibido",
            "Eficiencia Ofensiva",
            "Eficiencia Defensiva",
            "BTTS",
            "Gol HT",
            "Over 1.5 HT",
            "Over 1.5 Goles",
            "Over 2.5 Goles",
            "Promedio Remates",
            "Promedio Tiros a Puerta"
        ],
        f"{equipo_nombre} {tipo_partido.title()}": [
            media_gol,
            media_gol_recibido,
            media_gol_1t,
            media_gol_1t_recibido,
            media_gol_2t,
            media_gol_2t_recibido,
            media_xg_favor,
            media_xg_contra,
            f"{eficiencia_ofensiva:.1f}%",
            f"{eficiencia_defensiva:.1f}%",
            f"{btts:.1f}%",
            f"{gol_ht:.1f}%",
            f"{over_1_5_ht:.1f}%",
            f"{over_1_5_total:.1f}%",
            f"{over_2_5_goles:.1f}%",
            promedio_remates,
            promedio_tiros_puerta
        ],
        "Racha": [
            racha_media_gol,
            racha_media_gol_recibido,
            racha_media_gol_1t,
            racha_media_gol_1t_recibido,
            racha_media_gol_2t,
            racha_media_gol_2t_recibido,
            racha_media_xg_favor,
            racha_media_xg_contra,
            "N/A", # Eficiencia ofensiva no tiene racha
            "N/A", # Eficiencia defensiva no tiene racha
            racha_btts,
            racha_gol_ht,
            racha_over_1_5_ht,
            racha_over_1_5_total,
            racha_over_2_5,
            racha_prom_remates,
            racha_prom_tiros_puerta
        ],
    }

def resaltar_estadistica(df_stats):
    def color_fila(row):
        # Nombres de las estadísticas que tendrán color condicional por porcentaje
        estadisticas_porcentaje = [
            "BTTS", "Gol HT", "Over 1.5 HT", "Over 1.5 Goles", "Over 2.5 Goles"
        ]

        # Verificar si la fila actual es una de las estadísticas de porcentaje
        if row["Estadística"] in estadisticas_porcentaje:
            try:
                # Convertir el valor de porcentaje a un float
                porcentaje_str = row[df_stats.columns[1]].replace("%", "").strip()
                porcentaje = float(porcentaje_str)
                racha = row["Racha"]
                
                # Definir los colores
                amarillo = "background-color: #fff9c4"
                verde = "background-color: #c8e6c9"
                azul_claro = "background-color: #bbdefb" # Un color azul claro

                # Aplicar la lógica de color condicional
                if porcentaje >= 75 and isinstance(racha, (int, float)) and racha >= 3:
                    return [azul_claro] * len(row)
                elif porcentaje >= 75:
                    return [verde] * len(row)
                elif 60 <= porcentaje < 75:
                    return [amarillo] * len(row)
                else:
                    return [""] * len(row)
            except (ValueError, KeyError):
                # En caso de error, no aplicar ningún color
                return [""] * len(row)
        
        # Lógica original para las demás estadísticas (basada en Racha)
        val = row["Racha"]
        if isinstance(val, (int, float)):
            if 2 <= val <= 4:
                return ["background-color: #fff9c4"] * len(row)
            elif val >= 5:
                return ["background-color: #c8e6c9"] * len(row)
        return [""] * len(row)
    
    styler = df_stats.style.apply(color_fila, axis=1)

    # Formato de números con 1 decimal
    styler = styler.format(precision=1)
    
    return styler

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

    st.markdown("## 📊 Estadísticas Detalladas de los Últimos 10 Partidos")
    col_local_stats, col_visitante_stats = st.columns(2)

    with col_local_stats:
        st.subheader("🔵 Equipo Local")
        if not df_stats_local.empty:
            st.table(resaltar_estadistica(df_stats_local))

    with col_visitante_stats:
        st.subheader("🔴 Equipo Visitante")
        if not df_stats_visitante.empty:
            st.table(resaltar_estadistica(df_stats_visitante))

    st.markdown("---")
    st.markdown("## 📈 Tendencia de Juego (Ataque y Defensa)")

    col_local_chart, col_visitante_chart = st.columns(2)

    with col_local_chart:
        st.subheader(f"🔵 {equipo_local_nombre} (Local) - Gráficos")
        generar_grafico_tendencia(df_local_all, equipo_local_nombre, "local")

    with col_visitante_chart:
        st.subheader(f"🔴 {equipo_visitante_nombre} (Visitante) - Gráficos")
        generar_grafico_tendencia(df_visitante_all, equipo_visitante_nombre, "visitante")


    st.markdown("---")
    st.markdown("## 🔮 Predicción del Partido")

    # Lógica de predicción y sugerencias
    resultados = calcular_probabilidades_equipo(df_local_all, df_visitante_all)
    mostrar_resultados(resultados, df_local_all, df_visitante_all)

else:
    st.warning("Selecciona un partido para ver el análisis.")