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

# Styling CSS Dark Fintech - Palette Professionale
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

# Inizializzazione Stato Scommesse Locali
if "history_bets" not in st.session_state:
    st.session_state.history_bets = []

# Sidebar - Gestione Bankroll ed Esclusività
st.sidebar.markdown("### 👑 AREA RISERVATA SERIE A")
st.sidebar.markdown("**Utente:** `Esclusivo (Proprietario)`")
st.sidebar.markdown("**Protocollo:** `Match Analyst v4.0 Active`")

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
st.markdown('<div class="slogan-box">Protocollo Quantitativo v4.0: Zero opinioni. Zero sensazioni. Analisi rigorosa basata su xG, Edge e Kelly Mezzato (Kelly/2).</div>', unsafe_allow_html=True)

# Navigazione Tab (Solo sezioni richieste)
tab_analyzer, tab_register, tab_kpi = st.tabs([
    "🎯 Analisi & Inserimento Partita",
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
        
        # Verdetto da protocollo
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
    st.markdown("### 🏟️ SELEZIONE MATCH & INPUT DATI QUANTITATIVI")
    st.caption("Inserisci i dati richiesti dal protocollo per calcolare l'Edge statistico e la sostenibilità della scommessa.")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        home_team = st.text_input("Squadra di Casa", value="Atalanta")
        away_team = st.text_input("Squadra Trasferta", value="Bologna")
        match_day = st.text_input("Competizione & Giornata", value="Serie A - Giornata 28")
        
    with col_in2:
        market_category = st.selectbox(
            "Categoria Mercato",
            [
                "⚽ Gol (1X2, Over/Under, Gol/No Gol, Combo)",
                "🚩 Calci d'Angolo (Over/Under Totali e Team)",
                "🎯 Tiri in Porta / SOT (Individuali e Team)",
                "⚡ Falli & Cartellini (Giocatori e Match)",
                "🏆 Handicap & Risultati Esatti / Parziale-Finale",
                "✍️ Mercato Personalizzato / Tutti gli Altri"
            ]
        )
        exact_market_name = st.text_input("Specifica Mercato e Linea", placeholder="es. Over 2.5 / Over 8.5 Corner / Over 1.5 Atalanta")
        quota_bk = st.number_input("Quota Bookmaker (es. Vincitù / Sharp)", min_value=1.01, max_value=50.0, value=1.85, step=0.01)

    st.markdown("---")
    st.markdown("#### 📊 PARAMETRI STATISTICI DEL MODELLO")
    
    col_st1, col_st2, col_st3 = st.columns(3)
    with col_st1:
        xg_home = st.number_input("xG / Media Proiettata Casa", min_value=0.1, max_value=5.0, value=1.65, step=0.05)
    with col_st2:
        xg_away = st.number_input("xG / Media Proiettata Trasferta", min_value=0.1, max_value=5.0, value=1.15, step=0.05)
    with col_st3:
        conf_level = st.selectbox("Livello di Confidenza Modello", ["ALTA", "MEDIA", "BASSA"], index=0)

    # Calcolo Avanzato Poisson / Binomiale
    if "Gol" in market_category or "Handicap" in market_category:
        if "Over 2.5" in exact_market_name:
            lambda_tot = xg_home + xg_away
            p_model = float(1.0 - poisson.cdf(2, lambda_tot))
        elif "Over 1.5" in exact_market_name and ("Casa" in exact_market_name or home_team.lower() in exact_market_name.lower()):
            p_model = float(1.0 - poisson.cdf(1, xg_home))
        elif "Over 1.5" in exact_market_name and ("Trasferta" in exact_market_name or away_team.lower() in exact_market_name.lower()):
            p_model = float(1.0 - poisson.cdf(1, xg_away))
        else:
            # Stima parametrica generale basata su xG
            p_model = min(0.95, max(0.05, 0.50 + (xg_home - xg_away) * 0.10))
    else:
        # Per corner, tiri, falli basati sui parametri inseriti
        p_model = min(0.95, max(0.05, 0.52 + (xg_home - 1.3) * 0.15))

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
