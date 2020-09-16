
from pprint import pprint
from wowapi import WowApi
from wowapi.exceptions import *
import re

class WowDB:
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

    def findAuctions(self, connected_realm_id=None):
        data = None
        try:
            if connected_realm_id == None:
                self.__findConnectedRealm()
            data = self.api.get_auctions(region=self.region, namespace='dynamic-us', locale=self.locale, connected_realm_id=self.connected_realm_id)
            return data
        except WowApiException as e:
            print(e.args)
            raise e
        except Exception as e:
            print(e.args)
            raise e
    
    def getLocale(self):
        return self.locale
    
    def getRegion(self):
        return self.region

    def getRealm(self):
        return self.realm

    def getRealmID(self):
        return self.realm_id

    def getRealmSlug(self):
        return self.realm_slug

    def getConnectedRealmID(self):
        return self.connected_realm_id

def main():
    wow = WowDB()
    wow.getRealmID()
    wow.getRealmSlug()
    wow.getConnectedRealm()
    pprint(wow.getAuctions())

if __name__ == "__main__":
    main()