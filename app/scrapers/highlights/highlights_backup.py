from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
from app.models.highlights import HighlightsDB

def backup_highlights_scraped():
    url = 'https://fasthighlights.net'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    match_names = []
    dates = []
    competitions = []

    divs = soup.find_all('div', class_='aft-readmore-wrapper')
    for div in divs:
        a_tag = div.find('a')
        href = a_tag.get('href')

        response = requests.get(href)
        sub_soup = BeautifulSoup(response.text, 'html.parser')

        video_elements = sub_soup.find_all('iframe', attrs={"data-src": True})

        video_link = "N/A"

        for iframe in video_elements:
            src = iframe['data-src']
            if src.startswith("//"):
                src = "https:" + src
            src = src.split('?')[0]
            video_link = src
            break

        links.append(video_link)

        match_name_elements = sub_soup.find_all('h1', class_='entry-title')
        for element in match_name_elements:
            match_name_text = element.text.strip().split('/')[0].strip()
            team_names = match_name_text.split(' v ')
            match_name_text = ' vs '.join(team_names)
    
            match_names.append(match_name_text)

        competition_elements = sub_soup.find('h2', class_='wp-block-heading has-small-font-size')
        if competition_elements:
            text_inside_parentheses = re.search(r'\(([^)]+)\)', competition_elements.text)
            competition_text = text_inside_parentheses.group(1) if text_inside_parentheses else "N/A"
        else:
            competition_text = "N/A"

        competitions.append(competition_text)

        date_elements = sub_soup.find_all('span', class_='item-metadata posts-date')
        for element in date_elements:
            date_text = element.a.text.strip()
            date_object = datetime.strptime(date_text, "%d/%m/%Y")
            formatted_date = date_object.strftime("%d/%m/%y")
            dates.append(formatted_date)

    min_length = min(len(links), len(match_names), len(competitions), len(dates))

    data_list = []
    for i in range(min_length):
        data_dict = {
            "date": dates[i],  
            "competition": competitions[i],  
            "match_name": match_names[i], 
            "video_link": links[i]  
    }
    data_list.append(data_dict)

    return data_list

def insert_data_into_database(session, data_list):
    try:
        if data_list:
            for entry in data_list:
                existing_record = session.query(HighlightsDB).filter_by(
                    match_name=entry["match_name"]
                ).first()
                
                if not existing_record:
                    highlights_db = HighlightsDB(**entry)
                    session.add(highlights_db)
            session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()
