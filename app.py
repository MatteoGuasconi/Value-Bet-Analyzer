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

# Styling CSS Dark Fintech - Palette Frost Indigo & Fix Completo Safari iOS
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
    
    [data-testid="stIconMaterial"], [class*="material-symbols"], i {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
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
        if res.status_code in [200, 201]: return True, "Registrazione completata. Puoi accedere ora."
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
        return False, "Errore aggiornamento password."
    except Exception as e:
        return False, str(e)

def logout_user():
    st.session_state.user = None
    st.session_state.user_tier = "free"
    st.session_state.access_token = None

def redeem_vip_code(user_id, code_input):
    valid_promo_codes = ["Valuebet2026", "VIP2026", "PRO2026"]
    if code_input.strip() in valid_promo_codes:
        if SB_URL and SB_KEY and user_id and user_id != "local_user":
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

# Cloud Database Infortuni
def fetch_injuries():
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/team_injuries?select=*&order=created_at.desc"
        try:
            res = requests.get(url, headers=get_headers(token), timeout=10)
            if res.status_code == 200 and res.json():
                return pd.DataFrame(res.json())
        except Exception:
            pass
    return pd.DataFrame(columns=["id", "team", "player_name", "importance", "injury_type", "return_date"])

def save_injury(team, player_name, importance, injury_type, return_date):
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/team_injuries"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        payload = {
            "team": team,
            "player_name": player_name,
            "importance": importance,
            "injury_type": injury_type,
            "return_date": return_date
        }
        try:
            res = requests.post(url, json=payload, headers=hdrs, timeout=10)
            return res.status_code in [200, 201]
        except Exception:
            pass
    return False

def delete_injury(injury_id):
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/team_injuries?id=eq.{injury_id}"
        try:
            requests.delete(url, headers=get_headers(token), timeout=10)
        except Exception:
            pass

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

# DIZIONARIO COMPETIZIONI (TUTTI I 5 CAMPIONATI ABILITATI AL 100%)
LEAGUES_CONFIG = {
    "Serie A (Italia)": {"key": "soccer_italy_serie_a", "has_players": True},
    "Premier League (Inghilterra)": {"key": "soccer_epl", "has_players": True},
    "La Liga (Spagna)": {"key": "soccer_spain_la_liga", "has_players": True},
    "Bundesliga (Germania)": {"key": "soccer_germany_bundesliga", "has_players": True},
    "Ligue 1 (Francia)": {"key": "soccer_france_ligue_one", "has_players": True}
}

CLEAN_TEAM_NAMES = {
    "inter milan": "Inter", "internazionale": "Inter", "ac milan": "Milan", "milan": "Milan",
    "juventus fc": "Juventus", "as roma": "Roma", "ss lazio": "Lazio", "juventus": "Juventus",
    "napoli": "Napoli", "fiorentina": "Fiorentina", "bologna": "Bologna",
    "torino": "Torino", "parma": "Parma", "cagliari": "Cagliari",
    "empoli": "Empoli", "genoa": "Genoa", "monza": "Monza",
    "lecce": "Lecce", "udinese": "Udinese", "verona": "Verona",
    "venezia": "Venezia", "como": "Como", "manchester city": "Manchester City",
    "arsenal": "Arsenal", "liverpool": "Liverpool", "chelsea": "Chelsea",
    "tottenham": "Tottenham", "real madrid": "Real Madrid",
    "barcelona": "Barcellona", "fc barcelona": "Barcellona", "bayern munich": "Bayern Monaco",
    "bayern munchen": "Bayern Monaco", "paris saint germain": "PSG", "psg": "PSG"
}

def clean_name(raw_name):
    for eng, ita in CLEAN_TEAM_NAMES.items():
        if eng.lower() in raw_name.lower():
            return ita
    return raw_name

# ORGANICO COMPLETO ARBITRI CAN A-B & INTERNAZIONALI
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
    "taylor": {"name": "Anthony Taylor (Premier League)", "fouls_avg": 22.1, "cards_avg": 3.8, "severity": "Standard"},
    "oliver": {"name": "Michael Oliver (Premier League)", "fouls_avg": 21.4, "cards_avg": 3.6, "severity": "Permissivo"},
    "gil_manzano": {"name": "Jesus Gil Manzano (La Liga)", "fouls_avg": 26.5, "cards_avg": 5.1, "severity": "Severo"},
    "siebert": {"name": "Daniel Siebert (Bundesliga)", "fouls_avg": 23.8, "cards_avg": 4.2, "severity": "Standard"},
    "turpin": {"name": "Clement Turpin (Ligue 1)", "fouls_avg": 24.0, "cards_avg": 3.9, "severity": "Standard"}
}

