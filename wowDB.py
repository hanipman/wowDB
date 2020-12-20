from wowapi import WowApi
from wowapi.exceptions import *
import copy
import math
from multiprocessing import Event, Manager, Pool, Process, Queue
import queue as queue
import re
from welford import Welford
import urllib.request
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

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
                logging.exception(str(e))
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
            logging.exception(str(e))
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
            logging.exception(str(e))
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
            logging.exception(str(e))
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
            logging.exception(str(e))
            raise e

    def findItemName(self, item_id):
        '''
        Finds the item name of the given item id. If an exception is thrown, the
        item is not in the WoW database.

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
            logging.exception(str(e))
            raise e
    
    def findItemPic(self, item_id):
        '''
        Finds the item picture as a byte array of the given item id. If an
        exception is thrown, the item is not in the WoW database.

        @param item_id ID of item

        @return byte array

        @throws WowApiException Thrown if query returns 404
        @throws Exception       Thrown when any other exception is caught
        '''
        data = None
        try:
            data = self.api.get_item_media(region=self.region, id=item_id, namespace='static-us', locale=self.locale)
            url = data['assets'][0]['value']
            res = urllib.request.urlopen(url)
            return res.read()
        except (Exception, WowApiException) as e:
            logging.exception(str(e))
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
            logging.exception(str(e))
            raise e

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