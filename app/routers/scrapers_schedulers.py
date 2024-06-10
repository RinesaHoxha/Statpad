import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import UserDB


scheduler = BackgroundScheduler()

@scheduler.scheduled_job("interval", minutes=10)
def sportnews_scrape():
    requests.get(
        url="http://localhost:8080/sportnews/scrape",
    )

@scheduler.scheduled_job("interval", minutes=5)
def bets_scrape():
    requests.get(
        url="http://localhost:8080/bets/scrapebets"
    )

@scheduler.scheduled_job("interval", minutes=5)
def leaguetable_scrape():
    requests.get(
        url="http://localhost:8080/league_table/scrape"
    )

@scheduler.scheduled_job("interval", minutes=5)
def highlights_scrape():
    requests.get(
        url="http://localhost:8080/highlights/scrapehighlights"
    )
@scheduler.scheduled_job("interval", hours=6)
def link_scrape():
    requests.get(
        url="http://localhost:8080//livestream_scraper/scrape-and-insert"
    )

@scheduler.scheduled_job("interval", minutes=1)
def scores_scrape():
    requests.get(
        url="http://localhost:8080/matches/scrape-scores/"
    )

@scheduler.scheduled_job("interval", minutes=50)
def href_scrape():
    requests.get(
        url="http://localhost:8080/game_href/scrape-and-insert-href"
    )

def delete_unverified_users():
    try:
        db = SessionLocal()
        cutoff_time = datetime.utcnow() - timedelta(days=3)
        db.query(UserDB).filter(UserDB.is_verified == False, UserDB.created_at <= cutoff_time).delete()
        db.commit()
    finally:
        db.close()

scheduler.add_job(
    delete_unverified_users,
    trigger="interval",
    days=1,
    start_date=datetime.now() + timedelta(seconds=10),
)

