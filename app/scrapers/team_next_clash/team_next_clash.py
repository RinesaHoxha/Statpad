import requests
from bs4 import BeautifulSoup
from app.models.team_next_clash import NextMatches
from sqlalchemy import delete
from app.database import SessionLocal


def scrape_nextmatches():
    team_names = ['almeria', 'athletic-bilbao', 'atletico-madrid', 'barcelona', 'cadiz', 'celta', 'alaves', 'getafe', 'girona-fc', 'granada', 'ud-palmas', 'mallorca', 'osasuna', 'rayo-vallecano', 'betis', 'real-madrid', 'real-sociedad', 'sevilla', 'valencia-cf', 'villarreal',
             'borussia-dortmund', 'bayer-leverkusen', 'borussia-monchengla', 'bayern-munchen', 'darmstadt-98', 'eintracht-frankfurt', 'fc-augsburg', 'heidenheim', 'tsg-1899-hoffenheim', '1-fc-koln', 'mainz-amat', 'rb-leipzig', 'sc-freiburg', 'stuttgart', '1-fc-union-berlin', 'bochum', 'werder-bremen', 'wolfsburg',
             'clermont-foot', 'havre-ac', 'lens', 'lillestrom', 'lorient', 'metz', 'monaco', 'montpellier-hsc', 'nantes', 'nice', 'olympique-lyonnais', 'olympique-marsella', 'paris-saint-germain-fc', 'stade-brestois-29', 'stade-reims', 'stade-rennes', 'strasbourg', 'toulouse-fc',
             'ac-monza-brianza-1912', 'atalanta', 'bologna', 'cagliari', 'empoli-fc', 'fiorentina', 'frosinone-calcio', 'genoa', 'hellas-verona-fc', 'internazionale', 'juventus-fc', 'lazio', 'lecce', 'milan', 'napoli', 'roma', 'salernitana-calcio-1919', 'us-sassuolo-calcio', 'torino-fc', 'udinese',
             'afc-bournemouth', 'arsenal', 'aston-villa-fc', 'brentford', 'brighton-amp-hov', 'burnley-fc', 'chelsea-fc', 'crystal-palace-fc', 'everton-fc', 'fulham', 'liverpool', 'luton-town-fc', 'manchester-city-fc', 'manchester-united-fc', 'newcastle-united-fc', 'nottingham-forest-fc', 'sheffield-united', 'tottenham-hotspur-fc', 'west-ham-united', 'wolverhampton']

    data_list = []

    for team_name in team_names:
        url = f'https://www.besoccer.com/team/{team_name}'
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')

            # Find all div elements with class "panel"
            panels = soup.find('div', {'class': 'panel', 'data-cy': 'nextMatch'})

            # Iterate through the panels and extract the information
            if panels:
                # Extract other relevant data from the div elements
                status_1 = panels.find('div', class_='match-status-label')
                status = status_1.text.strip() if status_1 else "FT"
                league_element = panels.find('div', class_='middle-info ta-c')
                league = league_element.text.strip() if league_element else ""

                team_name_elements = panels.find_all('div', class_='name')
                if len(team_name_elements) == 2:
                    h_name = team_name_elements[0].text.strip()
                    a_name = team_name_elements[1].text.strip()
                else:
                    h_name = ""
                    a_name = ""

                team_image_elements = panels.find_all('img')
                if len(team_image_elements) == 2:
                    h_image = team_image_elements[0]['src']
                    a_image = team_image_elements[1]['src']
                else:
                    h_image = ""
                    a_image = ""
                marker = panels.find('div', class_='marker')
                result = marker.text.strip() if marker else "FT"

                date_element = panels.find('div', class_='date-transform date ta-c')
                date = date_element.text.strip() if date_element else ""

                # Create a dictionary to store the data
                matchday_data = {
                    'team_name': team_name,
                    'status': status,
                    'result': result,
                    'league': league,
                    'h_name': h_name,
                    'a_name': a_name,
                    'h_image': h_image,
                    'a_image': a_image,
                    'date': date
                }

                # Append the dictionary to the list
                data_list.append(matchday_data)

    return data_list

def delete_all_nextmatches(session):
    # Delete all records from the Stadiums table
    session.execute(delete(NextMatches))
    session.commit()

def insert_nextmatches_into_database(data_list, session):
    for data in data_list:
        next_match = NextMatches(
            team_name=data['team_name'],
            status=data['status'],
            result=data['result'],
            league=data['league'],
            h_name=data['h_name'],
            a_name=data['a_name'],
            h_image=data['h_image'],
            a_image=data['a_image'],
            date=data['date']
        )
        session.add(next_match)
    session.commit()
