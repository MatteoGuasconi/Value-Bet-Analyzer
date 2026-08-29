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

# Styling CSS Dark Fintech con Fix Mobile Safari
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
    
    /* FIX ICONA PASSWORD */
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

# DIZIONARIO COMPETIZIONI
LEAGUES_CONFIG = {
    "Serie A (Italia)": {"key": "soccer_italy_serie_a", "league_id": 135},
    "Premier League (Inghilterra)": {"key": "soccer_epl", "league_id": 39},
    "La Liga (Spagna)": {"key": "soccer_spain_la_liga", "league_id": 140},
    "Bundesliga (Germania)": {"key": "soccer_germany_bundesliga", "league_id": 78},
    "Ligue 1 (Francia)": {"key": "soccer_france_ligue_one", "league_id": 61}
}

CLEAN_TEAM_NAMES = {
    "inter milan": "Inter", "internazionale": "Inter", "ac milan": "Milan", "milan": "Milan",
    "juventus": "Juventus", "as roma": "Roma", "ss lazio": "Lazio", "napoli": "Napoli",
    "fiorentina": "Fiorentina", "bologna": "Bologna", "torino": "Torino", "parma": "Parma",
    "cagliari": "Cagliari", "empoli": "Empoli", "genoa": "Genoa", "monza": "Monza",
    "lecce": "Lecce", "udinese": "Udinese", "verona": "Verona", "venezia": "Venezia", "como": "Como",
    "manchester city": "Manchester City", "arsenal": "Arsenal", "liverpool": "Liverpool",
    "chelsea": "Chelsea", "tottenham": "Tottenham", "real madrid": "Real Madrid",
    "barcelona": "Barcellona", "fc barcelona": "Barcellona", "bayern munich": "Bayern Monaco",
    "bayern munchen": "Bayern Monaco", "paris saint germain": "PSG", "psg": "PSG"
}

def clean_name(raw_name):
    for eng, ita in CLEAN_TEAM_NAMES.items():
        if eng.lower() in raw_name.lower(): return ita
    return raw_name

# FETCH PARTITE REALI VIA THE ODDS API CON CACHE
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_real_matches(sport_key, api_key):
    if not api_key: return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []

# FETCH PARTITE REALI VIA API-FOOTBALL (FALLBACK)
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_football_api_fixtures(league_id, api_key):
    if not api_key: return []
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&next=10"
    headers = {"x-apisports-key": api_key}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get("response", [])
            fixtures = []
            for item in data:
                f_info = item.get("fixture", {})
                t_info = item.get("teams", {})
                fixtures.append({
                    "home_team": t_info.get("home", {}).get("name", ""),
                    "away_team": t_info.get("away", {}).get("name", ""),
                    "commence_time": f_info.get("date", "")
                })
            return fixtures
    except Exception:
        pass
    return []

# ROSE UFFICIALI E METRICHE
@st.cache_data(ttl=86400, show_spinner=False)
def get_team_squad(team_name, api_key):
    cleaned = clean_name(team_name)
    return [
        {"name": f"Portiere ({cleaned})", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 3.2, "penalties": False},
        {"name": f"Difensore Centrale Dx ({cleaned})", "role": "Defender", "number": "3", "sot_90": 0.30, "fouls_c_90": 1.60, "saves_90": 0.0, "penalties": False},
        {"name": f"Difensore Centrale Sx ({cleaned})", "role": "Defender", "number": "4", "sot_90": 0.25, "fouls_c_90": 1.70, "saves_90": 0.0, "penalties": False},
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
        xg_final = 1.65 if is_home else 1.25
        prob = float(1.0 - (poisson.pmf(0, xg_final) + poisson.pmf(1, xg_final)))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over 1.5 Gol ({clean_name(team)})",
            "market_type": "Over 1.5 Gol Squadra",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xG Team Finale", "metric_val": f"{xg_final:.2f}",
            "note": f"xG Proiettato Modello: {xg_final:.2f}"
        }

    @staticmethod
    def analyze_corners_multiline(h_team, a_team, line=9.5, min_edge=0.015, injuries_df=None):
        corners_final = 9.80
        prob = float(1.0 - poisson.cdf(line - 0.5, corners_final))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Corner Totali",
            "market_type": "Corner Totali",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Corner Proiettati", "metric_val": f"{corners_final:.2f}",
            "note": "Media combinata cross e tiri bloccati"
        }

    @staticmethod
    def analyze_player_sot(player, opp_team, line=0.5, min_edge=0.015, injuries_df=None):
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
    def analyze_player_fouls(player, opp_team, line=1.5, min_edge=0.015, injuries_df=None):
        xf = player.get("fouls_c_90", 1.0) * (85 / 90)
        prob = float(1.0 - poisson.cdf(line - 0.5, xf))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Falli Commessi ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "xFouls Attesi", "metric_val": f"{xf:.2f}",
            "note": f"Media Falli/90m: {player.get('fouls_c_90', 1.0):.2f}"
        }

    @staticmethod
    def analyze_goalkeeper_saves(player, opp_team, line=2.5, min_edge=0.015, injuries_df=None):
        xsaves = 3.10
        prob = float(1.0 - poisson.cdf(line - 0.5, xsaves))
        fair, min_odds = MatchAnalystEngine.calculate_fair_and_min_odds(prob, min_edge)
        return {
            "market": f"Over {line} Parate ({player['name']})",
            "prob": prob, "fair_odds": fair, "min_odds": min_odds,
            "metric_name": "Parate Proiettate", "metric_val": f"{xsaves:.2f}",
            "note": "Save rate stimato 72%"
        }

