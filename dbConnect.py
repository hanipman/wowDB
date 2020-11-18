import psycopg2
from psycopg2 import pool,sql
from configparser import ConfigParser
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def config(filename = 'settings.ini', section='wowdb'):
    '''
    Code for config found here:
    https://www.postgresqltutorial.com/postgresql-python/connect/
    Parses data from .ini file to dictionary

    @param filename File to open
    @param Section in file to store

    @return db Dictionary containing parsed database info

    @throws Exception thrown if specific section is not found in config file
    '''
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        msg = 'Section {0} not found in the {1} file'.format(section, filename)
        logging.exception(msg)
        raise Exception(msg)
    return db

class dbConnect():
    '''
    Class to connect with DB and execute queries specific to wowDB
    '''
    def __init__(self):
        self.conn_pool = None

    def __del__(self):
        self.conn_pool.closeall()

    def connect(self, host, database, port, user, password):
        '''
        Connect to database using details within settings.ini
        
        @throws Error Thrown if connection fails
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            self.conn_pool = psycopg2.pool.ThreadedConnectionPool(5,100,host=host,database=database,user=user,password=password,port=port)
            logging.debug("Connected to database {0} at {1} port {2}".format(database, host, port))
        except (Exception, psycopg2.Error) as e:
            logging.exception(str(e))
            raise e

    def checkTableExists(self, realm_slug):
        '''
        Checks if a table of desired realm exists. If the table does
        not exist, creates the table with the name according to the
        realm_slug. Also creates table item_list if it does not exist.
        
        @param realm_slug Name of table to look for
        
        @throws Error Thrown if error any of the database calls
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            self.realm = realm_slug.replace('-','_')
            local_conn = self.conn_pool.getconn()
            if local_conn:
                cur = local_conn.cursor()
                cur.execute(sql.SQL(
                    """
                    CREATE TABLE IF NOT EXISTS {} (
                        interval TIMESTAMP NOT NULL,
                        item_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        avg_unit_price BIGINT NOT NULL,
                        std_dev BIGINT NOT NULL,
                        high_price BIGINT NOT NULL,
                        low_price BIGINT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS item_list (
                        item_id INTEGER NOT NULL,
                        item_name TEXT NOT NULL,
                        item_pic BYTEA NOT NULL
                    )
                    """).format(sql.Identifier(self.realm)),[]
                )
                local_conn.commit()
                cur.close()
                self.conn_pool.putconn(local_conn)
                logging.debug("Created table %s and table item_list" % self.realm)
        except (Exception, psycopg2.Error) as e:
            logging.exception(str(e))
            raise e
    
    def addItem(self, item):
        '''
        Adds analyzed item to realm table.

        @param item Item of type dictionary to add to table
        
        @throws Error Thrown if error in any of the database calls
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            local_conn = self.conn_pool.getconn()
            if local_conn:
                cur = local_conn.cursor()
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
                                %s
                        )
                    """).format(sql.Identifier(self.realm)), [
                        item['item_id'],
                        item['quantity'],
                        item['avg_unit_price'],
                        item['std_dev'],
                        item['high_price'],
                        item['low_price']
                    ]
                )
                local_conn.commit()
                cur.close()
                self.conn_pool.putconn(local_conn)
        except (Exception, psycopg2.Error) as e:
            logging.exception(str(e))
            raise e

    def checkItemExists(self, item_id):
        '''
        Checks if the item already exists in the table item_list.

        @param item_id ID of item to be checked

        @return true/false

        @throws Error Thrown if error in any database calls
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            local_conn = self.conn_pool.getconn()
            if local_conn:
                cur = local_conn.cursor()
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT *
                        FROM item_list
                        WHERE item_id = %s
                    )
                    """,
                    (item_id,)
                )
                res = cur.fetchone()[0]
                cur.close()
                self.conn_pool.putconn(local_conn)
                return res
        except (Exception, psycopg2.Error) as e:
            logging.exception(str(e))
            raise e

    def storeItemDetails(self, item_id, item_name, item_pic):
        '''
        Stores item details into table item_list.

        @param item_id ID of the item
        @param item_name name of the item
        @param item_pic byte array of the item pic

        @throws Error Thrown if error in any database calls
        @throws Exception Thrown when any other exception is caught
        '''
        try:
            local_conn = self.conn_pool.getconn()
            if local_conn:
                cur = local_conn.cursor()
                cur.execute(
                    """
                    INSERT INTO item_list
                        (item_id, item_name, item_pic)
                    SELECT %s, %s, %s
                    WHERE
                        NOT EXISTS (
                            SELECT item_id
                            FROM item_list
                            WHERE item_id = %s
                        )
                    """,
                    (item_id, item_name, item_pic, item_id)
                )
                local_conn.commit()
                cur.close()
                self.conn_pool.putconn(local_conn)
                logging.debug("Storing item %s name and picture in table item_list" % item_id)
        except (Exception, psycopg2.Error) as e:
            logging.exception(str(e))
            raise e