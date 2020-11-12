import psycopg2
from psycopg2 import sql
from configparser import ConfigParser

def config(filename = 'settings.ini', section='wowdb'):
    '''
    Code for config found here:
    https://www.postgresqltutorial.com/postgresql-python/connect/
    Parses data from .ini file to dictionary

    @param filename File to open
    @param Section in file to store

    @return db Dictionary containing parsed database info
    '''
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

class dbConnect():
    '''
    Class to connect with DB and execute queries specific to wowDB
    '''
    def __init__(self):
        self.conn = None

    def __del__(self):
        self.conn.close()

    def connect(self, host, database, user, password):
        '''
        Connect to database using details within settings.ini
        
        @throws DatabaseError Thrown if connection fails
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            self.conn = psycopg2.connect(host=host, dbname=database, user=user, password=password)
        except (Exception, psycopg2.DatabaseError) as e:
            print(e.args)
            raise e

    def checkTableExists(self, realm_slug):
        '''
        Checks if a table of desired realm exists. If the table does
        not exist, creates the table with the name according to the
        realm_slug. Also creates table item_list if it does not exist.
        
        @param realm_slug Name of table to look for
        
        @throws DatabaseError Thrown if error in statement
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            self.realm = realm_slug.replace('-','_')
            cur = self.conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS %s (
                    interval TIMESTAMP NOT NULL,
                    item_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    avg_unit_price BIGINT NOT NULL,
                    std_dev BIGINT NOT NULL,
                    high_price BIGINT NOT NULL,
                    low_price BIGINT NOT NULL
                )
                CREATE TABLE IF NOT EXISTS item_list (
                    item_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    item_pic BYTEA NOT NULL
                )
                """ % self.realm
            )
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as e:
            print(e.args)
            raise e
    
    def addItem(self, item):
        '''
        Adds analyzed item to realm table.

        @param item Item of type dictionary to add to table
        
        @throws DatabaseError Thrown if error in statement
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            cur = self.conn.cursor()
            cur.execute(sql.SQL(
                """
                INSERT INTO {} (interval,
                                item_id,
                                quantity,
                                avg_unit_price,
                                std_dev,
                                high_price,
                                low_price)
                    VALUES (current_timestamp,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s)
                """).format(sql.Identifier(self.realm)), [
                        item['item_id'],
                        item['quantity'],
                        item['avg_unit_price'],
                        item['std_dev'],
                        item['high_price'],
                        item['low_price']
                    ]
            )
            self.conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as e:
            print(e.args)
            raise e