from datetime import date
import requests
from bs4 import BeautifulSoup
from app.models.livestream_links import Livestream_links
from sqlalchemy import delete


def scrape_webpage():
    url = 'https://sportsonline.gl/'
    # Send an HTTP GET request to the URL to retrieve the webpage content
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        body_tag = soup.text.split("\n")[:110]  # Split every line individually

        # Initialize a list to store the extracted lines
        extracted_matches = []

        current_date = date.today()

        if body_tag:
            # Split the text into lines
            lines = body_tag
            # Process each line
            for line in lines:
                # Check if the line starts with a time format and contains both | and -
                if any(time_str in line for time_str in
                       ["00:", "01:", "02:", "03:", "04:", "05:", "06:", "07:", "08:", "09:",
                        "10:", "11:", "12:", "13:", "14:", "15:", "16:", "17:", "18:", "19:",
                        "20:", "21:", "22:",
                        "23:"]) and '|' in line and 'x' in line and "Handball" not in line and "Rugby" not in line:
                    # Extract the relevant information from the line
                    match_parts = line.split('|')
                    time_and_teams = match_parts[0].strip().split('   ')
                    if len(time_and_teams) == 2:
                        time = time_and_teams[0]
                        teams = time_and_teams[1].split(' x ')
                        if len(teams) == 2:
                            home_team, away_team = teams
                            url = match_parts[1].strip()
                            line_dict = {
                                "Time": time.strip(),
                                "Match": f"{home_team} x {away_team}",
                                "URL": url,
                                "DATE": current_date.strftime('%Y-%m-%d')
                            }
                            extracted_matches.append(line_dict)
                    else:
                        print("Skipping line:", line)

            return extracted_matches

def delete_all_links(session):
    # Delete all records from the Livestream_links table
    session.execute(delete(Livestream_links))
    session.commit()


def insert_links_into_database(extracted_matches, session):
    if not extracted_matches:
        return
    delete_all_links(session)
    for line_dict in extracted_matches:
        new_match = Livestream_links(
            time=line_dict["Time"],
            match=line_dict["Match"],
            url=line_dict["URL"],
            date=line_dict["DATE"]
        )
        session.add(new_match)
    session.commit()

