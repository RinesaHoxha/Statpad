import requests
from bs4 import BeautifulSoup
from app.models.team import Team
from sqlalchemy import delete
from app.utils.team_names import team_names
import json
import re

# Replace this with the URL of the web page you want to scrape
# Replace with the actual URL

# Send an HTTP GET request to the URL
def scrape_team():

    data_list = []

    for team_name in team_names:
        base_url = f'https://besoccer.com/team/squad/{team_name}'

        html_text = requests.get(base_url).text

        response = requests.get(base_url)

        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(html_text, 'lxml')
            rows = soup.find_all('tr', class_='row-body')
            team = soup.find('h2', class_='title ta-c').text.strip()

            for row in rows:
                script = row.find('script', type='application/ld+json')
                if script:
                    data = script.contents[0]
                    data = json.loads(data)
                    job_title = data['jobTitle']
                    name_element = row.find('td', class_='name').find('a')
                    name = name_element.text.strip()
                    image = data['image']
                    number = row.find('td', class_='number-box').text.strip()
                    team_performance = [cell.text.strip() for cell in
                                        row.find_all('td', {'data-content-tab': 'team_performance'})]
                    team_info_cells = row.find_all('td', {'data-content-tab': 'team_info'})
                    team_info = [re.sub(r'\s+', ' ', cell.get_text(strip=True)) for cell in team_info_cells if
                                 cell.get_text(strip=True)]

                    team_data = {
                        'name': name,
                        'job_title': job_title,
                        'number': number,
                        'image': image,
                        'team_performance': team_performance,
                        'team_info': team_info,
                        'team': team,
                    }

                    data_list.append(team_data)

    return data_list


def delete_all_team(session):
    # Delete all records from the Stadiums table
    session.execute(delete(Team))
    session.commit()


def insert_team_into_database(data_list, session):
    if not data_list:
        return
    delete_all_team(session)
    for item in data_list:
        new_team = Team(
            name=item['name'],
            job_title=item['job_title'],
            number=item["number"],
            image=item["image"],
            team_performance=item["team_performance"],
            team_info=item["team_info"],
            team=item["team"]
        )
        session.add(new_team)
    session.commit()
