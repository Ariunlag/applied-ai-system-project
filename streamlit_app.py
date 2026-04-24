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


@st.cache_data
def get_catalog():
    return load_songs("data/songs.csv")


def profile_inputs(profile_name: str):
    default = DEMO_PROFILES[profile_name]
    st.sidebar.subheader("Demo Profile")
    genre = st.sidebar.text_input("Genre", value=default["genre"])
    mood = st.sidebar.text_input("Mood", value=default["mood"])
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
profile_name = st.sidebar.selectbox("Choose a demo profile", list(DEMO_PROFILES.keys()))
user_prefs = profile_inputs(profile_name)
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
        "Use these to record your video walkthrough: High-Energy Pop, Chill Lofi, Deep Intense Rock, and the Reliability Stress Case."
    )
    preview = []
    for name, profile in DEMO_PROFILES.items():
        preview.append({"Profile": name, **profile})
    st.dataframe(pd.DataFrame(preview), use_container_width=True, hide_index=True)
