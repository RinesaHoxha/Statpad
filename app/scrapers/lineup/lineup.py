from datetime import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy import delete
from app.database import SessionLocal
from app.models.bet import Bets
from app.models.lineup import LineupModel, Lineup


def scrape_lineup_info_for_teams():
    team_names = ['almeria', 'athletic-bilbao', 'atletico-madrid', 'barcelona', 'cadiz', 'celta', 'alaves', 'getafe',
                  'girona-fc', 'granada', 'ud-palmas', 'mallorca', 'osasuna', 'rayo-vallecano', 'betis', 'real-madrid',
                  'real-sociedad', 'sevilla', 'valencia-cf', 'villarreal',
                  'borussia-dortmund', 'bayer-leverkusen', 'borussia-monchengla', 'bayern-munchen', 'darmstadt-98',
                  'eintracht-frankfurt', 'fc-augsburg', 'heidenheim', 'tsg-1899-hoffenheim', '1-fc-koln', 'mainz-amat',
                  'rb-leipzig', 'sc-freiburg', 'stuttgart', '1-fc-union-berlin', 'bochum', 'werder-bremen', 'wolfsburg',
                  'clermont-foot', 'havre-ac', 'lens', 'lillestrom', 'lorient', 'metz', 'monaco', 'montpellier-hsc',
                  'nantes', 'nice', 'olympique-lyonnais', 'olympique-marsella', 'paris-saint-germain-fc',
                  'stade-brestois-29', 'stade-reims', 'stade-rennes', 'strasbourg', 'toulouse-fc',
                  'ac-monza-brianza-1912', 'atalanta', 'bologna', 'cagliari', 'empoli-fc', 'fiorentina',
                  'frosinone-calcio', 'genoa', 'hellas-verona-fc', 'internazionale', 'juventus-fc', 'lazio', 'lecce',
                  'milan', 'napoli', 'roma', 'salernitana-calcio-1919', 'us-sassuolo-calcio', 'torino-fc', 'udinese',
                  'afc-bournemouth', 'arsenal', 'aston-villa-fc', 'brentford', 'brighton-amp-hov', 'burnley-fc',
                  'chelsea-fc', 'crystal-palace-fc', 'everton-fc', 'fulham', 'liverpool', 'luton-town-fc',
                  'manchester-city-fc', 'manchester-united-fc', 'newcastle-united-fc', 'nottingham-forest-fc',
                  'sheffield-united', 'tottenham-hotspur-fc', 'west-ham-united', 'wolverhampton']
    lineup_data_list = []

    for team_name in team_names:
        base_url = f'https://www.besoccer.com/team/{team_name}'

        html_text = requests.get(base_url).text
        soup = BeautifulSoup(html_text, 'html.parser')

        try:
            team = soup.find('h2', class_='title ta-c').text.strip()
        except AttributeError:
            team = "Team Name Not Found"  # Provide a default value

        left_content_divs = soup.find_all('div', class_='left-content')

        for left_content in left_content_divs:
            number_element = left_content.find('b')
            name_element = left_content.find('div', class_='desc-boxes ta-l')

            if number_element and name_element:
                number = number_element.text.strip()
                name = name_element.text.strip()
                player_data = {
                    "team": team,
                    "number": number,
                    "name": name
                }
                lineup_data_list.append(player_data)

    return lineup_data_list

def delete_all_lineup():
    try:
        session = SessionLocal()
        session.execute(delete(Lineup))
        session.commit()
    except Exception as e:  # Handle exceptions or errors that may occur during database operations
        session.rollback()
        raise e
    finally:
        session.close()

def insert_lineup_data(lineup_data):
    session = SessionLocal()
    try:
        for data in lineup_data:
            lineup = Lineup(team=data["team"], number=data["number"], name=data["name"])
            session.add(lineup)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()