import csv

from fastapi import FastAPI, APIRouter, HTTPException
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

router = APIRouter(
    prefix='/predictions',  # Set the prefix to 'matches'
    tags=['predictions']
)
templates = Jinja2Templates(directory='templates')
# Load the model and required data
matches = pd.read_csv("utils/all_matches.csv", index_col=0)
matches["date"] = pd.to_datetime(matches["date"])

# Data Preprocessing
matches["date"] = pd.to_datetime(matches["date"])
matches["venue_code"] = matches["venue"].astype("category").cat.codes
matches["opp_code"] = matches["opponent"].astype("category").cat.codes
matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int")
matches["day_code"] = matches["date"].dt.dayofweek
matches["referee_code"] = matches["referee"].astype("category").cat.codes
matches["captain_code"] = matches["captain"].astype("category").cat.codes
matches["target"] = (matches["result"] == "W").astype("int")

# Initialize RandomForestClassifier
rf = RandomForestClassifier(n_estimators=1000, min_samples_split=32, random_state=1,
                            class_weight="balanced")  # make multiple min samples
# Split data into train and test sets
train = matches[(matches["date"] < '2024-08-08')]
test = matches[matches["date"] > '2020-08-08']

# Define predictors
predictors = ["venue_code", "opp_code", "hour", "day_code", "referee_code", "captain_code"]


file_path = 'utils/all_matches.csv'  # Replace 'your_file.csv' with your CSV file path
df = pd.read_csv(file_path)


# Function to replace 'Utd' with 'United' in a given text
def replace_opponent(text):
    text = text.replace(' Utd', ' United')  # Notice the space before Utd to avoid replacing within other words
    text = text.replace("Nott'ham Forest", "Nottingham Forest")
    text = text.replace('Leverkusen', 'Bayer Leverkusen') if 'Bayer' not in text else text
    text = text.replace("M'Gladbach", "Monchengladbach")
    text = text.replace('Köln', 'Koln')
    return text


def replace_teams(text):
    text = text.replace('Tottenham Hotspur', 'Tottenham')
    # Replace 'Wolverhampton Wanderers' with 'Wolves'
    text = text.replace('Wolverhampton Wanderers', 'Wolves')
    text = text.replace('Brighton and Hove Albion', 'Brighton')
    text = text.replace('West Ham United', 'West Ham')
    text = text.replace('Internazionale', 'Inter')
    return text


# Apply the function to the specific column containing the text

column_name = 'opponent'  # Replace 'column_name' with the actual column name in your DataFrame
df[column_name] = df[column_name].apply(replace_opponent)
column_name2 = 'team'
df[column_name2] = df[column_name2].apply(replace_teams)
# Save the modified DataFrame back to a new CSV file or the same file if needed
output_file_path = 'utils/all_matches.csv'  # Replace 'modified_file.csv' with your desired output file path
df.to_csv(output_file_path, index=False)

# Define a function for calculating rolling averages
def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed="left").mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group


# Get matches for a specific team
cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt", "poss", "xg", "xga"]
new_cols = [f"{c}_rolling" for c in cols]

# Calculate rolling averages for matches
rolling_matches = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
rolling_matches = rolling_matches.droplevel("team")
rolling_matches.index = range(rolling_matches.shape[0])


# Function to make predictions
def make_predictions(data, predictors):
    train = data[(data["date"] < '2024-08-08')]
    test = data[data["date"] > '2020-01-01']
    rf.fit(train[predictors], train["target"])
    preds = rf.predict(test[predictors])
    combined = pd.DataFrame(dict(actual=test["target"], prediction=preds), index=test.index)
    precision = precision_score(test["target"], preds)
    return combined, precision
