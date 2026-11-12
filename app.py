from typing import List, Union
import numpy as np
import streamlit as st
import pandas as pd
import os
from collections import Counter
from scipy.stats import poisson
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import BytesIO
from datetime import datetime
from partidos_manager import (
    inicializar_lista_partidos,
    mostrar_boton_agregar_partido,
)
from contexto_liga import (aplicar_contexto_goles, 
                           preparar_contexto_remates_sot, 
                           generar_analisis_cuartos,
                           predecir_goles_desde_entradas)

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Predicción de Partido", layout="wide")
from partidos_manager import inicializar_lista_partidos
inicializar_lista_partidos()
st.title("⚽ Predicción Condicional - Apuestas Inteligentes")

# === NORMALIZACIÓN DE COLUMNAS ===
def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

# === MAPA DE EQUIPOS ===
mapa_equipos = {
"aalesunds-fk_norway": "aalesund",
"aarhus_denmark": "aarhus",
"aberdeen-fc_scotland": "aberdeen",
"abha-club_saudi-arabia": "abha",
"abou-qir-fertilizers-sc_egypt": "abu qir semad",
"ac-horsens_denmark": "horsens",
"ac-milan_italy": "ac milan",
"ac-monza_italy": "monza",
"ac-omonia_cyprus": "omonia",
"ac-oulu_finland": "oulu",
"academico-de-viseu-fc_portugal": "academico viseu",
"acf-fiorentina_italy": "fiorentina",
"ad-ceuta-fc_spain_b": "ceuta",
"adc-juan-pablo-ii-college_peru": "juan pablo ii",
"adelaide-united-fc_australia": "adelaide united",
"ado-den-haag_netherlands": "den haag",
"ae-kifisia-fc_greece": "kifisia",
"aek-athens-fc_greece": "aek",
"aek-larnaca-fc_cyprus": "aek larnaca",
"ael-limassol_cyprus": "ael limassol",
"afc-ajax_netherlands": "ajax",
"afc-bournemouth_england": "bournemouth",
"aik_sweden": "aik stockholm",
"aj-auxerre_france": "auxerre",
"al-ahli-saudi-fc_saudi-arabia": "al ahli",
"al-ahly-sc_egypt": "al ahly",
"al-ettifaq-fc_saudi-arabia": "al ettifaq",
"al-faisaly-fc_saudi-arabia": "al faysaly",
"al-fateh-sc_saudi-arabia": "al fateh",
"al-fayha-fc_saudi-arabia": "al fayha",
"al-hazem-fc_saudi-arabia": "al hazem",
"al-hilal-fc_saudi-arabia": "al hilal",
"al-ittihad-ac_egypt": "al ittihad",
"al-ittihad-fc_saudi-arabia": "al-ittihad",
"al-kholood-club_saudi-arabia": "al kholood",
"al-masry-sc_egypt": "al masry",
"al-nassr-fc_saudi-arabia": "al nassr",
"al-qadsiah-fc_saudi-arabia": "al qadsiah",
"al-riyadh-sc_saudi-arabia": "al riyadh",
"al-shabab-fc_saudi-arabia": "al shabab",
"al-taawoun-fc_saudi-arabia": "al-taawon",
"albacete-balompie_spain_b": "albacete",
"albion-fc_uruguay": "albion",
"alianza-atletico_peru": "alianza atl.",
"alianza-fc_colombia": "alianza",
"alianza-lima_peru": "a. lima",
"america-de-cali_colombia": "america de cali",
"angers-sco_france": "angers",
"anorthosis-famagusta-fc_cyprus": "anorthosis",
"apoel-fc_cyprus": "apoel",
"apollon-limassol_cyprus": "apollon",
"arab-contractors-sc_egypt": "arab contractors",
"arda-kardzhali_bulgaria": "arda",
"argentinos-juniors_argentina": "argentinos jrs",
"aris-limassol-fc_cyprus": "aris limassol",
"aris-thessaloniki-fc_greece": "aris",
"arminia-bielefeld_germany_b": "bielefeld",
"arsenal-fc_england": "arsenal",
"as-monaco-fc_france": "monaco",
"as-roma_italy": "as roma",
"asc-otelul-galati_romania": "otelul",
"asociacion-deportiva-tarma_peru": "ad tarma",
"associacao-chapecoense-de-futebol_brazil": "chapecoense-sc",
"asteras-tripolis-fc_greece": "asteras t.",
"aston-villa-fc_england": "aston villa",
"asyut-petroleum-sc_egypt": "asyut petroleum",
"atalanta-bc_italy": "atalanta",
"athletic-bilbao_spain": "ath. bilbao",
"atlanta-united-fc_usa": "atlanta utd",
"atlante-fc_mexico": "atlante",
"atlas-fc_mexico": "atlas",
"atletico-bucaramanga_colombia": "bucaramanga",
"atletico-grau_peru": "grau",
"atletico-junior_colombia": "junior",
"atletico-madrid_spain": "atl. madrid",
"atletico-nacional_colombia": "atl. nacional",
"atletico-san-luis_mexico": "atl. san luis",
"atromitos-fc_greece": "atromitos",
"auckland-fc_australia": "auckland fc",
"audax-italiano_chile": "a. italiano",
"austin-fc_usa": "austin fc",
"austria-vienna_austria": "austria vienna",
"avispa-fukuoka_japan": "avispa fukuoka",
"az-alkmaar_netherlands": "alkmaar",
"barcelona-sc_ecuador": "barcelona sc",
"bayer-leverkusen_germany": "leverkusen",
"bayern-munich_germany": "bayern",
"beijing-guoan-fc_china": "beijing guoan",
"benfica_portugal": "benfica",
"birmingham-city-fc_england_b": "birmingham",
"bk-hacken_sweden": "hacken",
"blackburn-rovers-fc_england_b": "blackburn",
"bohemians-1905_czech-republic": "bohemians",
"bohemians-fc_ireland": "bohemians",
"bologna-fc-1909_italy": "bologna",
"bolton-wanderers-fc_england_b": "bolton",
"borussia-dortmund_germany": "dortmund",
"borussia-monchengladbach_germany": "monchengladbach",
"boston-river_uruguay": "boston river",
"botafogo-de-futebol-e-regatas_brazil": "botafogo rj",
"botev-plovdiv_bulgaria": "botev plovdiv",
"botev-vratsa_bulgaria": "botev vratsa",
"boyaca-chico-fc_colombia": "chico",
"braga_portugal": "braga",
"brentford-fc_england": "brentford",
"brighton-hove-albion-fc_england": "brighton",
"brisbane-roar-fc_australia": "brisbane roar",
"bristol-city-fc_england_b": "bristol city",
"brondby_denmark": "brondby",
"bsc-young-boys_switzerland": "young boys",
"bucheon-fc-1995_south-korea": "bucheon",
"budapest-honved-fc_hungary": "honved",
"burgos-cf_spain_b": "burgos cf",
"burnley-fc_england_b": "burnley",
"ca-osasuna_spain": "osasuna",
"cadiz-cf_spain_b": "cadiz",
"cagliari-calcio_italy": "cagliari",
"cardiff-city-fc_england_b": "cardiff",
"casa-pia-ac_portugal": "casa pia",
"cd-castellon_spain_b": "castellon",
"cd-cobresal_chile": "cobresal",
"cd-cuenca_ecuador": "dep. cuenca",
"cd-eldense_spain_b": "eldense",
"cd-guadalajara_mexico": "guadalajara",
"cd-huachipato_chile": "huachipato",
"cd-leganes_spain_b": "leganes",
"cd-nacional_portugal": "nacional",
"cd-palestino_chile": "palestino",
"cd-tenerife_spain_b": "tenerife",
"cd-universidad-catolica_chile": "u. catolica",
"cd-universidad-catolica_ecuador": "u. catolica",
"cd-universidad-de-concepcion_chile": "u. de concepcion",
"ce-sabadell-fc_spain_b": "sabadell",
"celta-de-vigo-b_spain_b": "celta vigo b",
"celta-vigo_spain": "celta vigo",
"celtic-fc_scotland": "celtic",
"central-coast-mariners-fc_australia": "central coast mariners",
"central-espanol_uruguay": "central esp.",
"ceramica-cleopatra-fc_egypt": "ceramica cleopatra",
"cercle-brugge-ksv_belgium": "cercle brugge",
"cerezo-osaka_japan": "c-osaka",
"cerro-largo-fc_uruguay": "cerro largo",
"cf-estrela-da-amadora_portugal": "estrela",
"cf-monterrey_mexico": "monterrey",
"cf-pachuca_mexico": "pachuca",
"cfr-cluj_romania": "cfr cluj",
"charlotte-fc_usa": "charlotte",
"charlton-athletic-fc_england_b": "charlton",
"chelsea-fc_england": "chelsea",
"chengdu-rongcheng-fc_china": "chengdu rongcheng",
"cherno-more_bulgaria": "cherno more",
"chicago-fire-fc_usa": "chicago fire",
"chongqing-tonglianglong-fc_china": "chongqing tongliang",
"club-america_mexico": "club america",
"club-athletico-paranaense_brazil": "athletico-pr",
"club-atletico-aldosivi_argentina": "aldosivi",
"club-atletico-banfield_argentina": "banfield",
"club-atletico-barracas-central_argentina": "barracas central",
"club-atletico-belgrano_argentina": "belgrano",
"club-atletico-boca-juniors_argentina": "boca juniors",
"club-atletico-central-cordoba_argentina": "central cordoba",
"club-atletico-cerro_uruguay": "cerro ca",
"club-atletico-huracan_argentina": "huracan",
"club-atletico-independiente_argentina": "independiente",
"club-atletico-lanus_argentina": "lanus",
"club-atletico-newells-old-boys_argentina": "newells old boys",
"club-atletico-platense_argentina": "platense",
"club-atletico-progreso_uruguay": "progreso",
"club-atletico-river-plate_argentina": "river plate",
"club-atletico-rosario-central_argentina": "rosario",
"club-atletico-sarmiento-junin_argentina": "sarmiento junin",
"club-atletico-talleres_argentina": "talleres cordoba",
"club-atletico-tigre_argentina": "tigre",
"club-atletico-tucuman_argentina": "atl. tucuman",
"club-atletico-union-de-santa-fe_argentina": "union santa fe",
"club-atletico-velez-sarsfield_argentina": "velez sarsfield",
"club-brugge-kv_belgium": "club brugge",
"club-de-foot-montreal_usa": "cf montreal",
"club-de-gimnasia-la-plata_argentina": "gimnasia l.p.",
"club-deportivo-moquegua_peru": "moquegua",
"club-estudiantes-de-la-plata_argentina": "estudiantes",
"club-gimnasia-de-mendoza_argentina": "gimnasia mendoza",
"club-leon_mexico": "leon",
"club-nacional-de-football_uruguay": "nacional",
"club-necaxa_mexico": "necaxa",
"club-puebla_mexico": "puebla",
"club-sportivo-cienciano_peru": "cienciano",
"club-sportivo-independiente-rivadavia_argentina": "ind. rivadavia",
"club-tijuana_mexico": "tijuana",
"club-universidad-de-chile_chile": "u. de chile",
"club-universitario-de-deportes_peru": "u. de deportes",
"clube-atletico-mineiro_brazil": "atletico-mg",
"clube-de-regatas-do-flamengo_brazil": "flamengo",
"clube-do-remo_brazil": "remo",
"colo-colo_chile": "colo colo",
"colorado-rapids_usa": "colorado rapids",
"columbus-crew-sc_usa": "columbus crew",
"comerciantes-unidos_peru": "comerciantes unidos",
"como-1907_italy": "como",
"coquimbo-unido_chile": "coquimbo",
"cordoba-cf_spain_b": "cordoba",
"coritiba-football-club_brazil": "coritiba",
"corvinul-hunedoara_romania": "corvinul",
"coventry-city-fc_england": "coventry",
"cr-vasco-da-gama_brazil": "vasco",
"cracovia_poland": "cracovia",
"cruz-azul_mexico": "cruz azul",
"cruzeiro-esporte-clube_brazil": "cruzeiro",
"crystal-palace-fc_england": "crystal palace",
"cs-emelec_ecuador": "emelec",
"cs-universitatea-craiova_romania": "univ. craiova",
"csd-independiente-del-valle_ecuador": "ind. del valle",
"csd-macara_ecuador": "macara",
"cska-sofia_bulgaria": "cska sofia",
"cucuta-deportivo-fc_colombia": "cucuta",
"cusco-fc_peru": "cusco",
"daejeon-hana-citizen_south-korea": "daejeon",
"dalian-yingbo-fc_china": "dalian yingbo",
"danubio-fc_uruguay": "danubio",
"darmstadt-98_germany_b": "darmstadt",
"dc-united_usa": "dc united",
"debrecen_hungary": "debrecen",
"defensa-y-justicia_argentina": "defensa y justicia",
"defensor-sporting_uruguay": "defensor sp.",
"degerfors-if_sweden": "degerfors",
"delfin-sc_ecuador": "delfin",
"deportes-concepcion_chile": "dep. concepcion",
"deportes-la-serena_chile": "la serena",
"deportes-limache_chile": "limache",
"deportes-tolima_colombia": "tolima",
"deportivo-alaves_spain": "alaves",
"deportivo-cali_colombia": "dep. cali",
"deportivo-de-a-coruna_spain": "a coruna",
"deportivo-garcilaso_peru": "deportivo garcilaso",
"deportivo-independiente-medellin_colombia": "ind. medellin",
"deportivo-maldonado_uruguay": "maldonado",
"deportivo-nublense_chile": "nublense",
"deportivo-pasto_colombia": "pasto",
"deportivo-pereira_colombia": "pereira",
"deportivo-riestra_argentina": "dep. riestra",
"deportivo-toluca-fc_mexico": "toluca",
"derby-county-fc_england_b": "derby",
"derry-city-fc_ireland": "derry city",
"dinamo-zagreb_croatia": "din. zagreb",
"diriyah-club_saudi-arabia": "al diriyah",
"djurgardens-if_sweden": "djurgarden",
"drogheda-united-fc_ireland": "drogheda",
"dundalk-fc_ireland": "dundalk",
"dundee-fc_scotland": "dundee fc",
"dundee-united-fc_scotland": "dundee utd",
"dynamo-dresden_germany_b": "dresden",
"eintracht-braunschweig_germany_b": "braunschweig",
"eintracht-frankfurt_germany": "frankfurt",
"el-gouna-fc_egypt": "el gounah",
"el-qanah-fc_egypt": "al qanah",
"elche-cf_spain": "elche",
"enppi-sc_egypt": "enppi",
"esporte-clube-bahia_brazil": "bahia",
"esporte-clube-vitoria_brazil": "vitoria",
"estudiantes-de-rio-cuarto_argentina": "estudiantes rio cuarto",
"everton-de-vina-del-mar_chile": "everton",
"everton-fc_england": "everton",
"fagiano-okayama_japan": "fagiano okayama",
"falkirk-fc_scotland": "falkirk",
"famalicao_portugal": "famalicao",
"fbc-melgar_peru": "melgar",
"fc-alverca_portugal": "alverca",
"fc-andorra_spain_b": "andorra",
"fc-anyang_south-korea": "anyang",
"fc-arges-pitesti_romania": "fc arges",
"fc-arouca_portugal": "arouca",
"fc-augsburg_germany": "augsburg",
"fc-banik-ostrava_czech-republic": "ostrava",
"fc-barcelona_spain": "barcelona",
"fc-basel_switzerland": "basel",
"fc-botosani_romania": "botosani",
"fc-cajamarca_peru": "fc cajamarca",
"fc-chornomorets-odessa_ukraine": "ch. odesa",
"fc-cincinnati_usa": "cincinnati",
"fc-copenhagen_denmark": "fc copenhagen",
"fc-cska-1948-sofia_bulgaria": "cska 1948 sofia",
"fc-dallas_usa": "fc dallas",
"fc-dinamo-bucuresti_romania": "dinamo bucuresti",
"fc-dunav-ruse_bulgaria": "dunav ruse",
"fc-dynamo-kyiv_ukraine": "dyn. kyiv",
"fc-energie-cottbus_germany_b": "cottbus",
"fc-epitsentr-kamianets-podilskyi_ukraine": "epitsentr",
"fc-farul-constanta_romania": "farul constanta",
"fc-fastav-zlin_czech-republic": "zlin",
"fc-groningen_netherlands": "groningen",
"fc-heidenheim_germany_b": "heidenheim",
"fc-hradec-kralove_czech-republic": "hradec kralove",
"fc-ilves_finland": "ilves",
"fc-inter-turku_finland": "inter turku",
"fc-juarez_mexico": "juarez",
"fc-kaiserslautern_germany_b": "kaiserslautern",
"fc-karpaty-lviv_ukraine": "karpaty lviv",
"fc-kharkiv_ukraine": "kryvbas",
"fc-koln_germany": "fc koln",
"fc-kolos-kovalivka_ukraine": "kolos kovalivka",
"fc-kryvbas-kryvyi-rih_ukraine": "kryvbas",
"fc-kudrivka_ukraine": "kudrivka",
"fc-lahti_finland": "lahti",
"fc-lausanne-sport_switzerland": "lausanne",
"fc-livyi-bereh-kyiv_ukraine": "livyi bereg",
"fc-lnz-cherkasy_ukraine": "lnz cherkasy",
"fc-lokomotiv-1929-sofia_bulgaria": "lok. sofia",
"fc-lorient_france": "lorient",
"fc-lugano_switzerland": "lugano",
"fc-luzern_switzerland": "luzern",
"fc-machida-zelvia_japan": "machida zelvia",
"fc-magdeburg_germany_b": "magdeburg",
"fc-midtjylland_denmark": "midtjylland",
"fc-nordsjaelland_denmark": "nordsjaelland",
"fc-nurnberg_germany_b": "nurnberg",
"fc-obolon-kyiv_ukraine": "obolon",
"fc-petrolul-ploiesti_romania": "petrolul",
"fc-polissya-zhytomyr_ukraine": "polissya zhytomyr",
"fc-porto_portugal": "fc porto",
"fc-rapid-bucuresti_romania": "fc rapid bucuresti",
"fc-seoul_south-korea": "seoul",
"fc-shakhtar-donetsk_ukraine": "shakhtar",
"fc-sion_switzerland": "sion",
"fc-slovacko_czech-republic": "slovacko",
"fc-slovan-liberec_czech-republic": "liberec",
"fc-spartak-varna_bulgaria": "spartak varna",
"fc-st-gallen_switzerland": "st. gallen",
"fc-st-pauli_germany_b": "st. pauli",
"fc-thun_switzerland": "thun",
"fc-tokyo_japan": "tokyo",
"fc-twente_netherlands": "twente",
"fc-universitatea-cluj_romania": "u. cluj",
"fc-uta-arad_romania": "uta arad",
"fc-utrecht_netherlands": "utrecht",
"fc-vaduz_switzerland": "vaduz",
"fc-viktoria-plzen_czech-republic": "plzen",
"fc-voluntari_romania": "fc voluntari",
"fc-zbrojovka-brno_czech-republic": "brno",
"fc-zorya-luhansk_ukraine": "zorya",
"fc-zurich_switzerland": "zurich",
"fcsb_romania": "fcsb",
"ferencvaros_hungary": "ferencvaros",
"feyenoord-rotterdam_netherlands": "feyenoord",
"ff-jaro_finland": "jaro",
"fk-bodo-glimt_norway": "bodo/glimt",
"fk-jablonec_czech-republic": "jablonec",
"fk-miercurea-ciuc_romania": "csikszereda m. ciuc",
"fk-mlada-boleslav_czech-republic": "mlada boleslav",
"fk-pardubice_czech-republic": "pardubice",
"fk-teplice_czech-republic": "teplice",
"fluminense-fc_brazil": "fluminense",
"fortaleza-ceif_colombia": "fortaleza",
"fortuna-sittard_netherlands": "sittard",
"fredrikstad-fk_norway": "fredrikstad",
"frosinone-calcio_italy": "frosinone",
"fsc-bukovyna-chernivtsi_ukraine": "bukovyna",
"fulham-fc_england": "fulham",
"gais_sweden": "gais",
"galway-united-fc_ireland": "galway",
"gamba-osaka_japan": "g-osaka",
"gangwon-fc_south-korea": "gangwon",
"gd-estoril-praia_portugal": "estoril",
"genoa-cfc_italy": "genoa",
"getafe-cf_spain": "getafe",
"ghazi-el-mahalla-sc_egypt": "ghazi el mahallah",
"gil-vicente_portugal": "gil vicente",
"gimcheon-sangmu-fc_south-korea": "gimcheon sangmu",
"girona-fc_spain_b": "girona",
"gks-katowice_poland": "katowice",
"go-ahead-eagles_netherlands": "g.a. eagles",
"gorica_croatia": "gorica",
"gornik-zabrze_poland": "gornik zabrze",
"granada-cf_spain_b": "granada",
"grasshopper-club-zurich_switzerland": "grasshoppers",
"grazer-ak_austria": "grazer ak",
"gremio-football-porto-alagrense_brazil": "gremio",
"greuther-furth_germany_b": "furth",
"guayaquil-city-fc_ecuador": "guayaquil city",
"gwangju-fc_south-korea": "gwangju",
"gyori-eto-fc_hungary": "gyor",
"hajduk-split_croatia": "hajduk split",
"halmstads-bk_sweden": "halmstad",
"ham-kam_norway": "hamkam",
"hamburger-sv_germany": "hamburger sv",
"hammarby-if_sweden": "hammarby",
"hannover-96_germany_b": "hannover",
"heart-of-midlothian-fc_scotland": "hearts",
"henan-fc_china": "henan fc",
"hertha-berlin_germany_b": "hertha",
"hibernian-fc_scotland": "hibernian",
"hjk-helsinki_finland": "hjk",
"hoffenheim_germany": "hoffenheim",
"holstein-kiel_germany_b": "kiel",
"houston-dynamo_usa": "houston dynamo",
"hull-city-fc_england": "hull",
"if-brommapojkarna_sweden": "brommapojkarna",
"if-elfsborg_sweden": "elfsborg",
"if-gnistan_finland": "gnistan",
"ifk-goteborg_sweden": "goteborg",
"ifk-mariehamn_finland": "mariehamn",
"ik-sirius_sweden": "sirius",
"ik-start_norway": "start",
"incheon-united_south-korea": "incheon",
"independiente-santa-fe_colombia": "santa fe",
"instituto-atletico-central-cordoba_argentina": "instituto",
"inter-miami-cf_usa": "inter miami",
"inter-milan_italy": "inter",
"internacional-de-bogota_colombia": "inter bogota",
"ipswich-town-fc_england": "ipswich",
"iraklis-fc_greece": "iraklis 1908",
"istra-1961_croatia": "istra 1961",
"jagiellona-bialystok_poland": "jagiellonia",
"jaguares-de-cordoba_colombia": "jaguares",
"jef-united-chiba_japan": "jef united chiba",
"jeju-sk-fc_south-korea": "jeju sk",
"jeonbuk-hyundai-motors_south-korea": "jeonbuk",
"juventud-de-las-piedras_uruguay": "juventud",
"juventus-fc_italy": "juventus",
"kaa-gent_belgium": "gent",
"kalamata-fc_greece": "kalamata",
"kalmar-ff_sweden": "kalmar",
"karlsruher-sc_germany_b": "karlsruher",
"karmiotissa-fc_cyprus": "karmiotissa",
"kashima-antlers_japan": "kashima",
"kashiwa-reysol_japan": "kashiwa",
"kawasaki-frontale_japan": "kawasaki",
"kfum-kameratene-oslo_norway": "kfum oslo",
"khaleej-fc_saudi-arabia": "al khaleej",
"kilmarnock-fc_scotland": "kilmarnock",
"kisvarda-fc_hungary": "kisvarda",
"korona-kielce_poland": "korona",
"krasava-eny-ypsonas-fc_cyprus": "krasava",
"krc-genk_belgium": "genk",
"kristiansund-bk_norway": "kristiansund",
"ks-wieczysta-krokow_poland": "wieczysta krakow",
"kuopion-palloseura_finland": "kups",
"kv-kortrijk_belgium": "kortrijk",
"kv-mechelen_belgium": "kv mechelen",
"kvc-westerlo_belgium": "westerlo",
"kyoto-sanga-fc_japan": "kyoto sanga",
"lask_austria": "lask",
"ldu-quito_ecuador": "ldu quito",
"le-havre-ac_france": "le havre",
"le-mans-fc_france": "le mans",
"lech-poznan_poland": "lech",
"leeds-united-fc_england": "leeds",
"legia-warsaw_poland": "legia",
"leones-fc_ecuador": "leones del norte",
"levadiakos-fc_greece": "levadiakos",
"levante-ud_spain": "levante",
"levski-sofia_bulgaria": "levski",
"liaoning-tieren-fc_china": "liaoning tieren",
"libertad-fc_ecuador": "libertad",
"lille-osc_france": "lille",
"lillestrom-sk_norway": "lillestrom",
"lincoln-city-fc_england_b": "lincoln",
"liverpool-fc-montevideo_uruguay": "liverpool m.",
"liverpool-fc_england": "liverpool",
"llaneros-fc_colombia": "llaneros",
"lokomotiv-plovdiv_bulgaria": "lok. plovdiv",
"lokomotiva-zagreb_croatia": "lok. zagreb",
"lommel-sk_belgium": "lommel sk",
"los-angeles-fc_usa": "los angeles fc",
"los-angeles-galaxy_usa": "los angeles galaxy",
"los-chankas-cyc_peru": "los chankas",
"ludogorets_bulgaria": "ludogorets",
"lyngby-bk_denmark": "lyngby",
"macarthur-fc_australia": "macarthur fc",
"mainz-05_germany": "mainz",
"malaga-cf_spain": "malaga",
"malmo-ff_sweden": "malmo ff",
"manchester-city-fc_england": "man city",
"manchester-united-fc_england": "man utd",
"manta-fc_ecuador": "manta",
"maritimo_portugal": "maritimo",
"melbourne-city-fc_australia": "melbourne city",
"melbourne-victory-fc_australia": "melbourne victory",
"middlesbrough-fc_england_b": "middlesbrough",
"millonarios-fc_colombia": "millonarios",
"millwall-fc_england_b": "millwall",
"minnesota-united-fc_usa": "minnesota",
"mirassol-fc_brazil": "mirassol",
"mito-hollyhock_japan": "mito hollyhock",
"mjallby-aif_sweden": "mjallby",
"mks-pogon-szczecin_poland": "pogon szczecin",
"modern-sport-fc_egypt": "modern sport",
"molde-fk_norway": "molde",
"montevideo-city-torque_uruguay": "montevideo city",
"montevideo-wanderers-fc_uruguay": "wanderers",
"moreirense-fc_portugal": "moreirense",
"motherwell-fc_scotland": "motherwell",
"motor-lublin_poland": "motor lublin",
"mtk-budapest-fc_hungary": "mtk budapest",
"mushuc-runa-sc_ecuador": "mushuc runa",
"nagoya-grampus_japan": "nagoya",
"nashville-sc_usa": "nashville sc",
"national-bank-of-egypt-sc_egypt": "national bank egypt",
"nea-salamis-famagusta-fc_cyprus": "nea salamis",
"nec-nijmegen_netherlands": "nijmegen",
"neom-sc_saudi-arabia": "neom fc",
"new-england-revolution_usa": "ne revolution",
"new-york-city-fc_usa": "new york city",
"new-york-red-bulls_usa": "new york red bulls",
"newcastle-jets-fc_australia": "newcastle jets",
"newcastle-united-fc_england": "newcastle",
"nk-rudes_croatia": "rudes",
"nk-veres-rivne_ukraine": "veres-rivne",
"norwich-city-fc_england_b": "norwich",
"nottingham-forest-fc_england": "nottm forest",
"nyiregyhaza-spartacus-fc_hungary": "nyiregyhaza",
"o-higgins-fc_chile": "o'higgins",
"odense-boldklub_denmark": "odense",
"ofi-crete-fc_greece": "ofi crete",
"ogc-nice_france": "nice",
"oh-leuven_belgium": "leuven",
"olympiacos-fc_greece": "olympiacos",
"olympiakos-nicosia_cyprus": "ol. nicosia",
"olympique-de-marseille_france": "marseille",
"olympique-lyonnais_france": "lyon",
"omonia-aradippou_cyprus": "omonia aradippou",
"once-caldas_colombia": "once caldas",
"orense-sc_ecuador": "orense",
"orgryte-is_sweden": "orgryte",
"orlando-city-sc_usa": "orlando city",
"osijek_croatia": "osijek",
"pac-omonia-29m_cyprus": "omonia 29th may",
"pafos-fc_cyprus": "pafos",
"paksi-fc_hungary": "paks",
"panathinaikos-fc_greece": "panathinaikos",
"panetolikos-fc_greece": "panetolikos",
"paok-fc_greece": "paok",
"paris-fc_france": "paris fc",
"paris-saint-germain-fc_france": "psg",
"parma-calcio-1913_italy": "parma",
"pec-zwolle_netherlands": "zwolle",
"penarol_uruguay": "penarol",
"perth-glory-fc_australia": "perth glory",
"petrojet-sc_egypt": "petrojet",
"pfc-septemvri-sofia_bulgaria": "septemvri sofia",
"philadelphia-union_usa": "philadelphia union",
"piast-gliwice_poland": "piast",
"pohang-steelers_south-korea": "pohang",
"portland-timbers_usa": "portland timbers",
"portsmouth-fc_england_b": "portsmouth",
"preston-north-end-fc_england_b": "preston",
"psv-eindhoven_netherlands": "psv",
"puskas-akademia-fc_hungary": "puskas academy",
"pyramids-fc_egypt": "pyramids",
"qingdao-hainiu-fc_china": "qingdao hainiu",
"qingdao-west-coast-fc_china": "qingdao west coast",
"queens-park-rangers-fc_england_b": "qpr",
"queretaro-fc_mexico": "queretaro",
"raal-la-louviere_belgium": "raal la louviere",
"racing-club-de-avellaneda_argentina": "racing club",
"racing-club-de-montevideo_uruguay": "racing montevideo",
"racing-de-santander_spain": "racing santander",
"radomiak-radom_poland": "radomiak radom",
"rakow-czestochowa_poland": "rakow",
"randers-fc_denmark": "randers",
"rangers-fc_scotland": "rangers",
"rapid-vienna_austria": "sk rapid",
"rayo-vallecano_spain": "rayo vallecano",
"rb-leipzig_germany": "rb leipzig",
"rc-lens_france": "lens",
"rc-strasbourg-alsace_france": "strasbourg",
"rcd-espanyol_spain": "espanyol",
"rcd-mallorca_spain_b": "mallorca",
"real-betis-balompie_spain": "betis",
"real-madrid-cf_spain": "real madrid",
"real-oviedo_spain_b": "oviedo",
"real-salt-lake_usa": "real salt lake",
"real-sociedad-b_spain_b": "real sociedad b",
"real-sociedad_spain": "real sociedad",
"real-valladolid_spain_b": "valladolid",
"red-bull-bragantino_brazil": "bragantino",
"red-bull-salzburg_austria": "salzburg",
"rheindorf-altach_austria": "altach",
"rijeka_croatia": "rijeka",
"rio-ave-fc_portugal": "rio ave",
"rionegro-aguilas_colombia": "aguilas",
"rosenborg-bk_norway": "rosenborg",
"royal-antwerp-fc_belgium": "antwerp",
"royal-charleroi-sc_belgium": "charleroi",
"rsc-anderlecht_belgium": "anderlecht",
"rts-widzew-lodz_poland": "widzew lodz",
"ru-saint-gilloise_belgium": "union sg",
"san-diego-fc_usa": "san diego fc",
"san-jose-earthquakes_usa": "san jose earthquakes",
"san-lorenzo-de-almagro_argentina": "san lorenzo",
"sandefjord-fotball_norway": "sandefjord",
"sanfreece-hiroshima_japan": "hiroshima",
"santa-clara_portugal": "santa clara",
"santos-fc_brazil": "santos",
"santos-laguna_mexico": "santos laguna",
"sao-paulo-fc_brazil": "sao paulo",
"sarpsborg-08-ff_norway": "sarpsborg 08",
"sbv-excelsior_netherlands": "excelsior",
"sc-austria-lustenau_austria": "a. lustenau",
"sc-cambuur_netherlands": "cambuur",
"sc-freiburg_germany": "freiburg",
"sc-heerenveen_netherlands": "heerenveen",
"sc-paderborn_germany": "paderborn",
"sc-telstar_netherlands": "telstar",
"schalke-04_germany": "schalke",
"sd-aucas_ecuador": "aucas",
"sd-eibar_spain_b": "eibar",
"seattle-sounders-fc_usa": "seattle sounders",
"sepsi-osk-sftantu-gheorghe_romania": "sepsi sf. gheorghe",
"servette-fc_switzerland": "servette",
"sevilla-fc_spain": "sevilla",
"shamrock-rovers-fc_ireland": "shamrock rovers",
"shandong-taishan-fc_china": "shandong taishan",
"shanghai-port-fc_china": "shanghai port",
"shanghai-shenhua-fc_china": "shanghai shenhua",
"sheffield-united-fc_england_b": "sheff utd",
"shelbourne-fc_ireland": "shelbourne",
"shenzhen-peng-city-fc_china": "shenzhen peng city",
"shimizu-s-pulse_japan": "shimizu",
"silkeborg-if_denmark": "silkeborg",
"sint-truidense-vv_belgium": "st. truiden",
"sjk_finland": "sjk",
"sk-artis-brno_czech-republic": "artis brno",
"sk-beveren_belgium": "beveren",
"sk-brann_norway": "brann",
"sk-sigma-olomouc_czech-republic": "sigma olomouc",
"slask-wroclaw_poland": "slask",
"slaven-belupo_croatia": "slaven belupo",
"slavia-prague_czech-republic": "slavia prague",
"slavia-sofia_bulgaria": "slavia sofia",
"sligo-rovers-fc_ireland": "sligo rovers",
"smouha-sc_egypt": "smouha",
"sociedade-esportiva-palmeiras_brazil": "palmeiras",
"sonderjyske_denmark": "sonderjyske",
"southampton-fc_england_b": "southampton",
"sparta-prague_czech-republic": "sparta prague",
"sparta-rotterdam_netherlands": "sparta rotterdam",
"sport-boys_peru": "sport boys",
"sport-club-corinthians-paulista_brazil": "corinthians",
"sport-club-internacional_brazil": "internacional",
"sport-huancayo_peru": "huancayo",
"sporting-cp_portugal": "sporting",
"sporting-cristal_peru": "sporting cristal",
"sporting-de-gijon_spain_b": "gijon",
"sporting-kansas-city_usa": "sporting kansas city",
"ss-lazio_italy": "lazio",
"ssc-napoli_italy": "napoli",
"st-johnstone-fc_scotland": "st. johnstone",
"st-louis-city-sc_usa": "st. louis city",
"st-mirren-fc_scotland": "st. mirren",
"st-patricks-athletic-fc_ireland": "st. patricks",
"stade-brestois-29_france": "brest",
"stade-rennais-fc_france": "rennes",
"standard-liege_belgium": "st. liege",
"stoke-city-fc_england_b": "stoke",
"sturm-graz_austria": "sturm graz",
"sunderland-afc_england": "sunderland",
"sv-elversberg_germany": "elversberg",
"sv-ried_austria": "ried",
"sv-zulte-waregem_belgium": "waregem",
"swansea-city-afc_england_b": "swansea",
"sydney-fc_australia": "sydney fc",
"talaea-el-gaish-sc_egypt": "el gaish",
"tecnico-universitario_ecuador": "tecnico u.",
"tianjin-jinmen-tiger-fc_china": "tianjin jinmen tiger",
"tigres-uanl_mexico": "tigres",
"tokyo-verdy_japan": "tokyo verdy",
"torino-fc_italy": "torino",
"toronto-fc_usa": "toronto fc",
"tottenham-hotspur-fc_england": "tottenham",
"toulouse-fc_france": "toulouse",
"tps-turku_finland": "tps turku",
"tromso-il_norway": "tromso",
"troyes-ac_france": "troyes",
"tsv-hartberg_austria": "hartberg",
"ud-almeria_spain_b": "almeria",
"ud-las-palmas_spain_b": "las palmas",
"udinese-calcio_italy": "udinese",
"ujpest-fc_hungary": "ujpest",
"ulsan-hd-fc_south-korea": "ulsan hd",
"unam_mexico": "u.n.a.m.",
"union-berlin_germany": "union berlin",
"union-la-calera_chile": "u. calera",
"universidad-tecnica-de-cajamarca_peru": "cajamarca",
"urawa-red-diamonds_japan": "urawa",
"us-lecce_italy": "lecce",
"us-sassuolo-calcio_italy": "sassuolo",
"v-varen-nagasaki_japan": "v-varen nagasaki",
"vaasan-palloseura_finland": "vps",
"valencia-cf_spain": "valencia",
"valerenga-fotball_norway": "valerenga",
"vancouver-whitecaps-fc_usa": "vancouver whitecaps",
"varazdin_croatia": "varazdin",
"vasas-sc_hungary": "vasas",
"vasteras-sk_sweden": "vasteras sk",
"venezia-fc_italy": "venezia",
"vfb-stuttgart_germany": "stuttgart",
"vfl-bochum_germany_b": "bochum",
"vfl-osnabruck_germany_b": "osnabruck",
"vfl-wolfsburg_germany_b": "wolfsburg",
"viborg-ff_denmark": "viborg",
"viking-fk_norway": "viking",
"villarreal-cf_spain": "villarreal",
"vissel-kobe_japan": "kobe",
"vitoria-de-guimaraes_portugal": "guimaraes",
"volos-fc_greece": "volos",
"wadi-degla-sc_egypt": "wadi degla",
"waterford-fc_ireland": "waterford",
"watford-fc_england_b": "watford",
"wellington-phoenix-fc_australia": "wellington phoenix",
"werder-bremen_germany": "bremen",
"west-bromwich-albion-fc_england_b": "west brom",
"west-ham-united-fc_england_b": "west ham",
"western-sydney-wanderers-fc_australia": "ws wanderers",
"willem-ii_netherlands": "willem ii",
"wisla-krakow_poland": "wisla",
"wisla-plock_poland": "wisla plock",
"wolfsberger-ac_austria": "wolfsberger",
"wolverhampton-wanderers-fc_england_b": "wolves",
"wrexham-afc_england_b": "wrexham",
"wsg-swarovski-tirol_austria": "tirol",
"wuhan-three-towns-fc_china": "wuhan three towns",
"yokohama-f-marinos_japan": "yokohama m.",
"yunnan-yukun-fc_china": "yunnan yukun",
"zaglebie-lubin_poland": "zaglebie",
"zalaegerszeg-te_hungary": "zalaegerszeg",
"zamalek-sc_egypt": "zamalek",
"zed-fc_egypt": "zed",
"zhejiang-professional-fc_china": "zhejiang fc",
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
        equipo_base = equipo_archivo.split("_", 1)[0]
        nombre_equipo = mapa_equipos.get(equipo_archivo, mapa_equipos.get(equipo_base, equipo_base.replace("-", " ").lower()))
        if condicion == "local":
            df_filtrado = df[df["equipo_local"].str.lower().str.contains(nombre_equipo, na=False)]
        else:
            df_filtrado = df[df["visitante"].str.lower().str.contains(nombre_equipo, na=False)]

        return df_filtrado.tail(n)

    except Exception as e:
        st.error(f"❌ Error al cargar datos para {equipo_archivo}: {e}")
        return pd.DataFrame()
    
RUTA_STATS = "new-stats"              
RUTA_EQUIPOS_LIGAS = "enlaces_equipos.xlsx"  

@st.cache_data
def media_goles_1t_liga(pais: str, n_partidos_max: int | None = None):    
    try:
        df_equipos = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    except Exception as e:
        st.error(f"No se pudo leer {RUTA_EQUIPOS_LIGAS}: {e}")
        return None

    df_equipos.columns = df_equipos.columns.str.strip().str.lower()
    if not {"equipo", "pais", "division"}.issubset(df_equipos.columns):
        st.error(
            "La tabla equipos_ligas debe tener columnas "
            "'equipo', 'pais' y 'division'."
        )
        return None

    df_pais = df_equipos[df_equipos["pais"].str.lower() == pais.lower()]
    if df_pais.empty:
        st.warning(f"No hay equipos registrados para el país '{pais}'.")
        return None

    goles_1t = 0.0
    partidos = 0

    for _, fila_equipo in df_pais.iterrows():
        equipo_archivo = str(fila_equipo["equipo"]).strip()
        division = str(fila_equipo["division"]).strip()

        nombre_archivo = (
            f"{equipo_archivo}_{division}"
            .replace(" ", "_")
            .lower()
            + ".xlsx"
        )

        ruta = os.path.join(RUTA_STATS, nombre_archivo)

        df = pd.read_excel(ruta)
        df = normalizar_columnas(df)

        for col in ["1t_goles_favor", "1t_goles_contra"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if n_partidos_max is not None:
            df = df.tail(n_partidos_max)

        g1 = df["1t_goles_favor"].fillna(0) + df["1t_goles_contra"].fillna(0)
        goles_1t += g1.sum()
        partidos += len(df)

    if partidos == 0:
        return None

    media_1t = goles_1t / partidos   
    return media_1t

@st.cache_data
def media_remates_liga(pais: str, condicion: str = "local", n_partidos_max: int | None = None):  
    try:
        df_equipos = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    except Exception as e:
        st.error(f"No se pudo leer {RUTA_EQUIPOS_LIGAS}: {e}")
        return 0.0, 0.0

    df_equipos.columns = df_equipos.columns.str.strip().str.lower()
    if not {"equipo", "pais", "division"}.issubset(df_equipos.columns):
        st.error(
            "La tabla equipos_ligas debe tener columnas "
            "'equipo', 'pais' y 'division'."
        )
        return 0.0, 0.0

    df_pais = df_equipos[df_equipos["pais"].str.lower() == pais.lower()]
    if df_pais.empty:
        st.warning(f"No hay equipos registrados para el país '{pais}'.")
        return 0.0, 0.0

    total_shots_favor = 0.0
    total_shots_contra = 0.0
    total_partidos = 0

    for _, fila_equipo in df_pais.iterrows():
        equipo_archivo = str(fila_equipo["equipo"]).strip()
        division = str(fila_equipo["division"]).strip()

        nombre_archivo = (
            f"{equipo_archivo}_{division}"
            .replace(" ", "_")
            .lower()
            + ".xlsx"
        )

        ruta = os.path.join(RUTA_STATS, nombre_archivo)

        df = pd.read_excel(ruta)
        df = normalizar_columnas(df)

        # Convertir columnas numéricas
        for col in ["shots_favor", "shots_contra"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Filtrar por condición (local o visitante)
        if condicion == "local":
            df_filtrado = df[df["equipo_local"].str.lower().str.contains(
                mapa_equipos.get(equipo_archivo, equipo_archivo.replace("-", " ").lower()), na=False)]
        else:  # visitante
            df_filtrado = df[df["visitante"].str.lower().str.contains(
                mapa_equipos.get(equipo_archivo, equipo_archivo.replace("-", " ").lower()), na=False)]

        if n_partidos_max is not None:
            df_filtrado = df_filtrado.tail(n_partidos_max)

        # Sumar remates
        shots_favor = df_filtrado["shots_favor"].fillna(0)
        shots_contra = df_filtrado["shots_contra"].fillna(0)
        
        total_shots_favor += shots_favor.sum()
        total_shots_contra += shots_contra.sum()
        total_partidos += len(df_filtrado)

    if total_partidos == 0:
        return 0.0, 0.0

    prom_favor = total_shots_favor / total_partidos
    prom_contra = total_shots_contra / total_partidos
    
    return round(prom_favor, 1), round(prom_contra, 1)

@st.cache_data
def pais_de_equipo(equipo_archivo: str) -> str | None:
    try:
        df_equipos = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    except Exception:
        return None

    df_equipos.columns = (
        df_equipos.columns.str.strip().str.lower()
    )

    if not {"equipo", "division", "pais"}.issubset(df_equipos.columns):
        return None

    identificadores = (
        df_equipos["equipo"].astype("string").str.strip()
        + "_"
        + df_equipos["division"].astype("string").str.strip()
    ).str.replace(" ", "_", regex=False).str.lower()

    fila = df_equipos[
        identificadores == equipo_archivo.strip().lower()
    ]

    if fila.empty:
        return None

    pais = fila["pais"].iloc[0]

    if pd.isna(pais):
        return None

    return str(pais).strip()

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

def calcular_xg_por_sot(df_segmento):
    if df_segmento is None or df_segmento.empty:
        return 0.0
    total_xg = df_segmento['xg_favor'].sum()
    total_sot = df_segmento['a_puerta_favor'].sum()
    
    if total_sot > 0:
        return round(total_xg / total_sot, 3)
    return 0.0

def calcular_fragilidad_defensiva(df_segmento):
    if df_segmento is None or df_segmento.empty:
        return 0.0
    
    total_xg_contra = df_segmento['xg_contra'].sum()
    total_sot_contra = df_segmento['a_puerta_contra'].sum()
    
    if total_sot_contra > 0:
        return round(total_xg_contra / total_sot_contra, 3)
    return 0.0

def calcular_remates_totales_favor(df_equipo):
    if df_equipo.empty:
        return 0
    
    col_remates = 'shots_favor'
    
    if col_remates not in df_equipo.columns:
        return 0
    remates = pd.to_numeric(df_equipo[col_remates], errors='coerce').fillna(0)
    
    if len(remates) == 0:
        return 0
    
    return remates.mean()

def calcular_remates_totales_contra(df_equipo):
    if df_equipo.empty:
        return 0
    
    col_remates_contra = 'shots_contra'
    
    if col_remates_contra not in df_equipo.columns:
        return 0
    remates = pd.to_numeric(df_equipo[col_remates_contra], errors='coerce').fillna(0)
    
    if len(remates) == 0:
        return 0
    
    return remates.mean()

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
def media_ultimos(df, col, n, min_obs=1, default=0.0):
    if df is None or df.empty:
        return float(default)

    if col not in df.columns:
        return float(default)

    s = pd.to_numeric(df[col].tail(n), errors="coerce").dropna()
    if len(s) < min_obs:
        return float(default)

    return float(s.mean())

def blend_10_5_3(df, col):
    m10 = media_U(df, col, 10)
    m5 = media_U(df, col, 5)
    m3 = media_U(df, col, 3)
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

def media_U(df, col, n):
    if col not in df.columns or df.empty:
        return 0.0
    df_n = pd.to_numeric(df.tail(n)[col], errors="coerce").dropna()
    if df_n.empty or len(df_n) < 2:
        return 0.0
    return float(df_n.mean())

def winsorized_mean(series, lower_q=0.10, upper_q=0.90):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return 0.0
    low = s.quantile(lower_q)
    high = s.quantile(upper_q)
    s_w = s.clip(lower=low, upper=high)
    return float(s_w.mean())

def coef_variacion(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 2:
        return 0.0
    media = s.mean()
    if media == 0:
        return 0.0
    std = s.std(ddof=1)
    return float(std / media)

def resumen_ventana(df, col, n):
    if df.empty or col not in df.columns:
        return {
            "media": 0.0,
            "media_winsor": 0.0,
            "mediana": 0.0,
            "p25": 0.0,
            "p75": 0.0,
            "std": 0.0,
            "cv": 0.0, 
            "centro": 0.0
        }

    s = pd.to_numeric(df.tail(n)[col], errors="coerce").dropna()
    if s.empty:
        return {
            "media": 0.0,
            "media_winsor": 0.0,
            "mediana": 0.0,
            "p25": 0.0,
            "p75": 0.0,
            "std": 0.0,
            "cv": 0.0,
            "centro": 0.0
        }

    media = float(s.mean())
    media_winsor = winsorized_mean(s, 0.10, 0.90)
    mediana = float(s.median())
    p25 = float(s.quantile(0.25))
    p75 = float(s.quantile(0.75))
    std = float(s.std(ddof=1)) if len(s) > 1 else 0.0
    cv = coef_variacion(s)
    
    centro = 0.20 * media + 0.50 * media_winsor + 0.30 * mediana

    return {
        "media": media,
        "media_winsor": media_winsor,
        "mediana": mediana,
        "p25": p25,
        "p75": p75,
        "std": std,
        "cv": cv,
        "centro": centro
    }
    
def blend_resumenes_10_5_3(df, col, pesos=(0.25, 0.50, 0.25)):
    w10, w5, w3 = pesos

    r10 = resumen_ventana(df, col, 10)
    r5 = resumen_ventana(df, col, 5)
    r3 = resumen_ventana(df, col, 3)

    def mix(key):
        return (
            w10 * r10.get(key, 0.0) +
            w5 * r5.get(key, 0.0) +
            w3 * r3.get(key, 0.0)
        )

    media = mix("media")
    media_winsor = mix("media_winsor")
    mediana = mix("mediana")
    p25 = mix("p25")
    p75 = mix("p75")
    std = mix("std")
    cv = mix("cv")

    centro = (
        0.20 * media +
        0.50 * media_winsor +
        0.30 * mediana
    )

    return {
        "media": media,
        "media_winsor": media_winsor,
        "mediana": mediana,
        "p25": p25,
        "p75": p75,
        "std": std,
        "cv": cv,
        "centro": centro,
        "r10": r10,
        "r5": r5,
        "r3": r3
    }

def score_confianza_remates(proyeccion, rango_bajo, rango_alto, own, opp, n_own, n_opp):
    eps = 1e-6

    cv_mix = 0.60 * own.get("cv", 0.0) + 0.40 * opp.get("cv", 0.0)

    amp_rango = max(rango_alto - rango_bajo, 0.0)
    amp_rel = amp_rango / max(proyeccion, eps)

    c10_5_3_own = np.mean([
        abs(own["r10"].get("centro", 0) - own["r5"].get("centro", 0)) / max(own["centro"], eps),
        abs(own["r5"].get("centro", 0) - own["r3"].get("centro", 0)) / max(own["centro"], eps),
        abs(own["r10"].get("centro", 0) - own["r3"].get("centro", 0)) / max(own["centro"], eps),
    ])

    c10_5_3_opp = np.mean([
        abs(opp["r10"].get("centro", 0) - opp["r5"].get("centro", 0)) / max(opp["centro"], eps),
        abs(opp["r5"].get("centro", 0) - opp["r3"].get("centro", 0)) / max(opp["centro"], eps),
        abs(opp["r10"].get("centro", 0) - opp["r3"].get("centro", 0)) / max(opp["centro"], eps),
    ])

    inconsistencia = 0.60 * c10_5_3_own + 0.40 * c10_5_3_opp

    sample_penalty = 0.0
    if n_own < 10:
        sample_penalty += (10 - n_own) * 0.015
    if n_opp < 10:
        sample_penalty += (10 - n_opp) * 0.010

    score = (
        1.00
        - 0.40 * cv_mix
        - 0.20 * amp_rel
        - 0.25 * inconsistencia
        - sample_penalty
    )

    score = max(0.0, min(1.0, score))
    return {
        "score": score,
        "cv_mix": cv_mix,
        "amp_rel": amp_rel,
        "inconsistencia": inconsistencia,
        "sample_penalty": sample_penalty
    }


def proyectar_remates_robustos(
    df_equipo,
    df_rival,
    media_liga_favor,
    media_liga_contra_rival,
    col_favor="shots_favor",
    col_contra_rival="shots_contra",
    condicion=""
):
    own = blend_resumenes_10_5_3(df_equipo, col_favor)
    opp = blend_resumenes_10_5_3(df_rival, col_contra_rival)

    centro_ataque = own["centro"]
    centro_rival = opp["centro"]
    
    cv_mix = 0.60 * own["cv"] + 0.40 * opp["cv"]

    rel_ataque = centro_ataque / max(media_liga_favor, 1.0)
    rel_defensa = centro_rival / max(media_liga_contra_rival, 1.0)
    base_matchup = media_liga_favor * rel_ataque * rel_defensa

    proy_bruta = (
        0.60 * base_matchup +
        0.40 * centro_ataque 
    )
    
    momento_own = own["r3"].get("centro", 1) / max(own["r10"].get("centro", 1), 1e-6)
    momento_opp = opp["r3"].get("centro", 1) / max(opp["r10"].get("centro", 1), 1e-6)
        
    c10_5_3_own = np.mean([
        abs(own["r10"].get("centro", 0) - own["r5"].get("centro", 0)) / max(own["centro"], 1e-6),
        abs(own["r5"].get("centro", 0) - own["r3"].get("centro", 0)) / max(own["centro"], 1e-6),
        abs(own["r10"].get("centro", 0) - own["r3"].get("centro", 0)) / max(own["centro"], 1e-6),
    ])

    c10_5_3_opp = np.mean([
        abs(opp["r10"].get("centro", 0) - opp["r5"].get("centro", 0)) / max(opp["centro"], 1e-6),
        abs(opp["r5"].get("centro", 0) - opp["r3"].get("centro", 0)) / max(opp["centro"], 1e-6),
        abs(opp["r10"].get("centro", 0) - opp["r3"].get("centro", 0)) / max(opp["centro"], 1e-6),
    ])

    inconsistencia = 0.60 * c10_5_3_own + 0.40 * c10_5_3_opp
    factor_vol = max(0.88, min(1.12, 1 - 0.18 * cv_mix))
    proy_preliminar = max(proy_bruta * factor_vol, 0.01)   

    base_margen = min(0.28, max(0.08, 0.55 * cv_mix + 0.45 * inconsistencia))
    if condicion == "local":
        margen = min(0.45, max(0.12, base_margen))
    else:
        margen = min(0.30, max(0.08, base_margen))
        
    rango_bajo_pre = max(0.01, proy_preliminar * (1 - margen))
    rango_alto_pre = max(0.01, proy_preliminar * (1 + margen))
        
    conf = score_confianza_remates(
        proyeccion=proy_preliminar,
        rango_bajo=rango_bajo_pre,
        rango_alto=rango_alto_pre,
        own=own,
        opp=opp,
        n_own=min(len(df_equipo), 10),
        n_opp=min(len(df_rival), 10),
    )
    
    boost = 1.0
    if conf["score"] >= 0.72:
        boost = 1.0 + (max(0, (momento_own + momento_opp) / 2 - 1)* 0.5)
        boost = min(1.15, boost)  
        
    proy_final = proy_preliminar * boost
    rango_bajo = max(0.01, proy_final * (1 - margen))
    rango_alto = max(0.01, proy_final * (1 + margen))

    return {
        "proyeccion": proy_final,
        "base_matchup": base_matchup,
        "centro_ataque": centro_ataque,
        "centro_rival": centro_rival,
        "cv": cv_mix,
        "confianza": round(100 * conf["score"], 1),
        "confidence_score": conf["score"],
        "amp_rel": conf["amp_rel"],
        "inconsistencia": conf["inconsistencia"],
        "sample_penalty": conf["sample_penalty"],
        "rango_bajo": rango_bajo,
        "rango_alto": rango_alto,
        "ataque": own,
        "rival": opp
    }
    
def proyectar_remates_contra_robustos(
    df_equipo,
    df_rival,
    media_liga_concedidos,
    media_liga_rival_favor,
    col_contra = "shots_contra",
    col_favor_rival = "shots_favor",
    condicion = ""
):
    own = blend_resumenes_10_5_3(df_equipo, col_contra)
    opp = blend_resumenes_10_5_3(df_rival, col_favor_rival)
    
    centro_defensa = own["centro"]
    centro_ataque_rival = opp["centro"]
    
    cv_mix = 0.60 * own["cv"] + 0.40 * opp["cv"]
    
    rel_defensa = centro_defensa / max(media_liga_concedidos, 1.0)
    rel_ataque_rival = centro_ataque_rival / max(media_liga_rival_favor, 1.0)
    
    base_matchup = media_liga_concedidos * rel_defensa * rel_ataque_rival
    
    proy_bruta = (0.60 * base_matchup + 0.40 * centro_defensa)
    
    c10_5_3_own = np.mean([
        abs(own["r10"].get("centro", 0) - own["r5"].get("centro", 0)) / max(own["centro"], 1e-6),
        abs(own["r5"].get("centro", 0) - own["r3"].get("centro", 0)) / max(own["centro"], 1e-6),
        abs(own["r10"].get("centro", 0) - own["r3"].get("centro", 0)) / max(own["centro"], 1e-6),
    ])
    c10_5_3_opp = np.mean([
        abs(opp["r10"].get("centro", 0) - opp["r5"].get("centro", 0)) / max(opp["centro"], 1e-6),
        abs(opp["r5"].get("centro", 0) - opp["r3"].get("centro", 0)) / max(opp["centro"], 1e-6),
        abs(opp["r10"].get("centro", 0) - opp["r3"].get("centro", 0)) / max(opp["centro"], 1e-6),
    ])
    
    inconsistencia = 0.60 * c10_5_3_own + 0.40 * c10_5_3_opp
    
    factor_vol = max(0.88, min(1.12, 1 - 0.18 * cv_mix))
    proy_preliminar = max(proy_bruta * factor_vol, 0.01)
    
    base_margen = min(0.28, max(0.08, 0.55 * cv_mix + 0.45 * inconsistencia))
    margen = min(0.40, max(0.12, base_margen)) if condicion == "local" else min(0.30, max(0.08, base_margen))
    
    rango_bajo = max(0.01, proy_preliminar * (1 - margen))
    rango_alto = max(0.01, proy_preliminar * (1 + margen))
    
    conf = score_confianza_remates(
        proyeccion=proy_preliminar,
        rango_bajo=rango_bajo,
        rango_alto=rango_alto,
        own=own,
        opp = opp,
        n_own= min(len(df_equipo), 10),
        n_opp = min(len(df_rival), 10)
    )    
    
    return {
        "proyeccion": proy_preliminar,
        "rango_bajo": rango_bajo,
        "rango_alto": rango_alto,
        "confianza": round(100 * conf["score"], 1),
        "confidence_score": conf["score"],
        "cv": cv_mix,
        "defensa": own,
        "rival": opp
    }
    

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
    
def calcular_racha_supera_linea(df, col, linea, n=10, incluir_igual=False):
    if df.empty or col not in df.columns:
        return {
        "linea": float(linea),
        "muestra": 0,
        "racha_actual": 0,
        "racha_max": 0,
        "hits_n": 0,
        "pct_n": 0.0,
        "pct_txt": "0.0%",
        "racha_actual_txt": "0",
        "racha_max_txt": "0",
        "hits_txt": "0/0"
    }

    s = pd.to_numeric(df[col], errors="coerce").dropna().tail(n)
    partidos = len(s)

    if partidos == 0:
        return {
        "linea": float(linea),
        "muestra": 0,
        "racha_actual": 0,
        "racha_max": 0,
        "hits_n": 0,
        "pct_n": 0.0,
        "pct_txt": "0.0%",
        "racha_actual_txt": "0",
        "racha_max_txt": "0",
        "hits_txt": "0/0"
    }

    if incluir_igual:
        cumple = (s >= linea).astype(int).tolist()
    else:
        cumple = (s > linea).astype(int).tolist()
        
    hits = sum(cumple)
    pct = (hits/partidos) * 100 if partidos > 0 else 0.0

    racha_actual = 0
    for v in reversed(cumple):
        if v == 1:
            racha_actual += 1
        else:
            break

    racha_max = 0
    racha_temp = 0
    for v in cumple:
        if v == 1:
            racha_temp += 1
            racha_max = max(racha_max, racha_temp)
        else:
            racha_temp = 0

    return {
    "linea": float(linea),
    "muestra": partidos,
    "racha_actual": racha_actual,
    "racha_max": racha_max,
    "hits_n": hits,
    "pct_n": pct,
    "pct_txt": f"{pct:.1f}%",
    "racha_actual_txt": str(racha_actual),
    "racha_max_txt": str(racha_max),
    "hits_txt": f"{hits}/{partidos}"
    }
    
def calcular_score_regularidad(pct_historico, racha_actual, racha_max):    
    racha_norm = min(100.0, (racha_actual / 5.0) * 100.0)    
    racha_max_norm = min(100.0, (racha_max / 10.0) * 100.0)
    
    score = (
        0.70 * pct_historico +
        0.20 * racha_norm +
        0.10 * racha_max_norm
    )
    
    return round(score, 1)

def calcular_score_regularidad_goles(pct_marca, pct_recibe, racha_marca, racha_no_marca, racha_recibe, racha_no_recibe):
    racha_marca_norm = min(100.0, (racha_marca / 5.0) * 100.0)
    racha_no_recibe_norm = min(100.0, (racha_no_recibe / 5.0) * 100.0)
    
    score_ofensivo = (
        0.70 * pct_marca +
        0.30 * racha_marca_norm 
    )
    
    score_defensivo = (
        0.70 * pct_recibe +
        0.30 * racha_no_recibe_norm
    )
    
    score_combinado = 0.60 * score_ofensivo + 0.40 * score_defensivo
    
    return round(min(100.0, max(0.0, score_combinado)), 1)

def ajustar_prob_por_regularidad(
    prob_base,
    score_regularidad,
    cv,
    n_partidos,
    peso_regularidad_max=0.70,
    peso_regularidad_min=0.20,
):
    confianza = score_regularidad / 100.0
    
    penalizacion_cv = 0.15 * cv 
    
    penalizacion_muestra = max(0, (10 - n_partidos) * 0.01)
    
    peso_regularidad = confianza * (1 - penalizacion_cv - penalizacion_muestra)
    peso_regularidad = max(peso_regularidad_min, min(peso_regularidad_max, peso_regularidad))
    
    prob_final = (
        peso_regularidad * score_regularidad +
        (1 - peso_regularidad) * prob_base
    )
    
    return round(max(0.0, min(100.0, prob_final)), 1)

def ajustar_prob_goles_por_regularidad(
    prob_base,
    score_regularidad,
    cv_goles,
    n_partidos,
    peso_regularidad_max=0.40,
    peso_regularidad_min=0.15,
):   
    confianza = score_regularidad / 100.0
    
    penalizacion_cv = 0.20 * cv_goles 
    
    penalizacion_muestra = max(0, (10 - n_partidos) * 0.01)
    
    peso_regularidad = confianza * (1 - penalizacion_cv - penalizacion_muestra)
    peso_regularidad = max(peso_regularidad_min, min(peso_regularidad_max, peso_regularidad))
    
    prob_final = (
        peso_regularidad * score_regularidad +
        (1 - peso_regularidad) * prob_base
    )
    
    return round(max(0.0, min(100.0, prob_final)), 1)
        
def calcular_racha_supera_linea_total_partido(df, col_local, col_visitante, linea, n=10, incluir_igual=False):
    if df.empty or col_local not in df.columns or col_visitante not in df.columns:
        return {
            "linea": float(linea),
            "muestra": 0,
            "racha_actual": 0,
            "racha_max": 0,
            "hits_n": 0,
            "pct_n": 0.0,
            "pct_txt": "0.0%",
            "racha_actual_txt": "0",
            "racha_max_txt": "0",
            "hits_txt": "0/0"
        }

    temp = df.copy()
    temp["_total_partido_"] = (
        pd.to_numeric(temp[col_local], errors="coerce").fillna(0) +
        pd.to_numeric(temp[col_visitante], errors="coerce").fillna(0)
    )

    return calcular_racha_supera_linea(
        temp, "_total_partido_", linea, n=n, incluir_igual=incluir_igual
    )
    
def calcular_proyeccion_over_racha(
    pct_local,
    racha_local,
    max_local,
    pct_visitante,
    racha_visitante,
    max_visitante,
    peso_pct=0.70,
    peso_racha=0.20,
    peso_max=0.10,
):    
    def numero(valor, default=0.0):
        try:
            if pd.isna(valor):
                return default
            return float(str(valor).replace("%", "").replace(",", "."))
        except (TypeError, ValueError):
            return default

    pct_l = max(0.0, min(100.0, numero(pct_local)))
    pct_v = max(0.0, min(100.0, numero(pct_visitante)))
    racha_l = max(0.0, numero(racha_local))
    racha_v = max(0.0, numero(racha_visitante))
    max_l = max(0.0, numero(max_local))
    max_v = max(0.0, numero(max_visitante))

    # Normalizar rachas para que no dominen al porcentaje
    racha_l_norm = min(100.0, racha_l / 5.0 * 100.0)
    racha_v_norm = min(100.0, racha_v / 5.0 * 100.0)
    max_l_norm = min(100.0, max_l / 10.0 * 100.0)
    max_v_norm = min(100.0, max_v / 10.0 * 100.0)

    proy_local = (
        peso_pct * pct_l
        + peso_racha * racha_l_norm
        + peso_max * max_l_norm
    )
    proy_visitante = (
        peso_pct * pct_v
        + peso_racha * racha_v_norm
        + peso_max * max_v_norm
    )

    proyeccion = (proy_local + proy_visitante) / 2.0
    return round(max(0.0, min(100.0, proyeccion)), 1)

def probabilidad_over_remates(
    proy_equipo,
    proy_rival,
    linea,
    cv_equipo,
    cv_rival,
    n_equipo,
    n_rival,
    peso_equipo=0.60,
    peso_rival=0.40,
    factor_contexto = 1.0
):
    lambda_remates = (
        peso_equipo * proy_equipo +
        peso_rival * proy_rival
    )

    cv_mix = 0.6 * cv_equipo + 0.4 * cv_rival
    factor_vol = max(0.85, min(1.15, 1 - 0.3 * cv_mix))
    lambda_ajustado = (
        lambda_remates * factor_vol * factor_contexto
    )
    
    penalizacion_muestra = 0.0
    if n_equipo < 10:
        penalizacion_muestra += (10 - n_equipo) * 0.005
    if n_rival < 10:
        penalizacion_muestra += (10 - n_rival) * 0.003

    penalizacion_muestra = min(0.15, penalizacion_muestra)
    
    from math import floor
    k_linea = int(floor(linea))
    p_over = 1 - poisson.cdf(k_linea, lambda_ajustado)
    
    p_over = max(0.0, min(1.0, p_over - penalizacion_muestra))

    return round(p_over * 100, 1)

def probabilidad_over_sot(
    sot_equipo,
    sot_rival,
    linea,
    cv_equipo,
    cv_rival,
    n_equipo,
    n_rival,
    peso_equipo=0.60,
    peso_rival=0.40,
    factor_contexto = 1.0
):
    lambda_sot = (
        peso_equipo * sot_equipo +
        peso_rival * sot_rival
    )
    
    cv_mix = 0.6 * cv_equipo + 0.4 * cv_rival
    factor_vol = max(0.85, min(1.15, 1 - 0.3 * cv_mix))
    lambda_ajustado = (
        lambda_sot * factor_vol * factor_contexto
    )
    
    penalizacion_muestra = 0.0
    if n_equipo < 10:
        penalizacion_muestra += (10 - n_equipo) * 0.005
    if n_rival < 10:
        penalizacion_muestra += (10 - n_rival) * 0.003

    penalizacion_muestra = min(0.15, penalizacion_muestra)
    
    from math import floor
    k_linea = int(floor(linea))
    p_over = 1 - poisson.cdf(k_linea, lambda_ajustado)
    p_over = max(0.0, min(1.0, p_over - penalizacion_muestra))

    return round(p_over * 100, 1)


def construir_fila_over_total(
    linea,
    lambda_total,
    df_local,
    df_visitante,
    col_local,
    col_visitante,
    n=10,
    incluir_igual=False,
    proy_rem_local=None,
    proy_rem_vis=None,
    cv_rem_local=None,
    cv_rem_vis=None,
    n_rem_local=None,
    n_rem_vis=None,
):
   
    under, over_poisson = poisson_prob_over_under(
        lambda_total, linea, max_k=40
    )

    hist_local = calcular_racha_supera_linea_total_partido(
        df_local,
        col_local,
        col_visitante,
        linea,
        n=n,
        incluir_igual=incluir_igual,
    )
    hist_visitante = calcular_racha_supera_linea_total_partido(
        df_visitante,
        col_local,
        col_visitante,
        linea,
        n=n,
        incluir_igual=incluir_igual,
    )

    proyeccion = calcular_proyeccion_over_racha(
        hist_local["pct_n"],
        hist_local["racha_actual"],
        hist_local["racha_max"],
        hist_visitante["pct_n"],
        hist_visitante["racha_actual"],
        hist_visitante["racha_max"],
    )

    if (
        proy_rem_local is not None and
        proy_rem_vis is not None and
        cv_rem_local is not None and
        cv_rem_vis is not None and
        n_rem_local is not None and
        n_rem_vis is not None
    ):
        lambda_rem_total = proy_rem_local + proy_rem_vis

        cv_mix = 0.6 * cv_rem_local + 0.4 * cv_rem_vis
        factor_vol = max(0.85, min(1.15, 1 - 0.3 * cv_mix))
        lambda_ajustado = lambda_rem_total * factor_vol
        
        penalizacion_muestra = 0.0
        if n_rem_local < 10:
            penalizacion_muestra += (10 - n_rem_local) * 0.005
        if n_rem_vis < 10:
            penalizacion_muestra += (10 - n_rem_vis) * 0.003
        penalizacion_muestra = min(0.15, penalizacion_muestra)
        
        from math import floor        
        k_linea = int(floor(linea))
        p_over = 1 - poisson.cdf(k_linea, lambda_ajustado)
        p_over = max(0.0, min(1.0, p_over - penalizacion_muestra))
        proyeccion = round(p_over * 100, 1)
    else:
        proyeccion = calcular_proyeccion_over_racha(
            hist_local["pct_n"],
            hist_local["racha_actual"],
            hist_local["racha_max"],
            hist_visitante["pct_n"],
            hist_visitante["racha_actual"],
            hist_visitante["racha_max"],
        )

    return [
        linea,
        over_poisson,
        under, 
        hist_local["pct_txt"],
        hist_local["racha_actual_txt"],
        hist_local["racha_max_txt"],
        hist_visitante["pct_txt"],
        hist_visitante["racha_actual_txt"],
        hist_visitante["racha_max_txt"],
        proyeccion
    ]
    
def calcular_racha_concede_linea(
    df,
    col_contra,
    linea,
    n=10,
    incluir_igual=False,
):
    if df.empty or col_contra not in df.columns:
        return {
            "linea": float(linea),
            "muestra": 0,
            "racha_actual": 0,
            "racha_max": 0,
            "hits_n": 0,
            "pct_n": 0.0,
            "pct_txt": "0.0%",
            "racha_actual_txt": "0",
            "racha_max_txt": "0",
            "hits_txt": "0/0"
        }

    s = pd.to_numeric(df[col_contra], errors="coerce").dropna().tail(n)
    partidos = len(s)

    if partidos == 0:
        return {
            "linea": float(linea),
            "muestra": 0,
            "racha_actual": 0,
            "racha_max": 0,
            "hits_n": 0,
            "pct_n": 0.0,
            "pct_txt": "0.0%",
            "racha_actual_txt": "0",
            "racha_max_txt": "0",
            "hits_txt": "0/0"
        }

    if incluir_igual:
        cumple = (s >= linea).astype(int).tolist()
    else:
        cumple = (s > linea).astype(int).tolist()

    hits = sum(cumple)
    pct = (hits / partidos) * 100 if partidos > 0 else 0.0

    racha_actual = 0
    for v in reversed(cumple):
        if v == 1:
            racha_actual += 1
        else:
            break

    racha_max = 0
    racha_temp = 0
    for v in cumple:
        if v == 1:
            racha_temp += 1
            racha_max = max(racha_max, racha_temp)
        else:
            racha_temp = 0

    return {
        "linea": float(linea),
        "muestra": partidos,
        "racha_actual": racha_actual,
        "racha_max": racha_max,
        "hits_n": hits,
        "pct_n": pct,
        "pct_txt": f"{pct:.1f}%",
        "racha_actual_txt": str(racha_actual),
        "racha_max_txt": str(racha_max),
        "hits_txt": f"{hits}/{partidos}"
    }


def calcular_proyeccion_individual(
    proy_equipo,
    proy_rival,
    linea,
    cv_equipo,
    cv_rival,
    n_equipo,
    n_rival,
    peso_equipo=0.60,
    peso_rival=0.40,
    pct_historico_equipo=None,
    racha_actual_equipo=None,
    racha_max_equipo=None,
    pct_historico_rival=None,
    racha_actual_rival=None,
    racha_max_rival=None,
    factor_contexto = 1.0
):
    prob_base = probabilidad_over_remates(
        proy_equipo,
        proy_rival,
        linea,
        cv_equipo,
        cv_rival,
        n_equipo,
        n_rival,
        peso_equipo,
        peso_rival,
        factor_contexto = factor_contexto
    )
    
    if (
        pct_historico_equipo is None or
        racha_actual_equipo is None or
        racha_max_equipo is None
    ):
        return prob_base
    
    score_equipo = calcular_score_regularidad(
        pct_historico_equipo,
        racha_actual_equipo,
        racha_max_equipo,
    )
    
    if (
        pct_historico_rival is not None and
        racha_actual_rival is not None and
        racha_max_rival is not None
    ):
        score_rival = calcular_score_regularidad(
            pct_historico_rival,
            racha_actual_rival,
            racha_max_rival,
        )
        score_combinado = 0.60 * score_equipo + 0.40 * score_rival
    else:
        score_combinado = score_equipo
    
    cv_mix = 0.6 * cv_equipo + 0.4 * cv_rival
    n_mix = min(n_equipo, n_rival)
    
    prob_final = ajustar_prob_por_regularidad(
        prob_base,
        score_combinado,
        cv_mix,
        n_mix,
    )
    
    return prob_final
    
def calcular_proyeccion_individual_sot(
    sot_equipo,
    sot_rival,
    linea,
    cv_equipo,
    cv_rival,
    n_equipo,
    n_rival,
    peso_equipo=0.60,
    peso_rival=0.40,
    pct_historico_equipo=None,
    racha_actual_equipo=None,
    racha_max_equipo=None,
    pct_historico_rival=None,
    racha_actual_rival=None,
    racha_max_rival=None,
    factor_contexto = 1.0,
):   
    prob_base = probabilidad_over_sot(
        sot_equipo,
        sot_rival,
        linea,
        cv_equipo,
        cv_rival,
        n_equipo,
        n_rival,
        peso_equipo,
        peso_rival,
        factor_contexto=factor_contexto,
    )
        
    if (
        pct_historico_equipo is None or
        racha_actual_equipo is None or
        racha_max_equipo is None
    ):
        return prob_base
    
    score_equipo = calcular_score_regularidad(
        pct_historico_equipo,
        racha_actual_equipo,
        racha_max_equipo,
    )
    
    if (
        pct_historico_rival is not None and
        racha_actual_rival is not None and
        racha_max_rival is not None
    ):
        score_rival = calcular_score_regularidad(
            pct_historico_rival,
            racha_actual_rival,
            racha_max_rival,
        )
        score_combinado = 0.60 * score_equipo + 0.40 * score_rival
    else:
        score_combinado = score_equipo
    
    cv_mix = 0.6 * cv_equipo + 0.4 * cv_rival
    n_mix = min(n_equipo, n_rival)
    
    prob_final = ajustar_prob_por_regularidad(
        prob_base,
        score_combinado,
        cv_mix,
        n_mix,
    )
    
    return prob_final

def normalizar_metrica(pct, racha_act, racha_max):   
    componente_pct = 0.70 * pct
    
    if racha_max == 0:
        componente_racha = 0.0
    else:
        componente_racha = 0.30 * ((racha_act / racha_max)*100)
    
    if racha_max > 0 and racha_act == racha_max:
        componente_bono = 0.05 * 100
    else:
        componente_bono = 0.0
    
    resultado = componente_pct + componente_racha + componente_bono
    
    return max(0.0, min(100.0, resultado))

def extraer_metricas_gol(stats, equipo_nombre, rango):
    col_valor = f"{equipo_nombre} ({rango})"
    col_racha = f"R{rango}"

    if col_valor not in stats or col_racha not in stats:
        raise KeyError(
            f"No existen las columnas '{col_valor}' o '{col_racha}'"
        )

    estadisticas = stats["Estadística"]

    def indice(nombre):
        if nombre not in estadisticas:
            raise KeyError(f"No existe la estadística '{nombre}'")
        return estadisticas.index(nombre)

    def porcentaje(nombre):
        valor = stats[col_valor][indice(nombre)]
        if isinstance(valor, str):
            valor = valor.replace("%", "").replace(",", ".").strip()
        return float(valor)

    def racha(nombre):
        return float(stats[col_racha][indice(nombre)])

    return {
        "marca_pct": porcentaje("Marca Gol"),
        "marca_racha": racha("Marca Gol"),
        "marca_max": racha("Máx. Racha Marca Gol"),

        "recibe_pct": porcentaje("Recibe Gol"),
        "recibe_racha": racha("Recibe Gol"),
        "recibe_max": racha("Máx. Racha Recibe Gol"),

        "no_marca_pct": porcentaje("No Marca Gol"),
        "no_marca_racha": racha("No Marca Gol"),
        "no_marca_max": racha("Máx. Racha No Marca"),

        "no_recibe_pct": porcentaje("No Recibe Gol"),
        "no_recibe_racha": racha("No Recibe Gol"),
        "no_recibe_max": racha("Máx. Racha No Recibe"),
    }
    
def extraer_entrada_goles(df, condicion, rango):    
    if condicion not in ("local", "visitante"):
        raise ValueError(
            "La condición debe ser 'local' o 'visitante'."
        )        

    if rango not in (3, 5, 10):
        raise ValueError(
            "El rango debe ser 3, 5 o 10."
        )

    if df is None or df.empty:
        raise ValueError(
            f"No hay partidos disponibles para la condición {condicion}."
        )

    col_favor = (
        "goles_local"
        if condicion == "local"
        else "goles_visitante"
    )

    col_contra = (
        "goles_visitante"
        if condicion == "local"
        else "goles_local"
    )

    faltantes = {
        col_favor, col_contra
    } - set(df.columns)

    if faltantes:
        raise ValueError(
            "Faltan columnas de goles: "
            + ", ".join(sorted(faltantes))
        )

    datos = df.copy()

    favor = pd.to_numeric(
        datos[col_favor],
        errors="coerce",
    )

    contra = pd.to_numeric(
        datos[col_contra],
        errors="coerce",
    )

    validos = (
        favor.notna()
        & contra.notna()
        & np.isfinite(favor)
        & np.isfinite(contra)
        & (favor >= 0)
        & (contra >= 0)
        & (favor == np.floor(favor))
        & (contra == np.floor(contra))
    )

    filas_invalidas = int((~validos).sum())

    datos = datos.loc[validos].copy()
    datos["_gf_modelo"] = favor.loc[validos].astype(int)
    datos["_gc_modelo"] = contra.loc[validos].astype(int)

    muestra = datos.tail(rango).copy()

    if muestra.empty:
        raise ValueError(
            f"No hay marcadores válidos para {condicion}, U{rango}."
        )

    gf = muestra["_gf_modelo"]
    gc = muestra["_gc_modelo"]
    total = gf + gc

    n = len(muestra)

    def resumen_evento(condicion_evento):
        """
        Frecuencia histórica y rachas dentro de la misma ventana.
        """
        secuencia = condicion_evento.astype(bool).tolist()

        actual = 0

        for cumple in reversed(secuencia):
            if not cumple:
                break
            actual += 1

        maxima = 0
        acumulada = 0

        for cumple in secuencia:
            if cumple:
                acumulada += 1
                maxima = max(maxima, acumulada)
            else:
                acumulada = 0

        aciertos = int(sum(secuencia))

        return {
            "hits": aciertos,
            "pct": 100.0 * aciertos / n,
            "racha_actual": actual,
            "racha_max": maxima,
        }

    eventos = {
        "marca": resumen_evento(gf >= 1),
        "recibe": resumen_evento(gc >= 1),
        "no_marca": resumen_evento(gf == 0),
        "no_recibe": resumen_evento(gc == 0),

        "marca_2mas": resumen_evento(gf >= 2),
        "recibe_2mas": resumen_evento(gc >= 2),
        "marca_3mas": resumen_evento(gf >= 3),
        "recibe_3mas": resumen_evento(gc >= 3),

        "btts": resumen_evento((gf >= 1) & (gc >= 1)),
        "over_15": resumen_evento(total >= 2),
        "over_25": resumen_evento(total >= 3),
    }

    media_goles_cuando_marca = (
        float(gf.loc[gf >= 1].mean())
        if (gf >= 1).any()
        else None
    )

    media_goles_cuando_recibe = (
        float(gc.loc[gc >= 1].mean())
        if (gc >= 1).any()
        else None
    )

    columnas_detalle = [
        columna
        for columna in ["fecha", "equipo_local", "visitante"]
        if columna in muestra.columns
    ]

    detalle = muestra[columnas_detalle].copy()

    detalle["Goles favor"] = gf.to_numpy()
    detalle["Goles contra"] = gc.to_numpy()
    detalle["Goles totales"] = total.to_numpy()

    return {
        "condicion": condicion,
        "rango_solicitado": rango,
        "n_partidos": n,
        "n_validos_disponibles": len(datos),
        "filas_invalidas": filas_invalidas,

        "goles_favor_total": int(gf.sum()),
        "goles_contra_total": int(gc.sum()),

        "media_goles_favor": float(gf.mean()),
        "media_goles_contra": float(gc.mean()),
        "media_goles_total": float(total.mean()),

        "media_goles_cuando_marca": media_goles_cuando_marca,
        "media_goles_cuando_recibe": media_goles_cuando_recibe,

        "std_goles_favor": (
            float(gf.std(ddof=1)) if n > 1 else None
        ),
        "std_goles_contra": (
            float(gc.std(ddof=1)) if n > 1 else None
        ),

        "eventos": eventos,

        "goles_favor": gf.tolist(),
        "goles_contra": gc.tolist(),

        "detalle": detalle.reset_index(drop=True),
        "datos_modelo": muestra.copy(),
    }
    
def mostrar_diagnostico_entrada_goles(
    entrada_local,
    entrada_visitante,
    nombre_local,
    nombre_visitante,
):
    def resumen_columna(entrada):
        eventos = entrada["eventos"]

        return {
            "Rango solicitado": entrada["rango_solicitado"],
            "Partidos utilizados": entrada["n_partidos"],

            "Goles favor": entrada["goles_favor_total"],
            "Goles contra": entrada["goles_contra_total"],

            "Media goles favor": entrada["media_goles_favor"],
            "Media goles contra": entrada["media_goles_contra"],
            "Media goles totales": entrada["media_goles_total"],

            "Media cuando marca": (
                entrada["media_goles_cuando_marca"]
            ),
            "Media cuando recibe": (
                entrada["media_goles_cuando_recibe"]
            ),

            "Marca %": eventos["marca"]["pct"],
            "Marca: racha actual": (
                eventos["marca"]["racha_actual"]
            ),
            "Marca: racha máxima": (
                eventos["marca"]["racha_max"]
            ),

            "Recibe %": eventos["recibe"]["pct"],
            "Recibe: racha actual": (
                eventos["recibe"]["racha_actual"]
            ),
            "Recibe: racha máxima": (
                eventos["recibe"]["racha_max"]
            ),

            "No marca %": eventos["no_marca"]["pct"],
            "No recibe %": eventos["no_recibe"]["pct"],

            "Marca 2+ %": eventos["marca_2mas"]["pct"],
            "Recibe 2+ %": eventos["recibe_2mas"]["pct"],
            "Marca 3+ %": eventos["marca_3mas"]["pct"],
            "Recibe 3+ %": eventos["recibe_3mas"]["pct"],

            "BTTS histórico %": eventos["btts"]["pct"],
            "Over 1.5 histórico %": eventos["over_15"]["pct"],
            "Over 2.5 histórico %": eventos["over_25"]["pct"],

            "Filas inválidas en DF recibido": (
                entrada["filas_invalidas"]
            ),
        }

    nombre_col_local = f"{nombre_local} · Local"
    nombre_col_vis = f"{nombre_visitante} · Visitante"

    tabla = pd.DataFrame({
        nombre_col_local: resumen_columna(entrada_local),
        nombre_col_vis: resumen_columna(entrada_visitante),
    })

    tabla.index.name = "Dato"
    tabla = tabla.reset_index()

    def formato_valor(valor):
        if pd.isna(valor):
            return "Sin datos"

        numero = float(valor)

        if numero.is_integer():
            return str(int(numero))

        return f"{numero:.2f}"

    st.table(
        tabla.style
        .format({
            nombre_col_local: formato_valor,
            nombre_col_vis: formato_valor,
        })
        .hide(axis="index")
    )

    st.caption(
        "Los porcentajes de esta tabla son frecuencias históricas "
        "de la ventana seleccionada, no probabilidades futuras."
    )

    st.markdown("#### 🏠 Partidos utilizados del local")

    st.table(
        entrada_local["detalle"].style
        .hide(axis="index")
    )

    st.markdown("#### ✈️ Partidos utilizados del visitante")

    st.table(
        entrada_visitante["detalle"].style
        .hide(axis="index")
    )
    
def mostrar_traza_modelo_goles(
    prediccion,
    prediccion_contexto,
):
    lambda_local_base = float(
        prediccion["_lambda_local_base"]
    )
    lambda_vis_base = float(
        prediccion["_lambda_visitante_base"]
    )

    lambda_local_final = float(
        prediccion_contexto.get(
            "_lambda_local_contexto",
            lambda_local_base,
        )
    )
    lambda_vis_final = float(
        prediccion_contexto.get(
            "_lambda_visitante_contexto",
            lambda_vis_base,
        )
    )

    factor_local = float(
        prediccion_contexto.get(
            "_factor_contexto_local",
            1.0,
        )
    )
    factor_vis = float(
        prediccion_contexto.get(
            "_factor_contexto_visitante",
            1.0,
        )
    )

    tabla_lambdas = pd.DataFrame([
        {
            "Equipo": "Local",
            "PJ propios": prediccion["_n_local"],
            "Media GF propia": prediccion["_media_gf_local"],
            "Media GC del rival": (
                prediccion["_media_gc_visitante"]
            ),
            "Lambda base": lambda_local_base,
            "Factor contexto": factor_local,
            "Lambda final": lambda_local_final,
        },
        {
            "Equipo": "Visitante",
            "PJ propios": prediccion["_n_visitante"],
            "Media GF propia": (
                prediccion["_media_gf_visitante"]
            ),
            "Media GC del rival": (
                prediccion["_media_gc_local"]
            ),
            "Lambda base": lambda_vis_base,
            "Factor contexto": factor_vis,
            "Lambda final": lambda_vis_final,
        },
    ])

    columnas_decimales = [
        "Media GF propia",
        "Media GC del rival",
        "Lambda base",
        "Factor contexto",
        "Lambda final",
    ]

    st.table(
        tabla_lambdas.style
        .format({
            columna: "{:.3f}"
            for columna in columnas_decimales
        })
        .hide(axis="index")
    )

    filas_controles = []

    for etiqueta, valores in [
        ("Base", prediccion),
        ("Con contexto", prediccion_contexto),
    ]:
        suma_1x2 = (
            valores["Gana Local"]
            + valores["Empate"]
            + valores["Gana Visitante"]
        )

        filas_controles.append({
            "Versión": etiqueta,
            "Suma 1X2 %": suma_1x2,
            "Over 1.5 %": valores["Over 1.5"],
            "Over 2.5 %": valores["Over 2.5"],
            "Exactamente 2 goles %": (
                valores["Over 1.5"]
                - valores["Over 2.5"]
            ),
            "BTTS %": valores["BTTS"],
        })

    controles = pd.DataFrame(filas_controles)

    st.table(
        controles.style
        .format({
            columna: "{:.2f}"
            for columna in controles.columns
            if columna != "Versión"
        })
        .hide(axis="index")
    )

    st.caption(
        "Lambda base = 50% de la media de goles a favor propia "
        "+ 50% de la media concedida por el rival. "
        "Exactamente 2 goles = Over 1.5 − Over 2.5. "
        "Los valores son salidas del modelo, no resultados "
        "garantizados."
    )

def calcular_prediccion_marca_recibe(
    marca_gol_local_pct, racha_marca_local, max_racha_marca_local,
    recibe_gol_local_pct, racha_recibe_local, max_racha_recibe_local,
    no_marca_gol_local_pct, racha_no_marca_local, max_racha_no_marca_local,
    no_recibe_gol_local_pct, racha_no_recibe_local, max_racha_no_recibe_local,
    marca_gol_visitante_pct, racha_marca_visitante, max_racha_marca_visitante,
    recibe_gol_visitante_pct, racha_recibe_visitante, max_racha_recibe_visitante,
    no_marca_gol_visitante_pct, racha_no_marca_visitante, max_racha_no_marca_visitante,
    no_recibe_gol_visitante_pct, racha_no_recibe_visitante, max_racha_no_recibe_visitante,
    df_local = None, df_visitante = None,
):
    from math import log
    
    # === NORMALIZAR MÉTRICAS ===
    marca_gol_local_norm = normalizar_metrica(marca_gol_local_pct, racha_marca_local, max_racha_marca_local)
    recibe_gol_local_norm = normalizar_metrica(recibe_gol_local_pct, racha_recibe_local, max_racha_recibe_local)
    no_marca_gol_local_norm = normalizar_metrica(no_marca_gol_local_pct, racha_no_marca_local, max_racha_no_marca_local)
    no_recibe_gol_local_norm = normalizar_metrica(no_recibe_gol_local_pct, racha_no_recibe_local, max_racha_no_recibe_local)
    
    marca_gol_visitante_norm = normalizar_metrica(marca_gol_visitante_pct, racha_marca_visitante, max_racha_marca_visitante)
    recibe_gol_visitante_norm = normalizar_metrica(recibe_gol_visitante_pct, racha_recibe_visitante, max_racha_recibe_visitante)
    no_marca_gol_visitante_norm = normalizar_metrica(no_marca_gol_visitante_pct, racha_no_marca_visitante, max_racha_no_marca_visitante)
    no_recibe_gol_visitante_norm = normalizar_metrica(no_recibe_gol_visitante_pct, racha_no_recibe_visitante, max_racha_no_recibe_visitante)
    
    # === CALCULAR ATAQUE Y DEFENSA ===
    ataque_local = (
        0.50 * (marca_gol_local_norm) +
        0.20 * (100 - (no_marca_gol_local_norm)) +
        0.30 * (recibe_gol_visitante_norm)
    )

    defensa_local = (
        0.50 * no_recibe_gol_local_norm +
        0.50 * (100 - recibe_gol_local_norm)
    )

    ataque_visitante = (
        0.50 * (marca_gol_visitante_norm) +
        0.20 * (100 - (no_marca_gol_visitante_norm)) +
        0.30 * (recibe_gol_local_norm)
    )

    defensa_visitante = (
        0.50 * no_recibe_gol_visitante_norm +
        0.50 * (100 - recibe_gol_visitante_norm)
    )   
      
    # === PROBABILIDAD DE MARCAR ===   
    prob_marcar_local = max(1, min(99, 0.65 * ataque_local + 0.35 * (100 - defensa_visitante)))
    prob_marcar_visitante = max(1, min(99, 0.65 * ataque_visitante + 0.35 * (100 - defensa_local)))
   
    # === LAMBDA POISSON ===
    lambda_local = -log(1 - prob_marcar_local/100) 
    lambda_visitante = -log(1 - prob_marcar_visitante/100)     
    
    # === PROBABILIDADES DE MERCADO ===
    prob_1x2 = poisson_prob_1x2_y_dobles(lambda_local, lambda_visitante, max_goals=8)
    prob_btts_val = prob_btts(lambda_local, lambda_visitante, max_goals=8)
    _, over_15 = poisson_prob_total_over_under(lambda_local, lambda_visitante, 1.5, max_k=8)
    _, over_25 = poisson_prob_total_over_under(lambda_local, lambda_visitante, 2.5, max_k=8)
    
    prob_marca_local = probabilidad_poisson(lambda_local) * 100
    prob_marca_visitante = probabilidad_poisson(lambda_visitante) * 100   
    
    score_regularidad_local = calcular_score_regularidad_goles(
        pct_marca=marca_gol_local_pct,
        pct_recibe=no_recibe_gol_local_pct,
        racha_marca=racha_marca_local,
        racha_no_marca=racha_no_marca_local,
        racha_recibe=racha_recibe_local,
        racha_no_recibe=racha_no_recibe_local,
    )

    score_regularidad_visitante = calcular_score_regularidad_goles(
        pct_marca=marca_gol_visitante_pct,
        pct_recibe=no_recibe_gol_visitante_pct,
        racha_marca=racha_marca_visitante,
        racha_no_marca=racha_no_marca_visitante,
        racha_recibe=racha_recibe_visitante,
        racha_no_recibe=racha_no_recibe_visitante,
    )

    score_regularidad_total = 0.5 * score_regularidad_local + 0.5 * score_regularidad_visitante
    
    goles_local = pd.to_numeric(df_local["goles_local"], errors="coerce").dropna().tail(10)
    goles_visitante = pd.to_numeric(df_visitante["goles_visitante"], errors="coerce").dropna().tail(10)

    cv_local = goles_local.std() / goles_local.mean() if len(goles_local) > 1 and goles_local.mean() > 0 else 0.3
    cv_visitante = goles_visitante.std() / goles_visitante.mean() if len(goles_visitante) > 1 and goles_visitante.mean() > 0 else 0.3
    cv_goles_mix = 0.5 * cv_local + 0.5 * cv_visitante
    n_partidos = min(len(goles_local), len(goles_visitante), 10)

    btts_ajustado = ajustar_prob_goles_por_regularidad(
        prob_btts_val,
        score_regularidad_total,
        cv_goles_mix,
        n_partidos,
    )

    over_15_ajustado = ajustar_prob_goles_por_regularidad(
        over_15,
        score_regularidad_total,
        cv_goles_mix,
        n_partidos,
    )

    over_25_ajustado = ajustar_prob_goles_por_regularidad(
        over_25,
        score_regularidad_total,
        cv_goles_mix,
        n_partidos,
    )

    marca_local_ajustado = ajustar_prob_goles_por_regularidad(
        prob_marca_local,
        score_regularidad_local,
        cv_local,
        n_partidos,
    )

    marca_visitante_ajustado = ajustar_prob_goles_por_regularidad(
        prob_marca_visitante,
        score_regularidad_visitante,
        cv_visitante,
        n_partidos,
    )

    return {
        "Gana Local": prob_1x2["1"],
        "Empate": prob_1x2["X"],
        "Gana Visitante": prob_1x2["2"],
        "1X": prob_1x2["1X"],
        "12": prob_1x2["12"],
        "X2": prob_1x2["X2"],
        "Marca Local": round(marca_local_ajustado, 1),
        "Marca Visitante": round(marca_visitante_ajustado, 1),
        "BTTS": round(btts_ajustado, 1),
        "Over 1.5": round(over_15_ajustado, 1),
        "Over 2.5": round(over_25_ajustado, 1),
    }
    
# === MÉTRICAS AVANZADAS: ATAQUE, DEFENSA, REMATES Y SOT ===
def calcular_metricas_avanzadas(df_local, df_visitante, equipo_local_archivo = None, equipo_visitante_archivo = None):
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
    PESO_ATAQUE = 0.6
    PESO_DEFENSA = 0.4
    lambda_local_new = (PESO_ATAQUE * Ataque_final_local + PESO_DEFENSA * Defensa_final_vis)
    lambda_vis_new = (PESO_ATAQUE* Ataque_final_vis + PESO_DEFENSA * Defensa_final_local)

    # Evitar negativos
    lambda_local_new = max(lambda_local_new, 0.01)
    lambda_vis_new = max(lambda_vis_new, 0.01)

    # --- PRECISIÓN DEL PARTIDO ---
    P_match_local = (P_att_local + P_def_local) / 2.0
    P_match_vis = (P_att_vis + P_def_vis) / 2.0

    # === REMATES ROBUSTOS: WINSOR, MEDIANA, PERCENTILES, STD, CV ===
    df_local_name = equipo_local_archivo
    df_visitante_name = equipo_visitante_archivo

    pais_local = pais_de_equipo(equipo_local_archivo) if equipo_local_archivo else None
    pais_vis = pais_de_equipo(equipo_visitante_archivo) if equipo_visitante_archivo else None

    if pais_local and pais_vis:
        liga_shots_local_fav, liga_shots_local_contra = media_remates_liga(pais_local, "local")
        liga_shots_vis_fav, liga_shots_vis_contra = media_remates_liga(pais_vis, "visitante")
    else:
        liga_shots_local_fav, liga_shots_local_contra = 12.5, 11.8
        liga_shots_vis_fav, liga_shots_vis_contra = 10.8, 12.2

    remates_local_obj = proyectar_remates_robustos(
        df_equipo=df_local,
        df_rival=df_visitante,
        media_liga_favor=liga_shots_local_fav,
        media_liga_contra_rival=liga_shots_vis_contra,
        col_favor="shots_favor",
        col_contra_rival="shots_contra", 
        condicion="local"
    )

    remates_vis_obj = proyectar_remates_robustos(
        df_equipo=df_visitante,
        df_rival=df_local,
        media_liga_favor=liga_shots_vis_fav,
        media_liga_contra_rival=liga_shots_local_contra,
        col_favor="shots_favor",
        col_contra_rival="shots_contra",
        condicion="visitante"
    )
    
    remates_local_contra = proyectar_remates_contra_robustos(
        df_equipo = df_local,
        df_rival = df_visitante,
        media_liga_concedidos = liga_shots_local_contra,
        media_liga_rival_favor = liga_shots_vis_fav,
        col_contra = "shots_contra",
        col_favor_rival = "shots_favor",
        condicion = "local"
    )
    
    remates_vis_contra = proyectar_remates_contra_robustos(
        df_equipo = df_visitante,
        df_rival = df_local,
        media_liga_concedidos = liga_shots_vis_contra,
        media_liga_rival_favor = liga_shots_local_fav,
        col_contra = "shots_contra",
        col_favor_rival = "shots_favor",
        condicion = "visitante"
    )
    
    eps = 1e-6
    xg_shot_local = xGF_local / max(remates_local_obj["centro_ataque"], eps)
    xg_shot_vis = xGF_vis / max(remates_vis_obj["centro_ataque"], eps)

    def cap_factor_xg(x):
        f = np.sqrt(max(x, 0.0))
        return max(0.95, min(1.05, f))

    F_xg_local = cap_factor_xg(xg_shot_local)
    F_xg_vis = cap_factor_xg(xg_shot_vis)
    
    xga_shot_local = xGC_local / max(remates_local_contra["defensa"]["centro"], eps)
    xga_shot_vis = xGC_vis / max(remates_vis_contra["defensa"]["centro"], eps)

    def cap_factor_xga(x):
        f = np.sqrt(max(x, 0.0))
        return max(0.97, min(1.03, f))

    F_xga_local = cap_factor_xga(xga_shot_local)
    F_xga_vis = cap_factor_xga(xga_shot_vis)    

    Remates_att_local = max(remates_local_obj["proyeccion"] * F_xg_local, 0.01)
    Remates_att_vis = max(remates_vis_obj["proyeccion"] * F_xg_vis, 0.01)
    Remates_contra_local = max(remates_local_contra["proyeccion"] * F_xga_local, 0.01)
    Remates_contra_vis = max(remates_vis_contra["proyeccion"] * F_xga_vis, 0.01)   
        
    linea_rem_l = max(1, int(np.floor(Remates_att_local + 0.5)))
    linea_rem_v = max(1, int(np.floor(Remates_att_vis + 0.5)))
        
    racha_rem_l = calcular_racha_supera_linea(df_local, "shots_favor", linea_rem_l, incluir_igual=True)
    racha_rem_v = calcular_racha_supera_linea(df_visitante, "shots_favor", linea_rem_v, incluir_igual=True)

    # --- TIROS A PUERTA ESPERADOS (SoT) ---
    SoT_local = Remates_att_local * P_match_local
    SoT_vis = Remates_att_vis * P_match_vis

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
        "Remates_contra_local": Remates_contra_local,
        "Remates_contra_vis": Remates_contra_vis,
        "Remates_base_matchup_local": remates_local_obj["base_matchup"],
        "Remates_base_matchup_vis": remates_vis_obj["base_matchup"],

        "Remates_rango_local_low": remates_local_obj["rango_bajo"],
        "Remates_rango_local_high": remates_local_obj["rango_alto"],
        "Remates_rango_vis_low": remates_vis_obj["rango_bajo"],
        "Remates_rango_vis_high": remates_vis_obj["rango_alto"],
        
        "Remates_rango_local_contra_low": remates_local_contra["rango_bajo"],
        "Remates_rango_local_contra_high": remates_local_contra["rango_alto"],
        "Remates_rango_vis_contra_low": remates_vis_contra["rango_bajo"],
        "Remates_rango_vis_contra_high": remates_vis_contra["rango_alto"],

        "Remates_cv_local": remates_local_obj["cv"],
        "Remates_cv_vis": remates_vis_obj["cv"],
        
        "Remates_confianza_local": remates_local_obj["confianza"],
        "Remates_confianza_vis": remates_vis_obj["confianza"],        
        "Remates_confianza_local_contra": remates_local_contra["confianza"],
        "Remates_confianza_vis_contra": remates_vis_contra["confianza"],
        
        "Remates_centro_ataque_local": remates_local_obj["centro_ataque"],
        "Remates_centro_rival_local": remates_local_obj["centro_rival"],
        "Remates_centro_ataque_vis": remates_vis_obj["centro_ataque"],
        "Remates_centro_rival_vis": remates_vis_obj["centro_rival"],

        "Remates_media_winsor_local": remates_local_obj["ataque"]["media_winsor"],
        "Remates_mediana_local": remates_local_obj["ataque"]["mediana"],
        "Remates_p25_local": remates_local_obj["ataque"]["p25"],
        "Remates_p75_local": remates_local_obj["ataque"]["p75"],
        "Remates_std_local": remates_local_obj["ataque"]["std"],

        "Remates_media_winsor_vis": remates_vis_obj["ataque"]["media_winsor"],
        "Remates_mediana_vis": remates_vis_obj["ataque"]["mediana"],
        "Remates_p25_vis": remates_vis_obj["ataque"]["p25"],
        "Remates_p75_vis": remates_vis_obj["ataque"]["p75"],
        "Remates_std_vis": remates_vis_obj["ataque"]["std"],
        
        "shots_favor_local_blend_media": remates_local_obj["ataque"]["media"],
        "shots_favor_local_blend_media_winsor": remates_local_obj["ataque"]["media_winsor"],
        "shots_favor_local_blend_mediana": remates_local_obj["ataque"]["mediana"],
        "shots_favor_local_blend_p25": remates_local_obj["ataque"]["p25"],
        "shots_favor_local_blend_p75": remates_local_obj["ataque"]["p75"],
        "shots_favor_local_blend_std": remates_local_obj["ataque"]["std"],
        "shots_favor_local_blend_cv": remates_local_obj["ataque"]["cv"],
        "shots_favor_local_blend_centro": remates_local_obj["ataque"]["centro"],

        "shots_favor_vis_blend_media": remates_vis_obj["ataque"]["media"],
        "shots_favor_vis_blend_media_winsor": remates_vis_obj["ataque"]["media_winsor"],
        "shots_favor_vis_blend_mediana": remates_vis_obj["ataque"]["mediana"],
        "shots_favor_vis_blend_p25": remates_vis_obj["ataque"]["p25"],
        "shots_favor_vis_blend_p75": remates_vis_obj["ataque"]["p75"],
        "shots_favor_vis_blend_std": remates_vis_obj["ataque"]["std"],
        "shots_favor_vis_blend_cv": remates_vis_obj["ataque"]["cv"],
        "shots_favor_vis_blend_centro": remates_vis_obj["ataque"]["centro"],
        "liga_shots_local_fav": liga_shots_local_fav,
        "liga_shots_vis_fav": liga_shots_vis_fav,        
        "SoT_local": SoT_local,
        "SoT_vis": SoT_vis,
        
        "MuestraRematesL": racha_rem_l["muestra"],
        "MuestraRematesV": racha_rem_v["muestra"],
        "RachaSuperaRematesL": racha_rem_l["racha_actual"],
        "RachaSuperaRematesV": racha_rem_v["racha_actual"],
        "HitsSuperaRemates10L": racha_rem_l["hits_n"],
        "HitsSuperaRemates10V": racha_rem_v["hits_n"],
        "PctSuperaRemates10L": racha_rem_l["pct_n"],
        "PctSuperaRemates10V": racha_rem_v["pct_n"],
        "RachaSuperaRematesL_txt": racha_rem_l["racha_actual_txt"],
        "RachaSuperaRematesV_txt": racha_rem_v["racha_actual_txt"],
        "HitsSuperaRemates10L_txt": racha_rem_l["hits_txt"],
        "HitsSuperaRemates10V_txt": racha_rem_v["hits_txt"],
        "PctSuperaRemates10L_txt": racha_rem_l["pct_txt"],
        "PctSuperaRemates10V_txt": racha_rem_v["pct_txt"],
    }

def prob_over05_total_1t(lmbda_L1, lmbda_V1):
    lmbda = lmbda_L1 + lmbda_V1
    return (1 - poisson.pmf(0, lmbda)) * 100

def prob_over15_total_1t(lmbda_L1, lmbda_V1):
    lmbda = lmbda_L1 + lmbda_V1
    p0 = poisson.pmf(0, lmbda)
    p1 = poisson.pmf(1, lmbda)
    return (1 - p0 - p1) * 100

def prob_over05_equipo_1t(lmbda_1t):
    return (1 - poisson.pmf(0, lmbda_1t)) * 100

# === FUNCIÓN PRINCIPAL (Actualizada para usar la nueva lambda híbrida) ===
def calcular_probabilidades_equipo(df_local, df_visitante,
                                   equipo_local_archivo=None,
                                   equipo_visitante_archivo=None):
    if df_local.empty or df_visitante.empty:
        return None

    # 1) Lambdas totales 90'
    lambda_local = calcular_lambda_hibrida(df_local, "goles_local", "xg_favor")
    lambda_visitante = calcular_lambda_hibrida(df_visitante, "goles_visitante", "xg_favor")

    # 2) Factor de liga para repartir 1T / 2T
    pais_local = pais_de_equipo(equipo_local_archivo) if equipo_local_archivo else None
    media_1t_liga = media_goles_1t_liga(pais_local, n_partidos_max=38) if pais_local else None

    if media_1t_liga is not None:
        media_total_liga = 2.6  # luego puedes calibrar por país
        f_1t = media_1t_liga / media_total_liga
        f_1t = max(0.35, min(f_1t, 0.50))
    else:
        f_1t = 0.44
    f_2t = 1 - f_1t

    # 3) Lambdas por mitad (derivados del total)
    lambda_local_1t = lambda_local * f_1t
    lambda_visitante_1t = lambda_visitante * f_1t
    lambda_local_2t = lambda_local * f_2t
    lambda_visitante_2t = lambda_visitante * f_2t

    # 4) Probabilidades de resultado 90'
    prob_resultados = calcular_probabilidades_resultado(lambda_local, lambda_visitante)

    # 5) Datos de forma últimos 5
    df_local_5 = df_local.head(5)
    df_visitante_5 = df_visitante.head(5)

    resultados = {
        # Goles 90'
        "Prob. Local marca": probabilidad_poisson(lambda_local) * 100,
        "Prob. Visitante marca": probabilidad_poisson(lambda_visitante) * 100,
        "Prob. BTTS": round(
            probabilidad_poisson(lambda_local) * probabilidad_poisson(lambda_visitante), 3
        ) * 100,

        # 1T total
        "Prob. Gol 1T total": prob_over05_total_1t(lambda_local_1t, lambda_visitante_1t),
        "Prob. Gol 1T over 1.5": prob_over15_total_1t(lambda_local_1t, lambda_visitante_1t),

        # 1T por equipo (over 0.5)
        "Prob. Local 1T": prob_over05_equipo_1t(lambda_local_1t),
        "Prob. Visitante 1T": prob_over05_equipo_1t(lambda_visitante_1t),

        # 2T (simétrico si quieres usarlo)
        "Prob. Gol 2T total": prob_over05_total_1t(lambda_local_2t, lambda_visitante_2t),
        "Prob. Local 2T": prob_over05_equipo_1t(lambda_local_2t),
        "Prob. Visitante 2T": prob_over05_equipo_1t(lambda_visitante_2t),

        # Remates / SoT (igual que antes)
        "Prom. Remates Local": round(metricas_avanzadas["Remates_att_local"], 1),
        "Prom. Remates Visitante": round(metricas_avanzadas["Remates_att_vis"], 1),
        "Total Remates": round(
            metricas_avanzadas["Remates_att_local"] + metricas_avanzadas["Remates_att_vis"], 1
        ),
        
        "Rango Remates Local": f"{metricas_avanzadas['Remates_rango_local_low']:.1f} - {metricas_avanzadas['Remates_rango_local_high']:.1f}",
        "Rango Remates Visitante": f"{metricas_avanzadas['Remates_rango_vis_low']:.1f} - {metricas_avanzadas['Remates_rango_vis_high']:.1f}",
        "Confianza Remates Local": metricas_avanzadas["Remates_confianza_local"],
        "Confianza Remates Visitante": metricas_avanzadas["Remates_confianza_vis"],
        "CV Remates Local": round(metricas_avanzadas["Remates_cv_local"], 3),
        "CV Remates Visitante": round(metricas_avanzadas["Remates_cv_vis"], 3),
        
        "A puerta Local": round(metricas_avanzadas["SoT_local"], 1),
        "A puerta Visitante": round(metricas_avanzadas["SoT_vis"], 1),
        "Total A puerta": round(
            metricas_avanzadas["SoT_local"] + metricas_avanzadas["SoT_vis"], 1
        ),

        # Overs totales 90'
        "Prob. Over 1.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 1.5),
        "Prob. Over 2.5 Goles": probabilidad_over_total(lambda_local, lambda_visitante, 2.5),

        # Overs por equipo 90'
        "Prob. Local Over 1.5 Goles": calcular_probabilidad_over_equipo(lambda_local, 1.5),
        "Prob. Visitante Over 1.5 Goles": calcular_probabilidad_over_equipo(lambda_visitante, 1.5),

        # Probabilidades de resultado 1X2
        **prob_resultados,

        # Guardar lambdas 1T para las tablas avanzadas
        "lambda_local_1t": lambda_local_1t,
        "lambda_visitante_1t": lambda_visitante_1t,
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
        
def color_racha(valor, tipo="actual"):
    try:
        v = int(float(str(valor).replace("%", "").split(" ")[0]))
    except Exception:
        return ""

    if v <= 0:
        return "background-color: #eceff1; color: #37474f;"
    elif v <= 2:
        return "background-color: #ffe0b2; color: #5d4037;"
    elif v <= 5:
        return "background-color: #c8e6c9; color: #1b5e20;"
    else:
        if tipo == "max":
            return "background-color: #bbdefb; color: #0d47a1; font-weight: 600;"
        return "background-color: #81c784; color: #ffffff; font-weight: 600;"


def resaltar_rachas(df, columnas_actual=None, columnas_max=None, col_prob=None, col_extra=None, umbrales=(80, 75)):
    columnas_actual = columnas_actual or []
    columnas_max = columnas_max or []

    df_fmt = df.reset_index(drop=True).copy()

    if "Línea" in df_fmt.columns:
        df_fmt["Línea"] = pd.to_numeric(df_fmt["Línea"], errors="coerce").round(1)

    # Normalizar col_prob y col_extra a listas
    cols_prob = col_prob if isinstance(col_prob, list) else [col_prob] if col_prob else []
    cols_extra = col_extra if isinstance(col_extra, list) else [col_extra] if col_extra else []

    for c in cols_prob + cols_extra:
        if c and c in df_fmt.columns:
            df_fmt[c] = pd.to_numeric(df_fmt[c], errors="coerce").round(1)

    def _style(row):
        estilos = [""] * len(row)
        for col in columnas_actual:
            if col in df_fmt.columns:
                idx = df_fmt.columns.get_loc(col)
                estilos[idx] = color_racha(row[col], tipo="actual")
        for col in columnas_max:
            if col in df_fmt.columns:
                idx = df_fmt.columns.get_loc(col)
                estilos[idx] = color_racha(row[col], tipo="max")
        return estilos

    styler = df_fmt.style.apply(_style, axis=1)

    if any(c and c in df_fmt.columns for c in cols_prob):
        umbral_verde, umbral_azul = umbrales

        def _color_prob(v):
            try:
                x = float(v)
            except Exception:
                x = 0.0
            if x >= umbral_verde:
                return "background-color: #68f78b;"
            elif x >= umbral_azul:
                return "background-color: #bbdefb;"
            return ""

        for col in cols_prob:
            if col and col in df_fmt.columns:
                styler = styler.map(_color_prob, subset=[col])
        for col in cols_extra:
            if col and col in df_fmt.columns:
                styler = styler.map(_color_prob, subset=[col])

    return styler.format({
        "Línea": "{:.1f}",
        **{col: "{:.1f}" for col in cols_prob + cols_extra if col and col in df_fmt.columns}
    })   
    
def formatear_historico_con_muestra(hist):
    n = int(hist.get("muestra", 0))

    if n <= 0:
        return "Sin datos"

    hits = int(hist.get("hits_n", 0))
    pct = float(hist.get("pct_n", 0.0))

    return f"{pct:.1f}% ({hits}/{n})"      

# === TABLAS AVANZADAS BASADAS EN NUEVOS LAMBDAS ===
def mostrar_tablas_avanzadas(metricas, lambda1_L, lambda1_V, df_local, df_visitante,
                             equipo_local_archivo=None, equipo_visitante_archivo=None):
    
    if metricas is None:
        return
    
    factores_contexto = {
        "remates_local": 1.0,
        "remates_visitante": 1.0,
        "sot_local": 1.0,
        "sot_visitante": 1.0,
    }

    estado_contexto_remates = (
        "Sin contexto: faltan identificadores de equipos."
    )
    
    auditoria_contexto = []

    if equipo_local_archivo and equipo_visitante_archivo:
        factores_contexto, estado_contexto_remates = (
            preparar_contexto_remates_sot(
                equipo_local=equipo_local_archivo,
                equipo_visitante=equipo_visitante_archivo,
                mapa_equipos=mapa_equipos,
                n_partidos=10,
                fuerza=0.50,
                auditoria=auditoria_contexto,
                aplicar_shrinkage=False,
                k_contexto=6.0,
            )
        )  

    lambda_L = metricas["lambda_local_new"]
    lambda_V = metricas["lambda_vis_new"]
    
    col1, col2, col3, col8 = st.columns(4)

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
        st.table(formatear_y_resaltar(df_res, "Probabilidad %", (80, 60)))

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
        st.table(formatear_y_resaltar(df_tot, "Prob. Over %", (76, 70), col_extra = "Prob. Under %"))

    # Tabla 3: Goles por equipo y BTTS
    with col3:
        st.subheader("Goles por Equipo y BTTS")

        lineas_equipo = [0.5, 1.5]
        rows_eq = []

        for L in lineas_equipo:
            # Over
            uL, oL = poisson_prob_over_under(lambda_L, L, max_k=8)
            uV, oV = poisson_prob_over_under(lambda_V, L, max_k=8)

            rows_eq.append([
                f"Local marca +{L}", oL,
                f"Local Under {L}", uL
            ])

            rows_eq.append([
                f"Visitante marca +{L}", oV,
                f"Visitante Under {L}", uV
            ])

        # BTTS
        btts = prob_btts(lambda_L, lambda_V, max_goals=8)
        no_btts = 100 - btts

        rows_eq.append([
            "BTTS", btts,
            "NO BTTS", no_btts
        ])

        df_eq = pd.DataFrame(
            rows_eq,
            columns=[
                "Métrica / Over",
                "Prob. Over %",
                "Métrica / Under",
                "Prob. Under %"
            ]
        )

        st.table(
            formatear_y_resaltar(
                df_eq,
                "Prob. Over %",
                (74, 70),
                col_extra="Prob. Under %"
            )
        )
        
    with col8:
        st.subheader("Goles en el 1T")
        lineas_1T = [0.5, 1.5]
        rows_1T = []
        for L in lineas_1T:
            u, o = poisson_prob_total_over_under(lambda1_L, lambda1_V, L, max_k=5)
            rows_1T.append([f"+{L} goles 1T", o, f"-{L} goles 1T", u])

        uL05, oL05 = poisson_prob_over_under(lambda1_L, 0.5, max_k=5)
        uV05, oV05 = poisson_prob_over_under(lambda1_V, 0.5, max_k=5)

        rows_1T.extend([
            ["Local marca 0.5+ 1T", oL05, "Local Under 0.5 1T", uL05],
            ["Visita marca 0.5+ 1T", oV05, "Visita Under 0.5 1T", uV05],
        ])

        df_1T = pd.DataFrame(
            rows_1T,
            columns=["Métrica / Over 1T", "Prob. Over %", "Métrica / Under 1T", "Prob. Under %"]
        )
        st.table(formatear_y_resaltar(df_1T, "Prob. Over %", (76.8, 73), col_extra="Prob. Under %")) 

    # === Tabla 4 y 5 en la misma fila ===
    col4, col5 = st.columns(2)
    
    with col4:
        st.subheader("Remates Totales en el Partido")

        lambda_shots_total = (
            metricas["Remates_att_local"]
            + metricas["Remates_att_vis"]
        )

        lineas_shots_total = [
            18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5,
            25.5, 26.5, 27.5, 28.5, 29.5, 30.5, 31.5,
        ]

        rows_shots_tot = []
            
        for L in lineas_shots_total:
            hist_local = calcular_racha_supera_linea_total_partido(
                df_local, "shots_favor", "shots_contra", L, n=10, incluir_igual=False
            )
            hist_vis = calcular_racha_supera_linea_total_partido(
                df_visitante, "shots_favor", "shots_contra", L, n=10, incluir_igual=False
            )

            lambda_rem_total = metricas["Remates_att_local"] + metricas["Remates_att_vis"]
            cv_rem_local = metricas["Remates_cv_local"]
            cv_rem_vis = metricas["Remates_cv_vis"]
            cv_mix = 0.6 * cv_rem_local + 0.4 * cv_rem_vis
            factor_vol = max(0.85, min(1.15, 1 - 0.3 * cv_mix))
            lambda_ajustado = lambda_rem_total * factor_vol
            
            n_rem_local = min(len(df_local), 10)
            n_rem_vis = min(len(df_visitante), 10)
            penalizacion_muestra = 0.0
            if n_rem_local < 10:
                penalizacion_muestra += (10 - n_rem_local) * 0.005
            if n_rem_vis < 10:
                penalizacion_muestra += (10 - n_rem_vis) * 0.003
            penalizacion_muestra = min(0.15, penalizacion_muestra)
            
            from math import floor
            k_linea = int(floor(L))
            p_over = 1 - poisson.cdf(k_linea, lambda_ajustado)
            p_over = max(0.0, min(1.0, p_over - penalizacion_muestra))
            prob_base = round(p_over * 100, 1)
            lambda_total_contexto = (
                metricas["Remates_att_local"]
                * factores_contexto["remates_local"]
                + metricas["Remates_att_vis"]
                * factores_contexto["remates_visitante"]
            )

            lambda_proyeccion_contexto = (
                lambda_total_contexto * factor_vol
            )

            p_over_contexto = poisson.sf(
                k_linea,
                lambda_proyeccion_contexto
            )

            p_over_contexto = max(
                0.0,
                min(1.0, p_over_contexto - penalizacion_muestra)
            )

            prob_base_contexto = round(
                p_over_contexto * 100, 1
            )

            score_local = calcular_score_regularidad(
                hist_local["pct_n"],
                hist_local["racha_actual"],
                hist_local["racha_max"],
            )
            score_vis = calcular_score_regularidad(
                hist_vis["pct_n"],
                hist_vis["racha_actual"],
                hist_vis["racha_max"],
            )
            score_combinado = 0.5 * score_local + 0.5 * score_vis

            n_mix = min(n_rem_local, n_rem_vis)
            
            proyeccion = ajustar_prob_por_regularidad(
                prob_base_contexto,
                score_combinado,
                cv_mix,
                n_mix,
            )

            under = round(100 - prob_base, 1)

            rows_shots_tot.append([
                L,
                prob_base,  
                under,
                hist_local["pct_txt"],
                hist_local["racha_actual_txt"],
                hist_local["racha_max_txt"],
                hist_vis["pct_txt"],
                hist_vis["racha_actual_txt"],
                hist_vis["racha_max_txt"],
                proyeccion,  
            ])
    

        df_shots_tot = pd.DataFrame(
            rows_shots_tot,
            columns=[
                "Línea", "Over %", "Under %", 
                "Local %", "Local Racha", "Local Máx",
                "Visitante %", "Visitante Racha", "Visitante Máx", "Proyección %"
            ],
        )

        st.table(
            resaltar_rachas(
                df_shots_tot,
                columnas_actual=["Local Racha", "Visitante Racha"],
                columnas_max=["Local Máx", "Visitante Máx"],
                col_prob=["Over %", "Proyección %"],
                col_extra="Under %",
                umbrales=(70, 60),
            )
        )
        
    controles_poisson = []

    # Tabla 5: Remates por equipo
    with col5:
        st.subheader("Remates por Equipo")
        lineas_shots_eq = [
            7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5,
            15.5, 16.5, 17.5, 18.5, 19.5, 20.5
        ]
        rows_shots_eq = []

        for L in lineas_shots_eq:
            _, oL = poisson_prob_over_under(metricas["Remates_att_local"], L, max_k=25)
            _, oV = poisson_prob_over_under(metricas["Remates_att_vis"], L, max_k=25)
            
            if L == 12.5:
                for lado, clave, obtenido in [
                    ("Local", "Remates_att_local", oL),
                    ("Visitante", "Remates_att_vis", oV),
                ]:
                    lambda_usado = float(metricas[clave])

                    prob_directa = float(
                        poisson.sf(
                            int(np.floor(L)),
                            lambda_usado,
                        ) * 100
                    )

                    controles_poisson.append({
                        "Mercado": "Remates",
                        "Lado": lado,
                        "Línea": L,
                        "Lambda recibido": lambda_usado,
                        "Prob. función %": float(obtenido),
                        "Prob. directa %": prob_directa,
                        "Diferencia pp":
                            float(obtenido) - prob_directa,
                    })

            hist_local = calcular_racha_supera_linea(df_local, "shots_favor", L, n=10, incluir_igual=False)
            hist_vis_concede = calcular_racha_concede_linea(df_visitante, "shots_contra", L, n=10, incluir_igual=False)
            
            hist_vis = calcular_racha_supera_linea(df_visitante, "shots_favor", L, n=10, incluir_igual=False)
            hist_local_concede = calcular_racha_concede_linea(df_local, "shots_contra", L, n=10, incluir_igual=False)

            proyeccion_local = calcular_proyeccion_individual(
                proy_equipo=metricas["Remates_att_local"],
                proy_rival=metricas["Remates_contra_vis"],
                linea=L,
                cv_equipo=metricas["Remates_cv_local"],
                cv_rival=metricas["Remates_cv_vis"],
                n_equipo=min(len(df_local), 10),
                n_rival=min(len(df_visitante), 10),
                peso_equipo=0.60,
                peso_rival=0.40,
                pct_historico_equipo=hist_local["pct_n"],
                racha_actual_equipo=hist_local["racha_actual"],
                racha_max_equipo=hist_local["racha_max"],
                pct_historico_rival=hist_vis_concede["pct_n"],
                racha_actual_rival=hist_vis_concede["racha_actual"],
                racha_max_rival=hist_vis_concede["racha_max"],
                factor_contexto=factores_contexto["remates_local"],
            )

            
            proyeccion_vis = calcular_proyeccion_individual(
                proy_equipo=metricas["Remates_att_vis"],
                proy_rival=metricas["Remates_contra_local"],
                linea=L,
                cv_equipo=metricas["Remates_cv_vis"],
                cv_rival=metricas["Remates_cv_local"],
                n_equipo=min(len(df_visitante), 10),
                n_rival=min(len(df_local), 10),
                peso_equipo=0.60,
                peso_rival=0.40,
                pct_historico_equipo=hist_vis["pct_n"],
                racha_actual_equipo=hist_vis["racha_actual"],
                racha_max_equipo=hist_vis["racha_max"],
                pct_historico_rival=hist_local_concede["pct_n"],
                racha_actual_rival=hist_local_concede["racha_actual"],
                racha_max_rival=hist_local_concede["racha_max"],
                factor_contexto=factores_contexto["remates_visitante"],
            )
                        
            rows_shots_eq.append([
                f"+{L} Remates",
                oL,
                formatear_historico_con_muestra(hist_local),
                formatear_historico_con_muestra(hist_vis_concede),
                hist_local["racha_actual_txt"],
                hist_local["racha_max_txt"],
                proyeccion_local,
                oV,
                formatear_historico_con_muestra(hist_vis),
                formatear_historico_con_muestra(hist_local_concede),
                hist_vis["racha_actual_txt"],
                hist_vis["racha_max_txt"],
                proyeccion_vis,
            ])

        df_shots_eq = pd.DataFrame(
            rows_shots_eq,
            columns=[
                "Remates",
                "Prob. Local %", "Hist. Local %", "Hist. Vis concede %", "Racha Local", "Máx Local", "Proy Local", 
                "Prob. Visitante %", "Hist. Visitante %", "Hist. Local concede %", "Racha Visitante", "Máx Visitante", "Proy Vis",
            ]
        )

        st.table(
            resaltar_rachas(
                df_shots_eq,
                columnas_actual=["Racha Local", "Racha Visitante"],
                columnas_max=["Máx Local", "Máx Visitante"],
                col_prob=["Prob. Local %", "Proy Local"],
                col_extra=["Prob. Visitante %", "Proy Vis"],
                umbrales=(70, 60)
            )
        )   

    # === Tabla 6 y 7 en la misma fila ===
    col6, col7 = st.columns(2)
    
    # Tabla 6: Tiros a puerta totales
    with col6:
        st.subheader("Tiros a Puerta Totales")
        lambda_sot_total = metricas["SoT_local"] + metricas["SoT_vis"]
        lineas_sot_total = [5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]
        rows_sot_tot = []

        for L in lineas_sot_total:
            hist_local = calcular_racha_supera_linea_total_partido(
                df_local, "a_puerta_favor", "a_puerta_contra", L, n=10, incluir_igual=False
            )
            hist_vis = calcular_racha_supera_linea_total_partido(
                df_visitante, "a_puerta_favor", "a_puerta_contra", L, n=10, incluir_igual=False
            )

            lambda_sot_total = metricas["SoT_local"] + metricas["SoT_vis"]
            cv_sot_local = metricas.get("Remates_cv_local", 0.3)
            cv_sot_vis = metricas.get("Remates_cv_vis", 0.3)
            cv_mix = 0.6 * cv_sot_local + 0.4 * cv_sot_vis
            factor_vol = max(0.85, min(1.15, 1 - 0.3 * cv_mix))
            lambda_ajustado = lambda_sot_total * factor_vol
            
            n_sot_local = min(len(df_local), 10)
            n_sot_vis = min(len(df_visitante), 10)
            penalizacion_muestra = 0.0
            if n_sot_local < 10:
                penalizacion_muestra += (10 - n_sot_local) * 0.005
            if n_sot_vis < 10:
                penalizacion_muestra += (10 - n_sot_vis) * 0.003
            penalizacion_muestra = min(0.15, penalizacion_muestra)
            
            from math import floor
            k_linea = int(floor(L))
            p_over = 1 - poisson.cdf(k_linea, lambda_ajustado)
            p_over = max(0.0, min(1.0, p_over - penalizacion_muestra))
            prob_base = round(p_over * 100, 1)
            
            lambda_total_contexto = (
                metricas["SoT_local"]
                * factores_contexto["sot_local"]
                + metricas["SoT_vis"]
                * factores_contexto["sot_visitante"]
            )

            lambda_proyeccion_contexto = (
                lambda_total_contexto * factor_vol
            )

            p_over_contexto = poisson.sf(
                k_linea,
                lambda_proyeccion_contexto
            )

            p_over_contexto = max(
                0.0,
                min(1.0, p_over_contexto - penalizacion_muestra)
            )

            prob_base_contexto = round(
                p_over_contexto * 100, 1
            )

            score_local = calcular_score_regularidad(
                hist_local["pct_n"],
                hist_local["racha_actual"],
                hist_local["racha_max"],
            )
            score_vis = calcular_score_regularidad(
                hist_vis["pct_n"],
                hist_vis["racha_actual"],
                hist_vis["racha_max"],
            )
            score_combinado = 0.5 * score_local + 0.5 * score_vis

            n_mix = min(n_sot_local, n_sot_vis)
            proyeccion = ajustar_prob_por_regularidad(
                prob_base_contexto,
                score_combinado,
                cv_mix,
                n_mix,
            )

            under = round(100 - prob_base, 1)

            rows_sot_tot.append([
                L,
                prob_base,  
                under,
                hist_local["pct_txt"],
                hist_local["racha_actual_txt"],
                hist_local["racha_max_txt"],
                hist_vis["pct_txt"],
                hist_vis["racha_actual_txt"],
                hist_vis["racha_max_txt"],
                proyeccion, 
            ])

        df_sot_tot = pd.DataFrame(
            rows_sot_tot,
            columns=[
                "Línea", "Over %", "Under %",
                "Local %", "Local Racha", "Local Máx",
                "Visitante %", "Visitante Racha", "Visitante Máx", "Proyección %"
            ]
        )

        st.table(
            resaltar_rachas(
                df_sot_tot,
                columnas_actual=["Local Racha", "Visitante Racha"],
                columnas_max=["Local Máx", "Visitante Máx"],
                col_prob=["Over %", "Proyección %"],
                col_extra="Under %",
                umbrales=(70, 60)
            )
        )

    # === Tabla 7: Tiros a puerta por equipo (1 por fila o en dos columnas) ===
    with col7:
        st.subheader("Tiros a Puerta por Equipo")
        lineas_sot_eq = [2.5, 3.5, 4.5, 5.5, 6.5, 7.5]
        rows_sot_eq = []
        sot_concede_local = pd.to_numeric(
            df_local["a_puerta_contra"].tail(10),
            errors="coerce"
        ).dropna().mean()

        sot_concede_vis = pd.to_numeric(
            df_visitante["a_puerta_contra"].tail(10),
            errors="coerce"
        ).dropna().mean()

        concesion_local_valida = (
            pd.notna(sot_concede_local)
            and np.isfinite(sot_concede_local)
            and sot_concede_local >= 0
        )

        concesion_vis_valida = (
            pd.notna(sot_concede_vis)
            and np.isfinite(sot_concede_vis)
            and sot_concede_vis >= 0
        )
        
        for L in lineas_sot_eq:
            _, oL = poisson_prob_over_under(metricas["SoT_local"], L, max_k=10)
            _, oV = poisson_prob_over_under(metricas["SoT_vis"], L, max_k=10)
            
            if L == 3.5:
                for lado, clave, obtenido in [
                    ("Local", "SoT_local", oL),
                    ("Visitante", "SoT_vis", oV),
                ]:
                    lambda_usado = float(metricas[clave])

                    prob_directa = float(
                        poisson.sf(
                            int(np.floor(L)),
                            lambda_usado,
                        ) * 100
                    )

                    controles_poisson.append({
                        "Mercado": "Tiros a puerta",
                        "Lado": lado,
                        "Línea": L,
                        "Lambda recibido": lambda_usado,
                        "Prob. función %": float(obtenido),
                        "Prob. directa %": prob_directa,
                        "Diferencia pp":
                            float(obtenido) - prob_directa,
                    })

            hist_local = calcular_racha_supera_linea(df_local, "a_puerta_favor", L, n=10, incluir_igual=False)
            hist_vis_concede = calcular_racha_concede_linea(df_visitante, "a_puerta_contra", L, n=10, incluir_igual=False)
            
            hist_vis = calcular_racha_supera_linea(df_visitante, "a_puerta_favor", L, n=10, incluir_igual=False)
            hist_local_concede = calcular_racha_concede_linea(df_local, "a_puerta_contra", L, n=10, incluir_igual=False)

            proyeccion_local = calcular_proyeccion_individual_sot(
                sot_equipo=metricas["SoT_local"],
                sot_rival=(float(sot_concede_vis)if concesion_vis_valida else metricas["SoT_vis"]),
                linea=L,
                cv_equipo=metricas.get("Remates_cv_local", 0.3),
                cv_rival=metricas.get("Remates_cv_vis", 0.3),
                n_equipo=min(len(df_local), 10),
                n_rival=min(len(df_visitante), 10),
                peso_equipo=0.60,
                peso_rival=0.40,
                pct_historico_equipo=hist_local["pct_n"],
                racha_actual_equipo=hist_local["racha_actual"],
                racha_max_equipo=hist_local["racha_max"],
                pct_historico_rival=hist_vis_concede["pct_n"],
                racha_actual_rival=hist_vis_concede["racha_actual"],
                racha_max_rival=hist_vis_concede["racha_max"],
                factor_contexto=factores_contexto["sot_local"],
            )
            
            proyeccion_vis = calcular_proyeccion_individual_sot(
                sot_equipo=metricas["SoT_vis"],
                sot_rival=(float(sot_concede_local) if concesion_local_valida else metricas["SoT_local"]),
                linea=L,
                cv_equipo=metricas.get("Remates_cv_vis", 0.3),
                cv_rival=metricas.get("Remates_cv_local", 0.3),
                n_equipo=min(len(df_visitante), 10),
                n_rival=min(len(df_local), 10),
                peso_equipo=0.60,
                peso_rival=0.40,
                pct_historico_equipo=hist_vis["pct_n"],
                racha_actual_equipo=hist_vis["racha_actual"],
                racha_max_equipo=hist_vis["racha_max"],
                pct_historico_rival=hist_local_concede["pct_n"],
                racha_actual_rival=hist_local_concede["racha_actual"],
                racha_max_rival=hist_local_concede["racha_max"],
                factor_contexto=factores_contexto["sot_visitante"],
            )

            rows_sot_eq.append([
                f"+{L} Tiros a puerta",
                oL,
                formatear_historico_con_muestra(hist_local),
                formatear_historico_con_muestra(hist_vis_concede),
                hist_local["racha_actual_txt"],
                hist_local["racha_max_txt"],
                proyeccion_local,
                oV,
                formatear_historico_con_muestra(hist_vis),
                formatear_historico_con_muestra(hist_local_concede),
                hist_vis["racha_actual_txt"],
                hist_vis["racha_max_txt"],
                proyeccion_vis,
            ])

        df_sot_eq = pd.DataFrame(
            rows_sot_eq,
            columns=[
                "Tiros a puerta",
                "Prob. Local %", "Hist. Local %", "Hist. Vis Concede", "Racha Local", "Máx Local", "Proy Local", 
                "Prob. Visitante %", "Hist. Visitante %", "Hist. Local Concede", "Racha Visitante", "Máx Visitante", "Proy Vis",
            ]
        )

        st.table(
            resaltar_rachas(
                df_sot_eq,
                columnas_actual=["Racha Local", "Racha Visitante"],
                columnas_max=["Máx Local", "Máx Visitante"],
                col_prob=["Prob. Local %", "Proy Local"],
                col_extra=["Prob. Visitante %", "Proy Vis"],
                umbrales=(70, 60)
            )
        )
        
        st.caption(estado_contexto_remates)
        with st.expander("Diagnóstico: volúmenes utilizados"):
            st.dataframe(
                pd.DataFrame([
                    {
                        "Equipo": "Local",
                        "Remates ataque modelo":
                            metricas["Remates_att_local"],
                        "Remates concesión modelo":
                            metricas["Remates_contra_local"],
                        "Tiros a puerta ataque modelo":
                            metricas["SoT_local"],
                    },
                    {
                        "Equipo": "Visitante",
                        "Remates ataque modelo":
                            metricas["Remates_att_vis"],
                        "Remates concesión modelo":
                            metricas["Remates_contra_vis"],
                        "Tiros a puerta ataque modelo":
                            metricas["SoT_vis"],
                    },
                ]),
                hide_index=True,
                use_container_width=True,
            )
        with st.expander("Control: lambda y probabilidad"):
            df_control_poisson = pd.DataFrame(
                controles_poisson
            )

            st.dataframe(
                df_control_poisson.style.format({
                    "Línea": "{:.1f}",
                    "Lambda recibido": "{:.4f}",
                    "Prob. función %": "{:.4f}",
                    "Prob. directa %": "{:.4f}",
                    "Diferencia pp": "{:.6f}",
                }),
                hide_index=True,
                use_container_width=True,
            )

            import inspect

            funcion_activa = inspect.unwrap(
                poisson_prob_over_under
            )

            try:
                st.caption(
                    "Función activa: "
                    f"{inspect.getsourcefile(funcion_activa)}"
                    " | Línea: "
                    f"{inspect.getsourcelines(funcion_activa)[1]}"
                )

                st.code(
                    inspect.getsource(funcion_activa),
                    language="python",
                )

            except (OSError, TypeError):
                st.caption(
                    "No se pudo recuperar el código fuente "
                    "de la función activa."
                )
        if auditoria_contexto:
            with st.expander(
                "🔎 Auditoría del contexto: remates y tiros a puerta"
            ):
                df_auditoria_contexto = pd.DataFrame(
                    auditoria_contexto
                )

                formatos = {
                    "Media ataque": "{:.2f}",
                    "Media concede rival": "{:.2f}",
                    "Percentil ataque": "{:.1f}",
                    "Percentil concede": "{:.1f}",
                    "Factor perfil": "{:.3f}",
                    "Factor sin shrinkage": "{:.3f}",
                    "Peso muestra": "{:.3f}",
                    "Factor con shrinkage": "{:.3f}",
                    "Factor aplicado": "{:.3f}",
                }

                st.dataframe(
                    df_auditoria_contexto.style.format(
                        formatos,
                        na_rep="—",
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    "El peso por muestra modera el factor hacia 1. "
                    "No es una probabilidad de acierto. "
                    "La comparación de factores no recalcula por sí "
                    "sola una segunda columna de proyección."
                )
        
def prob_a_texto_con_cuota(p):
    try:
        p_float = float(p)
    except Exception:
        return p
    if p_float <= 0:
        return "0.0% (0.00)"
    cuota = 100 / p_float
    return f"{p_float:.1f}%   ({cuota:.2f})"

    
def formatear_y_resaltar(df, col_prob, umbrales, col_extra=None):
    umbral_verde, umbral_azul = umbrales
    df_fmt = df.reset_index(drop=True).copy()
    
    if "Métrica" in df.columns:
        primera_metrica = df["Métrica"].iloc[0].lower()
        
        if "marca" in primera_metrica:
            umbral_verde, umbral_azul = 70, 60
        elif "btts" in primera_metrica:
            umbral_verde, umbral_azul = 65, 55
        elif "over 1.5" in primera_metrica:
            umbral_verde, umbral_azul = 70, 60
        elif "over 2.5" in primera_metrica:
            umbral_verde, umbral_azul = 65, 55

    # Línea numérica
    if "Línea" in df_fmt.columns and pd.api.types.is_numeric_dtype(df_fmt["Línea"]):
        df_fmt["Línea"] = df_fmt["Línea"].astype(float).round(1)

    # Guardar columnas numéricas para colorear
    cols_prob_numericas = []
    for col in [col_prob, col_extra]:
        if col and col in df_fmt.columns:
            df_fmt[col] = df_fmt[col].astype(float).round(1)
            cols_prob_numericas.append(col)

    def _color_col(col):
        styles = []
        for val in col:
            try:
                v = float(val)
            except Exception:
                v = 0.0
            if v >= umbral_verde:
                styles.append("background-color: #68f78b")  
            elif v >= umbral_azul:
                styles.append("background-color: #bbdefb") 
            else:
                styles.append("")
        return styles

    def _style_metric_col(col):
        return ["background-color: #fff3e0" for _ in col]
    
    styler = df_fmt.style.hide(axis="index")   

    styler = styler.set_table_styles([
        {
            "selector": "th.col_heading",
            "props": "background-color: #e0e0e0; font-weight: bold;"
        }
    ])

    metric_cols = [
        c for c in df_fmt.columns
        if c not in ["Línea", col_prob, col_extra]
    ]

    
    styler = styler.apply(
        _style_metric_col,
        subset=metric_cols,
        axis=0
    )

    for col in cols_prob_numericas:
        styler = styler.apply(_color_col, subset=[col], axis=0)

    # Formatos: Línea sólo número; probabilidades con % + cuota
    fmt_dict = {}
    if "Línea" in df_fmt.columns:
        fmt_dict["Línea"] = "{:.1f}"

    for col in cols_prob_numericas:
        fmt_dict[col] = prob_a_texto_con_cuota

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
    
@st.cache_data
def media_xg_liga(pais: str, npartidosmax: int = None):
    try:
        df_equipos = pd.read_excel(RUTA_EQUIPOS_LIGAS)
    except Exception:
        return None

    df_equipos.columns = df_equipos.columns.str.strip().str.lower()

    if "equipo" not in df_equipos.columns or "pais" not in df_equipos.columns:
        return None

    df_pais = df_equipos[
        df_equipos["pais"].str.lower() == pais.lower()
    ]    

    if df_pais.empty:
        return None
    
    suma_xg_favor_local = 0.0
    suma_xg_contra_local = 0.0
    suma_xg_favor_visita = 0.0
    suma_xg_contra_visita = 0.0
    partidos_local = 0
    partidos_visita = 0
        
    for _, fila_equipo in df_pais.iterrows():
        equipo_archivo = str(fila_equipo["equipo"]).strip()
        division = str(fila_equipo["division"]).strip()

        nombre_archivo = (
            f"{equipo_archivo}_{division}"
            .replace(" ", "_")
            .lower()
            + ".xlsx"
        )

        ruta = os.path.join(RUTA_STATS, nombre_archivo)

        if not os.path.exists(ruta):
            continue

        try:
            df = pd.read_excel(ruta)
        except Exception:
            continue

        df = normalizar_columnas(df)        

        columnas_necesarias = {
            "xg_favor",
            "xg_contra",
            "equipo_local",
            "visitante",
        }
        
        if not columnas_necesarias.issubset(df.columns):
            continue

        nombre_normalizado = mapa_equipos.get(
            equipo_archivo,
            equipo_archivo.replace("-", " ").lower(),
        ).lower()

        es_local = (
            df["equipo_local"]
            .str.lower()
            .str.contains(nombre_normalizado, na=False)
        )

        es_visitante = (
            df["visitante"]
            .str.lower()
            .str.contains(nombre_normalizado, na=False)
        )

        df_local = df[es_local]
        df_visitante = df[es_visitante]

        if npartidosmax is not None:
            df_local = df_local.tail(npartidosmax)
            df_visitante = df_visitante.tail(npartidosmax)

        suma_xg_favor_local += pd.to_numeric(
            df_local["xg_favor"], errors="coerce"
        ).fillna(0).sum()

        suma_xg_contra_local += pd.to_numeric(
            df_local["xg_contra"], errors="coerce"
        ).fillna(0).sum()

        suma_xg_favor_visita += pd.to_numeric(
            df_visitante["xg_favor"], errors="coerce"
        ).fillna(0).sum()

        suma_xg_contra_visita += pd.to_numeric(
            df_visitante["xg_contra"], errors="coerce"
        ).fillna(0).sum()

        partidos_local += len(df_local)
        partidos_visita += len(df_visitante)

    if partidos_local == 0 or partidos_visita == 0:
        return None

    xg_favor_local = suma_xg_favor_local / partidos_local
    xg_contra_local = suma_xg_contra_local / partidos_local
    xg_favor_visita = suma_xg_favor_visita / partidos_visita
    xg_contra_visita = suma_xg_contra_visita / partidos_visita

    return {
        "xg_favor_local": xg_favor_local,
        "xg_contra_local": xg_contra_local,
        "xg_favor_visita": xg_favor_visita,
        "xg_contra_visita": xg_contra_visita,
        "total_liga": xg_favor_local + xg_contra_local,
    }

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
    
    def calcular_racha_maxima_booleana(cond):
        if cond is None:
            return 0
        racha_maxima = 0
        racha_actual = 0
        for valor in pd.Series(cond).fillna(False).astype(bool):
            if valor:
                racha_actual += 1
                racha_maxima = max(racha_maxima, racha_actual)
            else:
                racha_actual = 0
        return racha_maxima


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
    
    # Nuevas métricas de gol
    marca_gol_cond = df_calculo[goles_a_favor_col] >= 1
    recibe_gol_cond = df_calculo[goles_en_contra_col] >= 1
    no_marca_gol_cond = df_calculo[goles_a_favor_col] == 0
    no_recibe_gol_cond = df_calculo[goles_en_contra_col] == 0

    racha_marca_gol = calcular_racha_booleana(df_calculo, marca_gol_cond)
    racha_recibe_gol = calcular_racha_booleana(df_calculo, recibe_gol_cond)
    racha_no_marca_gol = calcular_racha_booleana(df_calculo, no_marca_gol_cond)
    racha_no_recibe_gol = calcular_racha_booleana(df_calculo, no_recibe_gol_cond)

    max_racha_marca_gol = calcular_racha_maxima_booleana(marca_gol_cond)
    max_racha_recibe_gol = calcular_racha_maxima_booleana(recibe_gol_cond)
    max_racha_no_marca_gol = calcular_racha_maxima_booleana(no_marca_gol_cond)
    max_racha_no_recibe_gol = calcular_racha_maxima_booleana(no_recibe_gol_cond)

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
            "Marca Gol",
            "Máx. Racha Marca Gol",
            "Recibe Gol",
            "Máx. Racha Recibe Gol",
            "No Marca Gol",
            "Máx. Racha No Marca",
            "No Recibe Gol",
            "Máx. Racha No Recibe",
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

        f"{equipo_nombre} (10)": [
            media_gol,
            media_gol_recibido,
            media_gol_1t,
            media_gol_1t_recibido,
            media_gol_2t,
            media_gol_2t_recibido,
            media_xg_favor,
            media_xg_contra,
            f"{marca_gol_cond.mean() * 100:.1f}%",
            max_racha_marca_gol,
            f"{recibe_gol_cond.mean() * 100:.1f}%",
            max_racha_recibe_gol,
            f"{no_marca_gol_cond.mean() * 100:.1f}%",
            max_racha_no_marca_gol,
            f"{no_recibe_gol_cond.mean() * 100:.1f}%",
            max_racha_no_recibe_gol,
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
            racha_marca_gol,
            max_racha_marca_gol,
            racha_recibe_gol,
            max_racha_recibe_gol,
            racha_no_marca_gol,
            max_racha_no_marca_gol,
            racha_no_recibe_gol,
            max_racha_no_recibe_gol,
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

        f"{equipo_nombre} (5)": [
            round(df5[goles_a_favor_col].mean(), 2),
            round(df5[goles_en_contra_col].mean(), 2),
            round(df5[goles_ht_favor_col].mean(), 2),
            round(df5[goles_ht_contra_col].mean(), 2),
            round(df5[goles_st_favor_col].mean(), 2),
            round(df5[goles_st_contra_col].mean(), 2),
            round(df5[xg_favor_col].mean(), 2),
            round(df5[xg_contra_col].mean(), 2),
            f"{(df5[goles_a_favor_col] >= 1).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df5[goles_a_favor_col] >= 1),
            f"{(df5[goles_en_contra_col] >= 1).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df5[goles_en_contra_col] >= 1),
            f"{(df5[goles_a_favor_col] == 0).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df5[goles_a_favor_col] == 0),
            f"{(df5[goles_en_contra_col] == 0).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df5[goles_en_contra_col] == 0),
            f"{(((df5[goles_a_favor_col] > 0) & (df5[goles_en_contra_col] > 0)).mean() * 100):.1f}%",
            f"{((df5[goles_ht_favor_col] + df5[goles_ht_contra_col]) > 0).mean() * 100:.1f}%",
            f"{((df5[goles_ht_favor_col] + df5[goles_ht_contra_col]) > 1.5).mean() * 100:.1f}%",
            f"{((df5[goles_a_favor_col] + df5[goles_en_contra_col]) > 1.5).mean() * 100:.1f}%",
            f"{((df5[goles_a_favor_col] + df5[goles_en_contra_col]) > 2.5).mean() * 100:.1f}%",
            round(df5[remates_favor_col].mean(), 1),
            round(df5[remates_contra_col].mean(), 1),
            round(df5[a_puerta_favor_col].mean(), 1),
            round(df5[a_puerta_contra_col].mean(), 1)
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
            calcular_racha_booleana(df5, df5[goles_a_favor_col] >= 1),
            calcular_racha_maxima_booleana(df5[goles_a_favor_col] >= 1),
            calcular_racha_booleana(df5, df5[goles_en_contra_col] >= 1),
            calcular_racha_maxima_booleana(df5[goles_en_contra_col] >= 1),
            calcular_racha_booleana(df5, df5[goles_a_favor_col] == 0),
            calcular_racha_maxima_booleana(df5[goles_a_favor_col] == 0),
            calcular_racha_booleana(df5, df5[goles_en_contra_col] == 0),
            calcular_racha_maxima_booleana(df5[goles_en_contra_col] == 0),
            calcular_racha_booleana(df5, (df5[goles_a_favor_col] > 0) & (df5[goles_en_contra_col] > 0)),
            calcular_racha_booleana(df5, (df5[goles_ht_favor_col] + df5[goles_ht_contra_col]) > 0),
            calcular_racha_booleana(df5, (df5[goles_ht_favor_col] + df5[goles_ht_contra_col]) > 1.5),
            calcular_racha_booleana(df5, (df5[goles_a_favor_col] + df5[goles_en_contra_col]) > 1.5),
            calcular_racha_booleana(df5, (df5[goles_a_favor_col] + df5[goles_en_contra_col]) > 2.5),
            calcular_racha(df5, remates_favor_col, df5[remates_favor_col].mean()),
            calcular_racha(df5, remates_contra_col, df5[remates_contra_col].mean()),
            calcular_racha(df5, a_puerta_favor_col, df5[a_puerta_favor_col].mean()),
            calcular_racha(df5, a_puerta_contra_col, df5[a_puerta_contra_col].mean())
        ],

        f"{equipo_nombre} (3)": [
            round(df3[goles_a_favor_col].mean(), 2),
            round(df3[goles_en_contra_col].mean(), 2),
            round(df3[goles_ht_favor_col].mean(), 2),
            round(df3[goles_ht_contra_col].mean(), 2),
            round(df3[goles_st_favor_col].mean(), 2),
            round(df3[goles_st_contra_col].mean(), 2),
            round(df3[xg_favor_col].mean(), 2),
            round(df3[xg_contra_col].mean(), 2),
            f"{(df3[goles_a_favor_col] >= 1).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df3[goles_a_favor_col] >= 1),
            f"{(df3[goles_en_contra_col] >= 1).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df3[goles_en_contra_col] >= 1),
            f"{(df3[goles_a_favor_col] == 0).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df3[goles_a_favor_col] == 0),
            f"{(df3[goles_en_contra_col] == 0).mean() * 100:.1f}%",
            calcular_racha_maxima_booleana(df3[goles_en_contra_col] == 0),
            f"{(((df3[goles_a_favor_col] > 0) & (df3[goles_en_contra_col] > 0)).mean() * 100):.1f}%",
            f"{((df3[goles_ht_favor_col] + df3[goles_ht_contra_col]) > 0).mean() * 100:.1f}%",
            f"{((df3[goles_ht_favor_col] + df3[goles_ht_contra_col]) > 1.5).mean() * 100:.1f}%",
            f"{((df3[goles_a_favor_col] + df3[goles_en_contra_col]) > 1.5).mean() * 100:.1f}%",
            f"{((df3[goles_a_favor_col] + df3[goles_en_contra_col]) > 2.5).mean() * 100:.1f}%",
            round(df3[remates_favor_col].mean(), 1),
            round(df3[remates_contra_col].mean(), 1),
            round(df3[a_puerta_favor_col].mean(), 1),
            round(df3[a_puerta_contra_col].mean(), 1)
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
            calcular_racha_booleana(df3, df3[goles_a_favor_col] >= 1),
            calcular_racha_maxima_booleana(df3[goles_a_favor_col] >= 1),
            calcular_racha_booleana(df3, df3[goles_en_contra_col] >= 1),
            calcular_racha_maxima_booleana(df3[goles_en_contra_col] >= 1),
            calcular_racha_booleana(df3, df3[goles_a_favor_col] == 0),
            calcular_racha_maxima_booleana(df3[goles_a_favor_col] == 0),
            calcular_racha_booleana(df3, df3[goles_en_contra_col] == 0),
            calcular_racha_maxima_booleana(df3[goles_en_contra_col] == 0),
            calcular_racha_booleana(df3, (df3[goles_a_favor_col] > 0) & (df3[goles_en_contra_col] > 0)),
            calcular_racha_booleana(df3, (df3[goles_ht_favor_col] + df3[goles_ht_contra_col]) > 0),
            calcular_racha_booleana(df3, (df3[goles_ht_favor_col] + df3[goles_ht_contra_col]) > 1.5),
            calcular_racha_booleana(df3, (df3[goles_a_favor_col] + df3[goles_en_contra_col]) > 1.5),
            calcular_racha_booleana(df3, (df3[goles_a_favor_col] + df3[goles_en_contra_col]) > 2.5),
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
            "Marca Gol",
            "Recibe Gol",
            "No Marca Gol",
            "No Recibe Gol",
            "BTTS",
            "Gol HT",
            "Over 1.5 HT",
            "Over 1.5 Goles",
            "Over 2.5 Goles"
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

def mostrar_analisis_cuartos(
    equipo_local,
    equipo_visitante,
    mapa_equipos,
):
    st.markdown("## 📊 Rendimiento según clasificación del rival")

    try:
        analisis = generar_analisis_cuartos(
            equipo_local=equipo_local,
            equipo_visitante=equipo_visitante,
            mapa_equipos=mapa_equipos,
        )

    except (OSError, ValueError, KeyError) as error:
        st.warning(
            f"No se pudo construir el análisis por cuartos: {error}"
        )
        return

    st.markdown("### 🏆 Posiciones y puntos de la temporada")

    st.table(
        analisis["resumen"].style
        .hide(axis="index")
    )

    columnas_medias = [
    "Rem. favor", "Rem. contra", "Rem. totales",
    "A puerta favor", "A puerta contra", "A puerta totales",
    "BTTS", "Over 2.5", "Marca", "Recibe"  
    ]

    def estilo_cuartos(df, cuarto_objetivo):
        def color_fila(fila):
            if (
                cuarto_objetivo is not None
                and fila["Cuarto"] == cuarto_objetivo
            ):
                return [
                    "background-color: #fff3cd; color: #333333"
                ] * len(fila)

            return [""] * len(fila)

        return (
            df.style
            .apply(color_fila, axis=1)
            .format(
                {
                    columna: "{:.1f}"
                    for columna in columnas_medias
                },
                na_rep="Sin datos",
            )
            .hide(axis="index")
        )

    equipo_local_base = equipo_local.split("_", 1)[0]
    equipo_visitante_base = equipo_visitante.split("_", 1)[0]

    nombre_local = mapa_equipos.get(
        equipo_local,
        mapa_equipos.get(equipo_local_base, equipo_local_base)
    )

    nombre_vis = mapa_equipos.get(
        equipo_visitante,
        mapa_equipos.get(equipo_visitante_base, equipo_visitante_base)
    )

    # Una debajo de la otra para no comprimir tantas columnas.
    st.markdown(
        f"### 🏠 {nombre_local.title()} — partidos como local"
    )

    st.table(
        estilo_cuartos(
            analisis["local"],
            analisis["cuarto_objetivo_local"],
        )
    )

    st.markdown(
        f"### ✈️ {nombre_vis.title()} — partidos como visitante"
    )

    st.table(
        estilo_cuartos(
            analisis["visitante"],
            analisis["cuarto_objetivo_visitante"],
        )
    )

    st.caption(
        "Temporada completa. Los cuartos corresponden a la "
        "clasificación general actual de los rivales. "
        "La fila resaltada corresponde al cuarto del próximo rival "
        "cuando ambos equipos pertenecen a la misma división. "
        "PJ = partidos del grupo. N mín. métricas = menor cantidad "
        "de datos válidos utilizada entre las seis medias. "
        "Esta sección no modifica las probabilidades existentes."
    )

    if analisis["avisos"]:
        with st.expander("⚠️ Revisar cobertura e identificación de datos"):
            for aviso in analisis["avisos"]:
                st.write(f"• {aviso}")

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
        st.session_state.partidos_rango = 5

    # --- 2. CARGA DE DATOS ---
    # Cargamos siempre los 10 para que los dataframes df_local_all y df_visitante_all
    # tengan suficientes datos para todos los cálculos.
    df_local_all = cargar_datos(equipo_local_nombre, "local", 10)
    df_visitante_all = cargar_datos(equipo_visitante_nombre, "visitante", 10)       

    # Lógica para la tabla de la imagen
    stats_local = calcular_estadisticas_y_rachas(df_local_all, equipo_local_nombre, "local")
    stats_visitante = calcular_estadisticas_y_rachas(df_visitante_all, equipo_visitante_nombre, "visitante")

    # Lógica para la tabla de la imagen
    stats_local = calcular_estadisticas_y_rachas(df_local_all, equipo_local_nombre, "local")
    stats_visitante = calcular_estadisticas_y_rachas(df_visitante_all, equipo_visitante_nombre, "visitante")

    df_stats_local = pd.DataFrame(stats_local) if stats_local else pd.DataFrame()
    df_stats_visitante = pd.DataFrame(stats_visitante) if stats_visitante else pd.DataFrame()
    
    metricas_avanzadas = calcular_metricas_avanzadas(df_local_all, df_visitante_all, equipo_local_archivo=equipo_local_nombre, equipo_visitante_archivo=equipo_visitante_nombre)
    resultados = calcular_probabilidades_equipo(
        df_local_all, df_visitante_all,
        equipo_local_archivo=equipo_local_nombre,
        equipo_visitante_archivo=equipo_visitante_nombre,
    )
    
    prob_tablas = {} 
    
    posicion_local = None
    posicion_visitante = None   

    if metricas_avanzadas is not None:
        lambda_L = metricas_avanzadas["lambda_local_new"]
        lambda_V = metricas_avanzadas["lambda_vis_new"]
        lambda1_L = resultados["lambda_local_1t"]
        lambda1_V = resultados["lambda_visitante_1t"]

        # 1) Resultado y dobles (Tabla 1)
        res_1x2 = poisson_prob_1x2_y_dobles(lambda_L, lambda_V, max_goals=8)
        prob_tablas["Local_gana"] = res_1x2["1"]
        prob_tablas["Empate"] = res_1x2["X"]
        prob_tablas["Visitante_gana"] = res_1x2["2"]
        prob_tablas["1X"] = res_1x2["1X"]
        prob_tablas["X2"] = res_1x2["X2"]
        prob_tablas["12"] = res_1x2["12"]

        # 2) Goles en el partido (Tabla 2)
        lineas_goles = [0.5, 1.5, 2.5, 3.5]
        for L in lineas_goles:
            u, o = poisson_prob_total_over_under(lambda_L, lambda_V, L, max_k=8)
            clave_over = f"Over_{L}_partido"
            clave_under = f"Under_{L}_partido"
            prob_tablas[clave_over] = o
            prob_tablas[clave_under] = u
        prob_tablas["Over 1.5 Goles"] = prob_tablas["Over_1.5_partido"]
        prob_tablas["Over 2.5 Goles"] = prob_tablas["Over_2.5_partido"]

        # 3) Goles por equipo y BTTS (Tabla 3)
        for L in [0.5, 1.5]:
            uL, oL = poisson_prob_over_under(lambda_L, L, max_k=8)
            uV, oV = poisson_prob_over_under(lambda_V, L, max_k=8)
            prob_tablas[f"Local_over_{L}"] = oL
            prob_tablas[f"Local_under_{L}"] = uL
            prob_tablas[f"Visitante_over_{L}"] = oV
            prob_tablas[f"Visitante_under_{L}"] = uV
            
            if L == 0.5:
                prob_tablas["Marca Local"] = oL
                prob_tablas["Marca Visitante"] = oV

        btts = prob_btts(lambda_L, lambda_V, max_goals=8)
        prob_tablas["BTTS"] = btts
        prob_tablas["NO_BTTS"] = 100 - btts

        # 4) Goles en el 1T (Tabla 4)
        for L in [0.5, 1.5]:
            u, o = poisson_prob_total_over_under(lambda1_L, lambda1_V, L, max_k=5)
            prob_tablas[f"Over_{L}_1T"] = o
            prob_tablas[f"Under_{L}_1T"] = u

        uL05, oL05 = poisson_prob_over_under(lambda1_L, 0.5, max_k=5)
        uV05, oV05 = poisson_prob_over_under(lambda1_V, 0.5, max_k=5)
        prob_tablas["Local_over_0.5_1T"] = oL05
        prob_tablas["Local_under_0.5_1T"] = uL05
        prob_tablas["Visitante_over_0.5_1T"] = oV05
        prob_tablas["Visitante_under_0.5_1T"] = uV05    
        
        prob_tablas["Remates_favor_L"] = round(metricas_avanzadas["Remates_att_local"], 1)
        prob_tablas["Remates_favor_V"] = round(metricas_avanzadas["Remates_att_vis"], 1)
        
        # # Remates contra (mantener cálculo tradicional por ahora)
        # rem_3_l = calcular_remates_totales_contra(df_local_all.tail(3))
        # rem_5_l = calcular_remates_totales_contra(df_local_all.tail(5))
        # rem_tot_l = calcular_remates_totales_contra(df_local_all)
        # val_remates_contra_local = (rem_3_l * 0.20) + (rem_5_l * 0.30) + (rem_tot_l * 0.50)
        
        # rem_3_v = calcular_remates_totales_contra(df_visitante_all.tail(3))
        # rem_5_v = calcular_remates_totales_contra(df_visitante_all.tail(5))
        # rem_tot_v = calcular_remates_totales_contra(df_visitante_all)
        # val_remates_contra_visitante = (rem_3_v * 0.20) + (rem_5_v * 0.30) + (rem_tot_v * 0.50)
        
        prob_tablas["Remates_contra_L"] = round(metricas_avanzadas["Remates_contra_local"], 1)
        prob_tablas["Remates_contra_V"] = round(metricas_avanzadas["Remates_contra_vis"], 1)

        # Medias de liga
        prob_tablas["Liga_Local_Fav"] = round(metricas_avanzadas["liga_shots_local_fav"], 1)
        prob_tablas["Liga_Vis_Fav"] = round(metricas_avanzadas["liga_shots_vis_fav"], 1)

        # === MÉTRICAS ROBUSTAS CORREGIDAS ===
        prob_tablas["Rango_Remates_favor_L"] = (
            f"{metricas_avanzadas['Remates_rango_local_low']:.1f}-"
            f"{metricas_avanzadas['Remates_rango_local_high']:.1f}"
        ).replace(".", ",")
        prob_tablas["Amplitud_rango_favor_L"] = round(
            metricas_avanzadas['Remates_rango_local_high'] - metricas_avanzadas['Remates_rango_local_low'], 1
        )
        prob_tablas["Rango_Remates_favor_V"] = (
            f"{metricas_avanzadas['Remates_rango_vis_low']:.1f}-"
            f"{metricas_avanzadas['Remates_rango_vis_high']:.1f}"
        ).replace(".", ",")
        prob_tablas["Amplitud_rango_favor_V"] = round(
            metricas_avanzadas['Remates_rango_vis_high'] - metricas_avanzadas['Remates_rango_vis_low'], 1
        )
        
        prob_tablas["Rango_Remates_contra_L"] = (
            f"{metricas_avanzadas['Remates_rango_local_contra_low']:.1f}-"
            f"{metricas_avanzadas['Remates_rango_local_contra_high']:.1f}"
        ).replace(".", ",")
        prob_tablas["Amplitud_rango_contra_L"] = round(
            metricas_avanzadas['Remates_rango_local_contra_high'] - metricas_avanzadas['Remates_rango_local_contra_low'], 1
        )     
        prob_tablas["Rango_Remates_contra_V"] = (
            f"{metricas_avanzadas['Remates_rango_vis_contra_low']:.1f}-"
            f"{metricas_avanzadas['Remates_rango_vis_contra_high']:.1f}"
        ).replace(".", ",")
        prob_tablas["Amplitud_rango_contra_V"] = round(
            metricas_avanzadas['Remates_rango_vis_contra_high'] - metricas_avanzadas['Remates_rango_vis_contra_low'], 1
        )

        prob_tablas["Confianza_Remates_L"] = metricas_avanzadas["Remates_confianza_local"]
        prob_tablas["Confianza_Remates_V"] = metricas_avanzadas["Remates_confianza_vis"]
        prob_tablas["Confianza_Remates_contra_L"] = metricas_avanzadas["Remates_confianza_local_contra"]
        prob_tablas["Confianza_Remates_contra_V"] = metricas_avanzadas["Remates_confianza_vis_contra"]

        prob_tablas["CV_Remates_L"] = round(metricas_avanzadas["Remates_cv_local"], 3)
        prob_tablas["CV_Remates_V"] = round(metricas_avanzadas["Remates_cv_vis"], 3)

        # BLENDS detallados
        prob_tablas["Win_Remates_L"] = round(metricas_avanzadas["shots_favor_local_blend_media_winsor"], 2)
        prob_tablas["Win_Remates_V"] = round(metricas_avanzadas["shots_favor_vis_blend_media_winsor"], 2)

        prob_tablas["Mediana_Remates_L"] = round(metricas_avanzadas["shots_favor_local_blend_mediana"], 2)
        prob_tablas["Mediana_Remates_V"] = round(metricas_avanzadas["shots_favor_vis_blend_mediana"], 2)

        prob_tablas["P25_Remates_L"] = round(metricas_avanzadas["shots_favor_local_blend_p25"], 2)
        prob_tablas["P75_Remates_L"] = round(metricas_avanzadas["shots_favor_local_blend_p75"], 2)
        prob_tablas["P25_Remates_V"] = round(metricas_avanzadas["shots_favor_vis_blend_p25"], 2)
        prob_tablas["P75_Remates_V"] = round(metricas_avanzadas["shots_favor_vis_blend_p75"], 2)

        prob_tablas["STD_Remates_L"] = round(metricas_avanzadas["shots_favor_local_blend_std"], 2)
        prob_tablas["STD_Remates_V"] = round(metricas_avanzadas["shots_favor_vis_blend_std"], 2)
        
        prob_tablas["Racha_Local"] = metricas_avanzadas["RachaSuperaRematesL_txt"]
        prob_tablas["Racha_Visitante"] = metricas_avanzadas["RachaSuperaRematesV_txt"]
        prob_tablas["Hits_Local_U10"] = metricas_avanzadas["HitsSuperaRemates10L_txt"]
        prob_tablas["Hits_Visitante_U10"] = metricas_avanzadas["HitsSuperaRemates10V_txt"]
        prob_tablas["Porc_Hits_L"] = metricas_avanzadas["PctSuperaRemates10L_txt"]
        prob_tablas["Porc_Hits_V"] = metricas_avanzadas["PctSuperaRemates10V_txt"]           

        # Peligrosidad y Fragilidad (mantener cálculo tradicional)
        xgsot_3_l = calcular_xg_por_sot(df_local_all.tail(3))
        xgsot_5_l = calcular_xg_por_sot(df_local_all.tail(5))
        xgsot_tot_l = calcular_xg_por_sot(df_local_all)
        val_xgsot_local = (xgsot_3_l * 0.20) + (xgsot_5_l * 0.30) + (xgsot_tot_l * 0.50)

        xgsot_3_v = calcular_xg_por_sot(df_visitante_all.tail(3))
        xgsot_5_v = calcular_xg_por_sot(df_visitante_all.tail(5))
        xgsot_tot_v = calcular_xg_por_sot(df_visitante_all)
        val_xgsot_visitante = (xgsot_3_v * 0.20) + (xgsot_5_v * 0.30) + (xgsot_tot_v * 0.50)

        prob_tablas["Peligrosidad_L"] = round(val_xgsot_local, 2)
        prob_tablas["Peligrosidad_V"] = round(val_xgsot_visitante, 2)

        def_3_l = calcular_fragilidad_defensiva(df_local_all.tail(3))
        def_5_l = calcular_fragilidad_defensiva(df_local_all.tail(5))
        def_tot_l = calcular_fragilidad_defensiva(df_local_all)
        val_def_local = (def_3_l * 0.20) + (def_5_l * 0.30) + (def_tot_l * 0.50)

        def_3_v = calcular_fragilidad_defensiva(df_visitante_all.tail(3))
        def_5_v = calcular_fragilidad_defensiva(df_visitante_all.tail(5))
        def_tot_v = calcular_fragilidad_defensiva(df_visitante_all)
        val_def_visitante = (def_3_v * 0.20) + (def_5_v * 0.30) + (def_tot_v * 0.50)

        prob_tablas["Fragilidad_L"] = round(val_def_local, 2)
        prob_tablas["Fragilidad_V"] = round(val_def_visitante, 2)

        # Peligrosidad ajustada
        peligrosidad_ajustada_l = val_xgsot_local * val_def_visitante if val_def_visitante > 0 else val_xgsot_local
        peligrosidad_ajustada_v = val_xgsot_visitante * val_def_local if val_def_local > 0 else val_xgsot_visitante
        prob_tablas["Peligrosidad_Ajustada_L"] = round(peligrosidad_ajustada_l, 2)
        prob_tablas["Peligrosidad_Ajustada_V"] = round(peligrosidad_ajustada_v, 2)
         
        
    col_agregar = st.columns([1])
    with col_agregar[0]:
        if st.button(
            "➕ **Agregar a Lista**", 
            key=f"btn_agregar_{equipo_local_nombre}_{equipo_visitante_nombre}",
            use_container_width=True,
            help="Guarda este análisis en tu lista de partidos"
        ):
            from partidos_manager import agregar_partido_a_lista
            if agregar_partido_a_lista(
                equipo_local_nombre,
                equipo_visitante_nombre,
                prob_tablas,
            ):
                st.success(f"✅ {equipo_local_nombre} vs {equipo_visitante_nombre} agregado")
    
    if (equipo_local_nombre and equipo_visitante_nombre and
        resultados is not None and metricas_avanzadas is not None):
        mostrar_boton_agregar_partido(
            equipo_local_nombre,
            equipo_visitante_nombre,
            prob_tablas,
        )    

    mostrar_tablas_avanzadas(metricas_avanzadas, lambda1_L, lambda1_V, 
                            df_local_all, df_visitante_all, equipo_local_archivo=equipo_local_nombre, 
                            equipo_visitante_archivo=equipo_visitante_nombre)    

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
    
    stats_local = calcular_estadisticas_y_rachas(
        df_local_all,
        equipo_local_nombre,
        "local",
    )

    stats_visitante = calcular_estadisticas_y_rachas(
        df_visitante_all,
        equipo_visitante_nombre,
        "visitante",
    )

    if stats_local and stats_visitante:
        entrada_goles_local = None
        entrada_goles_visitante = None

        try:
            entrada_goles_local = extraer_entrada_goles(
                df=df_local_all,
                condicion="local",
                rango=rango_actual,
            )

            entrada_goles_visitante = extraer_entrada_goles(
                df=df_visitante_all,
                condicion="visitante",
                rango=rango_actual,
            )

        except ValueError as error:
            st.warning(
                f"Diagnóstico de entrada de goles: {error}"
            )

        if (
            entrada_goles_local is None
            or entrada_goles_visitante is None
        ):
            st.warning(
                "No se calculan probabilidades de goles: "
                "faltan entradas válidas."
            )

        else:
            # --- MEDIAS DE xG Y TIROS A PUERTA ---
            def media_segura(df, columna):
                if columna not in df.columns:
                    return 0.0

                valores = pd.to_numeric(
                    df[columna],
                    errors="coerce",
                ).dropna()

                if valores.empty:
                    return 0.0

                return float(valores.mean())


            df_local_rango = df_local_all.tail(rango_actual)
            df_visitante_rango = df_visitante_all.tail(rango_actual)            

            entrada_goles_local["media_xg_favor"] = media_segura(
                df_local_rango,
                "xg_favor",
            )

            entrada_goles_local["media_xg_contra"] = media_segura(
                df_local_rango,
                "xg_contra",
            )

            entrada_goles_local["media_tiros_puerta_favor"] = media_segura(
                df_local_rango,
                "a_puerta_favor",
            )

            entrada_goles_local["media_tiros_puerta_contra"] = media_segura(
                df_local_rango,
                "a_puerta_contra",
            )

            entrada_goles_visitante["media_xg_favor"] = media_segura(
                df_visitante_rango,
                "xg_favor",
            )

            entrada_goles_visitante["media_xg_contra"] = media_segura(
                df_visitante_rango,
                "xg_contra",
            )

            entrada_goles_visitante["media_tiros_puerta_favor"] = media_segura(
                df_visitante_rango,
                "a_puerta_favor",
            )

            entrada_goles_visitante["media_tiros_puerta_contra"] = media_segura(
                df_visitante_rango,
                "a_puerta_contra",
            )
            
            pais_local = pais_de_equipo(equipo_local_nombre)
            pais_visitante = pais_de_equipo(equipo_visitante_nombre)

            medias_liga = None

            if (
                pais_local
                and pais_visitante
                and pais_local == pais_visitante
            ):
                medias_liga = media_xg_liga(
                    pais=pais_local,
                    npartidosmax=rango_actual,
                )

            if medias_liga is not None:
                entrada_goles_local["xg_liga_favor"] = medias_liga[
                    "xg_favor_local"
                ]

                entrada_goles_local["xg_liga_contra"] = medias_liga[
                    "xg_contra_local"
                ]

                entrada_goles_local["total_liga"] = medias_liga[
                    "total_liga"
                ]

                entrada_goles_visitante["xg_liga_favor"] = medias_liga[
                    "xg_favor_visita"
                ]

                entrada_goles_visitante["xg_liga_contra"] = medias_liga[
                    "xg_contra_visita"
                ]

                entrada_goles_visitante["total_liga"] = medias_liga[
                    "total_liga"
                ]
            
            with st.expander(
                f"🔎 Diagnóstico del modelo de goles — "
                f"U{rango_actual}"
            ):
                mostrar_diagnostico_entrada_goles(
                    entrada_local=entrada_goles_local,
                    entrada_visitante=entrada_goles_visitante,
                    nombre_local=equipo_local_nombre,
                    nombre_visitante=equipo_visitante_nombre,
                )

            prediccion = predecir_goles_desde_entradas(
                entrada_local=entrada_goles_local,
                entrada_visitante=entrada_goles_visitante,
            )
            
            nivel_precision = prediccion.get(
                "_nivel_precision",
                "normal",
            )
                
            if nivel_precision == "muestra_baja":
                st.warning(
                    f"⚠️ Muestra baja: {prediccion['_n_referencia']} "
                    "partidos válidos por equipo. "
                    "El modelo aplica shrinkage hacia la media de liga "
                    "para reducir la volatilidad."
                )

            prediccion_contexto, estado_contexto = (
                aplicar_contexto_goles(
                    prediccion=prediccion,

                    df_local=(
                        entrada_goles_local["datos_modelo"]
                    ),
                    df_visitante=(
                        entrada_goles_visitante["datos_modelo"]
                    ),

                    equipo_local=equipo_local_nombre,
                    equipo_visitante=equipo_visitante_nombre,

                    n_partidos=rango_actual,
                    intensidad=0.10,
                )
            )
            with st.expander(
                "🧮 Construcción de lambdas y control de mercados"
            ):
                # --- AUDITORÍA xG + TIROS A PUERTA ---
                datos_auditoria = {
                    "Concepto": [
                        "Lambda base goles 60/40 local",
                        "Lambda base goles 60/40 visitante",
                        "Lambda xG local",
                        "Lambda xG visitante",
                        "Lambda final local",
                        "Lambda final visitante",
                        "Over 1.5 base",
                        "Over 2.5 base",
                        "BTTS base",
                        "Over 1.5 final",
                        "Over 2.5 final",
                        "BTTS final",
                        "Nivel de precisión",
                        "Partidos de referencia",
                        "Peso equipo",
                        "Peso liga",
                    ],
                    "Valor": [
                        prediccion["_lambda_local_base_60_40"],
                        prediccion["_lambda_visitante_base_60_40"],
                        prediccion["_lambda_xg_local"],
                        prediccion["_lambda_xg_visitante"],
                        prediccion["_lambda_local_base"],
                        prediccion["_lambda_visitante_base"],
                        prediccion["Over 1.5"],
                        prediccion["Over 2.5"],
                        prediccion["BTTS"],
                        prediccion_contexto.get("Over 1.5", prediccion["Over 1.5"]),
                        prediccion_contexto.get("Over 2.5", prediccion["Over 2.5"]),
                        prediccion_contexto.get("BTTS", prediccion["BTTS"]),
                        prediccion.get("_nivel_precision"),
                        prediccion.get("_n_referencia"),
                        round(prediccion.get("_peso_equipo", 0), 3),
                        round(prediccion.get("_peso_liga", 0), 3),
                    ],
                }

                df_auditoria = pd.DataFrame(datos_auditoria)

                st.subheader("Auditoría goles + xG")
                st.dataframe(
                    df_auditoria,
                    use_container_width=True,
                    hide_index=True,
                )
                mostrar_traza_modelo_goles(
                    prediccion=prediccion,
                    prediccion_contexto=prediccion_contexto,
                )

            mercados_prediccion = [
                ("Gana Local", "Gana Local"),
                ("Empate", "Empate"),
                ("Gana Visitante", "Gana Visitante"),
                ("Local o Empate 1X", "1X"),
                ("Visitante o Empate X2", "X2"),
                ("Gana Cualquiera 12", "12"),
                ("Marca Local", "Marca Local"),
                ("Marca Visitante", "Marca Visitante"),
                ("BTTS", "BTTS"),
                ("Over 1.5 Goles", "Over 1.5"),
                ("Over 2.5 Goles", "Over 2.5"),
            ]

            filas_prediccion = []

            for etiqueta, clave in mercados_prediccion:
                prob_base = float(prediccion[clave])
                prob_final = float(
                    prediccion_contexto.get(
                        clave,
                        prob_base,
                    )
                )

                filas_prediccion.append({
                    "Métrica": etiqueta,
                    "Prob. %": prob_base,
                    "Prob. final %": prob_final,
                })

            df_prediccion = pd.DataFrame(
                filas_prediccion
            )

            columnas_prediccion = [
                "Métrica",
                "Prob. %",
                "Prob. final %",
            ]

            col_pred1, col_pred2, col_pred3 = st.columns(3)

            with col_pred1:
                st.markdown("### 🏆 Resultado y Dobles")

                df_1x2 = (
                    df_prediccion.iloc[0:6]
                    .loc[:, columnas_prediccion]
                    .copy()
                    .reset_index(drop=True)
                )

                tabla_1x2 = formatear_y_resaltar(
                    df_1x2,
                    "Prob. %",
                    umbrales=(50, 45),
                    col_extra="Prob. final %",
                )

                st.table(
                    tabla_1x2.hide(axis="index")
                )

            with col_pred2:
                st.markdown("### ⚽ Goles y BTTS")

                df_goles = (
                    df_prediccion.iloc[6:9]
                    .loc[:, columnas_prediccion]
                    .copy()
                    .reset_index(drop=True)
                )

                tabla_goles = formatear_y_resaltar(
                    df_goles,
                    "Prob. %",
                    umbrales=(70, 60),
                    col_extra="Prob. final %",
                )

                st.table(
                    tabla_goles.hide(axis="index")
                )

            with col_pred3:
                st.markdown("### 📈 Overs")

                df_overs = (
                    df_prediccion.iloc[9:11]
                    .loc[:, columnas_prediccion]
                    .copy()
                    .reset_index(drop=True)
                )

                tabla_overs = formatear_y_resaltar(
                    df_overs,
                    "Prob. %",
                    umbrales=(65, 55),
                    col_extra="Prob. final %",
                )

                st.table(
                    tabla_overs.hide(axis="index")
                )

            st.caption(
                f"Modelo de referencia por volumen de goles. "
                f"U{rango_actual}: "
                f"{entrada_goles_local['n_partidos']} partidos "
                f"del local en casa y "
                f"{entrada_goles_visitante['n_partidos']} "
                f"del visitante fuera. "
                f"Rachas disponibles en el diagnóstico; "
                f"sin bono automático en esta versión."
            )

            st.caption(estado_contexto)

    else:
        st.warning(
            "No hay estadísticas suficientes para construir "
            "la predicción de goles en ambas condiciones."
        )

    # Sección independiente del modelo de goles.
    mostrar_analisis_cuartos(
        equipo_local=equipo_local_nombre,
        equipo_visitante=equipo_visitante_nombre,
        mapa_equipos=mapa_equipos,
    )
    
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
            
    mostrar_resultados(resultados, df_local_all, df_visitante_all)    
        
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

    
else:
    st.warning("Selecciona un partido para ver el análisis.")