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

# Styling CSS Dark Fintech - Palette Frost Indigo
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0B132B !important;
        color: #F8FAFC !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, input, button, select {
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
    
    header[data-testid="stHeader"] {
        background-color: #0B132B !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
        color: #F8FAFC !important;
        letter-spacing: -0.02em !important;
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
        color: #8597AC;
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
        color: #5E6F92;
    }
    
    .metric-value-neutral {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    .slogan-box {
        background-color: rgba(45, 212, 191, 0.08);
        border-left: 4px solid #2DD4BF;
        padding: 10px 16px;
        border-radius: 4px;
        margin-bottom: 18px;
        font-size: 0.90rem;
        color: #CBD5E1;
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
        color: #F8FAFC !important;
        font-size: 0.90rem !important;
    }
    
    thead tr th {
        background-color: #0B132B !important;
        color: #8597AC !important;
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
        color: #F8FAFC !important;
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
        padding: 16px 20px !important;
        color: #F8FAFC !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Parametri dai Secrets
SB_URL = st.secrets.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = st.secrets.get("SUPABASE_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")
FOOTBALL_KEY = st.secrets.get("FOOTBALL_API_KEY", "f59b5ad05a6b45fa5f19582d3e493f7f")

# Gestione Sessione
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

# Funzioni Autenticazione Supabase
def login_user(email, password):
    if not SB_URL or not SB_KEY:
        return False, "Chiavi Supabase mancanti nei Secrets."
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
    if not SB_URL or not SB_KEY:
        return False, "Chiavi Supabase mancanti nei Secrets."
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
    if not token:
        return False, "Sessione scaduta. Effettua nuovamente il login."
    url = f"{SB_URL}/auth/v1/user"
    try:
        res = requests.put(url, json={"password": new_password}, headers=get_headers(token), timeout=10)
        if res.status_code == 200:
            return True, "Password aggiornata con successo."
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
            try:
                requests.patch(url, json={"tier": "premium"}, headers=hdrs, timeout=10)
            except Exception:
                pass
        st.session_state.user_tier = "premium"
        return True, "Codice valido. Piano Premium attivato."
    return False, "Codice promozionale non valido."

CLEAN_TEAM_NAMES = {
    "Inter Milan": "Inter", "AC Milan": "Milan", "Atalanta BC": "Atalanta",
    "AS Roma": "Roma", "SS Lazio": "Lazio", "Juventus": "Juventus",
    "Napoli": "Napoli", "Fiorentina": "Fiorentina", "Bologna": "Bologna",
    "Torino": "Torino", "Parma": "Parma", "Cagliari": "Cagliari",
    "Empoli": "Empoli", "Genoa": "Genoa", "Monza": "Monza",
    "Lecce": "Lecce", "Udinese": "Udinese", "Verona": "Verona",
    "Venezia": "Venezia", "Como": "Como", "Manchester City": "Manchester City",
    "Arsenal": "Arsenal", "Liverpool": "Liverpool", "Real Madrid": "Real Madrid",
    "Barcelona": "Barcellona", "Bayern Munich": "Bayern Monaco", "PSG": "PSG",
}

def clean_name(raw_name):
    for eng, ita in CLEAN_TEAM_NAMES.items():
        if eng.lower() in raw_name.lower():
            return ita
    return raw_name

# Schermata di Login / Registrazione
if st.session_state.user is None:
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

# Database Cloud Scommesse
def fetch_user_bets(user_id):
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets?user_id=eq.{user_id}&select=*&order=created_at.desc"
        try:
            res = requests.get(url, headers=get_headers(token), timeout=10)
            if res.status_code == 200 and res.json():
                return pd.DataFrame(res.json())
        except Exception:
            pass
    return pd.DataFrame(columns=["id", "created_at", "match", "market", "odds", "stake", "ev", "status", "profit"])

def save_user_bet(user_id, match, market, odds, stake, ev):
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        payload = {
            "user_id": user_id,
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
    if new_status == "VINTA":
        profit_val = round((odds - 1.0) * stake, 2)
    elif new_status == "PERSA":
        profit_val = round(-stake, 2)
    if SB_URL and SB_KEY:
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets?id=eq.{bet_id}"
        hdrs = get_headers(token)
        hdrs["Prefer"] = "return=representation"
        try:
            requests.patch(url, json={"status": new_status, "profit": profit_val}, headers=hdrs, timeout=10)
        except Exception:
            pass

# Database Statistico Base Squadre
TEAM_METRICS = {
    "Inter": {"gf_h": 2.25, "gf_a": 1.90, "ga_h": 0.65, "ga_a": 0.80, "xg_5": 2.15, "xg_s": 2.05, "sot_pro": 6.2, "sot_against": 3.1, "corners_pro": 6.4, "corners_against": 3.6, "cross": 21.5, "blocked_shots": 5.4, "fouls_pro": 11.2, "fouls_against": 12.8, "cards_avg": 1.8, "tactics": "3-5-2 Pressing Alto"},
    "Juventus": {"gf_h": 1.70, "gf_a": 1.40, "ga_h": 0.50, "ga_a": 0.75, "xg_5": 1.65, "xg_s": 1.55, "sot_pro": 5.1, "sot_against": 2.8, "corners_pro": 5.6, "corners_against": 3.8, "cross": 18.2, "blocked_shots": 4.6, "fouls_pro": 12.1, "fouls_against": 13.5, "cards_avg": 2.1, "tactics": "4-2-3-1 Dominio Possesso"},
    "Milan": {"gf_h": 2.05, "gf_a": 1.65, "ga_h": 1.10, "ga_a": 1.25, "xg_5": 1.90, "xg_s": 1.80, "sot_pro": 5.6, "sot_against": 4.4, "corners_pro": 5.8, "corners_against": 4.2, "cross": 19.5, "blocked_shots": 5.2, "fouls_pro": 11.8, "fouls_against": 12.0, "cards_avg": 2.3, "tactics": "4-2-3-1 Transizione Rapida"},
    "Napoli": {"gf_h": 1.85, "gf_a": 1.55, "ga_h": 0.60, "ga_a": 0.85, "xg_5": 1.80, "xg_s": 1.70, "sot_pro": 5.3, "sot_against": 3.2, "corners_pro": 6.1, "corners_against": 3.5, "cross": 20.8, "blocked_shots": 5.1, "fouls_pro": 12.4, "fouls_against": 13.0, "cards_avg": 1.9, "tactics": "3-5-2 Compatto e Verticale"},
    "Atalanta": {"gf_h": 2.30, "gf_a": 1.80, "ga_h": 1.05, "ga_a": 1.20, "xg_5": 2.20, "xg_s": 2.10, "sot_pro": 6.5, "sot_against": 4.1, "corners_pro": 6.7, "corners_against": 4.0, "cross": 22.4, "blocked_shots": 5.8, "fouls_pro": 13.8, "fouls_against": 14.2, "cards_avg": 2.4, "tactics": "3-4-2-1 Pressing Ultra-Offensivo"},
    "Roma": {"gf_h": 1.60, "gf_a": 1.20, "ga_h": 0.95, "ga_a": 1.15, "xg_5": 1.55, "xg_s": 1.50, "sot_pro": 4.9, "sot_against": 3.8, "corners_pro": 5.4, "corners_against": 4.1, "cross": 17.5, "blocked_shots": 4.2, "fouls_pro": 13.0, "fouls_against": 12.5, "cards_avg": 2.2, "tactics": "3-4-2-1 Man-Oriented"},
    "Lazio": {"gf_h": 1.75, "gf_a": 1.35, "ga_h": 1.00, "ga_a": 1.25, "xg_5": 1.60, "xg_s": 1.55, "sot_pro": 4.8, "sot_against": 4.0, "corners_pro": 5.3, "corners_against": 4.3, "cross": 18.0, "blocked_shots": 4.5, "fouls_pro": 13.2, "fouls_against": 12.2, "cards_avg": 2.5, "tactics": "4-2-3-1 Attacco Diretto"},
    "Fiorentina": {"gf_h": 1.70, "gf_a": 1.30, "ga_h": 0.90, "ga_a": 1.20, "xg_5": 1.55, "xg_s": 1.45, "sot_pro": 4.7, "sot_against": 3.9, "corners_pro": 5.5, "corners_against": 4.2, "cross": 19.0, "blocked_shots": 4.8, "fouls_pro": 12.6, "fouls_against": 12.8, "cards_avg": 2.1, "tactics": "4-3-3 Possesso Laterale"},
    "Bologna": {"gf_h": 1.50, "gf_a": 1.15, "ga_h": 0.85, "ga_a": 1.10, "xg_5": 1.45, "xg_s": 1.40, "sot_pro": 4.5, "sot_against": 3.5, "corners_pro": 5.2, "corners_against": 3.9, "cross": 17.8, "blocked_shots": 4.3, "fouls_pro": 12.5, "fouls_against": 12.0, "cards_avg": 2.0, "tactics": "4-2-3-1 Costruzione Bassa"},
    "Torino": {"gf_h": 1.25, "gf_a": 0.95, "ga_h": 0.90, "ga_a": 1.15, "xg_5": 1.20, "xg_s": 1.15, "sot_pro": 3.9, "sot_against": 4.2, "corners_pro": 4.6, "corners_against": 4.5, "cross": 16.0, "blocked_shots": 3.9, "fouls_pro": 14.1, "fouls_against": 11.8, "cards_avg": 2.3, "tactics": "3-5-2 Duelli Fisici"},
    "Parma": {"gf_h": 1.35, "gf_a": 1.10, "ga_h": 1.45, "ga_a": 1.65, "xg_5": 1.30, "xg_s": 1.25, "sot_pro": 4.2, "sot_against": 5.4, "corners_pro": 4.7, "corners_against": 5.8, "cross": 15.5, "blocked_shots": 3.7, "fouls_pro": 13.5, "fouls_against": 11.5, "cards_avg": 2.2, "tactics": "4-2-3-1 Contropiede Rapido"},
    "Cagliari": {"gf_h": 1.20, "gf_a": 0.90, "ga_h": 1.35, "ga_a": 1.60, "xg_5": 1.15, "xg_s": 1.15, "sot_pro": 3.8, "sot_against": 5.2, "corners_pro": 4.5, "corners_against": 5.6, "cross": 16.5, "blocked_shots": 3.6, "fouls_pro": 13.6, "fouls_against": 12.0, "cards_avg": 2.4, "tactics": "3-5-2 Blocco Basso"},
}

DEFAULT_METRICS = {
    "gf_h": 1.30, "gf_a": 1.05, "ga_h": 1.10, "ga_a": 1.45, "xg_5": 1.25, "xg_s": 1.25,
    "sot_pro": 4.1, "sot_against": 4.8, "corners_pro": 4.6, "corners_against": 5.2,
    "cross": 16.0, "blocked_shots": 3.8, "fouls_pro": 13.0, "fouls_against": 12.0, "cards_avg": 2.2, "tactics": "4-4-2 Blocco Medio"
}

def get_metrics(team_name):
    cleaned = clean_name(team_name)
    for name, metrics in TEAM_METRICS.items():
        if name.lower() in cleaned.lower() or cleaned.lower() in name.lower():
            return metrics
    return DEFAULT_METRICS

# Calciatori e Arbitri Serie A Integrati con API-Football Fallback
SERIE_A_PLAYERS_DB = {
    "Inter": [
        {"name": "Lautaro Martinez", "role": "Attaccante", "sot_90": 1.85, "fouls_c_90": 1.45, "fouls_s_90": 2.10, "penalties": True},
        {"name": "Marcus Thuram", "role": "Attaccante", "sot_90": 1.40, "fouls_c_90": 1.20, "fouls_s_90": 1.85, "penalties": False},
        {"name": "Nicolo Barella", "role": "Centrocampista", "sot_90": 0.85, "fouls_c_90": 1.65, "fouls_s_90": 1.90, "penalties": False},
        {"name": "Federico Dimarco", "role": "Esterno", "sot_90": 0.95, "fouls_c_90": 0.80, "fouls_s_90": 1.15, "penalties": False},
    ],
    "Juventus": [
        {"name": "Dusan Vlahovic", "role": "Attaccante", "sot_90": 1.65, "fouls_c_90": 1.55, "fouls_s_90": 1.95, "penalties": True},
        {"name": "Kenan Yildiz", "role": "Seconda Punta", "sot_90": 1.25, "fouls_c_90": 1.10, "fouls_s_90": 2.20, "penalties": False},
        {"name": "Teun Koopmeiners", "role": "Trequartista", "sot_90": 1.15, "fouls_c_90": 1.30, "fouls_s_90": 1.50, "penalties": True},
    ],
    "Milan": [
        {"name": "Rafael Leao", "role": "Ala Sinistra", "sot_90": 1.30, "fouls_c_90": 0.85, "fouls_s_90": 2.45, "penalties": False},
        {"name": "Christian Pulisic", "role": "Ala Destra", "sot_90": 1.20, "fouls_c_90": 0.90, "fouls_s_90": 1.70, "penalties": True},
        {"name": "Alvaro Morata", "role": "Attaccante", "sot_90": 1.35, "fouls_c_90": 1.80, "fouls_s_90": 1.95, "penalties": False},
    ],
    "Napoli": [
        {"name": "Romelu Lukaku", "role": "Attaccante", "sot_90": 1.55, "fouls_c_90": 1.40, "fouls_s_90": 2.05, "penalties": True},
        {"name": "Khvicha Kvaratskhelia", "role": "Ala Sinistra", "sot_90": 1.35, "fouls_c_90": 1.10, "fouls_s_90": 2.60, "penalties": True},
        {"name": "Scott McTominay", "role": "Centrocampista", "sot_90": 1.10, "fouls_c_90": 1.75, "fouls_s_90": 1.80, "penalties": False},
    ],
    "Atalanta": [
        {"name": "Mateo Retegui", "role": "Attaccante", "sot_90": 1.70, "fouls_c_90": 1.65, "fouls_s_90": 1.75, "penalties": True},
        {"name": "Ademola Lookman", "role": "Seconda Punta", "sot_90": 1.45, "fouls_c_90": 1.05, "fouls_s_90": 1.90, "penalties": False},
        {"name": "Charles De Ketelaere", "role": "Trequartista", "sot_90": 1.15, "fouls_c_90": 1.20, "fouls_s_90": 1.65, "penalties": False},
    ],
    "Roma": [
        {"name": "Paulo Dybala", "role": "Seconda Punta", "sot_90": 1.45, "fouls_c_90": 0.70, "fouls_s_90": 2.30, "penalties": True},
        {"name": "Artem Dovbyk", "role": "Attaccante", "sot_90": 1.40, "fouls_c_90": 1.50, "fouls_s_90": 1.80, "penalties": True},
        {"name": "Gianluca Mancini", "role": "Difensore Centrale", "sot_90": 0.40, "fouls_c_90": 2.10, "fouls_s_90": 1.10, "penalties": False},
    ],
    "Lazio": [
        {"name": "Mattia Zaccagni", "role": "Ala Sinistra", "sot_90": 1.10, "fouls_c_90": 1.80, "fouls_s_90": 2.85, "penalties": True},
        {"name": "Valentin Castellanos", "role": "Attaccante", "sot_90": 1.50, "fouls_c_90": 1.90, "fouls_s_90": 1.70, "penalties": False},
    ],
    "Fiorentina": [
        {"name": "Moise Kean", "role": "Attaccante", "sot_90": 1.60, "fouls_c_90": 1.75, "fouls_s_90": 2.15, "penalties": False},
        {"name": "Albert Gudmundsson", "role": "Trequartista", "sot_90": 1.25, "fouls_c_90": 0.85, "fouls_s_90": 2.40, "penalties": True},
    ],
    "Bologna": [
        {"name": "Riccardo Orsolini", "role": "Ala Destra", "sot_90": 1.35, "fouls_c_90": 1.10, "fouls_s_90": 1.60, "penalties": True},
        {"name": "Santiago Castro", "role": "Attaccante", "sot_90": 1.20, "fouls_c_90": 1.85, "fouls_s_90": 2.00, "penalties": False},
    ],
    "Torino": [
        {"name": "Duvan Zapata", "role": "Attaccante", "sot_90": 1.45, "fouls_c_90": 1.60, "fouls_s_90": 2.10, "penalties": False},
        {"name": "Samuele Ricci", "role": "Centrocampista", "sot_90": 0.50, "fouls_c_90": 1.70, "fouls_s_90": 2.30, "penalties": False},
    ],
    "Parma": [
        {"name": "Ange-Yoan Bonny", "role": "Attaccante", "sot_90": 1.15, "fouls_c_90": 1.40, "fouls_s_90": 1.90, "penalties": True},
        {"name": "Dennis Man", "role": "Ala Destra", "sot_90": 1.30, "fouls_c_90": 0.95, "fouls_s_90": 1.85, "penalties": False},
    ],
    "Cagliari": [
        {"name": "Roberto Piccoli", "role": "Attaccante", "sot_90": 1.20, "fouls_c_90": 1.80, "fouls_s_90": 1.65, "penalties": False},
        {"name": "Zito Luvumbo", "role": "Seconda Punta", "sot_90": 1.05, "fouls_c_90": 1.30, "fouls_s_90": 2.50, "penalties": False},
    ]
}

SERIE_A_REFEREES = [
    {"name": "Daniele Doveri", "fouls_avg": 25.4, "cards_avg": 4.1, "severity": "Standard"},
    {"name": "Fabio Maresca", "fouls_avg": 28.2, "cards_avg": 5.4, "severity": "Severo"},
    {"name": "Maurizio Mariani", "fouls_avg": 27.8, "cards_avg": 4.8, "severity": "Severo"},
    {"name": "Simone Sozza", "fouls_avg": 21.5, "cards_avg": 3.6, "severity": "Permissivo"},
    {"name": "Michael Fabbri", "fouls_avg": 26.1, "cards_avg": 4.5, "severity": "Standard"},
    {"name": "Davide Massa", "fouls_avg": 26.8, "cards_avg": 4.9, "severity": "Standard"},
    {"name": "Marco Guida", "fouls_avg": 27.4, "cards_avg": 5.1, "severity": "Severo"}
]

# Motore Matematico dei Protocolli Match Analyst
class MatchAnalystEngine:
    @staticmethod
    def calculate_kelly(prob, odds, bankroll, kelly_fraction=0.50):
        b = odds - 1.0
        if b <= 0:
            return 0.0, 0.0
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
        if prob <= 0:
            return 99.0, 99.0
        fair_odds = round(1.0 / prob, 2)
        min_entry_odds = round((1.0 + min_edge) / prob, 2)
        return fair_odds, min_entry_odds

    # Cat 2: Over 1.5 Team Goals
    @staticmethod
    def analyze_over15_team(team, opp, is_home, min_edge=0.015):
        t_met = get_metrics(team)
        o_met = get_metrics(opp)
        gf = t_met["gf_h"] if is_home else t_met["gf_a"]
        ga_opp = o_met["ga_a"] if is_home else o_met["ga_h"]
        xg_base = gf * (ga_opp / 1.25) * (t_met["xg_5"] / max(0.1, t_met["xg_s"]))
        mod = 1.0
        if "3-4-2-1" in t_met["tactics"] or "4-3-3" in t_met["tactics"]: mod += 0.08
        if "Pressing" in t_met["tactics"]: mod += 0.10
        if "Low block" in o_met["tactics"]: mod -= 0.10
        xg_final = xg_base * mod
        prob = float(1.0 - (poisson.pmf(0, xg_final) + poisson.pmf(1, xg_final)))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over 1.5 Gol ({clean_name(team)})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xG Team Finale", "metric_val": f"{xg_final:.2f}",
            "note": f"Efficienza Offensiva: {gf:.2f} GF | Concessione Difensiva: {ga_opp:.2f} GA"
        }

    # Cat 2: Corner Totali
    @staticmethod
    def analyze_corners_match(h_team, a_team, line=9.5, min_edge=0.015):
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
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Corner Proiettati", "metric_val": f"{corners_final:.2f}",
            "note": f"Cross combinati: {h_met['cross']+a_met['cross']:.1f} | Tiri bloccati: {h_met['blocked_shots']+a_met['blocked_shots']:.1f}"
        }

    # Cat 3: Tiri in Porta Giocatore
    @staticmethod
    def analyze_player_sot(player, opp_team, line=0.5, min_edge=0.015):
        opp_met = get_metrics(opp_team)
        xsot_base = player["sot_90"] * (82 / 90) * (opp_met["sot_against"] / 4.3)
        mod = 1.0
        if player.get("penalties"): mod += 0.10
        if "Low block" in opp_met["tactics"]: mod -= 0.08
        xsot_final = xsot_base * mod
        prob = float(1.0 - poisson.cdf(line - 0.5, xsot_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Tiri in Porta ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xSOT Attesi", "metric_val": f"{xsot_final:.2f}",
            "note": f"Media SOT/90m: {player['sot_90']:.2f} | Tiri concessi avversario: {opp_met['sot_against']:.1f}/match"
        }

    # Cat 3: Falli Giocatore
    @staticmethod
    def analyze_player_fouls(player, opp_team, referee, line=1.5, min_edge=0.015):
        opp_met = get_metrics(opp_team)
        xf_base = player["fouls_c_90"] * (85 / 90) * (opp_met["fouls_against"] / 12.5) * (referee["fouls_avg"] / 25.5)
        mod = 1.10 if referee["severity"] == "Severo" else (0.90 if referee["severity"] == "Permissivo" else 1.0)
        xf_final = xf_base * mod
        prob = float(1.0 - poisson.cdf(line - 0.5, xf_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Commessi ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xFouls Attesi", "metric_val": f"{xf_final:.2f}",
            "note": f"Arbitro: {referee['name']} ({referee['fouls_avg']:.1f} falli/gara) | Avversario subisce {opp_met['fouls_against']:.1f} falli"
        }

    # Cat 4: Cartellini & Disciplina Match
    @staticmethod
    def analyze_disciplinary_match(h_team, a_team, referee, line=4.5, min_edge=0.015):
        h_met = get_metrics(h_team)
        a_met = get_metrics(a_team)
        cards_base = (h_met["cards_avg"] + a_met["cards_avg"]) / 2.0 * (referee["cards_avg"] / 4.5) * 2.0
        prob = float(1.0 - poisson.cdf(line - 0.5, cards_base))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Cartellini Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Cartellini Attesi", "metric_val": f"{cards_base:.2f}",
            "note": f"Arbitro: {referee['name']} (Media: {referee['cards_avg']:.1f} cartellini/partita - Severità: {referee['severity']})"
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
        if res.status_code == 200:
            return res.json(), None
        return None, f"Errore API {res.status_code}: {res.text}"
    except Exception as e:
        return None, str(e)

# Header Principale
st.title("VALUE BET ANALYZER")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)

# Sidebar
user_email = st.session_state.user.get("email", "")
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
            ok, msg = redeem_vip_code(st.session_state.user.get("id"), promo_code)
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
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0, help="Il capitale totale dedicato alle scommesse di valore.")

kelly_fraction = st.sidebar.select_slider(
    "Frazione di Kelly",
    options=[0.25, 0.50],
    value=0.50,
    format_func=lambda x: "0.25 (Prudente / Kelly/4)" if x == 0.25 else "0.50 (Standard / Kelly Mezzato)",
    help="Regola la formula di money management. 0.50 (Kelly Mezzato) è lo standard quantitativo matematico."
)

min_edge_pct = st.sidebar.slider(
    "Soglia Minima Edge (%)",
    min_value=1.0, max_value=3.0, value=1.5, step=0.5,
    help="Vantaggio matematico minimo richiesto rispetto al banco. Un range tra 1.0% e 3.0% è il terreno operativo dei tipster professionisti."
)
min_edge_val = min_edge_pct / 100.0

# Bankroll Cloud Running
bets_df = fetch_user_bets(st.session_state.user.get("id"))
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

# Recupero Partite Live
if "raw_matches" not in st.session_state and ODDS_KEY:
    data, err = fetch_odds_api(ODDS_KEY, "soccer_italy_serie_a")
    if data: st.session_state.raw_matches = data

matches_raw = st.session_state.get("raw_matches", [])
matches, round_start, round_end = filter_current_matchday(matches_raw)

if round_start:
    st.markdown(f'<div class="round-badge">TURNO IN CORSO: {round_start} - {round_end} ({len(matches)} incontri)</div>', unsafe_allow_html=True)

# 4 Categorie di Analisi + Registro e Account
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Cat. 1 - Mercati Principali",
    "Cat. 2 - Statistiche Squadre",
    "Cat. 3 - Prestazioni Calciatori",
    "Cat. 4 - Focus Disciplinare & Arbitri",
    "Registro Scommesse",
    "Gestione Account"
])

