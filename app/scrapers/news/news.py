from datetime import datetime
import requests
from bs4 import BeautifulSoup
from app.models.news import News

def scrape_sport_articles():
    url = 'https://www.skysports.com/football/news'
    news_articles = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all news items
        news_items = soup.select('.news-list__item')

        for news_item in news_items:
            title = news_item.find(class_='news-list__headline-link').get_text()
            link = news_item.find(class_='news-list__headline-link')['href']
            timestamp = news_item.select_one('.label__timestamp').get_text(strip=True)
            image_url = news_item.find('img', class_='news-list__image')['data-src']

            snippet = news_item.find('p', class_='news-list__snippet')
            context = snippet.get_text(strip=True) if snippet else "Snippet not found"

            news_articles.append({
                'title': title,
                'link': link,
                'image_url': image_url,
                'timestamp': timestamp,
                'context': context
            })

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data from {url}: {e}")
    return news_articles


def save_to_db(results, session):
    if results:
        for article in results:
            new_article = News(
                title=article["title"],
                url=article["link"],
                image_url=article['image_url'],
                dateposted=article['timestamp'],
                context=article['context'],
                date_scraped=datetime.now()
            )

            # Check if the article with the same title exists in the database before adding
            existing_article = session.query(News).filter_by(title=new_article.title).first()
            if not existing_article:
                session.add(new_article)

        session.commit()