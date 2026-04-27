# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch Reliability Loop 2.0**

---

## 2. Intended Use

This recommender suggests top songs from a catalog based on a user's taste profile. It generates simple, explainable recommendations for classroom learning and reliability analysis.

It assumes the user can describe their taste with a few preferences: favorite genre, favorite mood, target energy, and whether they like acoustic songs.

This is for classroom exploration and demo use (CLI and Streamlit), not for production use with real users. The Streamlit demo includes both preset profiles and a Custom mode so users can choose catalog-based genres and moods instead of being limited to fixed examples.

---

## 3. How the Model Works

Each song has features like genre, mood, energy, tempo, valence, danceability, and acousticness. The user profile uses genre, mood, energy, and acoustic preference.

For each song, the model calculates a weighted score. It gives points when genre matches, mood matches, energy is close to the target, and acousticness aligns with the user's preference.

The updated system now uses a multi-step process:
1. Planner stage normalizes user inputs and adapts weights for edge cases.
2. Scoring stage ranks candidates.
3. Self-check stage revises weak top-ranked items.
4. Reliability evaluator reports consistency and guardrail alerts.

The final score uses this weighting:
- genre match: 0.35
- mood match: 0.25
- energy fit: 0.25
- acoustic fit: 0.15

After scoring all songs, it sorts by score and returns the top results with plain-language reasons.

Compared to the starter logic, I implemented real scoring, reason generation, numeric data parsing from CSV, a planner plus self-check workflow, and a working CLI-first recommendation flow.

---

## 4. Data

The catalog has **124 songs** from `data/songs.csv`.

The data includes a mix of genres (for example pop, lofi, rock, house, jazz, ambient, folk, electronic, indie pop, soul) and moods (for example happy, chill, intense, romantic, focused, dreamy, warm, confident, reflective).

Compared with the original baseline catalog, this version includes 100 additional entries to improve ranking variety in demos and stress tests.

Missing parts of musical taste include lyrics, language, artist history, listening context, and user behavior data (skips, likes, repeats).

---

## 5. Strengths

The model works well when user preferences are clear, such as:
- High-Energy Pop
- Chill Lofi
- Deep Intense Rock

It captures intuitive patterns like high-energy profiles getting stronger, faster tracks and chill profiles getting lower-energy, often more acoustic songs.

The reliability loop also improves observability by reporting consistency, planner warnings, self-check flags, and guardrail alerts alongside recommendations.

---

## 6. Limitations and Bias

This system is simple and can over-prioritize one feature, especially genre, if the weights are not balanced.

Although the catalog is larger than the baseline, many records are still synthetic and may not represent real listening behavior diversity.

Some genres and moods remain underrepresented, so users with less common tastes may get weaker matches.

The model may also ignore good cross-genre songs that match mood and energy because exact genre matching still has the highest weight.

The consistency metric is a heuristic and not a ground-truth accuracy score.

---

## 7. Evaluation

I evaluated the system by running `python -m src.main`, `python -m src.evaluate`, and `python -m pytest -q`.

Profiles tested include:
- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Additional edge-case/adversarial profiles (missing values, unknown labels, extreme energy values)

I checked whether the top-ranked songs matched the expected vibe and whether the explanation reasons were consistent with the scoring weights.

I ran `python -m src.evaluate` as a reliability harness to test:
- normal profile behavior
- unknown labels
- invalid energy values outside [0, 1]

Recent reliability harness outputs (with 124-song catalog):
- baseline_pop: consistency 0.667, no alerts
- unknown_labels: consistency 0.0, guardrail alert triggered
- invalid_energy: consistency 0.667, planner warning for clipped energy

Automated tests: `5 passed` in `tests/test_recommender.py`.

I also compared behavior after discussing experiments like increasing energy weight and reducing genre weight, and removing mood checks, to see whether recommendations became more accurate or just different.

---

## 8. Future Work

Next improvements I would make:
- Add richer user preferences, such as target acousticness as a number instead of only a boolean.
- Add diversity control so top results are not too similar.
- Add fallback matching for unknown genre/mood values.
- Use valence, tempo, and danceability more actively as secondary tie-breakers.
- Improve explanations by showing each feature's score contribution.
- Replace synthetic catalog expansion with curated real-world metadata.
- Add human-labeled preference sets to evaluate recommendation quality beyond heuristics.

---

## 9. Personal Reflection

I learned that recommender systems can seem smart with simple rules, but quality depends heavily on feature design, data coverage, and evaluation loops.

A surprising result was that top recommendations could still look plausible even when reliability consistency was low, which reinforced the need for explicit guardrail and evaluation output.

This project changed how I think about music apps: recommendations are not only about matching taste, but also about balancing relevance, fairness, variety, and trustworthy evaluation.
