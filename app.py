import datetime
import numpy as np
import pandas as pd
import requests
from scipy.stats import poisson
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS Dark Fintech - Palette Frost Indigo con Contrasto Ottimizzato
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0B132B !important;
        color: #F8FAFC !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Protezione icone di sistema e icona password */
    [data-testid="stIconMaterial"], [class*="material-symbols"], i {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    
    /* FIX ICONA MOSTRA PASSWORD */
    [data-testid="stTextInput"] button {
        color: #1C2541 !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stTextInput"] button svg {
        fill: #1C2541 !important;
        stroke: #1C2541 !important;
    }
    
    header[data-testid="stHeader"] {
        background-color: #0B132B !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #1C2541 !important;
        border-right: 1px solid #2D3A5D !important;
    }
    
    [data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricLabel"] p {
        color: #CBD5E1 !important;
        font-size: 0.90rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }
    
    [data-testid="stCaptionContainer"] p, .stCaption {
        color: #CBD5E1 !important;
        font-size: 0.85rem !important;
    }
    
    p, span, label {
        color: #F8FAFC !important;
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
        color: #CBD5E1;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        font-weight: 600;
    }
    
    .metric-value-pos {
        font-size: 1.25rem;
        font-weight: 700;
        color: #2DD4BF;
    }
    
    .metric-value-neg {
        font-size: 1.25rem;
        font-weight: 700;
        color: #94A3B8;
    }
    
    .metric-value-neutral {
        font-size: 1.25rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    
    .slogan-box {
        background-color: rgba(45, 212, 191, 0.08);
        border-left: 4px solid #2DD4BF;
        padding: 12px 18px;
        border-radius: 4px;
        margin-bottom: 18px;
        font-size: 0.92rem;
        color: #FFFFFF;
        font-weight: 500;
    }
    
    .round-badge {
        background-color: #1C2541;
        border: 1px solid #2D3A5D;
        color: #2DD4BF;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 8px 14px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 14px;
    }
    
    .tactical-card {
        background-color: #131D38;
        border: 1px solid #2D3A5D;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .pitch-board {
        background: linear-gradient(180deg, #0d233a 0%, #0a192f 100%);
        border: 2px solid #2DD4BF;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .pitch-row {
        background: rgba(28, 37, 65, 0.7);
        border: 1px solid #2D3A5D;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    
    .lineup-badge-prob {
        background-color: rgba(245, 158, 11, 0.15);
        border: 1px solid #F59E0B;
        color: #FCD34D;
        font-size: 0.80rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }
    
    .lineup-badge-off {
        background-color: rgba(45, 212, 191, 0.15);
        border: 1px solid #2DD4BF;
        color: #2DD4BF;
        font-size: 0.80rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }
    
    .stButton>button {
        background-color: #2DD4BF !important;
        color: #0B132B !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .stButton>button:hover {
        background-color: #14B8A6 !important;
        color: #0B132B !important;
    }
    
    div[data-testid="stTable"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #2D3A5D;
        background-color: #1C2541;
    }
    
    table {
        color: #FFFFFF !important;
        font-size: 0.90rem !important;
    }
    
    thead tr th {
        background-color: #0B132B !important;
        color: #CBD5E1 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        font-size: 0.78rem !important;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="stExpander"] {
        background-color: #1C2541 !important;
        border: 1px solid #2D3A5D !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        overflow: hidden !important;
    }
    
    div[data-testid="stExpander"] summary {
        background-color: #0B132B !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stExpander"] summary:hover {
        background-color: #2D3A5D !important;
        color: #FFFFFF !important;
    }
    
    div[data-testid="stExpander"] details[open] > summary {
        border-bottom-left-radius: 0px !important;
        border-bottom-right-radius: 0px !important;
        border-bottom: 1px solid #2D3A5D !important;
        background-color: #0B132B !important;
    }
    
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #1C2541 !important;
        padding: 18px 22px !important;
        color: #FFFFFF !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Funzione di Sicurezza Numerica
def safe_odds_val(val, min_v=1.01, max_v=20.0):
    try:
        v = float(val)
        if np.isnan(v) or np.isinf(v) or v < min_v:
            return min_v
        if v > max_v:
            return max_v
        return round(v, 2)
    except Exception:
        return min_v

# Parametri Secrets
SB_URL = st.secrets.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = st.secrets.get("SUPABASE_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")
FOOTBALL_KEY = st.secrets.get("FOOTBALL_API_KEY", "f59b5ad05a6b45fa5f19582d3e493f7f")

# Inizializzazione Sessione
if "user" not in st.session_state:
    st.session_state.user = None
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "free"
if "access_token" not in st.session_state:
    st.session_state.access_token = None

def get_headers(token=None):
    auth_bearer = token or SB_KEY
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {auth_bearer}",
        "Content-Type": "application/json",
    }

# Autenticazione Supabase
def login_user(email, password):
    if not SB_URL or not SB_KEY: return False, "Chiavi Supabase mancanti nei Secrets."
    url = f"{SB_URL}/auth/v1/token?grant_type=password"
    try:
        res = requests.post(url, json={"email": email, "password": password}, headers=get_headers(), timeout=10)
        if res.status_code == 200:
            data = res.json()
            st.session_state.user = data.get("user")
            st.session_state.access_token = data.get("access_token")
            u_id = data["user"]["id"]
            prof_url = f"{SB_URL}/rest/v1/profiles?id=eq.{u_id}&select=tier"
            prof_res = requests.get(prof_url, headers=get_headers(data.get("access_token")), timeout=10)
            if prof_res.status_code == 200 and prof_res.json():
                st.session_state.user_tier = prof_res.json()[0].get("tier", "free")
            return True, None
        err = res.json().get("error_description") or res.json().get("msg") or "Credenziali non corrette."
        return False, err
    except Exception as e:
        return False, str(e)

def register_user(email, password):
    if not SB_URL or not SB_KEY: return False, "Chiavi Supabase mancanti nei Secrets."
    url = f"{SB_URL}/auth/v1/signup"
    try:
        res = requests.post(url, json={"email": email, "password": password}, headers=get_headers(), timeout=10)
        if res.status_code in [200, 201]:
            return True, "Registrazione completata. Puoi accedere ora."
        err = res.json().get("msg") or res.json().get("error_description") or "Errore di registrazione."
        return False, err
    except Exception as e:
        return False, str(e)

def update_user_password(new_password):
    token = st.session_state.get("access_token")
    if not token: return False, "Sessione scaduta. Effettua nuovamente il login."
    url = f"{SB_URL}/auth/v1/user"
    try:
        res = requests.put(url, json={"password": new_password}, headers=get_headers(token), timeout=10)
        if res.status_code == 200: return True, "Password aggiornata con successo."
        err = res.json().get("msg") or res.json().get("error_description") or "Errore aggiornamento password."
        return False, err
    except Exception as e:
        return False, str(e)

def logout_user():
    st.session_state.user = None
    st.session_state.user_tier = "free"
    st.session_state.access_token = None

def redeem_vip_code(user_id, code_input):
    valid_promo_codes = ["Valuebet2026", "VIP2026", "PRO2026"]
    if code_input.strip() in valid_promo_codes:
        if SB_URL and SB_KEY:
            token = st.session_state.get("access_token")
            url = f"{SB_URL}/rest/v1/profiles?id=eq.{user_id}"
            hdrs = get_headers(token)
            hdrs["Prefer"] = "return=representation"
            try: requests.patch(url, json={"tier": "premium"}, headers=hdrs, timeout=10)
            except Exception: pass
        st.session_state.user_tier = "premium"
        return True, "Codice valido. Piano Premium attivato."
    return False, "Codice promozionale non valido."

# Schermata di Accesso
if not st.session_state.user:
    st.title("VALUE BET ANALYZER")
    st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)
    
    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    with auth_col2:
        tab_log, tab_reg = st.tabs(["Accedi al Tuo Account", "Crea Nuovo Account"])
        with tab_log:
            log_email = st.text_input("Email", key="log_email")
            log_pwd = st.text_input("Password", type="password", key="log_pwd")
            if st.button("ACCEDI", use_container_width=True):
                if log_email and log_pwd:
                    ok, err = login_user(log_email, log_pwd)
                    if ok:
                        st.success("Accesso effettuato.")
                        st.rerun()
                    else:
                        st.error(f"Errore accesso: {err}")
                else:
                    st.warning("Compila tutti i campi.")
        with tab_reg:
            reg_email = st.text_input("Email", key="reg_email")
            reg_pwd = st.text_input("Password (min. 6 caratteri)", type="password", key="reg_pwd")
            if st.button("REGISTRATI", use_container_width=True):
                if reg_email and len(reg_pwd) >= 6:
                    ok, msg = register_user(reg_email, reg_pwd)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(f"Errore registrazione: {msg}")
                else:
                    st.warning("Inserisci un'email valida e una password di almeno 6 caratteri.")
    st.stop()

# Dati Utente
user_data = st.session_state.user if isinstance(st.session_state.user, dict) else {}
user_email = user_data.get("email", "")
user_id = user_data.get("id", "")

# Cloud Database Scommesse
def fetch_user_bets(u_id):
    if SB_URL and SB_KEY and u_id:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets?user_id=eq.{u_id}&select=*&order=created_at.desc"
        try:
            res = requests.get(url, headers=get_headers(token), timeout=10)
            if res.status_code == 200 and res.json():
                return pd.DataFrame(res.json())
        except Exception:
            pass
    return pd.DataFrame(columns=["id", "created_at", "match", "market", "odds", "stake", "ev", "status", "profit"])

def save_user_bet(u_id, match, market, odds, stake, ev):
    if SB_URL and SB_KEY and u_id:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        payload = {
            "user_id": u_id,
            "match": match,
            "market": market,
            "odds": float(odds),
            "stake": float(stake),
            "ev": float(ev),
            "status": "IN CORSO",
            "profit": 0.0,
        }
        try:
            res = requests.post(url, json=payload, headers=hdrs, timeout=10)
            return res.status_code in [200, 201]
        except Exception:
            pass
    return False

def update_bet_status(bet_id, new_status, odds, stake):
    profit_val = 0.0
    if new_status == "VINTA": profit_val = round((odds - 1.0) * stake, 2)
    elif new_status == "PERSA": profit_val = round(-stake, 2)
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets?id=eq.{bet_id}"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        try:
            requests.patch(url, json={"status": new_status, "profit": profit_val}, headers=hdrs, timeout=10)
        except Exception:
            pass

# Mapping Squadre
API_FOOTBALL_TEAM_IDS = {
    "Inter": 505, "Juventus": 496, "Milan": 489, "Napoli": 492,
    "Atalanta": 499, "Roma": 497, "Lazio": 487, "Fiorentina": 502,
    "Bologna": 500, "Torino": 503, "Parma": 511, "Cagliari": 490,
    "Empoli": 511, "Genoa": 495, "Monza": 1579, "Lecce": 867,
    "Udinese": 494, "Verona": 504, "Venezia": 517, "Como": 880
}

CLEAN_TEAM_NAMES = {
    "Inter Milan": "Inter", "AC Milan": "Milan", "Atalanta BC": "Atalanta",
    "AS Roma": "Roma", "SS Lazio": "Lazio", "Juventus": "Juventus",
    "Napoli": "Napoli", "Fiorentina": "Fiorentina", "Bologna": "Bologna",
    "Torino": "Torino", "Parma": "Parma", "Cagliari": "Cagliari",
    "Empoli": "Empoli", "Genoa": "Genoa", "Monza": "Monza",
    "Lecce": "Lecce", "Udinese": "Udinese", "Verona": "Verona",
    "Venezia": "Venezia", "Como": "Como"
}

def clean_name(raw_name):
    for eng, ita in CLEAN_TEAM_NAMES.items():
        if eng.lower() in raw_name.lower():
            return ita
    return raw_name

# ORGANICO UFFICIALE COMPLETO CAN A-B (Serie A & Serie B)
SERIE_A_REFEREES_DB = {
    "doveri": {"name": "Daniele Doveri", "fouls_avg": 25.4, "cards_avg": 4.1, "severity": "Standard"},
    "massa": {"name": "Davide Massa", "fouls_avg": 26.8, "cards_avg": 4.9, "severity": "Standard"},
    "mariani": {"name": "Maurizio Mariani", "fouls_avg": 27.8, "cards_avg": 4.8, "severity": "Severo"},
    "guida": {"name": "Marco Guida", "fouls_avg": 27.4, "cards_avg": 5.1, "severity": "Severo"},
    "sozza": {"name": "Simone Sozza", "fouls_avg": 21.5, "cards_avg": 3.6, "severity": "Permissivo"},
    "colombo": {"name": "Andrea Colombo", "fouls_avg": 26.2, "cards_avg": 4.6, "severity": "Standard"},
    "la penna": {"name": "Federico La Penna", "fouls_avg": 25.8, "cards_avg": 4.3, "severity": "Standard"},
    "pairetto": {"name": "Luca Pairetto", "fouls_avg": 28.0, "cards_avg": 5.2, "severity": "Severo"},
    "ayroldi": {"name": "Giovanni Ayroldi", "fouls_avg": 28.5, "cards_avg": 5.5, "severity": "Severo"},
    "chiffi": {"name": "Daniele Chiffi", "fouls_avg": 24.8, "cards_avg": 4.2, "severity": "Standard"},
    "di bello": {"name": "Marco Di Bello", "fouls_avg": 27.9, "cards_avg": 5.3, "severity": "Severo"},
    "abisso": {"name": "Rosario Abisso", "fouls_avg": 26.5, "cards_avg": 4.7, "severity": "Standard"},
    "feliciani": {"name": "Ermanno Feliciani", "fouls_avg": 25.0, "cards_avg": 4.0, "severity": "Standard"},
    "giua": {"name": "Antonio Giua", "fouls_avg": 28.2, "cards_avg": 5.4, "severity": "Severo"},
    "zufferli": {"name": "Luca Zufferli", "fouls_avg": 24.5, "cards_avg": 3.8, "severity": "Permissivo"},
    "piccinini": {"name": "Marco Piccinini", "fouls_avg": 26.0, "cards_avg": 4.5, "severity": "Standard"},
    "fabbri": {"name": "Michael Fabbri", "fouls_avg": 26.1, "cards_avg": 4.5, "severity": "Standard"},
    "rapuano": {"name": "Antonio Rapuano", "fouls_avg": 27.3, "cards_avg": 5.0, "severity": "Severo"},
    "marcenaro": {"name": "Matteo Marcenaro", "fouls_avg": 27.1, "cards_avg": 5.0, "severity": "Severo"},
    "marinelli": {"name": "Livio Marinelli", "fouls_avg": 25.2, "cards_avg": 4.2, "severity": "Standard"},
    "aureliano": {"name": "Gianluca Aureliano", "fouls_avg": 27.5, "cards_avg": 4.9, "severity": "Severo"},
    "marchetti": {"name": "Matteo Marchetti", "fouls_avg": 25.6, "cards_avg": 4.4, "severity": "Standard"},
    "maresca": {"name": "Fabio Maresca", "fouls_avg": 28.2, "cards_avg": 5.4, "severity": "Severo"},
    "ferrieri_caputi": {"name": "Maria Sole Ferrieri Caputi", "fouls_avg": 24.9, "cards_avg": 4.0, "severity": "Standard"},
    "fourneau": {"name": "Francesco Fourneau", "fouls_avg": 26.4, "cards_avg": 4.6, "severity": "Standard"},
    "manganelli": {"name": "Gianluca Manganiello", "fouls_avg": 25.1, "cards_avg": 4.2, "severity": "Standard"},
    "massimi": {"name": "Luca Massimi", "fouls_avg": 26.7, "cards_avg": 4.7, "severity": "Standard"},
    "prontera": {"name": "Alessandro Prontera", "fouls_avg": 27.0, "cards_avg": 4.8, "severity": "Standard"},
    "santoro": {"name": "Alberto Santoro", "fouls_avg": 26.3, "cards_avg": 4.5, "severity": "Standard"},
    "volpi": {"name": "Manuel Volpi", "fouls_avg": 28.0, "cards_avg": 5.1, "severity": "Severo"},
    "rutella": {"name": "Daniele Rutella", "fouls_avg": 27.6, "cards_avg": 4.9, "severity": "Severo"},
    "bonacina": {"name": "Kevin Bonacina", "fouls_avg": 25.8, "cards_avg": 4.3, "severity": "Standard"},
    "crezzini": {"name": "Valerio Crezzini", "fouls_avg": 26.0, "cards_avg": 4.5, "severity": "Standard"},
    "collu": {"name": "Giuseppe Collu", "fouls_avg": 27.2, "cards_avg": 4.8, "severity": "Severo"},
    "di_marco": {"name": "Davide Di Marco", "fouls_avg": 25.5, "cards_avg": 4.1, "severity": "Standard"},
    "perenzoni": {"name": "Daniele Perenzoni", "fouls_avg": 26.9, "cards_avg": 4.7, "severity": "Standard"},
    "pezzuto": {"name": "Ivano Pezzuto", "fouls_avg": 26.2, "cards_avg": 4.4, "severity": "Standard"},
    "scatena": {"name": "Gabriele Scatena", "fouls_avg": 25.9, "cards_avg": 4.3, "severity": "Standard"},
    "tremolada": {"name": "Paride Tremolada", "fouls_avg": 27.0, "cards_avg": 4.8, "severity": "Standard"},
    "cosso": {"name": "Francesco Cosso", "fouls_avg": 26.4, "cards_avg": 4.5, "severity": "Standard"}
}

# Database Squadre & Tattica
TEAM_METRICS = {
    "Inter": {"gf_h": 2.25, "gf_a": 1.90, "ga_h": 0.65, "ga_a": 0.80, "xg_5": 2.15, "xg_s": 2.05, "sot_pro": 6.2, "sot_against": 3.1, "corners_pro": 6.4, "corners_against": 3.6, "cross": 21.5, "blocked_shots": 5.4, "fouls_pro": 11.2, "fouls_against": 12.8, "cards_avg": 1.8, "modulo": "3-5-2", "stile": "Pressing Alto & Sovrapposizione Catene Esterne", "possesso": 61.2},
    "Juventus": {"gf_h": 1.70, "gf_a": 1.40, "ga_h": 0.50, "ga_a": 0.75, "xg_5": 1.65, "xg_s": 1.55, "sot_pro": 5.1, "sot_against": 2.8, "corners_pro": 5.6, "corners_against": 3.8, "cross": 18.2, "blocked_shots": 4.6, "fouls_pro": 12.1, "fouls_against": 13.5, "cards_avg": 2.1, "modulo": "4-2-3-1", "stile": "Dominio Territoriale & Costruzione Bassa", "possesso": 58.4},
    "Milan": {"gf_h": 2.05, "gf_a": 1.65, "ga_h": 1.10, "ga_a": 1.25, "xg_5": 1.90, "xg_s": 1.80, "sot_pro": 5.6, "sot_against": 4.4, "corners_pro": 5.8, "corners_against": 4.2, "cross": 19.5, "blocked_shots": 5.2, "fouls_pro": 11.8, "fouls_against": 12.0, "cards_avg": 2.3, "modulo": "4-2-3-1", "stile": "Transizione Rapida & Spinta sulle Fasce", "possesso": 56.0},
    "Napoli": {"gf_h": 1.85, "gf_a": 1.55, "ga_h": 0.60, "ga_a": 0.85, "xg_5": 1.80, "xg_s": 1.70, "sot_pro": 5.3, "sot_against": 3.2, "corners_pro": 6.1, "corners_against": 3.5, "cross": 20.8, "blocked_shots": 5.1, "fouls_pro": 12.4, "fouls_against": 13.0, "cards_avg": 1.9, "modulo": "3-5-2", "stile": "Compattezza Difensiva & Attacco Diretto", "possesso": 55.5},
    "Atalanta": {"gf_h": 2.30, "gf_a": 1.80, "ga_h": 1.05, "ga_a": 1.20, "xg_5": 2.20, "xg_s": 2.10, "sot_pro": 6.5, "sot_against": 4.1, "corners_pro": 6.7, "corners_against": 4.0, "cross": 22.4, "blocked_shots": 5.8, "fouls_pro": 13.8, "fouls_against": 14.2, "cards_avg": 2.4, "modulo": "3-4-2-1", "stile": "Pressing Ultra-Offensivo a Tutto Campo", "possesso": 57.8},
    "Roma": {"gf_h": 1.60, "gf_a": 1.20, "ga_h": 0.95, "ga_a": 1.15, "xg_5": 1.55, "xg_s": 1.50, "sot_pro": 4.9, "sot_against": 3.8, "corners_pro": 5.4, "corners_against": 4.1, "cross": 17.5, "blocked_shots": 4.2, "fouls_pro": 13.0, "fouls_against": 12.5, "cards_avg": 2.2, "modulo": "3-4-2-1", "stile": "Marcatura a Uomo & Rifinitura Centrale", "possesso": 52.3},
    "Lazio": {"gf_h": 1.75, "gf_a": 1.35, "ga_h": 1.00, "ga_a": 1.25, "xg_5": 1.60, "xg_s": 1.55, "sot_pro": 4.8, "sot_against": 4.0, "corners_pro": 5.3, "corners_against": 4.3, "cross": 18.0, "blocked_shots": 4.5, "fouls_pro": 13.2, "fouls_against": 12.2, "cards_avg": 2.5, "modulo": "4-2-3-1", "stile": "Verticalizzazioni Rapide & Aggressività", "possesso": 51.5},
    "Fiorentina": {"gf_h": 1.70, "gf_a": 1.30, "ga_h": 0.90, "ga_a": 1.20, "xg_5": 1.55, "xg_s": 1.45, "sot_pro": 4.7, "sot_against": 3.9, "corners_pro": 5.5, "corners_against": 4.2, "cross": 19.0, "blocked_shots": 4.8, "fouls_pro": 12.6, "fouls_against": 12.8, "cards_avg": 2.1, "modulo": "4-3-3", "stile": "Possesso Laterale & Densità Offensiva", "possesso": 54.0},
    "Bologna": {"gf_h": 1.50, "gf_a": 1.15, "ga_h": 0.85, "ga_a": 1.10, "xg_5": 1.45, "xg_s": 1.40, "sot_pro": 4.5, "sot_against": 3.5, "corners_pro": 5.2, "corners_against": 3.9, "cross": 17.8, "blocked_shots": 4.3, "fouls_pro": 12.5, "fouls_against": 12.0, "cards_avg": 2.0, "modulo": "4-2-3-1", "stile": "Costruzione Bassa & Controllo Ritmi", "possesso": 53.5},
    "Torino": {"gf_h": 1.25, "gf_a": 0.95, "ga_h": 0.90, "ga_a": 1.15, "xg_5": 1.20, "xg_s": 1.15, "sot_pro": 3.9, "sot_against": 4.2, "corners_pro": 4.6, "corners_against": 4.5, "cross": 16.0, "blocked_shots": 3.9, "fouls_pro": 14.1, "fouls_against": 11.8, "cards_avg": 2.3, "modulo": "3-5-2", "stile": "Duelli Fisici & Ripartenza", "possesso": 48.0},
    "Parma": {"gf_h": 1.35, "gf_a": 1.10, "ga_h": 1.45, "ga_a": 1.65, "xg_5": 1.30, "xg_s": 1.25, "sot_pro": 4.2, "sot_against": 5.4, "corners_pro": 4.7, "corners_against": 5.8, "cross": 15.5, "blocked_shots": 3.7, "fouls_pro": 13.5, "fouls_against": 11.5, "cards_avg": 2.2, "modulo": "4-2-3-1", "stile": "Contropiede Diretto ad Alta Velocità", "possesso": 45.2},
    "Cagliari": {"gf_h": 1.20, "gf_a": 0.90, "ga_h": 1.35, "ga_a": 1.60, "xg_5": 1.15, "xg_s": 1.15, "sot_pro": 3.8, "sot_against": 5.2, "corners_pro": 4.5, "corners_against": 5.6, "cross": 16.5, "blocked_shots": 3.6, "fouls_pro": 13.6, "fouls_against": 12.0, "cards_avg": 2.4, "modulo": "3-5-2", "stile": "Blocco Basso & Palle Inattive", "possesso": 44.0},
    "Venezia": {"gf_h": 1.15, "gf_a": 0.85, "ga_h": 1.40, "ga_a": 1.70, "xg_5": 1.10, "xg_s": 1.10, "sot_pro": 3.7, "sot_against": 5.5, "corners_pro": 4.4, "corners_against": 5.9, "cross": 15.0, "blocked_shots": 3.5, "fouls_pro": 13.4, "fouls_against": 11.8, "cards_avg": 2.3, "modulo": "3-5-2", "stile": "Difesa Posizionale & Ripartenza", "possesso": 43.5}
}

DEFAULT_METRICS = {
    "gf_h": 1.30, "gf_a": 1.05, "ga_h": 1.10, "ga_a": 1.45, "xg_5": 1.25, "xg_s": 1.25,
    "sot_pro": 4.1, "sot_against": 4.8, "corners_pro": 4.6, "corners_against": 5.2,
    "cross": 16.0, "blocked_shots": 3.8, "fouls_pro": 13.0, "fouls_against": 12.0, "cards_avg": 2.2, "modulo": "4-4-2", "stile": "Blocco Medio Bilanciato", "possesso": 50.0
}

def get_metrics(team_name):
    cleaned = clean_name(team_name)
    for name, metrics in TEAM_METRICS.items():
        if name.lower() in cleaned.lower() or cleaned.lower() in name.lower():
            return metrics
    return DEFAULT_METRICS

# Recupero Dinamico Squadre da API-Football
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_team_squad(team_name, api_key):
    c_name = clean_name(team_name)
    team_id = API_FOOTBALL_TEAM_IDS.get(c_name)
    if team_id and api_key:
        url = f"https://v3.football.api-sports.io/players/squads?team={team_id}"
        headers = {"x-apisports-key": api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json().get("response", [])
                if data and "players" in data[0]:
                    players = []
                    for p in data[0]["players"]:
                        pos = p.get("position", "Player")
                        if pos == "Goalkeeper": s, f, sv = 0.0, 0.1, 3.2
                        elif pos == "Attacker": s, f, sv = 1.30, 1.40, 0.0
                        elif pos == "Midfielder": s, f, sv = 0.70, 1.60, 0.0
                        else: s, f, sv = 0.30, 1.80, 0.0
                        players.append({
                            "name": p.get("name", ""),
                            "role": pos, "number": str(p.get("number", "-")),
                            "sot_90": s, "fouls_c_90": f, "saves_90": sv,
                            "penalties": (pos == "Attacker")
                        })
                    if len(players) >= 11:
                        return players
        except Exception:
            pass
    return []

# Rilevamento Ufficiale Partita (Lineup & Arbitro)
@st.cache_data(ttl=1800, show_spinner=False)
def check_fixture_details(home_team, away_team, api_key):
    h_name = clean_name(home_team)
    a_name = clean_name(away_team)
    h_id = API_FOOTBALL_TEAM_IDS.get(h_name)
    lineup_status = "PROBABILE"
    detected_ref = None
    
    if h_id and api_key:
        url = f"https://v3.football.api-sports.io/fixtures?team={h_id}&next=5"
        headers = {"x-apisports-key": api_key}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                fixtures = res.json().get("response", [])
                for fix in fixtures:
                    t_h = fix.get("teams", {}).get("home", {}).get("name", "")
                    t_a = fix.get("teams", {}).get("away", {}).get("name", "")
                    if h_name.lower() in t_h.lower() or a_name.lower() in t_a.lower():
                        ref = fix.get("fixture", {}).get("referee")
                        if ref: detected_ref = ref.split(",")[0].replace("Italy", "").strip()
                        f_id = fix.get("fixture", {}).get("id")
                        if f_id:
                            l_res = requests.get(f"https://v3.football.api-sports.io/fixtures/lineups?fixture={f_id}", headers=headers, timeout=5)
                            if l_res.status_code == 200 and len(l_res.json().get("response", [])) > 0:
                                lineup_status = "UFFICIALE"
        except Exception:
            pass
    return lineup_status, detected_ref

# Motore Matematico Quantitativo
class MatchAnalystEngine:
    @staticmethod
    def calculate_kelly(prob, odds, bankroll, kelly_fraction=0.50):
        b = odds - 1.0
        if b <= 0: return 0.0, 0.0
        p_loss = 1.0 - prob
        k_full = (prob * b - p_loss) / b
        k_scaled = max(0.0, k_full * kelly_fraction)
        edge = (prob * odds) - 1.0
        cap = 0.05 if edge <= 0.05 else (0.12 if edge <= 0.10 else 0.20)
        final_stake_pct = min(k_scaled, cap)
        monetary = round(bankroll * final_stake_pct, 2)
        return round(final_stake_pct * 100, 2), monetary

    @staticmethod
    def calculate_fair_and_min_odds(prob, min_edge=0.015):
        if prob <= 0.01: return 20.0, 20.0
        fair = round(1.0 / prob, 2)
        min_entry = round((1.0 + min_edge) / prob, 2)
        return min(fair, 20.0), min(min_entry, 20.0)

    @staticmethod
    def analyze_team_goals_over15(team, opp, is_home, min_edge=0.015):
        t_met = get_metrics(team)
        o_met = get_metrics(opp)
        gf = t_met["gf_h"] if is_home else t_met["gf_a"]
        ga_opp = o_met["ga_a"] if is_home else o_met["ga_h"]
        xg_base = gf * (ga_opp / 1.25) * (t_met["xg_5"] / max(0.1, t_met["xg_s"]))
        mod = 1.0
        if "3-4-2-1" in t_met["modulo"] or "4-3-3" in t_met["modulo"]: mod += 0.08
        if "Pressing" in t_met["stile"]: mod += 0.10
        if "Blocco Basso" in o_met["stile"]: mod -= 0.10
        xg_final = xg_base * mod
        prob = float(1.0 - (poisson.pmf(0, xg_final) + poisson.pmf(1, xg_final)))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over 1.5 Gol ({clean_name(team)})",
            "market_type": "Over 1.5 Gol Squadra",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xG Team Finale", "metric_val": f"{xg_final:.2f}",
            "note": f"Efficienza: {gf:.2f} GF | Difesa Avversario concede {ga_opp:.2f} GA"
        }

    @staticmethod
    def analyze_corners_multiline(h_team, a_team, line=9.5, min_edge=0.015):
        h_met = get_metrics(h_team)
        a_met = get_metrics(a_team)
        base = (h_met["corners_pro"] + a_met["corners_against"])/2.0 + (a_met["corners_pro"] + h_met["corners_against"])/2.0
        mod = 1.0
        if h_met["cross"] > 20.0 or a_met["cross"] > 20.0: mod += 0.08
        if h_met["blocked_shots"] > 5.0 or a_met["blocked_shots"] > 5.0: mod += 0.10
        corners_final = base * mod
        prob = float(1.0 - poisson.cdf(line - 0.5, corners_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Corner Totali",
            "market_type": "Corner Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Corner Proiettati", "metric_val": f"{corners_final:.2f}",
            "note": f"Cross combinati: {h_met['cross']+a_met['cross']:.1f} | Tiri bloccati: {h_met['blocked_shots']+a_met['blocked_shots']:.1f}"
        }

    @staticmethod
    def analyze_player_sot(player, opp_team, line=0.5, min_edge=0.015):
        opp_met = get_metrics(opp_team)
        xsot_base = player.get("sot_90", 1.0) * (82 / 90) * (opp_met["sot_against"] / 4.3)
        mod = 1.10 if player.get("penalties") else 1.0
        xsot_final = xsot_base * mod
        prob = float(1.0 - poisson.cdf(line - 0.5, xsot_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Tiri in Porta ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xSOT Attesi", "metric_val": f"{xsot_final:.2f}",
            "note": f"Ruolo: {player['role']} | Media SOT/90m: {player.get('sot_90', 1.0):.2f}"
        }

    @staticmethod
    def analyze_player_fouls(player, opp_team, ref_data, line=1.5, min_edge=0.015):
        opp_met = get_metrics(opp_team)
        ref_mod = 1.10 if ref_data.get("severity") == "Severo" else (0.90 if ref_data.get("severity") == "Permissivo" else 1.0)
        xf_final = player.get("fouls_c_90", 1.0) * (85 / 90) * (opp_met["fouls_against"] / 12.5) * ref_mod
        prob = float(1.0 - poisson.cdf(line - 0.5, xf_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Commessi ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xFouls Attesi", "metric_val": f"{xf_final:.2f}",
            "note": f"Arbitro: {ref_data.get('name')} (Media: {ref_data.get('fouls_avg'):.1f} falli/partita) | Falli subiti avversario: {opp_met['fouls_against']:.1f}"
        }

    @staticmethod
    def analyze_goalkeeper_saves(player, opp_team, line=2.5, min_edge=0.015):
        opp_met = get_metrics(opp_team)
        expected_shots_faced = opp_met["sot_pro"]
        xsaves = expected_shots_faced * 0.72
        prob = float(1.0 - poisson.cdf(line - 0.5, xsaves))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Parate ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Parate Proiettate", "metric_val": f"{xsaves:.2f}",
            "note": f"Tiri nello specchio avversario: {opp_met['sot_pro']:.1f} | Save Rate stimato: 72%"
        }

    @staticmethod
    def analyze_disciplinary_match(h_team, a_team, ref_data, line=4.5, min_edge=0.015):
        h_met = get_metrics(h_team)
        a_met = get_metrics(a_team)
        cards_exp = (h_met["cards_avg"] + a_met["cards_avg"]) / 2.0 * (ref_data["cards_avg"] / 4.5) * 2.0
        prob = float(1.0 - poisson.cdf(line - 0.5, cards_exp))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Cartellini Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Cartellini Attesi", "metric_val": f"{cards_exp:.2f}",
            "note": f"Arbitro: {ref_data['name']} (Media: {ref_data['cards_avg']:.1f} cartellini - Severità: {ref_data['severity']})"
        }

# Filtro Turno Singolo
def filter_current_matchday(matches):
    if not matches: return [], "", ""
    parsed = []
    for m in matches:
        ct_str = m.get("commence_time", "")
        try:
            dt = datetime.datetime.fromisoformat(ct_str.replace("Z", "+00:00"))
            parsed.append((dt, m))
        except Exception:
            pass
    if not parsed: return matches, "", ""
    parsed.sort(key=lambda x: x[0])
    first_dt = parsed[0][0]
    round_cutoff = first_dt + datetime.timedelta(days=4)
    current_round = [m for dt, m in parsed if dt <= round_cutoff]
    start_label = first_dt.strftime("%d/%m/%Y")
    end_label = max(dt for dt, m in parsed if dt <= round_cutoff).strftime("%d/%m/%Y")
    return current_round, start_label, end_label

# Cache Odds API
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_odds_api(api_key, sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200: return res.json(), None
        return None, f"Errore API {res.status_code}: {res.text}"
    except Exception as e:
        return None, str(e)

# Header & Sidebar
st.title("VALUE BET ANALYZER")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)

is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE (DEMO)"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")

if not is_premium:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### SBLOCCO PIANO PRO")
    promo_code = st.sidebar.text_input("Codice VIP / Tester", placeholder="Inserisci codice...", type="password")
    if st.sidebar.button("ATTIVA PREMIUM", use_container_width=True):
        if promo_code:
            ok, msg = redeem_vip_code(user_id, promo_code)
            if ok:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.error(msg)

if st.sidebar.button("LOGOUT", use_container_width=True):
    logout_user()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### PARAMETRI OPERATIVI")
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0, help="Capitale totale dedicato alle scommesse di valore.")

kelly_fraction = st.sidebar.select_slider(
    "Frazione di Kelly",
    options=[0.25, 0.50],
    value=0.50,
    format_func=lambda x: "0.25 (Prudente / Kelly/4)" if x == 0.25 else "0.50 (Standard / Kelly Mezzato)",
    help="Regola la formula di money management. 0.50 è lo standard quantitativo che protegge il bankroll."
)

min_edge_pct = st.sidebar.slider(
    "Soglia Minima Edge (%)",
    min_value=1.0, max_value=3.0, value=1.5, step=0.5,
    help="Vantaggio matematico minimo richiesto rispetto al banco."
)
min_edge_val = min_edge_pct / 100.0

# Calcolo Bankroll
bets_df = fetch_user_bets(user_id)
total_profit = 0.0
yield_pct = 0.0
win_rate_pct = 0.0

if not bets_df.empty and "status" in bets_df.columns:
    settled = bets_df[bets_df["status"].isin(["VINTA", "PERSA"])]
    total_profit = float(settled["profit"].sum()) if not settled.empty else 0.0
    total_stake = float(settled["stake"].sum()) if not settled.empty else 0.0
    won_c = len(settled[settled["status"] == "VINTA"]) if not settled.empty else 0
    if total_stake > 0: yield_pct = (total_profit / total_stake) * 100.0
    if len(settled) > 0: win_rate_pct = (won_c / len(settled)) * 100.0

current_bankroll = initial_bankroll + total_profit
profit_pct = (total_profit / initial_bankroll) * 100.0 if initial_bankroll > 0 else 0.0

st.sidebar.markdown("---")
st.sidebar.markdown("### IL TUO BANKROLL CLOUD")
st.sidebar.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Capitale Attuale</div>
        <div class="metric-value-neutral">{current_bankroll:.2f} €</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Profitto / Perdita Netta</div>
        <div class="{ 'metric-value-pos' if total_profit >= 0 else 'metric-value-neg' }">
            {total_profit:+.2f} € ({profit_pct:+.2f}%)
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Yield Operativo</div>
        <div class="{ 'metric-value-pos' if yield_pct >= 0 else 'metric-value-neg' }">
            {yield_pct:+.2f}%
        </div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Win Rate</div>
        <div class="metric-value-neutral">{win_rate_pct:.1f}%</div>
    </div>
""", unsafe_allow_html=True)

# Fetch Partite Live
if "raw_matches" not in st.session_state and ODDS_KEY:
    data, err = fetch_odds_api(ODDS_KEY, "soccer_italy_serie_a")
    if data: st.session_state.raw_matches = data

matches_raw = st.session_state.get("raw_matches", [])
matches, round_start, round_end = filter_current_matchday(matches_raw)

if round_start:
    st.markdown(f'<div class="round-badge">TURNO IN CORSO: {round_start} - {round_end} ({len(matches)} incontri)</div>', unsafe_allow_html=True)

# Schede Applicative
tab_scan, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Scanner Top 5 del Turno",
    "Cat. 1 - Mercati Principali",
    "Cat. 2 - Statistiche & Tattica Squadre",
    "Cat. 3 - Prestazioni Calciatori & Portieri",
    "Cat. 4 - Focus Disciplinare & Arbitri",
    "Registro Scommesse",
    "Gestione Account"
])

# SCANNER TOP 5 DEL TURNO
with tab_scan:
    st.markdown("### TOP 5 VALUE BETS CLASSIFICATE PER IL TURNO")
    st.caption("Classifica ordinata per valore atteso reale (Over 1.5 Gol Squadra e Corner Totali).")
    
    with st.expander("Guida ai Termini & Legenda Quantitativa", expanded=False):
        st.markdown("""
        * **Probabilità Modello:** La percentuale reale stimata dal nostro algoritmo matematico che l'evento si verifichi.
        * **Quota Equa:** Il prezzo puro matematico dell'evento ($1 / \\text{Probabilità}$), calcolato senza margini o commissioni del bookmaker.
        * **Quota Minima (Valore):** Il prezzo minimo a cui conviene entrare sul mercato. Se il tuo bookmaker offre una quota pari o superiore a questo valore, la giocata ha un vantaggio matematico (Value Bet). Sotto questa quota è **NO BET**.
        * **Edge:** Il margine di vantaggio percentuale stimato rispetto alla quota implicita del bookmaker.
        * **Stake:** L'importo monetario raccomandato per massimizzare il rendimento proteggendo il capitale.
        """)
    
    if matches:
        all_opportunities = []
        for m in matches:
            h = clean_name(m.get("home_team", ""))
            a = clean_name(m.get("away_team", ""))
            m_title = f"{h} vs {a}"
            m_date = m.get("commence_time", "")[:10]
            
            all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_team_goals_over15(h, a, True, min_edge_val)})
            all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_team_goals_over15(a, h, False, min_edge_val)})
            
            for l_c in [8.5, 9.5, 10.5]:
                all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_corners_multiline(h, a, l_c, min_edge_val)})
        
        valid_opps = [op for op in all_opportunities if op["min_odds"] >= 1.40]
        valid_opps.sort(key=lambda x: x["prob"], reverse=True)
        top5 = valid_opps[:5]
        
        table_data = []
        for idx, item in enumerate(top5):
            pos = idx + 1
            if is_premium or pos in [4, 5]:
                table_data.append({
                    "POS": f"#{pos}", "PARTITA": item["match"], "DATA": item["date"],
                    "MERCATO": item["market"], "PROB. MODELLO": f"{item['prob']*100:.1f}%",
                    "QUOTA EQUA": f"{item['fair_odds']:.2f}",
                    "QUOTA MINIMA (VALORE)": f"{item['min_odds']:.2f}"
                })
            else:
                table_data.append({
                    "POS": f"#{pos}", "PARTITA": item["match"], "DATA": item["date"],
                    "MERCATO": "[BLOCCATO - PIANO PREMIUM]", "PROB. MODELLO": "---",
                    "QUOTA EQUA": "---", "QUOTA MINIMA (VALORE)": "---"
                })
        
        st.table(pd.DataFrame(table_data))
        
        st.markdown("---")
        st.markdown("### SCHEDE MOTIVATE & VERIFICA QUOTA REALE")
        for idx, item in enumerate(top5):
            pos = idx + 1
            if is_premium or pos in [4, 5]:
                with st.expander(f"Report #{pos} | {item['match']} - {item['market']} (Quota Minima: {item['min_odds']:.2f})", expanded=(pos==1 or pos==4)):
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.metric("Probabilità Reale", f"{item['prob']*100:.1f}%")
                        st.write(f"**Quota Equa:** `{item['fair_odds']:.2f}` | **Quota Minima di Ingresso:** `{item['min_odds']:.2f}`")
                        st.info(f"**Dettaglio Tecnico:** {item['note']}")
                    with col_t2:
                        init_val = safe_odds_val(item['min_odds'])
                        odd_check = st.number_input(f"Inserisci Quota del tuo Bookmaker (#{pos})", min_value=1.01, max_value=20.0, value=init_val, step=0.02, key=f"top_odd_{idx}")
                        calc_edge = (item['prob'] * odd_check) - 1.0
                        k_p, k_e = MatchAnalystEngine.calculate_kelly(item['prob'], odd_check, current_bankroll, kelly_fraction)
                        if odd_check >= item['min_odds'] and calc_edge >= min_edge_val:
                            st.success(f"VALORE PRESENTE: Edge {calc_edge*100:+.2f}%\nStake: {k_p}% ({k_e:.2f} €)")
                            if st.button(f"REGISTRA GIOCATA #{pos}", key=f"btn_save_top_{idx}"):
                                save_user_bet(user_id, item["match"], item["market"], odd_check, k_e, calc_edge)
                                st.rerun()
                        else:
                            st.error(f"NO BET (Quota sotto soglia minima - Edge: {calc_edge*100:+.2f}%)")

# CAT 1: MERCATI PRINCIPALI
with tab1:
    st.markdown("### TOP 5 MERCATI PRINCIPALI (LIVE ODDS & POISSON)")
    st.caption("Classifica delle migliori 5 opportunità matematiche sui mercati live scaricati via API.")
    if matches:
        cat1_all = []
        for m in matches:
            h = clean_name(m.get("home_team", ""))
            a = clean_name(m.get("away_team", ""))
            m_title = f"{h} vs {a}"
            m_date = m.get("commence_time", "")[:10]
            
            h_met = get_metrics(h)
            a_met = get_metrics(a)
            lambda_tot = (h_met["gf_h"] + a_met["gf_a"] + a_met["ga_h"] + h_met["ga_a"]) / 2.0
            p_ov25 = float(1.0 - (poisson.pmf(0, lambda_tot) + poisson.pmf(1, lambda_tot) + poisson.pmf(2, lambda_tot)))
            p_un25 = 1.0 - p_ov25
            
            ov_odds_list = []
            un_odds_list = []
            for b in m.get("bookmakers", []):
                for market in b.get("markets", []):
                    if market["key"] == "totals":
                        for o in market.get("outcomes", []):
                            if o.get("name") == "Over" and o.get("point") == 2.5: ov_odds_list.append(o["price"])
                            elif o.get("name") == "Under" and o.get("point") == 2.5: un_odds_list.append(o["price"])
            
            if ov_odds_list:
                avg_ov = float(np.mean(ov_odds_list))
                edge_ov = (p_ov25 * avg_ov) - 1.0
                st_p_o, st_e_o = MatchAnalystEngine.calculate_kelly(p_ov25, avg_ov, current_bankroll, kelly_fraction)
                cat1_all.append({
                    "PARTITA": m_title, "DATA": m_date, "MERCATO": "Over 2.5 Totali",
                    "QUOTA LIVE": f"{avg_ov:.2f}", "PROB REALE": f"{p_ov25*100:.1f}%",
                    "EDGE": f"{edge_ov*100:+.2f}%", "STAKE": f"{st_p_o}% ({st_e_o:.2f} €)",
                    "edge_num": edge_ov, "prob_num": p_ov25, "odds_num": avg_ov, "stake_eur": st_e_o
                })
            if un_odds_list:
                avg_un = float(np.mean(un_odds_list))
                edge_un = (p_un25 * avg_un) - 1.0
                st_p_u, st_e_u = MatchAnalystEngine.calculate_kelly(p_un25, avg_un, current_bankroll, kelly_fraction)
                cat1_all.append({
                    "PARTITA": m_title, "DATA": m_date, "MERCATO": "Under 2.5 Totali",
                    "QUOTA LIVE": f"{avg_un:.2f}", "PROB REALE": f"{p_un25*100:.1f}%",
                    "EDGE": f"{edge_un*100:+.2f}%", "STAKE": f"{st_p_u}% ({st_e_u:.2f} €)",
                    "edge_num": edge_un, "prob_num": p_un25, "odds_num": avg_un, "stake_eur": st_e_u
                })
                
        cat1_all.sort(key=lambda x: x["edge_num"], reverse=True)
        top5_cat1 = cat1_all[:5]
        
        if top5_cat1:
            disp_c1 = [{k: v for k, v in item.items() if not k.endswith("_num") and k != "stake_eur"} for item in top5_cat1]
            st.table(pd.DataFrame(disp_c1))
            
            st.markdown("---")
            st.markdown("### REGISTRA GIOCATA MERCATI PRINCIPALI")
            c1_opts = [f"#{i+1} | {b['PARTITA']} | {b['MERCATO']} @ {b['QUOTA LIVE']}" for i, b in enumerate(top5_cat1)]
            sel_c1_i = st.selectbox("Seleziona Scommessa Live da Registrare", range(len(c1_opts)), format_func=lambda x: c1_opts[x])
            if st.button("SALVA SCOMMESSA LIVE NEL BANKROLL"):
                chosen_c1 = top5_cat1[sel_c1_i]
                save_user_bet(user_id, chosen_c1["PARTITA"], chosen_c1["MERCATO"], chosen_c1["odds_num"], chosen_c1["stake_eur"], chosen_c1["edge_num"])
                st.success("Scommessa live registrata.")
                st.rerun()
        else:
            st.info("Nessuna quota live disponibile al momento.")

# CAT 2: STATISTICHE, TATTICA & FORMAZIONI IN CAMPO (11 vs 11)
with tab2:
    st.markdown("### STATISTICHE, QUADRO TATTICO & DISPOSIZIONE IN CAMPO")
    st.caption("Schieramento in campo dei 22 titolari probabili/ufficiali e quote minime per Over 1.5 Gol e Corner.")
    
    if matches:
        match_options = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
        sel_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options)), format_func=lambda x: match_options[x], key="c2_match_sel")
        
        m_sel = matches[sel_idx]
        h2 = clean_name(m_sel["home_team"])
        a2 = clean_name(m_sel["away_team"])
        
        h_met2 = get_metrics(h2)
        a_met2 = get_metrics(a2)
        
        lineup_status, ref_detected = check_fixture_details(h2, a2, FOOTBALL_KEY)
        
        if lineup_status == "UFFICIALE":
            st.markdown(f'<div class="lineup-badge-off">FORMAZIONE UFFICIALE (AIA / FIGC)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="lineup-badge-prob">FORMAZIONE PROBABILE (Pre-Partita)</div>', unsafe_allow_html=True)
            
        st.markdown(f"#### Quadro Tattico: {h2} ({h_met2['modulo']}) vs {a2} ({a_met2['modulo']})")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"""
            <div class="tactical-card">
                <b>{h2.upper()} (Casa)</b><br>
                • <b>Modulo:</b> {h_met2['modulo']}<br>
                • <b>Identità Tattica:</b> {h_met2['stile']}<br>
                • <b>Possesso Palla Stimato:</b> {h_met2['possesso']:.1f}%<br>
                • <b>Cross Medi:</b> {h_met2['cross']:.1f} / gara
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            st.markdown(f"""
            <div class="tactical-card">
                <b>{a2.upper()} (Trasferta)</b><br>
                • <b>Modulo:</b> {a_met2['modulo']}<br>
                • <b>Identità Tattica:</b> {a_met2['stile']}<br>
                • <b>Possesso Palla Stimato:</b> {a_met2['possesso']:.1f}%<br>
                • <b>Cross Medi:</b> {a_met2['cross']:.1f} / gara
            </div>
            """, unsafe_allow_html=True)
            
        # DISPOSIZIONE IN CAMPO DEI 22 CALCIATORI (11 vs 11)
        st.markdown("#### Disposizione in Campo dei 22 Calciatori (11 vs 11)")
        
        h2_squad = fetch_live_team_squad(h2, FOOTBALL_KEY)
        a2_squad = fetch_live_team_squad(a2, FOOTBALL_KEY)
        
        col_p_h, col_p_a = st.columns(2)
        with col_p_h:
            st.markdown(f"**Schieramento {h2} ({h_met2['modulo']})**")
            gk_h = [p['name'] for p in h2_squad if p['role'] == 'Goalkeeper'][:1]
            def_h = [p['name'] for p in h2_squad if p['role'] == 'Defender'][:4]
            mid_h = [p['name'] for p in h2_squad if p['role'] == 'Midfielder'][:4]
            att_h = [p['name'] for p in h2_squad if p['role'] == 'Attacker'][:2]
            
            st.markdown(f"""
            <div class="pitch-board">
                <div class="pitch-row">🧤 <b>Portiere:</b> {', '.join(gk_h) if gk_h else 'Titolare da definire'}</div>
                <div class="pitch-row">🛡️ <b>Difesa:</b> {', '.join(def_h) if def_h else 'Linea difensiva a 4'}</div>
                <div class="pitch-row">⚙️ <b>Centrocampo:</b> {', '.join(mid_h) if mid_h else 'Reparto mediano'}</div>
                <div class="pitch-row">⚡ <b>Attacco:</b> {', '.join(att_h) if att_h else 'Attacco titolare'}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_p_a:
            st.markdown(f"**Schieramento {a2} ({a_met2['modulo']})**")
            gk_a = [p['name'] for p in a2_squad if p['role'] == 'Goalkeeper'][:1]
            def_a = [p['name'] for p in a2_squad if p['role'] == 'Defender'][:4]
            mid_a = [p['name'] for p in a2_squad if p['role'] == 'Midfielder'][:4]
            att_a = [p['name'] for p in a2_squad if p['role'] == 'Attacker'][:2]
            
            st.markdown(f"""
            <div class="pitch-board">
                <div class="pitch-row">🧤 <b>Portiere:</b> {', '.join(gk_a) if gk_a else 'Titolare da definire'}</div>
                <div class="pitch-row">🛡️ <b>Difesa:</b> {', '.join(def_a) if def_a else 'Linea difensiva'}</div>
                <div class="pitch-row">⚙️ <b>Centrocampo:</b> {', '.join(mid_a) if mid_a else 'Reparto mediano'}</div>
                <div class="pitch-row">⚡ <b>Attacco:</b> {', '.join(att_a) if att_a else 'Attacco titolare'}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        # CALCOLATORE STATISTICHE SQUADRA
        col_c2_1, col_c2_2 = st.columns(2)
        with col_c2_1:
            st.markdown("#### Mercato Over 1.5 Gol Squadra")
            team_choice = st.radio("Seleziona Squadra", [h2, a2], horizontal=True, key="c2_team_choice")
            is_home_sel = (team_choice == h2)
            opp_choice = a2 if is_home_sel else h2
            
            res_g = MatchAnalystEngine.analyze_team_goals_over15(team_choice, opp_choice, is_home_sel, min_edge_val)
            st.metric("Probabilità Modello", f"{res_g['prob']*100:.1f}%")
            st.write(f"**Quota Equa:** `{res_g['fair_odds']:.2f}` | **Quota Minima:** `{res_g['min_odds']:.2f}`")
            st.caption(res_g["note"])
            
            init_g = safe_odds_val(res_g['min_odds'])
            odd_g_in = st.number_input("Quota sul tuo Bookmaker (Over 1.5 Gol)", min_value=1.01, max_value=20.0, value=init_g, step=0.02, key="odd_g_in")
            edge_g = (res_g['prob'] * odd_g_in) - 1.0
            kp_g, ke_g = MatchAnalystEngine.calculate_kelly(res_g['prob'], odd_g_in, current_bankroll, kelly_fraction)
            if odd_g_in >= res_g['min_odds'] and edge_g >= min_edge_val:
                st.success(f"VALORE PRESENTE: Edge {edge_g*100:+.2f}% | Stake: {kp_g}% ({ke_g:.2f} €)")
                if st.button("SALVA BET GOL", key="btn_save_g"):
                    save_user_bet(user_id, f"{h2} vs {a2}", res_g["market"], odd_g_in, ke_g, edge_g)
                    st.rerun()
            else:
                st.error(f"NO BET (Quota insufficiente - Edge: {edge_g*100:+.2f}%)")
                
        with col_c2_2:
            st.markdown("#### Mercato Calci d'Angolo Multi-Linea")
            line_corn = st.selectbox("Linea Corner Totali", [7.5, 8.5, 9.5, 10.5, 11.5], index=2, key="c2_line_corn")
            res_c = MatchAnalystEngine.analyze_corners_multiline(h2, a2, line_corn, min_edge_val)
            st.metric("Probabilità Modello", f"{res_c['prob']*100:.1f}%")
            st.write(f"**Quota Equa:** `{res_c['fair_odds']:.2f}` | **Quota Minima:** `{res_c['min_odds']:.2f}`")
            st.caption(res_c["note"])
            
            init_c = safe_odds_val(res_c['min_odds'])
            odd_c_in = st.number_input("Quota sul tuo Bookmaker (Corner)", min_value=1.01, max_value=20.0, value=init_c, step=0.02, key="odd_c_in")
            edge_c = (res_c['prob'] * odd_c_in) - 1.0
            kp_c, ke_c = MatchAnalystEngine.calculate_kelly(res_c['prob'], odd_c_in, current_bankroll, kelly_fraction)
            if odd_c_in >= res_c['min_odds'] and edge_c >= min_edge_val:
                st.success(f"VALORE PRESENTE: Edge {edge_c*100:+.2f}% | Stake: {kp_c}% ({ke_c:.2f} €)")
                if st.button("SALVA BET CORNER", key="btn_save_c"):
                    save_user_bet(user_id, f"{h2} vs {a2}", res_c["market"], odd_c_in, ke_c, edge_c)
                    st.rerun()
            else:
                st.error(f"NO BET (Quota insufficiente - Edge: {edge_c*100:+.2f}%)")

# CAT 3: PRESTAZIONI CALCIATORI & PORTIERI (Rose Live da API-Football)
with tab3:
    st.markdown("### PRESTAZIONI CALCIATORI & PORTIERI (ROSE LIVE AGGIORNATE)")
    st.caption("Analisi per tiri in porta, falli commessi e parate del portiere su rose live sincronizzate.")
    
    if matches:
        match_options_c3 = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
        sel_m3_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options_c3)), format_func=lambda x: match_options_c3[x], key="c3_match_sel")
        
        m3 = matches[sel_m3_idx]
        h3 = clean_name(m3["home_team"])
        a3 = clean_name(m3["away_team"])
        
        with st.spinner("Sincronizzazione rose live con API-Football..."):
            h3_players = fetch_live_team_squad(h3, FOOTBALL_KEY)
            a3_players = fetch_live_team_squad(a3, FOOTBALL_KEY)
            
        lineup_st3, ref_detected3 = check_fixture_details(h3, a3, FOOTBALL_KEY)
        
        st.markdown("---")
        tab_h, tab_a = st.tabs([f"Squadra Casa: {h3}", f"Squadra Trasferta: {a3}"])
        
        def render_player_analysis(players_list, team_name, opp_team, key_prefix):
            if not players_list:
                st.warning(f"Caricamento rosa in corso per {team_name}...")
                return
            p_display = [f"{p['name']} ({p['role']} #{p['number']})" for p in players_list]
            sel_p_i = st.selectbox(f"Seleziona Calciatore ({team_name})", range(len(p_display)), format_func=lambda x: p_display[x], key=f"{key_prefix}_sel")
            chosen_p = players_list[sel_p_i]
            
            st.markdown(f"**Ruolo:** `{chosen_p['role']}` | **Avversario Diretto:** `{opp_team}`")
            
            if chosen_p["role"] == "Goalkeeper":
                st.markdown("#### Mercato: Parate Portiere")
                saves_line = st.selectbox("Linea Parate", [1.5, 2.5, 3.5, 4.5], index=1, key=f"{key_prefix}_saves_line")
                saves_res = MatchAnalystEngine.analyze_goalkeeper_saves(chosen_p, opp_team, saves_line, min_edge_val)
                st.metric("Probabilità Modello", f"{saves_res['prob']*100:.1f}%")
                st.write(f"**Quota Equa:** `{saves_res['fair_odds']:.2f}` | **Quota Minima:** `{saves_res['min_odds']:.2f}`")
                st.caption(saves_res["note"])
                
                init_sv = safe_odds_val(saves_res['min_odds'])
                odd_sv_in = st.number_input("Quota Parate Bookmaker", min_value=1.01, max_value=20.0, value=init_sv, step=0.02, key=f"{key_prefix}_odd_sv")
                edge_sv = (saves_res['prob'] * odd_sv_in) - 1.0
                kpsv, kesv = MatchAnalystEngine.calculate_kelly(saves_res['prob'], odd_sv_in, current_bankroll, kelly_fraction)
                if odd_sv_in >= saves_res['min_odds'] and edge_sv >= min_edge_val:
                    st.success(f"VALORE PRESENTE: Edge {edge_sv*100:+.2f}% | Stake: {kpsv}% ({kesv:.2f} €)")
                    if st.button("SALVA BET PARATE", key=f"{key_prefix}_btn_sv"):
                        save_user_bet(user_id, f"{h3} vs {a3}", saves_res["market"], odd_sv_in, kesv, edge_sv)
                        st.rerun()
                else:
                    st.error(f"NO BET (Quota insufficiente - Edge: {edge_sv*100:+.2f}%)")
            else:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("#### Mercato: Tiri in Porta")
                    sot_line = st.selectbox("Linea Tiri in Porta", [0.5, 1.5, 2.5], index=0, key=f"{key_prefix}_sot_line")
                    sot_res = MatchAnalystEngine.analyze_player_sot(chosen_p, opp_team, sot_line, min_edge_val)
                    st.metric("Probabilità Modello", f"{sot_res['prob']*100:.1f}%")
                    st.write(f"**Quota Equa:** `{sot_res['fair_odds']:.2f}` | **Quota Minima:** `{sot_res['min_odds']:.2f}`")
                    
                    init_sot = safe_odds_val(sot_res['min_odds'])
                    odd_sot_in = st.number_input("Quota Tiri Bookmaker", min_value=1.01, max_value=20.0, value=init_sot, step=0.02, key=f"{key_prefix}_odd_sot")
                    edge_s = (sot_res['prob'] * odd_sot_in) - 1.0
                    kps, kes = MatchAnalystEngine.calculate_kelly(sot_res['prob'], odd_sot_in, current_bankroll, kelly_fraction)
                    if odd_sot_in >= sot_res['min_odds'] and edge_s >= min_edge_val:
                        st.success(f"VALORE PRESENTE: Edge {edge_s*100:+.2f}% | Stake: {kps}% ({kes:.2f} €)")
                        if st.button("SALVA BET TIRI", key=f"{key_prefix}_btn_sot"):
                            save_user_bet(user_id, f"{h3} vs {a3}", sot_res["market"], odd_sot_in, kes, edge_s)
                            st.rerun()
                    else:
                        st.error(f"NO BET (Quota insufficiente - Edge: {edge_s*100:+.2f}%)")
                        
                with col_m2:
                    st.markdown("#### Mercato: Falli Commessi")
                    foul_line = st.selectbox("Linea Falli Commessi", [0.5, 1.5, 2.5], index=1, key=f"{key_prefix}_foul_line")
                    foul_res = MatchAnalystEngine.analyze_player_fouls(chosen_p, opp_team, {"name": "CAN A-B", "fouls_avg": 26.0, "severity": "Standard"}, foul_line, min_edge_val)
                    st.metric("Probabilità Modello", f"{foul_res['prob']*100:.1f}%")
                    st.write(f"**Quota Equa:** `{foul_res['fair_odds']:.2f}` | **Quota Minima:** `{foul_res['min_odds']:.2f}`")
                    
                    init_fl = safe_odds_val(foul_res['min_odds'])
                    odd_fl_in = st.number_input("Quota Falli Bookmaker", min_value=1.01, max_value=20.0, value=init_fl, step=0.02, key=f"{key_prefix}_odd_fl")
                    edge_f = (foul_res['prob'] * odd_fl_in) - 1.0
                    kpf, kef = MatchAnalystEngine.calculate_kelly(foul_res['prob'], odd_fl_in, current_bankroll, kelly_fraction)
                    if odd_fl_in >= foul_res['min_odds'] and edge_f >= min_edge_val:
                        st.success(f"VALORE PRESENTE: Edge {edge_f*100:+.2f}% | Stake: {kpf}% ({kef:.2f} €)")
                        if st.button("SALVA BET FALLI", key=f"{key_prefix}_btn_fl"):
                            save_user_bet(user_id, f"{h3} vs {a3}", foul_res["market"], odd_fl_in, kef, edge_f)
                            st.rerun()
                    else:
                        st.error(f"NO BET (Quota insufficiente - Edge: {edge_f*100:+.2f}%)")
        
        with tab_h:
            render_player_analysis(h3_players, h3, a3, "h_tab")
        with tab_a:
            render_player_analysis(a3_players, a3, h3, "a_tab")

# CAT 4: FOCUS DISCIPLINARE & ARBITRI (Organico Completo CAN A-B)
with tab4:
    st.markdown("### FOCUS DISCIPLINARE & ARBITRI (ORGANICO CAN A-B)")
    st.caption("Organico completo dei direttori di gara Serie A & Serie B con calcolo quote sui cartellini.")
    
    if matches:
        match_options_c4 = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
        sel_m4_idx = st.selectbox("Seleziona Incontro", range(len(match_options_c4)), format_func=lambda x: match_options_c4[x], key="c4_match_sel")
        
        m4 = matches[sel_m4_idx]
        h4 = clean_name(m4["home_team"])
        a4 = clean_name(m4["away_team"])
        
        lineup_st4, ref_auto = check_fixture_details(h4, a4, FOOTBALL_KEY)
        
        col_ref_sel, col_ref_status = st.columns([2, 1])
        ref_names_list = sorted(list(SERIE_A_REFEREES_DB.keys()))
        default_ref_idx = 0
        
        if ref_auto:
            for i, rk in enumerate(ref_names_list):
                if rk in ref_auto.lower() or ref_auto.lower() in SERIE_A_REFEREES_DB[rk]["name"].lower():
                    default_ref_idx = i
                    break
                    
        with col_ref_sel:
            chosen_ref_key = st.selectbox(
                "Seleziona Direttore di Gara (CAN Serie A & B)",
                ref_names_list,
                index=default_ref_idx,
                format_func=lambda x: SERIE_A_REFEREES_DB[x]["name"]
            )
            ref_data = SERIE_A_REFEREES_DB[chosen_ref_key]
            
        with col_ref_status:
            st.write("")
            st.write("")
            if ref_auto and chosen_ref_key in ref_auto.lower():
                st.success("Designazione AIA Rilevata da API")
            else:
                st.info("Arbitro Selezionato da Ruolo CAN")
                
        col_ref1, col_ref2 = st.columns(2)
        with col_ref1:
            st.markdown(f"#### Metriche Ufficiali: `{ref_data['name']}`")
            st.write(f"- **Media Cartellini / Partita:** `{ref_data['cards_avg']:.1f}`")
            st.write(f"- **Media Falli Fischiati / Partita:** `{ref_data['fouls_avg']:.1f}`")
            st.write(f"- **Indice di Severità Disciplinare:** `{ref_data['severity']}`")
            st.caption("Dati storici registrati AIA / CAN per la stagione agonistica in corso.")
                
        with col_ref2:
            st.markdown("#### Calcolo Cartellini Totali")
            cards_line = st.selectbox("Linea Cartellini Totali", [3.5, 4.5, 5.5], index=1, key="c4_cards_line")
            disc_res = MatchAnalystEngine.analyze_disciplinary_match(h4, a4, ref_data, cards_line, min_edge_val)
            
            st.metric("Probabilità Modello", f"{disc_res['prob']*100:.1f}%")
            st.write(f"**Quota Equa:** `{disc_res['fair_odds']:.2f}` | **Quota Minima:** `{disc_res['min_odds']:.2f}`")
            
            init_cd = safe_odds_val(disc_res['min_odds'])
            odd_card_in = st.number_input("Quota Cartellini Bookmaker", min_value=1.01, max_value=20.0, value=init_cd, step=0.02, key="odd_card_in")
            edge_card = (disc_res['prob'] * odd_card_in) - 1.0
            kpc, kec = MatchAnalystEngine.calculate_kelly(disc_res['prob'], odd_card_in, current_bankroll, kelly_fraction)
            if odd_card_in >= disc_res['min_odds'] and edge_card >= min_edge_val:
                st.success(f"VALORE PRESENTE: Edge {edge_card*100:+.2f}% | Stake: {kpc}% ({kec:.2f} €)")
                if st.button("SALVA BET CARTELLINI", key="btn_save_card"):
                    save_user_bet(user_id, f"{h4} vs {a4}", f"Over {cards_line} Cartellini", odd_card_in, kec, edge_card)
                    st.rerun()
            else:
                st.error(f"NO BET (Quota insufficiente - Edge: {edge_card*100:+.2f}%)")

