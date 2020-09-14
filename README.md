# wowDB

Python script that fills PostgreSQL database with historical price data from World of Warcraft API. Data is then visualized using Java GUI application from my other repository.

### Dependencies:
```
python-wowapi
pytest
psycopg2
```

### TODO:
- Refine class methods and tests for more conclusive testing
- Initialize and connect to PostgreSQL database
- Determine schema for storing data
- Parse relevant data from auction house API
- Store data in 30 minute intervals

### Stats to track:
- rolling average
- market value
- highs
- lows
