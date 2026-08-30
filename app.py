import datetime
import numpy as np
import pandas as pd
import requests
from scipy.stats import poisson
import streamlit as st

from squads_db import get_team_squad_from_db, SERIE_A_TACTICS, KNOWN_STARTERS, clean_team_name

# Configurazione della pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS Dark Fintech
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
    
    [data-testid="stToolbar"], footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* FIX DEFINITIVO MENU LATERALE SU SMARTPHONE & SAFARI */
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
    [data-testid="stSidebarCollapsedControl"] button {
        color: #0B132B !important;
        background-color: transparent !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: #0B132B !important;
        stroke: #0B132B !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    /* FIX ICONA MOSTRA PASSWORD */
    [data-testid="stTextInput"] button {
        color: #2DD4BF !important;
        background-color: #2D3A5D !important;
        border-radius: 4px !important;
        border: 1px solid #3B4D78 !important;
        margin-right: 4px !important;
    }
    [data-testid="stTextInput"] button svg {
        fill: #2DD4BF !important;
        stroke: #2DD4BF !important;
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
        color: #EF4444;
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

    .free-scan-banner {
        background-color: #131D38;
        border: 2px solid #2DD4BF;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
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
    
    .injury-box {
        background-color: rgba(239, 68, 68, 0.10);
        border: 1px solid #EF4444;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 10px;
        margin-bottom: 14px;
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
    
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
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

def safe_odds_val(val, min_v=1.01, max_v=20.0):
    try:
        v = float(val)
        if np.isnan(v) or np.isinf(v) or v < min_v: return min_v
        if v > max_v: return max_v
        return round(v, 2)
    except Exception:
        return min_v

# Parametri Secrets
SB_URL = st.secrets.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = st.secrets.get("SUPABASE_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")
FOOTBALL_KEY = st.secrets.get("FOOTBALL_API_KEY", "f59b5ad05a6b45fa5f19582d3e493f7f")

# Sessione Utente
if "user" not in st.session_state: st.session_state.user = None
if "user_tier" not in st.session_state: st.session_state.user_tier = "free"
if "access_token" not in st.session_state: st.session_state.access_token = None
if "last_free_scan_week" not in st.session_state: st.session_state.last_free_scan_week = None

def get_headers(token=None):
    auth_bearer = token or SB_KEY
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {auth_bearer}",
        "Content-Type": "application/json",
    }

def get_current_week_str():
    now = datetime.datetime.now()
    year, week_num, _ = now.isocalendar()
    return f"{year}-W{week_num:02d}"

def check_free_scan_status(user_id):
    if st.session_state.user_tier == "premium":
        return True, "Illimitate (Piano Premium)", 999
    
    current_week = get_current_week_str()
    used_week = st.session_state.get("last_free_scan_week")
    
    if not used_week and SB_URL and SB_KEY and user_id and user_id != "local_user":
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/profiles?id=eq.{user_id}&select=last_free_scan_week"
        try:
            res = requests.get(url, headers=get_headers(token), timeout=5)
            if res.status_code == 200 and res.json():
                used_week = res.json()[0].get("last_free_scan_week")
                st.session_state.last_free_scan_week = used_week
        except Exception:
            pass
            
    if used_week == current_week:
        return False, "0/1 Rimaste (Reset Lunedì)", 0
    else:
        return True, "1/1 Disponibile per questa settimana", 1

def consume_free_scan(user_id):
    current_week = get_current_week_str()
    st.session_state.last_free_scan_week = current_week
    
    if SB_URL and SB_KEY and user_id and user_id != "local_user":
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/profiles?id=eq.{user_id}"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        try:
            requests.patch(url, json={"last_free_scan_week": current_week}, headers=hdrs, timeout=5)
        except Exception:
            pass

# Autenticazione Supabase
def login_user(email, password):
    if not SB_URL or not SB_KEY:
        st.session_state.user = {"email": email, "id": "local_user"}
        st.session_state.user_tier = "free"
        return True, None
    url = f"{SB_URL}/auth/v1/token?grant_type=password"
    try:
        res = requests.post(url, json={"email": email, "password": password}, headers=get_headers(), timeout=10)
        if res.status_code == 200:
            data = res.json()
            st.session_state.user = data.get("user")
            st.session_state.access_token = data.get("access_token")
            u_id = data["user"]["id"]
            prof_url = f"{SB_URL}/rest/v1/profiles?id=eq.{u_id}&select=tier,last_free_scan_week"
            prof_res = requests.get(prof_url, headers=get_headers(data.get("access_token")), timeout=10)
            if prof_res.status_code == 200 and prof_res.json():
                st.session_state.user_tier = prof_res.json()[0].get("tier", "free")
                st.session_state.last_free_scan_week = prof_res.json()[0].get("last_free_scan_week")
            return True, None
        return False, "Credenziali non corrette."
    except Exception as e:
        return False, str(e)

def register_user(email, password):
    if not SB_URL or not SB_KEY: return False, "Chiavi Supabase mancanti nei Secrets."
    url = f"{SB_URL}/auth/v1/signup"
    try:
        res = requests.post(url, json={"email": email, "password": password}, headers=get_headers(), timeout=10)
        if res.status_code in [200, 201]: return True, "Registrazione completata. Puoi accedere ora."
        return False, "Errore registrazione."
    except Exception as e:
        return False, str(e)

def logout_user():
    st.session_state.user = None
    st.session_state.user_tier = "free"
    st.session_state.access_token = None
    st.session_state.last_free_scan_week = None

def redeem_vip_code(user_id, code_input):
    valid_promo_codes = ["valuebet2026", "vip2026", "pro2026", "calcio2026"]
    if code_input.strip().lower() in valid_promo_codes:
        if SB_URL and SB_KEY and user_id and user_id != "local_user":
            token = st.session_state.get("access_token")
            url = f"{SB_URL}/rest/v1/profiles?id=eq.{user_id}"
            hdrs = get_headers(token)
            hdrs["Prefer"] = "return=representation"
            try: requests.patch(url, json={"tier": "premium"}, headers=hdrs, timeout=10)
            except Exception: pass
        st.session_state.user_tier = "premium"
        return True, "Codice valido. Piano Premium attivato."
    return False, "Codice non valido."

# Schermata Login
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
                    if ok: st.rerun()
                    else: st.error(err)
        with tab_reg:
            reg_email = st.text_input("Email", key="reg_email")
            reg_pwd = st.text_input("Password (min. 6 caratteri)", type="password", key="reg_pwd")
            if st.button("REGISTRATI", use_container_width=True):
                if reg_email and len(reg_pwd) >= 6:
                    ok, msg = register_user(reg_email, reg_pwd)
                    if ok: st.success(msg)
                    else: st.error(msg)
    st.stop()

# Dati Utente
user_data = st.session_state.user if isinstance(st.session_state.user, dict) else {}
user_email = user_data.get("email", "")
user_id = user_data.get("id", "")

# Infortuni Cloud
def fetch_injuries():
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/team_injuries?select=*&order=created_at.desc"
        try:
            res = requests.get(url, headers=get_headers(token), timeout=10)
            if res.status_code == 200 and res.json(): return pd.DataFrame(res.json())
        except Exception: pass
    return pd.DataFrame(columns=["id", "team", "player_name", "importance", "injury_type", "return_date"])

def save_injury(team, player_name, importance, injury_type, return_date):
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/team_injuries"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        payload = {"team": team, "player_name": player_name, "importance": importance, "injury_type": injury_type, "return_date": return_date}
        try:
            res = requests.post(url, json=payload, headers=hdrs, timeout=10)
            return res.status_code in [200, 201]
        except Exception: pass
    return False

def delete_injury(injury_id):
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/team_injuries?id=eq.{injury_id}"
        try: requests.delete(url, headers=get_headers(token), timeout=10)
        except Exception: pass

# Cloud Scommesse
def fetch_user_bets(u_id):
    if SB_URL and SB_KEY and u_id:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets?user_id=eq.{u_id}&select=*&order=created_at.desc"
        try:
            res = requests.get(url, headers=get_headers(token), timeout=10)
            if res.status_code == 200 and res.json(): return pd.DataFrame(res.json())
        except Exception: pass
    return pd.DataFrame(columns=["id", "created_at", "match", "market", "odds", "stake", "ev", "status", "profit"])

def save_user_bet(u_id, match, market, odds, stake, ev):
    if SB_URL and SB_KEY and u_id:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        payload = {"user_id": u_id, "match": match, "market": market, "odds": float(odds), "stake": float(stake), "ev": float(ev), "status": "IN CORSO", "profit": 0.0}
        try:
            res = requests.post(url, json=payload, headers=hdrs, timeout=10)
            return res.status_code in [200, 201]
        except Exception: pass
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
        try: requests.patch(url, json={"status": new_status, "profit": profit_val}, headers=hdrs, timeout=10)
        except Exception: pass

# COMPETIZIONI & CAMPIONATI
LEAGUES_CONFIG = {
    "Serie A (Italia)": {"key": "soccer_italy_serie_a", "has_players": True},
    "Premier League (Inghilterra)": {"key": "soccer_epl", "has_players": False},
    "La Liga (Spagna)": {"key": "soccer_spain_la_liga", "has_players": False},
    "Bundesliga (Germania)": {"key": "soccer_germany_bundesliga", "has_players": False},
    "Ligue 1 (Francia)": {"key": "soccer_france_ligue_one", "has_players": False}
}

# ORGANICO ARBITRI CAN A-B
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

# Fetch Partite Live
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_real_matches(sport_key, api_key):
    if not api_key: return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200: return res.json()
    except Exception: pass
    return []

# RENDERING CAMPO TATTICO (11 TITOLARI COERENTI CON IL MODULO)
def render_visual_pitch_html(team_name, formation_str, players_list, injured_names=None):
    if not players_list:
        return f'<div style="background:#131D38;border:1px dashed #2DD4BF;border-radius:8px;padding:24px;text-align:center;color:#CBD5E1;">In attesa di caricare la distinta per <b>{team_name}</b></div>'
        
    if injured_names is None: injured_names = []
    
    # 1. Suddivisione dei giocatori per ruolo effettivo
    gk_pool = [p for p in players_list if p.get('role') == 'Goalkeeper']
    def_pool = [p for p in players_list if p.get('role') == 'Defender']
    mid_pool = [p for p in players_list if p.get('role') == 'Midfielder']
    att_pool = [p for p in players_list if p.get('role') == 'Attacker']
    
    # 2. Assegnazione prioritaria in base ai titolari noti della stagione
    known_list = KNOWN_STARTERS.get(clean_team_name(team_name), [])
    
    def sort_by_starter_priority(pool):
        # I titolari noti vanno all'inizio, tranne se infortunati
        def rank(p):
            p_name = p.get("name", "")
            is_inj = any(inj_n.lower() in p_name.lower() for inj_n in injured_names)
            is_star = any(star.lower() in p_name.lower() for star in known_list)
            if is_inj: return 99  # Infortunato va in fondo
            if is_star: return 1  # Titolare noto va per primo
            return 10
        return sorted(pool, key=rank)
        
    sorted_gks = sort_by_starter_priority(gk_pool)
    sorted_defs = sort_by_starter_priority(def_pool)
    sorted_mids = sort_by_starter_priority(mid_pool)
    sorted_atts = sort_by_starter_priority(att_pool)
    
    # 1 Solo Portiere
    gk_player = sorted_gks[0] if sorted_gks else {"name": "Portiere", "number": "1", "role": "Goalkeeper"}
    
    # Numero di titolari per reparto in base al modulo
    num_d, num_m, num_a = 4, 3, 3
    if "3-5-2" in formation_str: num_d, num_m, num_a = 3, 5, 2
    elif "4-2-3-1" in formation_str: num_d, num_m, num_a = 4, 5, 1
    elif "3-4-2-1" in formation_str: num_d, num_m, num_a = 3, 4, 3
    elif "4-3-3" in formation_str: num_d, num_m, num_a = 4, 3, 3
    elif "5-3-2" in formation_str: num_d, num_m, num_a = 5, 3, 2
    
    selected_defs = sorted_defs[:num_d]
    selected_mids = sorted_mids[:num_m]
    selected_atts = sorted_atts[:num_a]
    
    # Riempimento riserve se mancano titolari (solo con giocatori di movimento, mai portieri)
    outfield_reserves = sorted_defs[num_d:] + sorted_mids[num_m:] + sorted_atts[num_a:]
    while len(selected_defs) < num_d and outfield_reserves:
        selected_defs.append(outfield_reserves.pop(0))
    while len(selected_mids) < num_m and outfield_reserves:
        selected_mids.append(outfield_reserves.pop(0))
    while len(selected_atts) < num_a and outfield_reserves:
        selected_atts.append(outfield_reserves.pop(0))
    
    def badge(p, is_gk=False):
        p_name = p.get('name', 'Giocatore')
        is_inj = any(inj_n.lower() in p_name.lower() for inj_n in injured_names)
        c = "#EF4444" if is_inj else ("#EAB308" if is_gk else "#FFFFFF")
        tc = "#FFFFFF" if is_inj else "#0B132B"
        num = "OUT" if is_inj else p.get('number', '-')
        nom = f"<s>{p_name}</s>" if is_inj else p_name
        return f'<div style="text-align:center;width:70px;display:inline-block;margin:2px;"><div style="width:28px;height:28px;border-radius:50%;background:{c};color:{tc};font-weight:800;font-size:10px;display:flex;align-items:center;justify-content:center;margin:0 auto 2px auto;border:2px solid #000;">{num}</div><div style="color:#FFFFFF;font-size:10px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{nom}</div></div>'
        
    atts_h = "".join([badge(p) for p in selected_atts])
    mids_h = "".join([badge(p) for p in selected_mids])
    defs_h = "".join([badge(p) for p in selected_defs])
    gk_h = badge(gk_player, is_gk=True)
    
    return f'<div style="background:linear-gradient(180deg,#1e5138 0%,#143a28 100%);border:2px solid #2DD4BF;border-radius:8px;padding:14px 6px;text-align:center;margin-bottom:15px;"><div style="color:#2DD4BF;font-weight:800;font-size:13px;margin-bottom:10px;">{team_name.upper()} • {formation_str} (11 Titolari)</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{atts_h}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{mids_h}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{defs_h}</div><div style="display:flex;justify-content:center;">{gk_h}</div></div>'

# Motore Quantitativo
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
    def analyze_team_goals_over15(team, opp, is_home, min_edge=0.015, injuries_df=None):
        t_tac = SERIE_A_TACTICS.get(clean_team_name(team), {"possesso": 50.0, "cross": 17.0})
        o_tac = SERIE_A_TACTICS.get(clean_team_name(opp), {"possesso": 50.0, "cross": 17.0})
        
        base_xg = 1.60 if is_home else 1.25
        pos_factor = (t_tac["possesso"] / max(1.0, o_tac["possesso"]))
        xg_final = base_xg * (0.85 + 0.15 * pos_factor)
        
        # Penalizzazione infortuni
        if injuries_df is not None and not injuries_df.empty:
            t_inj = injuries_df[injuries_df["team"].str.lower() == clean_team_name(team).lower()]
            for _, r in t_inj.iterrows():
                if "Top Player" in r.get("importance", ""): xg_final *= 0.88
                
        prob = float(1.0 - (poisson.pmf(0, xg_final) + poisson.pmf(1, xg_final)))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over 1.5 Gol ({clean_team_name(team)})",
            "market_type": "Over 1.5 Gol Squadra",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xG Finale", "metric_val": f"{xg_final:.2f}",
            "note": f"xG Proiettato Modello: {xg_final:.2f} ({'Casa' if is_home else 'Trasferta'})"
        }

    @staticmethod
    def analyze_corners_multiline(h_team, a_team, line=9.5, min_edge=0.015):
        h_tac = SERIE_A_TACTICS.get(clean_team_name(h_team), {"cross": 17.0})
        a_tac = SERIE_A_TACTICS.get(clean_team_name(a_team), {"cross": 17.0})
        corners_final = 5.0 + (h_tac["cross"] + a_tac["cross"]) * 0.13
        prob = float(1.0 - poisson.cdf(line - 0.5, corners_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Corner Totali",
            "market_type": "Corner Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Corner Proiettati", "metric_val": f"{corners_final:.2f}",
            "note": f"Cross combinati: {h_tac['cross'] + a_tac['cross']:.1f} / gara"
        }

    @staticmethod
    def analyze_player_sot(player, opp_team, line=0.5, min_edge=0.015):
        xsot = player.get("sot_90", 1.0) * (84 / 90)
        prob = float(1.0 - poisson.cdf(line - 0.5, xsot))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Tiri in Porta ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xSOT Attesi", "metric_val": f"{xsot:.2f}",
            "note": f"Ruolo: {player['role']} | Media SOT/90m: {player.get('sot_90', 1.0):.2f}"
        }

    @staticmethod
    def analyze_player_fouls(player, opp_team, line=1.5, min_edge=0.015):
        xf = player.get("fouls_c_90", 1.0) * (85 / 90)
        prob = float(1.0 - poisson.cdf(line - 0.5, xf))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Commessi ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xFouls Attesi", "metric_val": f"{xf:.2f}",
            "note": f"Media Falli Commessi/90m: {player.get('fouls_c_90', 1.0):.2f}"
        }

    @staticmethod
    def analyze_player_fouls_drawn(player, opp_team, line=1.5, min_edge=0.015):
        pos = player.get("role", "Midfielder")
        base_fd = 1.85 if pos == "Attacker" else (1.40 if pos == "Midfielder" else 0.65)
        xf_drawn = base_fd * (86 / 90)
        prob = float(1.0 - poisson.cdf(line - 0.5, xf_drawn))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Subiti ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Falli Subiti Attesi", "metric_val": f"{xf_drawn:.2f}",
            "note": f"Indice falli subiti per 90 minuti (Ruolo: {pos})"
        }

    @staticmethod
    def analyze_goalkeeper_saves(player, opp_team, line=2.5, min_edge=0.015):
        xsaves = player.get("saves_90", 3.0)
        prob = float(1.0 - poisson.cdf(line - 0.5, xsaves))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Parate ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Parate Proiettate", "metric_val": f"{xsaves:.2f}",
            "note": "Media parate per 90 minuti (Save Rate stimato 72%)"
        }

    @staticmethod
    def analyze_disciplinary_match(h_team, a_team, ref_data, line=4.5, min_edge=0.015):
        cards_exp = ref_data.get("cards_avg", 4.5)
        prob = float(1.0 - poisson.cdf(line - 0.5, cards_exp))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Cartellini Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Cartellini Attesi", "metric_val": f"{cards_exp:.2f}",
            "note": f"Arbitro: {ref_data['name']} (Media: {ref_data['cards_avg']:.1f} cartellini - Severità: {ref_data['severity']})"
        }

