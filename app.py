from typing import List, Union
import numpy as np
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
"ac-omonia": "omonia",
"ac-pisa-1909": "pisa",
"academia-del-balompie-boliviano": "abb",
"acf-fiorentina": "fiorentina",
"ad-ceuta-fc": "ceuta",
"adc-juan-pablo-ii-college": "juan pablo ii",
"ae-kifisia-fc": "kifisia",
"aek-athens-fc": "aek",
"aek-larnaca-fc": "aek larnaca",
"ael-fc": "ael larissa",
"ael-limassol": "ael limassol",
"afc-ajax": "ajax",
"afc-bournemouth": "bournemouth",
"afc-unirea-slobozia": "unirea slobozia",
"aik": "aik stockholm",
"aj-auxerre": "auxerre",
"akritas-chlorakas": "chloraka",
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
"anorthosis-famagusta-fc": "anorthosis",
"antalyaspor": "antalyaspor",
"apoel-fc": "apoel",
"apollon-limassol": "apollon",
"arda-kardzhali": "arda",
"argentinos-juniors": "argentinos jrs",
"aris-limassol-fc": "aris limassol",
"aris-thessaloniki-fc": "aris",
"arka-gdynia": "arka",
"arminia-bielefeld": "bielefeld",
"arsenal-fc": "arsenal",
"as-monaco-fc": "monaco",
"as-roma": "as roma",
"asc-otelul-galati": "otelul",
"asociacion-deportiva-tarma": "ad tarma",
"asteras-tripolis-fc": "asteras t.",
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
"atromitos-fc": "atromitos",
"audax-italiano": "a. italiano",
"austin-fc": "austin fc",
"austria-vienna": "austria vienna",
"avs-futebol-sad": "afs",
"ayacucho-fc": "ayacucho",
"az-alkmaar": "alkmaar",
"barcelona-sc": "barcelona sc",
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
"cd-cuenca": "dep. cuenca",
"cd-el-nacional": "el nacional",
"cd-guadalajara": "guadalajara",
"cd-huachipato": "huachipato",
"cd-la-equidad": "la equidad",
"cd-leganes": "leganes",
"cd-mirandes": "mirandes",
"cd-nacional": "nacional",
"cd-palestino": "palestino",
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
"cs-emelec": "emelec",
"cs-universitatea-craiova": "univ. craiova",
"csd-independiente-del-valle": "ind. del valle",
"csd-macara": "macara",
"cska-sofia": "cska sofia",
"cultural-y-deportiva-leonesa": "cultural leonesa",
"cusco-fc": "cusco",
"damac-fc": "damac",
"darmstadt-98": "darmstadt",
"dc-united": "dc united",
"defensa-y-justicia": "defensa y justicia",
"degerfors-if": "degerfors",
"delfin-sc": "delfin",
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
"enosis-neon-paralimni-fc": "paralimni",
"envigado-fc": "envigado",
"esporte-clube-bahia": "bahia",
"esporte-clube-juventude": "juventude",
"esporte-clube-vitoria": "vitoria",
"ethnikos-achna-fc": "achnas",
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
"krasava-eny-ypsonas-fc": "ypsonas",
"krc-genk": "genk",
"kristiansund-bk": "kristiansund",
"kv-mechelen": "kv mechelen",
"kvc-westerlo": "westerlo",
"lask": "lask",
"ldu-quito": "ldu quito",
"le-havre-ac": "le havre",
"lech-poznan": "lech",
"lechia-gdansk": "lechia",
"leeds-united-fc": "leeds",
"legia-warsaw": "legia",
"leicester-city-fc": "leicester",
"levadiakos-fc": "levadiakos",
"levante-ud": "levante",
"levski-sofia": "levski",
"libertad-fc": "libertad",
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
"manta-fc": "manta",
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
"moreirense-fc": "moreirense",
"motherwell-fc": "motherwell",
"motor-lublin": "motor lublin",
"mushuc-runa-sc": "mushuc runa",
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
"ofi-crete-fc": "ofi crete",
"ogc-nice": "nice",
"oh-leuven": "leuven",
"olympiacos-fc": "olympiacos",
"olympiakos-nicosia": "ol. nicosia",
"olympique-de-marseille": "marseille",
"olympique-lyonnais": "lyon",
"omonia-aradippou": "omonia aradippou",
"once-caldas": "once caldas",
"orense-sc": "orense",
"orlando-city-sc": "orlando city",
"osijek": "osijek",
"osters-if": "oster",
"oxford-united-fc": "oxford utd",
"pafos-fc": "pafos",
"panathinaikos-fc": "panathinaikos",
"panetolikos-fc": "panetolikos",
"panserraikos-fc": "panserraikos",
"paok-fc": "paok",
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
"real-oviedo": "oviedo",
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
"sd-aucas": "aucas",
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
"tecnico-universitario": "tecnico u.",
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
"vfb-stuttgart": "stuttgart",
"vfl-bochum": "bochum",
"vfl-wolfsburg": "wolfsburg",
"viborg-ff": "viborg",
"viking-fk": "viking",
"villarreal-cf": "villarreal",
"vinotinto-fc-ecuador": "vinotinto",
"vitoria-de-guimaraes": "guimaraes",
"volos-fc": "volos",
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

# === FUNCIÓN BASE: CÁLCULO LAMBDA PONDERADA (30/30/40) SOBRE GOLES REALES ===
def calcular_lambda_ponderada_poisson(df: pd.DataFrame, col_goles: str) -> float:
    """
    Calcula la tasa de goles (lambda) usando el promedio ponderado: 
    30% U-10, 30% U-5, 40% U-3.
    """
    goles_3: List[Union[int, float]] = df[col_goles].tail(3).dropna().tolist()
    goles_5: List[Union[int, float]] = df[col_goles].tail(5).dropna().tolist()
    goles_all: List[Union[int, float]] = df[col_goles].dropna().tolist()

    # Calcular el promedio de los últimos 3 partidos
    if goles_3:
        avg_3 = np.array(goles_3, dtype=float).mean()
    else:
        avg_3 = 0.0
        print(f"Warning: No se encontraron datos para los últimos 3 partidos en '{col_goles}'. Usando promedio de 0.0 para este segmento.")

    # Calcular el promedio de los últimos 6 partidos
    if goles_5:
        avg_5 = np.array(goles_5, dtype=float).mean()
    else:
        avg_5 = 0.0
        print(f"Warning: No se encontraron datos para los últimos 5 partidos en '{col_goles}'. Usando promedio de 0.0 para este segmento.")

    # Calcular el promedio de todos los partidos
    if goles_all:
        avg_all = np.array(goles_all, dtype=float).mean()
    else:
        return 0.0
    
    WEIGHT_3 = 0.20
    WEIGHT_5 = 0.30
    WEIGHT_ALL = 0.50
    
    lambda_ponderada = (avg_3 * WEIGHT_3) + (avg_5 * WEIGHT_5) + (avg_all * WEIGHT_ALL)
    
    return lambda_ponderada

