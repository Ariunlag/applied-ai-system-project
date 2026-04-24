"""Reliability harness for the Music Recommender Simulation."""

from .recommender import load_songs, recommend_songs_with_reliability


EVAL_PROFILES = {
    "baseline_pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "likes_acoustic": False,
    },
    "unknown_labels": {
        "genre": "unknown-genre",
        "mood": "unknown-mood",
        "energy": 0.6,
        "likes_acoustic": None,
    },
    "invalid_energy": {
        "genre": "rock",
        "mood": "intense",
        "energy": 1.8,
        "likes_acoustic": False,
    },
}


def run_evaluation() -> None:
    songs = load_songs("data/songs.csv")
    print("Reliability Harness Results")
    print("=" * 40)

    for name, prefs in EVAL_PROFILES.items():
        ranked, report = recommend_songs_with_reliability(prefs, songs, k=3)

        print(f"\nProfile: {name}")
        print(f"Consistency: {report['consistency']}")
        print(f"Planner warnings: {report['planner_warnings']}")
        print(f"Self-check flagged: {report['self_check']['items_flagged']}")
        print(f"Guardrail alerts: {report['guardrail_alerts']}")

        for song, score, explanation in ranked:
            print(f"- {song['title']} ({score:.2f}) :: {explanation}")


if __name__ == "__main__":
    run_evaluation()
