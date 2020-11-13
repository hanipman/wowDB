from wowapi import WowApi
from wowapi.exceptions import *
import copy
import math
from multiprocessing import Event, Manager, Pool, Process, Queue
import queue as queue
import re
from welford import Welford
import urllib.request

class WowDB:
    '''
    Class WowDB contains server data and client credentials for the
    Battle.net API. Contains attributes locale, region, realm,
    realm_id, realm_slug, connected_realm_id, client_id, client_secret.
    '''
    def __init__(self, locale, region, realm, client_id, client_secret):
        '''
        Constructor, initializes main server attributes and stores
        client credentials for Battle.net API.

        @param locale, region, realm Main server details
        @param client_id, client_secret client authentication details

        @throws WowApiOauthException    Thrown if client_id or client_secret is
                                        invalid
        @throws ValueError              Thrown if locale, region, realm,
                                        client_id, or client_secret is empty
        @throws Exception               Thrown when any other exception is
                                        caught
        '''
        if client_id or client_secret:
            try:
                self.api = WowApi(client_id, client_secret)
            except (Exception, WowApiOauthException) as e:
                print(e.args)
                raise e
        else:
            raise ValueError('client_id or client_secret empty.')
        if locale:
            self.locale = locale
        else:
            raise ValueError('locale invalid')
        if region:
            self.region = region
        else:
            raise ValueError('region invalid')
        if realm:
            self.realm = realm
        else:
            raise ValueError('locale, region, and/or realm empty.')
        try:
            self.__findConnectedRealm()
        except (Exception, WowApiOauthException) as e:
            print(e.args)
            raise e

    def __findRealmID(self):
        '''
        Finds the realm ID of the given realm name. Sets realm_id.

        @throws WowApiException Thrown if query returns 400
        @throws Exception       Thrown when any other exception is caught
        '''
        self.realm_id = None
        try:
            data = self.api.get_realm_index(region=self.region, namespace='dynamic-us', locale=self.locale)
            for x in data['realms']:
                if x['name'] == self.realm:
                    self.realm_id = x['id']
        except (Exception, WowApiException) as e:
            print(e.arts)
            raise e
    
    def __findRealmSlug(self):
        '''
        Finds the realm slug of the given realm name. Sets realm_slug.

        @throws WowApiException Thrown if query returns 400
        @throws Exception       Thrown when any other exception is caught
        '''
        self.realm_slug = None
        try:
            data = self.api.get_realm_index(region=self.region, namespace='dynamic-us', locale=self.locale)
            for x in data['realms']:
                if x['name'] == self.realm:
                    self.realm_slug = x['slug']
        except (Exception, WowApiException) as e:
            print(e.args)
            raise e

    def __findConnectedRealm(self, realm_slug=None):
        '''
        Finds the connected realm id of the given realm slug. If no
        argument is passed, __findRealmSlug() is used to initialize
        attribute realm_slug. Sets connected_realm_id.

        @param  realm_slug       Initalized to None if no argument passed.

        @throws WowApiException Thrown if query returns 400
        @throws Exception       Thrown when any other exception is caught
        '''
        self.connected_realm_id = None
        try:
            if realm_slug == None:
                self.__findRealmSlug()
            data = self.api.get_realm(region=self.region, namespace='dynamic-us', locale=self.locale, realm_slug=self.realm_slug)
            data = data['connected_realm']['href']
            data = re.search(r'\d+', data).group()
            self.connected_realm_id = int(data)
        except (Exception, WowApiException) as e:
            print(e.args)
            raise e

    def findItemName(self, item_id):
        '''
        Finds the item name of the given item id.

        @param item_id ID of item
        
        @return item name

        @throws WowApiException Thrown if query returns 400
        @throws Exception       Thrown when any other exception is caught
        '''
        data = None
        try:
            data = self.api.get_item_data(region=self.region, id=item_id, namespace='static-us', locale=self.locale)
            return data['name']
        except (Exception, WowApiException) as e:
            print(e.args)
            raise e
    
    def findItemPic(self, item_id):
        '''
        Finds the item picture as a byte array of the given item id

        @param item_id ID of item

        @return byte array

        @throws WowApiException Thrown if query returns 400
        @throws Exception       Thrown when any other exception is caught
        '''
        data = None
        try:
            data = self.api.get_item_media(region=self.region, id=item_id, namespace='static-us', locale=self.locale)
            url = data['assets'][0]['value']
            res = urllib.request.urlopen(url)
            return res.read()
        except (Exception, WowApiException) as e:
            print(e.args)
            raise e

    def findAuctions(self, connected_realm_id=None):
        '''
        Finds the auction listings of the given connected realm. If
        no argument is passed, __findConnectedRealm is used to
        initialize connected_realm_id.

        @param  connected_realm_id  Initialized to None if no argument passed

        @return data                Details of auction house listings to be
                                    evaluated

        @throws WowApiException     Thrown if query returns 400
        @throws Exception           Thrown when any other exception is caught
        '''
        data = None
        try:
            if connected_realm_id == None:
                self.__findConnectedRealm()
            data = self.api.get_auctions(region=self.region, namespace='dynamic-us', locale=self.locale, connected_realm_id=self.connected_realm_id)
            data = data['auctions']
            return data
        except (Exception, WowApiException) as e:
            print(e.args)
            raise e

    def sortListings(self, data):
        '''
        Parses relevant data from auction house listing data and calculates
        the average, standard deviation, high, and low price for each item.
        The list is sorted by item_id.
        
        @param data Auction house listing data

        @return sorted_list List of items using json format:
        {
            'item_id': int,
            'quantity': int,
            'avg_unit_price': int,
            'std_dev': int,
            'high_price': int,
            'low_price': int
            'num': int
        }
        '''
        sorted_list = list()
        price_list = list()
        prev_id = 0
        data = sorted(data, key = lambda i: i['item']['id'])
        item_dict = {
            'item_id': 0,
            'quantity': 0,
            'avg_unit_price': 0,
            'std_dev': 0,
            'high_price': 0,
            'low_price': 0,
            'num': 0
        }
        item = None
        foo = None
        for listing in data:
            price = 0
            # update price if listing is by unit or buyout. Ignore bids
            if 'unit_price' in listing.keys():
                price = listing['unit_price']
                sub_quantity = listing['quantity']
                sub_list = [price] * sub_quantity
            elif 'buyout' in listing.keys():
                price = listing['buyout']
                sub_quantity = listing['quantity']
                sub_list = [price/sub_quantity] * sub_quantity
            else:
                price = -1

            if price >= 0:
                # if listing is the same item as previous listing
                # update item dict
                if listing['item']['id'] == prev_id:
                    item['quantity'] = item['quantity'] + listing['quantity']
                    item['num'] = item['num'] + 1
                    if item['high_price'] < price:
                        item['high_price'] = price
                    if item['low_price'] > price:
                        item['low_price'] = price
                    price_list += sub_list
                # if listing is a different item, add previous item 
                # to list and setup new item
                else:
                    # init case
                    if prev_id != 0:
                        try:
                            foo = Welford()
                            foo(price_list)
                            foo
                            item['std_dev'] = math.floor(foo.std)
                        except ValueError as e:
                            item['std_dev'] = 0
                        item['avg_unit_price'] = math.floor(foo.mean)
                        sorted_list.append(item)
                    item = dict(item_dict)
                    item['item_id'] = listing['item']['id']
                    item['quantity'] = listing['quantity']
                    item['high_price'] = price
                    item['low_price'] = price
                    item['num'] = 1
                    price_list.append(price)
            # update previous listing id
            prev_id = listing['item']['id']
        return sorted_list

    def create_price_list(self, data, q, event):
        '''
        Parses prices from data and appends to a list. The relevant item id,
        quantity, and price list are all added to the passed queue as a tuple.
        Following a multiprocessing producer consumer design, this function
        acts as the producer. An event is set when all listings are processed.
        If push to queue fails, will attempt to push again.

        @params data        Auction house listing data
        @params q           Queue for which item data should be pushed to
        @params event       Event to be set when all listings in data are
                            processed

        @throws queue.Full  Thrown if queue is full
        '''
        price_list = list()
        prev_id = 0
        quantity = 0
        for listing in data:
            price = 0
            if 'unit_price' in listing.keys():
                price = listing['unit_price']
                sub_quantity = listing['quantity']
                sub_list = [price] * sub_quantity
            elif 'buyout' in listing.keys():
                price = listing['buyout']
                sub_quantity = listing['quantity']
                sub_list = [price/sub_quantity] * sub_quantity
            else:
                price = -1
            if price >= 0:
                if listing['item']['id'] == prev_id:
                    price_list += sub_list
                    quantity += listing['quantity']
                else:
                    for attempt in range(10):
                        try:
                            if prev_id != 0:
                                q.put((copy.copy(prev_id), copy.copy(quantity), copy.copy(price_list)))
                        except queue.Full:
                            if attempt == 9:
                                raise queue.Full
                            continue
                        else:
                            prev_id = listing['item']['id']
                            price_list.clear()
                            price_list = sub_list
                            quantity = listing['quantity']
                            break
        event.set()

    def analyze_data(self, q):
        '''
        Calculates the average price and standard deviation of an item.
        Following a multiprocessing producer consumer design, this function
        acts as the consumer, popping items from the queue and calculating.

        @params q                                   Queue from which data is
                                                    popped
        
        @throws queue.Empty                         Thrown if queue is empty

        @return (item[0], item[1], foo.meanfull)    Tuple containing processed
                                                    item data
        '''
        try:
            item = q.get_nowait()
            foo = Welford()
            foo(item[2])
            item_dict = {
                'item_id': item[0],
                'quantity': item[1],
                'avg_unit_price': foo.mean,
                'std_dev': foo.std,
                'high_price': max(item[2]),
                'low_price': min(item[2]),
            }
            return item_dict
        except queue.Empty:
            pass

    def prod_cons_pool(self, data):
        '''
        Creates the producer and consumer pool to asynchronously
        process data

        @params data    data to be processed

        @return l       list of processed data
        '''
        manager = Manager()
        q = manager.Queue()
        l = list()
        event = manager.Event()
        p = Process(target=self.create_price_list, args=(data, q, event,))
        p.start()
        with Pool(processes=4) as pool:
            while True:
                if q.qsize() > 0:
                    res = pool.apply_async(self.analyze_data, (q,))
                    l.append(res.get())
                else:
                    break
        p.join()
        return l

    def storeItemPics(self, item):
        '''
        Checks if item picture is already stored in database. If not, download
        the picture and store.
        '''
        return True

    @property
    def locale(self):
        '''
        Gets property locale.

        @return locale
        '''
        return self._locale
    
    @locale.setter
    def locale(self, value):
        '''
        Sets property locale.
        '''
        self._locale = value

    @property
    def region(self):
        '''
        Gets property region.

        @return region
        '''
        return self._region

    @region.setter
    def region(self, value):
        '''
        Sets property region.
        '''
        self._region = value

    @property
    def realm(self):
        '''
        Gets property realm.

        @return realm
        '''
        return self._realm

    @realm.setter
    def realm(self, value):
        '''
        Sets property realm.
        '''
        self._realm = value

    @property
    def realm_id(self):
        '''
        Gets property realm ID.

        @return realm_id
        '''
        return self._realm_id

    @realm_id.setter
    def realm_id(self, value):
        '''
        Sets property realm ID
        '''
        self._realm_id = value

    @property
    def realm_slug(self):
        '''
        Gets property realm slug.

        @return realm_slug
        '''
        return self._realm_slug

    @realm_slug.setter
    def realm_slug(self, value):
        '''
        Sets property realm slug
        '''
        self._realm_slug = value

    @property
    def connected_realm_id(self):
        '''
        Gets property connected realm ID

        @return connected_realm_id
        '''
        return self._connected_realm_id

    @connected_realm_id.setter
    def connected_realm_id(self, value):
        '''
        Sets property connected realm ID
        '''
        self._connected_realm_id = value