def calcular_ajuste_xg(df, col_goles, col_xg, partidos_recientes = 5):
    
    if df.empty or df[col_xg].sum() == 0:
        return 1.0 
    
    xg_prom = df[col_xg].mean()
    
    efectividad_general = (df[col_goles].sum() / df[col_xg].sum()) if df[col_xg].sum() > 0 else 1.0

    df_recientes = df.head(partidos_recientes)
    xg_forma = df_recientes[col_xg].mean()
    goles_forma = df_recientes[col_goles].mean()
    efectividad_forma = (df_recientes[col_goles].sum() / df_recientes[col_xg].sum()) if df_recientes[col_xg].sum() > 0 else 1.0

    peso_xg_base = 0.4
    peso_efectividad_general = 0.3
    peso_forma = 0.3   

    ajuste = (
        (xg_prom * peso_xg_base) +
        (xg_prom * efectividad_general * peso_efectividad_general) +
        (xg_forma * efectividad_forma * peso_forma)
    )
    
    goles_promedio = df[col_goles].mean() if df[col_goles].mean() > 0 else 1.0

    # Factor de escalado
    factor_ajuste = ajuste / goles_promedio
    
    return factor_ajuste


# === FUNCIÓN DE COMBINACIÓN HÍBRIDA ===
def calcular_lambda_hibrida(df, col_goles, col_xg):
    """Combina la ponderación de Goles Reales (30/30/40) con el Factor de Ajuste xG/Efectividad."""
    
    # 1. Calcular Lambda Ponderada de Goles Reales (Sensibilidad a la forma)
    lambda_real = calcular_lambda_ponderada_poisson(df, col_goles)
    
    # 2. Calcular Factor de Ajuste basado en xG/Efectividad (Estabilidad y Calidad)
    factor_ajuste = calcular_ajuste_xg(df, col_goles, col_xg)
    
    # 3. Combinación (Ajuste el lambda real por el factor de calidad)   
    lambda_hibrida = lambda_real * factor_ajuste
    
    # Evitar valores negativos o excesivamente bajos
    return max(0.1, lambda_hibrida) 


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
    
    # Usamos los últimos 10 partidos para las estadísticas de remates/xg
    df_recientes = df.head(10)
    
    stats = {
        # Aquí debes usar la columna de goles real (local o visitante) en función de 'tipo'
        "Prom. Goles": round(df_recientes["goles_local"].mean(), 2) if tipo == "local" else round(df_recientes["goles_visitante"].mean(), 2),
        "Prom. xG": round(df_recientes["xg_favor"].mean(), 2),
        "Prom. Remates": round(df_recientes["shots_favor"].mean(), 1),
        "A puerta": round(df_recientes["a_puerta_favor"].mean(), 1),
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

# === AUXILIARES PARA MÉTRICAS AVANZADAS ===
def media_ultimos(df, col, n):
    if col not in df.columns or df.empty:
        return 0.0
    return float(df[col].tail(n).mean())

def blend_10_5_3(df, col):
    m10 = media_ultimos(df, col, 10)
    m5 = media_ultimos(df, col, 5)
    m3 = media_ultimos(df, col, 3)
    return 0.5 * m10 + 0.3 * m5 + 0.2 * m3

def calcular_q_p(df, shots_col, sot_col, xg_col, n=5):
    df5 = df.tail(n)
    # Evitar divisiones por cero con un epsilon pequeño
    shots = df5[shots_col].sum() if shots_col in df5.columns else 0.0
    sot = df5[sot_col].sum() if sot_col in df5.columns else 0.0
    xg = df5[xg_col].sum() if xg_col in df5.columns else 0.0
    eps = 1e-6
    q = xg / max(shots, eps)
    p = sot / max(shots, eps)
    return q, p

def poisson_prob_over_under(lmbda, line, max_k):    
    from math import floor
    if lmbda <= 0:
        return 0.0, 0.0
    k_max = max_k
    k_line = int(floor(line))
    k_line = min(k_line, k_max)
    pmfs = [poisson.pmf(k, lmbda) for k in range(0, k_max + 1)]
    cdf_line = sum(pmfs[:k_line + 1])
    p_under = cdf_line
    p_over = 1 - cdf_line
    return p_under * 100, p_over * 100

def poisson_prob_total_over_under(lambda_local, lambda_visitante, line, max_k):
    lmbda = lambda_local + lambda_visitante
    return poisson_prob_over_under(lmbda, line, max_k)

def poisson_prob_1x2_y_dobles(lambda_local, lambda_visitante, max_goals=8):
    prob_local = prob_empate = prob_visitante = 0.0
    for gl in range(0, max_goals + 1):
        for gv in range(0, max_goals + 1):
            p = poisson.pmf(gl, lambda_local) * poisson.pmf(gv, lambda_visitante)
            if gl > gv:
                prob_local += p
            elif gl == gv:
                prob_empate += p
            else:
                prob_visitante += p
    pL = prob_local * 100
    pE = prob_empate * 100
    pV = prob_visitante * 100
    p1x = (prob_local + prob_empate) * 100
    p12 = (prob_local + prob_visitante) * 100
    px2 = (prob_empate + prob_visitante) * 100
    return {
        "1": round(pL, 1),
        "X": round(pE, 1),
        "2": round(pV, 1),
        "1X": round(p1x, 1),
        "12": round(p12, 1),
        "X2": round(px2, 1),
    }

def prob_btts(lambda_local, lambda_visitante, max_goals=8):
    p_btts = 0.0
    for gl in range(1, max_goals + 1):
        for gv in range(1, max_goals + 1):
            p = poisson.pmf(gl, lambda_local) * poisson.pmf(gv, lambda_visitante)
            p_btts += p
    return round(p_btts * 100, 1)


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
    
    # === MÉTRICAS AVANZADAS: ATAQUE, DEFENSA, REMATES Y SOT ===

def calcular_metricas_avanzadas(df_local, df_visitante):
    if df_local.empty or df_visitante.empty:
        return None

    # --- BLENDS DE GOLES Y xG (LOCAL) ---
    GF_local = blend_10_5_3(df_local, "goles_local")
    xGF_local = blend_10_5_3(df_local, "xg_favor")
    GC_local = blend_10_5_3(df_local, "goles_visitante")
    xGC_local = blend_10_5_3(df_local, "xg_contra")

    # --- BLENDS DE GOLES Y xG (VISITANTE) ---
    GF_vis = blend_10_5_3(df_visitante, "goles_visitante")
    xGF_vis = blend_10_5_3(df_visitante, "xg_favor")
    GC_vis = blend_10_5_3(df_visitante, "goles_local")
    xGC_vis = blend_10_5_3(df_visitante, "xg_contra")

    # --- CALIDAD Y PRECISIÓN DE TIRO (SOLO ULT. 5 PARTIDOS) ---
    # Ataque local
    Q_shot_att_local, P_att_local = calcular_q_p(
        df_local, "shots_favor", "a_puerta_favor", "xg_favor", n=5
    )
    # Defensa local
    Q_shot_def_local, P_def_local = calcular_q_p(
        df_local, "shots_contra", "a_puerta_contra", "xg_contra", n=5
    )
    # Ataque visitante
    Q_shot_att_vis, P_att_vis = calcular_q_p(
        df_visitante, "shots_favor", "a_puerta_favor", "xg_favor", n=5
    )
    # Defensa visitante
    Q_shot_def_vis, P_def_vis = calcular_q_p(
        df_visitante, "shots_contra", "a_puerta_contra", "xg_contra", n=5
    )

    # --- ATAQUE Y DEFENSA BASE ---
    Ataque_base_local = 0.7 * xGF_local + 0.3 * GF_local
    Defensa_base_local = 0.7 * xGC_local + 0.3 * GC_local

    Ataque_base_vis = 0.7 * xGF_vis + 0.3 * GF_vis
    Defensa_base_vis = 0.7 * xGC_vis + 0.3 * GC_vis

    # --- FACTORES DE CAPADO ---
    import math

    F_att_local = math.sqrt(max(Q_shot_att_local, 0)) * math.sqrt(max(P_att_local, 0))
    F_def_local = math.sqrt(max(Q_shot_def_local, 0)) * math.sqrt(max(P_def_local, 0))

    F_att_vis = math.sqrt(max(Q_shot_att_vis, 0)) * math.sqrt(max(P_att_vis, 0))
    F_def_vis = math.sqrt(max(Q_shot_def_vis, 0)) * math.sqrt(max(P_def_vis, 0))

    def cap_factor(F):
        if F > 1.1:
            return 1.1
        if F < 0.9:
            return 0.9
        return F

    F_att_local_c = cap_factor(F_att_local)
    F_def_local_c = cap_factor(F_def_local)
    F_att_vis_c = cap_factor(F_att_vis)
    F_def_vis_c = cap_factor(F_def_vis)

    # --- ATAQUE Y DEFENSA FINALES ---
    Ataque_final_local = Ataque_base_local * F_att_local_c
    Defensa_final_local = Defensa_base_local * F_def_local_c

    Ataque_final_vis = Ataque_base_vis * F_att_vis_c
    Defensa_final_vis = Defensa_base_vis * F_def_vis_c

    # --- LAMBDAS CRUZADOS (GOLES) ---
    lambda_local_new = (Ataque_final_local + Defensa_final_vis) / 2.0
    lambda_vis_new = (Ataque_final_vis + Defensa_final_local) / 2.0

    # Evitar negativos
    lambda_local_new = max(lambda_local_new, 0.01)
    lambda_vis_new = max(lambda_vis_new, 0.01)

    # --- PRECISIÓN DEL PARTIDO ---
    P_match_local = (P_att_local + P_def_local) / 2.0
    P_match_vis = (P_att_vis + P_def_vis) / 2.0

    # --- REMATES ATAQUE (ULT. 5 PARTIDOS) ---
    df_local_5 = df_local.tail(5)
    df_vis_5 = df_visitante.tail(5)

    shots_fav_local = df_local_5["shots_favor"].mean() if "shots_favor" in df_local_5.columns else 0.0
    shots_contra_local = df_local_5["shots_contra"].mean() if "shots_contra" in df_local_5.columns else 0.0

    shots_fav_vis = df_vis_5["shots_favor"].mean() if "shots_favor" in df_vis_5.columns else 0.0
    shots_contra_vis = df_vis_5["shots_contra"].mean() if "shots_contra" in df_vis_5.columns else 0.0

    Remates_att_local = (shots_fav_local + shots_contra_vis) / 2.0
    Remates_att_vis = (shots_fav_vis + shots_contra_local) / 2.0

    # --- TIROS A PUERTA ESPERADOS ---
    SoT_local = Remates_att_local * P_match_local
    SoT_vis = Remates_att_vis * P_match_vis

    # Evitar negativos
    Remates_att_local = max(Remates_att_local, 0.01)
    Remates_att_vis = max(Remates_att_vis, 0.01)
    SoT_local = max(SoT_local, 0.01)
    SoT_vis = max(SoT_vis, 0.01)

    return {
        "GF_local_blend": GF_local,
        "xGF_local_blend": xGF_local,
        "GC_local_blend": GC_local,
        "xGC_local_blend": xGC_local,
        "GF_vis_blend": GF_vis,
        "xGF_vis_blend": xGF_vis,
        "GC_vis_blend": GC_vis,
        "xGC_vis_blend": xGC_vis,
        "Q_shot_att_local": Q_shot_att_local,
        "P_att_local": P_att_local,
        "Q_shot_def_local": Q_shot_def_local,
        "P_def_local": P_def_local,
        "Q_shot_att_vis": Q_shot_att_vis,
        "P_att_vis": P_att_vis,
        "Q_shot_def_vis": Q_shot_def_vis,
        "P_def_vis": P_def_vis,
        "Ataque_base_local": Ataque_base_local,
        "Defensa_base_local": Defensa_base_local,
        "Ataque_base_vis": Ataque_base_vis,
        "Defensa_base_vis": Defensa_base_vis,
        "F_att_local": F_att_local_c,
        "F_def_local": F_def_local_c,
        "F_att_vis": F_att_vis_c,
        "F_def_vis": F_def_vis_c,
        "Ataque_final_local": Ataque_final_local,
        "Defensa_final_local": Defensa_final_local,
        "Ataque_final_vis": Ataque_final_vis,
        "Defensa_final_vis": Defensa_final_vis,
        "lambda_local_new": lambda_local_new,
        "lambda_vis_new": lambda_vis_new,
        "P_match_local": P_match_local,
        "P_match_vis": P_match_vis,
        "Remates_att_local": Remates_att_local,
        "Remates_att_vis": Remates_att_vis,
        "SoT_local": SoT_local,
        "SoT_vis": SoT_vis,
    }


# === FUNCIÓN PRINCIPAL (Actualizada para usar la nueva lambda híbrida) ===
def calcular_probabilidades_equipo(df_local, df_visitante):
    if df_local.empty or df_visitante.empty:
        return None

    # NO USAMOS seleccionar_df. El DF ya está ordenado del más reciente al más antiguo.
    
    # 1. Calcular Lambdas HÍBRIDAS (Goles Ponderados 30/30/40 + Ajuste xG/Efectividad)
    lambda_local = calcular_lambda_hibrida(df_local, "goles_local", "xg_favor")
    lambda_visitante = calcular_lambda_hibrida(df_visitante, "goles_visitante", "xg_favor")

    # Cálculos por Mitad (Usamos la misma lógica híbrida)
    lambda_local_1t = calcular_lambda_hibrida(df_local, "1t_goles_favor", "xg_favor")
    lambda_visitante_1t = calcular_lambda_hibrida(df_visitante, "1t_goles_favor", "xg_favor")
    lambda_local_2t = calcular_lambda_hibrida(df_local, "2t_goles_favor", "xg_favor")
    lambda_visitante_2t = calcular_lambda_hibrida(df_visitante, "2t_goles_favor", "xg_favor")

    # Calculamos las probabilidades de resultado
    prob_resultados = calcular_probabilidades_resultado(lambda_local, lambda_visitante)

    # 2. Datos de forma para el resumen (últimos 5 partidos)
    df_local_5 = df_local.head(5)
    df_visitante_5 = df_visitante.head(5)

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

        "Prom. Remates Local": round(df_local_5["shots_favor"].mean(), 1),
        "Prom. Remates Visitante": round(df_visitante_5["shots_favor"].mean(), 1),
        "Total Remates": round((df_local_5["shots_favor"].mean() + df_visitante_5["shots_favor"].mean()), 1),

        "A puerta Local": round(df_local_5["a_puerta_favor"].mean(), 1),
        "A puerta Visitante": round(df_visitante_5["a_puerta_favor"].mean(), 1),
        "Total A puerta": round((df_local_5["a_puerta_favor"].mean() + df_visitante_5["a_puerta_favor"].mean()), 1),

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

    def colorear_resultado(val):
        color = ''
        if val == 'W':
            color = 'background-color: #c8e6c9'  # verde
        elif val == 'D':
            color = 'background-color: #fff9c4'  # amarillo
        elif val == 'L':
            color = 'background-color: #ffcdd2'  # rojo
        return color

    st.subheader("Últimos 5 partidos local")
    if 'resultado' in df_local.columns:
        st.dataframe(df_local.tail(5).style.map(colorear_resultado, subset=['resultado']))
    else:
        st.table(df_local.tail(5))

    st.subheader("Últimos 5 partidos visitante")
    if 'resultado' in df_visitante.columns:
        st.dataframe(df_visitante.tail(5).style.map(colorear_resultado, subset=['resultado']))
    else:
        st.table(df_visitante.tail(5))

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

# === TABLAS AVANZADAS BASADAS EN NUEVOS LAMBDAS ===
def mostrar_tablas_avanzadas(metricas):
    if metricas is None:
        return

    lambda_L = metricas["lambda_local_new"]
    lambda_V = metricas["lambda_vis_new"]

    col1, col2, col3 = st.columns(3)

    # Tabla 1: Resultado y dobles (umbral 60%)
    with col1:
        st.subheader("Resultado y Dobles")
        res = poisson_prob_1x2_y_dobles(lambda_L, lambda_V, max_goals=8)
        df_res = pd.DataFrame(
            [
                ["Gana Local", res["1"]],
                ["Empate", res["X"]],
                ["Gana Visitante", res["2"]],
                ["Local o Empate (1X)", res["1X"]],
                ["Visitante o Empate (X2)", res["X2"]],
                ["Gana Cualquiera (No empate)", res["12"]],
            ],
            columns=["Métrica", "Probabilidad %"],
        )
        st.table(formatear_y_resaltar(df_res, "Probabilidad %", umbral=60))

    # Tabla 2: Overs/Unders de goles totales
    with col2:
        st.subheader("Goles en el Partido")
        lineas_goles = [0.5, 1.5, 2.5, 3.5]
        rows_totales = []
        for L in lineas_goles:
            u, o = poisson_prob_total_over_under(lambda_L, lambda_V, L, max_k=8)
            rows_totales.append([f"+{L} goles", o, f"-{L} goles", u])
        df_tot = pd.DataFrame(
            rows_totales, columns=["Over", "Prob. Over %", "Under", "Prob. Under %"]
        )
        st.table(formatear_y_resaltar(df_tot, "Prob. Over %", umbral=70, col_extra = "Prob. Under %"))

    # Tabla 3: Goles por equipo y BTTS
    with col3:
        st.subheader("Goles por Equipo y BTTS")
        lineas_equipo = [0.5, 1.5]
        rows_eq = []
        for L in lineas_equipo:
            _, oL = poisson_prob_over_under(lambda_L, L, max_k=8)
            _, oV = poisson_prob_over_under(lambda_V, L, max_k=8)
            rows_eq.append(
                [f"Local marca +{L}", oL, metricas["P_match_local"]]
            )
            rows_eq.append(
                [f"Visitante marca +{L}", oV, metricas["P_match_vis"]]
            )
        btts = prob_btts(lambda_L, lambda_V, max_goals=8)
        rows_eq.append([
            "BTTS",
            btts,
            (metricas["P_match_local"] + metricas["P_match_vis"]) / 2.0
        ])
        df_eq = pd.DataFrame(
            rows_eq, columns=["Métrica", "Probabilidad %", "Precisión"]
        )
        st.table(formatear_y_resaltar(df_eq, "Probabilidad %", umbral=70, col_extra="Precisión"))

    # === Tabla 4 y 5 en la misma fila ===
    col4, col5 = st.columns(2)
    
    with col4:
        st.subheader("Remates Totales en el Partido")
        lambda_shots_total = metricas["Remates_att_local"] + metricas["Remates_att_vis"]
        lineas_shots_total = [18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5, 26.5, 27.5, 28.5, 29.5, 30.5, 31.5]
        rows_shots_tot = []
        for L in lineas_shots_total:
            u, o = poisson_prob_over_under(lambda_shots_total, L, max_k=25)
            rows_shots_tot.append([L, u, o])
        df_shots_tot = pd.DataFrame(
            rows_shots_tot, columns=["Línea", "Under %", "Over %"]
        )
        st.table(formatear_y_resaltar(df_shots_tot, "Over %", umbral=70, col_extra = "Under %"))

    # Tabla 5: Remates por equipo
    with col5:
        st.subheader("Remates por Equipo")
        lineas_shots_eq = [7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 20.5]
        rows_shots_eq = []
        for L in lineas_shots_eq:
            _, oL = poisson_prob_over_under(metricas["Remates_att_local"], L, max_k=25)
            _, oV = poisson_prob_over_under(metricas["Remates_att_vis"], L, max_k=25)
            rows_shots_eq.append([f"+{L} Remates", oL, oV])

        df_shots_eq = pd.DataFrame(
            rows_shots_eq,
            columns=["Remates", "Local %", "Visitante %"]
        )
        st.table(formatear_y_resaltar(df_shots_eq, "Local %", umbral=70, col_extra= "Visitante %"))

    # === Tabla 6 y 7 en la misma fila ===
    col6, col7 = st.columns(2)
    
    # Tabla 6: Tiros a puerta totales
    with col6:
        st.subheader("Tiros a Puerta Totales")
        lambda_sot_total = metricas["SoT_local"] + metricas["SoT_vis"]
        lineas_sot_total = [5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]
        rows_sot_tot = []
        for L in lineas_sot_total:
            u, o = poisson_prob_over_under(lambda_sot_total, L, max_k=10)
            rows_sot_tot.append([L, u, o])
        df_sot_tot = pd.DataFrame(
            rows_sot_tot, columns=["Línea", "Under %", "Over %"]
        )
        st.table(formatear_y_resaltar(df_sot_tot, "Over %", umbral=70, col_extra="Under %"))

    # === Tabla 7: Tiros a puerta por equipo (1 por fila o en dos columnas) ===
    with col7:
        st.subheader("Tiros a Puerta por Equipo")
        lineas_sot_eq = [2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
        rows_sot_eq = []
        for L in lineas_sot_eq:
            _, oL = poisson_prob_over_under(metricas["SoT_local"], L, max_k=10)
            _, oV = poisson_prob_over_under(metricas["SoT_vis"], L, max_k=10)
            rows_sot_eq.append([f"+{L} Tiros a puerta", oL, oV])

        df_sot_eq = pd.DataFrame(
            rows_sot_eq,
            columns=["Tiros a puerta", "Local %", "Visitante %"]
        )
        st.table(formatear_y_resaltar(df_sot_eq, "Local %", umbral=70, col_extra= "Visitante %"))

    
def formatear_y_resaltar(df, col_prob, umbral, col_extra=None):
    df_fmt = df.reset_index(drop=True).copy()

    # Redondear columnas de línea (goles / remates / tiros) a 1 decimal si son numéricas
    if "Línea" in df_fmt.columns and pd.api.types.is_numeric_dtype(df_fmt["Línea"]):
        df_fmt["Línea"] = df_fmt["Línea"].astype(float).round(1)

    # Redondear columnas de probabilidad (ya están en %)
    if col_prob in df_fmt.columns:
        df_fmt[col_prob] = df_fmt[col_prob].astype(float).round(1)
    if col_extra and col_extra in df_fmt.columns:
        df_fmt[col_extra] = df_fmt[col_extra].astype(float).round(1)

    def _color_col(col):
        styles = []
        for val in col:
            try:
                v = float(val)
            except Exception:
                v = 0.0
            styles.append("background-color: #bbdefb" if v >= umbral else "")
        return styles

    fmt_dict = {}

    # Formato para Línea (1 decimal, sin %)
    if "Línea" in df_fmt.columns:
        fmt_dict["Línea"] = "{:.1f}"

    # Formato para columnas de probabilidad (1 decimal con %)
    if col_prob in df_fmt.columns:
        fmt_dict[col_prob] = "{:.1f}%"
    if col_extra and col_extra in df_fmt.columns:
        fmt_dict[col_extra] = "{:.1f}%"

    styler = df_fmt.style.hide(axis="index")
    if col_prob in df_fmt.columns:
        styler = styler.apply(_color_col, subset=[col_prob], axis=0)
    if col_extra and col_extra in df_fmt.columns:
        styler = styler.apply(_color_col, subset=[col_extra], axis=0)
    if fmt_dict:
        styler = styler.format(fmt_dict)

    return styler

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
            x=x_data, y=df["xg_favor"], name='xG',
            mode='lines+markers+text',
            line=dict(color='green', width=3),
            text=df["xg_favor"].round(2),
            textposition="top center"
        ),
        secondary_y=True,
    )
    
    # Línea 2: Tiros a Puerta (A Favor)
    fig_ataque.add_trace(
        go.Scatter(
            x=x_data, y=df["a_puerta_favor"], name='Tiros a Puerta',
            mode='lines+markers+text',
            line=dict(color='orange', width=3),
            text=df["a_puerta_favor"].round(1),
            textposition="bottom center"
        ),
        secondary_y=True,
    )
    
    fig_ataque.add_hline(
        y=df[goles_favor_col].median(),
        line_dash="dot", line_color="blue",
        annotation_text=f"Mediana GF: {df[goles_favor_col].median():.2f}",
        annotation_position="top left"
    )

    fig_ataque.add_hline(
        y=df["xg_favor"].median(),
        line_dash="dot", line_color="green",
        annotation_text=f"Mediana xG: {df['xg_favor'].median():.2f}",
        annotation_position="top right"
    )

    fig_ataque.add_hline(
        y=df["a_puerta_favor"].median(),
        line_dash="dot", line_color="orange",
        annotation_text=f"Mediana ShotsOT: {df['a_puerta_favor'].median():.2f}",
        annotation_position="bottom left"
    )
    
    fig_ataque.update_layout(font=dict(color="black"))


    # Configuración del Eje y Título
    fig_ataque.update_layout(
        title_text=f"**{equipo_nombre}** - Tendencia de ATAQUE (vs Rivales)",
        xaxis_title="Rivales Enfrentados (Partidos Recientes)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100),
        plot_bgcolor = "#e6e6e6",
        paper_bgcolor = "#e6e6e6"
    )
    fig_ataque.update_yaxes(title_text="Goles Anotados", secondary_y=False, showgrid=False)
    fig_ataque.update_yaxes(title_text="xG / Tiros a Puerta", secondary_y=True, showgrid=True)
    fig_ataque.update_traces(textfont=dict(color="white", size=12, family="Arial", weight="bold"))
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
            x=x_data, y=df["xg_contra"], name='xG en Contra',
            mode='lines+markers+text',
            line=dict(color='purple', width=3),
            text=df["xg_contra"].round(2),
            textposition="top center"
        ),
        secondary_y=True,
    )
    
    # Línea 2: Tiros a Puerta *EN CONTRA* (Usando Shots Favor como PROXY/Control)
    fig_defensa.add_trace(
        go.Scatter(
            x=x_data, y=df["a_puerta_contra"], name='Tiros a puerta en contra',
            mode='lines+markers+text',
            line=dict(color='teal', width=3),
            text=df["a_puerta_contra"].round(1),
            textposition="bottom center"
        ),
        secondary_y=True,
    )
    
    fig_defensa.add_hline(
        y=df[goles_contra_col].median(),
        line_dash="dot", line_color="red",
        annotation_text=f"Mediana GC: {df[goles_contra_col].median():.2f}",
        annotation_position="top left"
    )

    fig_defensa.add_hline(
        y=df["xg_contra"].median(),
        line_dash="dot", line_color="purple",
        annotation_text=f"Mediana xG Contra: {df['xg_contra'].median():.2f}",
        annotation_position="top right"
    )

    fig_defensa.add_hline(
        y=df["a_puerta_contra"].median(),
        line_dash="dot", line_color="teal",
        annotation_text=f"Mediana ShotsOT C: {df['a_puerta_contra'].median():.2f}",
        annotation_position="bottom left"
    )
    
    fig_defensa.update_layout(font=dict(color="black"))

    # Configuración del Eje y Título
    fig_defensa.update_layout(
        title_text=f"**{equipo_nombre}** - Tendencia de DEFENSA (vs Rivales)",
        xaxis_title="Rivales Enfrentados (Partidos Recientes)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100),
        plot_bgcolor = "#e6e6e6",
        paper_bgcolor = "#e6e6e6"
    )
    fig_defensa.update_yaxes(title_text="Goles Recibidos", secondary_y=False, showgrid=False)
    fig_defensa.update_yaxes(title_text="xG en Contra / Tiros a puerta en contra", secondary_y=True, showgrid=True)
    fig_defensa.update_traces(textfont=dict(color="white", size=12, family="Arial", weight="bold"))
    st.plotly_chart(fig_defensa, use_container_width=True, config={"staticPlot": True})
    
        # === GRÁFICO DE GOLES POR MITAD (A FAVOR) ===
    x_data = [f"{rival.upper()}" for rival in df[rival_col]]

    fig_goles_mitad_favor = go.Figure()

    fig_goles_mitad_favor.add_trace(go.Bar(
        x=x_data,
        y=df["1t_goles_favor"],
        name="1T Goles a Favor",
        text=df["1t_goles_favor"].round(1),
        textposition="auto",
        marker_color="royalblue",
        offsetgroup=0
    ))

    fig_goles_mitad_favor.add_trace(go.Bar(
        x=x_data,
        y=df["2t_goles_favor"],
        name="2T Goles a Favor",
        text=df["2t_goles_favor"].round(1),
        textposition="auto",
        marker_color="orange",
        offsetgroup=1
    ))

    # Líneas de mediana (una para cada mitad)
    fig_goles_mitad_favor.add_hline(
        y=df["1t_goles_favor"].median(),
        line_dash="dot",
        line_color="royalblue",
        annotation_text=f"Mediana 1T: {df['1t_goles_favor'].median():.1f}",
        annotation_position="top left"
    )
    fig_goles_mitad_favor.add_hline(
        y=df["2t_goles_favor"].median(),
        line_dash="dot",
        line_color="orange",
        annotation_text=f"Mediana 2T: {df['2t_goles_favor'].median():.1f}",
        annotation_position="bottom left"
    )

    fig_goles_mitad_favor.update_layout(
        title_text=f"{equipo_nombre} - Goles a Favor por Partido (1T y 2T)",
        xaxis_title="Rivales Enfrentados",
        yaxis_title="Goles a Favor",
        barmode="group",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100),
        plot_bgcolor = "#e6e6e6",
        paper_bgcolor = "#e6e6e6"
    )
    
    st.plotly_chart(fig_goles_mitad_favor, use_container_width=True, config={"staticPlot": True})


    # === GRÁFICO DE GOLES POR MITAD (EN CONTRA) ===
    fig_goles_mitad_contra = go.Figure()

    fig_goles_mitad_contra.add_trace(go.Bar(
        x=x_data,
        y=df["1t_goles_contra"],
        name="1T Goles Recibidos",
        text=df["1t_goles_contra"].round(1),
        textposition="auto",
        marker_color="crimson",
        offsetgroup=0
    ))

    fig_goles_mitad_contra.add_trace(go.Bar(
        x=x_data,
        y=df["2t_goles_contra"],
        name="2T Goles Recibidos",
        text=df["2t_goles_contra"].round(1),
        textposition="auto",
        marker_color="goldenrod",
        offsetgroup=1
    ))

    # Líneas de mediana (una para cada mitad)
    fig_goles_mitad_contra.add_hline(
        y=df["1t_goles_contra"].median(),
        line_dash="dot",
        line_color="crimson",
        annotation_text=f"Mediana 1T: {df['1t_goles_contra'].median():.1f}",
        annotation_position="top left"
    )
    fig_goles_mitad_contra.add_hline(
        y=df["2t_goles_contra"].median(),
        line_dash="dot",
        line_color="goldenrod",
        annotation_text=f"Mediana 2T: {df['2t_goles_contra'].median():.1f}",
        annotation_position="bottom left"
    )

    fig_goles_mitad_contra.update_layout(
        title_text=f"{equipo_nombre} - Goles Recibidos por Partido (1T y 2T)",
        xaxis_title="Rivales Enfrentados",
        yaxis_title="Goles Recibidos",
        barmode="group",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=100),
        plot_bgcolor = "#e6e6e6",
        paper_bgcolor = "#e6e6e6"
    )
    st.plotly_chart(fig_goles_mitad_contra, use_container_width=True, config={"staticPlot": True})


