import requests
from bs4 import BeautifulSoup
from app.models.coaches import CoachesDB
from app.database import SessionLocal

def get_coaches_list():
    league_names = ["primera_division", "bundesliga", "ligue_1", "serie_a", "premier_league"]
    data_dict_list = []

    for league_name in league_names:
        base_url = f'https://www.besoccer.com/competition/coaches/{league_name}'

        html_text = requests.get(base_url).text
        soup = BeautifulSoup(html_text, 'html.parser')

        coach_list = soup.find_all('li')
        for coach_item in coach_list:
            coach_link = coach_item.find('a', class_='item-box')
            if coach_link:
                coach_logo = coach_link.find('img', class_='player-circle-box')['src']
                coach_name = coach_link.find('div', class_='name bold ml10').text.strip()
                club_link = coach_link.find('div', class_='name row align-center ml10 mt5').find('div', class_='ml5')
                club_name = club_link.text.strip()
                team_logo = coach_link.find_all('img', class_='player-circle-box noborder')[-1]['src']
                nationality_flag = coach_link.find('img', class_='w-20')['src']
                data_dict = {
                    "coach_name": coach_name,
                    "club_name": club_name,
                    "coach_logo": coach_logo,
                    "team_logo": team_logo,
                    "nationality_flag": nationality_flag
                }
                data_dict_list.append(data_dict)

    return data_dict_list

def insert_coach_data_into_database(data_dict_list):
    session = SessionLocal()

    try:
        if data_dict_list:
            for entry in data_dict_list:
                coach_db = CoachesDB(**entry)
                session.add(coach_db)
            session.commit()

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
