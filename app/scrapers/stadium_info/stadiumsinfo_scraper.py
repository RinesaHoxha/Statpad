import requests
from bs4 import BeautifulSoup
from app.models.stadiums_info import Stadiumsinfo

def scrape_stadiums():
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
    data_list = []

    for team_name in team_names:
        base_url = f'https://www.besoccer.com/team/{team_name}'
        response = requests.get(base_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            try:
                team = soup.find('h2', class_='title ta-c').text.strip()
            except AttributeError:
                team = "Team Name Not Found"  # Provide a default value

            stadium_info = soup.find('div', id='mod_stadium')

            # Extract the desired information
            stadium_name = stadium_info.find('div', class_='name').text
            city = stadium_info.find('div', class_='city').text
            address = stadium_info.find('div', class_='address').text
            image_url = stadium_info.find('img')['src']

            construction_date = stadium_info.find('div', text='Date of construction').find_next('div').text
            capacity = stadium_info.find('div', text='Capacity').find_next('div').text
            size_element = stadium_info.find('div', text='Size')
            if size_element:
                size = size_element.find_next('div').text
            else:
                size = "Size information not found"
            grass_type_element = stadium_info.find('div', text='Type of grass')

            if grass_type_element:
                grass_type = grass_type_element.find_next('div').text
            else:
                grass_type = "Grass type information not found"

            phone_element = stadium_info.find('div', text='Phone')

            if phone_element:
                phone = phone_element.find_next('div').text
            else:
                phone = "Phone information not found"

            fax_element = stadium_info.find('div', text='Fax')

            if fax_element:
                fax = fax_element.find_next('div').text
            else:
                fax = "Fax information not found"

            # Print the extracted information
            stadium_data = {
                "stadium_name": stadium_name,
                "image": image_url,
                "city": city,
                "address": address,
                "construction_date": construction_date,
                "capacity": capacity,
                "size": size,
                "grass_type": grass_type,
                "phone": phone,
                "fax": fax,
                'team': team
            }
            data_list.append(stadium_data)
    return data_list


def insert_stadiumsinfo_into_database(data_list, session):
    if not data_list:
        return
    for item in data_list:
        new_stadium = Stadiumsinfo(
            stadium_name=item["stadium_name"],
            image=item["image"],
            city=item["city"],
            address=item["address"],
            construction_date=item["construction_date"],  # Correct key
            capacity=item['capacity'],
            size=item['size'],
            grass_type=item['grass_type'],  # Correct key
            phone=item['phone'],
            fax=item['fax'],
            team=item['team']
        )
        session.add(new_stadium)
    session.commit()