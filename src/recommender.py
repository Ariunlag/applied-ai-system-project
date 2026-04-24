import csv
from typing import Any, List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Song metadata and audio-style features used for recommendation.

    Attributes:
        id: Unique integer song identifier.
        title: Song title.
        artist: Artist name.
        genre: Genre label (for example, pop or lofi).
        mood: Mood label (for example, happy or chill).
        energy: Energy value in the range [0, 1].
        tempo_bpm: Tempo in beats per minute.
        valence: Positivity value in the range [0, 1].
        danceability: Danceability value in the range [0, 1].
        acousticness: Acousticness value in the range [0, 1].
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    User taste preferences for personalized scoring.

    Attributes:
        favorite_genre: User's preferred genre label.
        favorite_mood: User's preferred mood label.
        target_energy: Desired energy level in the range [0, 1].
        likes_acoustic: True if user prefers acoustic songs.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    Object-oriented wrapper for recommendation behavior.

    This class is kept for test compatibility and future extension.
    """
    def __init__(self, songs: List[Song]):
        """Initialize the recommender with an in-memory song list."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """
        Return up to k songs for the given user.

        This delegates to the same workflow as the dictionary-based API so
        behavior stays consistent across tests and CLI usage.
        """
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        song_dicts = [song_to_dict(song) for song in self.songs]
        ranked = recommend_songs(user_prefs, song_dicts, k=k)

        # Map ranked dictionaries back to Song objects for test compatibility.
        by_id = {song.id: song for song in self.songs}
        return [by_id[item[0]["id"]] for item in ranked if item[0]["id"] in by_id]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """
        Return a plain-language explanation for why a song was suggested.

        Explanation mirrors the reasoning produced by score_song().
        """
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        _, reasons = score_song(user_prefs, song_to_dict(song))
        return "; ".join(reasons) if reasons else "overall match with preferences"


def song_to_dict(song: Song) -> Dict[str, Any]:
    """Convert Song dataclass to dictionary expected by ranking helpers."""
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
    }


def _clip01(value: float) -> float:
    """Clamp value into [0, 1] for safer scoring arithmetic."""
    return max(0.0, min(1.0, value))


def _normalize_user_prefs(user_prefs: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Normalize and validate raw user inputs for reliable downstream behavior.

    Returns:
        (normalized_prefs, warnings)
    """
    warnings: List[str] = []

    genre = str(user_prefs.get("genre", "")).strip().lower()
    mood = str(user_prefs.get("mood", "")).strip().lower()

    try:
        energy = float(user_prefs.get("energy", 0.5))
    except (TypeError, ValueError):
        warnings.append("invalid energy input; defaulted to 0.5")
        energy = 0.5

    if energy < 0.0 or energy > 1.0:
        warnings.append("energy outside [0,1]; clipped to valid range")
    energy = _clip01(energy)

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic not in (True, False, None):
        warnings.append("invalid likes_acoustic value; treated as unknown")
        likes_acoustic = None

    normalized = {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": likes_acoustic,
    }
    return normalized, warnings


