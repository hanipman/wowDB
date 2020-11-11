#!/usr/bin/env python3.8

from wowDB import WowDB
from dbConnect import *
# import pprint as pprint
import time
import logging

def main():
    logging.basicConfig(filename='info.log', format='%(asctime)s - %(levelname)'
        's: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:00')
    start_time = time.time()
    try:
        bnetcred = config('settings.ini', 'bnetcred')
        wow = WowDB(**bnetcred)
        data = wow.findAuctions()
        data = sorted(data, key = lambda i: i['item']['id'])

        # with open('output.txt', 'w') as file1:
        #     pprint.pprint(data, file1)

        l = wow.prod_cons_pool(data)
        
        # with open('sorted.txt', 'w') as file2:
        #     pprint.pprint(l, file2)

        db_params = config('settings.ini', 'wowdb')
        dbcon = dbConnect()
        dbcon.connect(**db_params)
        dbcon.checkTableExists(wow.realm_slug)
        for i in l:
            dbcon.addItem(i)
    except Exception as e:
        print(str(e))
        logging.error(str(e) + '\n')
    else:
        logging.info('Execution time %s seconds\n' % (time.time() - start_time))

if __name__ == "__main__":
    main()
