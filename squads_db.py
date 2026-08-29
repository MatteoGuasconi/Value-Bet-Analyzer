"""
Database e Motore Dinamico Rose per i 5 Grandi Campionati Europei.
Copre tutte le 96 squadre di:
- Serie A (20 squadre)
- Premier League (20 squadre)
- La Liga (20 squadre)
- Bundesliga (18 squadre)
- Ligue 1 (18 squadre)
"""

import requests
import streamlit as st

# MAPPATURA UFFICIALE ID API-FOOTBALL PER TUTTE LE 96 SQUADRE
ALL_LEAGUES_TEAMS_IDS = {
    # SERIE A (20 SQUADRE)
    "Inter": 505, "Juventus": 496, "Milan": 489, "Napoli": 492,
    "Atalanta": 499, "Roma": 497, "Lazio": 487, "Fiorentina": 502,
    "Bologna": 500, "Torino": 503, "Parma": 511, "Cagliari": 490,
    "Empoli": 514, "Genoa": 495, "Monza": 1579, "Lecce": 867,
    "Udinese": 494, "Verona": 504, "Venezia": 517, "Como": 880,

    # PREMIER LEAGUE (20 SQUADRE)
    "Manchester City": 50, "Arsenal": 42, "Liverpool": 40, "Chelsea": 49,
    "Manchester United": 33, "Tottenham": 47, "Newcastle": 34, "Aston Villa": 66,
    "Brighton": 51, "West Ham": 48, "Brentford": 55, "Crystal Palace": 52,
    "Fulham": 36, "Bournemouth": 35, "Everton": 45, "Wolves": 39,
    "Nottingham Forest": 65, "Leicester": 46, "Southampton": 41, "Ipswich": 60,

    # LA LIGA (20 SQUADRE)
    "Real Madrid": 541, "Barcellona": 529, "Barcelona": 529, "Atletico Madrid": 530,
    "Real Sociedad": 548, "Athletic Bilbao": 531, "Villarreal": 533, "Betis": 543,
    "Sevilla": 536, "Girona": 547, "Valencia": 532, "Celta Vigo": 538,
    "Mallorca": 539, "Osasuna": 527, "Getafe": 546, "Rayo Vallecano": 540,
    "Las Palmas": 534, "Alaves": 542, "Espanyol": 798, "Leganes": 545, "Valladolid": 720,

    # BUNDESLIGA (18 SQUADRE)
    "Bayern Monaco": 157, "Bayern Munich": 157, "Bayer Leverkusen": 168, "Borussia Dortmund": 165,
    "RB Leipzig": 173, "Eintracht Frankfurt": 169, "Stoccarda": 172, "Stuttgart": 172,
    "Wolfsburg": 161, "Borussia Monchengladbach": 163, "Friburgo": 160, "Freiburg": 160,
    "Hoffenheim": 167, "Werder Bremen": 162, "Augsburg": 170, "Union Berlin": 182,
    "Mainz": 164, "Heidenheim": 180, "St. Pauli": 186, "Holstein Kiel": 191, "Bochum": 176,

    # LIGUE 1 (18 SQUADRE)
    "PSG": 85, "Paris Saint Germain": 85, "Monaco": 91, "Marseille": 81, "Marsiglia": 81,
    "Lille": 79, "Lione": 80, "Lyon": 80, "Lens": 116, "Rennes": 94,
    "Nizza": 84, "Nice": 84, "Brest": 1063, "Reims": 93, "Strasburgo": 95,
    "Strasbourg": 95, "Tolosa": 96, "Toulouse": 96, "Montpellier": 82, "Nantes": 83,
    "Auxerre": 98, "Angers": 77, "Saint-Etienne": 1063, "Le Havre": 97
}

CLEAN_NAME_MAP = {
    "inter milan": "Inter", "internazionale": "Inter", "ac milan": "Milan",
    "juventus fc": "Juventus", "as roma": "Roma", "ss lazio": "Lazio",
    "fc barcelona": "Barcellona", "barcelona": "Barcellona",
    "bayern munchen": "Bayern Monaco", "bayern munich": "Bayern Monaco",
    "paris saint-germain": "PSG", "paris saint germain": "PSG",
    "manchester city fc": "Manchester City", "arsenal fc": "Arsenal",
    "liverpool fc": "Liverpool", "chelsea fc": "Chelsea", "tottenham hotspur": "Tottenham"
}