# REGISTRO SCOMMESSE
with tab5:
    st.markdown("### STORICO PERSONALE SCOMMESSE")
    user_bets = fetch_user_bets(user_id)
    
    if not user_bets.empty:
        display_df = user_bets[["created_at", "match", "market", "odds", "stake", "status", "profit"]].copy()
        display_df["created_at"] = pd.to_datetime(display_df["created_at"]).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df,
            column_config={
                "created_at": "DATA", "match": "PARTITA", "market": "MERCATO",
                "odds": st.column_config.NumberColumn("QUOTA", format="%.2f"),
                "stake": st.column_config.NumberColumn("STAKE (€)", format="%.2f €"),
                "status": "ESITO",
                "profit": st.column_config.NumberColumn("PROFITTO/PERDITA (€)", format="%.2f €")
            },
            use_container_width=True, hide_index=True
        )
        
        st.markdown("### CHIUDI ESITO SCOMMESSA")
        pending = user_bets[user_bets["status"] == "IN CORSO"]
        
        if not pending.empty:
            col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
            with col_u1:
                bet_to_update = st.selectbox("Scommessa da Concludere", pending["id"].tolist(), format_func=lambda x: f"ID {x} | {pending.loc[pending['id']==x, 'match'].values[0]} - {pending.loc[pending['id']==x, 'market'].values[0]}")
            with col_u2:
                new_status = st.selectbox("Esito", ["VINTA", "PERSA"])
            with col_u3:
                st.write("")
                st.write("")
                if st.button("AGGIORNA ESITO", use_container_width=True):
                    row = pending[pending["id"] == bet_to_update].iloc[0]
                    update_bet_status(bet_to_update, new_status, float(row["odds"]), float(row["stake"]))
                    st.success("Esito registrato con successo.")
                    st.rerun()
        else:
            st.info("Non ci sono scommesse in corso.")
    else:
        st.info("Nessuna scommessa registrata nel database.")

# GESTIONE ACCOUNT
with tab6:
    st.markdown("### GESTIONE ACCOUNT")
    with st.expander("Il Mio Profilo", expanded=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Email:** `{user_email}`")
            st.markdown(f"**Stato Abbonamento:** `{tier_label}`")
        with col_p2:
            st.markdown(f"**ID Utente:** `{user_id}`")
            
    with st.expander("Modifica Password"):
        new_pwd = st.text_input("Nuova Password (min. 6 caratteri)", type="password", key="chg_pwd")
        conf_pwd = st.text_input("Conferma Nuova Password", type="password", key="conf_pwd")
        if st.button("AGGIORNA PASSWORD", use_container_width=True):
            if len(new_pwd) < 6:
                st.warning("La password deve contenere almeno 6 caratteri.")
            elif new_pwd != conf_pwd:
                st.error("Le password inserite non coincidono.")
            else:
                ok, msg = update_user_password(new_pwd)
                if ok:
                    st.success(msg)
                else:
                    st.error(f"Errore: {msg}")