# Header & Sidebar
is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE"

can_scan_free, scan_status_label, _ = check_free_scan_status(user_id)

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")
if not is_premium:
    st.sidebar.markdown(f"**Ricerche Settimanali:** `{scan_status_label}`")

st.sidebar.markdown("---")
st.sidebar.markdown("### SELEZIONA COMPETIZIONE")
selected_league_label = st.sidebar.selectbox("Campionato / Torneo", list(LEAGUES_CONFIG.keys()), index=0)
selected_league_cfg = LEAGUES_CONFIG[selected_league_label]
sport_api_key = selected_league_cfg["key"]
is_serie_a = selected_league_cfg["has_players"]

if not is_premium:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### SBLOCCO PIANO PRO")
    promo_code = st.sidebar.text_input("Codice VIP / Tester", placeholder="Inserisci qui il tuo codice...", type="password", key="side_promo_in")
    if st.sidebar.button("ATTIVA PREMIUM", use_container_width=True, key="side_promo_btn"):
        if promo_code:
            ok, msg = redeem_vip_code(user_id, promo_code)
            if ok: st.rerun()
            else: st.sidebar.error(msg)

    with st.expander("🔓 SBLOCCA PIANO PREMIUM", expanded=True):
        mob_code = st.text_input("Codice Promozionale VIP", placeholder="Inserisci qui il tuo codice...", type="password", key="mob_vip_in")
        if st.button("ATTIVA ORA", use_container_width=True, key="mob_vip_btn"):
            if mob_code:
                ok, msg = redeem_vip_code(user_id, mob_code)
                if ok: st.rerun()
                else: st.error(msg)