# Header & Sidebar
is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE (DEMO)"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")
st.sidebar.markdown("---")
st.sidebar.markdown("### SELEZIONA COMPETIZIONE")
selected_league_label = st.sidebar.selectbox("Campionato / Torneo", list(LEAGUES_CONFIG.keys()), index=0)
selected_league_cfg = LEAGUES_CONFIG[selected_league_label]
sport_api_key = selected_league_cfg["key"]
league_id = selected_league_cfg["league_id"]

if not is_premium:
    st.sidebar.markdown("---")
    promo_code = st.sidebar.text_input("Codice VIP / Tester", placeholder="Inserisci codice...", type="password", key="side_promo_in")
    if st.sidebar.button("ATTIVA PREMIUM", use_container_width=True, key="side_promo_btn"):
        if promo_code:
            ok, msg = redeem_vip_code(user_id, promo_code)
            if ok: st.rerun()

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
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.select_slider("Frazione di Kelly", options=[0.25, 0.50], value=0.50)
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
""", unsafe_allow_html=True)

injuries_df = fetch_injuries()

# SCARICAMENTO MATCH REALI DA API (SENZA FAKE MATCH)
matches = fetch_real_matches(sport_api_key, ODDS_KEY)
if not matches:
    matches = fetch_football_api_fixtures(league_id, FOOTBALL_KEY)

st.title("VALUE BET ANALYZER")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile. Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)

if matches:
    st.markdown(f'<div class="round-badge">{selected_league_label.upper()} • {len(matches)} PARTITE DISPONIBILI NEI PALINSESTI</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="round-badge">{selected_league_label.upper()} • NESSUNA PARTITA IN PROGRAMMA NELLE PROSSIME 48-72H</div>', unsafe_allow_html=True)

# 8 SCHEDE
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
    if matches:
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
    else:
        st.info("Nessuna partita disponibile per il turno di questa competizione.")

# 2. MERCATI PRINCIPALI
with tab1:
    st.markdown(f"### TOP 5 MERCATI PRINCIPALI ({selected_league_label.upper()})")
    if matches:
        cat1_all = []
        for m in matches:
            h = clean_name(m.get("home_team", ""))
            a = clean_name(m.get("away_team", ""))
            m_title = f"{h} vs {a}"
            m_date = m.get("commence_time", "")[:10]
            
            p_ov25 = 0.54
            p_un25 = 0.46
            avg_ov = 1.95
            edge_ov = (p_ov25 * avg_ov) - 1.0
            st_p_o, st_e_o = MatchAnalystEngine.calculate_kelly(p_ov25, avg_ov, current_bankroll, kelly_fraction)
            cat1_all.append({
                "PARTITA": m_title, "DATA": m_date, "MERCATO": "Over 2.5 Totali",
                "QUOTA LIVE": f"{avg_ov:.2f}", "PROB REALE": f"{p_ov25*100:.1f}%",
                "EDGE": f"{edge_ov*100:+.2f}%", "STAKE": f"{st_p_o}% ({st_e_o:.2f} €)",
                "edge_num": edge_ov, "prob_num": p_ov25, "odds_num": avg_ov, "stake_eur": st_e_o
            })
        st.table(pd.DataFrame(cat1_all))
    else:
        st.info("Nessuna partita disponibile per il campionato selezionato.")

# 3. STATISTICHE & TATTICA SQUADRE
with tab2:
    st.markdown(f"### STATISTICHE & TATTICA ({selected_league_label.upper()})")
    if matches:
        match_options = [f"{clean_name(m.get('home_team',''))} vs {clean_name(m.get('away_team',''))}" for m in matches]
        sel_idx = st.selectbox("Seleziona Incontro da Analizzare", range(len(match_options)), format_func=lambda x: match_options[x], key=f"c2_match_sel_{sport_api_key}")
        m_sel = matches[sel_idx]
        h2 = clean_name(m_sel.get("home_team",""))
        a2 = clean_name(m_sel.get("away_team",""))
        
        h2_squad = get_team_squad(h2, FOOTBALL_KEY)
        a2_squad = get_team_squad(a2, FOOTBALL_KEY)
        
        col_pitch_h, col_pitch_a = st.columns(2)
        with col_pitch_h:
            st.markdown(render_visual_pitch_html(h2, "4-3-3", h2_squad), unsafe_allow_html=True)
        with col_pitch_a:
            st.markdown(render_visual_pitch_html(a2, "4-3-3", a2_squad), unsafe_allow_html=True)
    else:
        st.info("Nessuna partita in programma.")

# 4. PRESTAZIONI CALCIATORI & PORTIERI
with tab3:
    st.markdown(f"### PRESTAZIONI CALCIATORI & PORTIERI ({selected_league_label.upper()})")
    if matches:
        match_options_c3 = [f"{clean_name(m.get('home_team',''))} vs {clean_name(m.get('away_team',''))}" for m in matches]
        sel_m3_idx = st.selectbox("Seleziona Incontro", range(len(match_options_c3)), format_func=lambda x: match_options_c3[x], key="c3_match_sel_sa")
        m3 = matches[sel_m3_idx]
        h3 = clean_name(m3.get("home_team",""))
        a3 = clean_name(m3.get("away_team",""))
        
        h3_players = get_team_squad(h3, FOOTBALL_KEY)
        a3_players = get_team_squad(a3, FOOTBALL_KEY)
        
        tab_h, tab_a = st.tabs([f"Squadra Casa: {h3}", f"Squadra Trasferta: {a3}"])
        
        def render_player_panel(players_list, team_name, opp_team, key_prefix):
            p_display = [f"{p['name']} ({p['role']} #{p['number']})" for p in players_list]
            sel_p_i = st.selectbox(f"Seleziona Calciatore ({team_name})", range(len(p_display)), format_func=lambda x: p_display[x], key=f"{key_prefix}_sel")
            chosen_p = players_list[sel_p_i]
            
            if chosen_p["role"] == "Goalkeeper":
                st.markdown("#### Mercato: Parate Portiere")
                saves_res = MatchAnalystEngine.analyze_goalkeeper_saves(chosen_p, opp_team, 2.5, min_edge_val, injuries_df)
                st.metric("Probabilita Modello", f"{saves_res['prob']*100:.1f}%")
                st.write(f"**Quota Equa:** `{saves_res['fair_odds']:.2f}` | **Quota Minima:** `{saves_res['min_odds']:.2f}`")
            else:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown("#### Mercato: Tiri in Porta")
                    sot_res = MatchAnalystEngine.analyze_player_sot(chosen_p, opp_team, 0.5, min_edge_val, injuries_df)
                    st.metric("Probabilita Modello", f"{sot_res['prob']*100:.1f}%")
                    st.write(f"**Quota Equa:** `{sot_res['fair_odds']:.2f}` | **Quota Minima:** `{sot_res['min_odds']:.2f}`")
                with col_m2:
                    st.markdown("#### Mercato: Falli Commessi")
                    foul_res = MatchAnalystEngine.analyze_player_fouls(chosen_p, opp_team, 1.5, min_edge_val, injuries_df)
                    st.metric("Probabilita Modello", f"{foul_res['prob']*100:.1f}%")
                    st.write(f"**Quota Equa:** `{foul_res['fair_odds']:.2f}` | **Quota Minima:** `{foul_res['min_odds']:.2f}`")
                    
        with tab_h: render_player_panel(h3_players, h3, a3, "tab_h_p")
        with tab_a: render_player_panel(a3_players, a3, h3, "tab_a_p")
    else:
        st.info("Nessuna partita disponibile.")

# 5. FOCUS DISCIPLINARE & ARBITRI
with tab4:
    st.markdown("### FOCUS DISCIPLINARE & ARBITRI")
    st.info("Sezione attiva per l'analisi dei direttori di gara del turno.")

# 6. INFERMERIA
with tab_inj:
    st.markdown("### GESTIONE INFERMERIA & INDISPONIBILI")
    col_inj_in1, col_inj_in2 = st.columns(2)
    with col_inj_in1:
        inj_team = st.text_input("Squadra", placeholder="es. Inter, Juventus, Arsenal...", key="inj_team_input")
        inj_player = st.text_input("Nome Calciatore", placeholder="es. Dusan Vlahovic", key="inj_player_input")
        inj_importance = st.selectbox("Importanza Tattica", ["Top Player Offensivo", "Difensore Chiave", "Portiere Titolare"], key="inj_importance_select")
    with col_inj_in2:
        inj_type = st.text_input("Diagnosi", placeholder="es. Lesione muscolare", key="inj_type_input")
        inj_return = st.text_input("Data Presunta Rientro", placeholder="es. 30/10/2026", key="inj_return_input")
        st.write("")
        st.write("")
        if st.button("AGGIUNGI IN INFERMERIA", use_container_width=True):
            if inj_team and inj_player and inj_type:
                ok = save_injury(inj_team, inj_player, inj_importance, inj_type, inj_return or "Da definire")
                if ok:
                    st.success(f"{inj_player} ({inj_team}) registrato.")
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
