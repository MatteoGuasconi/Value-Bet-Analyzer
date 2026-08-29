"""
Modulo per la mappatura e normalizzazione di leghe, squadre e mercati.
Permette l'interoperabilità tra API-Football e The Odds API.
"""

# Mappatura Leghe: Nome visualizzato -> ID API-Football e Key The Odds API
LEAGUES_MAPPING = {
    "Serie A (Italia)": {
        "api_football_id": 135,
        "odds_api_key": "soccer_italy_serie_a",
        "has_players": True,
        "country": "Italy",
        "season": 2026
    },
    "Premier League (Inghilterra)": {
        "api_football_id": 39,
        "odds_api_key": "soccer_epl",
        "has_players": True,
        "country": "England",
        "season": 2026
    },
    "La Liga (Spagna)": {
        "api_football_id": 140,
        "odds_api_key": "soccer_spain_la_liga",
        "has_players": True,
        "country": "Spain",
        "season": 2026
    },
    "Bundesliga (Germania)": {
        "api_football_id": 78,
        "odds_api_key": "soccer_germany_bundesliga",
        "has_players": True,
        "country": "Germany",
        "season": 2026
    },
    "Ligue 1 (Francia)": {
        "api_football_id": 61,
        "odds_api_key": "soccer_france_ligue_one",
        "has_players": True,
        "country": "France",
        "season": 2026
    },
    "Champions League": {
        "api_football_id": 2,
        "odds_api_key": "soccer_uefa_champs_league",
        "has_players": True,
        "country": "World",
        "season": 2026
    },
    "Europa League": {
        "api_football_id": 3,
        "odds_api_key": "soccer_uefa_europa_league",
        "has_players": False,
        "country": "World",
        "season": 2026
    }
}

# Normalizzazione Nomi Squadre (The Odds API / Varianti -> Nome Standard)
TEAM_NAMES_CLEAN = {
    "inter milan": "Inter",
    "internazionale": "Inter",
    "ac milan": "Milan",
    "milan": "Milan",
    "juventus fc": "Juventus",
    "juventus": "Juventus",
    "as roma": "Roma",
    "roma": "Roma",
    "ss lazio": "Lazio",
    "lazio": "Lazio",
    "ssc napoli": "Napoli",
    "napoli": "Napoli",
    "atalanta bc": "Atalanta",
    "atalanta": "Atalanta",
    "acf fiorentina": "Fiorentina",
    "fiorentina": "Fiorentina",
    "bologna fc": "Bologna",
    "bologna": "Bologna",
    "torino fc": "Torino",
    "torino": "Torino",
    "parma calcio 1913": "Parma",
    "parma": "Parma",
    "cagliari calcio": "Cagliari",
    "cagliari": "Cagliari",
    "empoli fc": "Empoli",
    "empoli": "Empoli",
    "genoa cfc": "Genoa",
    "genoa": "Genoa",
    "ac monza": "Monza",
    "monza": "Monza",
    "us lecce": "Lecce",
    "lecce": "Lecce",
    "udinese calcio": "Udinese",
    "udinese": "Udinese",
    "hellas verona": "Verona",
    "verona": "Verona",
    "venezia fc": "Venezia",
    "venezia": "Venezia",
    "como 1907": "Como",
    "como": "Como",
    "manchester city": "Manchester City",
    "arsenal fc": "Arsenal",
    "arsenal": "Arsenal",
    "liverpool fc": "Liverpool",
    "liverpool": "Liverpool",
    "real madrid": "Real Madrid",
    "fc barcelona": "Barcellona",
    "barcelona": "Barcellona",
    "bayern munich": "Bayern Monaco",
    "bayern munchen": "Bayern Monaco",
    "paris saint germain": "PSG",
    "psg": "PSG"
}

# ID API-Football Ufficiali
API_FOOTBALL_TEAM_IDS = {
    "Inter": 505, "Juventus": 496, "Milan": 489, "Napoli": 492,
    "Atalanta": 499, "Roma": 497, "Lazio": 487, "Fiorentina": 502,
    "Bologna": 500, "Torino": 503, "Parma": 511, "Cagliari": 490,
    "Empoli": 511, "Genoa": 495, "Monza": 1579, "Lecce": 867,
    "Udinese": 494, "Verona": 504, "Venezia": 517, "Como": 880,
    "Arsenal": 42, "Manchester City": 50, "Liverpool": 40,
    "Real Madrid": 541, "Barcellona": 529, "Bayern Monaco": 157, "PSG": 85
}

def clean_team_name(raw_name: str) -> str:
    """Restituisce il nome standard normalizzato della squadra."""
    if not raw_name:
        return ""
    norm = raw_name.strip().lower()
    if norm in TEAM_NAMES_CLEAN:
        return TEAM_NAMES_CLEAN[norm]
    for key, val in TEAM_NAMES_CLEAN.items():
        if key in norm:
            return val
    return raw_name.strip()