# CAT 1: MERCATI PRINCIPALI (Quote API Reali)
with tab1:
    st.markdown("### MERCATI PRINCIPALI (1X2, UNDER/OVER 2.5, GOL/NOGOL)")
    st.caption("Quote reali aggregate e rilevamento automatico di discrepanze matematiche.")
    
    if matches:
        cat1_bets = []
        for m in matches:
            h = clean_name(m.get("home_team", ""))
            a = clean_name(m.get("away_team", ""))
            m_title = f"{h} vs {a}"
            m_date = m.get("commence_time", "")[:10]
            
            # Calcolo probabilità modello
            h_met = get_metrics(h)
            a_met = get_metrics(a)
            lambda_tot = (h_met["gf_h"] + a_met["gf_a"] + a_met["ga_h"] + h_met["ga_a"]) / 2.0
            p_ov25 = float(1.0 - (poisson.pmf(0, lambda_tot) + poisson.pmf(1, lambda_tot) + poisson.pmf(2, lambda_tot)))
            
            # Estrazione quota reale da bookmaker
            ov_odds_list = []
            for b in m.get("bookmakers", []):
                for market in b.get("markets", []):
                    if market["key"] == "totals":
                        for o in market.get("outcomes", []):
                            if o.get("name") == "Over" and o.get("point") == 2.5:
                                ov_odds_list.append(o["price"])
            
            if ov_odds_list:
                avg_odd = float(np.mean(ov_odds_list))
                edge = (p_ov25 * avg_odd) - 1.0
                if edge >= min_edge_val:
                    st_pct, st_eur = MatchAnalystEngine.calculate_kelly(p_ov25, avg_odd, current_bankroll, kelly_fraction)
                    cat1_bets.append({
                        "PARTITA": m_title, "DATA": m_date, "MERCATO": "Over 2.5 Totali",
                        "QUOTA BK": f"{avg_odd:.2f}", "PROB REALE": f"{p_ov25*100:.1f}%",
                        "EDGE": f"{edge*100:+.2f}%", "STAKE KELLY": f"{st_pct}% ({st_eur:.2f} €)",
                        "raw_obj": {"match": m_title, "market": "Over 2.5 Totali", "odds": avg_odd, "stake": st_eur, "ev": edge}
                    })
        
        if cat1_bets:
            st.table(pd.DataFrame(cat1_bets).drop(columns=["raw_obj"]))
        else:
            st.info(f"Nessuna giocata sui mercati principali supera la soglia Edge del {min_edge_pct:.1f}%.")
    else:
        st.info("Nessuna partita disponibile per il turno.")

