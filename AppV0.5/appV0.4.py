import joblib
import numpy as np
import pandas as pd
import streamlit as st
import base64

# function to read in image as base54
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


logo_path = "Media/super_rugby_logo_big.png"
logo_base64 = get_base64_of_bin_file(logo_path)

# logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="200" alt="Logo">'

# logo_top_class = "logo-top"
# logo_right_class = "logo-right"
# logo_width_class = "logo-width"


# logo html style and markdown
logo_html = f"""
    <style>
        .logo {{
            position: fixed;
            top: 10px;
            right: 10px;
            width: 300px;
            padding-top: 50px;
            padding-bottom: 50px;
            padding-left: 100px;
            padding-right: 50px;
        }}
    </style>
    <img src="data:image/png;base64,{logo_base64}" class="logo" alt="Logo">
"""
st.markdown(logo_html, unsafe_allow_html=True)

# Get data in here
file = "Collab/ability_df.csv"

# Preform filtering of data here:
player = pd.read_csv('Collab/ability_df.csv', sep=';').fillna(0).iloc[:,:]

# Title of the app
st.title('Super Rugby Fantasy Draft')
# Sidebar for user inputs
# st.sidebar.header('Navigation')

# # Function to add player to team DataFrame
# def add_player_to_team(player_id, team_df):
#     player_to_be_added = player[player["player_id"] == player_id]
#     team_df = team_df.concat(player_to_be_added, ignore_index=True)
#     return team_df

# # Function to add player to team DataFrame
# def add_player_name_to_team(player_name, team_df):
#     player_to_be_added = player[player["name"] == player_name]
#     team_df = team_df.concat(player_to_be_added, ignore_index=True)
#     return team_df


# Tab system of app

# Set up the tabs
tabs = ['Player Stats', "Draft", "Player Stats Leaderboard"]

tab1, tab2, tab3 = st.tabs(tabs)

