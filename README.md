# Real-time Twitter Sentiment Analysis System

A web-based system for real-time sentiment analysis of Twitter data, designed for government officials, researchers, marketers, and policy makers to analyze public sentiment and make informed decisions.

## Features

- Secure user authentication and role-based access control
- Real-time Twitter data streaming using Kafka
- Sentiment analysis using Natural Language Processing
- Interactive dashboards with real-time updates
- Data visualization and analytics
- Report generation
- Geographic visualization of tweet locations
- MongoDB integration for data storage

## Tech Stack

- Backend: Django
- Frontend: Django Templates, Bootstrap 5
- Database: MongoDB (for tweets and analytics), SQLite (for user management)
- Message Queue: Apache Kafka
- Real-time Processing: Tweepy
- Data Analysis: NLTK, TextBlob, Scikit-learn
- Visualization: Chart.js, Leaflet.js

## Prerequisites

- Python 3.8+
- MongoDB
- Apache Kafka
- Twitter Developer Account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sentiment-analysis-system.git
cd sentiment-analysis-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your configuration:
```
DJANGO_SECRET_KEY=your_secret_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
MONGODB_URI=mongodb://localhost:27017/
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the admin interface at `http://localhost:8000/admin/` to manage users and roles
2. Regular users can access the system at `http://localhost:8000/`
3. Start the Kafka consumer:
```bash
python manage.py start_kafka_consumer
```

4. Start the Twitter stream:
```bash
python manage.py start_twitter_stream
```

## Project Structure

```
sentiment_analysis_system/
├── users/                 # User management app
├── analytics/            # Data analytics app
├── sentiment_analytics/  # Sentiment analysis app
├── frontend/            # Frontend templates and static files
├── reports/             # Report generation app
├── models/              # ML model files
├── static/              # Global static files
├── templates/           # Global templates
└── media/              # User-uploaded files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Twitter API for providing access to real-time data
- MongoDB for efficient data storage
- Apache Kafka for reliable message streaming
- NLTK and TextBlob for natural language processing 