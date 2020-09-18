
from pprint import pprint
from wowapi import WowApi
from wowapi.exceptions import *
import re
'''
Class WowDB contains server data and client credentials for the
Battle.net API. Contains attributes locale, region, realm,
realm_id, realm_slug, connected_realm_id, client_id, client_secret.
'''
class WowDB:
    '''
    Constructor, initializes main server attributes and stores
    client credentials for Battle.net API.

    @param locale, region, realm Main server details
    @param client_id, client_secret client authentication details

    @throws WowApiOauthException Thrown if client_id or client_secret
        is invalid
    @throws ValueError Thrown if locale, region, realm, client_id,
        or client_secret is empty
    @throws Exception Thrown when any other exception is caught
    '''
    def __init__(self, locale, region, realm, client_id, client_secret):
        if client_id or client_secret:
            try:
                self.api = WowApi(client_id, client_secret)
            except WowApiOauthException as e:
                print(e.args)
                raise e
            except Exception as e:
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
        except WowApiOauthException as e:
            print(e.args)
            raise e
        except Exception as e:
            print(e.args)
            raise e

    '''
    Finds the realm ID of the given realm name. Sets realm_id.

    @throws WowApiException Thrown if query returns 400
    @throws Exception Thrown when any other exception is caught
    '''
    def __findRealmID(self):
        self.realm_id = None
        try:
            data = self.api.get_realm_index(region=self.region, namespace='dynamic-us', locale=self.locale)
            for x in data['realms']:
                if x['name'] == self.realm:
                    self.realm_id = x['id']
        except WowApiException as e:
            print(e.arts)
            raise e
        except Exception as e:
            print(e.args)
            raise e
    
    '''
    Finds the realm slug of the given realm name. Sets realm_slug.

    @throws WowApiException Thrown if query returns 400
    @throws Exception Thrown when any other exception is caught
    '''
    def __findRealmSlug(self):
        self.realm_slug = None
        try:
            data = self.api.get_realm_index(region=self.region, namespace='dynamic-us', locale=self.locale)
            for x in data['realms']:
                if x['name'] == self.realm:
                    self.realm_slug = x['slug']
        except WowApiException as e:
            print(e.args)
            raise e
        except Exception as e:
            print(e.args)
            raise e
    
    '''
    Finds the connected realm id of the given realm slug. If no
    argument is passed, __findRealmSlug() is used to initialize
    attribute realm_slug. Sets connected_realm_id.

    @param realm_slug Initalized to None if no argument passed.

    @throws WowApiException Thrown if query returns 400
    @throws Exception Thrown when any other exception is caught
    '''
    def __findConnectedRealm(self, realm_slug=None):
        self.connected_realm_id = None
        try:
            if realm_slug == None:
                self.__findRealmSlug()
            data = self.api.get_realm(region=self.region, namespace='dynamic-us', locale=self.locale, realm_slug=self.realm_slug)
            data = data['connected_realm']['href']
            data = re.search(r'\d+', data).group()
            self.connected_realm_id = int(data)
        except WowApiException as e:
            print(e.args)
            raise e
        except Exception as e:
            print(e.args)
            raise e

    '''
    Finds the auction listings of the given connected realm. If
    no argument is passed, __findConnectedRealm is used to
    initialize connected_realm_id.

    @param connected_realm_id Initialized to None if no argument
        passed

    @return data Details of auction house listings to be evaluated

    @throws WowApiException Thrown if query returns 400
    @throws Exception Thrown when any other exception is caught
    '''
    def findAuctions(self, connected_realm_id=None):
        data = None
        try:
            if connected_realm_id == None:
                self.__findConnectedRealm()
            data = self.api.get_auctions(region=self.region, namespace='dynamic-us', locale=self.locale, connected_realm_id=self.connected_realm_id)
            data = data['auctions']
            return data
        except WowApiException as e:
            print(e.args)
            raise e
        except Exception as e:
            print(e.args)
            raise e
    
    '''
    Parses relevant data from auction house listing data and calculates
    the average, high, and low price for each item. The list is sorted
    by item_id.
    
    @param data Auction house listing data

    @return item json format:
    {
        'item_id': int,
        'quantity': int,
        'avg_unit_price': int,
        'high_price': int,
        'low_price': int
        'num': int
    }
    '''
    def sortListings(self, data):
        sorted_list = list()
        for listing in data:
            # check if listing already exists in sorted_list
            res = next((sub for sub in sorted_list if sub['item_id'] == listing['item']['id']), None)
            
            # check if a unit price or buyout price exists
            # ignore bid only listings
            if 'unit_price' in listing.keys():
                price = listing['unit_price']
            elif 'buyout' in listing.keys():
                price = listing['buyout']
            else:
                price = -1

            if price >= 0:
                # if item not in sorted_list, append new dict
                if res is None:
                    item = {
                        'item_id': listing['item']['id'],
                        'quantity': listing['quantity'],
                        'avg_unit_price': price,
                        'high_price': price,
                        'low_price': price,
                        'num': 1
                    }
                    sorted_list.append(item)
                # if item is in sorted_list, update statistics
                else:
                    res['quantity'] = res['quantity'] + listing['quantity']
                    res['avg_unit_price'] = ((res['avg_unit_price'] * res['num']) + price)/(res['num'] + 1)
                    if res['high_price'] < price:
                        res['high_price'] = price
                    if res['low_price'] > price:
                        res['low_price'] = price
                    res['num'] = res['num'] + 1
        sorted_list = sorted(sorted_list, key = lambda i: i['item_id'])
        return sorted_list

    '''
    Gets attribute locale.

    @return locale
    '''
    def getLocale(self):
        return self.locale
    
    '''
    Gets attribute region.

    @return region
    '''
    def getRegion(self):
        return self.region

    '''
    Gets attribute realm.

    @return realm
    '''
    def getRealm(self):
        return self.realm

    '''
    Gets attribute realm ID.

    @return realm_id
    '''
    def getRealmID(self):
        return self.realm_id

    '''
    Gets attribute realm slug.

    @return realm_slug
    '''
    def getRealmSlug(self):
        return self.realm_slug

    '''
    Gets attribute connected realm ID

    @return connected_realm_id
    '''
    def getConnectedRealmID(self):
        return self.connected_realm_id

def main():
    wow = WowDB(locale='en_US',region='us',realm='Area 52',
        client_id='4a85a96821f44ed483c41628ebf656f1',
        client_secret='KHATRWXtHV2pIxK5jBbjV6tSyI87oycN')
    data = wow.findAuctions()
    sorted_list = wow.sortListings(data)
    with open('output.txt', 'w') as file:
        pprint(data, file)
    with open('sorted.txt', 'w') as file2:
        pprint(sorted_list, file2)

if __name__ == "__main__":
    main()