def plan_scoring_strategy(user_prefs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Plan a scoring strategy from user intent.

    This is a lightweight planner stage that dynamically adjusts weights,
    acting as a multi-step AI behavior instead of one fixed scoring rule.
    """
    normalized, warnings = _normalize_user_prefs(user_prefs)
    energy = normalized["energy"]

    weights = {
        "genre": 0.35,
        "mood": 0.25,
        "energy": 0.25,
        "acoustic": 0.15,
    }

    # For extreme energy preferences, promote energy alignment.
    if energy >= 0.85 or energy <= 0.15:
        weights = {
            "genre": 0.30,
            "mood": 0.20,
            "energy": 0.35,
            "acoustic": 0.15,
        }

    # If acoustic preference is unknown, reduce its influence.
    if normalized["likes_acoustic"] is None:
        weights = {
            "genre": weights["genre"] + 0.05,
            "mood": weights["mood"] + 0.05,
            "energy": weights["energy"] + 0.05,
            "acoustic": max(0.0, weights["acoustic"] - 0.15),
        }

    return {
        "normalized_profile": normalized,
        "weights": weights,
        "warnings": warnings,
    }

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from CSV and return them as dictionaries.

    Numeric columns are converted to numeric Python types so downstream
    scoring can run without additional casting.

    Args:
        csv_path: Relative or absolute path to the songs CSV file.

    Returns:
        A list of song dictionaries with typed values.
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            }
            songs.append(song)
    return songs

def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """
    Score one song against user preferences.

    Uses a simple weighted formula:
        score = 0.35*genre_match + 0.25*mood_match +
                0.25*energy_fit + 0.15*acoustic_fit

    Args:
        user_prefs: User preference dictionary with keys like
            genre, mood, energy, and likes_acoustic.
        song: Song dictionary with feature keys loaded from CSV.

    Returns:
        Tuple of (numeric_score, reasons_list).
    """
    if weights is None:
        weights = {
            "genre": 0.35,
            "mood": 0.25,
            "energy": 0.25,
            "acoustic": 0.15,
        }

    # Extract user preferences
    favorite_genre = str(user_prefs.get("genre", "")).lower()
    favorite_mood = str(user_prefs.get("mood", "")).lower()
    target_energy = _clip01(float(user_prefs.get("energy", 0.5)))
    likes_acoustic = user_prefs.get("likes_acoustic")
    
    # Extract song features
    song_genre = str(song.get("genre", "")).lower()
    song_mood = str(song.get("mood", "")).lower()
    song_energy = _clip01(float(song.get("energy", 0.5)))
    song_acousticness = _clip01(float(song.get("acousticness", 0.5)))
    
    # Calculate score components
    genre_match = 1.0 if song_genre == favorite_genre else 0.0
    mood_match = 1.0 if song_mood == favorite_mood else 0.0
    energy_fit = max(0.0, 1.0 - abs(song_energy - target_energy))
    
    # Acoustic fit
    if likes_acoustic is None:
        acoustic_fit = 0.5
        acoustic_reason = None
    elif likes_acoustic:
        acoustic_fit = song_acousticness
        acoustic_reason = "matches acoustic preference" if song_acousticness > 0.5 else None
    else:
        acoustic_fit = 1.0 - song_acousticness
        acoustic_reason = "matches non-acoustic preference" if song_acousticness < 0.5 else None
    
    # Weighted score
    score = (
        weights["genre"] * genre_match +
        weights["mood"] * mood_match +
        weights["energy"] * energy_fit +
        weights["acoustic"] * acoustic_fit
    )
    
    # Build reasons list
    reasons = []
    if genre_match > 0:
        reasons.append(f"genre matches {favorite_genre}")
    if mood_match > 0:
        reasons.append(f"mood matches {favorite_mood}")
    if energy_fit >= 0.8:
        reasons.append(f"energy is close to target ({song_energy:.2f})")
    if acoustic_reason:
        reasons.append(acoustic_reason)
    
    return score, reasons


def self_check_and_revise(
    ranked_items: List[Tuple[Dict, float, str]],
    user_prefs: Dict[str, Any],
    top_n: int = 5,
) -> Tuple[List[Tuple[Dict, float, str]], Dict[str, Any]]:
    """
    Reliability self-check stage that revises weak top-ranked items.

    If an item in top_n has weak alignment (few reasons and large energy gap),
    apply a small penalty and re-rank.
    """
    if not ranked_items:
        return ranked_items, {
            "items_flagged": 0,
            "checks_run": 0,
            "notes": ["no candidates to evaluate"],
        }

    target_energy = float(user_prefs.get("energy", 0.5))
    revised: List[Tuple[Dict, float, str]] = []
    checks_run = 0
    flagged = 0
    notes: List[str] = []

    for index, (song, score, explanation) in enumerate(ranked_items):
        checks_run += 1
        if index >= top_n:
            revised.append((song, score, explanation))
            continue

        reason_count = len([part for part in explanation.split(";") if part.strip()])
        energy_gap = abs(float(song.get("energy", 0.5)) - target_energy)

        if reason_count < 2 and energy_gap > 0.35:
            flagged += 1
            penalized_score = max(0.0, score - 0.08)
            revised_explanation = f"{explanation}; revised after self-check"
            revised.append((song, penalized_score, revised_explanation))
            notes.append(f"penalized {song.get('title', 'unknown')} for weak alignment")
        else:
            revised.append((song, score, explanation))

    revised.sort(key=lambda item: item[1], reverse=True)
    return revised, {
        "items_flagged": flagged,
        "checks_run": checks_run,
        "notes": notes,
    }


def evaluate_reliability(
    normalized_profile: Dict[str, Any],
    ranked_items: List[Tuple[Dict, float, str]],
) -> Dict[str, Any]:
    """Produce a compact reliability report for demos and testing."""
    if not ranked_items:
        return {
            "valid": False,
            "consistency": 0.0,
            "guardrail_alerts": ["no recommendations produced"],
        }

    top = ranked_items[: min(5, len(ranked_items))]
    expected_genre = normalized_profile.get("genre", "")
    expected_mood = normalized_profile.get("mood", "")

    matches = 0
    alerts: List[str] = []
    for song, _, _ in top:
        if expected_genre and str(song.get("genre", "")).lower() == expected_genre:
            matches += 1
        if expected_mood and str(song.get("mood", "")).lower() == expected_mood:
            matches += 1

    possible = 2 * len(top)
    consistency = matches / possible if possible else 0.0

    if consistency < 0.35:
        alerts.append("low profile consistency in top recommendations")

    return {
        "valid": True,
        "consistency": round(consistency, 3),
        "guardrail_alerts": alerts,
    }


def recommend_songs_with_reliability(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> Tuple[List[Tuple[Dict, float, str]], Dict[str, Any]]:
    """
    Multi-step recommendation pipeline.

    Steps:
    1) Plan strategy from user profile.
    2) Score all songs with adaptive weights.
    3) Run self-check and revise ranking.
    4) Produce reliability report.
    """
    plan = plan_scoring_strategy(user_prefs)
    normalized = plan["normalized_profile"]
    weights = plan["weights"]

    scored_songs: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(normalized, song, weights=weights)
        explanation = "; ".join(reasons) if reasons else "overall match with preferences"
        scored_songs.append((song, score, explanation))

    scored_songs.sort(key=lambda item: item[1], reverse=True)
    revised_ranked, self_check = self_check_and_revise(scored_songs, normalized, top_n=k)

    reliability = evaluate_reliability(normalized, revised_ranked[:k])
    reliability["planner_warnings"] = plan["warnings"]
    reliability["self_check"] = self_check
    reliability["weights"] = weights

    return revised_ranked[:k], reliability

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Recommend top-k songs by scoring and ranking the catalog.

    Args:
        user_prefs: User taste profile used for scoring.
        songs: List of song dictionaries.
        k: Number of recommendations to return.

    Returns:
        A list of tuples in the form:
        (song_dict, score, explanation_string), sorted by score descending.
    """
    ranked, _ = recommend_songs_with_reliability(user_prefs, songs, k=k)
    return ranked
