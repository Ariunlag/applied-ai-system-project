"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs_with_reliability


USER_PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.9,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.95,
        "likes_acoustic": False,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs\n")

    for selected_profile, user_prefs in USER_PROFILES.items():
        print(f"Using profile: {selected_profile}")

        recommendations, reliability = recommend_songs_with_reliability(user_prefs, songs, k=5)

        print("\nTop recommendations:\n")
        for rec in recommendations:
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()

        print("Reliability summary:")
        print(f"- consistency: {reliability['consistency']}")
        print(f"- planner warnings: {len(reliability['planner_warnings'])}")
        print(f"- items flagged by self-check: {reliability['self_check']['items_flagged']}")
        if reliability["guardrail_alerts"]:
            print(f"- alerts: {', '.join(reliability['guardrail_alerts'])}")
        else:
            print("- alerts: none")
        print("\n" + "=" * 48 + "\n")


if __name__ == "__main__":
    main()
