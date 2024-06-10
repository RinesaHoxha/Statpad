import requests
from bs4 import BeautifulSoup
from app.models.media import MediaDB
from app.database import SessionLocal

def get_media_links_with_text():
    league_names = ["primera_division", "bundesliga", "ligue_1", "serie_a", "premier_league"]
    media_data = []

    for league_name in league_names:
        base_url = f"https://www.besoccer.com/competition/media/{league_name}"

        html_text = requests.get(base_url).text
        soup = BeautifulSoup(html_text, 'html.parser')

        media_list = soup.select('a.grid-gallery-item')
        text_element = soup.select_one('div.temp-select.custom.ta-c h1')

        if text_element:
            text = text_element.text
        else:
            text = "Text not found"

        for item in media_list:
            media_link = item['href']
            media_data.append({
                "text": text,
                "link": media_link
            })

    return media_data

def insert_media_data_into_database(media_data):
    session = SessionLocal()

    try:
        if media_data:
            for entry in media_data:
                media_db = MediaDB(**entry)
                session.add(media_db)
            session.commit()

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
