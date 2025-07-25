# Flight Path AI Project

# Badges

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# Screenshots

Below are some screenshots of the Flight Path AI Project web interface and features:

![Home Page](static/img/home.jpeg)
_Home Page: Main dashboard for flight path AI project._

![Flight Optimization Empty](static/img/empty_optimization.jpeg)
![Flight Optimization](static/img/optimization.jpeg)
_Flight Optimization: Interface for optimizing flight routes._

![Map Visualization](static/img/map.jpeg)
_Map Visualization: Interactive map showing flight paths and airports._

![Chatbot (Gemini AI)](static/img/chat_bot_1.jpeg)
![Chatbot (Gemini AI)](static/img/chat_bot_2.jpeg)
_Chatbot (Gemini AI): AI-powered assistant for user queries._

> To add your own screenshots, place image files in `static/img/` and update the paths above as needed.

## Overview

Flight Path AI is a comprehensive platform for optimizing and analyzing flight routes using AI and advanced algorithms. It integrates airport data, flight information, and machine learning models to provide efficient flight path predictions and operational insights.

## Features

- **Flight Path Optimization**: Uses QAOA and other optimizers for route planning.
- **Airport Data Integration**: Supports cleaned and location-based airport datasets.
- **AI Model Integration**: Predicts flight angles and paths using trained Keras models.
- **Supabase Integration**: Manages data storage and retrieval with Supabase.
- **Web Interface**: Interactive web pages for flight info, optimization, reports, and chatbot.
- **Gemini AI Chatbot**: Integrated Gemini AI for intelligent chatbot interactions.
- **Visualization**: Map-based visualization of flight paths and airport locations.

## Folder Structure

```
Flight/
├── FILGHT/                      # Main Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── api_utils.py
│   ├── asgi.py
│   ├── models.py
│   ├── optimizer.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── wsgi.py
│   ├── migrations/              # Database migrations
│   └── templates/               # HTML templates
│       ├── base.html
│       ├── chat_bot.html
│       ├── flight_info.html
│       ├── home.html
│       ├── map.html
│       ├── optimize.html
│       ├── report.html
│       └── about.html
├── static/                  # Static files
│   ├── css/
│   │   ├── airport_dropdown.css
│   │   ├── chat_bot.css
│   │   ├── flight.css
│   │   ├── map.css
│   │   ├── navbar.css
│   │   ├── optimize.css
│   │   ├── report.css
│   ├── js/
│   │   ├── airport_dropdown.js
│   │   ├── chat_bot.js
│   │   ├── flight.js
│   ├── map.js
│   │   ├── navbar.js
│   │   ├── optimize.js
│   │   └── report.js                 # Image assets
│   └── img/
│       ├── home.jpeg
│       ├── empty_optimization.jpeg
│       ├── optimization.jpeg
│       ├── map.jpeg
│       ├── chat_bot_1.jpeg
│       └── chat_bot_2.jpeg
├── flight_path_ai_project/      # AI and ML scripts
│    └── qaoa_angle_predictor.keras
├── airports_cleaned.json        # Cleaned airport data
├── airports_locations.json      # Airport location data
├── db.sqlite3                   # SQLite database
├── requirements.txt             # Python dependencies
├── .env                         # Project configuration
├── README.md                    # Project documentation
├── .gitignore                   # Git configuration
|── .git/                        # Git repository
│── docker-compose.yml           # Docker Compose file
├── Dockerfile                   # Dockerfile for containerization
└── manage.py                    # Django management script

```

## Setup Instructions

1. **Clone the repository**
   ```cmd/Terminal
   git clone <repo-url>
   cd Flight
   ```
2. **Install dependencies**
   ```cmd/Terminal
   pythom -m venv flight
   flight\scripts\activate.bat
   pip install -r requirements.txt
   ```
3. **Apply migrations**
   ```cmd/Terminal
   python manage.py migrate
   ```
4. **Run the development server**
   ```cmd/Terminal
   python manage.py runserver
   ```

## Usage

- Access the web interface at `http://localhost:8000/`
- Use the chatbot (powered by Gemini AI), flight optimizer, and map visualizations via the provided HTML templates.
- Integrate new airport or flight data by updating the JSON files and running import scripts.

## AI & Optimization

- Train models using scripts in `flight_path_ai_project/`
- Use `qaoa_angle_predictor.keras` for flight angle predictions

## Contributing

Pull requests and issues are welcome! Please follow standard Python and Django best practices.

## License

This project is licensed under the MIT License.

## Contributors

- anushak1815
- mr unknown
- GitHub Copilot (AI Assistant)

## FAQ

**Q: What Python version is required?**
A: Python 3.10 or higher is recommended.

**Q: How do I add new airport data?**
A: Update the JSON files and use the import scripts provided.

**Q: Who maintains the chatbot?**
A: The chatbot is powered by Gemini AI and maintained by the project contributors.

## Technologies Used

- Python 3.10+
- Django
- Keras
- Gemini AI

## API Documentation

The project exposes several REST API endpoints for flight data, optimization, and airport information. See `FILGHT/api_utils.py` and `FILGHT/views.py` for details.

## Contact

For support or questions, open an issue or contact the contributors via GitHub.

## Changelog

- v1.0 Initial release with flight optimization, AI integration, and Supabase support.

## Acknowledgements

- Gemini AI for chatbot functionality
- Django and Keras communities
