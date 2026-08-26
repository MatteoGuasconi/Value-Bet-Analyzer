import datetime
import numpy as np
import pandas as pd
import requests
import streamlit as st
from scipy.stats import poisson

# Configurazione della pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER | QUANTITATIVE BETTING SUITE",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS: Tema Dark Fintech ad alto impatto visivo
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0A0E17;
        color: #F3F4F6;
    }
    
    /* Header e Titoli */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    
    /* Card Container */
    .metric-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
    }
    
    .badge-value {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid #10B981;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .badge-no-value {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 4px;
        border: 1px solid #EF4444;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Bottoni */
    .stButton>button {
        background-color: #10B981;
        color: #064E3B;
        font-weight: 600;
        border-radius: 6px;
        border: none;
        padding: 10px 24px;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        background-color: #059669;
        color: #FFFFFF;
    }
    
    /* Tabelle */
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
    
    tbody tr:hover {
        background-color: #1E293B !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inizializzazione Storico Scommesse
if "bet_history" not in st.session_state:
  st.session_state.bet_history = pd.DataFrame(
      columns=[
          "Data",
          "Partita",
          "Mercato",
          "Quota",
          "Stake (€)",
          "Probabilita IA",
          "EV (%)",
          "Esito",
          "Profitto (€)",
      ]
  )

# Database Statistico Ponderato Integrato (Top Leghe)
TEAM_METRICS = {
    # Serie A
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
    # Premier League
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
    # La Liga
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
    # Bundesliga
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
    # Ligue 1
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


# Motore Matematico Avanzato Dixon-Coles con Matrice Tau (tau)
class FullDixonColesEngine:

  def __init__(
      self, home_metrics, away_metrics, home_advantage=1.12, rho=-0.11
  ):
    self.rho = rho
    # Calcolo intensita di gol attesi (lambda e mu)
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
    else:
      return 1.0

  def generate_score_matrix(self, max_goals=6):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
      for a in range(max_goals + 1):
        p_h = poisson.pmf(h, self.lambda_home)
        p_a = poisson.pmf(a, self.lambda_away)
        matrix[h, a] = self.tau(h, a) * p_h * p_a

    # Normalizzazione probabilistica per somma pari a 1
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


# Funzione Recupero Dati da The Odds API
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


# Header Istituzionale
st.title("QUANTITATIVE VALUE BET ANALYZER")
st.caption("Modello Dixon-Coles Corretto | Analisi Statistica e Value Detection")

# Barra Laterale: Parametri Finanziari & Credenziali
st.sidebar.markdown("### AUTENTICAZIONE")
app_pwd = st.secrets.get("APP_PASSWORD", "")
user_pwd = st.sidebar.text_input(
    "Password Accesso", type="password", placeholder="Inserisci credenziali..."
)

if app_pwd and user_pwd != app_pwd:
  st.sidebar.warning("Inserisci la password per sbloccare l'applicazione.")
  st.warning("Accesso Riservato. Inserisci la password nella barra laterale.")
  st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("### GESTIONE DEL CAPITALE")
bankroll = st.sidebar.number_input(
    "Bankroll Operativo (€)", min_value=10.0, value=1000.0, step=50.0
)
kelly_fraction = st.sidebar.slider(
    "Frazione di Kelly",
    min_value=0.05,
    max_value=0.50,
    value=0.25,
    step=0.05,
    help="Valore raccomandato: 0.25 (Quarter Kelly)",
)
min_ev = (
    st.sidebar.slider(
        "Soglia Minima EV (%)", min_value=1.0, max_value=15.0, value=3.0, step=0.5
    )
    / 100.0
)

user_api_key = st.secrets.get("ODDS_API_KEY", "")

# Struttura Campionati
LEAGUE_KEYS = {
    "Serie A (Italia)": "soccer_italy_serie_a",
    "Premier League (Inghilterra)": "soccer_epl",
    "La Liga (Spagna)": "soccer_spain_la_liga",
    "Bundesliga (Germania)": "soccer_germany_bundesliga",
    "Ligue 1 (Francia)": "soccer_france_ligue_one",
    "Champions League": "soccer_uefa_champs_league",
    "Europa League": "soccer_uefa_europa_league",
}

# Sezione Principale: Analisi Turno
st.markdown("### SELEZIONE CAMPIONATO & DOWNLOAD AUTOMATICO")
col_sel1, col_sel2 = st.columns([2, 1])

with col_sel1:
  selected_league = st.selectbox(
      "Seleziona Torneo", list(LEAGUE_KEYS.keys()), index=0
  )
  sport_key = LEAGUE_KEYS[selected_league]

with col_sel2:
  st.write("")
  st.write("")
  sync_btn = st.button("AGGIORNA QUOTE E STATISTICHE", use_container_width=True)

if sync_btn or "cached_matches" not in st.session_state:
  if user_api_key:
    data, rem, err = fetch_odds_api(user_api_key, sport_key)
    if err:
      st.error(f"Errore download API: {err}")
    elif data:
      st.session_state["cached_matches"] = data
      st.session_state["cached_rem"] = rem
      st.success(f"Dati caricati con successo. Chiamate API rimanenti: {rem}")
  else:
    st.error("Chiave ODDS_API_KEY non rilevata nei Secrets.")

matches_data = st.session_state.get("cached_matches", [])

if matches_data:
  st.markdown("---")
  st.markdown("### ANALISI DETTAGLIATA INCONTRO")

  match_labels = [
      f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('commence_time', '')[:10]})"
      for m in matches_data
  ]
  selected_label = st.selectbox("Seleziona Partita in Palinsesto", match_labels)
  chosen_match = next(
      m
      for m in matches_data
      if f"{m.get('home_team')} vs {m.get('away_team')} ({m.get('commence_time', '')[:10]})"
      == selected_label
  )

  h_team = chosen_match.get("home_team")
  a_team = chosen_match.get("away_team")

  # Recupero metriche statistiche automatiche
  h_metrics = get_team_metrics(h_team)
  a_metrics = get_team_metrics(a_team)

  # Calcolo probabilita Dixon-Coles con matrice Tau
  dc = FullDixonColesEngine(h_metrics, a_metrics)
  model_probs = dc.get_probabilities()

  # Estrazione quote medie dai bookmaker
  bookmakers = chosen_match.get("bookmakers", [])
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

  q_1 = float(np.mean(h2h_1)) if h2h_1 else 2.10
  q_x = float(np.mean(h2h_x)) if h2h_x else 3.30
  q_2 = float(np.mean(h2h_2)) if h2h_2 else 3.50
  q_ov25 = float(np.mean(ov25)) if ov25 else 1.95
  q_un25 = float(np.mean(un25)) if un25 else 1.85

  odds_map = {
      "1": q_1,
      "X": q_x,
      "2": q_2,
      "Over 2.5": q_ov25,
      "Under 2.5": q_un25,
  }

  # Analisi di Valore e Stake Kelly
  results_rows = []
  for market, quota in odds_map.items():
    p = model_probs[market]
    ev = ValueEngine.calculate_ev(p, quota)
    stake = (
        ValueEngine.calculate_kelly_stake(p, quota, bankroll, kelly_fraction)
        if ev >= min_ev
        else 0.0
    )
    is_val = ev >= min_ev

    results_rows.append({
        "MERCATO": market,
        "PROBABILITA STIMATA": f"{p*100:.1f}%",
        "QUOTA MEDIA": f"{quota:.2f}",
        "EXPECTED VALUE": f"{ev*100:+.2f}%",
        "STAKE CONSIGLIATO": f"{stake:.2f} €" if is_val else "0.00 €",
        "STATUS": "VALORE" if is_val else "NO VALORE",
    })

  # Visualizzazione Risultati Tabellari
  st.table(pd.DataFrame(results_rows))

  # Note Tecniche sull'Incontro
  col_info1, col_info2 = st.columns(2)
  with col_info1:
    st.markdown(
        f"""
        <div class="metric-card">
            <h4 style="margin-top:0;">{h_team} (CASA)</h4>
            <p>Indice Efficienza Offensiva: <b>{h_metrics['att']:.2f}x</b></p>
            <p>Indice Concessione Difensiva: <b>{h_metrics['def']:.2f}x</b></p>
            <p>xG Medio Atteso: <b>{h_metrics['xg']:.2f}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with col_info2:
    st.markdown(
        f"""
        <div class="metric-card">
            <h4 style="margin-top:0;">{a_team} (TRASFERTA)</h4>
            <p>Indice Efficienza Offensiva: <b>{a_metrics['att']:.2f}x</b></p>
            <p>Indice Concessione Difensiva: <b>{a_metrics['def']:.2f}x</b></p>
            <p>xG Medio Atteso: <b>{a_metrics['xg']:.2f}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
  st.info(
      "Nessun evento caricato. Clicca sul pulsante 'AGGIORNA QUOTE E"
      " STATISTICHE' per interrogare il palinsesto."
  )
