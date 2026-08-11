import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from scipy.stats import poisson

st.set_page_config(
    page_title='VALUE BET ANALYZER - LIVE ODDS API', layout='wide'
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stButton>button {
        font-weight: bold;
        border-radius: 6px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if 'bet_history' not in st.session_state:
  st.session_state.bet_history = pd.DataFrame(
      columns=[
          'Data',
          'Partita',
          'Mercato',
          'Quota',
          'Stake (€)',
          'Probabilita IA',
          'EV (%)',
          'Esito',
          'Profitto (€)',
      ]
  )


def calculate_weighted_avg(season_avg, l5_avg, weight_l5):
  return (l5_avg * weight_l5) + (season_avg * (1.0 - weight_l5))


class AdvancedDixonColesEngine:

  def __init__(
      self,
      goals_h,
      g_against_a,
      xg_h,
      xga_a,
      goals_a,
      g_against_h,
      xg_a,
      xga_h,
      home_advantage=1.10,
  ):
    att_h = (goals_h + xg_h) / 2.0
    def_a = (g_against_a + xga_a) / 2.0
    att_a = (goals_a + xg_a) / 2.0
    def_h = (g_against_h + xga_h) / 2.0
    self.lambda_home = att_h * def_a * home_advantage
    self.lambda_away = att_a * def_h

  def generate_score_matrix(self, max_goals=6):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
      for a in range(max_goals + 1):
        prob_h = poisson.pmf(h, self.lambda_home)
        prob_a = poisson.pmf(a, self.lambda_away)
        matrix[h, a] = prob_h * prob_a
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
    prob_home_over15 = 1.0 - float(poisson.cdf(1, self.lambda_home))
    prob_away_over15 = 1.0 - float(poisson.cdf(1, self.lambda_away))
    return {
        '1': prob_1,
        'X': prob_x,
        '2': prob_2,
        'Over 2.5': prob_over25,
        'Under 2.5': prob_under25,
        'Goal': prob_gg,
        'NoGoal': prob_ng,
        'Over 1.5 Team Casa': prob_home_over15,
        'Over 1.5 Team Trasferta': prob_away_over15,
    }


class PoissonStatEngine:

  def __init__(self, stat_home, stat_away):
    self.lambda_home = stat_home
    self.lambda_away = stat_away
    self.lambda_total = stat_home + stat_away

  def get_over_prob(self, threshold, scope='total'):
    lam = (
        self.lambda_total
        if scope == 'total'
        else (self.lambda_home if scope == 'home' else self.lambda_away)
    )
    return 1.0 - float(poisson.cdf(int(threshold), lam))


class PlayerEngine:

  @staticmethod
  def get_player_over_prob(avg_stat, threshold, opp_difficulty_factor=1.0):
    adjusted_avg = avg_stat * opp_difficulty_factor
    return 1.0 - float(poisson.cdf(int(threshold), adjusted_avg))


class ValueEngine:

  @staticmethod
  def calculate_ev(prob, odds):
    return (prob * odds) - 1.0

  @staticmethod
  def calculate_kelly_stake(prob, odds, bankroll, fraction=0.25):
    b = odds - 1.0
    q = 1.0 - prob
    f_star = (b * prob - q) / b
    if f_star <= 0:
      return 0.0
    return round(bankroll * f_star * fraction, 2)


def fetch_odds_api(
    api_key, sport_key='soccer_italy_serie_a', regions='eu', markets='h2h,totals'
):
  url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions={regions}&markets={markets}&oddsFormat=decimal'
  try:
    res = requests.get(url, timeout=10)
    if res.status_code == 200:
      remaining = res.headers.get('x-requests-remaining', 'N/D')
      used = res.headers.get('x-requests-used', 'N/D')
      return res.json(), remaining, used, None
    else:
      return None, None, None, f'Errore API {res.status_code}: {res.text}'
  except Exception as e:
    return None, None, None, str(e)


st.title('VALUE BET ANALYZER + LIVE ODDS API')

st.sidebar.header('Parametri Generali & Rischio')
bankroll = st.sidebar.number_input(
    'Bankroll Totale (€)', min_value=10.0, value=1000.0, step=50.0
)
kelly_fraction = st.sidebar.slider(
    'Frazione di Kelly', min_value=0.05, max_value=1.0, value=0.25, step=0.05
)
min_ev = (
    st.sidebar.slider(
        'EV Minimo Richiesto (%)',
        min_value=1.0,
        max_value=15.0,
        value=3.0,
        step=0.5,
    )
    / 100.0
)

st.sidebar.header('Configurazione API')
user_api_key = st.sidebar.text_input(
    'The Odds API Key',
    value='82853c1071fbb31d273ace40cf209de4',
    type='password',
)

st.sidebar.header('Ponderazione Forma Recente')
weight_l5 = st.sidebar.slider(
    'Peso Ultime 5 Partite vs Stagione',
    min_value=0.0,
    max_value=1.0,
    value=0.70,
    step=0.05,
)

tab1, tab2, tab3 = st.tabs([
    'Analisi Squadre & Live Odds',
    'Analisi Giocatori',
    'Registro Scommesse & Dashboard',
])

LEAGUE_KEYS = {
    'Serie A (Italia)': 'soccer_italy_serie_a',
    'Premier League (Inghilterra)': 'soccer_epl',
    'La Liga (Spagna)': 'soccer_spain_la_liga',
    'Bundesliga (Germania)': 'soccer_germany_bundesliga',
    'Ligue 1 (Francia)': 'soccer_france_ligue_one',
    'Champions League': 'soccer_uefa_champs_league',
    'Europa League': 'soccer_uefa_europa_league',
}

with tab1:
  st.header('1. Selezione Partita & Download Quote in Tempo Reale')

  col_ap1, col_ap2 = st.columns([1, 2])
  with col_ap1:
    selected_league_name = st.selectbox(
        'Seleziona Campionato', list(LEAGUE_KEYS.keys()), index=0
    )
    sport_key = LEAGUE_KEYS[selected_league_name]
    fetch_btn = st.button('Sincronizza Partite & Quote Live')

  default_q1, default_qx, default_q2, default_qover25 = 2.10, 3.40, 3.60, 1.90

  if fetch_btn or 'api_data_cache' not in st.session_state:
    if user_api_key:
      data, rem, used, err = fetch_odds_api(user_api_key, sport_key)
      if err:
        st.error(f"Impossibile recuperare dati dall'API: {err}")
      elif data:
        st.session_state['api_data_cache'] = data
        st.session_state['api_data_rem'] = rem
        st.session_state['api_data_used'] = used
        st.success(f'Partite aggiornate! Chiamate API rimanenti: {rem}')
    else:
      st.warning('Inserisci una chiave API valida nel menu a sinistra.')

  api_matches = st.session_state.get('api_data_cache', [])
  rem_calls = st.session_state.get('api_data_rem', 'N/D')

  match_options = []
  match_dict = {}

  for m in api_matches:
    h_team = m.get('home_team')
    a_team = m.get('away_team')
    commence_time = m.get('commence_time', '')[:16].replace('T', ' ')
    label = f'{h_team} vs {a_team} ({commence_time})'
    match_options.append(label)
    match_dict[label] = m

  col_m1, col_m2 = st.columns(2)
  with col_m1:
    if match_options:
      selected_match_label = st.selectbox(
          'Scegli Partita dai Dati Live API', match_options
      )
      chosen_match = match_dict[selected_match_label]
      home_team = chosen_match.get('home_team', 'Squadra Casa')
      away_team = chosen_match.get('away_team', 'Squadra Trasferta')

      bookmakers = chosen_match.get('bookmakers', [])
      h2h_1_list, h2h_x_list, h2h_2_list, over25_list = [], [], [], []
      for b in bookmakers:
        for market in b.get('markets', []):
          if market['key'] == 'h2h':
            for outcome in market.get('outcomes', []):
              if outcome['name'] == home_team:
                h2h_1_list.append(outcome['price'])
              elif outcome['name'] == away_team:
                h2h_2_list.append(outcome['price'])
              elif outcome['name'] == 'Draw':
                h2h_x_list.append(outcome['price'])
          elif market['key'] == 'totals':
            for outcome in market.get('outcomes', []):
              if outcome.get('name') == 'Over' and outcome.get('point') == 2.5:
                over25_list.append(outcome['price'])

      if h2h_1_list:
        default_q1 = round(float(np.mean(h2h_1_list)), 2)
      if h2h_x_list:
        default_qx = round(float(np.mean(h2h_x_list)), 2)
      if h2h_2_list:
        default_q2 = round(float(np.mean(h2h_2_list)), 2)
      if over25_list:
        default_qover25 = round(float(np.mean(over25_list)), 2)

      st.info(
          f'Partita: **{home_team} vs {away_team}** (Dati recuperati da'
          f' {len(bookmakers)} bookmaker)'
      )
    else:
      st.warning(
          'Nessun match caricato o palinsesto non disponibile. Inserimento'
          ' manuale attivo.'
      )
      home_team = st.text_input('Squadra in Casa', 'Inter')
      away_team = st.text_input('Squadra in Trasferta', 'Juventus')

  with col_m2:
    st.write('**Personalizza Nomi Squadre** (facoltativo)')
    custom_h = st.text_input('Nome Casa', value=home_team)
    custom_a = st.text_input('Nome Trasferta', value=away_team)
    home_team, away_team = custom_h, custom_a

  match_name = f'{home_team} vs {away_team}'

  col_h, col_a = st.columns(2)
  with col_h:
    st.subheader(f'{home_team} (Casa)')
    g_h_season = st.number_input(
        f'Gol Medi Fatti Stagione {home_team}', value=1.70, step=0.05
    )
    g_h_l5 = st.number_input(
        f'Gol Medi Fatti L5 {home_team}', value=1.90, step=0.05
    )
    ga_h_season = st.number_input(
        f'Gol Medi Subiti Stagione {home_team}', value=0.85, step=0.05
    )
    ga_h_l5 = st.number_input(
        f'Gol Medi Subiti L5 {home_team}', value=0.75, step=0.05
    )
    xg_h_season = st.number_input(
        f'xG Medio Stagione {home_team}', value=1.65, step=0.05
    )
    xg_h_l5 = st.number_input(
        f'xG Medio L5 {home_team}', value=1.85, step=0.05
    )
    xga_h_season = st.number_input(
        f'xGA Subiti Stagione {home_team}', value=0.90, step=0.05
    )
    xga_h_l5 = st.number_input(
        f'xGA Subiti L5 {home_team}', value=0.80, step=0.05
    )
    shots_h_season = st.number_input(
        f'Tiri Porta Stagione {home_team}', value=5.1, step=0.1
    )
    shots_h_l5 = st.number_input(
        f'Tiri Porta L5 {home_team}', value=5.8, step=0.1
    )
    saves_h_season = st.number_input(
        f'Parate Stagione {home_team}', value=3.2, step=0.1
    )
    saves_h_l5 = st.number_input(f'Parate L5 {home_team}', value=3.5, step=0.1)
    cards_h_season = st.number_input(
        f'Cartellini Stagione {home_team}', value=2.1, step=0.1
    )
    cards_h_l5 = st.number_input(
        f'Cartellini L5 {home_team}', value=2.4, step=0.1
    )
    fouls_h_season = st.number_input(
        f'Falli Commessi Stagione {home_team}', value=12.5, step=0.5
    )
    fouls_h_l5 = st.number_input(
        f'Falli Commessi L5 {home_team}', value=13.0, step=0.5
    )
    corners_h_season = st.number_input(
        f'Corner Stagione {home_team}', value=5.5, step=0.1
    )
    corners_h_l5 = st.number_input(
        f'Corner L5 {home_team}', value=6.0, step=0.1
    )

  with col_a:
    st.subheader(f'{away_team} (Trasferta)')
    g_a_season = st.number_input(
        f'Gol Medi Fatti Stagione {away_team}', value=1.20, step=0.05
    )
    g_a_l5 = st.number_input(
        f'Gol Medi Fatti L5 {away_team}', value=1.35, step=0.05
    )
    ga_a_season = st.number_input(
        f'Gol Medi Subiti Stagione {away_team}', value=1.25, step=0.05
    )
    ga_a_l5 = st.number_input(
        f'Gol Medi Subiti L5 {away_team}', value=1.15, step=0.05
    )
    xg_a_season = st.number_input(
        f'xG Medio Stagione {away_team}', value=1.30, step=0.05
    )
    xg_a_l5 = st.number_input(
        f'xG Medio L5 {away_team}', value=1.45, step=0.05
    )
    xga_a_season = st.number_input(
        f'xGA Subiti Stagione {away_team}', value=1.20, step=0.05
    )
    xga_a_l5 = st.number_input(
        f'xGA Subiti L5 {away_team}', value=1.10, step=0.05
    )
    shots_a_season = st.number_input(
        f'Tiri Porta Stagione {away_team}', value=4.0, step=0.1
    )
    shots_a_l5 = st.number_input(
        f'Tiri Porta L5 {away_team}', value=4.5, step=0.1
    )
    saves_a_season = st.number_input(
        f'Parate Stagione {away_team}', value=2.8, step=0.1
    )
    saves_a_l5 = st.number_input(f'Parate L5 {away_team}', value=3.1, step=0.1)
    cards_a_season = st.number_input(
        f'Cartellini Stagione {away_team}', value=2.5, step=0.1
    )
    cards_a_l5 = st.number_input(
        f'Cartellini L5 {away_team}', value=2.8, step=0.1
    )
    fouls_a_season = st.number_input(
        f'Falli Commessi Stagione {away_team}', value=13.5, step=0.5
    )
    fouls_a_l5 = st.number_input(
        f'Falli Commessi L5 {away_team}', value=14.2, step=0.5
    )
    corners_a_season = st.number_input(
        f'Corner Stagione {away_team}', value=4.2, step=0.1
    )
    corners_a_l5 = st.number_input(
        f'Corner L5 {away_team}', value=4.5, step=0.1
    )

  st.header('2. Modulo Severità Arbitro')
  col_r1, col_r2 = st.columns(2)
  with col_r1:
    ref_cards = st.number_input('Media Cartellini Arbitro', value=4.5, step=0.1)
  with col_r2:
    ref_fouls = st.number_input(
        'Media Falli Fischiati Arbitro', value=25.5, step=0.5
    )

  st.header('3. Quote Bookmaker (Compilate da API o Personalizzate)')
  q_c1, q_c2, q_c3, q_c4 = st.columns(4)
  with q_c1:
    st.write('**1X2 & Gol Totali**')
    q_1 = st.number_input('Quota 1', value=default_q1, step=0.05)
    q_x = st.number_input('Quota X', value=default_qx, step=0.05)
    q_2 = st.number_input('Quota 2', value=default_q2, step=0.05)
    q_over25 = st.number_input(
        'Quota Over 2.5', value=default_qover25, step=0.05
    )
  with q_c2:
    st.write('**Gol Squadre**')
    q_team_h_over15 = st.number_input(
        f'Quota Over 1.5 {home_team}', value=2.00, step=0.05
    )
    q_team_a_over15 = st.number_input(
        f'Quota Over 1.5 {away_team}', value=2.60, step=0.05
    )
    q_gg = st.number_input('Quota Goal', value=1.75, step=0.05)
  with q_c3:
    st.write('**Tiri & Parate**')
    q_shots_tot_over85 = st.number_input(
        'Quota Tiri Porta Over 8.5', value=1.85, step=0.05
    )
    q_saves_tot_over55 = st.number_input(
        'Quota Parate Over 5.5', value=1.90, step=0.05
    )
  with q_c4:
    st.write('**Disciplinari & Corner**')
    q_cards_tot_over45 = st.number_input(
        'Quota Cartellini Over 4.5', value=1.85, step=0.05
    )
    q_fouls_tot_over265 = st.number_input(
        'Quota Falli Over 26.5', value=1.80, step=0.05
    )
    q_corners_tot_over85 = st.number_input(
        'Quota Corner Over 8.5', value=1.85, step=0.05
    )

  if st.button('Esegui Analisi Squadre', type='primary'):
    w_g_h = calculate_weighted_avg(g_h_season, g_h_l5, weight_l5)
    w_ga_h = calculate_weighted_avg(ga_h_season, ga_h_l5, weight_l5)
    w_xg_h = calculate_weighted_avg(xg_h_season, xg_h_l5, weight_l5)
    w_xga_h = calculate_weighted_avg(xga_h_season, xga_h_l5, weight_l5)

    w_g_a = calculate_weighted_avg(g_a_season, g_a_l5, weight_l5)
    w_ga_a = calculate_weighted_avg(ga_a_season, ga_a_l5, weight_l5)
    w_xg_a = calculate_weighted_avg(xg_a_season, xg_a_l5, weight_l5)
    w_xga_a = calculate_weighted_avg(xga_a_season, xga_a_l5, weight_l5)

    w_shots_h = calculate_weighted_avg(shots_h_season, shots_h_l5, weight_l5)
    w_shots_a = calculate_weighted_avg(shots_a_season, shots_a_l5, weight_l5)
    w_saves_h = calculate_weighted_avg(saves_h_season, saves_h_l5, weight_l5)
    w_saves_a = calculate_weighted_avg(saves_a_season, saves_a_l5, weight_l5)
    w_cards_h = calculate_weighted_avg(cards_h_season, cards_h_l5, weight_l5)
    w_cards_a = calculate_weighted_avg(cards_a_season, cards_a_l5, weight_l5)
    w_fouls_h = calculate_weighted_avg(fouls_h_season, fouls_h_l5, weight_l5)
    w_fouls_a = calculate_weighted_avg(fouls_a_season, fouls_a_l5, weight_l5)
    w_corners_h = calculate_weighted_avg(
        corners_h_season, corners_h_l5, weight_l5
    )
    w_corners_a = calculate_weighted_avg(
        corners_a_season, corners_a_l5, weight_l5
    )

    dc_engine = AdvancedDixonColesEngine(
        w_g_h, w_ga_a, w_xg_h, w_xga_a, w_g_a, w_ga_h, w_xg_a, w_xga_h
    )
    probs = dc_engine.get_probabilities()

    shots_engine = PoissonStatEngine(w_shots_h, w_shots_a)
    probs['Tiri Porta Over 8.5'] = shots_engine.get_over_prob(8.5, 'total')

    saves_engine = PoissonStatEngine(w_saves_h, w_saves_a)
    probs['Parate Over 5.5'] = saves_engine.get_over_prob(5.5, 'total')

    corners_engine = PoissonStatEngine(w_corners_h, w_corners_a)
    probs['Corner Over 8.5'] = corners_engine.get_over_prob(8.5, 'total')

    adj_cards_total = (w_cards_h + w_cards_a + ref_cards) / 2.0
    adj_fouls_total = (w_fouls_h + w_fouls_a + ref_fouls) / 2.0

    probs['Cartellini Over 4.5'] = 1.0 - float(poisson.cdf(4, adj_cards_total))
    probs['Falli Over 26.5'] = 1.0 - float(poisson.cdf(26, adj_fouls_total))

    odds_dict = {
        '1': q_1,
        'X': q_x,
        '2': q_2,
        'Over 2.5': q_over25,
        'Goal': q_gg,
        f'Over 1.5 Team {home_team}': q_team_h_over15,
        f'Over 1.5 Team {away_team}': q_team_a_over15,
        'Tiri Porta Over 8.5': q_shots_tot_over85,
        'Parate Over 5.5': q_saves_tot_over55,
        'Cartellini Over 4.5': q_cards_tot_over45,
        'Falli Over 26.5': q_fouls_tot_over265,
        'Corner Over 8.5': q_corners_tot_over85,
    }

    market_groups = {
        '1': 'Esito',
        'X': 'Esito',
        '2': 'Esito',
        'Over 2.5': 'Gol_Match',
        'Goal': 'Gol_Match',
        f'Over 1.5 Team {home_team}': 'Gol_Match',
        f'Over 1.5 Team {away_team}': 'Gol_Match',
        'Tiri Porta Over 8.5': 'Tiri',
        'Parate Over 5.5': 'Tiri',
        'Cartellini Over 4.5': 'Arbitro',
        'Falli Over 26.5': 'Arbitro',
        'Corner Over 8.5': 'Corner',
    }

    all_rows, raw_value_rows = [], []
    for market, odds in odds_dict.items():
      key_prob = (
          market
          if market in probs
          else market.replace(f'Team {home_team}', 'Team Casa').replace(
              f'Team {away_team}', 'Team Trasferta'
          )
      )
      if key_prob in probs:
        p = probs[key_prob]
        ev = ValueEngine.calculate_ev(p, odds)
        stake = ValueEngine.calculate_kelly_stake(
            p, odds, bankroll, kelly_fraction
        )
        is_value = ev >= min_ev
        row = {
            'Partita': match_name,
            'Mercato': market,
            'Probabilita IA': f'{p*100:.2f}%',
            'Quota Bookmaker': odds,
            'Valore Atteso (EV)': f'{ev*100:.2f}%',
            'Stake Consigliato (€)': stake if is_value else 0.0,
            'Esito Valore': 'VALORE' if is_value else 'NO VALORE',
            'raw_prob': p,
            'raw_ev': ev,
            'raw_stake': stake,
        }
        all_rows.append(row)
        if is_value:
          raw_value_rows.append(row)

    raw_value_rows.sort(key=lambda x: x['raw_ev'], reverse=True)
    final_value_rows = []
    seen_groups = set()

    for r in raw_value_rows:
      group = market_groups.get(r['Mercato'])
      if group not in seen_groups:
        final_value_rows.append(r)
        seen_groups.add(group)

    st.header('Risultati Analisi Partita')
    st.subheader(
        f'Migliori Giocate di Valore Selezionate: {len(final_value_rows)}'
    )

    if len(final_value_rows) > 0:
      df_val = pd.DataFrame(final_value_rows)
      st.table(df_val[[
          'Partita',
          'Mercato',
          'Probabilita IA',
          'Quota Bookmaker',
          'Valore Atteso (EV)',
          'Stake Consigliato (€)',
      ]])
    else:
      st.warning(
          'Nessuna giocata supera la soglia di valore atteso impostata.'
      )

    st.subheader('Tabelle Complete Tutti i Mercati (Non Filtrati)')
    st.table(
        pd.DataFrame(all_rows)[[
            'Mercato',
            'Probabilita IA',
            'Quota Bookmaker',
            'Valore Atteso (EV)',
            'Esito Valore',
        ]]
    )

with tab2:
  st.header('Analisi Statistica Singoli Giocatori e Contesto Avversario')
  col_p_ctx1, col_p_ctx2 = st.columns(2)
  with col_p_ctx1:
    p_team = st.selectbox(
        'Squadra del Giocatore', [home_team, away_team], index=0
    )
  with col_p_ctx2:
    opp_team = away_team if p_team == home_team else home_team
    st.info(f'Avversario affrontato: **{opp_team}**')

  opp_tier = st.select_slider(
      f'Livello Difensivo / Difficoltà Avversario ({opp_team})',
      options=[
          'Molto Facile (es. neopromossa)',
          'Medio-Bassa',
          'Standard',
          'Medio-Alta',
          'Top Club / Difesa Chiusa',
      ],
      value='Standard',
  )
  diff_factors = {
      'Molto Facile (es. neopromossa)': 1.25,
      'Medio-Bassa': 1.10,
      'Standard': 1.00,
      'Medio-Alta': 0.88,
      'Top Club / Difesa Chiusa': 0.75,
  }
  chosen_factor = diff_factors[opp_tier]

  p_col1, p_col2 = st.columns(2)
  with p_col1:
    player_name = st.text_input('Nome Giocatore', 'Lautaro Martinez')
    p_shots_season = st.number_input(
        'Media Tiri in Porta Stagionale', value=1.40, step=0.1
    )
    p_shots_l5 = st.number_input('Media Tiri in Porta L5', value=1.80, step=0.1)
    p_fouls_c_season = st.number_input(
        'Media Falli Commessi Stagionale', value=1.10, step=0.1
    )
    p_fouls_c_l5 = st.number_input(
        'Media Falli Commessi L5', value=1.50, step=0.1
    )

  with p_col2:
    st.write('**Quote Giocatore Bookmaker**')
    q_p_shot05 = st.number_input(
        'Quota Tiri Porta Over 0.5 Giocatore', value=1.45, step=0.05
    )
    q_p_shot15 = st.number_input(
        'Quota Tiri Porta Over 1.5 Giocatore', value=2.20, step=0.05
    )
    q_p_foul15 = st.number_input(
        'Quota Falli Commessi Over 1.5', value=1.90, step=0.05
    )

  if st.button('Analizza Giocatore', type='primary'):
    w_p_shots = calculate_weighted_avg(p_shots_season, p_shots_l5, weight_l5)
    w_p_fouls_c = calculate_weighted_avg(
        p_fouls_c_season, p_fouls_c_l5, weight_l5
    )
    prob_shot05 = PlayerEngine.get_player_over_prob(
        w_p_shots, 0.5, chosen_factor
    )
    prob_shot15 = PlayerEngine.get_player_over_prob(
        w_p_shots, 1.5, chosen_factor
    )
    prob_foul15 = PlayerEngine.get_player_over_prob(
        w_p_fouls_c, 1.5, chosen_factor
    )

    player_results = [
        {
            'Mercato Giocatore': f'{player_name} Over 0.5 Tiri Porta',
            'Probabilita IA': prob_shot05,
            'Quota': q_p_shot05,
        },
        {
            'Mercato Giocatore': f'{player_name} Over 1.5 Tiri Porta',
            'Probabilita IA': prob_shot15,
            'Quota': q_p_shot15,
        },
        {
            'Mercato Giocatore': f'{player_name} Over 1.5 Falli Commessi',
            'Probabilita IA': prob_foul15,
            'Quota': q_p_foul15,
        },
    ]

    p_rows = []
    for pr in player_results:
      p = pr['Probabilita IA']
      q = pr['Quota']
      ev = ValueEngine.calculate_ev(p, q)
      stake = ValueEngine.calculate_kelly_stake(
          p, q, bankroll, kelly_fraction
      )
      p_rows.append({
          'Mercato': pr['Mercato Giocatore'],
          'Probabilita IA': f'{p*100:.2f}%',
          'Quota': q,
          'EV (%)': f'{ev*100:.2f}%',
          'Stake Consigliato (€)': stake if ev >= min_ev else 0.0,
          'Esito Valore': 'VALORE' if ev >= min_ev else 'NO VALORE',
      })
    st.subheader(
        f'Risultati Analisi per {player_name} ({p_team}) vs {opp_team}'
    )
    st.table(pd.DataFrame(p_rows))

with tab3:
  st.header('Registro Scommesse & Dashboard')
  if len(st.session_state.bet_history) > 0:
    st.dataframe(st.session_state.bet_history, use_container_width=True)
  else:
    st.info('Nessuna scommessa registrata nel registro.')
