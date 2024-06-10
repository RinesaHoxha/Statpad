from datetime import datetime
import requests
from bs4 import BeautifulSoup
from sqlalchemy import delete
from app.database import SessionLocal
from app.models.bet import Bets

def scrape_bet():
    result = []
    url = f'https://lumisport.com/book/sport/1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', class_='sbtable')

    liga = None  # Initialize liga

    for row in table.find_all('tr'):

        bets = []
        header = row.find('th', class_='lgtit')
        if header:
            liga_text = ' - '.join(a.text.strip() for a in header.find_all('a'))
            parts = liga_text.split(" - ")
            liga = " - ".join(parts[1:])
        else:
            columns = row.find_all('td')
            if columns and len(columns) >= 13:
                date = columns[1].text.strip()
                team1 = columns[2].text.strip()
                team2 = columns[4].text.strip()
                odds_1 = columns[5].text.strip()
                odds_x = columns[6].text.strip()
                odds_2 = columns[7].text.strip()

                # Check and clean odds values
                try:
                    odds_1 = float(odds_1)
                    odds_x = float(odds_x)
                    odds_2 = float(odds_2)
                except ValueError:
                    # Handle the case where odds values are not valid numbers
                    continue

                bets.append({
                    'liga': liga,
                    'date': date,
                    'team1': team1,
                    'team2': team2,
                    'odds_1': odds_1,
                    'odds_x': odds_x,
                    'odds_2': odds_2,
                })
            result.extend(bets)

    return {'bets': result}

def delete_all_bets():
    try:
        session = SessionLocal()
        session.execute(delete(Bets))
        session.commit()
    except Exception as e:  # Handle exceptions or errors that may occur during database operations
        session.rollback()
        raise e
    finally:
        session.close()



def save_to_db(results, session):
    if not results:
        return
    for result in results:
        new_bets = Bets(
            liga=result['liga'],
            date=result['date'],
            team1= result['team1'],
            team2=result['team2'],
            odds_1= result['odds_1'],
            odds_x= result['odds_x'],
            odds_2= result['odds_2'],
            date_scraped=datetime.now()
        )
        # if session.query(Bets).filter_by(date=result['date']).first():
        #     continue
        session.add(new_bets)
    session.commit()