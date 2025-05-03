import streamlit as st
from streamlit_gsheets import GSheetsConnection
from PIL import Image
import random
import pandas as pd

from utils import get_team_picture, get_sport_picture

# Connect to Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# Set the page config for Streamlit
st.set_page_config(page_title="Munich Mixed Mixed Games", layout="centered")

# --- Header ---
st.title("🏟️ Munich Mixed Mixed Games 🏟️")
st.write("Save the date: 14.06.2025.")
st.write("More information coming soon!")



# --- Game Pairings Section ---
st.divider()
st.subheader("🎲 Next Round Draw")

# Button to trigger the pairing and sport assignment
if st.button("Draw Pairings"):
    # Assuming 'df' has columns 'Teams' and 'Sports'
    teams = df['Teams'].dropna().tolist()
    sports = df['Sports'].dropna().tolist()

    # Shuffle teams and sports randomly
    random.shuffle(teams)
    random.shuffle(sports)

    # Draw pairings (team1, team2) - if odd, the last team will remain free
    if len(teams) % 2 == 0:
        # Even number of teams, pair them all
        pairings = [(teams[i], teams[i+1]) for i in range(0, len(teams), 2)]
        free_team = None
    else:
        # Odd number of teams, one will remain free
        pairings = [(teams[i], teams[i+1]) for i in range(0, len(teams)-1, 2)]
        free_team = teams[-1]

    # Ensure that we don't assign more pairings than available sports
    if len(pairings) > len(sports):
        pairings = pairings[:len(sports)]  # Limit pairings to available sports

    # Assign sports to the pairings
    pairing_sports = {f'{team1} vs {team2}': sports[i] for i, (team1, team2) in enumerate(pairings)}

    # Create a structured table for the pairings
    pairing_data = []
    for (team1, team2), sport in zip(pairings, sports[:len(pairings)]):
        pairing_data.append([team1, team2, sport])

    # Convert the pairing data into a pandas DataFrame and display it as a table
    pairing_df = pd.DataFrame(pairing_data, columns=["Team A", "Team B", "Sport"])
    st.table(pairing_df)  # Display the table in Streamlit

    # If there is an odd team, display the free team
    if free_team:
        st.write(f"Free Team: {free_team}")

# --- Results Table ---
st.divider()
st.subheader("🏁 Results Table")
st.write("Coming soon!")

# --- Registered Teams And Sports ---
st.divider()
st.subheader("🫂 Registered Teams And Sports 🏅")

# Get unique teams and sports from the dataframe
unique_teams = df["Teams"].dropna().unique()
unique_sports = df["Sports"].dropna().unique()

# Main Layout Columns: Teams on Left, Divider in Center, Sports on Right
main_cols = st.columns([3, 0.2, 3])

# Teams Column (Left)
with main_cols[0]:
    if len(unique_teams) == 0:
        st.info("No teams registered yet.")
    else:
        # Display each unique team
        for team in unique_teams:
            team_img_path = get_team_picture(team)
            item_cols = st.columns([1, 3])  # Adjust ratio as needed

            with item_cols[0]:  # Image column
                if team_img_path:
                    try:
                        img = Image.open(team_img_path)
                        st.image(img, width=200)
                    except Exception as e:
                        st.error(f"Error loading image for {team}", icon="⚠️")

            with item_cols[1]:  # Name column
                st.markdown(f"**{team}**")

            st.write("")  # Add a small vertical space between team entries

# Divider Column (Center)
with main_cols[1]:
    st.markdown(
        """
        <div style='display: flex; justify-content: center; height: 500px;'>
            <div style='border-left: 1px solid #CCC; height: 100%;'></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Sports Column (Right)
with main_cols[2]:
    if len(unique_sports) == 0:
        st.info("No sports listed yet.")
    else:
        # Display each unique sport
        for sport in unique_sports:
            sport_img_path = get_sport_picture(sport)
            item_cols = st.columns([1, 3])  # Adjust ratio as needed

            with item_cols[0]:  # Image column
                if sport_img_path:
                    try:
                        img = Image.open(sport_img_path)
                        st.image(img, width=200)
                    except Exception as e:
                        st.error(f"Error loading image for {sport}", icon="⚠️")
                        st.write("🎯")  # Fallback icon if image is missing
                else:
                    st.write("🎯")  # Placeholder if no image path

            with item_cols[1]:  # Name column
                st.markdown(f"**{sport}**")

            st.write("")  # Add a small vertical space between sport entries
