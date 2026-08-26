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

# Styling CSS Dark Fintech - Palette A3: Frost Indigo
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
    
    /* Nasconde toolbar e footer */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Protezione icone native */
    [data-testid="stIconMaterial"], [class*="material-symbols"], i {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    
    /* Header superiore */
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
    
    /* Card Metriche Bankroll */
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
    
    .round-badge {
        background-color: #1C2541;
        border: 1px solid #2D3A5D;
        color: #8597AC;
        font-size: 0.85rem;
        font-weight: 600;
        padding: 8px 14px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .props-notice-badge {
        background-color: rgba(94, 111, 146, 0.15);
        border: 1px solid #5E6F92;
        color: #8597AC;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 16px;
    }
    
    .trial-banner {
        background: linear-gradient(90deg, rgba(45, 212, 191, 0.15) 0%, rgba(28, 37, 65, 0.8) 100%);
        border: 1px solid #2DD4BF;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
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
    
    /* Styling Expander */
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

# Parametri Supabase dai Secrets
SB_URL = st.secrets.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = st.secrets.get("SUPABASE_KEY", "")

# Gestione Sessione Utente
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
    res = requests.post(
        url,
        json={"email": email, "password": password},
        headers=get_headers(),
        timeout=10,
    )
    if res.status_code == 200:
      data = res.json()
      st.session_state.user = data.get("user")
      st.session_state.access_token = data.get("access_token")

      u_id = data["user"]["id"]
      prof_url = f"{SB_URL}/rest/v1/profiles?id=eq.{u_id}&select=tier"
      prof_res = requests.get(
          prof_url, headers=get_headers(data.get("access_token")), timeout=10
      )
      if prof_res.status_code == 200 and prof_res.json():
        st.session_state.user_tier = prof_res.json()[0].get("tier", "free")
      return True, None
    err = (
        res.json().get("error_description")
        or res.json().get("msg")
        or "Credenziali non corrette."
    )
    return False, err
  except Exception as e:
    return False, str(e)


def register_user(email, password):
  if not SB_URL or not SB_KEY:
    return False, "Chiavi Supabase mancanti nei Secrets."
  url = f"{SB_URL}/auth/v1/signup"
  try:
    res = requests.post(
        url,
        json={"email": email, "password": password},
        headers=get_headers(),
        timeout=10,
    )
    if res.status_code in [200, 201]:
      return True, "Registrazione completata. Puoi accedere ora."
    err = (
        res.json().get("msg")
        or res.json().get("error_description")
        or "Errore di registrazione."
    )
    return False, err
  except Exception as e:
    return False, str(e)


def update_user_password(new_password):
  token = st.session_state.get("access_token")
  if not token:
    return False, "Sessione scaduta. Effettua nuovamente il login."
  url = f"{SB_URL}/auth/v1/user"
  try:
    res = requests.put(
        url,
        json={"password": new_password},
        headers=get_headers(token),
        timeout=10,
    )
    if res.status_code == 200:
      return True, "Password aggiornata con successo."
    err = (
        res.json().get("msg")
        or res.json().get("error_description")
        or "Errore aggiornamento password."
    )
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
        requests.patch(
            url, json={"tier": "premium"}, headers=hdrs, timeout=10
        )
      except Exception:
        pass
    st.session_state.user_tier = "premium"
    return True, "Codice valido. Piano Premium attivato."
  return False, "Codice promozionale non valido."


# Normalizzatore Nomi Squadre in Italiano
CLEAN_TEAM_NAMES = {
    "Inter Milan": "Inter",
    "AC Milan": "Milan",
    "Atalanta BC": "Atalanta",
    "AS Roma": "Roma",
    "SS Lazio": "Lazio",
    "Juventus": "Juventus",
    "Napoli": "Napoli",
    "Fiorentina": "Fiorentina",
    "Bologna": "Bologna",
    "Torino": "Torino",
    "Parma": "Parma",
    "Cagliari": "Cagliari",
    "Empoli": "Empoli",
    "Genoa": "Genoa",
    "Monza": "Monza",
    "Lecce": "Lecce",
    "Udinese": "Udinese",
    "Verona": "Verona",
    "Venezia": "Venezia",
    "Como": "Como",
    "Manchester City": "Manchester City",
    "Arsenal": "Arsenal",
    "Liverpool": "Liverpool",
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barcellona",
    "Bayern Munich": "Bayern Monaco",
    "Paris Saint Germain": "PSG",
    "PSG": "PSG",
}


def clean_name(raw_name):
  for eng, ita in CLEAN_TEAM_NAMES.items():
    if eng.lower() in raw_name.lower():
      return ita
  return raw_name


# Schermata Login / Registrazione
if st.session_state.user is None:
  st.title("VALUE BET ANALYZER")
  st.caption("Suite Qualitativa Professionale | L'A.I. Applicata Al Mondo Del Betting")

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
      reg_pwd = st.text_input(
          "Password (min. 6 caratteri)", type="password", key="reg_pwd"
      )
      if st.button("REGISTRATI", use_container_width=True):
        if reg_email and len(reg_pwd) >= 6:
          ok, msg = register_user(reg_email, reg_pwd)
          if ok:
            st.success(msg)
          else:
            st.error(f"Errore registrazione: {msg}")
        else:
          st.warning(
              "Inserisci un'email valida e una password di almeno 6 caratteri."
          )
  st.stop()


# Funzioni Database Cloud Scommesse
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
  return pd.DataFrame(
      columns=[
          "id",
          "created_at",
          "match",
          "market",
          "odds",
          "stake",
          "ev",
          "status",
          "profit",
      ]
  )


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
      requests.patch(
          url,
          json={"status": new_status, "profit": profit_val},
          headers=hdrs,
          timeout=10,
      )
    except Exception:
      pass


# DATABASE STATISTICO INTEGRATO
TEAM_METRICS = {
    # SERIE A
    "Inter": {
        "gf_h": 2.25,
        "gf_a": 1.90,
        "ga_h": 0.65,
        "ga_a": 0.80,
        "xg_5": 2.15,
        "xga_5": 0.75,
        "xg_s": 2.05,
        "over15_pct": 0.82,
        "sot_pro": 6.2,
        "sot_against": 3.1,
        "corners_pro": 6.4,
        "corners_against": 3.6,
        "cross": 21.5,
        "blocked_shots": 5.4,
        "fouls_pro": 11.2,
        "fouls_against": 12.8,
        "tactics": "3-5-2 Pressing Alto",
    },
    "Juventus": {
        "gf_h": 1.70,
        "gf_a": 1.40,
        "ga_h": 0.50,
        "ga_a": 0.75,
        "xg_5": 1.65,
        "xga_5": 0.70,
        "xg_s": 1.55,
        "over15_pct": 0.68,
        "sot_pro": 5.1,
        "sot_against": 2.8,
        "corners_pro": 5.6,
        "corners_against": 3.8,
        "cross": 18.2,
        "blocked_shots": 4.6,
        "fouls_pro": 12.1,
        "fouls_against": 13.5,
        "tactics": "4-2-3-1 Dominio Possesso",
    },
    "Milan": {
        "gf_h": 2.05,
        "gf_a": 1.65,
        "ga_h": 1.10,
        "ga_a": 1.25,
        "xg_5": 1.90,
        "xga_5": 1.20,
        "xg_s": 1.80,
        "over15_pct": 0.78,
        "sot_pro": 5.6,
        "sot_against": 4.4,
        "corners_pro": 5.8,
        "corners_against": 4.2,
        "cross": 19.5,
        "blocked_shots": 5.2,
        "fouls_pro": 11.8,
        "fouls_against": 12.0,
        "tactics": "4-2-3-1 Transizione Rapida",
    },
    "Napoli": {
        "gf_h": 1.85,
        "gf_a": 1.55,
        "ga_h": 0.60,
        "ga_a": 0.85,
        "xg_5": 1.80,
        "xga_5": 0.85,
        "xg_s": 1.70,
        "over15_pct": 0.72,
        "sot_pro": 5.3,
        "sot_against": 3.2,
        "corners_pro": 6.1,
        "corners_against": 3.5,
        "cross": 20.8,
        "blocked_shots": 5.1,
        "fouls_pro": 12.4,
        "fouls_against": 13.0,
        "tactics": "3-5-2 Compatto e Verticale",
    },
    "Atalanta": {
        "gf_h": 2.30,
        "gf_a": 1.80,
        "ga_h": 1.05,
        "ga_a": 1.20,
        "xg_5": 2.20,
        "xga_5": 1.15,
        "xg_s": 2.10,
        "over15_pct": 0.84,
        "sot_pro": 6.5,
        "sot_against": 4.1,
        "corners_pro": 6.7,
        "corners_against": 4.0,
        "cross": 22.4,
        "blocked_shots": 5.8,
        "fouls_pro": 13.8,
        "fouls_against": 14.2,
        "tactics": "3-4-2-1 Pressing Ultra-Offensivo",
    },
    "Roma": {
        "gf_h": 1.60,
        "gf_a": 1.20,
        "ga_h": 0.95,
        "ga_a": 1.15,
        "xg_5": 1.55,
        "xga_5": 1.05,
        "xg_s": 1.50,
        "over15_pct": 0.65,
        "sot_pro": 4.9,
        "sot_against": 3.8,
        "corners_pro": 5.4,
        "corners_against": 4.1,
        "cross": 17.5,
        "blocked_shots": 4.2,
        "fouls_pro": 13.0,
        "fouls_against": 12.5,
        "tactics": "3-4-2-1 Man-Oriented",
    },
    "Lazio": {
        "gf_h": 1.75,
        "gf_a": 1.35,
        "ga_h": 1.00,
        "ga_a": 1.25,
        "xg_5": 1.60,
        "xga_5": 1.10,
        "xg_s": 1.55,
        "over15_pct": 0.70,
        "sot_pro": 4.8,
        "sot_against": 4.0,
        "corners_pro": 5.3,
        "corners_against": 4.3,
        "cross": 18.0,
        "blocked_shots": 4.5,
        "fouls_pro": 13.2,
        "fouls_against": 12.2,
        "tactics": "4-2-3-1 Attacco Diretto",
    },
    "Fiorentina": {
        "gf_h": 1.70,
        "gf_a": 1.30,
        "ga_h": 0.90,
        "ga_a": 1.20,
        "xg_5": 1.55,
        "xga_5": 1.10,
        "xg_s": 1.45,
        "over15_pct": 0.67,
        "sot_pro": 4.7,
        "sot_against": 3.9,
        "corners_pro": 5.5,
        "corners_against": 4.2,
        "cross": 19.0,
        "blocked_shots": 4.8,
        "fouls_pro": 12.6,
        "fouls_against": 12.8,
        "tactics": "4-3-3 Possesso Laterale",
    },
    "Bologna": {
        "gf_h": 1.50,
        "gf_a": 1.15,
        "ga_h": 0.85,
        "ga_a": 1.10,
        "xg_5": 1.45,
        "xga_5": 0.95,
        "xg_s": 1.40,
        "over15_pct": 0.60,
        "sot_pro": 4.5,
        "sot_against": 3.5,
        "corners_pro": 5.2,
        "corners_against": 3.9,
        "cross": 17.8,
        "blocked_shots": 4.3,
        "fouls_pro": 12.5,
        "fouls_against": 12.0,
        "tactics": "4-2-3-1 Costruzione Bassa",
    },
    "Torino": {
        "gf_h": 1.25,
        "gf_a": 0.95,
        "ga_h": 0.90,
        "ga_a": 1.15,
        "xg_5": 1.20,
        "xga_5": 1.05,
        "xg_s": 1.15,
        "over15_pct": 0.52,
        "sot_pro": 3.9,
        "sot_against": 4.2,
        "corners_pro": 4.6,
        "corners_against": 4.5,
        "cross": 16.0,
        "blocked_shots": 3.9,
        "fouls_pro": 14.1,
        "fouls_against": 11.8,
        "tactics": "3-5-2 Duelli Fisici",
    },
    "Parma": {
        "gf_h": 1.35,
        "gf_a": 1.10,
        "ga_h": 1.45,
        "ga_a": 1.65,
        "xg_5": 1.30,
        "xga_5": 1.60,
        "xg_s": 1.25,
        "over15_pct": 0.55,
        "sot_pro": 4.2,
        "sot_against": 5.4,
        "corners_pro": 4.7,
        "corners_against": 5.8,
        "cross": 15.5,
        "blocked_shots": 3.7,
        "fouls_pro": 13.5,
        "fouls_against": 11.5,
        "tactics": "4-2-3-1 Contropiede Rapido",
    },
    "Cagliari": {
        "gf_h": 1.20,
        "gf_a": 0.90,
        "ga_h": 1.35,
        "ga_a": 1.60,
        "xg_5": 1.15,
        "xga_5": 1.50,
        "xg_s": 1.15,
        "over15_pct": 0.48,
        "sot_pro": 3.8,
        "sot_against": 5.2,
        "corners_pro": 4.5,
        "corners_against": 5.6,
        "cross": 16.5,
        "blocked_shots": 3.6,
        "fouls_pro": 13.6,
        "fouls_against": 12.0,
        "tactics": "3-5-2 Blocco Basso",
    },
    # PREMIER LEAGUE
    "Manchester City": {
        "gf_h": 2.55,
        "gf_a": 2.10,
        "ga_h": 0.70,
        "ga_a": 0.95,
        "xg_5": 2.45,
        "xga_5": 0.85,
        "xg_s": 2.35,
        "over15_pct": 0.88,
        "sot_pro": 7.3,
        "sot_against": 2.9,
        "corners_pro": 7.8,
        "corners_against": 2.8,
        "cross": 23.0,
        "blocked_shots": 6.4,
        "fouls_pro": 9.5,
        "fouls_against": 11.5,
        "tactics": "3-2-4-1 Dominio Territoriale",
    },
    "Arsenal": {
        "gf_h": 2.30,
        "gf_a": 1.95,
        "ga_h": 0.65,
        "ga_a": 0.80,
        "xg_5": 2.25,
        "xga_5": 0.70,
        "xg_s": 2.15,
        "over15_pct": 0.85,
        "sot_pro": 6.7,
        "sot_against": 2.8,
        "corners_pro": 7.2,
        "corners_against": 3.1,
        "cross": 21.8,
        "blocked_shots": 5.9,
        "fouls_pro": 10.2,
        "fouls_against": 12.0,
        "tactics": "4-3-3 Pressing Asfissiante",
    },
    "Liverpool": {
        "gf_h": 2.40,
        "gf_a": 2.05,
        "ga_h": 0.75,
        "ga_a": 0.90,
        "xg_5": 2.35,
        "xga_5": 0.85,
        "xg_s": 2.25,
        "over15_pct": 0.86,
        "sot_pro": 7.0,
        "sot_against": 3.3,
        "corners_pro": 7.4,
        "corners_against": 3.4,
        "cross": 22.0,
        "blocked_shots": 6.1,
        "fouls_pro": 10.6,
        "fouls_against": 11.8,
        "tactics": "4-2-3-1 Verticale ad Alta Intensità",
    },
    "Real Madrid": {
        "gf_h": 2.45,
        "gf_a": 2.00,
        "ga_h": 0.70,
        "ga_a": 0.90,
        "xg_5": 2.30,
        "xga_5": 0.85,
        "xg_s": 2.20,
        "over15_pct": 0.85,
        "sot_pro": 6.9,
        "sot_against": 3.4,
        "corners_pro": 6.8,
        "corners_against": 3.6,
        "cross": 20.5,
        "blocked_shots": 5.8,
        "fouls_pro": 10.1,
        "fouls_against": 13.0,
        "tactics": "4-3-3 Fluidità e Transizione",
    },
    "Barcellona": {
        "gf_h": 2.60,
        "gf_a": 2.15,
        "ga_h": 0.85,
        "ga_a": 1.05,
        "xg_5": 2.40,
        "xga_5": 0.95,
        "xg_s": 2.30,
        "over15_pct": 0.89,
        "sot_pro": 7.1,
        "sot_against": 3.6,
        "corners_pro": 6.9,
        "corners_against": 3.5,
        "cross": 21.0,
        "blocked_shots": 6.0,
        "fouls_pro": 10.5,
        "fouls_against": 12.5,
        "tactics": "4-2-3-1 Linea Altissima",
    },
    "Bayern Monaco": {
        "gf_h": 2.70,
        "gf_a": 2.25,
        "ga_h": 0.80,
        "ga_a": 1.00,
        "xg_5": 2.55,
        "xga_5": 0.85,
        "xg_s": 2.45,
        "over15_pct": 0.90,
        "sot_pro": 7.5,
        "sot_against": 3.2,
        "corners_pro": 7.6,
        "corners_against": 3.0,
        "cross": 22.8,
        "blocked_shots": 6.5,
        "fouls_pro": 9.3,
        "fouls_against": 11.2,
        "tactics": "4-2-3-1 Dominio Offensivo",
    },
    "PSG": {
        "gf_h": 2.50,
        "gf_a": 2.05,
        "ga_h": 0.75,
        "ga_a": 0.95,
        "xg_5": 2.35,
        "xga_5": 0.90,
        "xg_s": 2.25,
        "over15_pct": 0.87,
        "sot_pro": 7.0,
        "sot_against": 3.5,
        "corners_pro": 7.0,
        "corners_against": 3.4,
        "cross": 21.2,
        "blocked_shots": 6.0,
        "fouls_pro": 10.2,
        "fouls_against": 12.0,
        "tactics": "4-3-3 Possesso e Pressione",
    },
}

DEFAULT_METRICS = {
    "gf_h": 1.30,
    "gf_a": 1.05,
    "ga_h": 1.10,
    "ga_a": 1.45,
    "xg_5": 1.25,
    "xga_5": 1.35,
    "xg_s": 1.25,
    "over15_pct": 0.50,
    "sot_pro": 4.1,
    "sot_against": 4.8,
    "corners_pro": 4.6,
    "corners_against": 5.2,
    "cross": 16.0,
    "blocked_shots": 3.8,
    "fouls_pro": 13.0,
    "fouls_against": 12.0,
    "tactics": "4-4-2 Blocco Medio",
}


def get_metrics(team_name):
  cleaned = clean_name(team_name)
  for name, metrics in TEAM_METRICS.items():
    if name.lower() in cleaned.lower() or cleaned.lower() in name.lower():
      return metrics
  return DEFAULT_METRICS


SERIE_A_PLAYERS = [
    {
        "team": "Inter",
        "name": "Lautaro Martinez",
        "role": "Attaccante",
        "sot_90": 1.85,
        "fouls_c_90": 1.45,
        "fouls_s_90": 2.10,
        "penalties": True,
        "freekicks": False,
    },
    {
        "team": "Inter",
        "name": "Marcus Thuram",
        "role": "Attaccante",
        "sot_90": 1.40,
        "fouls_c_90": 1.20,
        "fouls_s_90": 1.85,
        "penalties": False,
        "freekicks": False,
    },
    {
        "team": "Juventus",
        "name": "Dusan Vlahovic",
        "role": "Attaccante",
        "sot_90": 1.65,
        "fouls_c_90": 1.55,
        "fouls_s_90": 1.95,
        "penalties": True,
        "freekicks": True,
    },
    {
        "team": "Milan",
        "name": "Rafael Leao",
        "role": "Ala Sinistra",
        "sot_90": 1.30,
        "fouls_c_90": 0.85,
        "fouls_s_90": 2.45,
        "penalties": False,
        "freekicks": False,
    },
    {
        "team": "Napoli",
        "name": "Khvicha Kvaratskhelia",
        "role": "Ala Sinistra",
        "sot_90": 1.35,
        "fouls_c_90": 1.10,
        "fouls_s_90": 2.60,
        "penalties": True,
        "freekicks": True,
    },
    {
        "team": "Atalanta",
        "name": "Mateo Retegui",
        "role": "Attaccante",
        "sot_90": 1.70,
        "fouls_c_90": 1.65,
        "fouls_s_90": 1.75,
        "penalties": True,
        "freekicks": False,
    },
    {
        "team": "Roma",
        "name": "Paulo Dybala",
        "role": "Seconda Punta",
        "sot_90": 1.45,
        "fouls_c_90": 0.70,
        "fouls_s_90": 2.30,
        "penalties": True,
        "freekicks": True,
    },
    {
        "team": "Lazio",
        "name": "Mattia Zaccagni",
        "role": "Ala Sinistra",
        "sot_90": 1.10,
        "fouls_c_90": 1.80,
        "fouls_s_90": 2.85,
        "penalties": True,
        "freekicks": False,
    },
]

SERIE_A_REFEREES = [
    {
        "name": "Daniele Doveri",
        "fouls_avg": 25.4,
        "cards_avg": 4.1,
        "severity": "Standard",
    },
    {
        "name": "Fabio Maresca",
        "fouls_avg": 28.2,
        "cards_avg": 5.4,
        "severity": "Severo",
    },
    {
        "name": "Maurizio Mariani",
        "fouls_avg": 27.8,
        "cards_avg": 4.8,
        "severity": "Severo",
    },
    {
        "name": "Simone Sozza",
        "fouls_avg": 21.5,
        "cards_avg": 3.6,
        "severity": "Permissivo",
    },
    {
        "name": "Michael Fabbri",
        "fouls_avg": 26.1,
        "cards_avg": 4.5,
        "severity": "Standard",
    },
]


# MOTORE QUANTITATIVO MATCH ANALYST
class MatchAnalystEngine:

  @staticmethod
  def calculate_kelly_fraction(prob, odds, bankroll, kelly_fraction=0.50):
    b = odds - 1.0
    if b <= 0:
      return 0.0, 0.0
    p_loss = 1.0 - prob
    kelly_full = (prob * b - p_loss) / b
    kelly_scaled = max(0.0, kelly_full * kelly_fraction)

    edge = (prob * odds) - 1.0
    if edge <= 0.05:
      cap = 0.05
    elif edge <= 0.10:
      cap = 0.12
    else:
      cap = 0.20

    final_stake_pct = min(kelly_scaled, cap)
    monetary_stake = round(bankroll * final_stake_pct, 2)
    return round(final_stake_pct * 100, 2), monetary_stake

  @staticmethod
  def analyze_over15_team(
      team, opp, is_home, league_avg_ga=1.25, bookmaker_odds=1.85
  ):
    t_met = get_metrics(team)
    o_met = get_metrics(opp)
    c_team = clean_name(team)

    gf = t_met["gf_h"] if is_home else t_met["gf_a"]
    ga_opp = o_met["ga_a"] if is_home else o_met["ga_h"]

    xg_base = (
        gf
        * (ga_opp / league_avg_ga)
        * (t_met["xg_5"] / max(0.1, t_met["xg_s"]))
    )

    mod = 1.0
    if "3-4-2-1" in t_met["tactics"] or "4-3-3" in t_met["tactics"]:
      mod += 0.08
    if "Pressing" in t_met["tactics"]:
      mod += 0.10
    if "Low block" in o_met["tactics"]:
      mod -= 0.10

    xg_final = xg_base * mod

    p0 = poisson.pmf(0, xg_final)
    p1 = poisson.pmf(1, xg_final)
    prob_model = float(1.0 - (p0 + p1))
    prob_imp = 1.0 / bookmaker_odds
    edge = (prob_model * bookmaker_odds) - 1.0

    return {
        "market": f"Over 1.5 Gol ({c_team})",
        "market_type": "Over 1.5 Gol Squadra",
        "bookmaker_note": "Disponibile Subito (Betsson / .IT)",
        "xg_final": xg_final,
        "prob_model": prob_model,
        "prob_imp": prob_imp,
        "edge": edge,
        "odds": bookmaker_odds,
        "details": {
            "media_gf": gf,
            "ga_opp": ga_opp,
            "tactics_t": t_met["tactics"],
            "tactics_o": o_met["tactics"],
            "mod": mod,
        },
    }

  @staticmethod
  def analyze_sot_team(
      team,
      opp,
      is_home,
      line=4.5,
      league_sot_avg=4.3,
      bookmaker_odds=1.80,
  ):
    t_met = get_metrics(team)
    o_met = get_metrics(opp)
    c_team = clean_name(team)

    sot_fatti = t_met["sot_pro"]
    sot_subiti_opp = o_met["sot_against"]

    xs_base = sot_fatti * (sot_subiti_opp / league_sot_avg)

    mod = 1.0
    if "Dominio Possesso" in t_met["tactics"]:
      mod += 0.06
    if "Pressing" in t_met["tactics"]:
      mod += 0.08
    if "Low block" in o_met["tactics"]:
      mod -= 0.10

    xs_final = xs_base * mod
    prob_model = float(1.0 - poisson.cdf(line - 0.5, xs_final))
    prob_imp = 1.0 / bookmaker_odds
    edge = (prob_model * bookmaker_odds) - 1.0

    return {
        "market": f"Over {line} Tiri in porta ({c_team})",
        "market_type": "Tiri in porta Squadra",
        "bookmaker_note": "Aperta (< 48h)",
        "xs_final": xs_final,
        "prob_model": prob_model,
        "prob_imp": prob_imp,
        "edge": edge,
        "odds": bookmaker_odds,
        "details": {
            "sot_pro": sot_fatti,
            "sot_against_opp": sot_subiti_opp,
            "tactics": t_met["tactics"],
            "mod": mod,
        },
    }

  @staticmethod
  def analyze_corners_match(
      h_team, a_team, line=9.5, bookmaker_odds=1.92
  ):
    h_met = get_metrics(h_team)
    a_met = get_metrics(a_team)

    base_corners = (h_met["corners_pro"] + a_met["corners_against"]) / 2.0 + (
        a_met["corners_pro"] + h_met["corners_against"]
    ) / 2.0

    mod = 1.0
    if h_met["cross"] > 20.0 or a_met["cross"] > 20.0:
      mod += 0.08
    if h_met["blocked_shots"] > 5.0 or a_met["blocked_shots"] > 5.0:
      mod += 0.10

    corners_final = base_corners * mod
    prob_model = float(1.0 - poisson.cdf(line - 0.5, corners_final))
    prob_imp = 1.0 / bookmaker_odds
    edge = (prob_model * bookmaker_odds) - 1.0

    return {
        "market": f"Over {line} Corner Totali",
        "market_type": "Corner Totali",
        "bookmaker_note": "Disponibile Subito (Betsson / .IT)",
        "corners_final": corners_final,
        "prob_model": prob_model,
        "prob_imp": prob_imp,
        "edge": edge,
        "odds": bookmaker_odds,
        "details": {
            "h_cross": h_met["cross"],
            "a_cross": a_met["cross"],
            "h_blocked": h_met["blocked_shots"],
            "a_blocked": a_met["blocked_shots"],
        },
    }

  @staticmethod
  def analyze_player_fouls_serie_a(
      player, opp_team, referee, line=1.5, bookmaker_odds=1.95
  ):
    opp_met = get_metrics(opp_team)

    xf_base = (
        player["fouls_c_90"]
        * (85 / 90)
        * (opp_met["fouls_against"] / 12.5)
        * (referee["fouls_avg"] / 25.5)
    )

    mod = 1.0
    if referee["severity"] == "Severo":
      mod += 0.10
    elif referee["severity"] == "Permissivo":
      mod -= 0.10
    if "Pressing" in get_metrics(player["team"])["tactics"]:
      mod += 0.08

    xf_final = xf_base * mod
    prob_model = float(1.0 - poisson.cdf(line - 0.5, xf_final))
    prob_imp = 1.0 / bookmaker_odds
    edge = (prob_model * bookmaker_odds) - 1.0

    return {
        "market": f"Over {line} Falli Commessi ({player['name']})",
        "market_type": "Falli Giocatore (Serie A)",
        "bookmaker_note": "Aperta (< 48h)",
        "player": player["name"],
        "team": clean_name(player["team"]),
        "opp": clean_name(opp_team),
        "referee": referee["name"],
        "ref_severity": referee["severity"],
        "xf_final": xf_final,
        "prob_model": prob_model,
        "prob_imp": prob_imp,
        "edge": edge,
        "odds": bookmaker_odds,
        "details": {
            "fouls_90": player["fouls_c_90"],
            "ref_avg": referee["fouls_avg"],
            "opp_fouls_s": opp_met["fouls_against"],
        },
    }


# FILTRO AUTOMATICO DEL TURNO
def filter_current_matchday(matches):
  if not matches:
    return [], "", ""

  parsed = []
  for m in matches:
    ct_str = m.get("commence_time", "")
    try:
      dt = datetime.datetime.fromisoformat(ct_str.replace("Z", "+00:00"))
      parsed.append((dt, m))
    except Exception:
      pass

  if not parsed:
    return matches, "", ""

  parsed.sort(key=lambda x: x[0])
  first_dt = parsed[0][0]
  round_cutoff = first_dt + datetime.timedelta(days=4)
  current_round = [m for dt, m in parsed if dt <= round_cutoff]

  start_label = first_dt.strftime("%d/%m/%Y")
  end_label = max(dt for dt, m in parsed if dt <= round_cutoff).strftime(
      "%d/%m/%Y"
  )

  return current_round, start_label, end_label


# SCANNER AUTOMATIZZATO CON FILTRO TEMPORALE DINAMICO A 48 ORE
def scan_league_opportunities(
    matches,
    league_name,
    bankroll,
    kelly_fraction=0.50,
    min_odds=1.70,
    min_edge=0.01,
):
  results = []
  is_serie_a = "serie_a" in league_name.lower() or "italia" in league_name.lower()
  now_utc = datetime.datetime.now(datetime.timezone.utc)

  ref_cycle = 0

  for match in matches:
    raw_h = match.get("home_team", "")
    raw_a = match.get("away_team", "")
    h_team = clean_name(raw_h)
    a_team = clean_name(raw_a)
    match_title = f"{h_team} vs {a_team}"
    match_date = match.get("commence_time", "")[:10]
    ct_str = match.get("commence_time", "")

    hours_to_kickoff = 999.0
    if ct_str:
      try:
        match_dt = datetime.datetime.fromisoformat(
            ct_str.replace("Z", "+00:00")
        )
        hours_to_kickoff = (match_dt - now_utc).total_seconds() / 3600.0
      except Exception:
        hours_to_kickoff = 999.0

    props_unlocked = hours_to_kickoff <= 48.0

    # 1. Over 1.5 Gol Squadra Casa
    ov_h = MatchAnalystEngine.analyze_over15_team(
        h_team, a_team, is_home=True, bookmaker_odds=1.85
    )
    if ov_h["odds"] >= min_odds and ov_h["edge"] >= min_edge:
      stake_pct, stake_eur = MatchAnalystEngine.calculate_kelly_fraction(
          ov_h["prob_model"], ov_h["odds"], bankroll, kelly_fraction
      )
      results.append({
          "match": match_title,
          "date": match_date,
          "market": ov_h["market"],
          "type": ov_h["market_type"],
          "bk_note": ov_h["bookmaker_note"],
          "odds": ov_h["odds"],
          "prob_model": ov_h["prob_model"],
          "prob_imp": ov_h["prob_imp"],
          "edge": ov_h["edge"],
          "stake_pct": stake_pct,
          "stake_eur": stake_eur,
          "report_data": ov_h,
      })

    # 2. Over 1.5 Gol Squadra Trasferta
    ov_a = MatchAnalystEngine.analyze_over15_team(
        a_team, h_team, is_home=False, bookmaker_odds=1.95
    )
    if ov_a["odds"] >= min_odds and ov_a["edge"] >= min_edge:
      stake_pct, stake_eur = MatchAnalystEngine.calculate_kelly_fraction(
          ov_a["prob_model"], ov_a["odds"], bankroll, kelly_fraction
      )
      results.append({
          "match": match_title,
          "date": match_date,
          "market": ov_a["market"],
          "type": ov_a["market_type"],
          "bk_note": ov_a["bookmaker_note"],
          "odds": ov_a["odds"],
          "prob_model": ov_a["prob_model"],
          "prob_imp": ov_a["prob_imp"],
          "edge": ov_a["edge"],
          "stake_pct": stake_pct,
          "stake_eur": stake_eur,
          "report_data": ov_a,
      })

    # 3. Corner Totali
    corn = MatchAnalystEngine.analyze_corners_match(
        h_team, a_team, line=9.5, bookmaker_odds=1.92
    )
    if corn["odds"] >= min_odds and corn["edge"] >= min_edge:
      stake_pct, stake_eur = MatchAnalystEngine.calculate_kelly_fraction(
          corn["prob_model"], corn["odds"], bankroll, kelly_fraction
      )
      results.append({
          "match": match_title,
          "date": match_date,
          "market": corn["market"],
          "type": corn["market_type"],
          "bk_note": corn["bookmaker_note"],
          "odds": corn["odds"],
          "prob_model": corn["prob_model"],
          "prob_imp": corn["prob_imp"],
          "edge": corn["edge"],
          "stake_pct": stake_pct,
          "stake_eur": stake_eur,
          "report_data": corn,
      })

    # SBLOCCO MERCATI STATISTICI / PROPS (< 48h)
    if props_unlocked:
      # 4. Tiri in Porta Squadra
      sot_h = MatchAnalystEngine.analyze_sot_team(
          h_team, a_team, is_home=True, line=4.5, bookmaker_odds=1.80
      )
      if sot_h["odds"] >= min_odds and sot_h["edge"] >= min_edge:
        stake_pct, stake_eur = MatchAnalystEngine.calculate_kelly_fraction(
            sot_h["prob_model"], sot_h["odds"], bankroll, kelly_fraction
        )
        results.append({
            "match": match_title,
            "date": match_date,
            "market": sot_h["market"],
            "type": sot_h["market_type"],
            "bk_note": sot_h["bookmaker_note"],
            "odds": sot_h["odds"],
            "prob_model": sot_h["prob_model"],
            "prob_imp": sot_h["prob_imp"],
            "edge": sot_h["edge"],
            "stake_pct": stake_pct,
            "stake_eur": stake_eur,
            "report_data": sot_h,
        })

      # 5. Falli Giocatori Serie A
      if is_serie_a:
        assigned_ref = SERIE_A_REFEREES[ref_cycle % len(SERIE_A_REFEREES)]
        ref_cycle += 1

        for p in SERIE_A_PLAYERS:
          if p["team"].lower() in h_team.lower():
            f_res = MatchAnalystEngine.analyze_player_fouls_serie_a(
                p, a_team, assigned_ref, line=1.5, bookmaker_odds=1.95
            )
            if f_res["odds"] >= min_odds and f_res["edge"] >= min_edge:
              stake_pct, stake_eur = MatchAnalystEngine.calculate_kelly_fraction(
                  f_res["prob_model"], f_res["odds"], bankroll, kelly_fraction
              )
              results.append({
                  "match": match_title,
                  "date": match_date,
                  "market": f_res["market"],
                  "type": f_res["market_type"],
                  "bk_note": f_res["bookmaker_note"],
                  "odds": f_res["odds"],
                  "prob_model": f_res["prob_model"],
                  "prob_imp": f_res["prob_imp"],
                  "edge": f_res["edge"],
                  "stake_pct": stake_pct,
                  "stake_eur": stake_eur,
                  "report_data": f_res,
              })

  results.sort(key=lambda x: x["edge"], reverse=True)
  return results


# FETCH QUOTE API CON CACHE
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_odds_api(api_key, sport_key):
  url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
  try:
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
      remaining = res.headers.get("x-requests-remaining", "N/D")
      return res.json(), remaining, None
    return None, None, f"Errore API {res.status_code}: {res.text}"
  except Exception as e:
    return None, None, str(e)


# HEADER APPLICAZIONE
st.title("VALUE BET ANALYZER")
st.caption(
    "Suite Qualitativa Professionale | L'A.I. Applicata Al Mondo Del Betting"
)

# SIDEBAR: Utente, Parametri & Bankroll
user_email = st.session_state.user.get("email", "")
is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE (DEMO)"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")

if not is_premium:
  st.sidebar.markdown("---")
  st.sidebar.markdown("### SBLOCCO PIANO PRO")
  promo_code = st.sidebar.text_input(
      "Codice VIP / Tester",
      placeholder="Inserisci codice...",
      type="password",
  )
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
initial_bankroll = st.sidebar.number_input(
    "Bankroll Iniziale (€)",
    min_value=10.0,
    value=1000.0,
    step=50.0,
    help="Il capitale totale a disposizione dedicato alle giocate di valore.",
)

kelly_fraction = st.sidebar.select_slider(
    "Frazione di Kelly",
    options=[0.25, 0.50],
    value=0.50,
    format_func=lambda x: (
        "0.25 (Prudente / Kelly/4)"
        if x == 0.25
        else "0.50 (Standard / Kelly Mezzato)"
    ),
    help=(
        "Regola la formula di proporzionamento del capitale (Criterio di"
        " Kelly). 0.50 (Kelly Mezzato) è lo standard quantitativo che protegge"
        " il bankroll dalla varianza fisiologica, mentre 0.25 è una gestione"
        " iper-prudenziale."
    ),
)

min_edge_pct = st.sidebar.slider(
    "Soglia Minima Edge (%)",
    min_value=1.0,
    max_value=15.0,
    value=1.0,
    step=0.5,
    help=(
        "L'Edge rappresenta il vantaggio matematico percentuale stimato"
        " rispetto alla quota implicita del bookmaker. Solo le giocate con un"
        " vantaggio pari o superiore a questa soglia verranno mostrate nello"
        " scanner."
    ),
)
min_edge_val = min_edge_pct / 100.0

# Calcolo Metriche Personali Utente
bets_df = fetch_user_bets(st.session_state.user.get("id"))
total_profit = 0.0
yield_pct = 0.0
win_rate_pct = 0.0

if not bets_df.empty and "status" in bets_df.columns:
  settled_bets = bets_df[bets_df["status"].isin(["VINTA", "PERSA"])]
  total_profit = (
      float(settled_bets["profit"].sum()) if not settled_bets.empty else 0.0
  )
  total_settled_stake = (
      float(settled_bets["stake"].sum()) if not settled_bets.empty else 0.0
  )
  won_count = (
      len(settled_bets[settled_bets["status"] == "VINTA"])
      if not settled_bets.empty
      else 0
  )

  if total_settled_stake > 0:
    yield_pct = (total_profit / total_settled_stake) * 100.0
  if len(settled_bets) > 0:
    win_rate_pct = (won_count / len(settled_bets)) * 100.0

current_bankroll = initial_bankroll + total_profit
profit_pct = (
    (total_profit / initial_bankroll) * 100.0 if initial_bankroll > 0 else 0.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### IL TUO BANKROLL CLOUD")
st.sidebar.markdown(
    f"""
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
""",
    unsafe_allow_html=True,
)

user_api_key = st.secrets.get("ODDS_API_KEY", "")

ALL_LEAGUES = {
    "Serie A (Italia)": "soccer_italy_serie_a",
    "Premier League (Inghilterra)": "soccer_epl",
    "La Liga (Spagna)": "soccer_spain_la_liga",
    "Bundesliga (Germania)": "soccer_germany_bundesliga",
    "Ligue 1 (Francia)": "soccer_france_ligue_one",
    "Champions League": "soccer_uefa_champs_league",
    "Europa League": "soccer_uefa_europa_league",
}

available_leagues = (
    ALL_LEAGUES if is_premium else {"Serie A (Italia)": "soccer_italy_serie_a"}
)

if not is_premium:
  st.markdown(
      """
        <div class="trial-banner">
            <h4 style="margin:0 0 6px 0; color:#10B981;">MODALITÀ FREE (SOLO SERIE A)</h4>
            <p style="margin:0; font-size:0.92rem; color:#D1D5DB;">
                Visualizzi le giocate statistiche <b>#4 e #5</b> del turno in corso di Serie A. Attiva il piano <b>Premium</b> per sbloccare tutti i campionati europei e la Top 3 a massimo valore atteso.
            </p>
        </div>
        """,
      unsafe_allow_html=True,
  )

# SCHEDE PRINCIPALI
tab_scanner, tab_bets, tab_account = st.tabs(
    ["Scanner Value Bet", "Registro Scommesse", "Gestione Account"]
)

with tab_scanner:
  st.markdown("### SCANNER QUALITATIVO DI VALUE BET")
  col_l, col_btn = st.columns([2, 1])

  with col_l:
    selected_league = st.selectbox(
        "Seleziona Torneo", list(available_leagues.keys()), index=0
    )
    sport_key = available_leagues[selected_league]

  with col_btn:
    st.write("")
    st.write("")
    scan_trigger = st.button("AVVIA SCANNER", use_container_width=True)

  if scan_trigger or "league_matches_cache" not in st.session_state:
    if user_api_key:
      data, rem, err = fetch_odds_api(user_api_key, sport_key)
      if err:
        st.error(f"Errore API: {err}")
      elif data:
        st.session_state["league_matches_cache"] = data
        st.session_state["api_rem"] = rem
    else:
      st.error("Chiave ODDS_API_KEY mancante nei Secrets.")

  all_raw_matches = st.session_state.get("league_matches_cache", [])

  if all_raw_matches:
    matches, round_start, round_end = filter_current_matchday(all_raw_matches)

    st.markdown(
        f'<div class="round-badge">TURNO ATTIVO: {round_start} - {round_end}'
        f" ({len(matches)} incontri in programma)</div>",
        unsafe_allow_html=True,
    )

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    has_pending_props = False
    for m in matches:
      ct = m.get("commence_time")
      if ct:
        try:
          mdt = datetime.datetime.fromisoformat(ct.replace("Z", "+00:00"))
          if (mdt - now_utc).total_seconds() / 3600.0 > 48.0:
            has_pending_props = True
            break
        except Exception:
          pass

    if has_pending_props:
      st.markdown(
          """
            <div class="props-notice-badge">
                <b>AVVISO MERCATI:</b> Alcune gare del turno distano oltre 48 ore. Al momento lo scanner include i mercati principali disponibili subito (Over 1.5 Gol e Corner). Le quote statistiche (Tiri in porta e Falli) si sbloccheranno automaticamente nella Top 5 a 24-48h dal fischio d'inizio.
            </div>
            """,
          unsafe_allow_html=True,
      )

    all_bets = scan_league_opportunities(
        matches,
        selected_league,
        current_bankroll,
        kelly_fraction=kelly_fraction,
        min_odds=1.70,
        min_edge=min_edge_val,
    )

    st.markdown("---")
    st.markdown(
        f"### VALUE BETS RILEVATE (EDGE $\\ge$ {min_edge_pct:.1f}% | ZERO 1X2)"
    )

    if all_bets:
      top_bets = all_bets[:5]
      table_rows = []

      for idx, bet in enumerate(top_bets):
        pos = idx + 1
        if is_premium or pos in [4, 5]:
          table_rows.append({
              "POS": f"#{pos}",
              "PARTITA": bet["match"],
              "DATA": bet["date"],
              "MERCATO": bet["market"],
              "QUOTA": f"{bet['odds']:.2f}",
              "PROB. REALE": f"{bet['prob_model']*100:.1f}%",
              "EDGE REALE": f"{bet['edge']*100:+.2f}%",
              "STAKE CONSIGLIATO": f"{bet['stake_pct']}% ({bet['stake_eur']:.2f} €)",
              "DISPONIBILITÀ QUOTA": bet["bk_note"],
          })
        else:
          table_rows.append({
              "POS": f"#{pos}",
              "PARTITA": bet["match"],
              "DATA": bet["date"],
              "MERCATO": "[BLOCCATO - PIANO PREMIUM]",
              "QUOTA": "---",
              "PROB. REALE": "---",
              "EDGE REALE": "---",
              "STAKE CONSIGLIATO": "---",
              "DISPONIBILITÀ QUOTA": "---",
          })

      st.table(pd.DataFrame(table_rows))

      st.markdown("---")
      st.markdown("### SCHEDE MOTIVATE & SPIEGAZIONE TECNICA")

      for idx, bet in enumerate(top_bets):
        pos = idx + 1
        if is_premium or pos in [4, 5]:
          rep = bet["report_data"]
          with st.expander(
              f"Report #{pos} | {bet['match']} - {bet['market']} (Edge:"
              f" {bet['edge']*100:+.2f}%)",
              expanded=(pos == 1 or pos == 4),
          ):
            st.markdown(f"**Tipologia:** `{bet['type']}`")
            st.markdown(f"**Stato Quota:** `{bet['bk_note']}`")
            st.markdown(
                f"**Probabilità Modello:** `{bet['prob_model']*100:.1f}%` |"
                f" **Probabilità Implicita Bookmaker:**"
                f" `{bet['prob_imp']*100:.1f}%`"
            )
            st.markdown(
                f"**Edge Matematico:** `{bet['edge']*100:+.2f}%` | **Stake"
                f" Consigliato:** `{bet['stake_pct']}%` ({bet['stake_eur']:.2f}"
                " €)"
            )

            st.markdown("#### Motivazione Tecnica Quantitativa:")
            if "Gol Squadra" in bet["type"]:
              st.write(
                  f"- **Proiezione Gol Attesi:** `{rep['xg_final']:.2f}`"
                  " (modello Poisson)."
              )
              st.write(
                  f"- **Efficienza Offensiva:** Media Gol Fatti ="
                  f" `{rep['details']['media_gf']:.2f}`, Concessione Difensiva"
                  f" Avversario = `{rep['details']['ga_opp']:.2f}`."
              )
              st.write(
                  f"- **Assetto Tattico:** `{rep['details']['tactics_t']}` vs"
                  f" `{rep['details']['tactics_o']}` (Fattore correttivo: +"
                  f" {int((rep['details']['mod']-1)*100)}%)."
              )
            elif "Tiri in porta" in bet["type"]:
              st.write(
                  "- **Proiezione Tiri nello Specchio (xS):**"
                  f" `{rep['xs_final']:.2f}`"
              )
              st.write(
                  "- **Concessione Avversario:**"
                  f" `{rep['details']['sot_against_opp']:.1f}` tiri in porta"
                  " medi concessi a partita."
              )
              st.write(
                  "- **Indicazione Operativa:** Mercato aperto nelle 24-48 ore"
                  " pre-gara sui principali bookmaker .IT."
              )
            elif "Corner" in bet["type"]:
              st.write(
                  "- **Volume Corner Proiettato:**"
                  f" `{rep['corners_final']:.2f}` corner totali."
              )
              st.write(
                  "- **Metriche Laterali:** Cross medi combinati ="
                  f" `{rep['details']['h_cross'] + rep['details']['a_cross']:.1f}`"
                  " a partita | Tiri bloccati combinati ="
                  f" `{rep['details']['h_blocked'] + rep['details']['a_blocked']:.1f}`."
              )
            elif "Falli" in bet["type"]:
              st.write(
                  f"- **Proiezione Falli Attesi (xFouls):**"
                  f" `{rep['xf_final']:.2f}`"
              )
              st.write(
                  f"- **Designazione AIA:** Arbitro `{rep['referee']}` (Media:"
                  f" `{rep['details']['ref_avg']:.1f}` falli a partita -"
                  f" Severità: `{rep['ref_severity']}`)."
              )
              st.write(
                  f"- **Duello di Zona:** Avversario diretto subisce"
                  f" `{rep['details']['opp_fouls_s']:.1f}` falli a partita."
              )

      st.markdown("---")
      st.markdown("### REGISTRA GIOCATA NEL TUO BANKROLL")
      col_reg1, col_reg2 = st.columns([3, 1])
      with col_reg1:
        bet_options = [
            f"#{i+1} | {b['match']} | {b['market']} @ {b['odds']:.2f} (Stake: {b['stake_eur']:.2f} €)"
            for i, b in enumerate(top_bets)
            if is_premium or (i + 1) in [4, 5]
        ]
        if bet_options:
            selected_bet_idx = st.selectbox(
                "Seleziona Scommessa da Registrare",
                range(len(bet_options)),
                format_func=lambda x: bet_options[x],
            )
      with col_reg2:
        st.write("")
        st.write("")
        if bet_options and st.button(
            "SALVA NEL DATABASE", use_container_width=True
        ):
          chosen = [
              b
              for i, b in enumerate(top_bets)
              if is_premium or (i + 1) in [4, 5]
          ][selected_bet_idx]
          save_user_bet(
              st.session_state.user.get("id"),
              chosen["match"],
              chosen["market"],
              chosen["odds"],
              chosen["stake_eur"],
              chosen["edge"],
          )
          st.success("Scommessa salvata nel database cloud.")
          st.rerun()
    else:
      st.info(
          f"Nessuna giocata statistica supera la soglia Edge selezionata ({min_edge_pct:.1f}%)."
      )

with tab_bets:
  st.markdown("### STORICO PERSONALE SCOMMESSE")
  user_bets = fetch_user_bets(st.session_state.user.get("id"))

  if not user_bets.empty:
    # Mostriamo una vista formattata
    display_df = user_bets[["created_at", "match", "market", "odds", "stake", "status", "profit"]].copy()
    display_df["created_at"] = pd.to_datetime(display_df["created_at"]).dt.strftime('%d/%m/%Y')
    
    # Formattazione e Colorazione Colonna Profilto
    st.dataframe(
        display_df,
        column_config={
            "created_at": "DATA",
            "match": "PARTITA",
            "market": "MERCATO",
            "odds": st.column_config.NumberColumn("QUOTA", format="%.2f"),
            "stake": st.column_config.NumberColumn("STAKE (€)", format="%.2f €"),
            "status": "ESITO",
            "profit": st.column_config.NumberColumn(
                "PROFITTO/PERDITA (€)",
                format="%.2f €"
            )
        },
        use_container_width=True,
        hide_index=True
    )

    st.markdown("### CHIUDI ESITO SCOMMESSA")
    pending = user_bets[user_bets["status"] == "IN CORSO"]

    if not pending.empty:
      col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
      with col_u1:
        bet_to_update = st.selectbox(
            "Scommessa da Concludere",
            pending["id"].tolist(),
            format_func=lambda x: (
                f"ID {x} |"
                f" {pending.loc[pending['id']==x, 'match'].values[0]} -"
                f" {pending.loc[pending['id']==x, 'market'].values[0]}"
            ),
        )
      with col_u2:
        new_status = st.selectbox("Esito", ["VINTA", "PERSA"])
      with col_u3:
        st.write("")
        st.write("")
        if st.button("AGGIORNA ESITO", use_container_width=True):
          row = pending[pending["id"] == bet_to_update].iloc[0]
          update_bet_status(
              bet_to_update,
              new_status,
              float(row["odds"]),
              float(row["stake"]),
          )
          st.success("Esito registrato. Bankroll ricalcolato.")
          st.rerun()
    else:
      st.info("Non ci sono scommesse in corso.")
  else:
    st.info("Nessuna scommessa registrata finora.")

with tab_account:
  st.markdown("### GESTIONE ACCOUNT")

  with st.expander("Il Mio Profilo", expanded=True):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
      st.markdown(f"**Email:** `{user_email}`")
      st.markdown(f"**Stato Abbonamento:** `{tier_label}`")
    with col_p2:
      st.markdown(f"**ID Utente:** `{st.session_state.user.get('id')}`")

  with st.expander("Modifica Password"):
    new_pwd = st.text_input(
        "Nuova Password (min. 6 caratteri)",
        type="password",
        key="chg_pwd",
    )
    conf_pwd = st.text_input(
        "Conferma Nuova Password", type="password", key="conf_pwd"
    )

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