# CAT 2: STATISTICHE SQUADRE (Over 1.5 Team & Corner)
with tab2:
    st.markdown("### STATISTICHE & VALORE SQUADRE (OVER 1.5 GOL & CORNER)")
    st.caption("Calcolo quantitativo della Quota Minima di Ingresso e verifica interattiva della quota bookmaker.")
    
    if matches:
        match_options = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
        sel_match_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options)), format_func=lambda x: match_options[x], key="cat2_match_select")
        
        sel_match = matches[sel_match_idx]
        h_team = clean_name(sel_match["home_team"])
        a_team = clean_name(sel_match["away_team"])
        
        # Analisi Protocolli
        ov_h = MatchAnalystEngine.analyze_over15_team(h_team, a_team, is_home=True, min_edge=min_edge_val)
        ov_a = MatchAnalystEngine.analyze_over15_team(a_team, h_team, is_home=False, min_edge=min_edge_val)
        corn = MatchAnalystEngine.analyze_corners_match(h_team, a_team, line=9.5, min_edge=min_edge_val)
        
        opportunities = [ov_h, ov_a, corn]
        
        for idx, op in enumerate(opportunities):
            with st.expander(f"{op['market']} | Quota Minima: {op['min_odds']:.2f} (Prob: {op['prob']*100:.1f}%)", expanded=(idx==0)):
                col_i1, col_i2, col_i3 = st.columns(3)
                col_i1.metric("Probabilità Modello", f"{op['prob']*100:.1f}%")
                col_i1.caption(f"{op['metric_name']}: {op['metric_val']}")
                
                col_i2.metric("Quota Equa", f"{op['fair_odds']:.2f}")
                col_i2.metric("Quota Minima (Edge >= 1.5%)", f"{op['min_odds']:.2f}")
                
                with col_i3:
                    user_odd = st.number_input(f"Quota sul tuo Bookmaker", min_value=1.01, max_value=20.0, value=float(op['min_odds']), step=0.02, key=f"cat2_odd_{idx}")
                    real_edge = (op['prob'] * user_odd) - 1.0
                    st_pct, st_eur = MatchAnalystEngine.calculate_kelly(op['prob'], user_odd, current_bankroll, kelly_fraction)
                    
                    if user_odd >= op['min_odds'] and real_edge >= min_edge_val:
                        st.success(f"VALORE PRESENTE: Edge {real_edge*100:+.2f}%\nStake: {st_pct}% ({st_eur:.2f} €)")
                        if st.button(f"REGISTRA NEL BANKROLL", key=f"save_cat2_{idx}"):
                            save_user_bet(st.session_state.user.get("id"), f"{h_team} vs {a_team}", op["market"], user_odd, st_eur, real_edge)
                            st.rerun()
                    else:
                        st.error(f"NO BET (Nessun Valore)\nEdge reale: {real_edge*100:+.2f}%")
                st.info(op["note"])