with tab1:
    st.markdown(
        f"""
        <style>
        .main .block-container {{
            max-width: 90%;
            padding: 1rem 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    # Tab Player Stats header
    st.header("Summary")
    st.text("Using data from 2022-2024 Super Rugby data, this app predicts winners of matches using a specified assortment of team members")
    st.text("This app was produced by:\nJohn Lavack - 20001249\nSeunghyeok Kang - 20010572\nJonathan Tan - 15156031\n\n\n297201 Project 3, 2024")
    # Output dataframe
    # st.dataframe(player)

with tab2:
    st.header("Draft")
    
    centered_player_df = player.style.set_properties(**{'text-align': 'center'})

    # Display the centered DataFrame
    st.dataframe(centered_player_df)
    print(player.keys())
    col1, col2 = st.columns(2)
    
with col1: 
    # Home section
    with st.container():
        st.header("Home")
        
        # Create an empty team DataFrame if not already in session state
        if 'team_df' not in st.session_state:
            st.session_state['team_df'] = pd.DataFrame(columns=player.columns)
                    
        # Get the team DataFrame from session state
        team_df = st.session_state['team_df']

        # Player search input
        search_input = st.text_input("Search for HOME player by name or ID:")

        # Temporary select box for user confirmation
        selected_player = None
        selected_player_name = None
        
        # Create columns for buttons
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            # Search players
            if search_input:
                try:
                    # Try to parse search input as player ID
                    player_id = int(search_input)
                    search_results = player[player["player_id"] == player_id]
                    
                    # If player found by ID
                    if not search_results.empty:
                        # Extract player details
                        selected_player_id = search_results.iloc[0]['player_id']
                        selected_player_name = search_results.iloc[0]['name']
                        selected_player_team = search_results.iloc[0]['team_name']

                        # Check if the selected player is already added to the team
                        if selected_player_id in team_df['player_id'].values:
                            st.error(f"Player {selected_player_name} is already added to the home team.")
                        elif len(team_df) >= 24:
                            st.error("Cannot add more than 24 players to the home team.")
                        else:
                            # Add selected player to the team
                            st.session_state['team_df'] = pd.concat([team_df, search_results]).drop_duplicates().reset_index(drop=True)
                            st.success(f"Player {selected_player_name} added to the home team!")

                except ValueError:
                    # Search by name
                    search_results = player[player['name'].str.lower().str.contains(search_input.lower())]
                    
                    # If players found by name
                    if not search_results.empty:
                        # Create a new column that combines name and team_name
                        search_results['name_team'] = search_results['name'] + ' - ' + search_results['team_name']
                        
                        # Display the select box with the new column
                        selected_name_team = st.selectbox("Select HOME player to add:", search_results['name_team'])
                        
                        # Extract the selected player's name and team
                        selected_player_name, selected_player_team = selected_name_team.split(' - ')
                        
                        # Get the player's ID based on name and team
                        selected_player = player[(player['name'] == selected_player_name) & (player['team_name'] == selected_player_team)]
                        
                        # If player found by name and team
                        if not selected_player.empty:
                            selected_player_id = selected_player.iloc[0]['player_id']
                            
                            # Add selected player to the team
                            st.session_state['team_df'] = pd.concat([team_df, selected_player]).drop_duplicates().reset_index(drop=True)
                            st.success(f"Player {selected_player_name} added to the home team!")
                            team_df = st.session_state['team_df']
                    else:
                        st.error("No players found matching the search criteria.")

        with col1_2:
            if st.button("Remove last home player"):
                if 'team_df' in st.session_state and not st.session_state['team_df'].empty:
                    st.session_state['team_df'] = st.session_state['team_df'].iloc[:-1]
                    st.success("Last player removed from the home team!")
                    team_df = st.session_state['team_df']
                else:
                    st.error("No players to remove from the home team!")
                

        # Display the team DataFrame
        st.header("Home Team")
        st.write(team_df)
        
    with col2: 
        # Home section
        with st.container():
            st.header(f"Home")
            
            # Create an empty team DataFrame if not already in session state
            if 'team2_df' not in st.session_state:
                st.session_state['team2_df'] = pd.DataFrame(columns=player.columns)
                        
            # Get the team DataFrame from session state
            team2_df = st.session_state['team2_df']

            # Player search input
            search_input2 = st.text_input("Search for AWAY player by name or ID:")

            # Temporary select box for user confirmation
            selected_player2 = None
            selected_player_name2 = None
            
            # Create columns for buttons
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                # Search players
                if search_input2:
                    try:
                        # Try to parse search input as player ID
                        player_id2 = int(search_input2)
                        search_results2 = player[player["player_id"] == player_id2]
                        
                        # If player found by ID
                        if not search_results2.empty:
                            # Extract player details
                            selected_player_id2 = search_results2.iloc[0]['player_id']
                            selected_player_name2 = search_results2.iloc[0]['name']
                            selected_player_team2 = search_results2.iloc[0]['team_name']

                            # Check if the selected player is already added to the team
                            if selected_player_id2 in team2_df['player_id'].values:
                                st.error(f"Player {selected_player_name2} is already added to the home team.")
                            elif len(team2_df) >= 24:
                                st.error("Cannot add more than 24 players to the home team.")
                            else:
                                # Add selected player to the team
                                st.session_state['team2_df'] = pd.concat([team2_df, search_results2]).drop_duplicates().reset_index(drop=True)
                                st.success(f"Player {selected_player_name2} added to the home team!")

                    except ValueError:
                        # Search by name
                        search_results2 = player[player['name'].str.lower().str.contains(search_input2.lower())]
                        
                        # If players found by name
                        if not search_results2.empty:
                            # Create a new column that combines name and team_name
                            search_results2['name_team'] = search_results2['name'] + ' - ' + search_results2['team_name']
                            
                            # Display the select box with the new column
                            selected_name_team2 = st.selectbox("Select AWAY player to add:", search_results2['name_team'])
                            
                            # Extract the selected player's name and team
                            selected_player_name2, selected_player_team2 = selected_name_team2.split(' - ')
                            
                            # Get the player's ID based on name and team
                            selected_player2 = player[(player['name'] == selected_player_name2) & (player['team_name'] == selected_player_team2)]
                            
                            # If player found by name and team
                            if not selected_player2.empty:
                                selected_player_id2 = selected_player2.iloc[0]['player_id']
                                
                                # Add selected player to the team
                                st.session_state['team2_df'] = pd.concat([team2_df, selected_player2]).drop_duplicates().reset_index(drop=True)
                                st.success(f"Player {selected_player_name2} added to the away team!")
                                team2_df = st.session_state['team2_df']
                        else:
                            st.error("No players found matching the search criteria.")
                            
            # Remove last away player
            with col2_2:
                if st.button("Remove last away player"):
                    if 'team2_df' in st.session_state and not st.session_state['team2_df'].empty:
                        # Remove the last player from the away team
                        st.session_state['team2_df'] = st.session_state['team2_df'].iloc[:-1]
                        st.success("Last player removed from the away team!")
                        team2_df = st.session_state['team2_df']
                    else:
                        st.error("No players to remove from the away team!")
                

            # Display the team DataFrame for the away team
            st.header("Away")
            st.write(team2_df)
       
        

        
    # player_positions = {
    #     1: {"x": 50, "y": 10},
    #     2: {"x": 50, "y": 20},
    #     3: {"x": 50, "y": 35},
    #     4: {"x": 50, "y": 45},
    #     5: {"x": 45, "y": 60},
    #     6: {"x": 55, "y": 60},
    #     7: {"x": 35, "y": 80},
    #     8: {"x": 65, "y": 80},
    #     9: {"x": 35, "y": 60},
    #     10: {"x": 65, "y": 60},
    #     11: {"x": 20, "y": 80},
    #     12: {"x": 80, "y": 80},
    #     13: {"x": 50, "y": 90},
    #     14: {"x": 20, "y": 10},
    #     15: {"x": 80, "y": 10}
    # }

    
    # MODEL INTEGRATION
    
    def select_team(df, home, away, model):
        home_team_df = df[df['name'].isin(home)].reset_index()
        away_team_df = df[df['name'].isin(away)].reset_index()
        
        home_team = home_team_df.iloc[:, 3:6]
        home_team.columns = {'home_ability_score', 'home_attack_score', 'home_defend_score'}
        
        away_team = away_team_df.iloc[:, 3:6]
        away_team.columns = {'away_ability_score', 'away_attack_score', 'away_defend_score'}
        
        teams_df = pd.concat([home_team, away_team], axis = 1)
        teams_df = pd.DataFrame(teams_df.sum(axis=0)).T
        
        #turn into array for model
        team_arr = np.asarray(teams_df)
        team_data = team_arr.reshape(1, 6)
        
        winner = model.predict(team_data)
        probs = model.predict_proba(team_data)
        
        if winner == 1:
            st.success("The Home team wins")
        else:
            st.success("The away team wins")

        st.text(f"\nThere is a {np.round(probs[0][1] * 100)}% chance the HOME team will win\n")
        st.text(f"There is a {np.round(probs[0][0] * 100)}% chance the AWAY team will win\n")
        
        return
        
   
    filename = 'Collab/rugby_model.sav'
    loaded_model = joblib.load(filename)
    
    
    # CSS to center the button
    st.markdown("""
        <style>
        .button-container {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .stButton button {
            width: 200px;  /* Adjust the width of the button */
        }
        </style>
        """, unsafe_allow_html=True)

    # HTML container for the Streamlit button
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button('Generate Results'):
        st.balloons()
        select_team(player, team_df, team2_df, loaded_model)

    st.markdown('</div>', unsafe_allow_html=True)
    
    
    # MODEL INTEGRATION
    

    # Define the dimensions of the rugby field
    field_width = 700
    field_height = 1000
    
    # Define the CSS style for the rugby field with padding and a 3D tilt
    field_style = f"""
    width: {field_width}px;
    height: {field_height}px;
    background-color: #4CAF50;
    transform: perspective(700px) rotateZ(90deg) rotateY(-45deg);
    transform-origin: center;
    padding: 50px;
    box-sizing: border-box;
    """

    # Define the CSS style for the field lines
    line_style = "position: absolute; background-color: white;"

    # Define the HTML for the rugby field
    field_html = f"""
    <div style="display: flex; justify-content: center; align-items: center; width: 90vw; height: 100vh;">
        <div style="position: relative;">
            <div style="{field_style}">
                <div style="{line_style}; width: {field_width}px; height: 5px; top: 0; left: 0;"></div>
                <div style="{line_style}; width: {field_width}px; height: 5px; bottom: 0; left: 0;"></div>
                <div style="{line_style}; width: 5px; height: {field_height}px; top: 0; left: 0;"></div>
                <div style="{line_style}; width: 5px; height: {field_height}px; top: 0; right: 0;"></div>
                <div style="{line_style}; width: 5px; height: {field_height}px; top: 0; left: 50%; transform: translateX(-50%);"></div>
                <div style="{line_style}; width: 5px; height: {field_height}px; top: 0; left: 22%; transform: translateX(-50%);"></div>
                <div style="{line_style}; width: 5px; height: {field_height}px; top: 0; right: 22%; transform: translateX(50%);"></div>
                <div style="{line_style}; width: 5px; height: {field_height}px; top: 0; left: 78%; transform: translateX(-50%);"></div>
            </div>
            <div>
                <!-- Goal Posts -->
                <div style="position: absolute; width: 1%; height: 15%; background-color: white; top: 16.7%; left: 40%; transform: translateY(0);"></div>
                <div style="position: absolute; width: 1%; height: 15%; background-color: white; top: 16.7%; right: 40%; transform: translateY(0);"></div>
                <div style="position: absolute; width: 1%; height: 13.2%; background-color: white; top: 20.5%; right: 49%; transform: translateY(0) rotate(90deg);"></div>
                <div style="position: absolute; width: 1%; height: 22%; background-color: white; top: 66%; left: 30%; transform: translateY(0);"></div>
                <div style="position: absolute; width: 1%; height: 22%; background-color: white; top: 66%; right: 30%; transform: translateY(0);"></div>
                <div style="position: absolute; width: 1%; height: 27%; background-color: white; top: 65%; right: 50%; transform: translateY(0) rotate(90deg);"></div>
                """

    # Add the HTML for the Home team table
    field_html += """
    <div style="position: absolute; color: white; font-size: 40px; top: 5%; left: -40%; transform: translateY(-50%);">Home</div>
    <div style="position: absolute; background-color: lightblue; top: 10%; left: -40%; padding: 10px;">
        <table>
            <thead>
                <tr>
                    <th>Home Team</th>
                </tr>
            </thead>
            <tbody>"""
    # Add rows for each player in the Home team
    for team_name in team_df['name']:
        field_html += f"<tr><td>{team_name}</td></tr>"

    # Close the Home team table
    field_html += """
            </tbody>
        </table>
    </div>"""

    # Add the HTML for the Away team table
    field_html += """
    <div style="position: absolute; color: white; font-size: 40px; top: 5%; right: -40%; transform: translateY(-50%);">Away</div>
    <div style="position: absolute; background-color: pink; top: 10%; right: -40%; padding: 10px;">
        <table>
            <thead>
                <tr>
                    <th>Away Team</th>
                </tr>
            </thead>
            <tbody>"""
    # Add rows for each player in the Away team
    for team_name in team2_df['name']:
        field_html += f"<tr><td>{team_name}</td></tr>"

    # Close the Away team table and the outermost div
    field_html += """
            </tbody>
        </table>
    </div>
    </div>"""

    # Display the rugby field
    st.markdown(field_html, unsafe_allow_html=True)
    
    
# Stat leaderboard
with tab3:
    st.header("Player Stats Leaderboard")
    col3, col4, col5  = st.columns(3)
    with col3:
        st.header("Ability Score")
        st.dataframe(player[['name','Ability_score']].sort_values('Ability_score',ascending=False))
    with col4:
        st.header("Attack Score")
        st.dataframe(player[['name','attack_score']].sort_values('attack_score',ascending=False))
    with col5:
        st.header("Defend Score")
        st.dataframe(player[['name','defend_score']].sort_values('defend_score',ascending=False))
    #st.dataframe(player)