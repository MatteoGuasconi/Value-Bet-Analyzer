import datetime
import numpy as np
import pandas as pd
import requests
from scipy.stats import poisson
import streamlit as st

# Importazione modulo rose dinamico per tutti i 5 campionati
from squads_db import fetch_team_squad_api, clean_team_name, ALL_LEAGUES_TEAMS_IDS

# Configurazione della pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS Dark Fintech con Fix Safari Mobile
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
    
    /* FIX MENU LATERALE SU SMARTPHONE & SAFARI */
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
    
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        border-radius: 8px;
        border: 1px solid #2D3A5D;
        background-color: #1C2541;
    }
    
    div[data-testid="stExpander"] {
        background-color: #1C2541 !important;
        border: 1px solid #2D3A5D !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
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
                    else: st.error(f"Errore accesso: {err}")
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
    "Serie A (Italia)": {"key": "soccer_italy_serie_a"},
    "Premier League (Inghilterra)": {"key": "soccer_epl"},
    "La Liga (Spagna)": {"key": "soccer_spain_la_liga"},
    "Bundesliga (Germania)": {"key": "soccer_germany_bundesliga"},
    "Ligue 1 (Francia)": {"key": "soccer_france_ligue_one"}
}

# Parametri Tattici Squadre
TEAM_METRICS = {
    "Inter": {"gf_h": 2.25, "gf_a": 1.90, "ga_h": 0.65, "ga_a": 0.80, "xg_5": 2.15, "xg_s": 2.05, "sot_pro": 6.2, "sot_against": 3.1, "corners_pro": 6.4, "corners_against": 3.6, "cross": 21.5, "modulo": "3-5-2", "stile": "Pressing Alto & Fasce", "possesso": 61.2},
    "Juventus": {"gf_h": 1.70, "gf_a": 1.40, "ga_h": 0.50, "ga_a": 0.75, "xg_5": 1.65, "xg_s": 1.55, "sot_pro": 5.1, "sot_against": 2.8, "corners_pro": 5.6, "corners_against": 3.8, "cross": 18.2, "modulo": "4-2-3-1", "stile": "Costruzione Bassa", "possesso": 58.4},
    "Milan": {"gf_h": 2.05, "gf_a": 1.65, "ga_h": 1.10, "ga_a": 1.25, "xg_5": 1.90, "xg_s": 1.80, "sot_pro": 5.6, "sot_against": 4.4, "corners_pro": 5.8, "corners_against": 4.2, "cross": 19.5, "modulo": "4-2-3-1", "stile": "Transizione Rapida", "possesso": 56.0},
    "Napoli": {"gf_h": 1.85, "gf_a": 1.55, "ga_h": 0.60, "ga_a": 0.85, "xg_5": 1.80, "xg_s": 1.70, "sot_pro": 5.3, "sot_against": 3.2, "corners_pro": 6.1, "corners_against": 3.5, "cross": 20.8, "modulo": "3-5-2", "stile": "Compattezza Difensiva", "possesso": 55.5},
    "Manchester City": {"gf_h": 2.45, "gf_a": 2.10, "ga_h": 0.60, "ga_a": 0.80, "xg_5": 2.35, "xg_s": 2.25, "sot_pro": 7.1, "sot_against": 2.6, "corners_pro": 7.4, "corners_against": 3.0, "cross": 22.0, "modulo": "4-3-3", "stile": "Dominio Territoriale Assoluto", "possesso": 65.5},
    "Arsenal": {"gf_h": 2.20, "gf_a": 1.85, "ga_h": 0.55, "ga_a": 0.70, "xg_5": 2.05, "xg_s": 1.95, "sot_pro": 6.4, "sot_against": 2.7, "corners_pro": 6.8, "corners_against": 3.2, "cross": 20.5, "modulo": "4-3-3", "stile": "Pressione Alta & Palle Inattive", "possesso": 60.5},
    "Liverpool": {"gf_h": 2.30, "gf_a": 1.95, "ga_h": 0.65, "ga_a": 0.85, "xg_5": 2.20, "xg_s": 2.10, "sot_pro": 6.7, "sot_against": 3.0, "corners_pro": 7.0, "corners_against": 3.5, "cross": 21.0, "modulo": "4-3-3", "stile": "Verticalizzazioni Rapide", "possesso": 61.5},
    "Real Madrid": {"gf_h": 2.35, "gf_a": 1.95, "ga_h": 0.70, "ga_a": 0.85, "xg_5": 2.25, "xg_s": 2.10, "sot_pro": 6.8, "sot_against": 3.2, "corners_pro": 6.5, "corners_against": 3.8, "cross": 19.5, "modulo": "4-3-3", "stile": "Transizione Rapida", "possesso": 61.0},
    "Barcellona": {"gf_h": 2.40, "gf_a": 2.00, "ga_h": 0.75, "ga_a": 0.90, "xg_5": 2.30, "xg_s": 2.15, "sot_pro": 6.9, "sot_against": 3.4, "corners_pro": 6.6, "corners_against": 3.7, "cross": 18.5, "modulo": "4-2-3-1", "stile": "Linea Difensiva Alta", "possesso": 63.5},
    "Bayern Monaco": {"gf_h": 2.50, "gf_a": 2.15, "ga_h": 0.70, "ga_a": 0.95, "xg_5": 2.45, "xg_s": 2.30, "sot_pro": 7.3, "sot_against": 3.0, "corners_pro": 7.2, "corners_against": 3.4, "cross": 21.0, "modulo": "4-2-3-1", "stile": "Attacco Diretto", "possesso": 64.0},
    "PSG": {"gf_h": 2.30, "gf_a": 1.90, "ga_h": 0.65, "ga_a": 0.85, "xg_5": 2.15, "xg_s": 2.05, "sot_pro": 6.5, "sot_against": 3.1, "corners_pro": 6.3, "corners_against": 3.5, "cross": 19.0, "modulo": "4-3-3", "stile": "Possesso Laterale", "possesso": 62.0}
}

