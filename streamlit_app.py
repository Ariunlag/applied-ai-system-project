import pandas as pd
import streamlit as st

from src.recommender import load_songs, recommend_songs_with_reliability


DEMO_PROFILES = {
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
    "Reliability Stress Case": {
        "genre": "rock",
        "mood": "intense",
        "energy": 1.8,
        "likes_acoustic": False,
    },
}


def _catalog_options(catalog, key: str):
    return sorted({str(song[key]).strip().lower() for song in catalog if str(song.get(key, "")).strip()})


@st.cache_data
def get_catalog():
    return load_songs("data/songs.csv")


def profile_inputs(profile_name: str, catalog):
    st.sidebar.subheader("Demo Profile")

    genre_choices = _catalog_options(catalog, "genre")
    mood_choices = _catalog_options(catalog, "mood")

    if profile_name == "Custom":
        genre = st.sidebar.selectbox("Genre", genre_choices, index=0 if genre_choices else None)
        mood = st.sidebar.selectbox("Mood", mood_choices, index=0 if mood_choices else None)
        energy = st.sidebar.slider("Target energy", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        likes_acoustic = st.sidebar.selectbox("Acoustic preference", ["Unknown", "Yes", "No"], index=0)
        likes_acoustic = {"Yes": True, "No": False}.get(likes_acoustic, None)
    else:
        default = DEMO_PROFILES[profile_name]
        genre = st.sidebar.selectbox("Genre", [default["genre"]] + [g for g in genre_choices if g != default["genre"]])
        mood = st.sidebar.selectbox("Mood", [default["mood"]] + [m for m in mood_choices if m != default["mood"]])
        energy = st.sidebar.slider("Target energy", min_value=0.0, max_value=2.0, value=float(default["energy"]), step=0.01)
        likes_acoustic = st.sidebar.checkbox("Likes acoustic songs", value=bool(default["likes_acoustic"]))
    return {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": likes_acoustic,
    }


def render_recommendations(recommendations):
    rows = []
    for song, score, explanation in recommendations:
        rows.append(
            {
                "Title": song["title"],
                "Artist": song["artist"],
                "Genre": song["genre"],
                "Mood": song["mood"],
                "Energy": song["energy"],
                "Score": round(score, 3),
                "Why": explanation,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


st.set_page_config(page_title="Music Recommender Demo", page_icon="🎵", layout="wide")
st.title("Music Recommender Simulation with Reliability Loop")
st.caption("End-to-end demo: profile input -> adaptive scoring -> self-check -> reliability output")

st.markdown(
    """
    This demo shows the same workflow used in the CLI.
    Pick one of the built-in profiles or edit the sidebar fields, then run the recommender.
    """
)

catalog = get_catalog()
profile_name = st.sidebar.selectbox("Choose a demo profile", ["Custom"] + list(DEMO_PROFILES.keys()))
user_prefs = profile_inputs(profile_name, catalog)
run_button = st.sidebar.button("Run recommendation")

col1, col2 = st.columns([1.2, 1])
with col1:
    st.subheader("Catalog Summary")
    st.write(f"Loaded {len(catalog)} songs from data/songs.csv")
    st.write("This project uses a fixed catalog, so the same input will always produce the same output.")

with col2:
    st.subheader("Selected Input")
    st.json(user_prefs)

if run_button:
    recommendations, report = recommend_songs_with_reliability(user_prefs, catalog, k=5)

    st.divider()
    st.subheader("AI Output")
    st.success("Recommendation run completed")

    metrics = st.columns(4)
    metrics[0].metric("Consistency", report["consistency"])
    metrics[1].metric("Planner warnings", len(report["planner_warnings"]))
    metrics[2].metric("Self-check flags", report["self_check"]["items_flagged"])
    metrics[3].metric("Guardrail alerts", len(report["guardrail_alerts"]))

    if report["planner_warnings"]:
        st.warning("Planner warnings: " + "; ".join(report["planner_warnings"]))
    if report["guardrail_alerts"]:
        st.error("Guardrail alerts: " + "; ".join(report["guardrail_alerts"]))
    elif report["self_check"]["notes"]:
        st.info("Self-check notes: " + "; ".join(report["self_check"]["notes"]))

    st.subheader("Top Recommendations")
    render_recommendations(recommendations)

    with st.expander("See reliability details"):
        st.json(report)

    with st.expander("Human review checklist"):
        st.write("1. Do the top songs match the selected vibe?")
        st.write("2. Are the explanations consistent with the scores?")
        st.write("3. Do the reliability metrics look acceptable before using the output?")
else:
    st.info("Choose a profile and click Run recommendation to see the end-to-end system.")
    st.subheader("Example Profiles")
    st.write(
        "Use the built-in profiles for your video walkthrough, or choose Custom to test any genre and mood available in the catalog."
    )
    preview = []
    for name, profile in DEMO_PROFILES.items():
        preview.append({"Profile": name, **profile})
    st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