def clean_team_name(raw_name: str) -> str:
    """Pulisce e uniforma il nome della squadra."""
    if not raw_name:
        return ""
    norm = raw_name.strip().lower()
    for k, v in CLEAN_NAME_MAP.items():
        if k in norm:
            return v
    for std_name in ALL_LEAGUES_TEAMS_IDS.keys():
        if std_name.lower() in norm or norm in std_name.lower():
            return std_name
    return raw_name.strip()

@st.cache_data(ttl=604800, show_spinner=False)
def fetch_team_squad_api(team_name: str, api_key: str) -> list[dict]:
    """
    Scarica la rosa ufficiale dal server API-Football con salvataggio in cache per 7 giorni.
    Ritorna la lista completa dei calciatori tesserati.
    """
    c_name = clean_team_name(team_name)
    team_id = ALL_LEAGUES_TEAMS_IDS.get(c_name)
    
    if not team_id:
        for k, v in ALL_LEAGUES_TEAMS_IDS.items():
            if k.lower() in c_name.lower() or c_name.lower() in k.lower():
                team_id = v
                break

    if team_id and api_key:
        url = f"https://v3.football.api-sports.io/players/squads?team={team_id}"
        headers = {"x-apisports-key": api_key}
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json().get("response", [])
                if data and "players" in data[0]:
                    players = []
                    for p in data[0]["players"]:
                        pos = p.get("position", "Midfielder")
                        # Assegnazione parametri di base tarati sul ruolo
                        if pos == "Goalkeeper":
                            sot, fouls, saves = 0.0, 0.1, 3.2
                        elif pos == "Attacker":
                            sot, fouls, saves = 1.45, 1.25, 0.0
                        elif pos == "Midfielder":
                            sot, fouls, saves = 0.85, 1.55, 0.0
                        else:  # Defender
                            sot, fouls, saves = 0.35, 1.45, 0.0

                        players.append({
                            "name": p.get("name", "Calciatore"),
                            "role": pos,
                            "number": str(p.get("number") or "-"),
                            "sot_90": sot,
                            "fouls_c_90": fouls,
                            "saves_90": saves,
                            "penalties": (pos == "Attacker")
                        })
                    if players:
                        return players
        except Exception:
            pass

    # Fallback strutturato se la chiamata API fallisce o non e disponibile
    return [
        {"name": f"Portiere Titolare ({c_name})", "role": "Goalkeeper", "number": "1", "sot_90": 0.0, "fouls_c_90": 0.1, "saves_90": 3.1, "penalties": False},
        {"name": f"Difensore Centrale Dx ({c_name})", "role": "Defender", "number": "3", "sot_90": 0.30, "fouls_c_90": 1.60, "saves_90": 0.0, "penalties": False},
        {"name": f"Difensore Centrale Sx ({c_name})", "role": "Defender", "number": "4", "sot_90": 0.25, "fouls_c_90": 1.70, "saves_90": 0.0, "penalties": False},
        {"name": f"Terzino Destro ({c_name})", "role": "Defender", "number": "2", "sot_90": 0.45, "fouls_c_90": 1.30, "saves_90": 0.0, "penalties": False},
        {"name": f"Terzino Sinistro ({c_name})", "role": "Defender", "number": "5", "sot_90": 0.50, "fouls_c_90": 1.35, "saves_90": 0.0, "penalties": False},
        {"name": f"Mediano Difensivo ({c_name})", "role": "Midfielder", "number": "6", "sot_90": 0.55, "fouls_c_90": 1.90, "saves_90": 0.0, "penalties": False},
        {"name": f"Regista / Mezzala ({c_name})", "role": "Midfielder", "number": "8", "sot_90": 0.85, "fouls_c_90": 1.40, "saves_90": 0.0, "penalties": True},
        {"name": f"Trequartista ({c_name})", "role": "Midfielder", "number": "10", "sot_90": 1.15, "fouls_c_90": 1.15, "saves_90": 0.0, "penalties": False},
        {"name": f"Esterno Offensivo Dx ({c_name})", "role": "Attacker", "number": "7", "sot_90": 1.30, "fouls_c_90": 1.05, "saves_90": 0.0, "penalties": False},
        {"name": f"Esterno Offensivo Sx ({c_name})", "role": "Attacker", "number": "11", "sot_90": 1.35, "fouls_c_90": 1.00, "saves_90": 0.0, "penalties": False},
        {"name": f"Centravanti ({c_name})", "role": "Attacker", "number": "9", "sot_90": 1.75, "fouls_c_90": 1.45, "saves_90": 0.0, "penalties": True}
    ]
