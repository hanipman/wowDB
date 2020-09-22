# wowDB

Python script that fills PostgreSQL database with historical price data from World of Warcraft API. Data is then visualized using Java GUI application from my other repository. Currently only tested with Windows.

### Dependencies:
```
python-wowapi
psycopg2
pytest
```

### Setup:
1. Install and start Postgresql server
2. Create a database named as indicated in settings.ini
3. For Windows, use Windows Task Scheduler to implement a periodic task with the desired time interval.

### Stats to track:
- rolling average
- highs
- lows
