# wowDB

Python script that fills PostgreSQL database with historical price data from World of Warcraft API. Data is then visualized using Java GUI application from my other repository. Currently only tested with Windows.

wowDB implements a multiprocessing producer consumer design pattern, but a sequential method is included in the class.
The producer parses auction listings downloaded from the api and pushes a tuple consisting of the item ID, quantity, and price list. A pool of workers asynchronously consumes from the queue and calculates the desired statistics. Upon returning, the result is added to a list to be added to the database.

### Dependencies:
```
python-wowapi
psycopg2
pytest
```

### Setup:
1. Install and start Postgresql server
2. Modify settings.ini
3. For Windows, use Windows Task Scheduler to implement a periodic task with the desired time interval.

### Stats to track:
- average
- standard deviation
- highs
- lows

### Possible Goals:
- record more statistical calculations
- maybe apply machine learning algorithms (weighted averages, anomaly detection)