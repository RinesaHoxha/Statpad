
import requests
from bs4 import BeautifulSoup
from app.models.stadiums import Stadiums
from sqlalchemy import delete





# Replace this with the URL of the web page you want to scrape
  # Replace with the actual URL

# Send an HTTP GET request to the URL
def scrape_stadiums():
    league_names = ["primera_division", "bundesliga", "ligue_1", "serie_a", "premier_league"]
    data_list = []
    for league_name in league_names:
        base_url = f'https://www.besoccer.com/competition/stadiums/{league_name}'

        html_text = requests.get(base_url).text
        soup = BeautifulSoup(html_text, 'lxml')
        response = requests.get(base_url)
    # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all div elements with class "panel mb0"
            panels = soup.find_all('div', class_='panel mb0')

            # Create a list to store the data as dictionaries


            # Iterate through the panels and extract the information
            for panel in panels:
                # Extract data from the JSON-LD script tag
                script_tag = panel.find('script', type='application/ld+json')
                if script_tag:
                    json_data = script_tag.string.strip()
                else:
                    continue

                # Extract other relevant data from the div elements
                name = panel.find('a', class_='name').text.strip()
                image = panel.find('img', alt=name)['src']
                year = panel.find('div', class_='info mt5').text.strip()
                capacity = panel.find('div', class_='info mb5').text.strip()


                # Extract both images from the 'image-box' div
                image_box = panel.find('div', class_='image-box')
                images = image_box.find_all('img')
                stadium_img = images[0]['src']
                team_img = images[1]['src']

                # Create a dictionary to store the data
                stadium_data = {
                    'name': name,
                    'stadium_image': stadium_img,  # Store the stadium image
                    'team_image': team_img,  # Store the team image
                    'year': year,
                    'capacity': capacity
                }

                # Append the dictionary to the list
                data_list.append(stadium_data)
    return data_list
            # Print the extracted data for testing


            # Now you can use the 'data_list' to save the data into a database using SQLAlchemy and Pydantic.



def delete_all_stadiums(session):
    # Delete all records from the Stadiums table
    session.execute(delete(Stadiums))
    session.commit()

def insert_stadiums_into_database(data_list, session):
    if not data_list:
        return
    # delete_all_stadiums(session)
    for item in data_list:
        new_stadium = Stadiums(
            name=item["name"],
            img=item["stadium_image"],
            year=item["year"],
            capacity=item["capacity"],
            team=item["team_image"]
            )
        session.add(new_stadium)
    session.commit()