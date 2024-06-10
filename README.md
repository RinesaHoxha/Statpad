# Statpad

**Statpad** is a comprehensive football website that provides real-time football match updates, predictions, and personalized content for users. The backend is developed in Python using FastAPI, and the frontend is crafted with HTML, CSS, and JavaScript. Data is scraped from various football websites using BeautifulSoup and stored in a PostgreSQL database. The website also features an AI-powered prediction engine with over 70% accuracy in predicting match winners.

## Features

- **Real-time Football Matches**: Stay updated with live scores and match details.
- **AI Predictions**: Get match predictions with over 70% accuracy.
- **User Authentication**: Sign up and log in to access personalized features.
- **User Profiles**: Choose your favorite football team and get tailored news and match updates.
- **Betting Information**: Logged-in users can view betting information.
- **Results**: Access detailed match results.
- **News**: Stay informed with the latest football news.
- **My Team**: View personalized content related to your favorite team.
- **Highlights**: Watch match highlights.
- **Competitions**: Get information on various football competitions.
- **Livestream**: Post and comment on live matches and events.
- **Socials**: Engage with other users by posting and commenting on various topics.
- **Bets**: View and place bets on upcoming matches.

## Technologies Used

### Backend
- **Python**
- **FastAPI**

### Frontend
- **HTML**
- **CSS**
- **JavaScript**

### Data Scraping
- **BeautifulSoup**

### Database
- **PostgreSQL**

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/RinesaHoxha/Statpad.git
    cd Statpad
    ```

2. **Set up a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the PostgreSQL database:**
    - Create a database named `statpad`.
    - Update the database connection settings in the FastAPI configuration.

5. **Run the FastAPI application:**
    ```sh
    uvicorn main:app --reload
    ```

6. **Navigate to the frontend directory and open `index.html` in your browser to view the website.**

   ![image](https://github.com/RinesaHoxha/Statpad/assets/122171723/8dbc79ec-0616-4823-be25-2f6036a2d9e1)
sneak peak :)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