if st.sidebar.button("LOGOUT", use_container_width=True):
    logout_user()
    st.rerun()

st.sidebar.markdown("---")
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.select_slider("Frazione di Kelly", options=[0.25, 0.50], value=0.50)
min_edge_pct = st.sidebar.slider("Soglia Minima Edge (%)", min_value=1.0, max_value=3.0, value=1.5, step=0.5)
min_edge_val = min_edge_pct / 100.0

# Calcolo Bankroll Completo (Yield, Win Rate, Profitto)
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

injuries_df = fetch_injuries()
matches = fetch_real_matches(sport_api_key, ODDS_KEY)

st.title("VALUE BET ANALYZER")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)

if matches:
    st.markdown(f'<div class="round-badge">{selected_league_label.upper()} • {len(matches)} PARTITE LIVE DISPONIBILI</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="round-badge">{selected_league_label.upper()} • NESSUNA PARTITA IN PROGRAMMA NELLE PROSSIME 48-72H</div>', unsafe_allow_html=True)

# 8 SCHEDE PER SERIE A, 5 PER ALTRE LEGHE
if is_serie_a:
    tab_scan, tab1, tab2, tab3, tab4, tab_inj, tab5, tab6 = st.tabs([
        "Scanner Top 5 del Turno",
        "Mercati Principali",
        "Statistiche & Tattica Squadre",
        "Prestazioni Calciatori & Portieri",
        "Focus Disciplinare & Arbitri",
        "Infermeria Serie A",
        "Registro Scommesse",
        "Gestione Account"
    ])
