from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timedelta
from app.models.highlights import HighlightsDB
from sqlalchemy import desc



def highlights_scraped():

    url = "https://hoofoot.com/"
    
    def extract_video_links(soup):
        divs = soup.find_all('div', style="display:none;visibility:hidden;")
        links = []

        for div in divs:
            anchor_tags = div.find_all('a')
            for tag in anchor_tags:
                href = tag.get('href')
                if href and not href.startswith("./"):
                    links.append(href)

        video_links = []
        for link in links:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            highlights = soup.select_one('iframe[title*="video player"]')
            if highlights:
                src = highlights.get('src')
                if src:
                    video_links.append(src)
            else:
                alternative_links = soup.find('div', {'name': 'player', 'id': 'player'})
                if alternative_links:
                    object_tag = alternative_links.find('object')
                    if object_tag:
                        a_tag = object_tag.find('a', href=True)
                        if a_tag:
                            href = a_tag['href']
                            if href:
                                video_links.append(href)

        return video_links

    def parse_date_posted(date_posted):
        if "hours ago" in date_posted or "hour ago" in date_posted:
            hours = int(re.search(r'\d+', date_posted).group())
            parsed_date = datetime.now() - timedelta(hours=hours)

        elif "days ago" in date_posted or "day ago" in date_posted:
            days = int(re.search(r'\d+', date_posted).group())
            parsed_date = datetime.now() - timedelta(days=days)

        elif date_posted == "Yesterday":
            parsed_date = datetime.now() - timedelta(days=1)

        elif date_posted == "Today":
            parsed_date = datetime.now() - timedelta(days=0)

        elif date_posted == "Just now":
            parsed_date = datetime.now()
        else:
            try:
                parsed_date = datetime.strptime(date_posted, "%d/%m/%y")
            except ValueError:
                parsed_date = None

        return parsed_date

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all('div', id=re.compile(r'per'))

    # Initialize lists to store the extracted data
    dates = []
    competitions = []
    match_names = []

    for div in divs:
        span_elements = div.find_all('span')
        for span in span_elements:
            date_text = span.text.strip()
            actual_date = parse_date_posted(date_text)
            if actual_date:
                dates.append(actual_date.strftime("%d/%m/%y"))
            else:
                # Keep the original text if it couldn't be converted
                dates.append(date_text)

        league_name = div.find('img', alt=True)
        if league_name:
            competitions.append(league_name['alt'])

    a_elements = soup.find_all('a', id=re.compile(r'drut'))

    for a in a_elements:
        event = a.find('h2')
        if event:
            match_names.append(event.text)

    video_links = extract_video_links(soup)

    # Organize the data into a list of dictionaries
    highlights_data = []
    for date, competition, match_name, video_link in zip(dates, competitions, match_names, video_links):
        actual_date = parse_date_posted(date)
        if isinstance(actual_date, str):
            # Handle the case when actual_date is a string
            date_str = actual_date
        else:
            # Convert actual_date to a string using strftime
            date_str = actual_date.strftime("%d/%m/%y")

        data_entry = {
            "date": date_str,
            "competition": competition,
            "match_name": match_name,
            "video_link": video_link
        }
        highlights_data.append(data_entry)

    return highlights_data

def insert_data_into_database(session, highlights_data):
    try:
        if highlights_data:
            for entry in highlights_data:
                existing_record = session.query(HighlightsDB).filter_by(
                    match_name=entry["match_name"]
                ).first()

                if not existing_record:
                    highlights_db = HighlightsDB(**entry)
                    session.add(highlights_db)
            session.commit()

            sorted_data = session.query(HighlightsDB).order_by(desc(HighlightsDB.date)).all()

            return sorted_data

    except Exception as e:
        session.rollback()
    finally:
        session.close()


