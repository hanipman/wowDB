#!/usr/bin/env python3.9

from wowDB import *
from dbConnect import *
from notification import notify
import pprint as pprint
import time
import logging
import schedule

import concurrent.futures as concurrent

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

def findPrice(listing):
    '''
    Finds the unit price of the listing.

    @param listing Listing of an item
    
    @return unit_price of item
    @return None returned if listing does not contain valid price
    '''
    if 'unit_price' in listing:
        return listing['unit_price']
    elif 'buyout' in listing:
        return listing['buyout']/listing['quantity']
    return

def job():
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

        # Get list of ids that do not already exist in item_list table
        check_list = dbcon.getIDDiff(ids)

        # Remove listings with invalid item IDs
        results = filterInvalidListings(wow, dbcon, check_list)
        invalid_ids = [future.result() for future in concurrent.as_completed(results) if future.result()]
        filtered_list = [listing for listing in data if listing['item']['id'] not in invalid_ids]

        formatted_list = list()
        [formatted_list.append({'item_id': x['item']['id'], 'price': findPrice(x), 'quantity': x['quantity']}) for x in filtered_list if ('unit_price' in x or 'buyout' in x)]
        dbcon.checkTableExists(wow.realm_slug)
        dbcon.clearSnapshot()
        dbcon.storeSnapshot(formatted_list)

        # Add analyzed data to database
        dbcon.insertNewListings()
        logging.info('Filtered list length: %d', len(formatted_list))
    except Exception as e:
        # print(str(e))
        notify(str(e))
        logging.error(str(e) + '\n')
    else:
        logging.info('Execution time %s seconds\n' % (time.time() - start_time))

def main():
    schedule.every().hour.do(job).at(':00')
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()