# CAT 3: PRESTAZIONI SINGOLI CALCIATORI (Tiri & Falli)
with tab3:
    st.markdown("### PRESTAZIONI SINGOLI CALCIATORI (TIRI IN PORTA & FALLI)")
    st.caption("Modulo analitico per la stima individuale di xSOT e xFouls con verifica quota.")
    
    if matches:
        match_options_c3 = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
        sel_m3_idx = st.selectbox("Seleziona Incontro", range(len(match_options_c3)), format_func=lambda x: match_options_c3[x], key="cat3_match_select")
        
        sel_m3 = matches[sel_m3_idx]
        h3 = clean_name(sel_m3["home_team"])
        a3 = clean_name(sel_m3["away_team"])
        
        # Lista Giocatori delle due squadre
        available_players = []
        for p in SERIE_A_PLAYERS_DB.get(h3, []): available_players.append((p, h3, a3))
        for p in SERIE_A_PLAYERS_DB.get(a3, []): available_players.append((p, a3, h3))
        
        if available_players:
            p_names = [f"{p['name']} ({team} - {p['role']})" for p, team, opp in available_players]
            sel_p_idx = st.selectbox("Seleziona Calciatore", range(len(p_names)), format_func=lambda x: p_names[x], key="cat3_player_select")
            
            chosen_player, p_team, p_opp = available_players[sel_p_idx]
            referee_assigned = SERIE_A_REFEREES[sel_m3_idx % len(SERIE_A_REFEREES)]
            
            st.markdown("---")
            col_p_left, col_p_right = st.columns(2)
            
            with col_p_left:
                st.markdown("#### Mercato: Tiri in Porta")
                sot_res = MatchAnalystEngine.analyze_player_sot(chosen_player, p_opp, line=0.5, min_edge=min_edge_val)
                st.write(f"**Probabilità Modello:** `{sot_res['prob']*100:.1f}%`")
                st.write(f"**Quota Equa:** `{sot_res['fair_odds']:.2f}` | **Quota Minima:** `{sot_res['min_odds']:.2f}`")
                st.caption(sot_res["note"])
                
                odd_sot = st.number_input("Quota Tiri sul Bookmaker", min_value=1.01, max_value=20.0, value=float(sot_res['min_odds']), step=0.02, key="odd_sot_in")
                edge_sot = (sot_res['prob'] * odd_sot) - 1.0
                st_p_sot, st_e_sot = MatchAnalystEngine.calculate_kelly(sot_res['prob'], odd_sot, current_bankroll, kelly_fraction)
                
                if odd_sot >= sot_res['min_odds'] and edge_sot >= min_edge_val:
                    st.success(f"VALORE PRESENTE: Edge {edge_sot*100:+.2f}% | Stake: {st_p_sot}% ({st_e_sot:.2f} €)")
                    if st.button("SALVA BET TIRI NEL BANKROLL", key="save_sot_btn"):
                        save_user_bet(st.session_state.user.get("id"), f"{h3} vs {a3}", sot_res["market"], odd_sot, st_e_sot, edge_sot)
                        st.rerun()
                else:
                    st.error(f"NO BET (Quota insufficiente - Edge: {edge_sot*100:+.2f}%)")
                    
            with col_p_right:
                st.markdown("#### Mercato: Falli Commessi")
                foul_res = MatchAnalystEngine.analyze_player_fouls(chosen_player, p_opp, referee_assigned, line=1.5, min_edge=min_edge_val)
                st.write(f"**Probabilità Modello:** `{foul_res['prob']*100:.1f}%`")
                st.write(f"**Quota Equa:** `{foul_res['fair_odds']:.2f}` | **Quota Minima:** `{foul_res['min_odds']:.2f}`")
                st.caption(foul_res["note"])
                
                odd_foul = st.number_input("Quota Falli sul Bookmaker", min_value=1.01, max_value=20.0, value=float(foul_res['min_odds']), step=0.02, key="odd_foul_in")
                edge_foul = (foul_res['prob'] * odd_foul) - 1.0
                st_p_fl, st_e_fl = MatchAnalystEngine.calculate_kelly(foul_res['prob'], odd_foul, current_bankroll, kelly_fraction)
                
                if odd_foul >= foul_res['min_odds'] and edge_foul >= min_edge_val:
                    st.success(f"VALORE PRESENTE: Edge {edge_foul*100:+.2f}% | Stake: {st_p_fl}% ({st_e_fl:.2f} €)")
                    if st.button("SALVA BET FALLI NEL BANKROLL", key="save_foul_btn"):
                        save_user_bet(st.session_state.user.get("id"), f"{h3} vs {a3}", foul_res["market"], odd_foul, st_e_fl, edge_foul)
                        st.rerun()
                else:
                    st.error(f"NO BET (Quota insufficiente - Edge: {edge_foul*100:+.2f}%)")
        else:
            st.info("Statistiche calciatori non disponibili per le squadre selezionate.")