combined, precision = make_predictions(rolling_matches, predictors + new_cols)
combined = combined.merge(rolling_matches[["date","team","opponent","result"]], left_index=True, right_index=True)
def predict_winner(team1, team2):

    # Prepare features for the prediction
    team1_data = rolling_matches[rolling_matches["team"] == team1]
    team2_data = rolling_matches[rolling_matches["team"] == team2]

    # Make predictions using the RandomForestClassifier model
    team1_combined, team1_precision = make_predictions(team1_data, predictors + new_cols)
    team2_combined, team2_precision = make_predictions(team2_data, predictors + new_cols)

    team1_combined = team1_combined.merge(rolling_matches[["date", "team", "opponent", "result"]], left_index=True,
                                          right_index=True)
    team2_combined = team2_combined.merge(rolling_matches[["date", "team", "opponent", "result"]], left_index=True,
                                          right_index=True)

    #merge1 and 2 check the history between the two teamns
    merged1 = team1_combined.merge(combined, left_on=["date", "team"], right_on=["date", "opponent"])
    merged2 = team2_combined.merge(combined, left_on=["date", "team"], right_on=["date", "opponent"])

    # Get predicted winners for each team where both teams are predicted to win
    team1_draw = merged1[(merged1['prediction_x'] == 1) & (merged1['prediction_y'] == 1)].shape[0]
    team2_draw = merged2[(merged2['prediction_x'] == 1) & (merged2['prediction_y'] == 1)].shape[0]

    # team1_loss = merged1[(merged1['prediction_x']== 0) & (merged1['prediction_y']== 0)].shape[0]
    # team2_loss = merged2[(merged2['prediction_x'] == 0) & (merged2['prediction_y'] == 0)].shape[0]

    team1_wins = merged1[(merged1['prediction_x'] == 1) & (merged1['prediction_y'] == 0)].shape[0]
    team2_wins = merged2[(merged2['prediction_x'] == 1) & (merged2['prediction_y'] == 0)].shape[0]

    # Calculate total wins separately for each team
    total_team1_wins = team1_wins + team1_draw  # Include draws where team1 wins
    total_team2_wins = team2_wins + team2_draw  # Include draws where team2 wins

    threshold = 0.10

    if abs(team1_wins - team2_wins) <= threshold * (team1_wins +team1_draw + team2_wins + team2_draw):
        return f"It's predicted to be a draw{team1_wins}, {team2_wins}"

    elif team1_wins > team2_wins:
        return f"{team1} is predicted to win {team1_wins} to {team2_wins}"

    else:
        return f"{team2} is predicted to win {team2_wins} to {team1_wins}"


@router.get("/predict_winner")
async def predict_winner_view(request: Request, team1: str, team2: str):
    if team1 not in matches['team'].unique() or team2 not in matches['team'].unique():
        raise HTTPException(status_code=400, detail="Invalid team name(s). Please provide valid team names.")

    # Get the predicted winner between the provided teams
    winner = predict_winner(team1, team2)
    return winner


@router.get("/simulate_Premier_league")
async def simulate_matches_view():
    league_results = {}
    teams = set()  # Using a set to store unique team names

    # Read team names from the CSV file for Premier League 2024 season
    teams_data = pd.read_csv('utils/all_matches.csv')  # Replace 'teams_data.csv' with your CSV file path

    # Filter the data for Premier League 2024 season
    premier_league_2024 = teams_data[(teams_data['comp'] == 'Premier League') & (teams_data['season'] == '2024')]

    # Extract unique team names and store in the set
    teams.update(premier_league_2024['team'].unique())

    # Simulate matches between teams
    teams_list = list(teams)  # Convert set back to a list for iteration
    for i in range(len(teams_list)):
        team1 = teams_list[i]
        for j in range(i + 1, len(teams_list)):
            team2 = teams_list[j]

            # Simulate match between team1 and team2
            winner = predict_winner(team1, team2)

            if winner == "It's predicted to be a draw":
                # Award 1 point each for a draw
                league_results.setdefault(team1, 0)
                league_results[team1] += 1

                league_results.setdefault(team2, 0)
                league_results[team2] += 1

            elif team1 in winner:
                # Team1 wins the match, add 3 points to team1, 0 points to team2
                league_results.setdefault(team1, 0)
                league_results[team1] += 3

            else:
                # Team2 wins the match, add 3 points to team2, 0 points to team1
                league_results.setdefault(team2, 0)
                league_results[team2] += 3

    # Sort teams based on points
    sorted_teams = sorted(league_results.items(), key=lambda x: x[1], reverse=True)

    # Determine the league winner
    league_winner = sorted_teams[0][0]

    # Generate positions for all teams
    positions = {team: pos + 1 for pos, (team, _) in enumerate(sorted_teams)}

    return {
        "league_winner": league_winner,
        "team_positions": positions
    }


