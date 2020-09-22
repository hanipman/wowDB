# wowDB

Python script that fills PostgreSQL database with historical price data from World of Warcraft API. Data is then visualized using Java GUI application from my other repository. Script will be setup as a daemon, current compatibility through Windows planned.

### Dependencies:
```
python-wowapi
psycopg2
pytest
```

### TODO:
- Store data in 30 minute intervals using daemon.

### Stats to track:
- rolling average
- highs
- lows
