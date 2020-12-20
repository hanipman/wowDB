# wowDB

Python script that fills PostgreSQL database with historical price data from World of Warcraft API. Data is then visualized using Java GUI application from my other repository. Currently only tested with Windows and Linux.

v1.0:
wowDB implements a multiprocessing producer consumer design pattern, but a sequential method is included in the class.
The producer parses auction listings downloaded from the api and pushes a tuple consisting of the item ID, quantity, and price list. A pool of workers asynchronously consumes from the queue and calculates the desired statistics. Upon returning, the result is added to a list to be added to the database.

v2.0:
To avoid the GUI client from having to download item names and pictures, the item IDs are checked against a separate table containing previously downloaded item details. If the item does not exist in the table the item details are downloaded and inserted.
Now applies multithreaded functionality. Instead of a single database connection, a connection pool is created from which dbConnect functions can obtain a connection. HTTP requests are also implemented using concurrency.

v3.0:
Moved all calculations to be done by the database. This removed the use of multiprocessing and cut down the execution time from ~10 minutes to ~35 seconds. Table creation now allows a default timestamp floored to the hour on insert of new records. Analysis is done using Postgres inbuilt functions SUM(), AVG(), STDDEV_POP(), LOW(), HIGH().

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
   For Linux, use crontab by running the command 'crontab -e' in terminal

### Stats being tracked:
- average
- standard deviation
- highs
- lows

### Possible Goals:
- record more statistical calculations
- maybe apply machine learning algorithms (weighted averages, anomaly detection)
