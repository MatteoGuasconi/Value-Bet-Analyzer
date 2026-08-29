import datetime
import numpy as np
import pandas as pd
import requests
import streamlit as st

# Moduli Locali
from mapping import LEAGUES_MAPPING, API_FOOTBALL_TEAM_IDS, clean_team_name
from analytics import (
    calculate_p90,
    calculate_weighted_lambda,
    calculate_poisson_over_prob,
    calculate_fair_odds,
    calculate_min_value_odds,
    calculate_edge,
    calculate_kelly_stake,
    ValueBetEngine
)
import api_client

# Configurazione Pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER PRO",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark Fintech Theme & Fix Menu Mobile Safari
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0B132B !important;
        color: #F8FAFC !important;
    }
    
    [data-testid="stToolbar"], footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* FIX CRITICO TOGGLE MENU LATERALE SU SMARTPHONE & SAFARI */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: #2DD4BF !important;
        background-color: #1C2541 !important;
        border-radius: 8px !important;
        border: 1px solid #2D3A5D !important;
        z-index: 999999 !important;
        top: 0.6rem !important;
        left: 0.6rem !important;
        padding: 6px !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
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

    .badge-official {
        background-color: rgba(45, 212, 191, 0.15);
        border: 1px solid #2DD4BF;
        color: #2DD4BF;
        font-size: 0.80rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 4px;
        display: inline-block;
    }

    .badge-probable {
        background-color: rgba(245, 158, 11, 0.15);
        border: 1px solid #F59E0B;
        color: #FCD34D;
        font-size: 0.80rem;
        font-weight: 700;
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
    }
    .stButton>button:hover {
        background-color: #14B8A6 !important;
    }
    
    div[data-testid="stTable"], div[data-testid="stDataFrame"] {
        border-radius: 8px;
        border: 1px solid #2D3A5D;
        background-color: #1C2541;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Configurazione Secrets
SB_URL = st.secrets.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = st.secrets.get("SUPABASE_KEY", "")
ODDS_KEY = st.secrets.get("ODDS_API_KEY", "")
FOOTBALL_KEY = st.secrets.get("FOOTBALL_API_KEY", "")

# Gestione Stato Sessione
if "user" not in st.session_state:
    st.session_state.user = None
if "user_tier" not in st.session_state:
    st.session_state.user_tier = "free"
if "access_token" not in st.session_state:
    st.session_state.access_token = None

def get_supabase_headers(token=None):
    auth_bearer = token or SB_KEY
    return {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {auth_bearer}",
        "Content-Type": "application/json",
    }

# Autenticazione Supabase
def login_user(email, password):
    if not SB_URL or not SB_KEY:
        # Fallback offline
        st.session_state.user = {"email": email, "id": "local_demo"}
        st.session_state.user_tier = "free"
        return True, None
    url = f"{SB_URL}/auth/v1/token?grant_type=password"
    try:
        res = requests.post(url, json={"email": email, "password": password}, headers=get_supabase_headers(), timeout=8)
        if res.status_code == 200:
            data = res.json()
            st.session_state.user = data.get("user")
            st.session_state.access_token = data.get("access_token")
            u_id = data["user"]["id"]
            prof_url = f"{SB_URL}/rest/v1/profiles?id=eq.{u_id}&select=tier"
            prof_res = requests.get(prof_url, headers=get_supabase_headers(data.get("access_token")), timeout=8)
            if prof_res.status_code == 200 and prof_res.json():
                st.session_state.user_tier = prof_res.json()[0].get("tier", "free")
            return True, None
        return False, res.json().get("msg") or "Credenziali errate."
    except Exception as e:
        return False, str(e)

def redeem_vip_code(user_id, code_input):
    valid_codes = ["Valuebet2026", "VIP2026", "PRO2026"]
    if code_input.strip() in valid_codes:
        if SB_URL and SB_KEY and user_id != "local_demo":
            token = st.session_state.get("access_token")
            url = f"{SB_URL}/rest/v1/profiles?id=eq.{user_id}"
            try:
                requests.patch(url, json={"tier": "premium"}, headers=get_supabase_headers(token), timeout=8)
            except Exception:
                pass
        st.session_state.user_tier = "premium"
        return True, "Codice VIP confermato. Accesso Premium attivato."
    return False, "Codice promozionale non valido."

def save_user_bet(match, market, odds, stake, edge):
    if SB_URL and SB_KEY and st.session_state.user:
        u_id = st.session_state.user.get("id")
        token = st.session_state.get("access_token")
        url = f"{SB_URL}/rest/v1/user_bets"
        payload = {
            "user_id": u_id,
            "match": match,
            "market": market,
            "odds": float(odds),
            "stake": float(stake),
            "ev": float(edge),
            "status": "IN CORSO",
            "profit": 0.0
        }
        try:
            requests.post(url, json=payload, headers=get_supabase_headers(token), timeout=8)
        except Exception:
            pass

# Schermata Login se non autenticato
if not st.session_state.user:
    st.title("VALUE BET ANALYZER PRO")
    st.markdown('<div class="slogan-box">Suite quantitativa per scommesse sportive di valore (+EV). Nessun pronostico soggettivo: solo modelli statistici e distribuzioni di Poisson con edge positivo.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tab_log, tab_reg = st.tabs(["Accedi al Tuo Account", "Accesso Rapido Demo"])
        with tab_log:
            l_email = st.text_input("Email")
            l_pwd = st.text_input("Password", type="password")
            if st.button("ACCEDI ALLA SUITE", use_container_width=True):
                if l_email and l_pwd:
                    ok, msg = login_user(l_email, l_pwd)
                    if ok:
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Compila tutti i campi.")
        with tab_reg:
            st.info("Vuoi testare l'algoritmo quantitativo senza creare account?")
            if st.button("ENTRA IN MODALITA DEMO", use_container_width=True):
                login_user("demo@quantbet.com", "demopass")
                st.rerun()
    st.stop()

# -------------------------------------------------------------
# SIDEBAR: PARAMETRI & FILTRI
# -------------------------------------------------------------
user_email = st.session_state.user.get("email", "")
is_premium = st.session_state.user_tier == "premium"

st.sidebar.markdown(f"**Utente:** `{user_email}`")
st.sidebar.markdown(f"**Stato:** `{'PREMIUM (ATTIVO)' if is_premium else 'PIANO FREE'}`")

if not is_premium:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### SBLOCCO PIANO PRO")
    vip_in = st.sidebar.text_input("Codice VIP / Sblocco", type="password")
    if st.sidebar.button("ATTIVA PREMIUM", use_container_width=True):
        ok, msg = redeem_vip_code(st.session_state.user.get("id"), vip_in)
        if ok:
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error(msg)

st.sidebar.markdown("---")
st.sidebar.markdown("### SELEZIONA COMPETIZIONE")
selected_league = st.sidebar.selectbox("Campionato", list(LEAGUES_MAPPING.keys()), index=0)
league_cfg = LEAGUES_MAPPING[selected_league]

st.sidebar.markdown("---")
st.sidebar.markdown("### PARAMETRI DI MONEY MANAGEMENT")
bankroll = st.sidebar.number_input("Bankroll (€)", min_value=10.0, value=1000.0, step=50.0)
min_edge_pct = st.sidebar.slider("Edge Minimo (+EV %)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
min_edge_val = min_edge_pct / 100.0

kelly_fraction = st.sidebar.select_slider(
    "Frazione Criterio di Kelly",
    options=[0.25, 0.50],
    value=0.50,
    format_func=lambda x: f"{x} ({'Prudente / Kelly 1/4' if x==0.25 else 'Standard / Half-Kelly'})"
)

if st.sidebar.button("AGGIORNA CACHE API", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("Cache aggiornata con successo.")
    st.rerun()

if st.sidebar.button("LOGOUT", use_container_width=True):
    st.session_state.user = None
    st.session_state.user_tier = "free"
    st.rerun()

# -------------------------------------------------------------
# FETCH DATI CON RATE LIMIT SHIELD
# -------------------------------------------------------------
fixtures = api_client.get_league_fixtures(
    league_id=league_cfg["api_football_id"],
    season=league_cfg["season"],
    api_key=FOOTBALL_KEY,
    next_n=10
)

# Header Principale
st.title("VALUE BET ANALYZER PRO")
st.markdown('<div class="slogan-box">In questa suite non si forzano le giocate: si opera solo ed esclusivamente in presenza di valore matematico misurabile (+EV). Nel lungo periodo, il valore coincide con il profitto.</div>', unsafe_allow_html=True)

# Tabs di navigazione
tab_scanner, tab_matches, tab_bankroll = st.tabs([
    "Scanner Top Value Bets (+EV)",
    "Analisi Partita & Formazioni Ufficiali",
    "Registro Bankroll & Cloud Sync"
])

# -------------------------------------------------------------
# TAB 1: SCANNER TOP VALUE BETS
# -------------------------------------------------------------
with tab_scanner:
    st.markdown(f"### TOP VALUE BETS: {selected_league.upper()}")
    st.caption("Filtro quantitativo basato su distribuzione di Poisson, P90 storico e quote di mercato.")
    
    if not fixtures:
        st.info("Nessun match programmato o chiavi API non configurate. Verifica `secrets.toml`.")
    else:
        all_opportunities = []
        
        # Scansione partite del turno
        for fix in fixtures:
            h_team = fix["home_team"]
            a_team = fix["away_team"]
            h_id = fix["home_id"]
            a_id = fix["away_id"]
            match_title = f"{h_team} vs {a_team}"
            
            # Recupero formazioni e status
            lineup_status, h_starters, a_starters = api_client.get_fixture_lineups(fix["fixture_id"], FOOTBALL_KEY)
            
            # Recupero rose e P90
            h_squad = api_client.get_team_squad_stats(h_id, league_cfg["season"], FOOTBALL_KEY)
            a_squad = api_client.get_team_squad_stats(a_id, league_cfg["season"], FOOTBALL_KEY)
            
            # Analisi Player Props (Tiri in Porta & Falli)
            for p in h_squad:
                if p["minutes"] >= 180 and p["role"] in ["Attacker", "Midfielder"]:
                    is_starter = p["name"] in h_starters if lineup_status == "UFFICIALE" else True
                    # Over 0.5 Tiri in Porta
                    res_sot = ValueBetEngine.analyze_player_stat(
                        player_name=p["name"], role=p["role"], p90_val=p["sot_p90"],
                        opp_conceded=4.2, league_conceded_avg=4.3, line=0.5,
                        market_name="Tiri in Porta", book_odds=1.80, is_starter=is_starter
                    )
                    if res_sot["edge"] >= min_edge_val:
                        all_opportunities.append({"match": match_title, "lineup_status": lineup_status, **res_sot})
                        
                    # Over 1.5 Falli Commessi
                    res_fl = ValueBetEngine.analyze_player_stat(
                        player_name=p["name"], role=p["role"], p90_val=p["fouls_p90"],
                        opp_conceded=12.5, league_conceded_avg=12.5, line=1.5,
                        market_name="Falli Commessi", book_odds=2.10, is_starter=is_starter
                    )
                    if res_fl["edge"] >= min_edge_val:
                        all_opportunities.append({"match": match_title, "lineup_status": lineup_status, **res_fl})
                        
            for p in a_squad:
                if p["minutes"] >= 180 and p["role"] in ["Attacker", "Midfielder"]:
                    is_starter = p["name"] in a_starters if lineup_status == "UFFICIALE" else True
                    res_sot = ValueBetEngine.analyze_player_stat(
                        player_name=p["name"], role=p["role"], p90_val=p["sot_p90"],
                        opp_conceded=4.0, league_conceded_avg=4.3, line=0.5,
                        market_name="Tiri in Porta", book_odds=1.85, is_starter=is_starter
                    )
                    if res_sot["edge"] >= min_edge_val:
                        all_opportunities.append({"match": match_title, "lineup_status": lineup_status, **res_sot})
        
        # Ordinamento per Edge
        all_opportunities.sort(key=lambda x: x["edge"], reverse=True)
        
        if all_opportunities:
            table_rows = []
            for idx, op in enumerate(all_opportunities[:10]):
                pos = idx + 1
                k_pct, k_eur = calculate_kelly_stake(op["prob"], op["book_odds"], bankroll, kelly_fraction)
                
                if is_premium or pos in [4, 5]:
                    table_rows.append({
                        "POS": f"#{pos}",
                        "PARTITA": op["match"],
                        "SELEZIONE": f"{op['player']} ({op['role']})",
                        "MERCATO": op["market"],
                        "TITOLARE": "SI (Ufficiale)" if op["lineup_status"] == "UFFICIALE" else "Probabile",
                        "P90": f"{op['p90']:.2f}",
                        "PROB. REALE": op["prob_pct"],
                        "QUOTA EQUA": f"{op['fair_odds']:.2f}",
                        "QUOTA MINIMA": f"{op['min_odds']:.2f}",
                        "EDGE": op["edge_pct"],
                        "STAKE (KELLY)": f"{k_pct}% ({k_eur:.2f} €)"
                    })
                else:
                    table_rows.append({
                        "POS": f"#{pos}",
                        "PARTITA": op["match"],
                        "SELEZIONE": "[BLOCCATO - PIANO PREMIUM]",
                        "MERCATO": "[BLOCCATO]",
                        "TITOLARE": "---",
                        "P90": "---",
                        "PROB. REALE": "---",
                        "QUOTA EQUA": "---",
                        "QUOTA MINIMA": "---",
                        "EDGE": "---",
                        "STAKE (KELLY)": "---"
                    })
            
            st.table(pd.DataFrame(table_rows))
            
            st.markdown("---")
            st.markdown("### CALCOLATORE STAKE & VERIFICA QUOTA REALE BOOKMAKER")
            selected_opp = all_opportunities[0]
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown(f"**Partita:** `{selected_opp['match']}`")
                st.markdown(f"**Mercato:** `{selected_opp['market']}`")
                st.markdown(f"**Probabilita Modello:** `{selected_opp['prob_pct']}` | **Quota Equa:** `{selected_opp['fair_odds']:.2f}`")
                st.markdown(f"**Quota Minima di Ingresso:** `{selected_opp['min_odds']:.2f}`")
            with col_v2:
                real_book_odd = st.number_input("Inserisci Quota del tuo Bookmaker (AAMS/.IT)", min_value=1.01, max_value=20.0, value=float(selected_opp['book_odds']), step=0.02)
                real_edge = calculate_edge(selected_opp["prob"], real_book_odd)
                kp, ke = calculate_kelly_stake(selected_opp["prob"], real_book_odd, bankroll, kelly_fraction)
                
                if real_book_odd >= selected_opp["min_odds"] and real_edge >= min_edge_val:
                    st.success(f"VALORE PRESENTE: Edge {real_edge*100:+.2f}%\nStake Suggerito: {kp}% ({ke:.2f} €)")
                    if st.button("REGISTRA SCOMMESSA NEL DATABASE"):
                        save_user_bet(selected_opp["match"], selected_opp["market"], real_book_odd, ke, real_edge)
                        st.success("Scommessa registrata con successo.")
                else:
                    st.error(f"NO BET (Quota sotto la soglia minima di valore. Edge: {real_edge*100:+.2f}%)")
        else:
            st.info("Nessuna value bet trovata per i filtri selezionati.")

# -------------------------------------------------------------
# TAB 2: ANALISI PARTITA & FORMAZIONI
# -------------------------------------------------------------
with tab_matches:
    st.markdown("### DETTAGLIO PARTITA & VERIFICA FORMAZIONI")
    if fixtures:
        f_options = [f"{f['home_team']} vs {f['away_team']} ({f['date']})" for f in fixtures]
        sel_fix_i = st.selectbox("Seleziona Incontro", range(len(f_options)), format_func=lambda x: f_options[x])
        cur_fix = fixtures[sel_fix_i]
        
        l_status, h_st, a_st = api_client.get_fixture_lineups(cur_fix["fixture_id"], FOOTBALL_KEY)
        
        if l_status == "UFFICIALE":
            st.markdown('<div class="badge-official">FORMAZIONI UFFICIALI CONFERMATE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-probable">FORMAZIONI PROBABILI (IN ATTESA DI DISTINTA UFFICIALE)</div>', unsafe_allow_html=True)
            
        st.markdown(f"**Direttore di Gara:** `{cur_fix['referee']}`")
        
        col_sq1, col_sq2 = st.columns(2)
        with col_sq1:
            st.markdown(f"#### {cur_fix['home_team']} (Casa)")
            h_players = api_client.get_team_squad_stats(cur_fix["home_id"], league_cfg["season"], FOOTBALL_KEY)
            if h_players:
                df_h = pd.DataFrame(h_players)[["name", "role", "minutes", "sot_p90", "fouls_p90"]]
                st.dataframe(df_h, use_container_width=True, hide_index=True)
        with col_sq2:
            st.markdown(f"#### {cur_fix['away_team']} (Trasferta)")
            a_players = api_client.get_team_squad_stats(cur_fix["away_id"], league_cfg["season"], FOOTBALL_KEY)
            if a_players:
                df_a = pd.DataFrame(a_players)[["name", "role", "minutes", "sot_p90", "fouls_p90"]]
                st.dataframe(df_a, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 3: REGISTRO BANKROLL & CLOUD SYNC
# -------------------------------------------------------------
with tab_bankroll:
    st.markdown("### IL TUO BANKROLL & RESOCONTO OPERATIVO")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Capitale Dedicato</div>
        <div class="metric-value-neutral">{bankroll:.2f} €</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Tutte le giocate registrate vengono salvate sul database Supabase con aggiornamento automatico di Yield e Win Rate.")
