
from pprint import pprint

from wowapi import WowApi

class WowDB:
    def __init__(self, locale, region, realm, client_id, client_secret):
        self.locale = locale
        self.region = region
        self.realm = realm
        # self.client_id = client_id
        # self.client_secret = client_secret
        api = WowApi(client_id, client_secret)

    def getRealmID(self):
        data = api.get_realm_index(region=region, namespace='dynamic-us', locale=locale)
        for x in data['realms']:
            if x['name'] == self.realm:
                return x['id']
        return -1

    def getRealmSlug(realm):
        data = api.get_realm_index(region=region, namespace='dynamic-us', locale=locale)
        return data

    def getAuctions(realm_id):
        data = api.get_auctions(region=region, namespace='dynamic-us', locale=locale, connected_realm_id=realm_id)
        return data

def main():
    wow = WowDB(locale=locale, region=region, realm=realm, 
                client_id=WOW_CLIENT_ID, client_secret=WOW_CLIENT_SECRET)

if __name__ == "__main__":
    main()