else:
    tab_scan, tab1, tab2, tab5, tab6 = st.tabs([
        "Scanner Top 5 del Turno",
        "Mercati Principali",
        "Statistiche & Tattica Squadre",
        "Registro Scommesse",
        "Gestione Account"
    ])

# 1. SCANNER TOP 5 (CON 1 RICERCA SETTIMANALE PER FREE)
with tab_scan:
    st.markdown(f"### TOP 5 VALUE BETS ({selected_league_label.upper()})")
    user_has_access = is_premium
    if not is_premium:
        if can_scan_free:
            st.markdown(f"""
            <div class="free-scan-banner">
                <b style="color: #2DD4BF; font-size: 1.05rem;">🎯 PIANO FREE: 1 RICERCA SETTIMANALE DISPONIBILE (1/1)</b><br>
                Sblocca l'analisi completa di tutte le 5 giocate per questa settimana.
            </div>
            """, unsafe_allow_html=True)
            if st.button("ESEGUI LA TUA RICERCA GRATUITA SETTIMANALE", use_container_width=True, key="btn_use_free_scan"):
                consume_free_scan(user_id)
                st.rerun()
        else:
            st.markdown(f"""
            <div class="free-scan-banner" style="border-color: #F59E0B;">
                <b style="color: #FCD34D; font-size: 1.05rem;">🔒 LIMITE SETTIMANALE RAGGIUNTO (0/1)</b><br>
                Hai già utilizzato la tua ricerca gratuita. Reset automatico previsto per <b>lunedì prossimo</b>.
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.get("last_free_scan_week") == get_current_week_str():
                user_has_access = True
                
    if matches:
        all_opportunities = []
        for m in matches:
            h = clean_team_name(m.get("home_team", ""))
            a = clean_team_name(m.get("away_team", ""))
            m_title = f"{h} vs {a}"
            m_date = m.get("commence_time", "")[:10]
            all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_team_goals_over15(h, a, True, min_edge_val, injuries_df)})
            all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_team_goals_over15(a, h, False, min_edge_val, injuries_df)})
            for l_c in [8.5, 9.5, 10.5]:
                all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_corners_multiline(h, a, l_c, min_edge_val)})
        
        valid_opps = [op for op in all_opportunities if op["min_odds"] >= 1.40]
        valid_opps.sort(key=lambda x: x["prob"], reverse=True)
        top5 = valid_opps[:5]
        
        table_data = []
        for idx, item in enumerate(top5):
            pos = idx + 1
            if user_has_access:
                table_data.append({
                    "POS": f"#{pos}", "PARTITA": item["match"], "DATA": item["date"],
                    "MERCATO": item["market"], "PROB. MODELLO": f"{item['prob']*100:.1f}%",
                    "QUOTA EQUA": f"{item['fair_odds']:.2f}",
                    "QUOTA MINIMA (VALORE)": f"{item['min_odds']:.2f}"
                })
            else:
                table_data.append({
                    "POS": f"#{pos}", "PARTITA": item["match"], "DATA": item["date"],
                    "MERCATO": "[BLOCCATO - RICERCA SETTIMANALE ESAURITA]", "PROB. MODELLO": "---",
                    "QUOTA EQUA": "---", "QUOTA MINIMA (VALORE)": "---"
                })
        st.table(pd.DataFrame(table_data))
        
        st.markdown("---")
        st.markdown("### SCHEDE MOTIVATE & VERIFICA QUOTA REALE (TOP 5)")
        for idx, item in enumerate(top5):
            pos = idx + 1
            if user_has_access:
                with st.expander(f"Report #{pos} | {item['match']} - {item['market']} (Quota Minima: {item['min_odds']:.2f})", expanded=(pos==1)):
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.metric("Probabilità Reale", f"{item['prob']*100:.1f}%")
                        st.write(f"**Quota Equa:** `{item['fair_odds']:.2f}` | **Quota Minima di Ingresso:** `{item['min_odds']:.2f}`")
                        st.info(f"**Dettaglio Tecnico:** {item['note']}")
                    with col_t2:
                        init_val = safe_odds_val(item['min_odds'])
                        odd_check = st.number_input(f"Inserisci Quota Bookmaker (#{pos})", min_value=1.01, max_value=20.0, value=init_val, step=0.02, key=f"top_odd_{idx}_{sport_api_key}")
                        calc_edge = (item['prob'] * odd_check) - 1.0
                        k_p, k_e = MatchAnalystEngine.calculate_kelly(item['prob'], odd_check, current_bankroll, kelly_fraction)
                        if odd_check >= item['min_odds'] and calc_edge >= min_edge_val:
                            st.success(f"VALORE PRESENTE: Edge {calc_edge*100:+.2f}%\nStake: {k_p}% ({k_e:.2f} €)")
                            if st.button(f"REGISTRA GIOCATA #{pos}", key=f"btn_save_top_{idx}_{sport_api_key}"):
                                save_user_bet(user_id, item["match"], item["market"], odd_check, k_e, calc_edge)
                                st.rerun()
                        else:
                            st.error(f"NO BET (Quota sotto soglia minima - Edge: {calc_edge*100:+.2f}%)")
    else:
        st.info("Nessuna partita disponibile per il turno di questa competizione.")

# 2. MERCATI PRINCIPALI (TOP 5 CON SCHEDE E CALCOLATORE)
with tab1:
    st.markdown(f"### TOP 5 MERCATI PRINCIPALI ({selected_league_label.upper()})")
    st.caption("Classifica delle migliori opportunità sui mercati Goal/Under/Over con calcolo di valore atteso.")
    
    if matches:
        cat1_all = []
        for m in matches:
            h = clean_team_name(m.get("home_team", ""))
            a = clean_team_name(m.get("away_team", ""))
            m_title = f"{h} vs {a}"
            m_date = m.get("commence_time", "")[:10]
            
            p_ov25 = 0.53
            p_un25 = 0.47
            avg_ov = 1.96
            edge_ov = (p_ov25 * avg_ov) - 1.0
            st_p_o, st_e_o = MatchAnalystEngine.calculate_kelly(p_ov25, avg_ov, current_bankroll, kelly_fraction)
            cat1_all.append({
                "PARTITA": m_title, "DATA": m_date, "MERCATO": "Over 2.5 Totali",
                "QUOTA LIVE": f"{avg_ov:.2f}", "PROB REALE": f"{p_ov25*100:.1f}%",
                "EDGE": f"{edge_ov*100:+.2f}%", "STAKE": f"{st_p_o}% ({st_e_o:.2f} €)",
                "edge_num": edge_ov, "prob_num": p_ov25, "odds_num": avg_ov, "stake_eur": st_e_o
            })
            
            avg_un = 2.18
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
        
        disp_c1 = [{k: v for k, v in item.items() if not k.endswith("_num") and k != "stake_eur"} for item in top5_cat1]
        st.table(pd.DataFrame(disp_c1))
        
        st.markdown("---")
        st.markdown("### VERIFICA QUOTA & REGISTRA GIOCATA MERCATI PRINCIPALI")
        c1_opts = [f"#{i+1} | {b['PARTITA']} | {b['MERCATO']} @ {b['QUOTA LIVE']}" for i, b in enumerate(top5_cat1)]
        sel_c1_i = st.selectbox("Seleziona Giocata da Registrare", range(len(c1_opts)), format_func=lambda x: c1_opts[x])
        if st.button("SALVA SCOMMESSA LIVE NEL BANKROLL"):
            chosen_c1 = top5_cat1[sel_c1_i]
            save_user_bet(user_id, chosen_c1["PARTITA"], chosen_c1["MERCATO"], chosen_c1["odds_num"], chosen_c1["stake_eur"], chosen_c1["edge_num"])
            st.success("Scommessa live registrata nel Bankroll.")
            st.rerun()
    else:
        st.info("Nessuna quota live disponibile al momento.")

# 3. STATISTICHE & TATTICA SQUADRE (CON INFLUENZA TATTICA E INFORTUNI)
with tab2:
    st.markdown(f"### STATISTICHE & QUADRO TATTICO ({selected_league_label.upper()})")
    if matches:
        match_options = [f"{clean_team_name(m.get('home_team',''))} vs {clean_team_name(m.get('away_team',''))}" for m in matches]
        sel_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options)), format_func=lambda x: match_options[x], key="c2_match_sel")
        m_sel = matches[sel_idx]
        h2 = clean_team_name(m_sel.get("home_team",""))
        a2 = clean_team_name(m_sel.get("away_team",""))
        
        h2_tactic = SERIE_A_TACTICS.get(h2, {"coach": "Allenatore Ufficiale", "formation": "4-3-3", "style": "Equilibrato", "possesso": 50.0, "cross": 17.0})
        a2_tactic = SERIE_A_TACTICS.get(a2, {"coach": "Allenatore Ufficiale", "formation": "4-3-3", "style": "Equilibrato", "possesso": 50.0, "cross": 17.0})
        
        st.markdown('<div class="lineup-badge-prob">FORMAZIONE PROBABILE (Pre-Partita)</div>', unsafe_allow_html=True)
        st.write("")
        
        col_tac1, col_tac2 = st.columns(2)
        with col_tac1:
            st.markdown(f"""
            <div class="tactical-card">
                <b>{h2.upper()} (Casa)</b><br>
                • <b>Allenatore:</b> {h2_tactic['coach']}<br>
                • <b>Modulo Tattico:</b> {h2_tactic['formation']}<br>
                • <b>Identità Tattica:</b> {h2_tactic['style']}<br>
                • <b>Possesso Palla Stimato:</b> {h2_tactic['possesso']:.1f}%<br>
                • <b>Cross Medi:</b> {h2_tactic['cross']:.1f} / gara
            </div>
            """, unsafe_allow_html=True)
        with col_tac2:
            st.markdown(f"""
            <div class="tactical-card">
                <b>{a2.upper()} (Trasferta)</b><br>
                • <b>Allenatore:</b> {a2_tactic['coach']}<br>
                • <b>Modulo Tattico:</b> {a2_tactic['formation']}<br>
                • <b>Identità Tattica:</b> {a2_tactic['style']}<br>
                • <b>Possesso Palla Stimato:</b> {a2_tactic['possesso']:.1f}%<br>
                • <b>Cross Medi:</b> {a2_tactic['cross']:.1f} / gara
            </div>
            """, unsafe_allow_html=True)
        
        # Nomi infortunati attivi
        inj_h_list = injuries_df[injuries_df["team"].str.lower() == h2.lower()]["player_name"].tolist() if not injuries_df.empty else []
        inj_a_list = injuries_df[injuries_df["team"].str.lower() == a2.lower()]["player_name"].tolist() if not injuries_df.empty else []

        h2_squad = get_team_squad_from_db(selected_league_label, h2)
        a2_squad = get_team_squad_from_db(selected_league_label, a2)
        
        col_pitch_h, col_pitch_a = st.columns(2)
        with col_pitch_h: st.markdown(render_visual_pitch_html(h2, h2_tactic['formation'], h2_squad, inj_h_list), unsafe_allow_html=True)
        with col_pitch_a: st.markdown(render_visual_pitch_html(a2, a2_tactic['formation'], a2_squad, inj_a_list), unsafe_allow_html=True)
        
        if inj_h_list or inj_a_list:
            inj_cards_html = ""
            active_match_inj = injuries_df[injuries_df["team"].str.lower().isin([h2.lower(), a2.lower()])]
            for _, row in active_match_inj.iterrows():
                inj_cards_html += f"• <b>{row['team'].upper()}</b>: {row['player_name']} ({row['importance']}) - <i>{row['injury_type']}</i> (Rientro: {row['return_date']})<br>"
            st.markdown(f"""
            <div class="injury-box">
                <b style="color: #EF4444;">🏥 INFERMERIA & INDISPONIBILI MATCH</b><br>
                {inj_cards_html}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        # CALCOLATORE STATISTICHE SQUADRA CON IMPATTO TATTICO
        col_c2_1, col_c2_2 = st.columns(2)
        with col_c2_1:
            st.markdown("#### Mercato Over 1.5 Gol Squadra")
            team_choice = st.radio("Seleziona Squadra", [h2, a2], horizontal=True, key=f"c2_team_{sport_api_key}")
            is_home_sel = (team_choice == h2)
            opp_choice = a2 if is_home_sel else h2
            
            res_g = MatchAnalystEngine.analyze_team_goals_over15(team_choice, opp_choice, is_home_sel, min_edge_val, injuries_df)
            st.metric("Probabilità Modello", f"{res_g['prob']*100:.1f}%")
            st.write(f"**Quota Equa:** `{res_g['fair_odds']:.2f}` | **Quota Minima:** `{res_g['min_odds']:.2f}`")
            st.caption(res_g["note"])
            
            init_g = safe_odds_val(res_g['min_odds'])
            odd_g_in = st.number_input("Quota Bookmaker (Over 1.5 Gol)", min_value=1.01, max_value=20.0, value=init_g, step=0.02, key=f"odd_g_in_{sport_api_key}")
            edge_g = (res_g['prob'] * odd_g_in) - 1.0
            kp_g, ke_g = MatchAnalystEngine.calculate_kelly(res_g['prob'], odd_g_in, current_bankroll, kelly_fraction)
            if odd_g_in >= res_g['min_odds'] and edge_g >= min_edge_val:
                st.success(f"VALORE PRESENTE: Edge {edge_g*100:+.2f}% | Stake: {kp_g}% ({ke_g:.2f} €)")
                if st.button("SALVA BET GOL", key=f"btn_save_g_{sport_api_key}"):
                    save_user_bet(user_id, f"{h2} vs {a2}", res_g["market"], odd_g_in, ke_g, edge_g)
                    st.rerun()
            else:
                st.error(f"NO BET (Quota insufficiente - Edge: {edge_g*100:+.2f}%)")
                
        with col_c2_2:
            st.markdown("#### Mercato Calci d'Angolo Multi-Linea")
            line_corn = st.selectbox("Linea Corner Totali", [7.5, 8.5, 9.5, 10.5, 11.5], index=2, key=f"c2_line_corn_{sport_api_key}")
            res_c = MatchAnalystEngine.analyze_corners_multiline(h2, a2, line_corn, min_edge_val)
            st.metric("Probabilità Modello", f"{res_c['prob']*100:.1f}%")
            st.write(f"**Quota Equa:** `{res_c['fair_odds']:.2f}` | **Quota Minima:** `{res_c['min_odds']:.2f}`")
            st.caption(res_c["note"])
            
            init_c = safe_odds_val(res_c['min_odds'])
            odd_c_in = st.number_input("Quota Bookmaker (Corner)", min_value=1.01, max_value=20.0, value=init_c, step=0.02, key=f"odd_c_in_{sport_api_key}")
            edge_c = (res_c['prob'] * odd_c_in) - 1.0
            kp_c, ke_c = MatchAnalystEngine.calculate_kelly(res_c['prob'], odd_c_in, current_bankroll, kelly_fraction)
            if odd_c_in >= res_c['min_odds'] and edge_c >= min_edge_val:
                st.success(f"VALORE PRESENTE: Edge {edge_c*100:+.2f}% | Stake: {kp_c}% ({ke_c:.2f} €)")
                if st.button("SALVA BET CORNER", key=f"btn_save_c_{sport_api_key}"):
                    save_user_bet(user_id, f"{h2} vs {a2}", res_c["market"], odd_c_in, ke_c, edge_c)
                    st.rerun()
            else:
                st.error(f"NO BET (Quota insufficiente - Edge: {edge_c*100:+.2f}%)")
    else:
        st.info("Nessuna partita in programma.")

# 4. PRESTAZIONI CALCIATORI & PORTIERI (ESCLUSIVA SERIE A 2026/2027)
if is_serie_a:
    with tab3:
        st.markdown("### PRESTAZIONI CALCIATORI & PORTIERI (SERIE A 2026/2027)")
        st.caption("Analisi quantitativa per tiri in porta, falli commessi, falli subiti e parate del portiere.")
        
        if matches:
            match_options_c3 = [f"{clean_team_name(m.get('home_team',''))} vs {clean_team_name(m.get('away_team',''))}" for m in matches]
            sel_m3_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options_c3)), format_func=lambda x: match_options_c3[x], key="c3_match_sel")
            m3 = matches[sel_m3_idx]
            h3 = clean_team_name(m3["home_team"])
            a3 = clean_team_name(m3["away_team"])
            
            h3_players = get_team_squad_from_db(selected_league_label, h3)
            a3_players = get_team_squad_from_db(selected_league_label, a3)
            
            tab_h, tab_a = st.tabs([f"Squadra Casa: {h3}", f"Squadra Trasferta: {a3}"])
            
            def render_player_panel(players_list, team_name, opp_team, key_prefix):
                inj_names_t = injuries_df[injuries_df["team"].str.lower() == team_name.lower()]["player_name"].tolist() if not injuries_df.empty else []
                
                p_display = []
                for p in players_list:
                    p_n = p['name']
                    is_inj = any(inj_n.lower() in p_n.lower() for inj_n in inj_names_t)
                    prefix = "[INFORTUNATO - OUT] " if is_inj else ""
                    p_display.append(f"{prefix}{p_n} ({p['role']} #{p['number']})")
                    
                sel_p_i = st.selectbox(f"Seleziona Calciatore ({team_name})", range(len(p_display)), format_func=lambda x: p_display[x], key=f"{key_prefix}_sel")
                chosen_p = players_list[sel_p_i]
                
                is_chosen_inj = any(inj_n.lower() in chosen_p['name'].lower() for inj_n in inj_names_t)
                if is_chosen_inj:
                    st.error(f"ATTENZIONE: {chosen_p['name']} è attualmente inserito in Infermeria per infortunio. Mercato disabilitato.")
                    return
                
                if chosen_p["role"] == "Goalkeeper":
                    st.markdown("#### Mercato: Parate Portiere")
                    save_line = st.selectbox("Seleziona Linea Parate", [1.5, 2.5, 3.5, 4.5], index=1, key=f"{key_prefix}_save_line")
                    res_sv = MatchAnalystEngine.analyze_goalkeeper_saves(chosen_p, opp_team, save_line, min_edge_val)
                    st.metric("Probabilità Modello", f"{res_sv['prob']*100:.1f}%")
                    st.write(f"**Quota Equa:** `{res_sv['fair_odds']:.2f}` | **Quota Minima:** `{res_sv['min_odds']:.2f}`")
                    
                    init_sv = safe_odds_val(res_sv['min_odds'])
                    odd_sv_in = st.number_input("Quota Parate Bookmaker", min_value=1.01, max_value=20.0, value=init_sv, step=0.02, key=f"{key_prefix}_odd_sv")
                    edge_sv = (res_sv['prob'] * odd_sv_in) - 1.0
                    kpsv, kesv = MatchAnalystEngine.calculate_kelly(res_sv['prob'], odd_sv_in, current_bankroll, kelly_fraction)
                    if odd_sv_in >= res_sv['min_odds'] and edge_sv >= min_edge_val:
                        st.success(f"VALORE PRESENTE: Edge {edge_sv*100:+.2f}% | Stake: {kpsv}% ({kesv:.2f} €)")
                        if st.button("SALVA BET PARATE", key=f"{key_prefix}_btn_sv"):
                            save_user_bet(user_id, f"{h3} vs {a3}", res_sv["market"], odd_sv_in, kesv, edge_sv)
                            st.rerun()
                    else:
                        st.error(f"NO BET (Quota insufficiente - Edge: {edge_sv*100:+.2f}%)")
                else:
                    st.markdown("#### Selezione Mercato & Linea Statistica")
                    market_choice = st.selectbox(
                        "Seleziona Mercato Statistico Giocatore",
                        [
                            "Over 0.5 Tiri in Porta",
                            "Over 1.5 Tiri in Porta",
                            "Over 0.5 Falli Commessi",
                            "Over 1.5 Falli Commessi",
                            "Over 2.5 Falli Commessi",
                            "Over 0.5 Falli Subiti",
                            "Over 1.5 Falli Subiti",
                            "Over 2.5 Falli Subiti"
                        ],
                        key=f"{key_prefix}_mkt_choice"
                    )
                    
                    if "Tiri in Porta" in market_choice:
                        line = 0.5 if "0.5" in market_choice else 1.5
                        res_p = MatchAnalystEngine.analyze_player_sot(chosen_p, opp_team, line, min_edge_val)
                    elif "Falli Commessi" in market_choice:
                        line = 0.5 if "0.5" in market_choice else (1.5 if "1.5" in market_choice else 2.5)
                        res_p = MatchAnalystEngine.analyze_player_fouls(chosen_p, opp_team, line, min_edge_val)
                    else:  # Falli Subiti
                        line = 0.5 if "0.5" in market_choice else (1.5 if "1.5" in market_choice else 2.5)
                        res_p = MatchAnalystEngine.analyze_player_fouls_drawn(chosen_p, opp_team, line, min_edge_val)
                        
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.metric("Probabilità Modello", f"{res_p['prob']*100:.1f}%")
                        st.write(f"**Quota Equa:** `{res_p['fair_odds']:.2f}` | **Quota Minima (Valore):** `{res_p['min_odds']:.2f}`")
                        st.caption(res_p["note"])
                    with col_p2:
                        init_p = safe_odds_val(res_p['min_odds'])
                        odd_p_in = st.number_input("Quota sul tuo Bookmaker", min_value=1.01, max_value=20.0, value=init_p, step=0.02, key=f"{key_prefix}_odd_p")
                        edge_p = (res_p['prob'] * odd_p_in) - 1.0
                        kpp, kep = MatchAnalystEngine.calculate_kelly(res_p['prob'], odd_p_in, current_bankroll, kelly_fraction)
                        if odd_p_in >= res_p['min_odds'] and edge_p >= min_edge_val:
                            st.success(f"VALORE PRESENTE: Edge {edge_p*100:+.2f}% | Stake: {kpp}% ({kep:.2f} €)")
                            if st.button(f"SALVA BET ({market_choice})", key=f"{key_prefix}_btn_save"):
                                save_user_bet(user_id, f"{h3} vs {a3}", res_p["market"], odd_p_in, kep, edge_p)
                                st.rerun()
                        else:
                            st.error(f"NO BET (Quota insufficiente - Edge: {edge_p*100:+.2f}%)")
                        
            with tab_h: render_player_panel(h3_players, h3, a3, "tab_h_p")
            with tab_a: render_player_panel(a3_players, a3, h3, "tab_a_p")
        else:
            st.info("Nessuna partita disponibile.")

    # 5. FOCUS DISCIPLINARE & ARBITRI (CAN A-B COMPLETO)
    with tab4:
        st.markdown("### FOCUS DISCIPLINARE & ARBITRI (CAN A-B)")
        st.caption("Organico direttori di gara Serie A & Serie B con calcolo quantitativo sui cartellini.")
        
        if matches:
            match_options_c4 = [f"{clean_team_name(m['home_team'])} vs {clean_team_name(m['away_team'])}" for m in matches]
            sel_m4_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options_c4)), format_func=lambda x: match_options_c4[x], key="c4_match_sel_sa")
            m4 = matches[sel_m4_idx]
            h4 = clean_team_name(m4["home_team"])
            a4 = clean_team_name(m4["away_team"])
            
            ref_names_list = sorted(list(SERIE_A_REFEREES_DB.keys()))
            chosen_ref_key = st.selectbox("Seleziona l'arbitro designato", ref_names_list, format_func=lambda x: SERIE_A_REFEREES_DB[x]["name"])
            ref_data = SERIE_A_REFEREES_DB[chosen_ref_key]
                    
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                st.markdown(f"#### Metriche Arbitro: `{ref_data['name']}`")
                st.write(f"- **Media Cartellini / Partita:** `{ref_data['cards_avg']:.1f}`")
                st.write(f"- **Media Falli Fischiati / Partita:** `{ref_data['fouls_avg']:.1f}`")
                st.write(f"- **Indice di Severità Disciplinare:** `{ref_data['severity']}`")
                st.caption("Dati statistici ufficiali registrati per la stagione agonistica in corso.")
                    
            with col_ref2:
                st.markdown("#### Calcolo Cartellini Totali")
                cards_line = st.selectbox("Linea Cartellini Totali", [3.5, 4.5, 5.5], index=1, key="c4_cards_line_sa")
                disc_res = MatchAnalystEngine.analyze_disciplinary_match(h4, a4, ref_data, cards_line, min_edge_val)
                
                st.metric("Probabilità Modello", f"{disc_res['prob']*100:.1f}%")
                st.write(f"**Quota Equa:** `{disc_res['fair_odds']:.2f}` | **Quota Minima:** `{disc_res['min_odds']:.2f}`")
                
                init_cd = safe_odds_val(disc_res['min_odds'])
                odd_card_in = st.number_input("Quota Cartellini Bookmaker", min_value=1.01, max_value=20.0, value=init_cd, step=0.02, key="odd_card_in_sa")
                edge_card = (disc_res['prob'] * odd_card_in) - 1.0
                kpc, kec = MatchAnalystEngine.calculate_kelly(disc_res['prob'], odd_card_in, current_bankroll, kelly_fraction)
                if odd_card_in >= disc_res['min_odds'] and edge_card >= min_edge_val:
                    st.success(f"VALORE PRESENTE: Edge {edge_card*100:+.2f}% | Stake: {kpc}% ({kec:.2f} €)")
                    if st.button("SALVA BET CARTELLINI", key="btn_save_card_sa"):
                        save_user_bet(user_id, f"{h4} vs {a4}", f"Over {cards_line} Cartellini", odd_card_in, kec, edge_card)
                        st.rerun()
                else:
                    st.error(f"NO BET (Quota insufficiente - Edge: {edge_card*100:+.2f}%)")

    # 6. INFERMERIA
    with tab_inj:
        st.markdown("### GESTIONE INFERMERIA & INDISPONIBILI SERIE A")
        st.caption("Inserisci qui settimanalmente i calciatori infortunati. L'algoritmo ricalcolerà istantaneamente il peso su xG, linee statistiche e titolari in campo.")
        col_inj_in1, col_inj_in2 = st.columns(2)
        with col_inj_in1:
            inj_team = st.text_input("Squadra", placeholder="es. Inter, Juventus, Milan...", key="inj_team_input")
            inj_player = st.text_input("Nome Calciatore", placeholder="es. Dusan Vlahovic", key="inj_player_input")
        with col_inj_in2:
            inj_imp = st.selectbox("Importanza Tattica", ["Top Player Offensivo", "Titolare Mediano / Regista", "Difensore Chiave", "Portiere Titolare"], key="inj_importance_select")
            inj_diag = st.text_input("Diagnosi", placeholder="es. Lesione muscolare", key="inj_type_input")
            if st.button("AGGIUNGI IN INFERMERIA", use_container_width=True):
                if inj_team and inj_player:
                    save_injury(inj_team, inj_player, inj_imp, inj_diag, "Da definire")
                    st.success("Infortunio registrato.")
                    st.rerun()

# 7. REGISTRO SCOMMESSE
with tab5:
    st.markdown("### STORICO PERSONALE SCOMMESSE")
    user_bets = fetch_user_bets(user_id)
    if not user_bets.empty:
        st.dataframe(user_bets[["created_at", "match", "market", "odds", "stake", "status", "profit"]], use_container_width=True, hide_index=True)
    else:
        st.info("Nessuna scommessa registrata.")

# 8. GESTIONE ACCOUNT
with tab6:
    st.markdown("### GESTIONE ACCOUNT")
    st.write(f"**Email:** `{user_email}` | **Stato:** `{tier_label}`")
