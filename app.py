import datetime
import numpy as np
import pandas as pd
import requests
import streamlit as st
from scipy.stats import poisson

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0A0E17;
        color: #F3F4F6;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    .metric-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    
    .metric-title {
        font-size: 0.75rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    
    .metric-value-pos {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.20rem;
        font-weight: 700;
        color: #10B981;
    }
    
    .metric-value-neg {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.20rem;
        font-weight: 700;
        color: #EF4444;
    }
    
    .metric-value-neutral {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.20rem;
        font-weight: 700;
        color: #F9FAFB;
    }
    
    .trial-banner {
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid #10B981;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background-color: #10B981;
        color: #064E3B;
        font-weight: 700;
        border-radius: 6px;
        border: none;
        padding: 10px 20px;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        background-color: #059669;
        color: #FFFFFF;
    }
    
    div[data-testid="stTable"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #1F2937;
        background-color: #111827;
    }
    
    table {
        color: #F9FAFB !important;
        font-family: 'JetBrains Mono', monospace;
    }
    
    thead tr th {
        background-color: #1E293B !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.05em;
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


# Funzioni Autenticazione HTTP Supabase
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
        or "Credenziali non valide."
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
      return True, "Registrazione completata. Ora puoi accedere."
    err = (
        res.json().get("msg")
        or res.json().get("error_description")
        or "Errore durante la registrazione."
    )
    return False, err
  except Exception as e:
    return False, str(e)


def reset_password_request(email):
  if not SB_URL or not SB_KEY:
    return False, "Chiavi Supabase mancanti."
  url = f"{SB_URL}/auth/v1/recover"
  try:
    res = requests.post(
        url, json={"email": email}, headers=get_headers(), timeout=10
    )
    if res.status_code in [200, 201]:
      return (
          True,
          "Se l'email esiste, riceverai un link per reimpostare la password.",
      )
    return False, "Impossibile elaborare la richiesta."
  except Exception as e:
    return False, str(e)


def change_user_password(new_password):
  token = st.session_state.get("access_token")
  if not token or not SB_URL:
    return False, "Sessione non valida. Effettua nuovamente il login."
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
    err = res.json().get("msg") or "Errore durante l'aggiornamento."
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
    return True, "Codice valido. Piano Premium attivato con successo."
  return False, "Codice VIP non valido o scaduto."


# Schermata Login / Registrazione
if st.session_state.user is None:
  st.title("VALUE BET ANALYZER")
  st.caption("Accedi per consultare le analisi statistiche e il tuo bankroll")

  auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
  with auth_col2:
    tab_log, tab_reg, tab_rec = st.tabs([
        "Accedi al Tuo Account",
        "Crea Nuovo Account",
        "Password Dimenticata",
    ])

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

    with tab_rec:
      rec_email = st.text_input("Inserisci la tua email", key="rec_email")
      if st.button("INVIA LINK DI RESET", use_container_width=True):
        if rec_email:
          ok, msg = reset_password_request(rec_email)
          if ok:
            st.success(msg)
          else:
            st.error(msg)
        else:
          st.warning("Inserisci l'indirizzo email.")
  st.stop()


# Funzioni Database HTTP per Scommesse Utente
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


# Database Statistico Ponderato Integrato
TEAM_METRICS = {
    "Inter": {
        "att": 1.45,
        "def": 0.65,
        "xg": 2.10,
        "xga": 0.85,
        "shots": 6.2,
        "fouls": 11.0,
        "cards": 1.8,
    },
    "Juventus": {
        "att": 1.15,
        "def": 0.60,
        "xg": 1.55,
        "xga": 0.75,
        "shots": 4.8,
        "fouls": 12.5,
        "cards": 2.1,
    },
    "AC Milan": {
        "att": 1.30,
        "def": 0.90,
        "xg": 1.85,
        "xga": 1.15,
        "shots": 5.4,
        "fouls": 11.8,
        "cards": 2.3,
    },
    "Napoli": {
        "att": 1.25,
        "def": 0.70,
        "xg": 1.75,
        "xga": 0.90,
        "shots": 5.2,
        "fouls": 12.0,
        "cards": 1.9,
    },
    "Atalanta": {
        "att": 1.40,
        "def": 0.95,
        "xg": 2.05,
        "xga": 1.20,
        "shots": 6.0,
        "fouls": 13.5,
        "cards": 2.4,
    },
    "AS Roma": {
        "att": 1.10,
        "def": 0.85,
        "xg": 1.50,
        "xga": 1.05,
        "shots": 4.9,
        "fouls": 12.8,
        "cards": 2.2,
    },
    "Lazio": {
        "att": 1.15,
        "def": 0.90,
        "xg": 1.55,
        "xga": 1.10,
        "shots": 4.7,
        "fouls": 13.0,
        "cards": 2.5,
    },
    "Bologna": {
        "att": 1.05,
        "def": 0.80,
        "xg": 1.40,
        "xga": 0.95,
        "shots": 4.5,
        "fouls": 12.2,
        "cards": 2.0,
    },
    "Fiorentina": {
        "att": 1.10,
        "def": 0.95,
        "xg": 1.45,
        "xga": 1.15,
        "shots": 4.6,
        "fouls": 12.4,
        "cards": 2.1,
    },
    "Torino": {
        "att": 0.90,
        "def": 0.85,
        "xg": 1.15,
        "xga": 1.05,
        "shots": 3.8,
        "fouls": 13.8,
        "cards": 2.3,
    },
    "Manchester City": {
        "att": 1.60,
        "def": 0.60,
        "xg": 2.35,
        "xga": 0.80,
        "shots": 7.1,
        "fouls": 9.5,
        "cards": 1.4,
    },
    "Arsenal": {
        "att": 1.50,
        "def": 0.55,
        "xg": 2.15,
        "xga": 0.70,
        "shots": 6.4,
        "fouls": 10.2,
        "cards": 1.7,
    },
    "Liverpool": {
        "att": 1.55,
        "def": 0.65,
        "xg": 2.25,
        "xga": 0.85,
        "shots": 6.8,
        "fouls": 10.5,
        "cards": 1.6,
    },
    "Chelsea": {
        "att": 1.25,
        "def": 1.00,
        "xg": 1.75,
        "xga": 1.25,
        "shots": 5.2,
        "fouls": 11.5,
        "cards": 2.4,
    },
    "Tottenham Hotspur": {
        "att": 1.35,
        "def": 1.10,
        "xg": 1.90,
        "xga": 1.40,
        "shots": 5.6,
        "fouls": 11.0,
        "cards": 2.3,
    },
    "Newcastle United": {
        "att": 1.20,
        "def": 0.95,
        "xg": 1.65,
        "xga": 1.20,
        "shots": 5.0,
        "fouls": 12.1,
        "cards": 2.0,
    },
    "Aston Villa": {
        "att": 1.25,
        "def": 1.00,
        "xg": 1.70,
        "xga": 1.25,
        "shots": 5.1,
        "fouls": 11.8,
        "cards": 2.2,
    },
    "Manchester United": {
        "att": 1.15,
        "def": 1.10,
        "xg": 1.55,
        "xga": 1.45,
        "shots": 4.8,
        "fouls": 11.2,
        "cards": 2.1,
    },
    "Real Madrid": {
        "att": 1.55,
        "def": 0.65,
        "xg": 2.20,
        "xga": 0.85,
        "shots": 6.7,
        "fouls": 10.0,
        "cards": 1.8,
    },
    "Barcelona": {
        "att": 1.60,
        "def": 0.75,
        "xg": 2.30,
        "xga": 0.95,
        "shots": 6.9,
        "fouls": 10.5,
        "cards": 2.0,
    },
    "Atletico Madrid": {
        "att": 1.25,
        "def": 0.70,
        "xg": 1.70,
        "xga": 0.90,
        "shots": 5.0,
        "fouls": 12.0,
        "cards": 2.2,
    },
    "Bayern Munich": {
        "att": 1.65,
        "def": 0.65,
        "xg": 2.45,
        "xga": 0.85,
        "shots": 7.3,
        "fouls": 9.2,
        "cards": 1.5,
    },
    "Bayer Leverkusen": {
        "att": 1.45,
        "def": 0.70,
        "xg": 2.10,
        "xga": 0.90,
        "shots": 6.3,
        "fouls": 10.1,
        "cards": 1.9,
    },
    "Borussia Dortmund": {
        "att": 1.35,
        "def": 1.00,
        "xg": 1.90,
        "xga": 1.30,
        "shots": 5.7,
        "fouls": 10.8,
        "cards": 1.8,
    },
    "PSG": {
        "att": 1.55,
        "def": 0.70,
        "xg": 2.25,
        "xga": 0.90,
        "shots": 6.8,
        "fouls": 10.0,
        "cards": 1.7,
    },
    "Marseille": {
        "att": 1.20,
        "def": 0.90,
        "xg": 1.65,
        "xga": 1.15,
        "shots": 5.0,
        "fouls": 12.0,
        "cards": 2.2,
    },
    "Monaco": {
        "att": 1.30,
        "def": 1.00,
        "xg": 1.80,
        "xga": 1.25,
        "shots": 5.3,
        "fouls": 11.5,
        "cards": 2.1,
    },
}

DEFAULT_BENCHMARK = {
    "att": 1.00,
    "def": 1.00,
    "xg": 1.35,
    "xga": 1.35,
    "shots": 4.2,
    "fouls": 12.5,
    "cards": 2.2,
}


def get_team_metrics(team_name):
  for name, metrics in TEAM_METRICS.items():
    if name.lower() in team_name.lower() or team_name.lower() in name.lower():
      return metrics
  return DEFAULT_BENCHMARK


class FullDixonColesEngine:

  def __init__(
      self, home_metrics, away_metrics, home_advantage=1.12, rho=-0.11
  ):
    self.rho = rho
    self.lambda_home = (
        home_metrics["att"]
        * away_metrics["def"]
        * home_advantage
        * ((home_metrics["xg"] + away_metrics["xga"]) / 2.7)
    )
    self.lambda_away = (
        away_metrics["att"]
        * home_metrics["def"]
        * ((away_metrics["xg"] + home_metrics["xga"]) / 2.7)
    )

  def tau(self, x, y):
    if x == 0 and y == 0:
      return 1.0 - (self.lambda_home * self.lambda_away * self.rho)
    elif x == 1 and y == 0:
      return 1.0 + (self.lambda_away * self.rho)
    elif x == 0 and y == 1:
      return 1.0 + (self.lambda_home * self.rho)
    elif x == 1 and y == 1:
      return 1.0 - self.rho
    return 1.0

  def generate_score_matrix(self, max_goals=6):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
      for a in range(max_goals + 1):
        p_h = poisson.pmf(h, self.lambda_home)
        p_a = poisson.pmf(a, self.lambda_away)
        matrix[h, a] = self.tau(h, a) * p_h * p_a
    total_p = np.sum(matrix)
    if total_p > 0:
      matrix = matrix / total_p
    return matrix

  def get_probabilities(self):
    matrix = self.generate_score_matrix()
    prob_1 = float(np.sum(np.tril(matrix, -1)))
    prob_x = float(np.sum(np.diag(matrix)))
    prob_2 = float(np.sum(np.triu(matrix, 1)))
    prob_over25 = float(
        np.sum([
            matrix[h, a]
            for h in range(7)
            for a in range(7)
            if h + a > 2.5
        ])
    )
    prob_under25 = 1.0 - prob_over25
    prob_gg = float(
        np.sum([matrix[h, a] for h in range(1, 7) for a in range(1, 7)])
    )
    prob_ng = 1.0 - prob_gg
    return {
        "1": prob_1,
        "X": prob_x,
        "2": prob_2,
        "Over 2.5": prob_over25,
        "Under 2.5": prob_under25,
        "Goal": prob_gg,
        "NoGoal": prob_ng,
    }


class ValueEngine:

  @staticmethod
  def calculate_ev(prob, odds):
    return (prob * odds) - 1.0

  @staticmethod
  def calculate_kelly_stake(prob, odds, bankroll, fraction=0.25):
    b = odds - 1.0
    q = 1.0 - prob
    if b <= 0:
      return 0.0
    f_star = (b * prob - q) / b
    if f_star <= 0:
      return 0.0
    return round(bankroll * f_star * fraction, 2)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_odds_api(api_key, sport_key):
  url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
  try:
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
      remaining = res.headers.get("x-requests-remaining", "N/D")
      return res.json(), remaining, None
    return None, None, f"Errore {res.status_code}: {res.text}"
  except Exception as e:
    return None, None, str(e)


def run_league_scanner(matches, bankroll, kelly_fraction, min_ev):
  detected_opportunities = []
  for match in matches:
    h_team = match.get("home_team")
    a_team = match.get("away_team")
    match_title = f"{h_team} vs {a_team}"
    commence_date = match.get("commence_time", "")[:10]

    h_metrics = get_team_metrics(h_team)
    a_metrics = get_team_metrics(a_team)
    dc = FullDixonColesEngine(h_metrics, a_metrics)
    model_probs = dc.get_probabilities()

    bookmakers = match.get("bookmakers", [])
    h2h_1, h2h_x, h2h_2, ov25, un25 = [], [], [], [], []

    for b in bookmakers:
      for m in b.get("markets", []):
        if m["key"] == "h2h":
          for o in m.get("outcomes", []):
            if o["name"] == h_team:
              h2h_1.append(o["price"])
            elif o["name"] == a_team:
              h2h_2.append(o["price"])
            elif o["name"] == "Draw":
              h2h_x.append(o["price"])
        elif m["key"] == "totals":
          for o in m.get("outcomes", []):
            if o.get("name") == "Over" and o.get("point") == 2.5:
              ov25.append(o["price"])
            elif o.get("name") == "Under" and o.get("point") == 2.5:
              un25.append(o["price"])

    odds_map = {}
    if h2h_1:
      odds_map["1"] = float(np.mean(h2h_1))
    if h2h_x:
      odds_map["X"] = float(np.mean(h2h_x))
    if h2h_2:
      odds_map["2"] = float(np.mean(h2h_2))
    if ov25:
      odds_map["Over 2.5"] = float(np.mean(ov25))
    if un25:
      odds_map["Under 2.5"] = float(np.mean(un25))

    for market, quota in odds_map.items():
      p = model_probs.get(market, 0.0)
      ev = ValueEngine.calculate_ev(p, quota)
      if ev >= min_ev:
        stake = ValueEngine.calculate_kelly_stake(
            p, quota, bankroll, kelly_fraction
        )
        detected_opportunities.append({
            "Partita": match_title,
            "Data": commence_date,
            "Mercato": market,
            "Quota Media": quota,
            "Probabilita": p,
            "EV": ev,
            "Stake": stake,
        })

  detected_opportunities.sort(key=lambda x: x["EV"], reverse=True)
  return detected_opportunities


# Header Applicazione
st.title("VALUE BET ANALYZER")
st.caption("Suite Algoritmica Quantitativa | Modello Dixon-Coles Corretto")

# Sidebar: Utente, Voucher & Metriche
user_email = st.session_state.user.get("email", "")
is_premium = st.session_state.user_tier == "premium"
tier_label = "PIANO PREMIUM (ATTIVO)" if is_premium else "PIANO FREE (DEMO)"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{tier_label}`")

# Box Riscatto Codice VIP per Utenti Free
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
    "Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0
)
kelly_fraction = st.sidebar.slider(
    "Frazione di Kelly", min_value=0.05, max_value=0.50, value=0.25, step=0.05
)
min_ev = (
    st.sidebar.slider(
        "Soglia Minima EV (%)", min_value=1.0, max_value=15.0, value=3.0, step=0.5
    )
    / 100.0
)

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
            <h4 style="margin:0 0 6px 0; color:#10B981;">PIANO FREE ATTIVO (DEMO SERIE A)</h4>
            <p style="margin:0; font-size:0.92rem; color:#D1D5DB;">
                Passa al piano <b>Premium</b> per sbloccare tutti i campionati europei e accedere alle <b>Top 3 Value Bets con EV massimo</b>. Inserisci il tuo codice VIP nella barra laterale per sbloccare tutte le funzioni.
            </p>
        </div>
        """,
      unsafe_allow_html=True,
  )

tab_scanner, tab_bets, tab_account = st.tabs(
    ["Scanner Value Bets", "Registro Scommesse Personale", "Profilo & Sicurezza"]
)

with tab_scanner:
  st.markdown("### SCANNER AUTOMATICO DI GIORNATA")
  col_l, col_btn = st.columns([2, 1])

  with col_l:
    selected_league = st.selectbox(
        "Seleziona Torneo", list(available_leagues.keys()), index=0
    )
    sport_key = available_leagues[selected_league]

  with col_btn:
    st.write("")
    st.write("")
    scan_trigger = st.button("AVVIA SCANNER GIORNATA", use_container_width=True)

  if scan_trigger or "league_matches_cache" not in st.session_state:
    if user_api_key:
      data, rem, err = fetch_odds_api(user_api_key, sport_key)
      if err:
        st.error(f"Errore download API: {err}")
      elif data:
        st.session_state["league_matches_cache"] = data
        st.session_state["api_rem"] = rem
    else:
      st.error("Chiave ODDS_API_KEY non configurata nei Secrets.")

  matches = st.session_state.get("league_matches_cache", [])

  if matches:
    all_value_bets = run_league_scanner(
        matches, current_bankroll, kelly_fraction, min_ev
    )

    st.markdown("---")
    st.markdown("### TOP 5 VALUE BETS RILEVATE")

    if all_value_bets:
      top_5 = all_value_bets[:5]
      table_rows = []

      for idx, bet in enumerate(top_5):
        pos = idx + 1
        if is_premium or pos in [4, 5]:
          table_rows.append({
              "POS": f"#{pos}",
              "PARTITA": bet["Partita"],
              "DATA": bet["Data"],
              "MERCATO": bet["Mercato"],
              "QUOTA": f"{bet['Quota Media']:.2f}",
              "PROBABILITA": f"{bet['Probabilita']*100:.1f}%",
              "EXPECTED VALUE": f"{bet['EV']*100:+.2f}%",
              "STAKE CONSIGLIATO": f"{bet['Stake']:.2f} €",
          })
        else:
          table_rows.append({
              "POS": f"#{pos}",
              "PARTITA": bet["Partita"],
              "DATA": bet["Data"],
              "MERCATO": "[BLOCCATO - PIANO PREMIUM]",
              "QUOTA": "---",
              "PROBABILITA": "---",
              "EXPECTED VALUE": "---",
              "STAKE CONSIGLIATO": "---",
          })

      st.table(pd.DataFrame(table_rows))

      st.markdown("### REGISTRA GIOCATA NEL TUO BANKROLL")
      col_reg1, col_reg2 = st.columns([3, 1])
      with col_reg1:
        bet_options = [
            f"#{i+1} | {b['Partita']} | {b['Mercato']} @ {b['Quota Media']:.2f} (Stake: {b['Stake']:.2f} €)"
            for i, b in enumerate(top_5)
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
              for i, b in enumerate(top_5)
              if is_premium or (i + 1) in [4, 5]
          ][selected_bet_idx]
          save_user_bet(
              st.session_state.user.get("id"),
              chosen["Partita"],
              chosen["Mercato"],
              chosen["Quota Media"],
              chosen["Stake"],
              chosen["EV"],
          )
          st.success("Scommessa registrata con successo.")
          st.rerun()
    else:
      st.info("Nessuna giocata di valore rilevata per questo turno.")

with tab_bets:
  st.markdown("### STORICO PERSONALE SCOMMESSE")
  user_bets = fetch_user_bets(st.session_state.user.get("id"))

  if not user_bets.empty:
    st.dataframe(user_bets, use_container_width=True)

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
      st.info("Non hai scommesse in corso.")
  else:
    st.info("Non hai ancora salvato alcuna scommessa.")

with tab_account:
  st.markdown("### DETTAGLI ACCOUNT")
  st.markdown(f"**Email di Registrazione:** `{user_email}`")
  st.markdown(f"**ID Utente Supabase:** `{st.session_state.user.get('id')}`")
  st.markdown(
      f"**Piano di Abbonamento Attuale:** `{'PREMIUM' if is_premium else 'FREE'}`"
  )

  st.markdown("---")
  st.markdown("### MODIFICA PASSWORD DI ACCESSO")

  acc_c1, acc_c2 = st.columns(2)
  with acc_c1:
    new_pwd = st.text_input(
        "Nuova Password (min. 6 caratteri)", type="password"
    )
  with acc_c2:
    conf_pwd = st.text_input("Conferma Nuova Password", type="password")

  if st.button("AGGIORNA PASSWORD", use_container_width=False):
    if not new_pwd or len(new_pwd) < 6:
      st.error("La password deve contenere almeno 6 caratteri.")
    elif new_pwd != conf_pwd:
      st.error("Le password inserite non coincidono.")
    else:
      ok, msg = change_user_password(new_pwd)
      if ok:
        st.success(msg)
      else:
        st.error(msg)
