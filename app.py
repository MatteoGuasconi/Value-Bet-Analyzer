import datetime
import numpy as np
import pandas as pd
from scipy.stats import poisson
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER - SERIE A",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS Dark Fintech - Contrasto Alto e Testi Bianchi
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0B132B !important;
        color: #FFFFFF !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    div[data-baseweb="select"] > div {
        background-color: #F8FAFC !important;
        color: #0B132B !important;
        border-radius: 6px !important;
    }
    
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: #0B132B !important;
    }
    
    div[data-baseweb="popover"] div, div[role="listbox"] div {
        background-color: #F8FAFC !important;
        color: #0B132B !important;
    }
    
    div[role="option"] {
        background-color: #F8FAFC !important;
        color: #0B132B !important;
    }
    
    div[role="option"]:hover {
        background-color: #2DD4BF !important;
        color: #0B132B !important;
    }
    
    [data-testid="stToolbar"], footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        position: fixed !important;
        top: 12px !important;
        left: 12px !important;
        z-index: 9999999 !important;
        background-color: #2DD4BF !important;
        color: #0B132B !important;
        border-radius: 8px !important;
        padding: 6px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
        border: 2px solid #FFFFFF !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #0B132B !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #1C2541 !important;
        border-right: 1px solid #2D3A5D !important;
    }
    
    .metric-card {
        background-color: #1C2541;
        border: 1px solid #2D3A5D;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    
    .metric-title {
        font-size: 0.75rem;
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        font-weight: 600;
    }
    
    .stButton>button {
        background-color: #2DD4BF !important;
        color: #0B132B !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    
    .stButton>button:hover {
        background-color: #14B8A6 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# DATABASE UFFICIALE SERIE A (20 SQUADRE - SENZA VERONA, CON SASSUOLO)
SERIE_A_SQUADS = {
    "Atalanta": [
        {"name": "Carnesecchi", "role": "Goalkeeper", "number": "29", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Kossounou", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Hien", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.7},
        {"name": "Kolasinac", "role": "Defender", "number": "23", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Bellanova", "role": "Midfielder", "number": "16", "sot_90": 0.6, "fouls_c_90": 1.1},
        {"name": "De Roon", "role": "Midfielder", "number": "15", "sot_90": 0.3, "fouls_c_90": 1.9},
        {"name": "Ederson", "role": "Midfielder", "number": "13", "sot_90": 0.7, "fouls_c_90": 1.8},
        {"name": "Ruggeri", "role": "Midfielder", "number": "22", "sot_90": 0.4, "fouls_c_90": 1.0},
        {"name": "De Ketelaere", "role": "Attacker", "number": "17", "sot_90": 1.4, "fouls_c_90": 0.8},
        {"name": "Lookman", "role": "Attacker", "number": "11", "sot_90": 1.8, "fouls_c_90": 0.9},
        {"name": "Retegui", "role": "Attacker", "number": "32", "sot_90": 2.1, "fouls_c_90": 1.4}
    ],
    "Bologna": [
        {"name": "Skorupski", "role": "Goalkeeper", "number": "28", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Posch", "role": "Defender", "number": "3", "sot_90": 0.2, "fouls_c_90": 1.4},
        {"name": "Beukema", "role": "Defender", "number": "31", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Lucumi", "role": "Defender", "number": "26", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Miranda", "role": "Defender", "number": "33", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Freuler", "role": "Midfielder", "number": "8", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Aebischer", "role": "Midfielder", "number": "20", "sot_90": 0.4, "fouls_c_90": 1.2},
        {"name": "Fabbian", "role": "Midfielder", "number": "80", "sot_90": 0.9, "fouls_c_90": 1.0},
        {"name": "Orsolini", "role": "Attacker", "number": "7", "sot_90": 1.5, "fouls_c_90": 0.8},
        {"name": "Ndoye", "role": "Attacker", "number": "11", "sot_90": 1.2, "fouls_c_90": 1.1},
        {"name": "Castro", "role": "Attacker", "number": "9", "sot_90": 1.6, "fouls_c_90": 1.5}
    ],
    "Cagliari": [
        {"name": "Scuffet", "role": "Goalkeeper", "number": "22", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Zappa", "role": "Defender", "number": "28", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Mina", "role": "Defender", "number": "26", "sot_90": 0.1, "fouls_c_90": 2.1},
        {"name": "Luperto", "role": "Defender", "number": "33", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Augello", "role": "Defender", "number": "27", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Prati", "role": "Midfielder", "number": "16", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Adopo", "role": "Midfielder", "number": "8", "sot_90": 0.4, "fouls_c_90": 1.7},
        {"name": "Viola", "role": "Midfielder", "number": "10", "sot_90": 0.8, "fouls_c_90": 0.8},
        {"name": "Luvumbo", "role": "Attacker", "number": "77", "sot_90": 1.3, "fouls_c_90": 1.0},
        {"name": "Piccoli", "role": "Attacker", "number": "91", "sot_90": 1.5, "fouls_c_90": 1.8},
        {"name": "Lapadula", "role": "Attacker", "number": "9", "sot_90": 1.4, "fouls_c_90": 1.6}
    ],
    "Como": [
        {"name": "Audero", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Goldaniga", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Dossena", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Kempf", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Moreno", "role": "Defender", "number": "18", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Perrone", "role": "Midfielder", "number": "6", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Sergi Roberto", "role": "Midfielder", "number": "20", "sot_90": 0.5, "fouls_c_90": 1.0},
        {"name": "Strefezza", "role": "Midfielder", "number": "7", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Nico Paz", "role": "Midfielder", "number": "79", "sot_90": 1.4, "fouls_c_90": 0.8},
        {"name": "Fadera", "role": "Attacker", "number": "16", "sot_90": 1.0, "fouls_c_90": 1.1},
        {"name": "Cutrone", "role": "Attacker", "number": "10", "sot_90": 1.6, "fouls_c_90": 1.4}
    ],
    "Fiorentina": [
        {"name": "De Gea", "role": "Goalkeeper", "number": "43", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Dodo", "role": "Defender", "number": "2", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Comuzzo", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Ranieri", "role": "Defender", "number": "68", "sot_90": 0.15, "fouls_c_90": 1.4},
        {"name": "Gosens", "role": "Defender", "number": "21", "sot_90": 0.8, "fouls_c_90": 1.1},
        {"name": "Cataldi", "role": "Midfielder", "number": "32", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Bove", "role": "Midfielder", "number": "4", "sot_90": 0.7, "fouls_c_90": 1.6},
        {"name": "Colpani", "role": "Midfielder", "number": "23", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Beltran", "role": "Attacker", "number": "9", "sot_90": 1.3, "fouls_c_90": 1.2},
        {"name": "Gudmundsson", "role": "Attacker", "number": "10", "sot_90": 1.7, "fouls_c_90": 0.9},
        {"name": "Kean", "role": "Attacker", "number": "20", "sot_90": 2.0, "fouls_c_90": 1.7}
    ],
    "Frosinone": [
        {"name": "Cerofolini", "role": "Goalkeeper", "number": "31", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Oyono", "role": "Defender", "number": "19", "sot_90": 0.2, "fouls_c_90": 1.4},
        {"name": "Biraschi", "role": "Defender", "number": "30", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Monterisi", "role": "Defender", "number": "5", "sot_90": 0.15, "fouls_c_90": 1.3},
        {"name": "Marchizza", "role": "Defender", "number": "22", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Barrenechea", "role": "Midfielder", "number": "45", "sot_90": 0.2, "fouls_c_90": 1.8},
        {"name": "Brescianini", "role": "Midfielder", "number": "4", "sot_90": 0.8, "fouls_c_90": 1.5},
        {"name": "Reinier", "role": "Midfielder", "number": "12", "sot_90": 0.9, "fouls_c_90": 1.0},
        {"name": "Soulé", "role": "Attacker", "number": "18", "sot_90": 1.6, "fouls_c_90": 0.8},
        {"name": "Cheddira", "role": "Attacker", "number": "70", "sot_90": 1.5, "fouls_c_90": 1.7},
        {"name": "Kaio Jorge", "role": "Attacker", "number": "9", "sot_90": 1.4, "fouls_c_90": 1.1}
    ],
    "Genoa": [
        {"name": "Gollini", "role": "Goalkeeper", "number": "95", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Vogliacco", "role": "Defender", "number": "14", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Bani", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Vasquez", "role": "Defender", "number": "22", "sot_90": 0.2, "fouls_c_90": 1.6},
        {"name": "Sabelli", "role": "Midfielder", "number": "20", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Frendrup", "role": "Midfielder", "number": "32", "sot_90": 0.4, "fouls_c_90": 2.2},
        {"name": "Badelj", "role": "Midfielder", "number": "47", "sot_90": 0.2, "fouls_c_90": 1.5},
        {"name": "Malinovskyi", "role": "Midfielder", "number": "17", "sot_90": 1.3, "fouls_c_90": 1.1},
        {"name": "Martin", "role": "Midfielder", "number": "3", "sot_90": 0.3, "fouls_c_90": 1.0},
        {"name": "Vitinha", "role": "Attacker", "number": "9", "sot_90": 1.4, "fouls_c_90": 1.1},
        {"name": "Pinamonti", "role": "Attacker", "number": "99", "sot_90": 1.8, "fouls_c_90": 1.5}
    ],
    "Inter": [
        {"name": "Sommer", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Pavard", "role": "Defender", "number": "28", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Acerbi", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Bastoni", "role": "Defender", "number": "95", "sot_90": 0.15, "fouls_c_90": 0.9},
        {"name": "Darmian", "role": "Midfielder", "number": "36", "sot_90": 0.4, "fouls_c_90": 1.0},
        {"name": "Barella", "role": "Midfielder", "number": "23", "sot_90": 0.8, "fouls_c_90": 1.4},
        {"name": "Calhanoglu", "role": "Midfielder", "number": "20", "sot_90": 1.1, "fouls_c_90": 1.5},
        {"name": "Mkhitaryan", "role": "Midfielder", "number": "22", "sot_90": 0.9, "fouls_c_90": 1.2},
        {"name": "Dimarco", "role": "Midfielder", "number": "32", "sot_90": 1.0, "fouls_c_90": 0.8},
        {"name": "Thuram", "role": "Attacker", "number": "9", "sot_90": 1.8, "fouls_c_90": 1.3},
        {"name": "Lautaro Martinez", "role": "Attacker", "number": "10", "sot_90": 2.2, "fouls_c_90": 1.6}
    ],
    "Juventus": [
        {"name": "Di Gregorio", "role": "Goalkeeper", "number": "29", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Savona", "role": "Defender", "number": "37", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Gatti", "role": "Defender", "number": "4", "sot_90": 0.2, "fouls_c_90": 1.6},
        {"name": "Bremer", "role": "Defender", "number": "3", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Cambiaso", "role": "Defender", "number": "27", "sot_90": 0.7, "fouls_c_90": 1.2},
        {"name": "Locatelli", "role": "Midfielder", "number": "5", "sot_90": 0.4, "fouls_c_90": 1.7},
        {"name": "Thuram", "role": "Midfielder", "number": "19", "sot_90": 0.6, "fouls_c_90": 1.5},
        {"name": "Conceicao", "role": "Midfielder", "number": "7", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Koopmeiners", "role": "Midfielder", "number": "8", "sot_90": 1.4, "fouls_c_90": 1.0},
        {"name": "Yildiz", "role": "Attacker", "number": "10", "sot_90": 1.3, "fouls_c_90": 0.8},
        {"name": "Vlahovic", "role": "Attacker", "number": "9", "sot_90": 2.1, "fouls_c_90": 1.4}
    ],
    "Lazio": [
        {"name": "Provedel", "role": "Goalkeeper", "number": "94", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Lazzari", "role": "Defender", "number": "29", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Gila", "role": "Defender", "number": "34", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Romagnoli", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Nuno Tavares", "role": "Defender", "number": "30", "sot_90": 0.5, "fouls_c_90": 1.3},
        {"name": "Guendouzi", "role": "Midfielder", "number": "8", "sot_90": 0.6, "fouls_c_90": 1.8},
        {"name": "Rovella", "role": "Midfielder", "number": "6", "sot_90": 0.2, "fouls_c_90": 1.6},
        {"name": "Isaksen", "role": "Midfielder", "number": "18", "sot_90": 1.1, "fouls_c_90": 0.7},
        {"name": "Dia", "role": "Midfielder", "number": "19", "sot_90": 1.5, "fouls_c_90": 1.0},
        {"name": "Zaccagni", "role": "Attacker", "number": "10", "sot_90": 1.4, "fouls_c_90": 1.5},
        {"name": "Castellanos", "role": "Attacker", "number": "19", "sot_90": 1.9, "fouls_c_90": 1.8}
    ],
    "Lecce": [
        {"name": "Falcone", "role": "Goalkeeper", "number": "30", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Guilbert", "role": "Defender", "number": "12", "sot_90": 0.2, "fouls_c_90": 1.4},
        {"name": "Baschirotto", "role": "Defender", "number": "6", "sot_90": 0.1, "fouls_c_90": 1.8},
        {"name": "Gaspar", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Gallo", "role": "Defender", "number": "25", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Ramadani", "role": "Midfielder", "number": "20", "sot_90": 0.3, "fouls_c_90": 2.1},
        {"name": "Coulibaly", "role": "Midfielder", "number": "29", "sot_90": 0.4, "fouls_c_90": 1.9},
        {"name": "Pierotti", "role": "Midfielder", "number": "50", "sot_90": 0.9, "fouls_c_90": 1.2},
        {"name": "Dorgu", "role": "Midfielder", "number": "13", "sot_90": 1.1, "fouls_c_90": 1.5},
        {"name": "Banda", "role": "Attacker", "number": "22", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Krstovic", "role": "Attacker", "number": "9", "sot_90": 2.2, "fouls_c_90": 1.6}
    ],
    "Milan": [
        {"name": "Maignan", "role": "Goalkeeper", "number": "16", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Calabria", "role": "Defender", "number": "2", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Tomori", "role": "Defender", "number": "23", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Pavlovic", "role": "Defender", "number": "31", "sot_90": 0.15, "fouls_c_90": 1.5},
        {"name": "Theo Hernandez", "role": "Defender", "number": "19", "sot_90": 1.1, "fouls_c_90": 1.6},
        {"name": "Fofana", "role": "Midfielder", "number": "29", "sot_90": 0.5, "fouls_c_90": 1.8},
        {"name": "Reijnders", "role": "Midfielder", "number": "14", "sot_90": 0.9, "fouls_c_90": 1.1},
        {"name": "Pulisic", "role": "Midfielder", "number": "11", "sot_90": 1.5, "fouls_c_90": 0.8},
        {"name": "Loftus-Cheek", "role": "Midfielder", "number": "8", "sot_90": 1.1, "fouls_c_90": 1.4},
        {"name": "Leao", "role": "Attacker", "number": "10", "sot_90": 1.9, "fouls_c_90": 0.7},
        {"name": "Morata", "role": "Attacker", "number": "7", "sot_90": 1.6, "fouls_c_90": 1.5}
    ],
    "Monza": [
        {"name": "Turati", "role": "Goalkeeper", "number": "30", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Izzo", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.9},
        {"name": "Pablo Marí", "role": "Defender", "number": "22", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Carboni", "role": "Defender", "number": "44", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Pereira", "role": "Midfielder", "number": "27", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Bondo", "role": "Midfielder", "number": "38", "sot_90": 0.3, "fouls_c_90": 1.7},
        {"name": "Pessina", "role": "Midfielder", "number": "32", "sot_90": 0.6, "fouls_c_90": 1.4},
        {"name": "Kyriakopoulos", "role": "Midfielder", "number": "77", "sot_90": 0.5, "fouls_c_90": 1.2},
        {"name": "Maldini", "role": "Attacker", "number": "14", "sot_90": 1.2, "fouls_c_90": 0.7},
        {"name": "Caprari", "role": "Attacker", "number": "10", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Djuric", "role": "Attacker", "number": "11", "sot_90": 1.4, "fouls_c_90": 1.8}
    ],
    "Napoli": [
        {"name": "Meret", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Di Lorenzo", "role": "Defender", "number": "22", "sot_90": 0.5, "fouls_c_90": 1.1},
        {"name": "Rrahmani", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.0},
        {"name": "Buongiorno", "role": "Defender", "number": "4", "sot_90": 0.15, "fouls_c_90": 1.4},
        {"name": "Olivera", "role": "Defender", "number": "17", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Anguissa", "role": "Midfielder", "number": "99", "sot_90": 0.6, "fouls_c_90": 1.6},
        {"name": "Lobotka", "role": "Midfielder", "number": "68", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "McTominay", "role": "Midfielder", "number": "8", "sot_90": 1.3, "fouls_c_90": 1.5},
        {"name": "Politano", "role": "Attacker", "number": "21", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "Lukaku", "role": "Attacker", "number": "11", "sot_90": 2.0, "fouls_c_90": 1.6},
        {"name": "Kvaratskhelia", "role": "Attacker", "number": "77", "sot_90": 1.9, "fouls_c_90": 0.8}
    ],
    "Parma": [
        {"name": "Suzuki", "role": "Goalkeeper", "number": "31", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Coulibaly", "role": "Defender", "number": "26", "sot_90": 0.2, "fouls_c_90": 1.4},
        {"name": "Delprato", "role": "Defender", "number": "15", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Circati", "role": "Defender", "number": "39", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Valeri", "role": "Defender", "number": "14", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Bernabe", "role": "Midfielder", "number": "10", "sot_90": 0.7, "fouls_c_90": 1.0},
        {"name": "Estevez", "role": "Midfielder", "number": "8", "sot_90": 0.3, "fouls_c_90": 2.0},
        {"name": "Man", "role": "Attacker", "number": "98", "sot_90": 1.6, "fouls_c_90": 0.8},
        {"name": "Sohm", "role": "Midfielder", "number": "19", "sot_90": 0.8, "fouls_c_90": 1.3},
        {"name": "Mihaila", "role": "Attacker", "number": "28", "sot_90": 1.2, "fouls_c_90": 0.7},
        {"name": "Bonny", "role": "Attacker", "number": "13", "sot_90": 1.5, "fouls_c_90": 1.5}
    ],
    "Roma": [
        {"name": "Svilar", "role": "Goalkeeper", "number": "99", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Celik", "role": "Defender", "number": "19", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Mancini", "role": "Defender", "number": "23", "sot_90": 0.2, "fouls_c_90": 2.0},
        {"name": "Ndicka", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Angelino", "role": "Defender", "number": "3", "sot_90": 0.3, "fouls_c_90": 1.0},
        {"name": "Cristante", "role": "Midfielder", "number": "4", "sot_90": 0.5, "fouls_c_90": 1.8},
        {"name": "Paredes", "role": "Midfielder", "number": "16", "sot_90": 0.4, "fouls_c_90": 2.1},
        {"name": "Pellegrini", "role": "Midfielder", "number": "7", "sot_90": 1.2, "fouls_c_90": 1.2},
        {"name": "Soulé", "role": "Attacker", "number": "18", "sot_90": 1.4, "fouls_c_90": 0.7},
        {"name": "Dybala", "role": "Attacker", "number": "21", "sot_90": 1.8, "fouls_c_90": 0.6},
        {"name": "Dovbyk", "role": "Attacker", "number": "11", "sot_90": 2.1, "fouls_c_90": 1.5}
    ],
    "Sassuolo": [
        {"name": "Consigli", "role": "Goalkeeper", "number": "47", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Toljan", "role": "Defender", "number": "22", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Erlic", "role": "Defender", "number": "28", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Ferrari", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Doig", "role": "Defender", "number": "3", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Matheus Henrique", "role": "Midfielder", "number": "7", "sot_90": 0.5, "fouls_c_90": 1.6},
        {"name": "Boloca", "role": "Midfielder", "number": "24", "sot_90": 0.3, "fouls_c_90": 1.8},
        {"name": "Thorstvedt", "role": "Midfielder", "number": "42", "sot_90": 0.9, "fouls_c_90": 1.4},
        {"name": "Berardi", "role": "Attacker", "number": "10", "sot_90": 1.8, "fouls_c_90": 0.7},
        {"name": "Laurienté", "role": "Attacker", "number": "45", "sot_90": 1.5, "fouls_c_90": 1.0},
        {"name": "Pinamonti", "role": "Attacker", "number": "9", "sot_90": 1.9, "fouls_c_90": 1.5}
    ],
    "Torino": [
        {"name": "Milinkovic-Savic", "role": "Goalkeeper", "number": "32", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Walukiewicz", "role": "Defender", "number": "23", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Coco", "role": "Defender", "number": "4", "sot_90": 0.2, "fouls_c_90": 1.5},
        {"name": "Masina", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Lazaro", "role": "Midfielder", "number": "20", "sot_90": 0.5, "fouls_c_90": 1.1},
        {"name": "Ricci", "role": "Midfielder", "number": "28", "sot_90": 0.4, "fouls_c_90": 1.6},
        {"name": "Ilic", "role": "Midfielder", "number": "8", "sot_90": 0.6, "fouls_c_90": 1.5},
        {"name": "Vlasic", "role": "Midfielder", "number": "10", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "Sosa", "role": "Defender", "number": "24", "sot_90": 0.3, "fouls_c_90": 1.0},
        {"name": "Sanabria", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.1},
        {"name": "Zapata", "role": "Attacker", "number": "91", "sot_90": 2.0, "fouls_c_90": 1.7}
    ],
    "Udinese": [
        {"name": "Okoye", "role": "Goalkeeper", "number": "40", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Kabasele", "role": "Defender", "number": "27", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Bijol", "role": "Defender", "number": "29", "sot_90": 0.15, "fouls_c_90": 1.8},
        {"name": "Giannetti", "role": "Defender", "number": "30", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Ehizibue", "role": "Midfielder", "number": "19", "sot_90": 0.4, "fouls_c_90": 1.3},
        {"name": "Karlstrom", "role": "Midfielder", "number": "25", "sot_90": 0.2, "fouls_c_90": 2.0},
        {"name": "Lovric", "role": "Midfielder", "number": "8", "sot_90": 0.7, "fouls_c_90": 1.4},
        {"name": "Kamara", "role": "Midfielder", "number": "11", "sot_90": 0.4, "fouls_c_90": 1.2},
        {"name": "Thauvin", "role": "Attacker", "number": "10", "sot_90": 1.5, "fouls_c_90": 0.9},
        {"name": "Brenner", "role": "Attacker", "number": "17", "sot_90": 1.2, "fouls_c_90": 0.8},
        {"name": "Lucca", "role": "Attacker", "number": "93", "sot_90": 1.8, "fouls_c_90": 1.7}
    ],
    "Venezia": [
        {"name": "Joronen", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Svoboda", "role": "Defender", "number": "30", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Idzes", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Sverko", "role": "Defender", "number": "33", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Candela", "role": "Midfielder", "number": "27", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Duncan", "role": "Midfielder", "number": "32", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Nicolussi Caviglia", "role": "Midfielder", "number": "38", "sot_90": 0.5, "fouls_c_90": 1.6},
        {"name": "Zampano", "role": "Midfielder", "number": "7", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Oristanio", "role": "Attacker", "number": "19", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Busio", "role": "Midfielder", "number": "6", "sot_90": 0.8, "fouls_c_90": 1.2},
        {"name": "Pohjanpalo", "role": "Attacker", "number": "20", "sot_90": 1.9, "fouls_c_90": 1.4}
    ]
}

# Inizializzazione Stato
if "history_bets" not in st.session_state:
    st.session_state.history_bets = []
if "injuries_list" not in st.session_state:
    st.session_state.injuries_list = []

# Sidebar
st.sidebar.markdown("### 👑 SERIE A • PROTOCOLLO v4.0")

st.sidebar.markdown("---")
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.select_slider("Frazione di Kelly", options=[0.25, 0.50, 1.0], value=0.50, help="Protocollo standard: Kelly/2 (0.50)")
min_edge_pct = st.sidebar.slider("Soglia Minima Edge (%)", min_value=1.0, max_value=5.0, value=3.0, step=0.5, help="Soglia minima da protocollo: 3.0%")
min_edge_val = min_edge_pct / 100.0

total_profit = sum([b.get("profit", 0.0) for b in st.session_state.history_bets if b.get("status") in ["VINTA", "PERSA"]])
total_stake_history = sum([b.get("stake", 0.0) for b in st.session_state.history_bets if b.get("status") in ["VINTA", "PERSA"]])
current_bankroll = initial_bankroll + total_profit
yield_val = (total_profit / total_stake_history * 100.0) if total_stake_history > 0 else 0.0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 STATISTICHE PORTAFOGLIO")
st.sidebar.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Capitale Attuale</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF;">{current_bankroll:.2f} €</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Profitto / Perdita</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: {'#2DD4BF' if total_profit >= 0 else '#EF4444'};">{total_profit:+.2f} €</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Yield %</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: {'#2DD4BF' if yield_val >= 0 else '#EF4444'};">{yield_val:+.2f}%</div>
    </div>
""", unsafe_allow_html=True)

st.title("VALUE BET ANALYZER • SERIE A")

tab_analyzer, tab_players, tab_injuries, tab_register, tab_kpi = st.tabs([
    "🎯 Analisi Squadre & Match",
    "⚡ Statistiche Giocatori (SOT & Falli)",
    "🏥 Gestione Infermeria",
    "📝 Registro Scommesse",
    "📈 KPI & Statistiche"
])

class QuantitativeEngine:
    @staticmethod
    def calculate_metrics(p_reale, quota_book, bankroll):
        if p_reale <= 0.0 or quota_book <= 1.0:
            return {
                "p_imp": 0.0, "edge": 0.0, "ev": 0.0, "quota_equa": 99.0,
                "kelly_half": 0.0, "stake_pct": 0.0, "stake_eur": 0.0, "verdetto": "NO BET / Dati non validi"
            }
        p_imp = 1.0 / quota_book
        edge = (quota_book / (1.0 / p_reale)) - 1.0
        ev = (p_reale * quota_book) - 1.0
        b = quota_book - 1.0
        
        if b > 0:
            kelly_full = ((p_reale * b) - (1.0 - p_reale)) / b
            kelly_half = max(0.0, kelly_full * 0.50)
        else:
            kelly_half = 0.0
            
        if edge < 0.03:
            cap_fascia = 0.05
        elif edge <= 0.07:
            cap_fascia = 0.12
        else:
            cap_fascia = 0.20
            
        final_stake_pct = min(kelly_half, cap_fascia)
        stake_eur = round(bankroll * final_stake_pct, 2)
        
        verdetto = "BET QUALIFICATO" if edge >= 0.03 and ev > 0 and quota_book >= 1.70 else "NO BET / Sotto soglia protocollo"
        
        return {
            "p_imp": round(p_imp * 100, 2),
            "edge": round(edge * 100, 2),
            "ev": round(ev * 100, 2),
            "quota_equa": round(1.0 / p_reale, 2),
            "kelly_half": round(kelly_half * 100, 2),
            "stake_pct": round(final_stake_pct * 100, 2),
            "stake_eur": stake_eur,
            "verdetto": verdetto
        }

with tab_analyzer:
    st.markdown("### 🏟️ ANALISI MATCH & MERCATI DI SQUADRA")
    st.caption("Protocollo Match Analyst v4.0: Seleziona il mercato per sbloccare i parametri statistici corretti.")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        home_team = st.selectbox("Squadra di Casa", sorted(list(SERIE_A_SQUADS.keys())), index=0)
        away_team = st.selectbox("Squadra Trasferta", sorted(list(SERIE_A_SQUADS.keys())), index=1)
        match_day = st.text_input("Competizione & Giornata", value="Serie A - Giornata 28")
        
    with col_in2:
        market_category = st.selectbox(
            "Protocollo / Categoria Mercato",
            [
                "⚽ Gol (Over 2.5, Over 1.5 Team, 1X2, BTTS)",
                "🚩 Calci d'Angolo (Over/Under Totali e Team)",
                "🎯 Tiri in Porta / SOT (Team)",
                "🏆 Handicap & Risultati Esatti / Parziale-Finale",
                "✍️ Mercato Personalizzato / Tutti gli Altri"
            ]
        )
        exact_market_name = st.text_input("Specifica Mercato e Linea", placeholder="es. Over 2.5 / Over 8.5 Corner / Over 1.5 Inter")
        quota_bk = st.number_input("Quota Bookmaker (es. Vincitù / Sharp)", min_value=1.01, max_value=50.0, value=1.85, step=0.01)

    st.markdown("---")
    
    def get_injury_penalty(team_name):
        penalty_xg = 0.0
        for inj in st.session_state.injuries_list:
            if inj["team"].strip().lower() == team_name.strip().lower():
                imp = inj["importance"]
                if "Top player" in imp: penalty_xg += 0.10
                elif "Attaccante titolare" in imp: penalty_xg += 0.05
                elif "Centrocampista top" in imp: penalty_xg += 0.05
                elif "Centrocampista titolare" in imp: penalty_xg += 0.02
        return penalty_xg

    pen_home = get_injury_penalty(home_team)
    pen_away = get_injury_penalty(away_team)
    
    if pen_home > 0 or pen_away > 0:
        st.info(f"🏥 Impatto Infermeria rilevato dal modello -> Penalità xG applicata: {home_team} (-{pen_home*100:.0f}%), {away_team} (-{pen_away*100:.0f}%)")

    if "⚽ Gol" in market_category:
        st.markdown("#### 📊 PARAMETRI GOL & EXPECTED GOALS (xG)")
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1: xg_home_raw = st.number_input("xG Base Casa (ultime 8)", min_value=0.1, max_value=5.0, value=1.65, step=0.05)
        with col_st2: xg_away_raw = st.number_input("xG Base Trasferta (ultime 8)", min_value=0.1, max_value=5.0, value=1.15, step=0.05)
        with col_st3: conf_level = st.selectbox("Confidenza Modello", ["ALTA", "MEDIA", "BASSA"], index=0)
        
        xg_home = max(0.1, xg_home_raw * (1.0 - pen_home))
        xg_away = max(0.1, xg_away_raw * (1.0 - pen_away))
        
        lambda_tot = xg_home + xg_away
        if "Over 2.5" in exact_market_name:
            p_model = float(1.0 - poisson.cdf(2, lambda_tot))
        elif "Over 1.5" in exact_market_name and ("Casa" in exact_market_name or home_team.lower() in exact_market_name.lower()):
            p_model = float(1.0 - poisson.cdf(1, xg_home))
        elif "Over 1.5" in exact_market_name and ("Trasferta" in exact_market_name or away_team.lower() in exact_market_name.lower()):
            p_model = float(1.0 - poisson.cdf(1, xg_away))
        else:
            p_model = min(0.95, max(0.05, 0.50 + (xg_home - xg_away) * 0.10))

    elif "🚩 Calci d'Angolo" in market_category:
        st.markdown("#### 🚩 PARAMETRI CALCI D'ANGOLO (Protocollo Corner)")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: mean_corners = st.number_input("Media Corner Combinati / Proiettati", min_value=2.0, max_value=18.0, value=9.5, step=0.5)
        with col_c2: cross_vol = st.number_input("Volume Cross / Gara (Correzione +8% se >20)", min_value=10.0, max_value=35.0, value=19.0, step=1.0)
        with col_c3: ref_sev = st.selectbox("Direttore di Gara / Arbitro", ["Permissivo (-5%)", "Standard (0%)", "Severo (+5%)"])
        
        c_mod = mean_corners * (1.08 if cross_vol > 20 else 1.0)
        if "Severo" in ref_sev: c_mod *= 1.05
        elif "Permissivo" in ref_sev: c_mod *= 0.95
        
        p_model = float(1.0 - poisson.cdf(8, c_mod)) if "Over 8.5" in exact_market_name else 0.55

    elif "🎯 Tiri in Porta" in market_category:
        st.markdown("#### 🎯 PARAMETRI TIRI IN PORTA / SOT TEAM")
        col_t1, col_t2 = st.columns(2)
        with col_t1: base_sot = st.number_input("Media SOT / Tiri in Porta Proiettati", min_value=1.0, max_value=15.0, value=4.5, step=0.5)
        with col_t2: low_block = st.selectbox("Atteggiamento Avversario", ["Normale / Linea Alta", "Blocco Basso (Low Block)"])
        
        sot_mod = base_sot * (0.90 if "Blocco Basso" in low_block else 1.0)
        p_model = float(1.0 - poisson.cdf(3, sot_mod)) if "Over 3.5" in exact_market_name else 0.52

    else:
        st.markdown("#### ✍️ PARAMETRI MERCATO PERSONALIZZATO")
        col_p1, col_p2 = st.columns(2)
        with col_p1: est_prob = st.slider("Stima Probabilità Reale (%)", min_value=5.0, max_value=95.0, value=55.0, step=1.0)
        p_model = est_prob / 100.0

    calc_res = QuantitativeEngine.calculate_metrics(p_model, quota_bk, current_bankroll)

    st.markdown("---")
    st.markdown("### 📋 REPORT DI VALUTAZIONE TECNICO-QUANTITATIVA")
    
    rep_col1, rep_col2, rep_col3 = st.columns(3)
    with rep_col1:
        st.metric("Probabilità Reale Modello", f"{p_model*100:.1f}%")
        st.metric("Quota Equa", f"{calc_res['quota_equa']:.2f}")
    with rep_col2:
        st.metric("Edge Statistico", f"{calc_res['edge']:+.2f}%", help="Soglia minima protocollo: > 3.0%")
        st.metric("Valore Atteso (EV)", f"{calc_res['ev']:+.2f}%")
    with rep_col3:
        st.metric("Stake Consigliato (Kelly/2)", f"{calc_res['stake_pct']}%", f"{calc_res['stake_eur']:.2f} €")
        st.metric("Verdetto Protocollo", calc_res['verdetto'])

    st.markdown("---")
    if calc_res['edge'] >= 3.0 and quota_bk >= 1.70:
        st.success(f"✅ **BET QUALIFICATO**: Il match rispetta tutti i filtri quantitativi del protocollo v4.0.")
        if st.button("REGISTRA SCOMMESSA NEL REGISTRO"):
            new_bet = {
                "id": len(st.session_state.history_bets) + 1,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "match": f"{home_team} vs {away_team}",
                "market": exact_market_name or market_category,
                "odds": quota_bk,
                "stake": calc_res['stake_eur'],
                "ev": calc_res['ev'],
                "status": "IN CORSO",
                "profit": 0.0
            }
            st.session_state.history_bets.append(new_bet)
            st.success("Scommessa salvata con successo nel Registro!")
            st.rerun()
    else:
        st.warning("⚠️ **NO BET**: L'opportunità non soddisfa i requisiti minimi di Edge (≥3%) o Quota (≥1.70) previsti dal protocollo.")

with tab_players:
    st.markdown("### ⚡ ANALISI STATISTICA GIOCATORI (SOT & FALLI)")
    st.caption("Protocollo Tiri in Porta Giocatori & Falli Serie A: Seleziona squadra e calciatore dalla rosa ufficiale.")
    
    col_pl1, col_pl2 = st.columns(2)
    with col_pl1:
        pl_team = st.selectbox("Seleziona Squadra", sorted(list(SERIE_A_SQUADS.keys())), key="pl_team_sel")
        squad_list = SERIE_A_SQUADS[pl_team]
        player_names = [f"{p['name']} ({p['role']} #{p['number']})" for p in squad_list]
        chosen_p_str = st.selectbox("Seleziona Calciatore", player_names)
        chosen_p_obj = squad_list[player_names.index(chosen_p_str)]
    with col_pl2:
        p_market = st.selectbox("Mercato Giocatore", ["Over 0.5 Tiri in Porta (SOT)", "Over 1.5 Tiri in Porta (SOT)", "Over 1.5 Falli Commessi", "Over 1.5 Falli Subiti"])
        p_quota = st.number_input("Quota Bookmaker Giocatore", min_value=1.01, max_value=30.0, value=1.90, step=0.01)
        p_rigorista = st.checkbox("Rigorista principale in campo (+10% xSOT)")

    base_p90 = chosen_p_obj["sot_90"] if "Tiri" in p_market else chosen_p_obj["fouls_c_90"]
    p_mod_val = base_p90 * (1.10 if p_rigorista else 1.0)
    
    if "0.5" in p_market: p_p_model = float(1.0 - poisson.cdf(0, p_mod_val))
    elif "1.5" in p_market: p_p_model = float(1.0 - poisson.cdf(1, p_mod_val))
    else: p_p_model = 0.55

    p_calc_res = QuantitativeEngine.calculate_metrics(p_p_model, p_quota, current_bankroll)

    st.markdown("---")
    col_pp1, col_pp2, col_pp3 = st.columns(3)
    with col_pp1:
        st.metric("Probabilità Reale Giocatore", f"{p_p_model*100:.1f}%")
        st.metric("Quota Equa", f"{p_calc_res['quota_equa']:.2f}")
    with col_pp2:
        st.metric("Edge Giocatore", f"{p_calc_res['edge']:+.2f}%")
        st.metric("EV", f"{p_calc_res['ev']:+.2f}%")
    with col_pp3:
        st.metric("Stake Consigliato", f"{p_calc_res['stake_pct']}%", f"{p_calc_res['stake_eur']:.2f} €")
        st.metric("Verdetto Giocatore", p_calc_res['verdetto'])

    if p_calc_res['edge'] >= 3.0 and p_quota >= 1.70:
        if st.button("REGISTRA SCOMMESSA GIOCATORE"):
            st.session_state.history_bets.append({
                "id": len(st.session_state.history_bets) + 1,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "match": f"Prop: {chosen_p_obj['name']} ({pl_team})",
                "market": p_market,
                "odds": p_quota,
                "stake": p_calc_res['stake_eur'],
                "ev": p_calc_res['ev'],
                "status": "IN CORSO",
                "profit": 0.0
            })
            st.success("Giocata registrata nel Registro Scommesse!")
            st.rerun()

with tab_injuries:
    st.markdown("### 🏥 GESTIONE INFERMERIA & INDISPONIBILI SERIE A")
    st.caption("Inserisci i calciatori infortunati. L'impatto percentuale aggiornerà automaticamente gli xG.")
    
    col_inj1, col_inj2 = st.columns(2)
    with col_inj1:
        inj_team = st.selectbox("Squadra di Serie A", sorted(list(SERIE_A_SQUADS.keys())), key="inj_team_sel")
        inj_player = st.text_input("Nome Calciatore Indisponibile", placeholder="es. Hakan Calhanoglu")
    with col_inj2:
        inj_imp = st.selectbox(
            "Ruolo ed Impatto Tattico",
            [
                "Top player -10% xG",
                "Attaccante titolare -5% xG",
                "Attaccante riserva",
                "Centrocampista top -5% xG",
                "Centrocampista titolare -2% xG",
                "Centrocampista riserva",
                "Difensore top -5% xGA",
                "Difensore titolare -2% xGA",
                "Difensore riserva",
                "Portiere titolare -5% xGA",
                "Portiere riserva"
            ]
        )
        if st.button("REGISTRA INDISPONIBILE"):
            if inj_team and inj_player:
                st.session_state.injuries_list.append({
                    "team": inj_team, "player": inj_player, "importance": inj_imp
                })
                st.success(f"Indisponibile registrato per {inj_team}.")
                st.rerun()
                
    if st.session_state.injuries_list:
        st.markdown("#### Elenco Attuale Indisponibili")
        df_inj = pd.DataFrame(st.session_state.injuries_list)
        st.dataframe(df_inj, use_container_width=True, hide_index=True)
        if st.button("PULISCI INFERMERIA"):
            st.session_state.injuries_list = []
            st.rerun()
    else:
        st.info("Nessun calciatore registrato in infermeria.")

with tab_register:
    st.markdown("### 📝 REGISTRO OPERATIVO SCOMMESSE")
    st.caption("Storico completo delle giocate effettuate e tracciamento dei profitti.")
    
    if st.session_state.history_bets:
        df_bets = pd.DataFrame(st.session_state.history_bets)
        st.dataframe(df_bets[["created_at", "match", "market", "odds", "stake", "status", "profit"]], use_container_width=True, hide_index=True)
        
        st.markdown("#### Aggiorna Esito Scommessa")
        b_idx = st.selectbox("Seleziona ID Scommessa", range(len(st.session_state.history_bets)), format_func=lambda x: f"#{st.session_state.history_bets[x]['id']} - {st.session_state.history_bets[x]['match']} ({st.session_state.history_bets[x]['market']})")
        
        col_es1, col_es2 = st.columns(2)
        with col_es1:
            new_status = st.selectbox("Esito Finale", ["IN CORSO", "VINTA", "PERSA", "VOID"], key="upd_status_sel")
        with col_es2:
            st.write("")
            st.write("")
            if st.button("AGGIORNA STATO SCOMMESSA"):
                bet_item = st.session_state.history_bets[b_idx]
                bet_item["status"] = new_status
                if new_status == "VINTA":
                    bet_item["profit"] = round((bet_item["odds"] - 1.0) * bet_item["stake"], 2)
                elif new_status == "PERSA":
                    bet_item["profit"] = round(-bet_item["stake"], 2)
                else:
                    bet_item["profit"] = 0.0
                st.success("Stato aggiornato correttamente!")
                st.rerun()
    else:
        st.info("Nessuna scommessa registrata nel registro operativo.")

with tab_kpi:
    st.markdown("### 📈 ANALISI KPI & PERFORMANCE")
    st.markdown(f"""
        - **Capitale Iniziale:** `{initial_bankroll:.2f} €`
        - **Capitale Attuale:** `{current_bankroll:.2f} €`
        - **Profitto Netto:** `{total_profit:+.2f} €`
        - **Yield Operativo:** `{yield_val:+.2f}%`
        - **Totale Scommesse Tracciate:** `{len(st.session_state.history_bets)}`
    """)
