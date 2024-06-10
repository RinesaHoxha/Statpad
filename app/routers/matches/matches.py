from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
from fastapi.templating import Jinja2Templates
from app.models.highlights import HighlightsDB
from app.models.matches import LiveSoccerScores,TomorrowSoccerScores
from app.scrapers.matches.matches import scrape_and_store_soccer_scores,save_to_live_scores_table,save_to_tomorrow_scores_table
from app.models.live_game_href import Live_game_href
from app.database import SessionLocal
from typing import Optional
from datetime import timedelta
from app.models.news import News



templates=Jinja2Templates(directory='templates')

router = APIRouter(
    prefix='/matches',  # Set the prefix to 'matches'
    tags=['matches']
)

@router.get("/scrape-scores/")
def scrape_and_save_live_scores(date: Optional[str] = datetime.now().strftime("%Y-%m-%d")):
    try:
        print("Start of scrape_and_save_live_scores")
        if date is None:
            query_date = datetime.now().strftime("%Y-%m-%d")
        else:
            query_date = date

        print(f"Query date: {query_date}")

        if not query_date:
            raise HTTPException(status_code=400, detail="Invalid date provided")


        scraped_data=scrape_and_store_soccer_scores(query_date)


        db = SessionLocal()
        for match_data in scraped_data:
            if match_data["match_date"] == query_date:
                save_to_live_scores_table(match_data, db)
            elif match_data["match_date"] == (datetime.strptime(query_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"):
                save_to_tomorrow_scores_table(match_data, db)

        return {"message": f"Live soccer scores for {query_date} scraped and saved successfully!"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@router.get("/scores/")
def get_scores_by_date(date: Optional[str] = None):
    db = SessionLocal()

    if date is not None:
        # User provided a specific date
        query_date = date
        live_scores = db.query(LiveSoccerScores).filter(LiveSoccerScores.match_date == query_date).order_by(LiveSoccerScores.league).all()

        # If live scores exist for the specified date, return them
        if live_scores:
            return {"live_scores": live_scores}
    else:
        # Default to today's date if no date provided
        query_date = datetime.now().strftime("%Y-%m-%d")

    # Query tomorrow's scores only if the date doesn't exist in live scores
    tomorrow_scores = db.query(TomorrowSoccerScores).filter(TomorrowSoccerScores.match_date == query_date).order_by(TomorrowSoccerScores.league).all()

    db.close()

    return {"tomorrow_scores": tomorrow_scores}



@router.get('/view')
def scores_view(
        request: Request,
        match_date: Optional[str] = None,
        league_name: Optional[str] = None
):
    db = SessionLocal()
    scores_query = db.query(LiveSoccerScores)

    if match_date and league_name:
        scores_query = scores_query.filter(
            LiveSoccerScores.match_date == match_date,
            LiveSoccerScores.league == league_name
        ).order_by(LiveSoccerScores.match_date)  # Change the order_by clause to match_date
    elif match_date:
        scores_query = scores_query.filter(LiveSoccerScores.match_date == match_date).order_by(
            LiveSoccerScores.match_date)
    elif league_name:
        scores_query = scores_query.filter(LiveSoccerScores.league == league_name).order_by(
            LiveSoccerScores.match_date).limit(10)
    else:
        # No match_date or league_name provided, default to today
        match_date = datetime.now().strftime("%Y-%m-%d")
        scores_query = scores_query.filter(LiveSoccerScores.match_date == match_date).order_by(
            LiveSoccerScores.match_date)

    scores = scores_query.all()

    page = 1
    total_pages = 1  # Assuming all scores fit on one page since there's no paging logic provided

    page_numbers = range(1, total_pages + 1)
    href = db.query(Live_game_href).all()

    if not scores:
        raise HTTPException(status_code=404, detail="No scores found for the specified date or league")

    news = db.query(News).all()
    hg = db.query(HighlightsDB).all()

    return templates.TemplateResponse('matches.html',
                                      {
                                          'request': request,
                                          'scores': scores,
                                          'total_pages': total_pages,
                                          'current_page': page,
                                          'page_numbers': page_numbers,
                                          'live_game_href': href,
                                          'match_date': match_date,
                                          'league_name': league_name,
                                          'news': news,
                                          'hg': hg
                                      })