# Parametri Tattici Squadre Top 5 Campionati
TEAM_METRICS = {
    "Inter": {"gf_h": 2.25, "gf_a": 1.90, "ga_h": 0.65, "ga_a": 0.80, "xg_5": 2.15, "xg_s": 2.05, "sot_pro": 6.2, "sot_against": 3.1, "corners_pro": 6.4, "corners_against": 3.6, "cross": 21.5, "blocked_shots": 5.4, "fouls_pro": 11.2, "fouls_against": 12.8, "cards_avg": 1.8, "modulo": "3-5-2", "stile": "Pressing Alto & Sovrapposizione Catene Esterne", "possesso": 61.2},
    "Juventus": {"gf_h": 1.70, "gf_a": 1.40, "ga_h": 0.50, "ga_a": 0.75, "xg_5": 1.65, "xg_s": 1.55, "sot_pro": 5.1, "sot_against": 2.8, "corners_pro": 5.6, "corners_against": 3.8, "cross": 18.2, "blocked_shots": 4.6, "fouls_pro": 12.1, "fouls_against": 13.5, "cards_avg": 2.1, "modulo": "4-2-3-1", "stile": "Dominio Territoriale & Costruzione Bassa", "possesso": 58.4},
    "Milan": {"gf_h": 2.05, "gf_a": 1.65, "ga_h": 1.10, "ga_a": 1.25, "xg_5": 1.90, "xg_s": 1.80, "sot_pro": 5.6, "sot_against": 4.4, "corners_pro": 5.8, "corners_against": 4.2, "cross": 19.5, "blocked_shots": 5.2, "fouls_pro": 11.8, "fouls_against": 12.0, "cards_avg": 2.3, "modulo": "4-2-3-1", "stile": "Transizione Rapida & Spinta sulle Fasce", "possesso": 56.0},
    "Napoli": {"gf_h": 1.85, "gf_a": 1.55, "ga_h": 0.60, "ga_a": 0.85, "xg_5": 1.80, "xg_s": 1.70, "sot_pro": 5.3, "sot_against": 3.2, "corners_pro": 6.1, "corners_against": 3.5, "cross": 20.8, "blocked_shots": 5.1, "fouls_pro": 12.4, "fouls_against": 13.0, "cards_avg": 1.9, "modulo": "3-5-2", "stile": "Compattezza Difensiva & Attacco Diretto", "possesso": 55.5},
    "Atalanta": {"gf_h": 2.30, "gf_a": 1.80, "ga_h": 1.05, "ga_a": 1.20, "xg_5": 2.20, "xg_s": 2.10, "sot_pro": 6.5, "sot_against": 4.1, "corners_pro": 6.7, "corners_against": 4.0, "cross": 22.4, "blocked_shots": 5.8, "fouls_pro": 13.8, "fouls_against": 14.2, "cards_avg": 2.4, "modulo": "3-4-2-1", "stile": "Pressing Ultra-Offensivo a Tutto Campo", "possesso": 57.8},
    "Roma": {"gf_h": 1.60, "gf_a": 1.20, "ga_h": 0.95, "ga_a": 1.15, "xg_5": 1.55, "xg_s": 1.50, "sot_pro": 4.9, "sot_against": 3.8, "corners_pro": 5.4, "corners_against": 4.1, "cross": 17.5, "blocked_shots": 4.2, "fouls_pro": 13.0, "fouls_against": 12.5, "cards_avg": 2.2, "modulo": "3-4-2-1", "stile": "Marcatura a Uomo & Rifinitura Centrale", "possesso": 52.3},
    "Lazio": {"gf_h": 1.75, "gf_a": 1.35, "ga_h": 1.00, "ga_a": 1.25, "xg_5": 1.60, "xg_s": 1.55, "sot_pro": 4.8, "sot_against": 4.0, "corners_pro": 5.3, "corners_against": 4.3, "cross": 18.0, "blocked_shots": 4.5, "fouls_pro": 13.2, "fouls_against": 12.2, "cards_avg": 2.5, "modulo": "4-2-3-1", "stile": "Verticalizzazioni Rapide & Aggressivita", "possesso": 51.5},
    "Fiorentina": {"gf_h": 1.70, "gf_a": 1.30, "ga_h": 0.90, "ga_a": 1.20, "xg_5": 1.55, "xg_s": 1.45, "sot_pro": 4.7, "sot_against": 3.9, "corners_pro": 5.5, "corners_against": 4.2, "cross": 19.0, "blocked_shots": 4.8, "fouls_pro": 12.6, "fouls_against": 12.8, "cards_avg": 2.1, "modulo": "4-3-3", "stile": "Possesso Laterale & Densita Offensiva", "possesso": 54.0},
    "Bologna": {"gf_h": 1.50, "gf_a": 1.15, "ga_h": 0.85, "ga_a": 1.10, "xg_5": 1.45, "xg_s": 1.40, "sot_pro": 4.5, "sot_against": 3.5, "corners_pro": 5.2, "corners_against": 3.9, "cross": 17.8, "blocked_shots": 4.3, "fouls_pro": 12.5, "fouls_against": 12.0, "cards_avg": 2.0, "modulo": "4-2-3-1", "stile": "Costruzione Bassa & Controllo Ritmi", "possesso": 53.5},
    "Torino": {"gf_h": 1.25, "gf_a": 0.95, "ga_h": 0.90, "ga_a": 1.15, "xg_5": 1.20, "xg_s": 1.15, "sot_pro": 3.9, "sot_against": 4.2, "corners_pro": 4.6, "corners_against": 4.5, "cross": 16.0, "blocked_shots": 3.9, "fouls_pro": 14.1, "fouls_against": 11.8, "cards_avg": 2.3, "modulo": "3-5-2", "stile": "Duelli Fisici & Ripartenza", "possesso": 48.0},
    "Manchester City": {"gf_h": 2.45, "gf_a": 2.10, "ga_h": 0.60, "ga_a": 0.80, "xg_5": 2.35, "xg_s": 2.25, "sot_pro": 7.1, "sot_against": 2.6, "corners_pro": 7.4, "corners_against": 3.0, "cross": 22.0, "blocked_shots": 5.8, "fouls_pro": 9.5, "fouls_against": 11.5, "cards_avg": 1.4, "modulo": "4-3-3", "stile": "Dominio Territoriale Assoluto", "possesso": 65.5},
    "Arsenal": {"gf_h": 2.20, "gf_a": 1.85, "ga_h": 0.55, "ga_a": 0.70, "xg_5": 2.05, "xg_s": 1.95, "sot_pro": 6.4, "sot_against": 2.7, "corners_pro": 6.8, "corners_against": 3.2, "cross": 20.5, "blocked_shots": 5.2, "fouls_pro": 10.8, "fouls_against": 12.2, "cards_avg": 1.7, "modulo": "4-3-3", "stile": "Pressione Alta & Palle Inattive", "possesso": 60.5},
    "Liverpool": {"gf_h": 2.30, "gf_a": 1.95, "ga_h": 0.65, "ga_a": 0.85, "xg_5": 2.20, "xg_s": 2.10, "sot_pro": 6.7, "sot_against": 3.0, "corners_pro": 7.0, "corners_against": 3.5, "cross": 21.0, "blocked_shots": 5.4, "fouls_pro": 11.0, "fouls_against": 11.8, "cards_avg": 1.8, "modulo": "4-3-3", "stile": "Transizione e Verticalizzazione Rapida", "possesso": 61.5},
    "Real Madrid": {"gf_h": 2.35, "gf_a": 1.95, "ga_h": 0.70, "ga_a": 0.85, "xg_5": 2.25, "xg_s": 2.10, "sot_pro": 6.8, "sot_against": 3.2, "corners_pro": 6.5, "corners_against": 3.8, "cross": 19.5, "blocked_shots": 5.4, "fouls_pro": 10.2, "fouls_against": 13.8, "cards_avg": 1.8, "modulo": "4-3-3", "stile": "Verticalizzazioni Rapide & Attacco Spazi", "possesso": 61.0},
    "Barcellona": {"gf_h": 2.40, "gf_a": 2.00, "ga_h": 0.75, "ga_a": 0.90, "xg_5": 2.30, "xg_s": 2.15, "sot_pro": 6.9, "sot_against": 3.4, "corners_pro": 6.6, "corners_against": 3.7, "cross": 18.5, "blocked_shots": 5.1, "fouls_pro": 11.0, "fouls_against": 13.0, "cards_avg": 2.0, "modulo": "4-2-3-1", "stile": "Linea Difensiva Alta & Attacco Rapido", "possesso": 63.5},
    "Bayern Monaco": {"gf_h": 2.50, "gf_a": 2.15, "ga_h": 0.70, "ga_a": 0.95, "xg_5": 2.45, "xg_s": 2.30, "sot_pro": 7.3, "sot_against": 3.0, "corners_pro": 7.2, "corners_against": 3.4, "cross": 21.0, "blocked_shots": 5.6, "fouls_pro": 10.5, "fouls_against": 11.8, "cards_avg": 1.6, "modulo": "4-2-3-1", "stile": "Ritmo Ultra-Offensivo", "possesso": 64.0},
    "PSG": {"gf_h": 2.30, "gf_a": 1.90, "ga_h": 0.65, "ga_a": 0.85, "xg_5": 2.15, "xg_s": 2.05, "sot_pro": 6.5, "sot_against": 3.1, "corners_pro": 6.3, "corners_against": 3.5, "cross": 19.0, "blocked_shots": 4.9, "fouls_pro": 10.8, "fouls_against": 12.5, "cards_avg": 1.8, "modulo": "4-3-3", "stile": "Possesso Posizionale & Ripartenza", "possesso": 62.0}
}

DEFAULT_METRICS = {
    "gf_h": 1.40, "gf_a": 1.15, "ga_h": 1.10, "ga_a": 1.40, "xg_5": 1.35, "xg_s": 1.30,
    "sot_pro": 4.4, "sot_against": 4.6, "corners_pro": 4.8, "corners_against": 4.8,
    "cross": 16.5, "blocked_shots": 4.0, "fouls_pro": 12.5, "fouls_against": 12.5, "cards_avg": 2.2, "modulo": "4-3-3", "stile": "Equilibrato & Costruzione Rapida", "possesso": 50.0
}

# Ricalcolo Dinamico Metriche Squadra con Impatto Infortuni
def get_adjusted_metrics(team_name, injuries_df):
    cleaned = clean_name(team_name)
    base = None
    for name, metrics in TEAM_METRICS.items():
        if name.lower() in cleaned.lower() or cleaned.lower() in name.lower():
            base = dict(metrics)
            break
    if not base:
        base = dict(DEFAULT_METRICS)
        
    if not injuries_df.empty:
        team_inj = injuries_df[injuries_df["team"].str.lower() == cleaned.lower()]
        for _, row in team_inj.iterrows():
            imp = row.get("importance", "")
            if imp == "Top Player Offensivo":
                base["gf_h"] *= 0.88
                base["gf_a"] *= 0.88
                base["xg_5"] *= 0.88
                base["sot_pro"] = max(1.0, base["sot_pro"] - 0.8)
            elif imp == "Titolare Mediano / Regista":
                base["possesso"] = max(30.0, base["possesso"] - 4.0)
                base["corners_pro"] = max(2.0, base["corners_pro"] * 0.92)
                base["gf_h"] *= 0.95
                base["gf_a"] *= 0.95
            elif imp == "Difensore Chiave":
                base["ga_h"] *= 1.15
                base["ga_a"] *= 1.15
                base["sot_against"] += 0.8
            elif imp == "Portiere Titolare":
                base["ga_h"] *= 1.10
                base["ga_a"] *= 1.10
            elif imp == "Riserva Offensiva / Rotazione":
                base["gf_h"] *= 0.97
                base["gf_a"] *= 0.97
            elif imp == "Riserva Difensiva / Rotazione":
                base["ga_h"] *= 1.04
                base["ga_a"] *= 1.04
    return base

