"""
Client API unificato con Caching Intelligente e Gestione Rate Limits.
- API-Football (Statistiche, Rose, Formazioni, Arbitri): TTL 6h-24h
- The Odds API (Quote pre-match live): TTL 30m / Chiamate mirate
"""

import requests
import streamlit as st
import datetime
from mapping import clean_team_name, API_FOOTBALL_TEAM_IDS

BASE_API_FOOTBALL_URL = "https://v3.football.api-sports.io"
BASE_ODDS_API_URL = "https://api.the-odds-api.com/v4"

# -------------------------------------------------------------
# API-FOOTBALL (CACHE 24 ORE PER STATISTICHE AGGREGATE)
# -------------------------------------------------------------

@st.cache_data(ttl=86400, show_spinner=False)
def get_team_squad_stats(team_id: int, season: int, api_key: str) -> list[dict]:
    """Recupera la rosa completa con statistiche per calcolo P90 (Cache 24 ore)."""
    if not api_key or not team_id:
        return []
    url = f"{BASE_API_FOOTBALL_URL}/players?team={team_id}&season={season}"
    headers = {"x-apisports-key": api_key}
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json().get("response", [])
            parsed_players = []
            for item in data:
                p_info = item.get("player", {})
                stats_list = item.get("statistics", [])
                if not stats_list:
                    continue
                st_data = stats_list[0]
                
                mins = float(st_data.get("games", {}).get("minutes") or 0)
                shots_tot = float(st_data.get("shots", {}).get("total") or 0)
                sot_tot = float(st_data.get("shots", {}).get("on") or 0)
                fouls_c = float(st_data.get("fouls", {}).get("committed") or 0)
                fouls_d = float(st_data.get("fouls", {}).get("drawn") or 0)
                cards_y = float(st_data.get("cards", {}).get("yellow") or 0)
                saves = float(st_data.get("goals", {}).get("saves") or 0)
                
                pos = st_data.get("games", {}).get("position", "Player")
                
                # Calcolo P90
                sot_p90 = (sot_tot / mins * 90.0) if mins >= 180 else (1.20 if pos == "Attacker" else 0.50)
                shots_p90 = (shots_tot / mins * 90.0) if mins >= 180 else (2.40 if pos == "Attacker" else 1.10)
                fouls_p90 = (fouls_c / mins * 90.0) if mins >= 180 else 1.35
                saves_p90 = (saves / mins * 90.0) if mins >= 180 else 3.10
                
                parsed_players.append({
                    "id": p_info.get("id"),
                    "name": p_info.get("name", "Unknown"),
                    "role": pos,
                    "number": str(st_data.get("games", {}).get("number") or "-"),
                    "minutes": mins,
                    "sot_p90": round(sot_p90, 2),
                    "shots_p90": round(shots_p90, 2),
                    "fouls_p90": round(fouls_p90, 2),
                    "saves_p90": round(saves_p90, 2),
                    "cards_yellow": cards_y
                })
            return parsed_players
    except Exception:
        pass
    return []

# -------------------------------------------------------------
# API-FOOTBALL (CACHE 6 ORE PER CALENDARI E ARBITRI)
# -------------------------------------------------------------

@st.cache_data(ttl=21600, show_spinner=False)
def get_league_fixtures(league_id: int, season: int, api_key: str, next_n: int = 10) -> list[dict]:
    """Recupera le prossime partite in programma per la lega specificata (Cache 6 ore)."""
    if not api_key:
        return []
    url = f"{BASE_API_FOOTBALL_URL}/fixtures?league={league_id}&season={season}&next={next_n}"
    headers = {"x-apisports-key": api_key}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json().get("response", [])
            fixtures = []
            for item in data:
                f_info = item.get("fixture", {})
                t_info = item.get("teams", {})
                ref_str = f_info.get("referee") or "Non comunicato"
                ref_name = ref_str.split(",")[0].replace("Italy", "").strip() if ref_str else "CAN"
                
                fixtures.append({
                    "fixture_id": f_info.get("id"),
                    "date": f_info.get("date", "")[:10],
                    "datetime": f_info.get("date", ""),
                    "home_team": clean_team_name(t_info.get("home", {}).get("name", "")),
                    "away_team": clean_team_name(t_info.get("away", {}).get("name", "")),
                    "home_id": t_info.get("home", {}).get("id"),
                    "away_id": t_info.get("away", {}).get("id"),
                    "referee": ref_name,
                    "status": f_info.get("status", {}).get("short", "NS")
                })
            return fixtures
    except Exception:
        pass
    return []

@st.cache_data(ttl=900, show_spinner=False)
def get_fixture_lineups(fixture_id: int, api_key: str) -> tuple[str, list[str], list[str]]:
    """Verifica formazioni ufficiali (XI titolari) pre-partita (Cache 15 min)."""
    if not api_key or not fixture_id:
        return "PROBABILE", [], []
    url = f"{BASE_API_FOOTBALL_URL}/fixtures/lineups?fixture={fixture_id}"
    headers = {"x-apisports-key": api_key}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if len(data) >= 2:
                home_starters = [p.get("player", {}).get("name", "") for p in data[0].get("startXI", [])]
                away_starters = [p.get("player", {}).get("name", "") for p in data[1].get("startXI", [])]
                return "UFFICIALE", home_starters, away_starters
    except Exception:
        pass
    return "PROBABILE", [], []

# -------------------------------------------------------------
# THE ODDS API (CACHE 30 MINUTI O REFRESH MANUALE)
# -------------------------------------------------------------

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_odds_api_markets(sport_key: str, api_key: str) -> list[dict]:
    """Scarica le quote pre-match via The Odds API per il campionato selezionato."""
    if not api_key:
        return []
    url = f"{BASE_ODDS_API_URL}/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu&markets=h2h,totals&oddsFormat=decimal"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []
