import streamlit as st
import random
import pandas as pd
import math

# --- Initialization & Session State ---

# Initialize session state variables if they don't exist
# This ensures data persists across reruns within the same session

# Core data
if 'teams' not in st.session_state:
    st.session_state.teams = []
if 'sports' not in st.session_state:
    st.session_state.sports = []
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

# Tournament progress
if 'round_number' not in st.session_state:
    st.session_state.round_number = 0 # 0 means setup phase
if 'current_matches' not in st.session_state:
    st.session_state.current_matches = [] # List of dicts for the current round's matches
if 'results_recorded_for_round' not in st.session_state:
    st.session_state.results_recorded_for_round = False
if 'standings' not in st.session_state:
    st.session_state.standings = {} # {team_name: score}
if 'match_history' not in st.session_state:
    st.session_state.match_history = [] # List to store all past matches
if 'bye_team_this_round' not in st.session_state:
    st.session_state.bye_team_this_round = None


# --- Helper Functions ---

def reset_tournament():
    """Clears all session state variables to start fresh."""
    st.session_state.teams = []
    st.session_state.sports = []
    st.session_state.setup_complete = False
    st.session_state.round_number = 0
    st.session_state.current_matches = []
    st.session_state.results_recorded_for_round = False
    st.session_state.standings = {}
    st.session_state.match_history = []
    st.session_state.bye_team_this_round = None
    st.success("Tournament reset!")

def draw_matches(teams, sports, round_num):
    """Draws pairs of teams and assigns sports for the round."""
    if not teams or not sports:
        st.error("Cannot draw matches without teams and sports.")
        return [], None

    num_teams = len(teams)
    shuffled_teams = random.sample(teams, num_teams) # Use sample to not modify original list in state
    available_sports = random.sample(sports, len(sports)) # Shuffle sports too

    matches = []
    bye_team = None

    # Handle odd number of teams
    if num_teams % 2 != 0:
        bye_team = shuffled_teams.pop() # Last team sits out
        st.info(f"Team '{bye_team}' has a bye this round.")
        num_teams -= 1 # Adjust count for pairing

    # Pair teams
    sport_index = 0
    for i in range(0, num_teams, 2):
        team1 = shuffled_teams[i]
        team2 = shuffled_teams[i+1]
        # Cycle through sports
        sport = available_sports[sport_index % len(available_sports)]
        matches.append({
            "round": round_num,
            "team1": team1,
            "team2": team2,
            "sport": sport,
            "winner": None # Placeholder for result
        })
        sport_index += 1

    return matches, bye_team

def update_standings(standings, team1, team2, winner):
    """Updates scores based on match results."""
    if winner == team1:
        standings[team1] = standings.get(team1, 0) + 3
        standings[team2] = standings.get(team2, 0) + 0 # Explicitly add 0 if team not present
    elif winner == team2:
        standings[team2] = standings.get(team2, 0) + 3
        standings[team1] = standings.get(team1, 0) + 0 # Explicitly add 0 if team not present
    elif winner == "Draw":
        standings[team1] = standings.get(team1, 0) + 1
        standings[team2] = standings.get(team2, 0) + 1
    # Ensure all teams exist in standings even if they haven't scored
    if team1 not in standings: standings[team1] = 0
    if team2 not in standings: standings[team2] = 0


# --- App Layout ---

st.title("🏆 Sports Event Manager")

# --- Setup Section ---
if not st.session_state.setup_complete:
    st.header("⚙️ 1. Setup Tournament")

    team_input = st.text_area("Enter Team Names (one per line, 4 or more required):", height=150)
    sport_input = st.text_area("Enter Sport Names (one per line, 4-5 recommended):", height=100)

    if st.button("Confirm Setup & Start Tournament"):
        teams = [team.strip() for team in team_input.split('\n') if team.strip()]
        sports = [sport.strip() for sport in sport_input.split('\n') if sport.strip()]

        # Validation
        error = False
        if len(teams) < 4:
            st.error("Please enter at least 4 teams.")
            error = True
        if len(sports) < 4 :
             st.warning("Fewer than 4 sports entered. Proceeding, but 4-5 are recommended.")
             # Proceed even if fewer than 4 sports, but warn
        # You could add stricter validation for 4-5 sports if needed:
        # if not (4 <= len(sports) <= 5):
        #    st.error("Please enter between 4 and 5 sports.")
        #    error = True

        if not error:
            st.session_state.teams = teams
            st.session_state.sports = sports
            # Initialize standings with 0 points for all teams
            st.session_state.standings = {team: 0 for team in teams}
            st.session_state.round_number = 1 # Move to round 1
            st.session_state.setup_complete = True
            st.session_state.results_recorded_for_round = True # Start ready to draw round 1
            st.success("Setup complete! Ready for Round 1.")
            st.rerun() # Rerun to hide setup and show round management