@router.get("/simulate_SerieA")
async def simulate_matches_view():
    league_results = {}
    teams = set()  # Using a set to store unique team names

    # Read team names from the CSV file for Premier League 2024 season
    teams_data = pd.read_csv('utils/all_matches.csv')  # Replace 'teams_data.csv' with your CSV file path

    # Filter the data for Premier League 2024 season
    premier_league_2024 = teams_data[(teams_data['comp'] == 'Serie A') & (teams_data['season'] == '2024')]

    # Extract unique team names and store in the set
    teams.update(premier_league_2024['team'].unique())

    # Simulate matches between teams
    teams_list = list(teams)  # Convert set back to a list for iteration
    for i in range(len(teams_list)):
        team1 = teams_list[i]
        for j in range(i + 1, len(teams_list)):
            team2 = teams_list[j]

            # Simulate match between team1 and team2
            winner = predict_winner(team1, team2)

            if winner == "It's predicted to be a draw":
                # Award 1 point each for a draw
                league_results.setdefault(team1, 0)
                league_results[team1] += 1

                league_results.setdefault(team2, 0)
                league_results[team2] += 1

            elif team1 in winner:
                # Team1 wins the match, add 3 points to team1, 0 points to team2
                league_results.setdefault(team1, 0)
                league_results[team1] += 3

            else:
                # Team2 wins the match, add 3 points to team2, 0 points to team1
                league_results.setdefault(team2, 0)
                league_results[team2] += 3

    # Sort teams based on points
    sorted_teams = sorted(league_results.items(), key=lambda x: x[1], reverse=True)

    # Determine the league winner
    league_winner = sorted_teams[0][0]

    # Generate positions for all teams
    positions = {team: pos + 1 for pos, (team, _) in enumerate(sorted_teams)}

    return {
        "league_winner": league_winner,
        "team_positions": positions
    }

@router.get("/simulate_BundesLiga")
async def simulate_matches_view():
    league_results = {}
    teams = set()  # Using a set to store unique team names

    # Read team names from the CSV file for Premier League 2024 season
    teams_data = pd.read_csv('utils/all_matches.csv')  # Replace 'teams_data.csv' with your CSV file path

    # Filter the data for Premier League 2024 season
    premier_league_2024 = teams_data[(teams_data['comp'] == 'Bundesliga') & (teams_data['season'] == '2024')]

    # Extract unique team names and store in the set
    teams.update(premier_league_2024['team'].unique())

    # Simulate matches between teams
    teams_list = list(teams)  # Convert set back to a list for iteration
    for i in range(len(teams_list)):
        team1 = teams_list[i]
        for j in range(i + 1, len(teams_list)):
            team2 = teams_list[j]

            # Simulate match between team1 and team2
            winner = predict_winner(team1, team2)

            if winner == "It's predicted to be a draw":
                # Award 1 point each for a draw
                league_results.setdefault(team1, 0)
                league_results[team1] += 1

                league_results.setdefault(team2, 0)
                league_results[team2] += 1

            elif team1 in winner:
                # Team1 wins the match, add 3 points to team1, 0 points to team2
                league_results.setdefault(team1, 0)
                league_results[team1] += 3

            else:
                # Team2 wins the match, add 3 points to team2, 0 points to team1
                league_results.setdefault(team2, 0)
                league_results[team2] += 3

    # Sort teams based on points
    sorted_teams = sorted(league_results.items(), key=lambda x: x[1], reverse=True)

    # Determine the league winner
    league_winner = sorted_teams[0][0]

    # Generate positions for all teams
    positions = {team: pos + 1 for pos, (team, _) in enumerate(sorted_teams)}

    return {
        "league_winner": league_winner,
        "team_positions": positions
    }

