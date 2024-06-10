import requests
from bs4 import BeautifulSoup
from app.models.live_game_href import Live_game_href
from sqlalchemy import delete


def scrape_live_game_href():
    # Create a list to store the data
    data_list = []

    base_url = 'https://www.besoccer.com/livescore/'
    html_text = requests.get(base_url).text
    soup = BeautifulSoup(html_text, 'lxml')
    table = soup.find('div', {"id": "tableMatches"})
    # Find the first 16 div elements with id "mod_panel"
    panels = table.find_all('div', {"id": "mod_panel"})

    for panel in panels:
        # Find the div with class "panel-body p0 match-list-new panel view-more" inside each "mod_panel"
        match_panel = panel.find('div', class_='panel-body p0 match-list-new panel view-more')

        if match_panel:
            # Extract all href links and their associated team names within match_panel
            match_data = []

            # Find all <a> elements with class "match-link" within match_panel
            match_links = match_panel.find_all('a', class_='match-link')
            for match_link in match_links:
                href_link = match_link['href']

                # Extract the team names
                team_name_divs = match_link.find_all('div', class_='name')
                team_1 = team_name_divs[0].text.strip()
                team_2 = team_name_divs[1].text.strip()

                # Create a dictionary to store the data
                match_info = {
                    'href_link': href_link,
                    'team_1': team_1,
                    'team_2': team_2
                }

                match_data.append(match_info)

            # Append the list of match data to the data_list
            data_list.extend(match_data)

    return data_list


# Call the function to scrape and return the data list


# You can now use the data_list as needed

# The rest of your code remains the same


def delete_all_href(session):
    # Delete all records from the Stadiums table
    session.execute(delete(Live_game_href))
    session.commit()


def insert_href_into_database(data_list, session):
    if not data_list:
        return
    delete_all_href(session)
    for item in data_list:
        new_href = Live_game_href(
            href_link=item['href_link'],
            team_1=item["team_1"],
            team_2=item["team_2"],

        )
        session.add(new_href)
    session.commit()
