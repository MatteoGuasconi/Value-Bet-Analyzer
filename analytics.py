"""
Motore Matematico e Quantitativo per Value Bet (+EV).
Include:
- Calcolo e normalizzazione Per 90 Minuti (P90)
- Distribuzione di Poisson con ponderazione difensiva e arbitrale
- Calcolo Fair Odds (Quota Reale) ed Expected Value (Edge %)
- Money Management con Criterio di Kelly Frazionario
"""

import numpy as np
from scipy.stats import poisson

def calculate_p90(total_events: float, minutes_played: float) -> float:
    """Calcola la media normalizzata per 90 minuti di gioco."""
    if minutes_played <= 0:
        return 0.0
    return float((total_events / minutes_played) * 90.0)

def calculate_weighted_lambda(
    player_p90: float,
    opp_conceded_avg: float,
    league_avg_conceded: float = 4.30,
    ref_factor: float = 1.0,
    expected_minutes: float = 84.0
) -> float:
    """
    Calcola il parametro Lambda ponderato per la distribuzione di Poisson.
    Considera:
    1. Performance P90 del giocatore
    2. Minuti medi stimati in campo
    3. Tasso di concessione della difesa avversaria rispetto alla media lega
    4. Moltiplicatore di severita dell'arbitro
    """
    if league_avg_conceded <= 0:
        league_avg_conceded = 4.30
    opp_ratio = opp_conceded_avg / league_avg_conceded
    minutes_ratio = expected_minutes / 90.0
    
    lambd = player_p90 * minutes_ratio * opp_ratio * ref_factor
    return max(0.01, float(lambd))

def calculate_poisson_over_prob(lambd: float, line: float) -> float:
    """
    Calcola la probabilita P(X > line) usando la distribuzione cumulativa di Poisson.
    Per esempio:
    - Over 0.5 -> P(X > 0) = 1 - P(X = 0)
    - Over 1.5 -> P(X > 1) = 1 - P(X <= 1)
    """
    k = int(np.floor(line))
    prob = 1.0 - float(poisson.cdf(k, lambd))
    return max(0.001, min(0.999, prob))

def calculate_fair_odds(prob: float, max_odds: float = 20.0) -> float:
    """Calcola la Quota Equa (Fair Odd) pura: 1 / Probabilita."""
    if prob <= 0.001:
        return max_odds
    return min(max_odds, round(1.0 / prob, 2))

def calculate_min_value_odds(prob: float, min_edge: float = 0.015, max_odds: float = 20.0) -> float:
    """Calcola la Quota Minima di Ingresso per avere il margine matematico minimo richiesto."""
    if prob <= 0.001:
        return max_odds
    return min(max_odds, round((1.0 + min_edge) / prob, 2))

def calculate_edge(prob: float, bookmaker_odds: float) -> float:
    """Calcola il Valore Atteso / Edge percentuale: (Probabilita * Quota) - 1."""
    if bookmaker_odds <= 1.0:
        return -1.0
    return float((prob * bookmaker_odds) - 1.0)

def calculate_kelly_stake(
    prob: float,
    odds: float,
    bankroll: float,
    kelly_fraction: float = 0.50,
    max_cap_pct: float = 0.10
) -> tuple[float, float]:
    """
    Calcola la percentuale e l'importo monetario di puntata con Criterio di Kelly Frazionario.
    Include cap di sicurezza sul bankroll per azzerare il rischio di rovina.
    """
    b = odds - 1.0
    if b <= 0 or prob <= 0:
        return 0.0, 0.0
    
    p_loss = 1.0 - prob
    k_full = (prob * b - p_loss) / b
    if k_full <= 0:
        return 0.0, 0.0
    
    k_scaled = k_full * kelly_fraction
    final_pct = min(k_scaled, max_cap_pct)
    monetary = round(bankroll * final_pct, 2)
    return round(final_pct * 100, 2), monetary

class ValueBetEngine:
    """Motore quantitativo specializzato per l'analisi di tutte le linee statistiche."""
    
    @staticmethod
    def analyze_player_stat(
        player_name: str,
        role: str,
        p90_val: float,
        opp_conceded: float,
        league_conceded_avg: float,
        line: float,
        market_name: str,
        book_odds: float,
        ref_factor: float = 1.0,
        expected_mins: float = 85.0,
        is_starter: bool = True
    ) -> dict:
        lambd = calculate_weighted_lambda(p90_val, opp_conceded, league_conceded_avg, ref_factor, expected_mins)
        prob = calculate_poisson_over_prob(lambd, line)
        fair_odd = calculate_fair_odds(prob)
        min_odd = calculate_min_value_odds(prob, min_edge=0.02)
        edge = calculate_edge(prob, book_odds)
        
        return {
            "player": player_name,
            "role": role,
            "market": f"Over {line} {market_name}",
            "line": line,
            "lambda": round(lambd, 2),
            "p90": round(p90_val, 2),
            "prob": prob,
            "prob_pct": f"{prob * 100:.1f}%",
            "fair_odds": fair_odd,
            "min_odds": min_odd,
            "book_odds": book_odds,
            "edge": edge,
            "edge_pct": f"{edge * 100:+.2f}%",
            "is_value": edge >= 0.02 and book_odds >= min_odd,
            "is_starter": is_starter
        }