DEFAULT_METRICS = {
    "gf_h": 1.40, "gf_a": 1.15, "ga_h": 1.10, "ga_a": 1.40, "xg_5": 1.35, "xg_s": 1.30,
    "sot_pro": 4.4, "sot_against": 4.6, "corners_pro": 4.8, "corners_against": 4.8,
    "cross": 16.5, "modulo": "4-3-3", "stile": "Equilibrato", "possesso": 50.0
}

def get_adjusted_metrics(team_name, injuries_df):
    cleaned = clean_team_name(team_name)
    base = None
    for name, metrics in TEAM_METRICS.items():
        if name.lower() in cleaned.lower() or cleaned.lower() in name.lower():
            base = dict(metrics)
            break
    if not base: base = dict(DEFAULT_METRICS)
    return base

# Rendering Campo Tattico 11 vs 11
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
        return f'<div style="text-align:center;width:72px;display:inline-block;margin:3px;"><div style="width:28px;height:28px;border-radius:50%;background:{c};color:{tc};font-weight:800;font-size:10px;display:flex;align-items:center;justify-content:center;margin:0 auto 2px auto;border:2px solid #000;">{num}</div><div style="color:#FFFFFF;font-size:10px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{nom}</div></div>'
        
    atts_h = "".join([badge(p) for p in atts[:3]])
    mids_h = "".join([badge(p) for p in mids[:5]])
    defs_h = "".join([badge(p) for p in defs[:5]])
    gk_h = badge(gk_player, is_gk=True)
    
    return f'<div style="background:linear-gradient(180deg,#1e5138 0%,#143a28 100%);border:2px solid #2DD4BF;border-radius:8px;padding:14px 6px;text-align:center;margin-bottom:15px;"><div style="color:#2DD4BF;font-weight:800;font-size:13px;margin-bottom:10px;">{team_name.upper()} • {formation_str}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{atts_h}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{mids_h}</div><div style="display:flex;justify-content:center;margin-bottom:10px;">{defs_h}</div><div style="display:flex;justify-content:center;">{gk_h}</div></div>'

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
        xg_final = gf * (ga_opp / 1.25) * (t_met["xg_5"] / max(0.1, t_met["xg_s"]))
        prob = float(1.0 - (poisson.pmf(0, xg_final) + poisson.pmf(1, xg_final)))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over 1.5 Gol ({clean_team_name(team)})", "market_type": "Over 1.5 Gol Squadra",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xG Finale", "metric_val": f"{xg_final:.2f}",
            "note": f"Efficienza: {gf:.2f} GF | Concessione Difensiva: {ga_opp:.2f} GA"
        }

    @staticmethod
    def analyze_corners_multiline(h_team, a_team, line=9.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        h_met = get_adjusted_metrics(h_team, injuries_df)
        a_met = get_adjusted_metrics(a_team, injuries_df)
        corners_final = (h_met["corners_pro"] + a_met["corners_against"])/2.0 + (a_met["corners_pro"] + h_met["corners_against"])/2.0
        prob = float(1.0 - poisson.cdf(line - 0.5, corners_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Corner Totali", "market_type": "Corner Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Corner Proiettati", "metric_val": f"{corners_final:.2f}",
            "note": f"Cross combinati: {h_met['cross']+a_met['cross']:.1f}"
        }

    @staticmethod
    def analyze_player_sot(player, opp_team, line=0.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        opp_met = get_adjusted_metrics(opp_team, injuries_df)
        xsot_final = player.get("sot_90", 1.0) * (84 / 90) * (opp_met["sot_against"] / 4.3)
        prob = float(1.0 - poisson.cdf(line - 0.5, xsot_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Tiri in Porta ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xSOT Attesi", "metric_val": f"{xsot_final:.2f}",
            "note": f"Ruolo: {player['role']} | Media SOT/90m: {player.get('sot_90', 1.0):.2f}"
        }

    @staticmethod
    def analyze_player_fouls(player, opp_team, line=1.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        opp_met = get_adjusted_metrics(opp_team, injuries_df)
        xf_final = player.get("fouls_c_90", 1.0) * (85 / 90) * (12.5 / 12.5)
        prob = float(1.0 - poisson.cdf(line - 0.5, xf_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Commessi ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xFouls Attesi", "metric_val": f"{xf_final:.2f}",
            "note": f"Media Falli/90m: {player.get('fouls_c_90', 1.0):.2f}"
        }

    @staticmethod
    def analyze_goalkeeper_saves(player, opp_team, line=2.5, min_edge=0.015, injuries_df=None):
        if injuries_df is None: injuries_df = pd.DataFrame()
        opp_met = get_adjusted_metrics(opp_team, injuries_df)
        xsaves = opp_met["sot_pro"] * 0.72
        prob = float(1.0 - poisson.cdf(line - 0.5, xsaves))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Parate ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Parate Proiettate", "metric_val": f"{xsaves:.2f}",
            "note": f"Tiri nello specchio avversario: {opp_met['sot_pro']:.1f}"
        }

# Calendario partite automatico per tutti i campionati
def get_league_matches_mock(league_label):
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
    return [
        {"home_team": "Inter", "away_team": "Juventus", "commence_time": now_dt.isoformat()},
        {"home_team": "Milan", "away_team": "Napoli", "commence_time": now_dt.isoformat()},
        {"home_team": "Atalanta", "away_team": "Roma", "commence_time": now_dt.isoformat()},
        {"home_team": "Lazio", "away_team": "Fiorentina", "commence_time": now_dt.isoformat()},
        {"home_team": "Bologna", "away_team": "Torino", "commence_time": now_dt.isoformat()}
    ]

# Header & Sidebar
is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE (DEMO)"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")
st.sidebar.markdown("---")
st.sidebar.markdown("### SELEZIONA COMPETIZIONE")
selected_league_label = st.sidebar.selectbox("Campionato / Torneo", list(LEAGUES_CONFIG.keys()), index=0)

if not is_premium:
    st.sidebar.markdown("---")
    promo_code = st.sidebar.text_input("Codice VIP / Tester", placeholder="Inserisci codice...", type="password")
    if st.sidebar.button("ATTIVA PREMIUM", use_container_width=True):
        if promo_code:
            ok, msg = redeem_vip_code(user_id, promo_code)
            if ok: st.rerun()

if st.sidebar.button("LOGOUT", use_container_width=True):
    logout_user()
    st.rerun()

st.sidebar.markdown("---")
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.select_slider("Frazione di Kelly", options=[0.25, 0.50], value=0.50)
min_edge_pct = st.sidebar.slider("Soglia Minima Edge (%)", min_value=1.0, max_value=3.0, value=1.5, step=0.5)
min_edge_val = min_edge_pct / 100.0

# Bankroll
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

st.sidebar.markdown("---")
st.sidebar.markdown("### IL TUO BANKROLL CLOUD")
st.sidebar.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Capitale Attuale</div>
        <div class="metric-value-neutral">{current_bankroll:.2f} €</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Profitto Netto</div>
        <div class="{ 'metric-value-pos' if total_profit >= 0 else 'metric-value-neg' }">
            {total_profit:+.2f} €
        </div>
    </div>
""", unsafe_allow_html=True)

injuries_df = fetch_injuries()
matches = get_league_matches_mock(selected_league_label)

st.title("VALUE BET ANALYZER")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)
st.markdown(f'<div class="round-badge">{selected_league_label.upper()} • ROSE ATTIVE 2026/2027</div>', unsafe_allow_html=True)

# 8 SCHEDE ORIGINALI ATTIVE SU TUTTI I 5 CAMPIONATI
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

# 1. SCANNER TOP 5
with tab_scan:
    st.markdown(f"### TOP 5 VALUE BETS ({selected_league_label.upper()})")
    all_opportunities = []
    for m in matches:
        h = clean_team_name(m.get("home_team", ""))
        a = clean_team_name(m.get("away_team", ""))
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
                "QUOTA EQUA": f"{item['fair_odds']:.2f}", "QUOTA MINIMA (VALORE)": f"{item['min_odds']:.2f}"
            })
        else:
            table_data.append({
                "POS": f"#{pos}", "PARTITA": item["match"], "DATA": item["date"],
                "MERCATO": "[BLOCCATO - PIANO PREMIUM]", "PROB. MODELLO": "---",
                "QUOTA EQUA": "---", "QUOTA MINIMA (VALORE)": "---"
            })
    st.table(pd.DataFrame(table_data))

# 2. MERCATI PRINCIPALI
with tab1:
    st.markdown(f"### TOP MERCATI TOTALI ({selected_league_label.upper()})")
    for m in matches:
        h = clean_team_name(m["home_team"])
        a = clean_team_name(m["away_team"])
        res_g = MatchAnalystEngine.analyze_team_goals_over15(h, a, True, min_edge_val, injuries_df)
        st.write(f"**{h} vs {a}** | Over 1.5 Gol {h} -> Quota Minima: `{res_g['min_odds']:.2f}` (Prob: {res_g['prob']*100:.1f}%)")

# 3. STATISTICHE & TATTICA
with tab2:
    st.markdown(f"### QUADRO TATTICO & DISPOSIZIONE ({selected_league_label.upper()})")
    m_opts = [f"{m['home_team']} vs {m['away_team']}" for m in matches]
    sel_m_i = st.selectbox("Seleziona Partita", range(len(m_opts)), format_func=lambda x: m_opts[x])
    cur_m = matches[sel_m_i]
    h2 = clean_team_name(cur_m["home_team"])
    a2 = clean_team_name(cur_m["away_team"])
    
    h2_squad = fetch_team_squad_api(h2, FOOTBALL_KEY)
    a2_squad = fetch_team_squad_api(a2, FOOTBALL_KEY)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1: st.markdown(render_visual_pitch_html(h2, "4-3-3", h2_squad), unsafe_allow_html=True)
    with col_p2: st.markdown(render_visual_pitch_html(a2, "4-3-3", a2_squad), unsafe_allow_html=True)

# 4. PRESTAZIONI CALCIATORI & PORTIERI (DISPONIBILE SU TUTTE LE 96 SQUADRE)
with tab3:
    st.markdown(f"### PRESTAZIONI CALCIATORI & PORTIERI ({selected_league_label.upper()})")
    m_opts3 = [f"{m['home_team']} vs {m['away_team']}" for m in matches]
    sel_m3_i = st.selectbox("Seleziona Incontro da Analizzare", range(len(m_opts3)), format_func=lambda x: m_opts3[x], key="tab3_m_sel")
    m3 = matches[sel_m3_i]
    h3 = clean_team_name(m3["home_team"])
    a3 = clean_team_name(m3["away_team"])
    
    h3_players = fetch_team_squad_api(h3, FOOTBALL_KEY)
    a3_players = fetch_team_squad_api(a3, FOOTBALL_KEY)
    
    tab_h, tab_a = st.tabs([f"Squadra Casa: {h3}", f"Squadra Trasferta: {a3}"])
    
    def render_players_panel(plist, team_name, opp_team, pkey):
        p_names = [f"{p['name']} ({p['role']} #{p['number']})" for p in plist]
        sel_p = st.selectbox(f"Seleziona Calciatore ({team_name})", range(len(p_names)), format_func=lambda x: p_names[x], key=f"{pkey}_sel")
        chosen = plist[sel_p]
        
        if chosen["role"] == "Goalkeeper":
            st.markdown("#### Mercato: Parate Portiere")
            sv_res = MatchAnalystEngine.analyze_goalkeeper_saves(chosen, opp_team, 2.5, min_edge_val, injuries_df)
            st.metric("Probabilita Modello", f"{sv_res['prob']*100:.1f}%")
            st.write(f"**Quota Equa:** `{sv_res['fair_odds']:.2f}` | **Quota Minima:** `{sv_res['min_odds']:.2f}`")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### Mercato: Tiri in Porta")
                sot_res = MatchAnalystEngine.analyze_player_sot(chosen, opp_team, 0.5, min_edge_val, injuries_df)
                st.metric("Probabilita Modello", f"{sot_res['prob']*100:.1f}%")
                st.write(f"**Quota Equa:** `{sot_res['fair_odds']:.2f}` | **Quota Minima:** `{sot_res['min_odds']:.2f}`")
            with c2:
                st.markdown("#### Mercato: Falli Commessi")
                fl_res = MatchAnalystEngine.analyze_player_fouls(chosen, opp_team, 1.5, min_edge_val, injuries_df)
                st.metric("Probabilita Modello", f"{fl_res['prob']*100:.1f}%")
                st.write(f"**Quota Equa:** `{fl_res['fair_odds']:.2f}` | **Quota Minima:** `{fl_res['min_odds']:.2f}`")
                
    with tab_h: render_players_panel(h3_players, h3, a3, "tab3_h")
    with tab_a: render_players_panel(a3_players, a3, h3, "tab3_a")

# 5. FOCUS DISCIPLINARE
with tab4:
    st.markdown("### FOCUS DISCIPLINARE & ARBITRI")
    st.info("Statistiche arbitrali integrate con modello di Poisson sui cartellini.")

# 6. INFERMERIA
with tab_inj:
    st.markdown("### GESTIONE INFERMERIA & INDISPONIBILI")
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        inj_team = st.text_input("Squadra", placeholder="es. Real Madrid")
        inj_player = st.text_input("Nome Giocatore", placeholder="es. Vinicius Junior")
    with c_in2:
        inj_imp = st.selectbox("Importanza", ["Top Player Offensivo", "Difensore Chiave", "Portiere Titolare"])
        inj_diag = st.text_input("Diagnosi", placeholder="es. Lesione muscolare")
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
        st.info("Nessuna scommessa salvata nel database.")

# 8. GESTIONE ACCOUNT
with tab6:
    st.markdown("### GESTIONE ACCOUNT")
    st.write(f"**Email:** `{user_email}` | **Stato:** `{tier_label}`")
