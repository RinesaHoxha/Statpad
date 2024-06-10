import requests
from bs4 import BeautifulSoup
import datetime
from app.models.matches import LiveSoccerScores, TomorrowSoccerScores
from app.database import SessionLocal
from sqlalchemy import asc

league_ru = {
    "https://cdn.resfu.com/media/img/flags/st3/small/ru.png?size=30x&lossy=1": "Russian Premier League",
}
def scrape_and_store_soccer_scores(date):
    session = SessionLocal()
    match_data_list = []  # Create an empty list to store match_data

    url = f'https://www.besoccer.com/livescore/{date}'
    try:
        data_get = requests.get(url)
        data_get.raise_for_status()
        soup = BeautifulSoup(data_get.text, 'html.parser')
        panels = soup.find_all('div', class_='panel')
        for panel in panels:
            panel_titles = panel.find_all('div', class_='panel-title')
            panel_body = panel.find_all('div', class_='panel-body p0 match-list-new panel view-more')
            league_img = ' '
            league = ' '
            round = ' '
            for panel_title in panel_titles:
                spans = panel_title.find_all('span', class_='va-m')
                league_img = panel_title.find_all(class_='comp-img va-m')
                for span in spans:
                    league = span.get_text()

                for l in league_img:
                    league_img = l.get('src')
                    league = league_ru.get(league_img, league)  # Use the mapping or keep the original league name

            for body in panel_body:
                info = body.find_all(class_='middle-info ta-c')
                for i in info:
                    round = i.get_text()
                team_elements = body.find_all(class_='name')
                score_elements = body.find_all(class_='marker')
                team_logos = body.find_all('img')
                home_team_logos = team_logos[::2]
                away_team_logos = team_logos[1::2]
                matches_status = body.find_all(class_='match-status-label')  # Extract the match status directly
                for home, away, score, home_logo, away_logo, match in zip(
                        team_elements[::2], team_elements[1::2], score_elements, home_team_logos, away_team_logos,
                        matches_status
                ):
                    home_team = home.get_text().strip()
                    home_team_img = home_logo.get('src')
                    away_team = away.get_text()
                    away_team_img = away_logo.get('src')
                    score_text = score.get_text().strip()
                    match_status = match.get_text().strip()

                    match_data = {
                        "league_img": league_img,
                        "league": league,
                        "round": round,
                        "home_team": home_team,
                        "home_team_img": home_team_img,
                        "score": score_text,
                        "away_team": away_team,
                        "away_team_img": away_team_img,
                        "match_status": match_status,
                        "match_date": date,
                    }

                    match_data_list.append(match_data)  # Append match_data to the list

                    # Check if the match data already exists in the database
                    existing_match = session.query(LiveSoccerScores).filter(
                        LiveSoccerScores.match_date == date,
                        LiveSoccerScores.home_team == home_team,
                        LiveSoccerScores.away_team == away_team
                    ).first()

                    if existing_match:
                        # Update the existing match data
                        existing_match.league = match_data["league_img"]
                        existing_match.league = match_data["league"]
                        existing_match.round = match_data["round"]
                        existing_match.home_team_img = match_data["home_team_img"]
                        existing_match.away_team_img = match_data["away_team_img"]
                        existing_match.score = match_data["score"]
                        existing_match.match_status = match_data["match_status"]
                        existing_match.date_scraped = datetime.datetime.now()
                    else:
                        # Insert a new match record
                        live_score = LiveSoccerScores(
                            league_img=match_data["league_img"],
                            league=match_data["league"],
                            round=match_data["round"],
                            home_team=match_data["home_team"],
                            home_team_img=match_data["home_team_img"],
                            away_team=match_data["away_team"],
                            away_team_img=match_data["away_team_img"],
                            score=match_data["score"],
                            match_status=match_data["match_status"],
                            match_date=date,
                            date_scraped=datetime.datetime.now()
                        )
                        session.add(live_score)

        session.commit()
        print(f"Soccer scores for {date} scraped and stored successfully.")
    except requests.exceptions.RequestException as e:
        print("Error:", e)
    finally:
        session.close()

    return match_data_list



def match_is_live(match_data):
    current_date = datetime.date.today()
    match_date = datetime.datetime.strptime(match_data["match_date"], "%Y-%m-%d").date()
    return match_date == current_date


def match_is_tomorrow(match_data):
    match_date = datetime.datetime.strptime(match_data["match_date"], "%Y-%m-%d").date()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return match_date == tomorrow


def save_to_live_scores_table(match_data, session):
    try:
        existing_match = session.query(LiveSoccerScores).filter(
            LiveSoccerScores.match_date == match_data["match_date"],
            LiveSoccerScores.home_team == match_data["home_team"],
            LiveSoccerScores.away_team == match_data["away_team"]
        ).order_by(asc(LiveSoccerScores.league), asc(LiveSoccerScores.round)).first()

        if existing_match:
            # Update the existing match data
            existing_match.league_img= match_data["league_img"]
            existing_match.league = match_data["league"]
            existing_match.round = match_data["round"]
            existing_match.home_team_img = match_data["home_team_img"]
            existing_match.away_team_img = match_data["away_team_img"]
            existing_match.score = match_data["score"]
            existing_match.match_status = match_data["match_status"]
            existing_match.date_scraped = datetime.datetime.now()
        else:
            # Insert a new match record
            live_score = LiveSoccerScores(
                league_img = match_data["league_img"],
                league=match_data["league"],
                round=match_data["round"],
                home_team=match_data["home_team"],
                home_team_img=match_data["home_team_img"],
                away_team=match_data["away_team"],
                away_team_img=match_data["away_team_img"],
                score=match_data["score"],
                match_status=match_data["match_status"],
                match_date=match_data["match_date"],
                date_scraped=datetime.datetime.now()
            )
            session.add(live_score)
        session.commit()
    except Exception as e:
        print("Error in save_to_live_scores_table:", e)


def save_to_tomorrow_scores_table(match_data, session):
    try:
        existing_match = session.query(TomorrowSoccerScores).filter(
            TomorrowSoccerScores.match_date == match_data["match_date"],
            TomorrowSoccerScores.home_team == match_data["home_team"],
            TomorrowSoccerScores.away_team == match_data["away_team"]
        ).order_by(asc(TomorrowSoccerScores.league), asc(TomorrowSoccerScores.round)).first()

        if existing_match:
            # Update the existing match data
            existing_match.league_img = match_data["league_img"]
            existing_match.league = match_data["league"]
            existing_match.round = match_data["round"]
            existing_match.home_team_img = match_data["home_team_img"]
            existing_match.away_team_img = match_data["away_team_img"]
            existing_match.score = match_data["score"]
            existing_match.match_status = match_data["match_status"]
            existing_match.date_scraped = datetime.datetime.now()
        else:
            # Insert a new match record
            tomorrow_score = TomorrowSoccerScores(
                league_img=match_data["league_img"],
                league=league_ru.get(match_data["league_img"], match_data["league"]),
                round=match_data["round"],
                home_team=match_data["home_team"],
                home_team_img=match_data["home_team_img"],
                away_team=match_data["away_team"],
                away_team_img=match_data["away_team_img"],
                score=match_data["score"],
                match_status=match_data["match_status"],
                match_date=match_data["match_date"],
                date_scraped=datetime.datetime.now()
            )
            session.add(tomorrow_score)
        session.commit()
    except Exception as e:
        print("Error in save_to_tomorrow_scores_table:", e)
