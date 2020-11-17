#!/usr/bin/env python3.8

from wowDB import *
from dbConnect import *
import pprint as pprint
import time
import logging

import concurrent.futures as concurrent

# I want to filter the results and download names and pics at the same time
# 1. Check if item is in database using checkItemExists
# 2a. If true, skip and append listing to filtered list
# 2b. If false, attempt to download item name and item pic
# 3a. If exception thrown, item is invalid, so skip and do not append
# 3b. If exception is not thrown, item is found, add to database and append to list

wow = None

def reqItemDet(wow, dbcon, item_id):
    '''
    Looks for Item name and picture if it does not already exist in the database

    @param wow Wowapi wrapper object
    @param dbcon postgresql connection wrapper class
    @param item_id ID of item used to download name and picture

    @return item_id id of an invalid item
    @return None nothing returned if item is valid

    @throws Exception Any exception is returned as an invalid id
    '''
    try:
        if not dbcon.checkItemExists(item_id):
            item_name = wow.findItemName(item_id)
            item_pic = wow.findItemPic(item_id)
            dbcon.storeItemDetails(item_id, item_name, item_pic)
    except Exception as e:
        logging.warning('Item name or picture not found for ID %d' % item_id)
        return item_id
    else:
        return None

def filterInvalidListings(wow, dbcon, ids):
    '''
    Creates a thread pool whose threads download item information.

    @param wow Wowapi wrapper object
    @param dbcon postgresql connection wrapper class
    @param ids list of ids to check

    @return result_futures A list of futures
    @return None returned if invalid item
    
    @throws WowApiException handled if item is invalid
    @throws Exception Thrown when any other exception is caught
    '''
    with concurrent.ThreadPoolExecutor(max_workers=100) as executor:
        try:
            result_futures = list(map(lambda x: executor.submit(reqItemDet, wow, dbcon, x), ids))
            return result_futures
        except WowApiException as e:
            logging.warning(str(e))
            return None
        except Exception as e:
            logging.exception(str(e))
            raise e

def addUpdatedListings(dbcon, filtered_list):
    '''
    Creates a threadpool whose threads add items to the database

    @param dbcon postgresql connection wrapper class
    @param filtered_list List of items to be added

    @thrown Exception Thrown when any exception is caught
    '''
    with concurrent.ThreadPoolExecutor(max_workers=100) as executor:
        logging.debug("Adding items to database...")
        try:
            executor.map(dbcon.addItem, filtered_list)
        except Exception as e:
            logging.warning(str(e))
            pass

def main():
    logging.basicConfig(filename='info.log', format='%(asctime)s - %(levelname)'
        's: %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
    start_time = time.time()
    try:
        bnetcred = config('settings.ini', 'bnetcred')
        wow = WowDB(**bnetcred)

        db_params = config('settings.ini', 'wowdb')
        dbcon = dbConnect()
        dbcon.connect(**db_params)
        
        data = wow.findAuctions()
        data = sorted(data, key = lambda i: i['item']['id'])
        
        # Get list of unique IDs
        ids = list()
        [ids.append(x['item']['id']) for x in data if x['item']['id'] not in ids]

        # Remove listings with invalid item IDs
        results = filterInvalidListings(wow, dbcon, ids)
        invalid_ids = [future.result() for future in concurrent.as_completed(results) if future.result()]
        filtered_list = [listing for listing in data if listing['item']['id'] not in invalid_ids]

        # Analyze data
        l = wow.prod_cons_pool(filtered_list)

        # Add analyzed data to database
        dbcon.checkTableExists(wow.realm_slug)
        addUpdatedListings(dbcon, l)
    except Exception as e:
        print(str(e))
        logging.error(str(e) + '\n')
    else:
        logging.info('Execution time %s seconds\n' % (time.time() - start_time))

if __name__ == "__main__":
    main()