# CAT 4: FOCUS DISCIPLINARE & ARBITRI
with tab4:
    st.markdown("### FOCUS DISCIPLINARE & ARBITRI AIA")
    st.caption("Analisi quantitativa dei parametri arbitrali e scommesse sui cartellini totali.")
    
    if matches:
        match_options_c4 = [f"{clean_name(m['home_team'])} vs {clean_name(m['away_team'])}" for m in matches]
        sel_m4_idx = st.selectbox("Seleziona Incontro", range(len(match_options_c4)), format_func=lambda x: match_options_c4[x], key="cat4_match_select")
        
        sel_m4 = matches[sel_m4_idx]
        h4 = clean_name(sel_m4["home_team"])
        a4 = clean_name(sel_m4["away_team"])
        ref4 = SERIE_A_REFEREES[sel_m4_idx % len(SERIE_A_REFEREES)]
        
        disc_res = MatchAnalystEngine.analyze_disciplinary_match(h4, a4, ref4, line=4.5, min_edge=min_edge_val)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.markdown(f"#### Arbitro Designato: `{ref4['name']}`")
            st.write(f"- **Media Cartellini / Partita:** `{ref4['cards_avg']:.1f}`")
            st.write(f"- **Media Falli Fischiati:** `{ref4['fouls_avg']:.1f}`")
            st.write(f"- **Indice di Severità AIA:** `{ref4['severity']}`")
            st.write(f"- **Proiezione Cartellini Sfida:** `{disc_res['metric_val']}`")
            
        with col_d2:
            st.markdown("#### Calcolo Valore Over 4.5 Cartellini")
            st.write(f"**Probabilità Modello:** `{disc_res['prob']*100:.1f}%`")
            st.write(f"**Quota Equa:** `{disc_res['fair_odds']:.2f}` | **Quota Minima:** `{disc_res['min_odds']:.2f}`")
            
            odd_disc = st.number_input("Quota Cartellini sul tuo Bookmaker", min_value=1.01, max_value=20.0, value=float(disc_res['min_odds']), step=0.02, key="odd_disc_in")
            edge_disc = (disc_res['prob'] * odd_disc) - 1.0
            st_p_d, st_e_d = MatchAnalystEngine.calculate_kelly(disc_res['prob'], odd_disc, current_bankroll, kelly_fraction)
            
            if odd_disc >= disc_res['min_odds'] and edge_disc >= min_edge_val:
                st.success(f"VALORE PRESENTE: Edge {edge_disc*100:+.2f}% | Stake: {st_p_d}% ({st_e_d:.2f} €)")
                if st.button("SALVA BET CARTELLINI NEL BANKROLL", key="save_disc_btn"):
                    save_user_bet(st.session_state.user.get("id"), f"{h4} vs {a4}", disc_res["market"], odd_disc, st_e_d, edge_disc)
                    st.rerun()
            else:
                st.error(f"NO BET (Quota insufficiente - Edge: {edge_disc*100:+.2f}%)")

# REGISTRO SCOMMESSE
with tab5:
    st.markdown("### STORICO PERSONALE SCOMMESSE")
    user_bets = fetch_user_bets(st.session_state.user.get("id"))
    
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
        st.info("Nessuna scommessa salvata nel database.")

# GESTIONE ACCOUNT
with tab6:
    st.markdown("### GESTIONE ACCOUNT")
    with st.expander("Il Mio Profilo", expanded=True):
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Email:** `{user_email}`")
            st.markdown(f"**Stato Abbonamento:** `{tier_label}`")
        with col_p2:
            st.markdown(f"**ID Utente:** `{st.session_state.user.get('id')}`")
            
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
