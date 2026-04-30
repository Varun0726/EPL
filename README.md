# EPL FBref Scraper

A Python-based Premier League scraping project built with SeleniumBase, BeautifulSoup, and pandas.  
This project scrapes team-level FBref data and exports match, shooting, goalkeeping, and miscellaneous tables into CSV files for analysis and dashboard work.

## Features

- Scrapes Premier League team pages from FBref
- Uses an OOP project structure for cleaner, reusable code
- Extracts:
  - Scores & Fixtures
  - Shooting
  - Goalkeeping
  - Miscellaneous
- Saves individual team CSV files
- Creates combined league-wide CSV outputs
- Uses logging and safer error handling for debugging

## Tech stack

- Python
- SeleniumBase
- BeautifulSoup4
- pandas
- lxml
- html5lib

## Project structure

```text
epl-fbref-scraper/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── epl_scraper/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── parser.py
│   ├── scraper.py
│   └── utils.py
└── data/
