import datetime
import numpy as np
import pandas as pd
import plotly.express as px
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

# DATABASE UFFICIALE E INTEGRALE SERIE A (20 SQUADRE CON TITOLARI E RISERVE)
SERIE_A_SQUADS = {
    "AC Milan": [
        {"name": "Mike Maignan", "role": "Goalkeeper", "number": "16", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Pietro Terracciano", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Lorenzo Torriani", "role": "Goalkeeper", "number": "96", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Strahinja Pavlović", "role": "Defender", "number": "31", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Mario Gila", "role": "Defender", "number": "34", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Koni De Winter", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Davide Bartesaghi", "role": "Defender", "number": "33", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Fikayo Tomori", "role": "Defender", "number": "-", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Matteo Gabbia", "role": "Defender", "number": "46", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Filippo Terracciano", "role": "Defender", "number": "42", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Sankhoun Diawara", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Pervis Estupiñán", "role": "Defender", "number": "2", "sot_90": 0.3, "fouls_c_90": 1.3},
        {"name": "Ardon Jashari", "role": "Midfielder", "number": "30", "sot_90": 0.3, "fouls_c_90": 1.6},
        {"name": "Adrien Rabiot", "role": "Midfielder", "number": "12", "sot_90": 0.8, "fouls_c_90": 1.6},
        {"name": "Yunus Musah", "role": "Midfielder", "number": "80", "sot_90": 0.5, "fouls_c_90": 1.7},
        {"name": "Ruben Loftus-Cheek", "role": "Midfielder", "number": "8", "sot_90": 1.0, "fouls_c_90": 1.4},
        {"name": "Warren Bondo", "role": "Midfielder", "number": "-", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Christian Comotto", "role": "Midfielder", "number": "28", "sot_90": 0.3, "fouls_c_90": 1.0},
        {"name": "Luka Modrić", "role": "Midfielder", "number": "14", "sot_90": 0.9, "fouls_c_90": 1.0},
        {"name": "Christian Pulisic", "role": "Attacker", "number": "11", "sot_90": 1.6, "fouls_c_90": 0.8},
        {"name": "Samuel Chukwueze", "role": "Attacker", "number": "21", "sot_90": 1.4, "fouls_c_90": 0.9},
        {"name": "Alexis Saelemaekers", "role": "Attacker", "number": "56", "sot_90": 1.1, "fouls_c_90": 1.1},
        {"name": "Diego Moreira", "role": "Attacker", "number": "22", "sot_90": 1.0, "fouls_c_90": 0.9},
        {"name": "Alphadjo Cissè", "role": "Attacker", "number": "70", "sot_90": 1.2, "fouls_c_90": 0.8},
        {"name": "Omari Hutchinson", "role": "Attacker", "number": "20", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Gonçalo Ramos", "role": "Attacker", "number": "9", "sot_90": 2.1, "fouls_c_90": 1.4},
        {"name": "Francesco Camarda", "role": "Attacker", "number": "73", "sot_90": 1.5, "fouls_c_90": 1.2}
    ],
    "AC Monza": [
        {"name": "Noel Törnqvist", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Demba Thiam", "role": "Goalkeeper", "number": "20", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Aljaz Strajnar", "role": "Goalkeeper", "number": "43", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Saba Goglichidze", "role": "Defender", "number": "-", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Jan Ziolkowski", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Lorenzo Lucchesi", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Ricardo Mangas", "role": "Defender", "number": "7", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Samuele Birindelli", "role": "Defender", "number": "19", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Andrea Carboni", "role": "Defender", "number": "44", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Eddy Kouadio", "role": "Defender", "number": "60", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Valentin Antov", "role": "Defender", "number": "6", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Yvan Maye", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Adam Bakoune", "role": "Defender", "number": "24", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Leonardo Colombo", "role": "Midfielder", "number": "21", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Ebenezer Akinsanmiro", "role": "Midfielder", "number": "14", "sot_90": 0.4, "fouls_c_90": 1.6},
        {"name": "Matteo Pessina", "role": "Midfielder", "number": "32", "sot_90": 0.6, "fouls_c_90": 1.4},
        {"name": "Michael Folorunsho", "role": "Midfielder", "number": "90", "sot_90": 0.8, "fouls_c_90": 1.8},
        {"name": "Mathis Mout", "role": "Midfielder", "number": "80", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Foe Ondoa", "role": "Midfielder", "number": "8", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Idrissa Touré", "role": "Midfielder", "number": "27", "sot_90": 0.4, "fouls_c_90": 1.5},
        {"name": "Patrick Ciurria", "role": "Midfielder", "number": "26", "sot_90": 0.9, "fouls_c_90": 0.9},
        {"name": "Andrea Colpani", "role": "Midfielder", "number": "28", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Exequiel Zeballos", "role": "Attacker", "number": "-", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Jay Robinson", "role": "Attacker", "number": "46", "sot_90": 1.0, "fouls_c_90": 0.8},
        {"name": "Keita Baldé", "role": "Attacker", "number": "17", "sot_90": 1.2, "fouls_c_90": 1.0},
        {"name": "Cyril Ngonge", "role": "Attacker", "number": "16", "sot_90": 1.4, "fouls_c_90": 1.1},
        {"name": "Omari Forson", "role": "Attacker", "number": "11", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Kevin Martins", "role": "Attacker", "number": "70", "sot_90": 1.0, "fouls_c_90": 0.9},
        {"name": "Gustavo Varela", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.3},
        {"name": "Patrick Cutrone", "role": "Attacker", "number": "10", "sot_90": 1.8, "fouls_c_90": 1.5},
        {"name": "Dany Mota", "role": "Attacker", "number": "47", "sot_90": 1.3, "fouls_c_90": 1.2}
    ],
    "ACF Fiorentina": [
        {"name": "David de Gea", "role": "Goalkeeper", "number": "43", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Oliver Christensen", "role": "Goalkeeper", "number": "53", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Luca Lezzerini", "role": "Goalkeeper", "number": "19", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Radu Drăgușin", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Marin Pongracic", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Luca Ranieri", "role": "Defender", "number": "6", "sot_90": 0.15, "fouls_c_90": 1.4},
        {"name": "Fabiano Parisi", "role": "Defender", "number": "65", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Dodô", "role": "Defender", "number": "2", "sot_90": 0.4, "fouls_c_90": 1.3},
        {"name": "Viery", "role": "Defender", "number": "33", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Víctor Valdepeñas", "role": "Defender", "number": "21", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Álex Jiménez", "role": "Defender", "number": "20", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "João Mário", "role": "Defender", "number": "17", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Christ Inao Oulaï", "role": "Midfielder", "number": "42", "sot_90": 0.4, "fouls_c_90": 1.6},
        {"name": "Arthur Atta", "role": "Midfielder", "number": "14", "sot_90": 0.5, "fouls_c_90": 1.7},
        {"name": "Antonín Barák", "role": "Midfielder", "number": "-", "sot_90": 1.0, "fouls_c_90": 1.1},
        {"name": "Cher Ndour", "role": "Midfielder", "number": "27", "sot_90": 0.6, "fouls_c_90": 1.5},
        {"name": "Nicolò Fagioli", "role": "Midfielder", "number": "44", "sot_90": 0.6, "fouls_c_90": 1.3},
        {"name": "Marco Brescianini", "role": "Midfielder", "number": "4", "sot_90": 0.7, "fouls_c_90": 1.4},
        {"name": "Franco Mastantuono", "role": "Midfielder", "number": "30", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Pedro Gonçalves", "role": "Attacker", "number": "-", "sot_90": 1.5, "fouls_c_90": 0.8},
        {"name": "Riccardo Sottil", "role": "Attacker", "number": "-", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Alieu Njie", "role": "Attacker", "number": "-", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Federico Croci", "role": "Attacker", "number": "70", "sot_90": 1.0, "fouls_c_90": 0.7},
        {"name": "Wilfried Gnonto", "role": "Attacker", "number": "-", "sot_90": 1.4, "fouls_c_90": 1.0},
        {"name": "Mateo Pellegrino", "role": "Attacker", "number": "32", "sot_90": 1.3, "fouls_c_90": 1.2},
        {"name": "Beto", "role": "Attacker", "number": "-", "sot_90": 1.9, "fouls_c_90": 1.6}
    ],
    "AS Roma": [
        {"name": "Mile Svilar", "role": "Goalkeeper", "number": "99", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Devis Vásquez", "role": "Goalkeeper", "number": "-", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Pierluigi Gollini", "role": "Goalkeeper", "number": "95", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Giorgio De Marzi", "role": "Goalkeeper", "number": "70", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Evan Ndicka", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Konstantinos Koulierakis", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Leonardo Balerdi", "role": "Defender", "number": "26", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Daniele Ghilardi", "role": "Defender", "number": "87", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Gianluca Mancini", "role": "Defender", "number": "23", "sot_90": 0.2, "fouls_c_90": 2.0},
        {"name": "Mario Hermoso", "role": "Defender", "number": "22", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Nahuel Molina", "role": "Defender", "number": "20", "sot_90": 0.4, "fouls_c_90": 1.2},
        {"name": "Devyne Rensch", "role": "Defender", "number": "2", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Emanuele Lulli", "role": "Defender", "number": "77", "sot_90": 0.1, "fouls_c_90": 1.0},
        {"name": "Wesley", "role": "Defender", "number": "43", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Anass Salah-Eddine", "role": "Defender", "number": "34", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Bryan Cristante", "role": "Midfielder", "number": "4", "sot_90": 0.5, "fouls_c_90": 1.8},
        {"name": "Manu Koné", "role": "Midfielder", "number": "17", "sot_90": 0.7, "fouls_c_90": 1.9},
        {"name": "Marten de Roon", "role": "Midfielder", "number": "15", "sot_90": 0.3, "fouls_c_90": 1.9},
        {"name": "Niccolò Pisilli", "role": "Midfielder", "number": "61", "sot_90": 0.5, "fouls_c_90": 1.3},
        {"name": "Rodrigo Mora", "role": "Midfielder", "number": "86", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Lorenzo Pellegrini", "role": "Midfielder", "number": "7", "sot_90": 1.2, "fouls_c_90": 1.2},
        {"name": "Matías Soulé", "role": "Attacker", "number": "18", "sot_90": 1.4, "fouls_c_90": 0.7},
        {"name": "Paulo Dybala", "role": "Attacker", "number": "21", "sot_90": 1.8, "fouls_c_90": 0.6},
        {"name": "Santiago Castro", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.4},
        {"name": "Donyell Malen", "role": "Attacker", "number": "14", "sot_90": 2.1, "fouls_c_90": 1.4}
    ],
    "Atalanta": [
        {"name": "Marco Carnesecchi", "role": "Goalkeeper", "number": "29", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Marco Sportiello", "role": "Goalkeeper", "number": "57", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Thomas Pompei", "role": "Goalkeeper", "number": "-", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Giorgio Scalvini", "role": "Defender", "number": "42", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Isak Hien", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.7},
        {"name": "Odilon Kossounou", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Thomas Kristensen", "role": "Defender", "number": "31", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Sead Kolasinac", "role": "Defender", "number": "23", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Davide Zappacosta", "role": "Defender", "number": "77", "sot_90": 0.4, "fouls_c_90": 1.1},
        {"name": "Lorenzo Bernasconi", "role": "Defender", "number": "47", "sot_90": 0.2, "fouls_c_90": 1.0},
        {"name": "Nicola Zalewski", "role": "Defender", "number": "59", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Gianluca Gaetano", "role": "Midfielder", "number": "70", "sot_90": 0.8, "fouls_c_90": 1.1},
        {"name": "Éderson", "role": "Midfielder", "number": "13", "sot_90": 0.7, "fouls_c_90": 1.8},
        {"name": "Franck Kessié", "role": "Midfielder", "number": "19", "sot_90": 0.7, "fouls_c_90": 1.8},
        {"name": "Mario Pašalić", "role": "Midfielder", "number": "8", "sot_90": 0.9, "fouls_c_90": 1.3},
        {"name": "Lazar Samardžić", "role": "Midfielder", "number": "10", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Eljif Elmas", "role": "Midfielder", "number": "99", "sot_90": 1.0, "fouls_c_90": 1.0},
        {"name": "Raoul Bellanova", "role": "Midfielder", "number": "16", "sot_90": 0.6, "fouls_c_90": 1.1},
        {"name": "Charles De Ketelaere", "role": "Attacker", "number": "17", "sot_90": 1.4, "fouls_c_90": 0.8},
        {"name": "Jonathan Rowe", "role": "Attacker", "number": "-", "sot_90": 1.5, "fouls_c_90": 0.9},
        {"name": "Kamaldeen Sulemana", "role": "Attacker", "number": "7", "sot_90": 1.2, "fouls_c_90": 0.8},
        {"name": "Giacomo Raspadori", "role": "Attacker", "number": "18", "sot_90": 1.4, "fouls_c_90": 0.7},
        {"name": "Nikola Krstović", "role": "Attacker", "number": "90", "sot_90": 1.6, "fouls_c_90": 1.5},
        {"name": "Gianluca Scamacca", "role": "Attacker", "number": "9", "sot_90": 2.2, "fouls_c_90": 1.6}
    ],
    "Bologna FC": [
        {"name": "Lukasz Skorupski", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Massimo Pessina", "role": "Goalkeeper", "number": "25", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Ukko Happonen", "role": "Goalkeeper", "number": "77", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Arthur Theate", "role": "Defender", "number": "3", "sot_90": 0.2, "fouls_c_90": 1.5},
        {"name": "Torbjørn Heggem", "role": "Defender", "number": "14", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Martin Vitík", "role": "Defender", "number": "41", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Juan Miranda", "role": "Defender", "number": "33", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Emil Holm", "role": "Defender", "number": "2", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Eivind Helland", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Nicolò Casale", "role": "Defender", "number": "16", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Rahim Alhassane", "role": "Defender", "number": "23", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Nadir Zortea", "role": "Defender", "number": "20", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Lorenzo De Silvestri", "role": "Defender", "number": "29", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Nikola Moro", "role": "Midfielder", "number": "6", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Lewis Ferguson", "role": "Midfielder", "number": "19", "sot_90": 0.9, "fouls_c_90": 1.3},
        {"name": "Jens Odgaard", "role": "Midfielder", "number": "21", "sot_90": 1.0, "fouls_c_90": 0.9},
        {"name": "Oussama El Azzouzi", "role": "Midfielder", "number": "17", "sot_90": 0.3, "fouls_c_90": 1.8},
        {"name": "Tommaso Pobega", "role": "Midfielder", "number": "4", "sot_90": 0.6, "fouls_c_90": 1.9},
        {"name": "Mikel Amondarain", "role": "Midfielder", "number": "8", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Riccardo Orsolini", "role": "Attacker", "number": "7", "sot_90": 1.5, "fouls_c_90": 0.8},
        {"name": "Artem Dovbyk", "role": "Attacker", "number": "9", "sot_90": 2.0, "fouls_c_90": 1.5},
        {"name": "Nicolò Cambiaghi", "role": "Attacker", "number": "28", "sot_90": 1.3, "fouls_c_90": 1.1},
        {"name": "Samuel Mbangula", "role": "Attacker", "number": "11", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Jesper Karlsson", "role": "Attacker", "number": "-", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Federico Bernardeschi", "role": "Attacker", "number": "10", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Roberto Piccoli", "role": "Attacker", "number": "91", "sot_90": 1.5, "fouls_c_90": 1.8}
    ],
    "Cagliari Calcio": [
        {"name": "Elia Caprile", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Alen Sherri", "role": "Goalkeeper", "number": "12", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Boris Radunović", "role": "Goalkeeper", "number": "23", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Juan Rodríguez", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Raphael Kofler", "role": "Defender", "number": "22", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Zé Pedro", "role": "Defender", "number": "2", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Adam Obert", "role": "Defender", "number": "33", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Yukinari Sugawara", "role": "Defender", "number": "-", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Yerry Mina", "role": "Defender", "number": "26", "sot_90": 0.1, "fouls_c_90": 2.1},
        {"name": "Riyad Idrissi", "role": "Defender", "number": "3", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Giuseppe Aurelio", "role": "Defender", "number": "24", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Harry Winks", "role": "Midfielder", "number": "6", "sot_90": 0.2, "fouls_c_90": 1.5},
        {"name": "Jacopo Fazzini", "role": "Midfielder", "number": "10", "sot_90": 0.9, "fouls_c_90": 1.1},
        {"name": "Alessandro Romano", "role": "Midfielder", "number": "4", "sot_90": 0.3, "fouls_c_90": 1.3},
        {"name": "Michel Adopo", "role": "Midfielder", "number": "8", "sot_90": 0.4, "fouls_c_90": 1.7},
        {"name": "Joseph Liteta", "role": "Midfielder", "number": "27", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Alessandro Deiola", "role": "Midfielder", "number": "14", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Roberto Gagliardini", "role": "Midfielder", "number": "-", "sot_90": 0.4, "fouls_c_90": 1.9},
        {"name": "Daniel Maldini", "role": "Attacker", "number": "70", "sot_90": 1.2, "fouls_c_90": 0.7},
        {"name": "Alieu Fadera", "role": "Attacker", "number": "39", "sot_90": 1.0, "fouls_c_90": 1.1},
        {"name": "Kevin Carlos", "role": "Attacker", "number": "9", "sot_90": 1.6, "fouls_c_90": 1.5},
        {"name": "Mattia Felici", "role": "Attacker", "number": "17", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "Riccardo Ciervo", "role": "Attacker", "number": "20", "sot_90": 1.0, "fouls_c_90": 0.8},
        {"name": "Gennaro Borrelli", "role": "Attacker", "number": "29", "sot_90": 1.4, "fouls_c_90": 1.6}
    ],
    "Como 1907": [
        {"name": "Jean Butez", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Robert Sánchez", "role": "Goalkeeper", "number": "-", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Mauro Vigorito", "role": "Goalkeeper", "number": "22", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Trevoh Chalobah", "role": "Defender", "number": "99", "sot_90": 0.15, "fouls_c_90": 1.4},
        {"name": "Jacobo Ramón", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Alberto Dossena", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Marc Oliver Kempf", "role": "Defender", "number": "2", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Willy Kambwala", "role": "Defender", "number": "53", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Edoardo Goldaniga", "role": "Defender", "number": "18", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Álex Valle", "role": "Defender", "number": "3", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Yan Couto", "role": "Defender", "number": "27", "sot_90": 0.4, "fouls_c_90": 1.3},
        {"name": "Ivan Smolcic", "role": "Defender", "number": "28", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Máximo Perrone", "role": "Midfielder", "number": "5", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Samuele Ricci", "role": "Midfielder", "number": "14", "sot_90": 0.4, "fouls_c_90": 1.6},
        {"name": "Maxence Caqueret", "role": "Midfielder", "number": "8", "sot_90": 0.5, "fouls_c_90": 1.3},
        {"name": "Luis Milla", "role": "Midfielder", "number": "6", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Luca Mazzitelli", "role": "Midfielder", "number": "-", "sot_90": 0.6, "fouls_c_90": 1.7},
        {"name": "Luscas Da Cunha", "role": "Midfielder", "number": "7", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "Nico Paz", "role": "Midfielder", "number": "10", "sot_90": 1.4, "fouls_c_90": 0.8},
        {"name": "Martin Baturina", "role": "Midfielder", "number": "20", "sot_90": 1.1, "fouls_c_90": 0.7},
        {"name": "Assane Diao", "role": "Attacker", "number": "11", "sot_90": 1.4, "fouls_c_90": 0.9},
        {"name": "Anastasios Douvikas", "role": "Attacker", "number": "9", "sot_90": 1.7, "fouls_c_90": 1.3},
        {"name": "Moise Kean", "role": "Attacker", "number": "-", "sot_90": 2.0, "fouls_c_90": 1.7}
    ],
    "Frosinone Calcio": [
        {"name": "Lorenzo Palmisani", "role": "Goalkeeper", "number": "22", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Sebastiano Desplanches", "role": "Goalkeeper", "number": "91", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Matteo Pisseri", "role": "Goalkeeper", "number": "12", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Gabriele Calvani", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Ilario Monterisi", "role": "Defender", "number": "30", "sot_90": 0.15, "fouls_c_90": 1.3},
        {"name": "Kevin Akpoguma", "role": "Defender", "number": "25", "sot_90": 0.1, "fouls_c_90": 1.7},
        {"name": "Giorgio Cittadini", "role": "Defender", "number": "2", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Wisdom Amey", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Omar Fayed", "role": "Defender", "number": "74", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Aleksa Terzić", "role": "Defender", "number": "71", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Enzo Tchato", "role": "Defender", "number": "90", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Gabriele Bracaglia", "role": "Defender", "number": "79", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Giacomo Calò", "role": "Midfielder", "number": "14", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Florian Grillitsch", "role": "Midfielder", "number": "27", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Matteo Cichella", "role": "Midfielder", "number": "16", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Luis Hasa", "role": "Midfielder", "number": "70", "sot_90": 0.8, "fouls_c_90": 1.1},
        {"name": "Ilias Koutsoupias", "role": "Midfielder", "number": "8", "sot_90": 0.5, "fouls_c_90": 1.7},
        {"name": "Romano Schmid", "role": "Midfielder", "number": "10", "sot_90": 1.0, "fouls_c_90": 1.1},
        {"name": "Seydou Fini", "role": "Attacker", "number": "40", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "Alessio Zerbin", "role": "Attacker", "number": "24", "sot_90": 1.2, "fouls_c_90": 1.0},
        {"name": "Giorgi Kvernadze", "role": "Attacker", "number": "17", "sot_90": 1.2, "fouls_c_90": 1.0},
        {"name": "Antonio Raimondo", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.4},
        {"name": "Daniel Bîrligea", "role": "Attacker", "number": "11", "sot_90": 1.4, "fouls_c_90": 1.3}
    ],
    "Genoa CFC": [
        {"name": "Justin Bijlow", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Franz Stolz", "role": "Goalkeeper", "number": "99", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Daniele Sommariva", "role": "Goalkeeper", "number": "39", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Alessandro Marcandalli", "role": "Defender", "number": "27", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Leo Østigård", "role": "Defender", "number": "5", "sot_90": 0.2, "fouls_c_90": 1.8},
        {"name": "Johan Vásquez", "role": "Defender", "number": "22", "sot_90": 0.2, "fouls_c_90": 1.6},
        {"name": "Sebastian Otoa", "role": "Defender", "number": "34", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Mamedi Doucouré", "role": "Defender", "number": "74", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Mario Mitaj", "role": "Defender", "number": "2", "sot_90": 0.2, "fouls_c_90": 1.1},
        {"name": "Cody Drameh", "role": "Defender", "number": "-", "sot_90": 0.3, "fouls_c_90": 1.3},
        {"name": "Stefano Sabelli", "role": "Defender", "number": "20", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Djibril Sow", "role": "Midfielder", "number": "97", "sot_90": 0.5, "fouls_c_90": 1.7},
        {"name": "Morten Frendrup", "role": "Midfielder", "number": "32", "sot_90": 0.4, "fouls_c_90": 2.2},
        {"name": "Mikael Egill Ellertsson", "role": "Midfielder", "number": "77", "sot_90": 0.6, "fouls_c_90": 1.4},
        {"name": "Tommaso Baldanzi", "role": "Midfielder", "number": "8", "sot_90": 1.1, "fouls_c_90": 0.8},
        {"name": "Junior Messias", "role": "Midfielder", "number": "10", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Vitinha", "role": "Attacker", "number": "9", "sot_90": 1.4, "fouls_c_90": 1.1},
        {"name": "Lorenzo Colombo", "role": "Attacker", "number": "29", "sot_90": 1.6, "fouls_c_90": 1.5},
        {"name": "Milutin Osmajic", "role": "Attacker", "number": "18", "sot_90": 1.5, "fouls_c_90": 1.7}
    ],
    "Inter": [
        {"name": "Josep Martínez", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Ivan Provedel", "role": "Goalkeeper", "number": "49", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Raffaele Di Gennaro", "role": "Goalkeeper", "number": "12", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Manuel Akanji", "role": "Defender", "number": "25", "sot_90": 0.15, "fouls_c_90": 1.1},
        {"name": "John Stones", "role": "Defender", "number": "6", "sot_90": 0.1, "fouls_c_90": 0.9},
        {"name": "Alessandro Bastoni", "role": "Defender", "number": "95", "sot_90": 0.15, "fouls_c_90": 0.9},
        {"name": "Yann Bisseck", "role": "Defender", "number": "31", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Benjamin Pavard", "role": "Defender", "number": "28", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Carlos Augusto", "role": "Defender", "number": "30", "sot_90": 0.3, "fouls_c_90": 1.0},
        {"name": "Federico Dimarco", "role": "Defender", "number": "32", "sot_90": 1.0, "fouls_c_90": 0.8},
        {"name": "Djed Spence", "role": "Defender", "number": "99", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Aleksandar Stanković", "role": "Midfielder", "number": "5", "sot_90": 0.3, "fouls_c_90": 1.4},
        {"name": "Hakan Çalhanoğlu", "role": "Midfielder", "number": "20", "sot_90": 1.1, "fouls_c_90": 1.5},
        {"name": "Nicolò Barella", "role": "Midfielder", "number": "23", "sot_90": 0.8, "fouls_c_90": 1.4},
        {"name": "Petar Sučić", "role": "Midfielder", "number": "8", "sot_90": 0.6, "fouls_c_90": 1.3},
        {"name": "Curtis Jones", "role": "Midfielder", "number": "21", "sot_90": 0.7, "fouls_c_90": 1.3},
        {"name": "Piotr Zielinski", "role": "Midfielder", "number": "7", "sot_90": 0.8, "fouls_c_90": 1.0},
        {"name": "Henrikh Mkhitaryan", "role": "Midfielder", "number": "22", "sot_90": 0.9, "fouls_c_90": 1.2},
        {"name": "Andy Diouf", "role": "Midfielder", "number": "17", "sot_90": 0.4, "fouls_c_90": 1.2},
        {"name": "Luis Henrique", "role": "Midfielder", "number": "11", "sot_90": 0.9, "fouls_c_90": 0.9},
        {"name": "Lautaro Martínez", "role": "Attacker", "number": "10", "sot_90": 2.2, "fouls_c_90": 1.6},
        {"name": "Marcus Thuram", "role": "Attacker", "number": "9", "sot_90": 1.8, "fouls_c_90": 1.3},
        {"name": "Pio Esposito", "role": "Attacker", "number": "94", "sot_90": 1.3, "fouls_c_90": 1.1},
        {"name": "Ange-Yoan Bonny", "role": "Attacker", "number": "14", "sot_90": 1.4, "fouls_c_90": 1.5}
    ],
    "Juventus FC": [
        {"name": "Guglielmo Vicario", "role": "Goalkeeper", "number": "25", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Kamil Grabara", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Carlo Pinsoglio", "role": "Goalkeeper", "number": "23", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Pierre Kalulu", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Bremer", "role": "Defender", "number": "3", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Jhon Lucumí", "role": "Defender", "number": "26", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Zeki Çelik", "role": "Defender", "number": "2", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Federico Gatti", "role": "Defender", "number": "4", "sot_90": 0.2, "fouls_c_90": 1.6},
        {"name": "Daniele Rugani", "role": "Defender", "number": "24", "sot_90": 0.1, "fouls_c_90": 1.1},
        {"name": "Juan Cabal", "role": "Defender", "number": "32", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Andrea Cambiaso", "role": "Defender", "number": "20", "sot_90": 0.7, "fouls_c_90": 1.2},
        {"name": "Lloyd Kelly", "role": "Defender", "number": "6", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Douglas Luiz", "role": "Midfielder", "number": "12", "sot_90": 0.7, "fouls_c_90": 1.6},
        {"name": "Manuel Locatelli", "role": "Midfielder", "number": "5", "sot_90": 0.4, "fouls_c_90": 1.7},
        {"name": "Khéphren Thuram", "role": "Midfielder", "number": "19", "sot_90": 0.6, "fouls_c_90": 1.5},
        {"name": "Weston McKennie", "role": "Midfielder", "number": "22", "sot_90": 0.9, "fouls_c_90": 1.5},
        {"name": "Teun Koopmeiners", "role": "Midfielder", "number": "8", "sot_90": 1.4, "fouls_c_90": 1.0},
        {"name": "Pape Matar Sarr", "role": "Midfielder", "number": "29", "sot_90": 0.5, "fouls_c_90": 1.4},
        {"name": "Francisco Conceição", "role": "Attacker", "number": "7", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Kenan Yıldız", "role": "Attacker", "number": "10", "sot_90": 1.3, "fouls_c_90": 0.8},
        {"name": "Nico González", "role": "Attacker", "number": "31", "sot_90": 1.4, "fouls_c_90": 1.0},
        {"name": "Edon Zhegrova", "role": "Attacker", "number": "11", "sot_90": 1.3, "fouls_c_90": 0.8},
        {"name": "Randal Kolo Muani", "role": "Attacker", "number": "9", "sot_90": 2.0, "fouls_c_90": 1.5},
        {"name": "Nick Woltemade", "role": "Attacker", "number": "27", "sot_90": 1.7, "fouls_c_90": 1.3},
        {"name": "Arkadiusz Milik", "role": "Attacker", "number": "14", "sot_90": 1.5, "fouls_c_90": 1.4}
    ],
    "Parma Calcio": [
        {"name": "Edoardo Corvi", "role": "Goalkeeper", "number": "40", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Giovanni Daffara", "role": "Goalkeeper", "number": "30", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Simone Ghidotti", "role": "Goalkeeper", "number": "-", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Enrico Delprato", "role": "Defender", "number": "15", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Mariano Troilo", "role": "Defender", "number": "37", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Diego Carlos", "role": "Defender", "number": "-", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Emanuele Valeri", "role": "Defender", "number": "14", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Abdoulaye Ndiaye", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Lautaro Valenti", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Franco Carboni", "role": "Defender", "number": "29", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Mandela Keita", "role": "Midfielder", "number": "16", "sot_90": 0.3, "fouls_c_90": 2.0},
        {"name": "Adrián Bernabé", "role": "Midfielder", "number": "10", "sot_90": 0.7, "fouls_c_90": 1.0},
        {"name": "Giovanni Fabbian", "role": "Midfielder", "number": "80", "sot_90": 0.9, "fouls_c_90": 1.0},
        {"name": "Hans Nicolussi Caviglia", "role": "Midfielder", "number": "41", "sot_90": 0.4, "fouls_c_90": 1.6},
        {"name": "Benja Cremaschi", "role": "Midfielder", "number": "25", "sot_90": 0.5, "fouls_c_90": 1.2},
        {"name": "Simone Lontani", "role": "Attacker", "number": "76", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "David Romero", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.4},
        {"name": "El Bilal Touré", "role": "Attacker", "number": "19", "sot_90": 1.7, "fouls_c_90": 1.2},
        {"name": "Pontus Almqvist", "role": "Attacker", "number": "11", "sot_90": 1.2, "fouls_c_90": 0.8},
        {"name": "Matija Frigan", "role": "Attacker", "number": "20", "sot_90": 1.4, "fouls_c_90": 1.3}
    ],
    "SS Lazio": [
        {"name": "Christos Mandas", "role": "Goalkeeper", "number": "35", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Edoardo Motta", "role": "Goalkeeper", "number": "40", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Alessio Furlanetto", "role": "Goalkeeper", "number": "55", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Adam Marusic", "role": "Defender", "number": "77", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Josip Sutalo", "role": "Defender", "number": "37", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Danilho Doekhi", "role": "Defender", "number": "5", "sot_90": 0.15, "fouls_c_90": 1.5},
        {"name": "Alfonso Pedraza", "role": "Defender", "number": "23", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Oliver Provstgaard", "role": "Defender", "number": "25", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Alessio Romagnoli", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.2},
        {"name": "Patric", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Nuno Tavares", "role": "Defender", "number": "17", "sot_90": 0.5, "fouls_c_90": 1.3},
        {"name": "Manuel Lazzari", "role": "Defender", "number": "29", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Kenneth Taylor", "role": "Midfielder", "number": "24", "sot_90": 0.8, "fouls_c_90": 1.4},
        {"name": "Nicolò Rovella", "role": "Midfielder", "number": "6", "sot_90": 0.2, "fouls_c_90": 1.6},
        {"name": "Davide Frattesi", "role": "Midfielder", "number": "16", "sot_90": 1.0, "fouls_c_90": 1.5},
        {"name": "Fisayo Dele-Bashiru", "role": "Midfielder", "number": "7", "sot_90": 0.6, "fouls_c_90": 1.4},
        {"name": "Danilo Cataldi", "role": "Midfielder", "number": "32", "sot_90": 0.3, "fouls_c_90": 1.6},
        {"name": "Gustav Isaksen", "role": "Attacker", "number": "11", "sot_90": 1.1, "fouls_c_90": 0.7},
        {"name": "Andrea Pinamonti", "role": "Attacker", "number": "9", "sot_90": 1.8, "fouls_c_90": 1.5},
        {"name": "Mattia Zaccagni", "role": "Attacker", "number": "10", "sot_90": 1.4, "fouls_c_90": 1.5},
        {"name": "Tijjani Noslin", "role": "Attacker", "number": "14", "sot_90": 1.2, "fouls_c_90": 1.1},
        {"name": "Matteo Cancellieri", "role": "Attacker", "number": "22", "sot_90": 1.0, "fouls_c_90": 0.9}
    ],
    "SSC Napoli": [
        {"name": "Alex Meret", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Vanja Milinković-Savić", "role": "Goalkeeper", "number": "32", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Nikita Contini", "role": "Goalkeeper", "number": "14", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Giovanni Di Lorenzo", "role": "Defender", "number": "22", "sot_90": 0.5, "fouls_c_90": 1.1},
        {"name": "Amir Rrahmani", "role": "Defender", "number": "13", "sot_90": 0.1, "fouls_c_90": 1.0},
        {"name": "Alessandro Buongiorno", "role": "Defender", "number": "4", "sot_90": 0.15, "fouls_c_90": 1.4},
        {"name": "Benoît Badiashile", "role": "Defender", "number": "5", "sot_90": 0.15, "fouls_c_90": 1.3},
        {"name": "Rafa Marín", "role": "Defender", "number": "16", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Leonardo Spinazzola", "role": "Defender", "number": "37", "sot_90": 0.4, "fouls_c_90": 1.0},
        {"name": "Mathías Olivera", "role": "Defender", "number": "17", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Kevin De Bruyne", "role": "Midfielder", "number": "11", "sot_90": 1.5, "fouls_c_90": 0.8},
        {"name": "Stanislav Lobotka", "role": "Midfielder", "number": "68", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Scott McTominay", "role": "Midfielder", "number": "8", "sot_90": 1.3, "fouls_c_90": 1.5},
        {"name": "Billy Gilmour", "role": "Midfielder", "number": "6", "sot_90": 0.2, "fouls_c_90": 1.4},
        {"name": "Frank Anguissa", "role": "Midfielder", "number": "99", "sot_90": 0.6, "fouls_c_90": 1.6},
        {"name": "Matteo Politano", "role": "Attacker", "number": "21", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "David Neres", "role": "Attacker", "number": "7", "sot_90": 1.4, "fouls_c_90": 0.8},
        {"name": "Noa Lang", "role": "Attacker", "number": "70", "sot_90": 1.3, "fouls_c_90": 0.9},
        {"name": "Rasmus Højlund", "role": "Attacker", "number": "19", "sot_90": 2.2, "fouls_c_90": 1.6},
        {"name": "Alisson Santos", "role": "Attacker", "number": "27", "sot_90": 1.4, "fouls_c_90": 0.9},
        {"name": "Lorenzo Lucca", "role": "Attacker", "number": "20", "sot_90": 1.6, "fouls_c_90": 1.7}
    ],
    "Torino FC": [
        {"name": "Lucas Perri", "role": "Goalkeeper", "number": "20", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Franco Israel", "role": "Goalkeeper", "number": "81", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Alberto Paleari", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Diego Mascardi", "role": "Goalkeeper", "number": "26", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Pietro Comuzzo", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Saúl Coco", "role": "Defender", "number": "23", "sot_90": 0.2, "fouls_c_90": 1.5},
        {"name": "Eray Cömert", "role": "Defender", "number": "5", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Rafik Belghali", "role": "Defender", "number": "-", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Cristiano Biraghi", "role": "Defender", "number": "3", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Rolando Mandragora", "role": "Midfielder", "number": "-", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Kian Fitz-Jim", "role": "Midfielder", "number": "28", "sot_90": 0.5, "fouls_c_90": 1.3},
        {"name": "Alessio Cacciamani", "role": "Midfielder", "number": "77", "sot_90": 0.4, "fouls_c_90": 1.1},
        {"name": "Cesare Casadei", "role": "Midfielder", "number": "22", "sot_90": 0.8, "fouls_c_90": 1.4},
        {"name": "Gvidas Gineitis", "role": "Midfielder", "number": "66", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Tino Anjorin", "role": "Midfielder", "number": "14", "sot_90": 0.4, "fouls_c_90": 1.3},
        {"name": "Nikola Vlašić", "role": "Attacker", "number": "10", "sot_90": 1.1, "fouls_c_90": 0.9},
        {"name": "Gaetano Oristanio", "role": "Attacker", "number": "11", "sot_90": 1.2, "fouls_c_90": 0.8},
        {"name": "Giovanni Simeone", "role": "Attacker", "number": "18", "sot_90": 1.7, "fouls_c_90": 1.5},
        {"name": "Duván Zapata", "role": "Attacker", "number": "91", "sot_90": 2.0, "fouls_c_90": 1.7},
        {"name": "Pietro Pellegri", "role": "Attacker", "number": "9", "sot_90": 1.4, "fouls_c_90": 1.6}
    ],
    "US Lecce": [
        {"name": "Wladimiro Falcone", "role": "Goalkeeper", "number": "30", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Marco Bleve", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Danilo Veiga", "role": "Defender", "number": "17", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Tiago Gabriel", "role": "Defender", "number": "44", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Gaspar", "role": "Defender", "number": "4", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Antonino Gallo", "role": "Defender", "number": "25", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Gaby Jean", "role": "Defender", "number": "18", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Corrie Ndaba", "role": "Defender", "number": "3", "sot_90": 0.2, "fouls_c_90": 1.3},
        {"name": "Ali Dembélé", "role": "Defender", "number": "2", "sot_90": 0.2, "fouls_c_90": 1.2},
        {"name": "Lassana Coulibaly", "role": "Midfielder", "number": "29", "sot_90": 0.4, "fouls_c_90": 1.9},
        {"name": "Ivan Ilić", "role": "Midfielder", "number": "20", "sot_90": 0.5, "fouls_c_90": 1.6},
        {"name": "Olaf Gorter", "role": "Midfielder", "number": "28", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Mohamed Kaba", "role": "Midfielder", "number": "77", "sot_90": 0.4, "fouls_c_90": 1.7},
        {"name": "Youssef Maleh", "role": "Midfielder", "number": "14", "sot_90": 0.5, "fouls_c_90": 1.6},
        {"name": "Medon Berisha", "role": "Midfielder", "number": "10", "sot_90": 0.8, "fouls_c_90": 1.1},
        {"name": "Santiago Pierotti", "role": "Attacker", "number": "50", "sot_90": 0.9, "fouls_c_90": 1.2},
        {"name": "Willem Geubbels", "role": "Attacker", "number": "69", "sot_90": 1.7, "fouls_c_90": 1.4},
        {"name": "Joël Monteiro", "role": "Attacker", "number": "99", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Konan N'Dri", "role": "Attacker", "number": "11", "sot_90": 1.3, "fouls_c_90": 1.0},
        {"name": "Nikola Stulic", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.5}
    ],
    "US Sassuolo": [
        {"name": "Arijanet Murić", "role": "Goalkeeper", "number": "49", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Stefano Turati", "role": "Goalkeeper", "number": "80", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Giacomo Satalino", "role": "Goalkeeper", "number": "12", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Ignace Van der Brempt", "role": "Defender", "number": "-", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Jay Idzes", "role": "Defender", "number": "21", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Fedde Leysen", "role": "Defender", "number": "16", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Rafa Obrador", "role": "Defender", "number": "33", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Cas Odenthal", "role": "Defender", "number": "26", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Josh Doig", "role": "Defender", "number": "3", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Sebastian Walukiewicz", "role": "Defender", "number": "6", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Nemanja Matić", "role": "Midfielder", "number": "18", "sot_90": 0.3, "fouls_c_90": 2.1},
        {"name": "Darryl Bakola", "role": "Midfielder", "number": "50", "sot_90": 0.4, "fouls_c_90": 1.4},
        {"name": "Daniel Boloca", "role": "Midfielder", "number": "11", "sot_90": 0.3, "fouls_c_90": 1.8},
        {"name": "Kristian Thorstvedt", "role": "Midfielder", "number": "42", "sot_90": 0.9, "fouls_c_90": 1.4},
        {"name": "Andrea Ghion", "role": "Midfielder", "number": "8", "sot_90": 0.2, "fouls_c_90": 1.5},
        {"name": "Domenico Berardi", "role": "Attacker", "number": "10", "sot_90": 1.9, "fouls_c_90": 0.7},
        {"name": "Armand Laurienté", "role": "Attacker", "number": "45", "sot_90": 1.5, "fouls_c_90": 1.0},
        {"name": "Sebastiano Esposito", "role": "Attacker", "number": "-", "sot_90": 1.6, "fouls_c_90": 1.3},
        {"name": "Cristian Volpato", "role": "Attacker", "number": "7", "sot_90": 1.2, "fouls_c_90": 0.9},
        {"name": "Nicholas Pierini", "role": "Attacker", "number": "77", "sot_90": 1.1, "fouls_c_90": 0.8}
    ],
    "Udinese Calcio": [
        {"name": "Maduka Okoye", "role": "Goalkeeper", "number": "40", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Bartosz Mrozek", "role": "Goalkeeper", "number": "41", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Daniele Padelli", "role": "Goalkeeper", "number": "93", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "James Abankwah", "role": "Defender", "number": "14", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Christian Kabasele", "role": "Defender", "number": "27", "sot_90": 0.1, "fouls_c_90": 1.6},
        {"name": "Oumar Solet", "role": "Defender", "number": "28", "sot_90": 0.2, "fouls_c_90": 1.4},
        {"name": "Mërgim Vojvoda", "role": "Defender", "number": "23", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Enzo Ebosse", "role": "Defender", "number": "77", "sot_90": 0.1, "fouls_c_90": 1.5},
        {"name": "Hassane Kamara", "role": "Defender", "number": "11", "sot_90": 0.4, "fouls_c_90": 1.2},
        {"name": "Alessandro Zanoli", "role": "Defender", "number": "59", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Jakub Piotrowski", "role": "Midfielder", "number": "24", "sot_90": 0.5, "fouls_c_90": 1.6},
        {"name": "Jesper Karlström", "role": "Midfielder", "number": "8", "sot_90": 0.2, "fouls_c_90": 2.0},
        {"name": "Jurgen Ekkelenkamp", "role": "Midfielder", "number": "32", "sot_90": 0.8, "fouls_c_90": 1.3},
        {"name": "Sandi Lovrić", "role": "Midfielder", "number": "4", "sot_90": 0.7, "fouls_c_90": 1.4},
        {"name": "Oier Zarraga", "role": "Midfielder", "number": "6", "sot_90": 0.3, "fouls_c_90": 1.5},
        {"name": "Lennon Miller", "role": "Midfielder", "number": "38", "sot_90": 0.4, "fouls_c_90": 1.2},
        {"name": "Nicolò Zaniolo", "role": "Attacker", "number": "10", "sot_90": 1.6, "fouls_c_90": 1.5},
        {"name": "Lazar Jovanovic", "role": "Attacker", "number": "91", "sot_90": 1.2, "fouls_c_90": 0.8},
        {"name": "Keinan Davis", "role": "Attacker", "number": "9", "sot_90": 1.8, "fouls_c_90": 1.7},
        {"name": "Vakoun Bayo", "role": "Attacker", "number": "15", "sot_90": 1.4, "fouls_c_90": 1.6}
    ],
    "Venezia FC": [
        {"name": "Filip Stanković", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Lorenzo Montipò", "role": "Goalkeeper", "number": "96", "sot_90": 0.0, "fouls_c_90": 0.0},
        {"name": "Joël Schingtienne", "role": "Defender", "number": "3", "sot_90": 0.1, "fouls_c_90": 1.3},
        {"name": "Armel Bella-Kotchap", "role": "Defender", "number": "17", "sot_90": 0.15, "fouls_c_90": 1.5},
        {"name": "Juan Jesus", "role": "Defender", "number": "15", "sot_90": 0.1, "fouls_c_90": 1.4},
        {"name": "Antoine Hainaut", "role": "Defender", "number": "18", "sot_90": 0.3, "fouls_c_90": 1.2},
        {"name": "Ridgeciano Haps", "role": "Defender", "number": "5", "sot_90": 0.3, "fouls_c_90": 1.1},
        {"name": "Thierry Correia", "role": "Defender", "number": "14", "sot_90": 0.3, "fouls_c_90": 1.3},
        {"name": "Thórir Jóhann Helgason", "role": "Midfielder", "number": "21", "sot_90": 0.4, "fouls_c_90": 1.6},
        {"name": "Gianluca Busio", "role": "Midfielder", "number": "6", "sot_90": 0.5, "fouls_c_90": 1.2},
        {"name": "Toma Bašić", "role": "Midfielder", "number": "26", "sot_90": 0.6, "fouls_c_90": 1.5},
        {"name": "Alfred Duncan", "role": "Midfielder", "number": "32", "sot_90": 0.4, "fouls_c_90": 1.8},
        {"name": "Simon Sohm", "role": "Midfielder", "number": "19", "sot_90": 0.8, "fouls_c_90": 1.3},
        {"name": "John Yeboah", "role": "Attacker", "number": "10", "sot_90": 1.4, "fouls_c_90": 0.8},
        {"name": "Albion Rrahmani", "role": "Attacker", "number": "7", "sot_90": 1.7, "fouls_c_90": 1.3},
        {"name": "Andrea Adorante", "role": "Attacker", "number": "9", "sot_90": 1.5, "fouls_c_90": 1.4}
    ]
}

# Inizializzazione Stato
if "history_bets" not in st.session_state:
    st.session_state.history_bets = []
if "injuries_list" not in st.session_state:
    st.session_state.injuries_list = []
if "saved_bets_pool" not in st.session_state:
    st.session_state.saved_bets_pool = []

# Sidebar
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

tab_analyzer, tab_combo, tab_players, tab_injuries, tab_register, tab_kpi = st.tabs([
    "🎯 Analisi Squadre & Match",
    "🔗 Schedine Multiple (Combo)",
    "⚡ Statistiche Giocatori (SOT & Falli)",
    "🏥 Gestione Infermeria",
    "📝 Registro Scommesse",
    "📈 KPI & Grafico Bankroll"
])

class QuantitativeEngine:
    @staticmethod
    def calculate_metrics(p_reale, quota_book, bankroll):
        if p_reale <= 0.0 or quota_book <= 1.0:
            return {
                "p_imp": 0.0, "edge": 0.0, "ev": 0.0, "quota_equa": 99.0,
                "kelly_half": 0.0, "stake_pct": 0.0, "stake_eur": 0.0, "verdetto": "NO BET❌"
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
        
        verdetto = "VALUE BET✅" if edge >= 0.03 and ev > 0 and quota_book >= 1.70 else "NO BET❌"
        
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
    
    D_PEN_HOME = pen_home
    D_PEN_AWAY = pen_away
    
    if D_PEN_HOME > 0 or D_PEN_AWAY > 0:
        st.info(f"🏥 Impatto Infermeria rilevato dal modello -> Penalità xG applicata: {home_team} (-{D_PEN_HOME*100:.0f}%), {away_team} (-{D_PEN_AWAY*100:.0f}%)")

    if "⚽ Gol" in market_category:
        st.markdown("#### 📊 PARAMETRI GOL & EXPECTED GOALS (xG)")
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1: xg_home_raw = st.number_input("xG Base Casa (ultime 8)", min_value=0.1, max_value=5.0, value=1.65, step=0.05)
        with col_st2: xg_away_raw = st.number_input("xG Base Trasferta (ultime 8)", min_value=0.1, max_value=5.0, value=1.15, step=0.05)
        with col_st3: conf_level = st.selectbox("Confidenza Modello", ["ALTA", "MEDIA", "BASSA"], index=0)
        
        xg_home = max(0.1, xg_home_raw * (1.0 - D_PEN_HOME))
        xg_away = max(0.1, xg_away_raw * (1.0 - D_PEN_AWAY))
        
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
        with col_c2: cross_vol = st.number_input("Volume Cross / Gara (Correzione +8% se >20)", min_value=1.0, max_value=35.0, value=19.0, step=1.0)
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
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if calc_res['verdetto'] == "VALUE BET✅":
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
            
    with col_act2:
        if st.button("➕ AGGIUNGI ALLA POOL PER SCHEDINA MULTIPLA (COMBO)"):
            st.session_state.saved_bets_pool.append({
                "label": f"{home_team} vs {away_team} - {exact_market_name or market_category}",
                "prob": p_model,
                "quota": quota_bk
            })
            st.success("Analisi aggiunta alla pool delle Multiple!")

with tab_combo:
    st.markdown("### 🔗 MODULO SCHEDINE MULTIPLE (COMBO)")
    st.caption("Seleziona due o più eventi salvati dalla pool di analisi per calcolare probabilità congiunta, quota totale e Kelly Mezzato.")
    
    if st.session_state.saved_bets_pool:
        pool_options = [f"{b['label']} (Q: {b['quota']} | P: {b['prob']*100:.1f}%)" for b in st.session_state.saved_bets_pool]
        selected_combo = st.multiselect("Seleziona Eventi per la Multipla", pool_options)
        
        if selected_combo:
            total_combo_odds = 1.0
            total_combo_prob = 1.0
            for item in selected_combo:
                idx = pool_options.index(item)
                b_obj = st.session_state.saved_bets_pool[idx]
                total_combo_odds *= b_obj["quota"]
                total_combo_prob *= b_obj["prob"]
                
            combo_res = QuantitativeEngine.calculate_metrics(total_combo_prob, total_combo_odds, current_bankroll)
            
            st.markdown("---")
            st.markdown("#### 📋 RISULTATO MULTIPLA CONGIUNTA")
            cc1, cc2, cc3 = st.columns(3)
            with cc1:
                st.metric("Probabilità Congiunta", f"{total_combo_prob*100:.2f}%")
                st.metric("Quota Totale Schedina", f"{total_combo_odds:.2f}")
            with cc2:
                st.metric("Edge Schedina", f"{combo_res['edge']:+.2f}%")
                st.metric("Valore Atteso (EV)", f"{combo_res['ev']:+.2f}%")
            with cc3:
                st.metric("Stake Consigliato (Kelly/2)", f"{combo_res['stake_pct']}%", f"{combo_res['stake_eur']:.2f} €")
                st.metric("Verdetto Multipla", combo_res['verdetto'])
                
            if st.button("REGISTRA MULTIPLA NEL REGISTRO"):
                st.session_state.history_bets.append({
                    "id": len(st.session_state.history_bets) + 1,
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "match": "MULTIPLA (COMBO)",
                    "market": f"Combo di {len(selected_combo)} eventi",
                    "odds": round(total_combo_odds, 2),
                    "stake": combo_res['stake_eur'],
                    "ev": combo_res['ev'],
                    "status": "IN CORSO",
                    "profit": 0.0
                })
                st.success("Schedina multipla registrata con successo!")
                st.rerun()
        else:
            st.info("Seleziona almeno un evento dalla lista sopra per calcolare la multipla.")
            
        if st.button("PULISCI POOL MULTIPLE"):
            st.session_state.saved_bets_pool = []
            st.rerun()
    else:
        st.info("Nessun evento salvato nella pool. Vai nella tab 'Analisi Squadre & Match' e clicca su 'Aggiungi alla pool per Schedina Multipla'.")

with tab_players:
    st.markdown("### ⚡ ANALISI STATISTICA GIOCATORI (SOT & FALLI & XL)")
    st.caption("Protocollo Tiri in Porta, Falli e Mercati XL Serie A: Seleziona squadra e calciatore dalla rosa ufficiale.")
    
    col_pl1, col_pl2 = st.columns(2)
    with col_pl1:
        pl_team = st.selectbox("Seleziona Squadra", sorted(list(SERIE_A_SQUADS.keys())), key="pl_team_sel")
        squad_list = SERIE_A_SQUADS[pl_team]
        player_names = [f"{p['name']} ({p['role']} #{p['number']})" for p in squad_list]
        chosen_p_str = st.selectbox("Seleziona Calciatore", player_names)
        chosen_p_obj = squad_list[player_names.index(chosen_p_str)]
    with col_pl2:
        p_market = st.selectbox(
            "Mercato Giocatore",
            [
                "Over 0.5 Tiri in Porta (SOT)",
                "Over 1.5 Tiri in Porta (SOT)",
                "Over 1.5 Falli Commessi",
                "Over 1.5 Falli Subiti",
                "Quasi Marcatore XL (x tiri in porta o gol)",
                "Quasi Ammonito XL (x falli commessi o ammonizione)"
            ]
        )
        p_quota = st.number_input("Quota Bookmaker Giocatore", min_value=1.01, max_value=30.0, value=1.90, step=0.01)
        p_rigorista = st.checkbox("Rigorista principale in campo (+10% xSOT)")

    # Gestione calcolo in base al mercato (inclusi i mercati XL)
    if "Quasi Marcatore XL" in p_market:
        # Valore combinato SOT + propensione gol stimata dal P90 del giocatore
        base_p90 = chosen_p_obj["sot_90"] * 1.35
    elif "Quasi Ammonito XL" in p_market:
        # Valore combinato falli commessi + boost ammonizione
        base_p90 = chosen_p_obj["fouls_c_90"] * 1.25
    else:
        base_p90 = chosen_p_obj["sot_90"] if "Tiri" in p_market else chosen_p_obj["fouls_c_90"]

    p_mod_val = base_p90 * (1.10 if p_rigorista else 1.0)
    
    if "0.5" in p_market or "XL" in p_market: 
        p_p_model = float(1.0 - poisson.cdf(0, p_mod_val))
    elif "1.5" in p_market: 
        p_p_model = float(1.0 - poisson.cdf(1, p_mod_val))
    else: 
        p_p_model = 0.55

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

    if p_calc_res['verdetto'] == "VALUE BET✅":
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
    st.markdown("### 📈 ANALISI KPI & GRAFICO TEMPORALE BANKROLL")
    st.markdown(f"""
        - **Capitale Iniziale:** `{initial_bankroll:.2f} €`
        - **Capitale Attuale:** `{current_bankroll:.2f} €`
        - **Profitto Netto:** `{total_profit:+.2f} €`
        - **Yield Operativo:** `{yield_val:+.2f}%`
        - **Totale Scommesse Tracciate:** `{len(st.session_state.history_bets)}`
    """)
    
    st.markdown("---")
    st.markdown("#### 📉 Andamento Temporale del Bankroll")
    
    concluded_bets = [b for b in st.session_state.history_bets if b.get("status") in ["VINTA", "PERSA"]]
    if concluded_bets:
        df_chart = pd.DataFrame(concluded_bets)
        df_chart = df_chart.sort_values(by="created_at")
        
        running_balance = [initial_bankroll]
        curr_b = initial_bankroll
        for p in df_chart["profit"]:
            curr_b += p
            running_balance.append(curr_b)
            
        chart_dates = ["Inizio"] + list(df_chart["created_at"])
        df_plot = pd.DataFrame({"Data": chart_dates, "Bankroll": running_balance})
        
        fig = px.line(
            df_plot, x="Data", y="Bankroll", markers=True,
            title="Evoluzione Storica del Capitale",
            labels={"Bankroll": "Capitale (€)", "Data": "Data Registrazione"}
        )
        fig.update_layout(
            plot_bgcolor="#1C2541",
            paper_bgcolor="#0B132B",
            font_color="#FFFFFF",
            xaxis=dict(showgrid=True, gridcolor="#2D3A5D"),
            yaxis=dict(showgrid=True, gridcolor="#2D3A5D")
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Registra e concludi almeno una scommessa (segnandola come VINTA o PERSA) per generare il grafico temporale dell'andamento del bankroll.")
