from datetime import datetime
import requests
from bs4 import BeautifulSoup
from app.models.news import News


def backup_scrape_sport_articles():
    result = []
    url = 'https://www.teamtalk.com/'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            news_articles = []
            articles = soup.find_all('article', class_='ps-more-articles-card')

            for article in articles:
                title = article.find('h3', class_='text-title').text.strip()
                img_tag = article.find('img', class_='h-full object-center object-cover rounded-md ps-lazy-img')
                img_url = img_tag.get('data-src') if img_tag else None
                link_tag = article.find('a', href=True)
                article_url = link_tag['href'] if link_tag else None
                date_tag = article.find('time', class_='text-time')
                date = date_tag['datetime'] if date_tag else None

                day_part, time_part = date.rsplit(' ', 1)

                day_part = day_part.replace("th", "").replace("st", "")
                parsed_date = datetime.strptime(day_part + " " + time_part, "%A %d %B %Y %I:%M %p")
                formatted_date = parsed_date.strftime("%d/%m/%y %I:%M%p").replace(" 0", " ")

                news_articles.append({
                    'title': title,
                    'link': article_url,
                    'image_url': img_url,
                    'timestamp': formatted_date,
                })
                result.extend(news_articles)
            result = {"articles": news_articles}
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve data from {url}: {e}")

    return result

def backup_save_to_db(results, session):
    if not results:
        return

    for result in results:
        new_article = News(
            title=result["title"],
            url=result["link"],
            image_url=result['image_url'],
            dateposted=result['timestamp'],
            date_scraped=datetime.now()
        )

        if session.query(News).filter_by(title=result['title']).first():
            continue

        session.add(new_article)

    session.commit()