@router.get("/simulate_LaLiga")
async def simulate_matches_view():
    league_results = {}
    teams = set()  # Using a set to store unique team names

    # Read team names from the CSV file for Premier League 2024 season
    teams_data = pd.read_csv('utils/all_matches.csv')  # Replace 'teams_data.csv' with your CSV file path

    # Filter the data for Premier League 2024 season
    premier_league_2024 = teams_data[(teams_data['comp'] == 'La Liga') & (teams_data['season'] == '2024')]

    # Extract unique team names and store in the set
    teams.update(premier_league_2024['team'].unique())

    # Simulate matches between teams
    teams_list = list(teams)  # Convert set back to a list for iteration
    for i in range(len(teams_list)):
        team1 = teams_list[i]
        for j in range(i + 1, len(teams_list)):
            team2 = teams_list[j]

            # Simulate match between team1 and team2
            winner = predict_winner(team1, team2)

            if winner == "It's predicted to be a draw":
                # Award 1 point each for a draw
                league_results.setdefault(team1, 0)
                league_results[team1] += 1

                league_results.setdefault(team2, 0)
                league_results[team2] += 1

            elif team1 in winner:
                # Team1 wins the match, add 3 points to team1, 0 points to team2
                league_results.setdefault(team1, 0)
                league_results[team1] += 3

            else:
                # Team2 wins the match, add 3 points to team2, 0 points to team1
                league_results.setdefault(team2, 0)
                league_results[team2] += 3

    # Sort teams based on points
    sorted_teams = sorted(league_results.items(), key=lambda x: x[1], reverse=True)

    # Determine the league winner
    league_winner = sorted_teams[0][0]

    # Generate positions for all teams
    positions = {team: pos + 1 for pos, (team, _) in enumerate(sorted_teams)}

    return {
        "league_winner": league_winner,
        "team_positions": positions
    }

@router.get("/simulate_Ligue1")
async def simulate_matches_view():
    league_results = {}
    teams = set()  # Using a set to store unique team names

    # Read team names from the CSV file for Premier League 2024 season
    teams_data = pd.read_csv('utils/all_matches.csv')  # Replace 'teams_data.csv' with your CSV file path

    # Filter the data for Premier League 2024 season
    premier_league_2024 = teams_data[(teams_data['comp'] == 'Ligue 1') & (teams_data['season'] == '2024')]

    # Extract unique team names and store in the set
    teams.update(premier_league_2024['team'].unique())

    # Simulate matches between teams
    teams_list = list(teams)  # Convert set back to a list for iteration
    for i in range(len(teams_list)):
        team1 = teams_list[i]
        for j in range(i + 1, len(teams_list)):
            team2 = teams_list[j]

            # Simulate match between team1 and team2
            winner = predict_winner(team1, team2)

            if winner == "It's predicted to be a draw":
                # Award 1 point each for a draw
                league_results.setdefault(team1, 0)
                league_results[team1] += 1

                league_results.setdefault(team2, 0)
                league_results[team2] += 1

            elif team1 in winner:
                # Team1 wins the match, add 3 points to team1, 0 points to team2
                league_results.setdefault(team1, 0)
                league_results[team1] += 3

            else:
                # Team2 wins the match, add 3 points to team2, 0 points to team1
                league_results.setdefault(team2, 0)
                league_results[team2] += 3

    # Sort teams based on points
    sorted_teams = sorted(league_results.items(), key=lambda x: x[1], reverse=True)

    # Determine the league winner
    league_winner = sorted_teams[0][0]

    # Generate positions for all teams
    positions = {team: pos + 1 for pos, (team, _) in enumerate(sorted_teams)}

    return {
        "league_winner": league_winner,
        "team_positions": positions
    }