# === CÁLCULO DE ESTADÍSTICAS Y RACHAS ===
def calcular_estadisticas_y_rachas(df, equipo_nombre, tipo_partido):
    if df.empty:
        return None
    
    df10 = df.tail(10)
    df5 = df.tail(5)
    df3 = df.tail(3)

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
    remates_contra_col = "shots_contra"
    a_puerta_favor_col = "a_puerta_favor"
    a_puerta_contra_col = "a_puerta_contra"

    # Goles y remates
    media_gol = round(df_calculo[goles_a_favor_col].mean(), 2)
    media_gol_recibido = round(df_calculo[goles_en_contra_col].mean(), 2)
    media_gol_1t = round(df_calculo[goles_ht_favor_col].mean(), 2)
    media_gol_1t_recibido = round(df_calculo[goles_ht_contra_col].mean(), 2)
    media_gol_2t = round(df_calculo[goles_st_favor_col].mean(), 2)
    media_gol_2t_recibido = round(df_calculo[goles_st_contra_col].mean(), 2)
    promedio_remates = round(df_calculo[remates_favor_col].mean(), 1)
    promedio_remates_contra = round(df_calculo[remates_contra_col].mean(), 1)
    promedio_tiros_puerta = round(df_calculo[a_puerta_favor_col].mean(), 1)
    promedio_tiros_puerta_contra = round(df_calculo[a_puerta_contra_col].mean(), 1)
    media_xg_favor = round(df_calculo[xg_favor_col].mean(), 2)
    media_xg_contra = round(df_calculo[xg_contra_col].mean(), 2)    

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
    racha_prom_remates_contra = calcular_racha(df_calculo, remates_contra_col, promedio_remates_contra)
    racha_prom_tiros_puerta = calcular_racha(df_calculo, a_puerta_favor_col, promedio_tiros_puerta)
    racha_prom_tiros_puerta_contra = calcular_racha(df_calculo, a_puerta_contra_col, promedio_tiros_puerta_contra)

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
            "BTTS",
            "Gol HT",
            "Over 1.5 HT",
            "Over 1.5 Goles",
            "Over 2.5 Goles",
            "Promedio Remates",
            "Promedio Remates Contra",
            "Promedio Tiros a Puerta",
            "Promedio Tiros a Puerta Contra"
        ],

        # ======= ÚLTIMOS 10 PARTIDOS (YA EXISTENTE) =======
        f"{equipo_nombre} (10)": [
            media_gol,
            media_gol_recibido,
            media_gol_1t,
            media_gol_1t_recibido,
            media_gol_2t,
            media_gol_2t_recibido,
            media_xg_favor,
            media_xg_contra,
            f"{btts:.1f}%",
            f"{gol_ht:.1f}%",
            f"{over_1_5_ht:.1f}%",
            f"{over_1_5_total:.1f}%",
            f"{over_2_5_goles:.1f}%",
            promedio_remates,
            promedio_remates_contra,
            promedio_tiros_puerta,
            promedio_tiros_puerta_contra
        ],

        "R10": [
            racha_media_gol,
            racha_media_gol_recibido,
            racha_media_gol_1t,
            racha_media_gol_1t_recibido,
            racha_media_gol_2t,
            racha_media_gol_2t_recibido,
            racha_media_xg_favor,
            racha_media_xg_contra,            
            racha_btts,
            racha_gol_ht,
            racha_over_1_5_ht,
            racha_over_1_5_total,
            racha_over_2_5,
            racha_prom_remates,
            racha_prom_remates_contra,
            racha_prom_tiros_puerta,
            racha_prom_tiros_puerta_contra
        ],

        # ======= ÚLTIMOS 5 PARTIDOS =======
        f"{equipo_nombre} (5)": [
            round(df5[goles_a_favor_col].mean(), 2),
            round(df5[goles_en_contra_col].mean(), 2),
            round(df5[goles_ht_favor_col].mean(), 2),
            round(df5[goles_ht_contra_col].mean(), 2),
            round(df5[goles_st_favor_col].mean(), 2),
            round(df5[goles_st_contra_col].mean(), 2),
            round(df5[xg_favor_col].mean(), 2),
            round(df5[xg_contra_col].mean(), 2),
            f"{( ((df5[goles_a_favor_col]>0)&(df5[goles_en_contra_col]>0)).mean()*100 ):.1f}%",
            f"{((df5[goles_ht_favor_col]+df5[goles_ht_contra_col])>0).mean()*100:.1f}%",
            f"{((df5[goles_ht_favor_col]+df5[goles_ht_contra_col])>1.5).mean()*100:.1f}%",
            f"{((df5[goles_a_favor_col]+df5[goles_en_contra_col])>1.5).mean()*100:.1f}%",
            f"{((df5[goles_a_favor_col]+df5[goles_en_contra_col])>2.5).mean()*100:.1f}%",
            round(df5[remates_favor_col].mean(),1),
            round(df5[remates_contra_col].mean(),1),
            round(df5[a_puerta_favor_col].mean(),1),
            round(df5[a_puerta_contra_col].mean(),1)
        ],

        "R5": [
            calcular_racha(df5, goles_a_favor_col, df5[goles_a_favor_col].mean()),
            calcular_racha(df5, goles_en_contra_col, df5[goles_en_contra_col].mean()),
            calcular_racha(df5, goles_ht_favor_col, df5[goles_ht_favor_col].mean()),
            calcular_racha(df5, goles_ht_contra_col, df5[goles_ht_contra_col].mean()),
            calcular_racha(df5, goles_st_favor_col, df5[goles_st_favor_col].mean()),
            calcular_racha(df5, goles_st_contra_col, df5[goles_st_contra_col].mean()),
            calcular_racha(df5, xg_favor_col, df5[xg_favor_col].mean()),
            calcular_racha(df5, xg_contra_col, df5[xg_contra_col].mean()),
            calcular_racha_booleana(df5, (df5[goles_a_favor_col]>0)&(df5[goles_en_contra_col]>0)),
            calcular_racha_booleana(df5, (df5[goles_ht_favor_col]+df5[goles_ht_contra_col])>0),
            calcular_racha_booleana(df5, (df5[goles_ht_favor_col]+df5[goles_ht_contra_col])>1.5),
            calcular_racha_booleana(df5, (df5[goles_a_favor_col]+df5[goles_en_contra_col])>1.5),
            calcular_racha_booleana(df5, (df5[goles_a_favor_col]+df5[goles_en_contra_col])>2.5),
            calcular_racha(df5, remates_favor_col, df5[remates_favor_col].mean()),
            calcular_racha(df5, remates_contra_col, df5[remates_contra_col].mean()),
            calcular_racha(df5, a_puerta_favor_col, df5[a_puerta_favor_col].mean()),
            calcular_racha(df5, a_puerta_contra_col, df5[a_puerta_contra_col].mean())
        ],

        # ======= ÚLTIMOS 3 PARTIDOS =======
        f"{equipo_nombre} (3)": [
            round(df3[goles_a_favor_col].mean(), 2),
            round(df3[goles_en_contra_col].mean(), 2),
            round(df3[goles_ht_favor_col].mean(), 2),
            round(df3[goles_ht_contra_col].mean(), 2),
            round(df3[goles_st_favor_col].mean(), 2),
            round(df3[goles_st_contra_col].mean(), 2),
            round(df3[xg_favor_col].mean(), 2),
            round(df3[xg_contra_col].mean(), 2),
            f"{(((df3[goles_a_favor_col]>0)&(df3[goles_en_contra_col]>0)).mean()*100):.1f}%",
            f"{((df3[goles_ht_favor_col]+df3[goles_ht_contra_col])>0).mean()*100:.1f}%",
            f"{((df3[goles_ht_favor_col]+df3[goles_ht_contra_col])>1.5).mean()*100:.1f}%",
            f"{((df3[goles_a_favor_col]+df3[goles_en_contra_col])>1.5).mean()*100:.1f}%",
            f"{((df3[goles_a_favor_col]+df3[goles_en_contra_col])>2.5).mean()*100:.1f}%",
            round(df3[remates_favor_col].mean(),1),
            round(df3[remates_contra_col].mean(),1),
            round(df3[a_puerta_favor_col].mean(),1),
            round(df3[a_puerta_contra_col].mean(),1)
        ],

        "R3": [
            calcular_racha(df3, goles_a_favor_col, df3[goles_a_favor_col].mean()),
            calcular_racha(df3, goles_en_contra_col, df3[goles_en_contra_col].mean()),
            calcular_racha(df3, goles_ht_favor_col, df3[goles_ht_favor_col].mean()),
            calcular_racha(df3, goles_ht_contra_col, df3[goles_ht_contra_col].mean()),
            calcular_racha(df3, goles_st_favor_col, df3[goles_st_favor_col].mean()),
            calcular_racha(df3, goles_st_contra_col, df3[goles_st_contra_col].mean()),
            calcular_racha(df3, xg_favor_col, df3[xg_favor_col].mean()),
            calcular_racha(df3, xg_contra_col, df3[xg_contra_col].mean()),
            calcular_racha_booleana(df3, (df3[goles_a_favor_col]>0)&(df3[goles_en_contra_col]>0)),
            calcular_racha_booleana(df3, (df3[goles_ht_favor_col]+df3[goles_ht_contra_col])>0),
            calcular_racha_booleana(df3, (df3[goles_ht_favor_col]+df3[goles_ht_contra_col])>1.5),
            calcular_racha_booleana(df3, (df3[goles_a_favor_col]+df3[goles_en_contra_col])>1.5),
            calcular_racha_booleana(df3, (df3[goles_a_favor_col]+df3[goles_en_contra_col])>2.5),
            calcular_racha(df3, remates_favor_col, df3[remates_favor_col].mean()),
            calcular_racha(df3, remates_contra_col, df3[remates_contra_col].mean()),
            calcular_racha(df3, a_puerta_favor_col, df3[a_puerta_favor_col].mean()),
            calcular_racha(df3, a_puerta_contra_col, df3[a_puerta_contra_col].mean())
        ]
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
    # --- 1. CONFIGURACIÓN DEL ESTADO DE SESIÓN ---
    if 'partidos_rango' not in st.session_state:
        st.session_state.partidos_rango = 10 # Valor inicial

    # --- 2. CARGA DE DATOS ---
    # Cargamos siempre los 10 para que los dataframes df_local_all y df_visitante_all
    # tengan suficientes datos para todos los cálculos.
    df_local_all = cargar_datos(equipo_local_nombre, "local", 10)
    df_visitante_all = cargar_datos(equipo_visitante_nombre, "visitante", 10)

    # Lógica para la tabla de la imagen
    stats_local = calcular_estadisticas_y_rachas(df_local_all, equipo_local_nombre, "local")
    stats_visitante = calcular_estadisticas_y_rachas(df_visitante_all, equipo_visitante_nombre, "visitante")

    df_stats_local = pd.DataFrame(stats_local) if stats_local else pd.DataFrame()
    df_stats_visitante = pd.DataFrame(stats_visitante) if stats_visitante else pd.DataFrame()

    st.markdown("## 📊 Estadísticas Detalladas de Partidos Recientes")
    
    # --- 3. CREACIÓN DE BOTONES Y MANEJO DEL ESTADO ---
    def set_rango(rango):
        st.session_state.partidos_rango = rango
        
    col_btn_10, col_btn_5, col_btn_3, _ = st.columns([1, 1, 1, 9])
    
    with col_btn_10:
        st.button("10 Partidos", on_click=set_rango, args=[10], 
                  type="primary" if st.session_state.partidos_rango == 10 else "secondary")
    with col_btn_5:
        st.button("5 Partidos", on_click=set_rango, args=[5], 
                  type="primary" if st.session_state.partidos_rango == 5 else "secondary")
    with col_btn_3:
        st.button("3 Partidos", on_click=set_rango, args=[3], 
                  type="primary" if st.session_state.partidos_rango == 3 else "secondary")
        
    rango_actual = st.session_state.partidos_rango
    
    # Definición de las columnas a mostrar basado en el rango seleccionado
    cols_to_show = ["Estadística", f"{equipo_local_nombre} ({rango_actual})", f"R{rango_actual}"]
    
    # --- 4. VISUALIZACIÓN DE LA TABLA DINÁMICA ---
    col_local_stats, col_visitante_stats = st.columns(2)

    with col_local_stats:
        st.subheader(f"🔵 Equipo Local (Últimos {rango_actual})")
        if not df_stats_local.empty:
            # Seleccionar solo las columnas correspondientes al rango actual para mostrar
            df_local_filtered = df_stats_local[["Estadística", f"{equipo_local_nombre} ({rango_actual})", f"R{rango_actual}"]].copy()
            df_local_filtered.columns = ["Estadística", "Valor", "Racha"] # Renombrar para 'resaltar_estadistica'
            st.table(resaltar_estadistica(df_local_filtered))

    with col_visitante_stats:
        st.subheader(f"🔴 Equipo Visitante (Últimos {rango_actual})")
        if not df_stats_visitante.empty:
            # Seleccionar solo las columnas correspondientes al rango actual para mostrar
            df_visitante_filtered = df_stats_visitante[["Estadística", f"{equipo_visitante_nombre} ({rango_actual})", f"R{rango_actual}"]].copy()
            df_visitante_filtered.columns = ["Estadística", "Valor", "Racha"] # Renombrar para 'resaltar_estadistica'
            st.table(resaltar_estadistica(df_visitante_filtered))
            
    metricas_avanzadas = calcular_metricas_avanzadas(df_local_all, df_visitante_all)
    mostrar_tablas_avanzadas(metricas_avanzadas)
    
    st.markdown("---")
    st.markdown("## 📈 Tendencia de Juego (Ataque y Defensa)")

    col_local_chart, col_visitante_chart = st.columns(2)

    with col_local_chart:
        st.subheader(f"🔵 {equipo_local_nombre} (Local) - Gráficos")
        # Mostrar solo los últimos partidos relevantes para los gráficos de tendencia
        df_local_trend = df_local_all.tail(rango_actual)
        generar_grafico_tendencia(df_local_trend, equipo_local_nombre, "local")

    with col_visitante_chart:
        st.subheader(f"🔴 {equipo_visitante_nombre} (Visitante) - Gráficos")
        # Mostrar solo los últimos partidos relevantes para los gráficos de tendencia
        df_visitante_trend = df_visitante_all.tail(rango_actual)
        generar_grafico_tendencia(df_visitante_trend, equipo_visitante_nombre, "visitante")

    st.markdown("---")
    st.markdown("## 🔮 Predicción del Partido")

    # Lógica de predicción y sugerencias (Usa df_local_all y df_visitante_all para el cálculo)
    resultados = calcular_probabilidades_equipo(df_local_all, df_visitante_all)
    mostrar_resultados(resultados, df_local_all, df_visitante_all)

else:
    st.warning("Selecciona un partido para ver el análisis.")