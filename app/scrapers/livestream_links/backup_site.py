import re
from datetime import date
import requests
from bs4 import BeautifulSoup
from app.models.livestream_links import Livestream_links
from sqlalchemy import delete
def get_iframe_links(url):
    # Fetch the webpage content
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        # Initialize a list to store iframe links
        iframe_links = []

        # Find all <iframe> elements
        iframe_elements = soup.find_all('iframe')
        for iframe in iframe_elements:
            iframe_src = iframe.get('src')
            if iframe_src:
                iframe_links.append(iframe_src)

        return iframe_links

def scrape_and_store_links():
    # Fetch the webpage content
    url = 'https://freestreams-live1.se/football-streamz5/'
    response = requests.get(url)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        # Find the body element
        body = soup.find('body')

        # Initialize a list to store links and associated matchtime and event-title
        extracted_matches = []

        # Find all <tr> elements within the body
        tr_elements = body.find_all('tr')
        current_date = date.today()
        iframe_links = []
        for tr in tr_elements:
            # Find all links within the <tr> element
            tr_links = tr.find_all('a', href=True)
            for link in tr_links:
                href = link['href']

                # Find the associated matchtime and event-title in <td> elements
                match_time = tr.find('td', class_='matchtime')
                event_title = tr.find('td', class_='event-title')

                if match_time and event_title:
                    extracted_match = {
                        'Time': match_time.text.strip(),
                        'Match': event_title.text.strip(),
                        'DATE': date.today().strftime('%d-%m-%Y'),
                        'URL': []  # Initialize the URL list
                    }

                    # Get iframe links for the current href
                    iframe_links = get_iframe_links(href)

                    # Add each iframe link to the URL list
                    for iframe_link in iframe_links:
                        extracted_match['URL'].append(iframe_link)

                    extracted_matches.append(extracted_match)
        return extracted_matches



def delete_all_links(session):
    # Delete all records from the Livestream_links table
    session.execute(delete(Livestream_links))
    session.commit()


def insert_links_into_database_backup(extracted_matches, session):
    if not extracted_matches:
        return
    delete_all_links(session)
    for line_dict in extracted_matches:
        formatted_match = ' '.join(line_dict['Match'].strip().split())

        # Format the "URL" field as a single string (assuming there's only one URL)
        formatted_url = line_dict["URL"][0] if line_dict["URL"] else ''
        new_match = Livestream_links(
            time=line_dict["Time"],
            match=formatted_match,
            url=formatted_url,
            date=line_dict["DATE"]
        )
        session.add(new_match)
    session.commit()