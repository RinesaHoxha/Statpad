from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.form import FormDB
from app.models.matchday import Matchday
from app.models.standing import LeagueTable

def calculate_team_evaluation(team, is_home=False):

    league_data = session.query(LeagueTable).filter(LeagueTable.club == team).first()

    home_advantage = 0.2 if is_home else 0.0

    last5_wins = last5_losses = last5_draws = last5_gs = last5_gc = 0

    form_data = session.query(FormDB).filter(FormDB.team_name == team).order_by(FormDB.date.desc()).limit(5).all()

    for match in form_data:
        try:
            if match.h_or_a == 'H':
                home_score = int(match.home_scores)
                away_score = int(match.away_scores)
                last5_gs += home_score
                last5_gc += away_score
                if home_score > away_score:
                    last5_wins += 1
                elif home_score < away_score:
                    last5_losses += 1
                else:
                    last5_draws += 1
            elif match.h_or_a == 'A':
                home_score = int(match.home_scores)
                away_score = int(match.away_scores)
                last5_gs += away_score
                last5_gc += home_score
                if away_score > home_score:
                    last5_wins += 1
                elif away_score < home_score:
                    last5_losses += 1
                else:
                    last5_draws += 1
        except ValueError:
            continue

    last5_points = last5_wins * 3 + last5_draws * 1

    league_performance = (
            league_data.points * 0.25 +
            league_data.wins * 0.3 +
            league_data.draws * 0.1 +
            league_data.goalsscored * 0.2 -
            league_data.goalsconceded * 0.05
    )

    last_5_matches = (
            last5_points * 0.25 +
            last5_wins * 0.3 +
            last5_draws * 0.1 +
            last5_gs * 0.3 -
            last5_gc * 0.05
    )

    default_home_advantage = home_advantage

    evaluation = (league_performance + 
                  last_5_matches + 
                  default_home_advantage)

    return evaluation




Session = sessionmaker(bind=engine)
session = Session()

more_data = session.query(Matchday).all()

for matchday_instance in more_data:
    H_Team = matchday_instance.h_team
    A_Team = matchday_instance.a_team
    current_league = matchday_instance.league

    if current_league in ["Champions League", "Europa League"]:
        continue

    # Determine if it's the home team based on your data structure
    is_home_team = True  # Modify this based on how you identify the home team
    evaluate_h_team = calculate_team_evaluation(H_Team, is_home=is_home_team)
    evaluate_a_team = calculate_team_evaluation(A_Team, is_home=False)


    def calculate_odds(team1_eval, team2_eval):
        total = team1_eval + team2_eval

        if total > 0:
            if total > 100:
                team1_eval = (team1_eval / total) * 100
                team2_eval = (team2_eval / total) * 100

            odds_team1_wins = (team1_eval / total) * 100
            odds_team2_wins = (team2_eval / total) * 100
        else:
            odds_team1_wins = odds_team2_wins = 50.0  # Default equal odds for invalid total

        return odds_team1_wins, odds_team2_wins


    odds_h_wins, odds_a_wins = calculate_odds(evaluate_h_team, evaluate_a_team)


