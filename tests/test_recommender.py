from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    plan_scoring_strategy,
    recommend_songs,
    recommend_songs_with_reliability,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_strategy_planner_clips_invalid_energy_and_warns():
    plan = plan_scoring_strategy(
        {
            "genre": "Pop",
            "mood": "Happy",
            "energy": 1.8,
            "likes_acoustic": "sometimes",
        }
    )

    normalized = plan["normalized_profile"]
    assert normalized["energy"] == 1.0
    assert normalized["likes_acoustic"] is None
    assert len(plan["warnings"]) >= 1


def test_recommend_songs_with_reliability_returns_report():
    songs = [
        {
            "id": 1,
            "title": "Pop Spark",
            "artist": "A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.9,
            "tempo_bpm": 120,
            "valence": 0.8,
            "danceability": 0.7,
            "acousticness": 0.1,
        },
        {
            "id": 2,
            "title": "Calm Air",
            "artist": "B",
            "genre": "ambient",
            "mood": "chill",
            "energy": 0.2,
            "tempo_bpm": 78,
            "valence": 0.3,
            "danceability": 0.2,
            "acousticness": 0.9,
        },
    ]
    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
    }

    ranked, report = recommend_songs_with_reliability(prefs, songs, k=2)
    assert len(ranked) == 2
    assert report["valid"] is True
    assert "consistency" in report
    assert "self_check" in report
    assert ranked[0][0]["genre"] == "pop"


def test_recommend_songs_preserves_legacy_shape():
    songs = [
        {
            "id": 1,
            "title": "Match",
            "artist": "A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.8,
            "danceability": 0.7,
            "acousticness": 0.2,
        }
    ]
    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    ranked = recommend_songs(prefs, songs, k=1)
    assert len(ranked) == 1
    song, score, explanation = ranked[0]
    assert song["title"] == "Match"
    assert isinstance(score, float)
    assert isinstance(explanation, str)
