import requests
from bs4 import BeautifulSoup
from app.models.players import Player
from sqlalchemy import delete

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Referer': 'https://www.google.com',
}

def scrape_players(league_name, num_pages=1, max_players=15):
    base_urls = {
        "La Liga": "https://www.transfermarkt.com/laliga/scorerliste/wettbewerb/ES1/saison_id/2023",
        "Bundesliga": "https://www.transfermarkt.com/bundesliga/scorerliste/wettbewerb/L1/saison_id/2023",
        "Ligue 1": "https://www.transfermarkt.com/ligue-1/scorerliste/wettbewerb/FR1/saison_id/2023",
        "Serie A": "https://www.transfermarkt.com/serie-a/scorerliste/wettbewerb/IT1/saison_id/2023",
        "Premier League": "https://www.transfermarkt.com/premier-league/scorerliste/wettbewerb/GB1/saison_id/2023",
    }

    base_url = base_urls.get(league_name)

    if base_url is None:
        return []

    all_players = []
    rank = 0

    print(f"Scraping data for {league_name} from URL: {base_url}")

    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        h1_element = soup.find('h1', class_='content-box-headline')

        table_title = h1_element.get_text(strip=True)

        print(f"{table_title} ({league_name})")

        table = soup.find('table', {'class': 'items'})

        tr_elements = table.find_all('tr', class_=['even', 'odd'])

        for tr_element in tr_elements:
            rank += 1

            player_img_element = tr_element.find('img', class_='bilderrahmen-fixed')
            if player_img_element and 'data-src' in player_img_element.attrs:
                player_img_url = player_img_element['data-src']
            else:
                player_img_url = "2 Clubs"

            player_name_element = tr_element.find_all('a', title=True)[0]
            player_name = player_name_element.text.strip()

            club_name_elements = tr_element.find_all('a', title=True)
            if len(club_name_elements) >= 2:
                club_name = club_name_elements[1]['title']
            else:
                club_name = "Club name not found"

            goals_elements = tr_element.find_all('td', class_='zentriert')
            if len(goals_elements) > 5:
                goals = goals_elements[5].text.strip()
            else:
                goals = "0"

            nationality_element = tr_element.find('img', class_='flaggenrahmen')
            nationality = nationality_element.get('title') if nationality_element else "Nationality not found"

            age = tr_element.find_all('td', class_='zentriert')[3].text.strip()

            assists = tr_element.find_all('td', class_='zentriert')[6].text.strip()

            player_data = {
                "Rank": rank,
                "Player Image URL": player_img_url,
                "Player Name": player_name,
                "Club Name": club_name,
                "Goals": goals,
                "Nationality": nationality,
                "Age": age,
                "Assists": assists,
                "League Name": league_name
            }

            all_players.append(player_data)

            if rank >= max_players:
                break
    else:
        print(f"Failed to retrieve the {league_name} web page")

    # Sort the players by goals in descending order
    all_players.sort(key=lambda x: int(x['Goals']), reverse=True)

    return all_players

def delete_all_players(session):
    session.execute(delete(Player))
    session.commit()

def save_player_data_to_db(player_data_list, session, league_name):
    if not player_data_list:
        return
    for player_data in player_data_list:
        new_player = Player(
            rank=player_data["Rank"],
            player_image_url=player_data["Player Image URL"],
            player_name=player_data["Player Name"],
            club_name=player_data["Club Name"],
            goals=player_data["Goals"],
            nationality=player_data["Nationality"],
            age=player_data["Age"],
            assists=player_data["Assists"],
            league_name=league_name,
        )

        existing_player = session.query(Player).filter_by(player_name=new_player.player_name).first()

        if existing_player:
            continue

        session.add(new_player)

    session.commit()
    print(f"Saved {len(player_data_list)} players to the database for {league_name}")
