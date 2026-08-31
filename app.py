import datetime
import numpy as np
import pandas as pd
from scipy.stats import poisson
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="VALUE BET ANALYZER - SERIE A",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling CSS Dark Fintech - Contrasto Alto e Testi Bianchi
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #0B132B !important;
        color: #FFFFFF !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div, label, button, select, .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    [data-testid="stToolbar"], footer {
        visibility: hidden !important;
        display: none !important;
    }
    
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
    
    header[data-testid="stHeader"] {
        background-color: #0B132B !important;
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
        color: #FFFFFF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        font-weight: 600;
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
    </style>
""",
    unsafe_allow_html=True,
)

# Inizializzazione Stato Scommesse, Infortuni
if "history_bets" not in st.session_state:
    st.session_state.history_bets = []
if "injuries_list" not in st.session_state:
    st.session_state.injuries_list = []

# Sidebar - Gestione Bankroll ed Esclusività
st.sidebar.markdown("### 👑 SERIE A • PROTOCOLLO v4.0")
st.sidebar.markdown("**Modalità:** `Esclusiva Proprietario`")

st.sidebar.markdown("---")
initial_bankroll = st.sidebar.number_input("Bankroll Iniziale (€)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.select_slider("Frazione di Kelly", options=[0.25, 0.50, 1.0], value=0.50, help="Protocollo standard: Kelly/2 (0.50)")
min_edge_pct = st.sidebar.slider("Soglia Minima Edge (%)", min_value=1.0, max_value=5.0, value=3.0, step=0.5, help="Soglia minima da protocollo: 3.0%")
min_edge_val = min_edge_pct / 100.0

# Calcolo Bankroll Dinamico
total_profit = sum([b.get("profit", 0.0) for b in st.session_state.history_bets if b.get("status") in ["VINTA", "PERSA"]])
total_stake_history = sum([b.get("stake", 0.0) for b in st.session_state.history_bets if b.get("status") in ["VINTA", "PERSA"]])
current_bankroll = initial_bankroll + total_profit
yield_val = (total_profit / total_stake_history * 100.0) if total_stake_history > 0 else 0.0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 STATISTICHE PORTAFOGLIO")
st.sidebar.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Capitale Attuale</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF;">{current_bankroll:.2f} €</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Profitto / Perdita</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: {'#2DD4BF' if total_profit >= 0 else '#EF4444'};">{total_profit:+.2f} €</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">Yield %</div>
        <div style="font-size: 1.25rem; font-weight: 800; color: {'#2DD4BF' if yield_val >= 0 else '#EF4444'};">{yield_val:+.2f}%</div>
    </div>
""", unsafe_allow_html=True)

# Titolo Principale
st.title("VALUE BET ANALYZER • SERIE A")

# Navigazione Tab
tab_analyzer, tab_players, tab_injuries, tab_register, tab_kpi = st.tabs([
    "🎯 Analisi Squadre & Match",
    "⚡ Statistiche Giocatori (SOT & Falli)",
    "🏥 Gestione Infermeria",
    "📝 Registro Scommesse",
    "📈 KPI & Statistiche"
])

# MOTOR QUANTITATIVO DA PROTOCOLLO
class QuantitativeEngine:
    @staticmethod
    def calculate_metrics(p_reale, quota_book, bankroll):
        p_imp = 1.0 / quota_book
        edge = (quota_book / (1.0 / p_reale)) - 1.0
        ev = (p_reale * quota_book) - 1.0
        b = quota_book - 1.0
        
        # Kelly Mezzato (Kelly/2)
        if b > 0:
            kelly_full = ((p_reale * b) - (1.0 - p_reale)) / b
            kelly_half = max(0.0, kelly_full * 0.50)
        else:
            kelly_half = 0.0
            
        # Cap di fascia da protocollo
        if edge < 0.03:
            cap_fascia = 0.05
        elif edge <= 0.07:
            cap_fascia = 0.12
        else:
            cap_fascia = 0.20
            
        final_stake_pct = min(kelly_half, cap_fascia)
        stake_eur = round(bankroll * final_stake_pct, 2)
        
        verdetto = "BET QUALIFICATO" if edge >= 0.03 and ev > 0 and quota_book >= 1.70 else "NO BET / Sotto soglia protocollo"
        
        return {
            "p_imp": round(p_imp * 100, 2),
            "edge": round(edge * 100, 2),
            "ev": round(ev * 100, 2),
            "quota_equa": round(1.0 / p_reale, 2),
            "kelly_half": round(kelly_half * 100, 2),
            "stake_pct": round(final_stake_pct * 100, 2),
            "stake_eur": stake_eur,
            "verdetto": verdetto
        }

