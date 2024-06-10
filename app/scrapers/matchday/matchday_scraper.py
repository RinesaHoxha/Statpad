import requests
from bs4 import BeautifulSoup
from app.models.matchday import Matchday
from sqlalchemy import delete


# Replace this with the URL of the web page you want to scrape
# Replace with the actual URL

# Send an HTTP GET request to the URL
def scrape_matchday():
    league_names = ["primera_division", "bundesliga", "ligue_1", "serie_a", "premier_league",'champions_league','europa_league']
    data_list = []
    for league_name in league_names:
        base_url = f'https://www.besoccer.com/competition/scores/{league_name}'

        html_text = requests.get(base_url).text
        soup = BeautifulSoup(html_text, 'lxml')

        response = requests.get(base_url)
        # Check if the request was successful
        if response.status_code == 200:
            response.encoding = 'utf-8'
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'lxml')

            # Find all div elements with class "match-link p0"
            panels = soup.find_all('div', class_='match-link p0')

            # Iterate through the panels and extract the information
            for panel in panels:
                # Extract data from the JSON-LD script tag
                script_tag = panel.find('script', type='application/ld+json')
                if script_tag:
                    json_data = script_tag.string.strip()
                else:
                    continue
                matchweek_1 = soup.find('div', class_='comp-matches')
                matchweek_2 = matchweek_1.find('h1', class_='panel-title')
                matchweek = matchweek_2.text.strip() if matchweek_2 is not None else ""
                # Extract other relevant data from the div elements
                league_element_1 = panel.find('div', class_='info-head')
                league_element_2 = league_element_1.find('div',class_='middle-info ta-c')
                league = league_element_2.text.strip() if league_element_2 else ""

                name_1 = panel.find('div', class_='team-name ta-r team_left')
                h_name_element = name_1.find('div', class_='name') if name_1 else None
                h_name = h_name_element.text.strip() if h_name_element else ""
                # If 'team-name ta-r team_left' is empty, look for 'team-name ta-r team_left winner'
                if not h_name:
                    name_1_winner = panel.find('div', class_='team-name ta-r team_left winner')
                    h_name_element_winner = name_1_winner.find('div', class_='name') if name_1_winner else None
                    h_name = h_name_element_winner.text.strip() if h_name_element_winner else ""

                name_2 = panel.find('div', class_='team-name ta-l team_right')
                a_name_element = name_2.find('div', class_='name') if name_2 else None
                a_name = a_name_element.text.strip() if a_name_element else ""
                # If 'team-name ta-r team_left' is empty, look for 'team-name ta-r team_left winner'
                if not a_name:
                    name_2_winner = panel.find('div', class_='team-name ta-l team_right winner')
                    a_name_element_winner = name_2_winner.find('div', class_='name') if name_2_winner else None
                    a_name = a_name_element_winner.text.strip() if a_name_element_winner else ""

                time_element = panel.find('p', class_='match_hour time')
                time = time_element.text.strip() if time_element else ""

                if not time:
                    marker = panel.find('div', class_='marker')
                    time = marker.text.strip() if marker else"FT"

                date_element = panel.find('div', class_='date-transform date ta-c')
                date = date_element.text.strip() if date_element else ""

                # Extract both images from the 'image-box' div
                image_box = panel.find('a')
                images = image_box.find_all('img')
                h_image = images[0]['src']
                a_image = images[1]['src']

                # Create a dictionary to store the data
                matchday_data = {
                    'matchweek': matchweek,
                    'league': league,
                    'h_name': h_name,
                    'a_name': a_name,
                    'h_image': h_image,
                    'a_image': a_image,
                    'time': time,
                    'date': date
                }

                # Append the dictionary to the list
                data_list.append(matchday_data)
    return data_list


def delete_all_matchday(session):
    # Delete all records from the Stadiums table
    session.execute(delete(Matchday))
    session.commit()


def insert_matchday_into_database(data_list, session):
    if not data_list:
        return
    delete_all_matchday(session)
    for item in data_list:
        new_matchday = Matchday(
            matchweek=item['matchweek'],
            league=item["league"],
            h_team=item["h_name"],
            a_team=item["a_name"],
            h_image=item["h_image"],
            a_image=item["a_image"],
            time=item["time"],
            date=item["date"]
        )
        session.add(new_matchday)
    session.commit()
