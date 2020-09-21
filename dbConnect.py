import psycopg2
from configparser import ConfigParser

'''
Code for config found here:
https://www.postgresqltutorial.com/postgresql-python/connect/
Parses data from .ini file to dictionary

@param filename File to open
@param Section in file to store

@return db Dictionary containing parsed database info
'''
def config(filename = 'settings.ini', section='wowdb'):
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

'''
Class to connect with DB and execute queries specific to wowDB
'''
class dbConnect():

    def __init__(self):
        self.conn = None

    '''
    Connect to database using details within settings.ini
    
    @throws DatabaseError Thrown if connection fails
    @throws Exception Thrown when any other exception is caught
    '''
    def connect(self):
        try:
            params = config()
            self.conn = psycopg2.connect(**params)
        except (Exception, psycopg2.DatabaseError) as e:
            print(e.args)
            raise e

    '''
    Checks if a table of desired realm exists. If the table does
    not exist, creates the table with the name according to the
    realm_slug
    
    @param realm_slug Name of table to look for
    
    @throws DatabaseError Thrown if error in statement
    @throws Exception Thrown when any other exception is caught
    '''
    def __checkTableExists(self, realm_slug):
        try:
            self.realm = realm_slug
            cur = self.conn.cursor()
            if cur.execute(
                '''
                SELECT EXISTS (
                    SELECT *
                    FROM information_schema.tables
                    WHERE
                        table_schema = 'public' AND
                        table_name = '%s'
                )
                ''', realm_slug
            ) == False:
                cur.execute(
                    '''
                    CREATE TABLE '%s' (
                        interval TIMESTAMP NOT NULL,
                        item_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        avg_unit_price INTEGER NOT NULL,
                        high_price INTEGER NOT NULL,
                        low_price INTEGER NOT NULL
                    )
                    ''', realm_slug
                )
        except (Exception, psycopg2.DatabaseError) as e:
            print(e.args)
            raise e
    
    '''
    Adds item to table.

    @param item Item of type dictionary to add to table
    
    @throws DatabaseError Thrown if error in statement
    @throws Exception Thrown when any other exception is caught
    '''
    def addItem(self, item):
        try:
            cur = self.conn.cursor()
            cur.execute(
                '''
                INSERT INTO %s ()
                    current_timestamp,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                ''', (
                        self.realm,
                        item['item_id'],
                        item['quantity'],
                        item['avg_unit_price'],
                        item['high_price'],
                        item['low_price']
                    )
            )
        except (Exception, psycopg2.DatabaseError) as e:
            print(e.args)
            raise e