# ROSE UFFICIALI 2026/2027 DINAMICHE
@st.cache_data(ttl=86400, show_spinner=False)
def get_team_squad(team_name, api_key):
    cleaned = clean_name(team_name)
    
    # Rose Pronte 2026/2027 per Squadre Top
    squads_2026_2027 = {
        "Inter": [
            {"name": "Yann Sommer", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.8, "penalties": False},
            {"name": "Alessandro Bastoni", "role": "Defender", "number": "95", "sot_90": 0.35, "fouls_c_90": 1.25, "saves_90": 0.0, "penalties": False},
            {"name": "Benjamin Pavard", "role": "Defender", "number": "28", "sot_90": 0.30, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": False},
            {"name": "Francesco Acerbi", "role": "Defender", "number": "15", "sot_90": 0.20, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": False},
            {"name": "Federico Dimarco", "role": "Midfielder", "number": "32", "sot_90": 0.95, "fouls_c_90": 0.80, "saves_90": 0.0, "penalties": False},
            {"name": "Denzel Dumfries", "role": "Midfielder", "number": "2", "sot_90": 0.80, "fouls_c_90": 1.50, "saves_90": 0.0, "penalties": False},
            {"name": "Nicolo Barella", "role": "Midfielder", "number": "23", "sot_90": 0.85, "fouls_c_90": 1.65, "saves_90": 0.0, "penalties": False},
            {"name": "Hakan Calhanoglu", "role": "Midfielder", "number": "20", "sot_90": 1.30, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": True},
            {"name": "Henrikh Mkhitaryan", "role": "Midfielder", "number": "22", "sot_90": 0.75, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": False},
            {"name": "Piotr Zielinski", "role": "Midfielder", "number": "7", "sot_90": 0.80, "fouls_c_90": 1.05, "saves_90": 0.0, "penalties": False},
            {"name": "Lautaro Martinez", "role": "Attacker", "number": "10", "sot_90": 1.85, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": True},
            {"name": "Marcus Thuram", "role": "Attacker", "number": "9", "sot_90": 1.40, "fouls_c_90": 1.20, "saves_90": 0.0, "penalties": False}
        ],
        "Juventus": [
            {"name": "Michele Di Gregorio", "role": "Goalkeeper", "number": "29", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.7, "penalties": False},
            {"name": "Gleison Bremer", "role": "Defender", "number": "3", "sot_90": 0.45, "fouls_c_90": 1.80, "saves_90": 0.0, "penalties": False},
            {"name": "Federico Gatti", "role": "Defender", "number": "4", "sot_90": 0.50, "fouls_c_90": 1.95, "saves_90": 0.0, "penalties": False},
            {"name": "Pierre Kalulu", "role": "Defender", "number": "15", "sot_90": 0.25, "fouls_c_90": 1.35, "saves_90": 0.0, "penalties": False},
            {"name": "Andrea Cambiaso", "role": "Defender", "number": "27", "sot_90": 0.60, "fouls_c_90": 1.25, "saves_90": 0.0, "penalties": False},
            {"name": "Manuel Locatelli", "role": "Midfielder", "number": "5", "sot_90": 0.55, "fouls_c_90": 1.65, "saves_90": 0.0, "penalties": False},
            {"name": "Khephren Thuram", "role": "Midfielder", "number": "19", "sot_90": 0.70, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": False},
            {"name": "Teun Koopmeiners", "role": "Midfielder", "number": "8", "sot_90": 1.20, "fouls_c_90": 1.30, "saves_90": 0.0, "penalties": True},
            {"name": "Douglas Luiz", "role": "Midfielder", "number": "26", "sot_90": 0.85, "fouls_c_90": 1.50, "saves_90": 0.0, "penalties": False},
            {"name": "Kenan Yildiz", "role": "Attacker", "number": "10", "sot_90": 1.30, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": False},
            {"name": "Francisco Conceicao", "role": "Attacker", "number": "7", "sot_90": 1.15, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Dusan Vlahovic", "role": "Attacker", "number": "9", "sot_90": 1.70, "fouls_c_90": 1.55, "saves_90": 0.0, "penalties": True}
        ],
        "Milan": [
            {"name": "Mike Maignan", "role": "Goalkeeper", "number": "16", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 3.4, "penalties": False},
            {"name": "Theo Hernandez", "role": "Defender", "number": "19", "sot_90": 0.85, "fouls_c_90": 1.70, "saves_90": 0.0, "penalties": True},
            {"name": "Fikayo Tomori", "role": "Defender", "number": "23", "sot_90": 0.25, "fouls_c_90": 1.55, "saves_90": 0.0, "penalties": False},
            {"name": "Strahinja Pavlovic", "role": "Defender", "number": "31", "sot_90": 0.40, "fouls_c_90": 1.90, "saves_90": 0.0, "penalties": False},
            {"name": "Emerson Royal", "role": "Defender", "number": "22", "sot_90": 0.30, "fouls_c_90": 1.60, "saves_90": 0.0, "penalties": False},
            {"name": "Tijjani Reijnders", "role": "Midfielder", "number": "14", "sot_90": 1.10, "fouls_c_90": 1.20, "saves_90": 0.0, "penalties": False},
            {"name": "Youssouf Fofana", "role": "Midfielder", "number": "29", "sot_90": 0.65, "fouls_c_90": 1.85, "saves_90": 0.0, "penalties": False},
            {"name": "Ruben Loftus-Cheek", "role": "Midfielder", "number": "8", "sot_90": 0.90, "fouls_c_90": 1.50, "saves_90": 0.0, "penalties": False},
            {"name": "Christian Pulisic", "role": "Attacker", "number": "11", "sot_90": 1.30, "fouls_c_90": 0.90, "saves_90": 0.0, "penalties": True},
            {"name": "Rafael Leao", "role": "Attacker", "number": "10", "sot_90": 1.45, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Alvaro Morata", "role": "Attacker", "number": "7", "sot_90": 1.35, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": False}
        ],
        "Napoli": [
            {"name": "Alex Meret", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.9, "penalties": False},
            {"name": "Giovanni Di Lorenzo", "role": "Defender", "number": "22", "sot_90": 0.65, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": False},
            {"name": "Amir Rrahmani", "role": "Defender", "number": "13", "sot_90": 0.35, "fouls_c_90": 1.20, "saves_90": 0.0, "penalties": False},
            {"name": "Alessandro Buongiorno", "role": "Defender", "number": "4", "sot_90": 0.40, "fouls_c_90": 1.95, "saves_90": 0.0, "penalties": False},
            {"name": "Mathias Olivera", "role": "Defender", "number": "17", "sot_90": 0.30, "fouls_c_90": 1.60, "saves_90": 0.0, "penalties": False},
            {"name": "Stanislav Lobotka", "role": "Midfielder", "number": "68", "sot_90": 0.35, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": False},
            {"name": "Andre-Frank Zambo Anguissa", "role": "Midfielder", "number": "99", "sot_90": 0.85, "fouls_c_90": 1.75, "saves_90": 0.0, "penalties": False},
            {"name": "Scott McTominay", "role": "Midfielder", "number": "8", "sot_90": 1.20, "fouls_c_90": 1.65, "saves_90": 0.0, "penalties": False},
            {"name": "Matteo Politano", "role": "Attacker", "number": "21", "sot_90": 1.10, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": True},
            {"name": "Khvicha Kvaratskhelia", "role": "Attacker", "number": "77", "sot_90": 1.45, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": True},
            {"name": "Romelu Lukaku", "role": "Attacker", "number": "11", "sot_90": 1.60, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": True}
        ],
        "Manchester City": [
            {"name": "Ederson", "role": "Goalkeeper", "number": "31", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.3, "penalties": False},
            {"name": "Josko Gvardiol", "role": "Defender", "number": "24", "sot_90": 0.80, "fouls_c_90": 0.90, "saves_90": 0.0, "penalties": False},
            {"name": "Ruben Dias", "role": "Defender", "number": "3", "sot_90": 0.35, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Manuel Akanji", "role": "Defender", "number": "25", "sot_90": 0.30, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Rodri", "role": "Midfielder", "number": "16", "sot_90": 1.10, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": False},
            {"name": "Kevin De Bruyne", "role": "Midfielder", "number": "17", "sot_90": 1.35, "fouls_c_90": 0.75, "saves_90": 0.0, "penalties": True},
            {"name": "Bernardo Silva", "role": "Midfielder", "number": "20", "sot_90": 0.90, "fouls_c_90": 1.20, "saves_90": 0.0, "penalties": False},
            {"name": "Phil Foden", "role": "Attacker", "number": "47", "sot_90": 1.55, "fouls_c_90": 0.70, "saves_90": 0.0, "penalties": False},
            {"name": "Savinho", "role": "Attacker", "number": "26", "sot_90": 1.10, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Jeremy Doku", "role": "Attacker", "number": "11", "sot_90": 1.20, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Erling Haaland", "role": "Attacker", "number": "9", "sot_90": 2.20, "fouls_c_90": 0.80, "saves_90": 0.0, "penalties": True}
        ],
        "Arsenal": [
            {"name": "David Raya", "role": "Goalkeeper", "number": "22", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.5, "penalties": False},
            {"name": "Gabriel Magalhaes", "role": "Defender", "number": "6", "sot_90": 0.55, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": False},
            {"name": "William Saliba", "role": "Defender", "number": "2", "sot_90": 0.25, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Jurrien Timber", "role": "Defender", "number": "12", "sot_90": 0.40, "fouls_c_90": 1.30, "saves_90": 0.0, "penalties": False},
            {"name": "Declan Rice", "role": "Midfielder", "number": "41", "sot_90": 0.85, "fouls_c_90": 1.35, "saves_90": 0.0, "penalties": False},
            {"name": "Thomas Partey", "role": "Midfielder", "number": "5", "sot_90": 0.70, "fouls_c_90": 1.55, "saves_90": 0.0, "penalties": False},
            {"name": "Martin Odegaard", "role": "Midfielder", "number": "8", "sot_90": 1.25, "fouls_c_90": 0.90, "saves_90": 0.0, "penalties": False},
            {"name": "Bukayo Saka", "role": "Attacker", "number": "7", "sot_90": 1.50, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": True},
            {"name": "Gabriel Martinelli", "role": "Attacker", "number": "11", "sot_90": 1.30, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Kai Havertz", "role": "Attacker", "number": "29", "sot_90": 1.45, "fouls_c_90": 1.85, "saves_90": 0.0, "penalties": True}
        ],
        "Real Madrid": [
            {"name": "Thibaut Courtois", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.8, "penalties": False},
            {"name": "Antonio Rudiger", "role": "Defender", "number": "22", "sot_90": 0.45, "fouls_c_90": 1.20, "saves_90": 0.0, "penalties": False},
            {"name": "Eder Militao", "role": "Defender", "number": "3", "sot_90": 0.35, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": False},
            {"name": "Dani Carvajal", "role": "Defender", "number": "2", "sot_90": 0.40, "fouls_c_90": 1.65, "saves_90": 0.0, "penalties": False},
            {"name": "Ferland Mendy", "role": "Defender", "number": "23", "sot_90": 0.20, "fouls_c_90": 1.30, "saves_90": 0.0, "penalties": False},
            {"name": "Aurelien Tchouameni", "role": "Midfielder", "number": "14", "sot_90": 0.70, "fouls_c_90": 1.70, "saves_90": 0.0, "penalties": False},
            {"name": "Federico Valverde", "role": "Midfielder", "number": "8", "sot_90": 1.30, "fouls_c_90": 1.05, "saves_90": 0.0, "penalties": False},
            {"name": "Jude Bellingham", "role": "Midfielder", "number": "5", "sot_90": 1.45, "fouls_c_90": 1.55, "saves_90": 0.0, "penalties": True},
            {"name": "Rodrygo", "role": "Attacker", "number": "11", "sot_90": 1.35, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Vinicius Junior", "role": "Attacker", "number": "7", "sot_90": 1.75, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": True},
            {"name": "Kylian Mbappe", "role": "Attacker", "number": "9", "sot_90": 2.15, "fouls_c_90": 0.90, "saves_90": 0.0, "penalties": True}
        ],
        "Barcellona": [
            {"name": "Marc-Andre ter Stegen", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.7, "penalties": False},
            {"name": "Pau Cubarsi", "role": "Defender", "number": "2", "sot_90": 0.20, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": False},
            {"name": "Inigo Martinez", "role": "Defender", "number": "5", "sot_90": 0.30, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": False},
            {"name": "Jules Kounde", "role": "Defender", "number": "23", "sot_90": 0.45, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Alejandro Balde", "role": "Defender", "number": "3", "sot_90": 0.35, "fouls_c_90": 1.05, "saves_90": 0.0, "penalties": False},
            {"name": "Pedri", "role": "Midfielder", "number": "8", "sot_90": 0.95, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": False},
            {"name": "Dani Olmo", "role": "Midfielder", "number": "20", "sot_90": 1.40, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": False},
            {"name": "Lamine Yamal", "role": "Attacker", "number": "19", "sot_90": 1.55, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Raphinha", "role": "Attacker", "number": "11", "sot_90": 1.60, "fouls_c_90": 1.25, "saves_90": 0.0, "penalties": True},
            {"name": "Robert Lewandowski", "role": "Attacker", "number": "9", "sot_90": 1.95, "fouls_c_90": 1.35, "saves_90": 0.0, "penalties": True}
        ],
        "Bayern Monaco": [
            {"name": "Manuel Neuer", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.4, "penalties": False},
            {"name": "Dayot Upamecano", "role": "Defender", "number": "2", "sot_90": 0.35, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": False},
            {"name": "Kim Min-jae", "role": "Defender", "number": "3", "sot_90": 0.40, "fouls_c_90": 1.35, "saves_90": 0.0, "penalties": False},
            {"name": "Alphonso Davies", "role": "Defender", "number": "19", "sot_90": 0.65, "fouls_c_90": 1.20, "saves_90": 0.0, "penalties": False},
            {"name": "Joshua Kimmich", "role": "Midfielder", "number": "6", "sot_90": 0.85, "fouls_c_90": 1.25, "saves_90": 0.0, "penalties": False},
            {"name": "Jamal Musiala", "role": "Midfielder", "number": "42", "sot_90": 1.60, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Michael Olise", "role": "Attacker", "number": "17", "sot_90": 1.40, "fouls_c_90": 0.80, "saves_90": 0.0, "penalties": False},
            {"name": "Serge Gnabry", "role": "Attacker", "number": "7", "sot_90": 1.30, "fouls_c_90": 0.90, "saves_90": 0.0, "penalties": False},
            {"name": "Harry Kane", "role": "Attacker", "number": "9", "sot_90": 2.10, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": True}
        ],
        "PSG": [
            {"name": "Gianluigi Donnarumma", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 2.6, "penalties": False},
            {"name": "Marquinhos", "role": "Defender", "number": "5", "sot_90": 0.35, "fouls_c_90": 0.95, "saves_90": 0.0, "penalties": False},
            {"name": "Willian Pacho", "role": "Defender", "number": "51", "sot_90": 0.25, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": False},
            {"name": "Achraf Hakimi", "role": "Defender", "number": "2", "sot_90": 0.95, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": True},
            {"name": "Nuno Mendes", "role": "Defender", "number": "25", "sot_90": 0.60, "fouls_c_90": 1.25, "saves_90": 0.0, "penalties": False},
            {"name": "Vitinha", "role": "Midfielder", "number": "17", "sot_90": 1.15, "fouls_c_90": 1.10, "saves_90": 0.0, "penalties": True},
            {"name": "Joao Neves", "role": "Midfielder", "number": "87", "sot_90": 0.75, "fouls_c_90": 1.65, "saves_90": 0.0, "penalties": False},
            {"name": "Ousmane Dembele", "role": "Attacker", "number": "10", "sot_90": 1.65, "fouls_c_90": 0.85, "saves_90": 0.0, "penalties": False},
            {"name": "Bradley Barcola", "role": "Attacker", "number": "29", "sot_90": 1.55, "fouls_c_90": 0.90, "saves_90": 0.0, "penalties": False},
            {"name": "Goncalo Ramos", "role": "Attacker", "number": "9", "sot_90": 1.70, "fouls_c_90": 1.30, "saves_90": 0.0, "penalties": True}
        ]
    }
    
    for s_name, players in squads_2026_2027.items():
        if s_name.lower() in cleaned.lower() or cleaned.lower() in s_name.lower():
            return players
            
    # Per qualsiasi altra squadra, genera l'organico bilanciato
    return [
        {"name": f"Portiere ({cleaned})", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 3.2, "penalties": False},
        {"name": f"Centrale Difensivo 1 ({cleaned})", "role": "Defender", "number": "3", "sot_90": 0.30, "fouls_c_90": 1.60, "saves_90": 0.0, "penalties": False},
        {"name": f"Centrale Difensivo 2 ({cleaned})", "role": "Defender", "number": "4", "sot_90": 0.25, "fouls_c_90": 1.70, "saves_90": 0.0, "penalties": False},
        {"name": f"Terzino Destro ({cleaned})", "role": "Defender", "number": "2", "sot_90": 0.40, "fouls_c_90": 1.30, "saves_90": 0.0, "penalties": False},
        {"name": f"Terzino Sinistro ({cleaned})", "role": "Defender", "number": "5", "sot_90": 0.45, "fouls_c_90": 1.35, "saves_90": 0.0, "penalties": False},
        {"name": f"Mediano ({cleaned})", "role": "Midfielder", "number": "6", "sot_90": 0.55, "fouls_c_90": 1.90, "saves_90": 0.0, "penalties": False},
        {"name": f"Regista ({cleaned})", "role": "Midfielder", "number": "8", "sot_90": 0.85, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": True},
        {"name": f"Trequartista ({cleaned})", "role": "Midfielder", "number": "10", "sot_90": 1.10, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": False},
        {"name": f"Ala Destra ({cleaned})", "role": "Attacker", "number": "7", "sot_90": 1.25, "fouls_c_90": 1.05, "saves_90": 0.0, "penalties": False},
        {"name": f"Ala Sinistra ({cleaned})", "role": "Attacker", "number": "11", "sot_90": 1.30, "fouls_c_90": 1.00, "saves_90": 0.0, "penalties": False},
        {"name": f"Centravanti ({cleaned})", "role": "Attacker", "number": "9", "sot_90": 1.65, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": True}
    ]

# RENDERING CAMPO TATTICO
def render_visual_pitch_html(team_name, formation_str, players_list, injured_names=None):
    if injured_names is None: injured_names = []
    gk = [p for p in players_list if p.get('role') == 'Goalkeeper']
    defs = [p for p in players_list if p.get('role') == 'Defender']
    mids = [p for p in players_list if p.get('role') == 'Midfielder']
    atts = [p for p in players_list if p.get('role') == 'Attacker']
    
    gk_player = gk[0] if gk else {"name": "Portiere", "number": "1"}
    
    def badge(p, is_gk=False):
        p_name = p.get('name', 'Giocatore')
        is_inj = any(inj_n.lower() in p_name.lower() for inj_n in injured_names)
        c = "#EF4444" if is_inj else ("#EAB308" if is_gk else "#FFFFFF")
        tc = "#FFFFFF" if is_inj else "#0B132B"
        num = "OUT" if is_inj else p.get('number', '-')
        nom = f"<s>{p_name}</s>" if is_inj else p_name
        return f'<div style="text-align:center;width:72px;display:inline-block;margin:3px;"><div style="width:28px;height:28px;border-radius:50%;background:{c};color:{tc};font-weight:800;font-size:10px;display:flex;align-items:center;justify-content:center;margin:0 auto 2px auto;border:2px solid #000;box-shadow:0 2px 4px rgba(0,0,0,0.5);">{num}</div><div style="color:#FFFFFF;font-size:10px;font-weight:700;text-shadow:0 1px 2px #000;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{nom}</div></div>'
        
    atts_h = "".join([badge(p) for p in atts[:3]])
    mids_h = "".join([badge(p) for p in mids[:5]])
    defs_h = "".join([badge(p) for p in defs[:5]])
    gk_h = badge(gk_player, is_gk=True)
    
    html = f'<div style="background:linear-gradient(180deg,#1e5138 0%,#143a28 100%);border:2px solid #2DD4BF;border-radius:8px;padding:14px 6px;text-align:center;margin-bottom:15px;box-shadow:inset 0 0 20px rgba(0,0,0,0.6);"><div style="color:#2DD4BF;font-weight:800;font-size:13px;margin-bottom:10px;letter-spacing:0.05em;">{team_name.upper()} • {formation_str}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{atts_h}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{mids_h}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{defs_h}</div><div style="display:flex;justify-content:center;">{gk_h}</div></div>'
    return html

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
        if injuries_df is None: injuries_df = pd.DataFrame()
        t_met = get_adjusted_metrics(team, injuries_df)
        o_met = get_adjusted_metrics(opp, injuries_df)
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
            "note": f"Efficienza: {gf:.2f} GF | Concessione Difensiva: {ga_opp:.2f} GA"
        }

    @staticmethod
    def analyze_corners_multiline(h_team, a_team, line=9.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        h_met = get_adjusted_metrics(h_team, injuries_df)
        a_met = get_adjusted_metrics(a_team, injuries_df)
        base = (h_met["corners_pro"] + a_met["corners_against"])/2.0 + (a_met["corners_pro"] + h_met["corners_against"])/2.0
        mod = 1.0
        if h_met["cross"] > 20.0 or a_met["cross"] > 20.0: mod += 0.08
        corners_final = base * mod
        prob = float(1.0 - poisson.cdf(line - 0.5, corners_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Corner Totali",
            "market_type": "Corner Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Corner Proiettati", "metric_val": f"{corners_final:.2f}",
            "note": f"Cross combinati: {h_met['cross']+a_met['cross']:.1f}"
        }

    @staticmethod
    def analyze_player_sot(player, opp_team, line=0.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        opp_met = get_adjusted_metrics(opp_team, injuries_df)
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
    def analyze_player_fouls(player, opp_team, ref_data, line=1.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        opp_met = get_adjusted_metrics(opp_team, injuries_df)
        ref_mod = 1.10 if ref_data.get("severity") == "Severo" else (0.90 if ref_data.get("severity") == "Permissivo" else 1.0)
        xf_final = player.get("fouls_c_90", 1.0) * (85 / 90) * (opp_met["fouls_against"] / 12.5) * ref_mod
        prob = float(1.0 - poisson.cdf(line - 0.5, xf_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Commessi ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xFouls Attesi", "metric_val": f"{xf_final:.2f}",
            "note": f"Arbitro: {ref_data.get('name', 'CAN')} (Media: {ref_data.get('fouls_avg', 26.0):.1f} falli/partita)"
        }

    @staticmethod
    def analyze_goalkeeper_saves(player, opp_team, line=2.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        opp_met = get_adjusted_metrics(opp_team, injuries_df)
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
    def analyze_disciplinary_match(h_team, a_team, ref_data, line=4.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        h_met = get_adjusted_metrics(h_team, injuries_df)
        a_met = get_adjusted_metrics(a_team, injuries_df)
        cards_exp = (h_met["cards_avg"] + a_met["cards_avg"]) / 2.0 * (ref_data["cards_avg"] / 4.5) * 2.0
        prob = float(1.0 - poisson.cdf(line - 0.5, cards_exp))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Cartellini Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Cartellini Attesi", "metric_val": f"{cards_exp:.2f}",
            "note": f"Arbitro: {ref_data['name']} (Media: {ref_data['cards_avg']:.1f} cartellini - Severita: {ref_data['severity']})"
        }

# Calendario per il campionato selezionato
def get_league_matches(league_label):
    now_dt = datetime.datetime.now()
    if "Premier" in league_label:
        return [
            {"home_team": "Manchester City", "away_team": "Arsenal", "commence_time": now_dt.isoformat()},
            {"home_team": "Liverpool", "away_team": "Chelsea", "commence_time": now_dt.isoformat()},
            {"home_team": "Tottenham", "away_team": "Manchester United", "commence_time": now_dt.isoformat()},
            {"home_team": "Aston Villa", "away_team": "Newcastle", "commence_time": now_dt.isoformat()}
        ]
    elif "La Liga" in league_label:
        return [
            {"home_team": "Real Madrid", "away_team": "Barcellona", "commence_time": now_dt.isoformat()},
            {"home_team": "Atletico Madrid", "away_team": "Sevilla", "commence_time": now_dt.isoformat()},
            {"home_team": "Real Sociedad", "away_team": "Athletic Bilbao", "commence_time": now_dt.isoformat()}
        ]
    elif "Bundesliga" in league_label:
        return [
            {"home_team": "Bayern Monaco", "away_team": "Bayer Leverkusen", "commence_time": now_dt.isoformat()},
            {"home_team": "Borussia Dortmund", "away_team": "RB Leipzig", "commence_time": now_dt.isoformat()},
            {"home_team": "Eintracht Frankfurt", "away_team": "Stuttgart", "commence_time": now_dt.isoformat()}
        ]
    elif "Ligue 1" in league_label:
        return [
            {"home_team": "PSG", "away_team": "Marseille", "commence_time": now_dt.isoformat()},
            {"home_team": "Monaco", "away_team": "Lyon", "commence_time": now_dt.isoformat()},
            {"home_team": "Lille", "away_team": "Lens", "commence_time": now_dt.isoformat()}
        ]
    # Serie A
    return [
        {"home_team": "Inter", "away_team": "Juventus", "commence_time": now_dt.isoformat()},
        {"home_team": "Milan", "away_team": "Napoli", "commence_time": now_dt.isoformat()},
        {"home_team": "Atalanta", "away_team": "Roma", "commence_time": now_dt.isoformat()},
        {"home_team": "Lazio", "away_team": "Fiorentina", "commence_time": now_dt.isoformat()},
        {"home_team": "Bologna", "away_team": "Torino", "commence_time": now_dt.isoformat()}
    ]

# Header & Sidebar
st.title("VALUE BET ANALYZER")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)

is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE (DEMO)"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")

# SELETTORE COMPETIZIONE
st.sidebar.markdown("---")
st.sidebar.markdown("### SELEZIONA COMPETIZIONE")
selected_league_label = st.sidebar.selectbox("Campionato / Torneo", list(LEAGUES_CONFIG.keys()), index=0)
selected_league_cfg = LEAGUES_CONFIG[selected_league_label]
sport_api_key = selected_league_cfg["key"]

if not is_premium:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### SBLOCCO PIANO PRO")
    promo_code = st.sidebar.text_input("Codice VIP / Tester", placeholder="Inserisci codice...", type="password", key="side_promo_in")
    if st.sidebar.button("ATTIVA PREMIUM", use_container_width=True, key="side_promo_btn"):
        if promo_code:
            ok, msg = redeem_vip_code(user_id, promo_code)
            if ok:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.error(msg)

    # Box Rapido di Sblocco a Schermo per Smartphone
    with st.expander("🔓 SBLOCCA PIANO PREMIUM (Inserisci Codice VIP)", expanded=True):
        c_m1, c_m2 = st.columns([3, 1])
        with c_m1:
            mob_code = st.text_input("Codice Promozionale VIP", placeholder="es. Valuebet2026", type="password", key="mob_vip_in")
        with c_m2:
            st.write("")
            st.write("")
            if st.button("ATTIVA ORA", use_container_width=True, key="mob_vip_btn"):
                if mob_code:
                    ok, msg = redeem_vip_code(user_id, mob_code)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

if st.sidebar.button("LOGOUT", use_container_width=True):
    logout_user()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### PARAMETRI OPERATIVI")
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.select_slider(
    "Frazione di Kelly",
    options=[0.25, 0.50],
    value=0.50,
    format_func=lambda x: "0.25 (Prudente / Kelly/4)" if x == 0.25 else "0.50 (Standard / Kelly Mezzato)"
)
min_edge_pct = st.sidebar.slider("Soglia Minima Edge (%)", min_value=1.0, max_value=3.0, value=1.5, step=0.5)
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

# Infortuni e Partite
injuries_df = fetch_injuries()
matches = get_league_matches(selected_league_label)

st.markdown(f'<div class="round-badge">{selected_league_label.upper()} • TURNO IN CORSO (ROSE 2026/2027 ATTIVE)</div>', unsafe_allow_html=True)

# TUTTE LE 8 SCHEDE ORIGINALI ATTIVE
tab_scan, tab1, tab2, tab3, tab4, tab_inj, tab5, tab6 = st.tabs([
    "Scanner Top 5 del Turno",
    "Mercati Principali",
    "Statistiche & Tattica Squadre",
    "Prestazioni Calciatori & Portieri",
    "Focus Disciplinare & Arbitri",
    "Infermeria",
    "Registro Scommesse",
    "Gestione Account"
])

# 1. SCANNER TOP 5 DEL TURNO
with tab_scan:
    st.markdown(f"### TOP 5 VALUE BETS ({selected_league_label.upper()})")
    st.caption("Classifica ordinata per valore atteso reale (Over 1.5 Gol Squadra e Corner Totali).")
    
    with st.expander("Guida ai Termini & Legenda Quantitativa", expanded=False):
        st.markdown("""
        * **Probabilita Modello:** La percentuale reale stimata dal nostro algoritmo matematico.
        * **Quota Equa:** Il prezzo puro matematico dell'evento ($1 / \\text{Probabilita}$).
        * **Quota Minima (Valore):** Il prezzo minimo a cui conviene entrare sul mercato. Se il tuo bookmaker offre una quota pari o superiore, la giocata ha valore matematico (Value Bet).
        * **Edge:** Il margine di vantaggio percentuale stimato rispetto al banco.
        * **Stake:** L'importo monetario raccomandato dalla formula di Kelly.
        """)
    
    all_opportunities = []
    for m in matches:
        h = clean_name(m.get("home_team", ""))
        a = clean_name(m.get("away_team", ""))
        m_title = f"{h} vs {a}"
        m_date = m.get("commence_time", "")[:10]
        all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_team_goals_over15(h, a, True, min_edge_val, injuries_df)})
        all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_team_goals_over15(a, h, False, min_edge_val, injuries_df)})
        for l_c in [8.5, 9.5, 10.5]:
            all_opportunities.append({"match": m_title, "date": m_date, **MatchAnalystEngine.analyze_corners_multiline(h, a, l_c, min_edge_val, injuries_df)})
    
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
                    st.metric("Probabilita Reale", f"{item['prob']*100:.1f}%")
                    st.write(f"**Quota Equa:** `{item['fair_odds']:.2f}` | **Quota Minima di Ingresso:** `{item['min_odds']:.2f}`")
                    st.info(f"**Dettaglio Tecnico:** {item['note']}")
                with col_t2:
                    init_val = safe_odds_val(item['min_odds'])
                    odd_check = st.number_input(f"Inserisci Quota del tuo Bookmaker (#{pos})", min_value=1.01, max_value=20.0, value=init_val, step=0.02, key=f"top_odd_{idx}_{sport_api_key}")
                    calc_edge = (item['prob'] * odd_check) - 1.0
                    k_p, k_e = MatchAnalystEngine.calculate_kelly(item['prob'], odd_check, current_bankroll, kelly_fraction)
                    if odd_check >= item['min_odds'] and calc_edge >= min_edge_val:
                        st.success(f"VALORE PRESENTE: Edge {calc_edge*100:+.2f}%\nStake: {k_p}% ({k_e:.2f} €)")
                        if st.button(f"REGISTRA GIOCATA #{pos}", key=f"btn_save_top_{idx}_{sport_api_key}"):
                            save_user_bet(user_id, item["match"], item["market"], odd_check, k_e, calc_edge)
                            st.rerun()
                    else:
                        st.error(f"NO BET (Quota sotto soglia minima - Edge: {calc_edge*100:+.2f}%)")

# 2. MERCATI PRINCIPALI
with tab1:
    st.markdown(f"### TOP 5 MERCATI PRINCIPALI ({selected_league_label.upper()})")
    cat1_all = []
    for m in matches:
        h = clean_name(m.get("home_team", ""))
        a = clean_name(m.get("away_team", ""))
        m_title = f"{h} vs {a}"
        m_date = m.get("commence_time", "")[:10]
        
        h_met = get_adjusted_metrics(h, injuries_df)
        a_met = get_adjusted_metrics(a, injuries_df)
        lambda_tot = (h_met["gf_h"] + a_met["gf_a"] + a_met["ga_h"] + h_met["ga_a"]) / 2.0
        p_ov25 = float(1.0 - (poisson.pmf(0, lambda_tot) + poisson.pmf(1, lambda_tot) + poisson.pmf(2, lambda_tot)))
        p_un25 = 1.0 - p_ov25
        
        avg_ov = round(1.0 / p_ov25 * 1.04, 2)
        edge_ov = (p_ov25 * avg_ov) - 1.0
        st_p_o, st_e_o = MatchAnalystEngine.calculate_kelly(p_ov25, avg_ov, current_bankroll, kelly_fraction)
        cat1_all.append({
            "PARTITA": m_title, "DATA": m_date, "MERCATO": "Over 2.5 Totali",
            "QUOTA LIVE": f"{avg_ov:.2f}", "PROB REALE": f"{p_ov25*100:.1f}%",
            "EDGE": f"{edge_ov*100:+.2f}%", "STAKE": f"{st_p_o}% ({st_e_o:.2f} €)",
            "edge_num": edge_ov, "prob_num": p_ov25, "odds_num": avg_ov, "stake_eur": st_e_o
        })
        
        avg_un = round(1.0 / p_un25 * 1.04, 2)
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

# 3. STATISTICHE & TATTICA SQUADRE
with tab2:
    st.markdown(f"### STATISTICHE, QUADRO TATTICO & DISPOSIZIONE ({selected_league_label.upper()})")
    match_options = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
    sel_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options)), format_func=lambda x: match_options[x], key=f"c2_match_sel_{sport_api_key}")
    
    m_sel = matches[sel_idx]
    h2 = clean_name(m_sel["home_team"])
    a2 = clean_name(m_sel["away_team"])
    
    h_met2 = get_adjusted_metrics(h2, injuries_df)
    a_met2 = get_adjusted_metrics(a2, injuries_df)
    
    st.markdown(f'<div class="lineup-badge-off">FORMAZIONE CONFERMATA 2026/2027</div>', unsafe_allow_html=True)
    st.markdown(f"#### Quadro Tattico: {h2} ({h_met2['modulo']}) vs {a2} ({a_met2['modulo']})")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(f"""
        <div class="tactical-card">
            <b>{h2.upper()} (Casa)</b><br>
            • <b>Modulo:</b> {h_met2['modulo']}<br>
            • <b>Identita Tattica:</b> {h_met2['stile']}<br>
            • <b>Possesso Palla Stimato:</b> {h_met2['possesso']:.1f}%<br>
            • <b>Cross Medi:</b> {h_met2['cross']:.1f} / gara
        </div>
        """, unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"""
        <div class="tactical-card">
            <b>{a2.upper()} (Trasferta)</b><br>
            • <b>Modulo:</b> {a_met2['modulo']}<br>
            • <b>Identita Tattica:</b> {a_met2['stile']}<br>
            • <b>Possesso Palla Stimato:</b> {a_met2['possesso']:.1f}%<br>
            • <b>Cross Medi:</b> {a_met2['cross']:.1f} / gara
        </div>
        """, unsafe_allow_html=True)
        
    inj_h_list = injuries_df[injuries_df["team"].str.lower() == h2.lower()]["player_name"].tolist() if not injuries_df.empty else []
    inj_a_list = injuries_df[injuries_df["team"].str.lower() == a2.lower()]["player_name"].tolist() if not injuries_df.empty else []

    st.markdown("#### Disposizione in Campo dei Titolari (11 vs 11)")
    h2_squad = get_team_squad(h2, FOOTBALL_KEY)
    a2_squad = get_team_squad(a2, FOOTBALL_KEY)
    
    col_pitch_h, col_pitch_a = st.columns(2)
    with col_pitch_h:
        st.markdown(render_visual_pitch_html(h2, h_met2['modulo'], h2_squad, inj_h_list), unsafe_allow_html=True)
    with col_pitch_a:
        st.markdown(render_visual_pitch_html(a2, a_met2['modulo'], a2_squad, inj_a_list), unsafe_allow_html=True)

    if inj_h_list or inj_a_list:
        inj_cards_html = ""
        if not injuries_df.empty:
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
    col_c2_1, col_c2_2 = st.columns(2)
    with col_c2_1:
        st.markdown("#### Mercato Over 1.5 Gol Squadra")
        team_choice = st.radio("Seleziona Squadra", [h2, a2], horizontal=True, key=f"c2_team_{sport_api_key}")
        is_home_sel = (team_choice == h2)
        opp_choice = a2 if is_home_sel else h2
        
        res_g = MatchAnalystEngine.analyze_team_goals_over15(team_choice, opp_choice, is_home_sel, min_edge_val, injuries_df)
        st.metric("Probabilita Modello", f"{res_g['prob']*100:.1f}%")
        st.write(f"**Quota Equa:** `{res_g['fair_odds']:.2f}` | **Quota Minima:** `{res_g['min_odds']:.2f}`")
        st.caption(res_g["note"])
        
        init_g = safe_odds_val(res_g['min_odds'])
        odd_g_in = st.number_input("Quota sul tuo Bookmaker (Over 1.5 Gol)", min_value=1.01, max_value=20.0, value=init_g, step=0.02, key=f"odd_g_in_{sport_api_key}")
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
        res_c = MatchAnalystEngine.analyze_corners_multiline(h2, a2, line_corn, min_edge_val, injuries_df)
        st.metric("Probabilita Modello", f"{res_c['prob']*100:.1f}%")
        st.write(f"**Quota Equa:** `{res_c['fair_odds']:.2f}` | **Quota Minima:** `{res_c['min_odds']:.2f}`")
        st.caption(res_c["note"])
        
        init_c = safe_odds_val(res_c['min_odds'])
        odd_c_in = st.number_input("Quota sul tuo Bookmaker (Corner)", min_value=1.01, max_value=20.0, value=init_c, step=0.02, key=f"odd_c_in_{sport_api_key}")
        edge_c = (res_c['prob'] * odd_c_in) - 1.0
        kp_c, ke_c = MatchAnalystEngine.calculate_kelly(res_c['prob'], odd_c_in, current_bankroll, kelly_fraction)
        if odd_c_in >= res_c['min_odds'] and edge_c >= min_edge_val:
            st.success(f"VALORE PRESENTE: Edge {edge_c*100:+.2f}% | Stake: {kp_c}% ({ke_c:.2f} €)")
            if st.button("SALVA BET CORNER", key=f"btn_save_c_{sport_api_key}"):
                save_user_bet(user_id, f"{h2} vs {a2}", res_c["market"], odd_c_in, ke_c, edge_c)
                st.rerun()
        else:
            st.error(f"NO BET (Quota insufficiente - Edge: {edge_c*100:+.2f}%)")

# 4. PRESTAZIONI CALCIATORI & PORTIERI
with tab3:
    st.markdown(f"### PRESTAZIONI CALCIATORI & PORTIERI ({selected_league_label.upper()})")
    match_options_c3 = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
    sel_m3_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options_c3)), format_func=lambda x: match_options_c3[x], key="c3_match_sel_sa")
    
    m3 = matches[sel_m3_idx]
    h3 = clean_name(m3["home_team"])
    a3 = clean_name(m3["away_team"])
    
    h3_players = get_team_squad(h3, FOOTBALL_KEY)
    a3_players = get_team_squad(a3, FOOTBALL_KEY)
    
    st.markdown("---")
    tab_h, tab_a = st.tabs([f"Squadra Casa: {h3} (Titolari)", f"Squadra Trasferta: {a3} (Titolari)"])
    
    def render_player_analysis(players_list, team_name, opp_team, key_prefix):
        if not players_list:
            st.warning(f"Caricamento rosa in corso per {team_name}...")
            return
        
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
            st.error(f"ATTENZIONE: {chosen_p['name']} e attualmente inserito in Infermeria per infortunio. Mercato disabilitato.")
            return
        
        st.markdown(f"**Ruolo:** `{chosen_p['role']}` | **Avversario Diretto:** `{opp_team}`")
        
        if chosen_p["role"] == "Goalkeeper":
            st.markdown("#### Mercato: Parate Portiere")
            saves_line = st.selectbox("Linea Parate", [1.5, 2.5, 3.5, 4.5], index=1, key=f"{key_prefix}_saves_line")
            saves_res = MatchAnalystEngine.analyze_goalkeeper_saves(chosen_p, opp_team, saves_line, min_edge_val, injuries_df)
            st.metric("Probabilita Modello", f"{saves_res['prob']*100:.1f}%")
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
                sot_res = MatchAnalystEngine.analyze_player_sot(chosen_p, opp_team, sot_line, min_edge_val, injuries_df)
                st.metric("Probabilita Modello", f"{sot_res['prob']*100:.1f}%")
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
                foul_res = MatchAnalystEngine.analyze_player_fouls(chosen_p, opp_team, {"name": "Arbitro Ufficiale", "fouls_avg": 26.0, "severity": "Standard"}, foul_line, min_edge_val, injuries_df)
                st.metric("Probabilita Modello", f"{foul_res['prob']*100:.1f}%")
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
        render_player_analysis(h3_players, h3, a3, "h_tab_sa")
    with tab_a:
        render_player_analysis(a3_players, a3, h3, "a_tab_sa")

# 5. FOCUS DISCIPLINARE & ARBITRI
with tab4:
    st.markdown("### FOCUS DISCIPLINARE & ARBITRI")
    st.caption("Organico direttori di gara con calcolo quantitativo sui cartellini.")
    
    match_options_c4 = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
    sel_m4_idx = st.selectbox("Seleziona Incontro", range(len(match_options_c4)), format_func=lambda x: match_options_c4[x], key="c4_match_sel_sa")
    
    m4 = matches[sel_m4_idx]
    h4 = clean_name(m4["home_team"])
    a4 = clean_name(m4["away_team"])
    
    ref_names_list = sorted(list(SERIE_A_REFEREES_DB.keys()))
    chosen_ref_key = st.selectbox("Seleziona l'arbitro", ref_names_list, format_func=lambda x: SERIE_A_REFEREES_DB[x]["name"])
    ref_data = SERIE_A_REFEREES_DB[chosen_ref_key]
            
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        st.markdown(f"#### Metriche Arbitro: `{ref_data['name']}`")
        st.write(f"- **Media Cartellini / Partita:** `{ref_data['cards_avg']:.1f}`")
        st.write(f"- **Media Falli Fischiati / Partita:** `{ref_data['fouls_avg']:.1f}`")
        st.write(f"- **Indice di Severita Disciplinare:** `{ref_data['severity']}`")
            
    with col_ref2:
        st.markdown("#### Calcolo Cartellini Totali")
        cards_line = st.selectbox("Linea Cartellini Totali", [3.5, 4.5, 5.5], index=1, key="c4_cards_line_sa")
        disc_res = MatchAnalystEngine.analyze_disciplinary_match(h4, a4, ref_data, cards_line, min_edge_val, injuries_df)
        
        st.metric("Probabilita Modello", f"{disc_res['prob']*100:.1f}%")
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

# 6. SCHEDA INFERMERIA
with tab_inj:
    st.markdown("### GESTIONE INFERMERIA & INDISPONIBILI")
    st.caption("Inserisci qui i calciatori infortunati. L'algoritmo ricalcolera istantaneamente il peso su xG e linee statistiche.")
    
    col_inj_in1, col_inj_in2 = st.columns(2)
    with col_inj_in1:
        inj_team = st.text_input("Squadra", placeholder="es. Inter, Real Madrid, Manchester City...", key="inj_team_input")
        inj_player = st.text_input("Nome e Cognome Calciatore", placeholder="es. Dusan Vlahovic", key="inj_player_input")
        inj_importance = st.selectbox(
            "Ruolo & Importanza Tattica",
            [
                "Top Player Offensivo",
                "Titolare Mediano / Regista",
                "Difensore Chiave",
                "Portiere Titolare",
                "Riserva Offensiva / Rotazione",
                "Riserva Difensiva / Rotazione"
            ],
            key="inj_importance_select"
        )
    with col_inj_in2:
        inj_type = st.text_input("Tipo di Infortunio / Diagnosi", placeholder="es. Lesione bicipite femorale", key="inj_type_input")
        inj_return = st.text_input("Data Presunta Rientro", placeholder="es. 30/10/2026", key="inj_return_input")
        st.write("")
        st.write("")
        if st.button("AGGIUNGI IN INFERMERIA", use_container_width=True):
            if inj_team and inj_player and inj_type:
                ok = save_injury(inj_team, inj_player, inj_importance, inj_type, inj_return or "Da definire")
                if ok:
                    st.success(f"{inj_player} ({inj_team}) registrato in infermeria.")
                    st.rerun()
                else:
                    st.error("Errore salvataggio infortunio su database Supabase.")
            else:
                st.warning("Compila tutti i campi obbligatori.")
                
    st.markdown("---")
    st.markdown("#### Elenco Calciatori Attualmente Indisponibili")
    current_injuries = fetch_injuries()
    
    if not current_injuries.empty:
        disp_inj = current_injuries[["id", "team", "player_name", "importance", "injury_type", "return_date"]].copy()
        st.dataframe(
            disp_inj,
            column_config={
                "id": "ID", "team": "SQUADRA", "player_name": "CALCIATORE",
                "importance": "IMPORTANZA TATTICA", "injury_type": "DIAGNOSI", "return_date": "DATA RIENTRO"
            },
            use_container_width=True, hide_index=True
        )
        
        st.markdown("##### Rimuovi Calciatore Rientrato dall'Infortunio")
        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            del_id = st.selectbox("Seleziona Calciatore da Rimuovere", current_injuries["id"].tolist(), format_func=lambda x: f"{current_injuries.loc[current_injuries['id']==x, 'player_name'].values[0]} ({current_injuries.loc[current_injuries['id']==x, 'team'].values[0]})")
        with col_del2:
            st.write("")
            st.write("")
            if st.button("RIMUOVI DALL'INFERMERIA", use_container_width=True):
                delete_injury(del_id)
                st.success("Calciatore rimosso dall'infermeria.")
                st.rerun()
    else:
        st.info("Nessun calciatore inserito in infermeria.")

# 7. REGISTRO SCOMMESSE
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

# 8. GESTIONE ACCOUNT
with tab6:
    st.markdown("### GESTIONE ACCOUNT")
    with st.expander("Il Mio Profilo", expanded=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Email:** `{user_email}`")
            st.markdown(f"**Stato Abbonamento:** `{tier_label}`")
        with col_p2:
            st.markdown(f"**ID Utente:** `{user_id}`")
            
    if not is_premium:
        with st.expander("Sblocca Piano Premium con Codice VIP", expanded=True):
            acc_code = st.text_input("Inserisci Codice VIP", type="password", key="acc_vip_code_key")
            if st.button("ATTIVA PIANO PREMIUM", key="acc_btn_vip_key"):
                if acc_code:
                    ok, msg = redeem_vip_code(user_id, acc_code)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with st.expander("Modifica Password"):
        new_pwd = st.text_input("Nuova Password (min. 6 caratteri)", type="password", key="chg_pwd_key")
        conf_pwd = st.text_input("Conferma Nuova Password", type="password", key="conf_pwd_key")
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