# --- Tournament Active Section ---
else:
    st.sidebar.header("Tournament Controls")
    if st.sidebar.button("⚠️ Reset Tournament"):
        reset_tournament()
        st.rerun()

    st.sidebar.header("Current State")
    st.sidebar.write(f"**Teams:** {', '.join(st.session_state.teams)}")
    st.sidebar.write(f"**Sports:** {', '.join(st.session_state.sports)}")
    st.sidebar.write(f"**Current Round:** {st.session_state.round_number}")

    st.header(f"🏁 Round {st.session_state.round_number}")

    # --- Match Drawing ---
    # Only show draw button if results for the *previous* round were recorded
    # or if it's the very first round after setup
    if st.session_state.results_recorded_for_round:
        if st.button(f"Draw Matches for Round {st.session_state.round_number}"):
            st.session_state.current_matches, st.session_state.bye_team_this_round = draw_matches(
                st.session_state.teams,
                st.session_state.sports,
                st.session_state.round_number
            )
            if st.session_state.current_matches: # If drawing was successful
                 st.session_state.results_recorded_for_round = False # Need to record results now
                 st.rerun() # Rerun to display the drawn matches section

    # --- Display Matches & Record Results ---
    # Show this section only if matches have been drawn for the current round
    # AND results haven't been submitted yet
    if not st.session_state.results_recorded_for_round and st.session_state.current_matches:
        st.subheader("Matches for this Round:")

        # Display Bye team info if applicable
        if st.session_state.bye_team_this_round:
             st.info(f"**Bye:** {st.session_state.bye_team_this_round} sits out this round.")

        results_input = {}
        for i, match in enumerate(st.session_state.current_matches):
            match_label = f"**{match['sport']}**: {match['team1']} vs {match['team2']}"
            # Use unique keys for each selectbox based on round and index
            key = f"round_{st.session_state.round_number}_match_{i}"
            winner_options = [match['team1'], match['team2'], "Draw"]
            results_input[i] = st.selectbox(match_label, options=winner_options, index=None, key=key, placeholder="Select Winner/Draw") # index=None for default empty selection

        if st.button(f"Submit Results for Round {st.session_state.round_number}"):
            all_results_entered = True
            temp_match_updates = [] # Store updates temporarily

            for i, match in enumerate(st.session_state.current_matches):
                selected_winner = results_input.get(i)
                if selected_winner is None:
                    all_results_entered = False
                    st.warning(f"Please select a result for the match: {match['team1']} vs {match['team2']}")
                else:
                    # Update the match dictionary with the winner
                    updated_match = match.copy() # Avoid modifying the list while iterating
                    updated_match["winner"] = selected_winner
                    temp_match_updates.append(updated_match)

                    # Update standings immediately based on selection
                    update_standings(st.session_state.standings, match['team1'], match['team2'], selected_winner)

            if all_results_entered:
                # Add the finalized matches of this round to history
                st.session_state.match_history.extend(temp_match_updates)
                # Clear current matches for the next draw
                st.session_state.current_matches = []
                # Clear bye team
                st.session_state.bye_team_this_round = None
                # Mark results as recorded
                st.session_state.results_recorded_for_round = True
                # Increment round number
                st.session_state.round_number += 1
                st.success(f"Results for Round {st.session_state.round_number - 1} submitted!")
                st.rerun() # Rerun to prepare for the next round's drawing

    # --- Display Standings ---
    st.header("📊 Standings")
    if st.session_state.standings:
        # Convert standings dict to DataFrame for better display & sorting
        standings_df = pd.DataFrame(list(st.session_state.standings.items()), columns=['Team', 'Score'])
        standings_df = standings_df.sort_values(by='Score', ascending=False).reset_index(drop=True)
        standings_df.index += 1 # Start index from 1 for rank
        st.dataframe(standings_df, use_container_width=True)
    else:
        st.info("Standings will appear here once results are recorded.")

    # --- Display Match History (Optional) ---
    st.header("📜 Match History")
    if st.session_state.match_history:
        history_df = pd.DataFrame(st.session_state.match_history)
        # Reorder columns for clarity
        history_df = history_df[['round', 'sport', 'team1', 'team2', 'winner']]
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("Completed matches will appear here.")