with tab_analyzer:
    st.markdown("### 🏟️ ANALISI MATCH & MERCATI DI SQUADRA")
    st.caption("Protocollo Match Analyst v4.0: Seleziona il mercato per sbloccare i parametri statistici corretti.")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        home_team = st.text_input("Squadra di Casa", value="Atalanta")
        away_team = st.text_input("Squadra Trasferta", value="Bologna")
        match_day = st.text_input("Competizione & Giornata", value="Serie A - Giornata 28")
        
    with col_in2:
        market_category = st.selectbox(
            "Protocollo / Categoria Mercato",
            [
                "⚽ Gol (Over 2.5, Over 1.5 Team, 1X2, BTTS)",
                "🚩 Calci d'Angolo (Over/Under Totali e Team)",
                "🎯 Tiri in Porta / SOT (Team)",
                "🏆 Handicap & Risultati Esatti / Parziale-Finale",
                "✍️ Mercato Personalizzato / Tutti gli Altri"
            ]
        )
        exact_market_name = st.text_input("Specifica Mercato e Linea", placeholder="es. Over 2.5 / Over 8.5 Corner / Over 1.5 Atalanta")
        quota_bk = st.number_input("Quota Bookmaker (es. Vincitù / Sharp)", min_value=1.01, max_value=50.0, value=1.85, step=0.01)

    st.markdown("---")
    
    # -------------------------------------------------------------
    # CAMPI DINAMICI INTUITIVI IN BASE AL MERCATO SELEZIONATO
    # -------------------------------------------------------------
    if "⚽ Gol" in market_category:
        st.markdown("#### 📊 PARAMETRI GOL & EXPECTED GOALS (xG)")
        col_st1, col_st2, col_st3 = st.columns(3)
        with col_st1: xg_home = st.number_input("xG Casa (ultime 8 / normalizzato)", min_value=0.1, max_value=5.0, value=1.65, step=0.05)
        with col_st2: xg_away = st.number_input("xG Trasferta (ultime 8 / normalizzato)", min_value=0.1, max_value=5.0, value=1.15, step=0.05)
        with col_st3: conf_level = st.selectbox("Confidenza Modello", ["ALTA", "MEDIA", "BASSA"], index=0)
        
        lambda_tot = xg_home + xg_away
        if "Over 2.5" in exact_market_name:
            p_model = float(1.0 - poisson.cdf(2, lambda_tot))
        elif "Over 1.5" in exact_market_name and ("Casa" in exact_market_name or home_team.lower() in exact_market_name.lower()):
            p_model = float(1.0 - poisson.cdf(1, xg_home))
        elif "Over 1.5" in exact_market_name and ("Trasferta" in exact_market_name or away_team.lower() in exact_market_name.lower()):
            p_model = float(1.0 - poisson.cdf(1, xg_away))
        else:
            p_model = min(0.95, max(0.05, 0.50 + (xg_home - xg_away) * 0.10))

    elif "🚩 Calci d'Angolo" in market_category:
        st.markdown("#### 🚩 PARAMETRI CALCI D'ANGOLO (Protocollo Corner)")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1: mean_corners = st.number_input("Media Corner Combinati / Proiettati", min_value=2.0, max_value=18.0, value=9.5, step=0.5)
        with col_c2: cross_vol = st.number_input("Volume Cross / Gara (Correzione +8% se >20)", min_value=10.0, max_value=35.0, value=19.0, step=1.0)
        with col_c3: ref_sev = st.selectbox("Direttore di Gara / Arbitro", ["Permissivo (-5%)", "Standard (0%)", "Severo (+5%)"])
        
        c_mod = mean_corners * (1.08 if cross_vol > 20 else 1.0)
        if "Severo" in ref_sev: c_mod *= 1.05
        elif "Permissivo" in ref_sev: c_mod *= 0.95
        
        p_model = float(1.0 - poisson.cdf(8, c_mod)) if "Over 8.5" in exact_market_name else 0.55

    elif "🎯 Tiri in Porta" in market_category:
        st.markdown("#### 🎯 PARAMETRI TIRI IN PORTA / SOT TEAM")
        col_t1, col_t2 = st.columns(2)
        with col_t1: base_sot = st.number_input("Media SOT / Tiri in Porta Proiettati", min_value=1.0, max_value=15.0, value=4.5, step=0.5)
        with col_t2: low_block = st.selectbox("Atteggiamento Avversario", ["Normale / Linea Alta", "Blocco Basso (Low Block)"])
        
        sot_mod = base_sot * (0.90 if "Blocco Basso" in low_block else 1.0)
        p_model = float(1.0 - poisson.cdf(3, sot_mod)) if "Over 3.5" in exact_market_name else 0.52

    else:
        st.markdown("#### ✍️ PARAMETRI MERCATO PERSONALIZZATO")
        col_p1, col_p2 = st.columns(2)
        with col_p1: est_prob = st.slider("Stima Probabilità Reale (%)", min_value=5.0, max_value=95.0, value=55.0, step=1.0)
        p_model = est_prob / 100.0

    calc_res = QuantitativeEngine.calculate_metrics(p_model, quota_bk, current_bankroll)

    st.markdown("---")
    st.markdown("### 📋 REPORT DI VALUTAZIONE TECNICO-QUANTITATIVA")
    
    rep_col1, rep_col2, rep_col3 = st.columns(3)
    with rep_col1:
        st.metric("Probabilità Reale Modello", f"{p_model*100:.1f}%")
        st.metric("Quota Equa", f"{calc_res['quota_equa']:.2f}")
    with rep_col2:
        st.metric("Edge Statistico", f"{calc_res['edge']:+.2f}%", help="Soglia minima protocollo: > 3.0%")
        st.metric("Valore Atteso (EV)", f"{calc_res['ev']:+.2f}%")
    with rep_col3:
        st.metric("Stake Consigliato (Kelly/2)", f"{calc_res['stake_pct']}%", f"{calc_res['stake_eur']:.2f} €")
        st.metric("Verdetto Protocollo", calc_res['verdetto'])

    st.markdown("---")
    if calc_res['edge'] >= 3.0 and quota_bk >= 1.70:
        st.success(f"✅ **BET QUALIFICATO**: Il match rispetta tutti i filtri quantitativi del protocollo v4.0.")
        if st.button("REGISTRA SCOMMESSA NEL REGISTRO"):
            new_bet = {
                "id": len(st.session_state.history_bets) + 1,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "match": f"{home_team} vs {away_team}",
                "market": exact_market_name or market_category,
                "odds": quota_bk,
                "stake": calc_res['stake_eur'],
                "ev": calc_res['ev'],
                "status": "IN CORSO",
                "profit": 0.0
            }
            st.session_state.history_bets.append(new_bet)
            st.success("Scommessa salvata con successo nel Registro!")
            st.rerun()
    else:
        st.warning("⚠️ **NO BET**: L'opportunità non soddisfa i requisiti minimi di Edge (≥3%) o Quota (≥1.70) previsti dal protocollo.")

