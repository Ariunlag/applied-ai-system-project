# 5-7 Minute Video Walkthrough Script

## 0:00 - 0:30 Intro
"Hi, this is my Music Recommender Simulation with a reliability loop. My original project from Modules  3 was a small classroom music recommender that loaded songs from a CSV file and ranked them with a simple weighted score using genre, mood, energy, and acousticness. The new version adds a multi-step AI workflow with planning, self-checking, and reliability evaluation."

## 0:30 - 1:15 What the project does
"The project matters because it shows how a recommendation system can be made more trustworthy, not just more accurate. It takes a user profile, scores the catalog, revises weak recommendations, and reports reliability metrics so I can see whether the output is stable and reasonable."

## 1:15 - 2:00 Architecture overview
"The system has four main parts. First is retrieval, which loads songs from the CSV catalog. Second is the agent planner, which normalizes the input and adjusts the weights depending on the user's profile. Third is the recommender and evaluator, which rank songs, run a self-check, and produce reliability alerts. Fourth is testing and human review, where I use the evaluation script, pytest, and a manual review of the outputs to decide whether the recommendations look acceptable."

## 2:00 - 3:40 Demo run 1: High-Energy Pop
"First I run the High-Energy Pop profile. Here I'm expecting upbeat pop songs with a strong match on mood and energy. The model should explain why each song was selected and show a reliability summary. I check whether the top recommendations actually match the vibe, whether the consistency score looks reasonable, and whether any guardrail alerts appear."

Show screenshot: [high-energy-pop.png](assets/high-energy-pop.png)

If you want a before-and-after moment, start with [initial-recommendation.png](assets/initial-recommendation.png) and then switch to [high-energy-pop.png](assets/high-energy-pop.png).

## 3:40 - 4:40 Demo run 2: Chill Lofi
"Next I switch to Chill Lofi. This tests whether the system adapts to a different taste profile and whether acoustic preference changes the ranking. I want to show that the same model can behave differently with a different input and still give understandable explanations."

Show screenshot: [chili-pop.png](assets/chili-pop.png)

If you prefer to keep the walkthrough simple, show the Chill Lofi run in the app first, then use [chili-pop.png](assets/chili-pop.png) as the visual proof of a second profile.

## 4:40 - 5:40 Demo run 3: Reliability stress case
"Now I run the reliability stress case with an invalid energy value. This is important because it shows the guardrail behavior. The planner should clip the energy value into a valid range and warn me that the input was out of bounds. This demonstrates that the project doesn't just make a recommendation; it also checks and explains problems in the input."

Show screenshot: [deep-intense-rock.png](assets/deep-intense-rock.png)

Use this after the invalid-input example if you want a high-confidence case on screen, then narrate the guardrail behavior from the live Streamlit output.

## 5:40 - 6:30 Testing and reliability summary
"For testing, I used automated pytest tests plus a separate reliability harness in src/evaluate.py. The evaluator checks normal inputs, unknown labels, and invalid values. One thing that surprised me was that the top recommendations could still look good even when the consistency score was low, which is why I added the reliability output."

## 6:30 - 7:00 Reflection and close
"What I learned is that AI systems need validation and evaluation loops, not just a single prediction step. A helpful AI suggestion was to add the reliability stage after ranking. A flawed suggestion was to over-penalize weak signals too aggressively, which I fixed by making the penalty smaller and combining it with the energy-gap check. Overall, this project taught me to think about AI as a system of inputs, decisions, checks, and human review, not just a model that produces output."