with tab_players:
    st.markdown("### ⚡ ANALISI STATISTICA GIOCATORI (SOT & FALLI)")
    st.caption("Protocollo Tiri in Porta Giocatori & Falli Serie A: Inserisci le metriche P90 del calciatore.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        p_name = st.text_input("Nome Calciatore", value="Mateo Retegui")
        p_role = st.selectbox("Ruolo", ["Attaccante", "Centrocampista", "Difensore"])
        p_market = st.selectbox("Mercato Giocatore", ["Over 0.5 Tiri in Porta (SOT)", "Over 1.5 Tiri in Porta (SOT)", "Over 1.5 Falli Commessi", "Over 1.5 Falli Subiti"])
    with col_p2:
        p_stat_p90 = st.number_input("Media Statistica / 90 minuti (SOT o Falli)", min_value=0.1, max_value=5.0, value=1.25, step=0.05)
        p_quota = st.number_input("Quota Bookmaker Giocatore", min_value=1.01, max_value=30.0, value=1.90, step=0.01)
        p_rigorista = st.checkbox("Rigorista principale in campo (+10% xSOT)")

    p_mod_val = p_stat_p90 * (1.10 if p_rigorista else 1.0)
    if "0.5" in p_market: p_p_model = float(1.0 - poisson.cdf(0, p_mod_val))
    elif "1.5" in p_market: p_p_model = float(1.0 - poisson.cdf(1, p_mod_val))
    else: p_p_model = 0.55

    p_calc_res = QuantitativeEngine.calculate_metrics(p_p_model, p_quota, current_bankroll)

    st.markdown("---")
    col_pp1, col_pp2, col_pp3 = st.columns(3)
    with col_pp1:
        st.metric("Probabilità Reale Giocatore", f"{p_p_model*100:.1f}%")
        st.metric("Quota Equa", f"{p_calc_res['quota_equa']:.2f}")
    with col_pp2:
        st.metric("Edge Giocatore", f"{p_calc_res['edge']:+.2f}%")
        st.metric("EV", f"{p_calc_res['ev']:+.2f}%")
    with col_pp3:
        st.metric("Stake Consigliato", f"{p_calc_res['stake_pct']}%", f"{p_calc_res['stake_eur']:.2f} €")
        st.metric("Verdetto Giocatore", p_calc_res['verdetto'])

    if p_calc_res['edge'] >= 3.0 and p_quota >= 1.70:
        if st.button("REGISTRA SCOMMESSA GIOCATORE"):
            st.session_state.history_bets.append({
                "id": len(st.session_state.history_bets) + 1,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "match": f"Prop: {p_name}",
                "market": p_market,
                "odds": p_quota,
                "stake": p_calc_res['stake_eur'],
                "ev": p_calc_res['ev'],
                "status": "IN CORSO",
                "profit": 0.0
            })
            st.success("Giocata registrata nel Registro Scommesse!")
            st.rerun()

with tab_injuries:
    st.markdown("### 🏥 GESTIONE INFERMERIA & INDISPONIBILI SERIE A")
    st.caption("Inserisci i calciatori infortunati per ponderare correttamente l'impatto quantitativo su xG e linee statistiche.")
    
    col_inj1, col_inj2 = st.columns(2)
    with col_inj1:
        inj_team = st.text_input("Squadra di Serie A", placeholder="es. Atalanta, Bologna, Milan...")
        inj_player = st.text_input("Nome Calciatore Indisponibile", placeholder="es. Scamacca")
    with col_inj2:
        inj_imp = st.selectbox("Importanza Tattica", ["Top Player Offensivo (-12% xG)", "Titolare Mediano / Regista", "Difensore Centrale Titolare", "Portiere Titolare"])
        inj_date = st.text_input("Data Rientro Prevista", value="Da valutare")
        if st.button("REGISTRA INDISPONIBILE"):
            if inj_team and inj_player:
                st.session_state.injuries_list.append({
                    "team": inj_team, "player": inj_player, "importance": inj_imp, "return": inj_date
                })
                st.success(f"Indisponibile registrato per {inj_team}.")
                st.rerun()
                
    if st.session_state.injuries_list:
        st.markdown("#### Elenco Attuale Indisponibili")
        df_inj = pd.DataFrame(st.session_state.injuries_list)
        st.dataframe(df_inj, use_container_width=True, hide_index=True)
        if st.button("PULISCI INFERMERIA"):
            st.session_state.injuries_list = []
            st.rerun()
    else:
        st.info("Nessun calciatore registrato in infermeria.")

with tab_register:
    st.markdown("### 📝 REGISTRO OPERATIVO SCOMMESSE")
    st.caption("Storico completo delle giocate effettuate e tracciamento dei profitti.")
    
    if st.session_state.history_bets:
        df_bets = pd.DataFrame(st.session_state.history_bets)
        st.dataframe(df_bets[["created_at", "match", "market", "odds", "stake", "status", "profit"]], use_container_width=True, hide_index=True)
        
        st.markdown("#### Aggiorna Esito Scommessa")
        b_idx = st.selectbox("Seleziona ID Scommessa", range(len(st.session_state.history_bets)), format_func=lambda x: f"#{st.session_state.history_bets[x]['id']} - {st.session_state.history_bets[x]['match']} ({st.session_state.history_bets[x]['market']})")
        
        col_es1, col_es2 = st.columns(2)
        with col_es1:
            new_status = st.selectbox("Esito Finale", ["IN CORSO", "VINTA", "PERSA", "VOID"], key="upd_status_sel")
        with col_es2:
            st.write("")
            st.write("")
            if st.button("AGGIORNA STATO SCOMMESSA"):
                bet_item = st.session_state.history_bets[b_idx]
                bet_item["status"] = new_status
                if new_status == "VINTA":
                    bet_item["profit"] = round((bet_item["odds"] - 1.0) * bet_item["stake"], 2)
                elif new_status == "PERSA":
                    bet_item["profit"] = round(-bet_item["stake"], 2)
                else:
                    bet_item["profit"] = 0.0
                st.success("Stato aggiornato correttamente!")
                st.rerun()
    else:
        st.info("Nessuna scommessa registrata nel registro operativo.")

with tab_kpi:
    st.markdown("### 📈 ANALISI KPI & PERFORMANCE")
    st.markdown(f"""
        - **Capitale Iniziale:** `{initial_bankroll:.2f} €`
        - **Capitale Attuale:** `{current_bankroll:.2f} €`
        - **Profitto Netto:** `{total_profit:+.2f} €`
        - **Yield Operativo:** `{yield_val:+.2f}%`
        - **Totale Scommesse Tracciate:** `{len(st.session_state.history_bets)}`
    """)
