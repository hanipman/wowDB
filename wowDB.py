
from pprint import pprint
from wowapi import WowApi
import re
import time

class WowDB:
    def __init__(self):
        try:
            file = open('bliz_cred.txt', 'r')
            lines = file.readlines()
            if not lines:
                raise ValueError('No arguments found. File \'bliz_cred.txt\' empty.')
            file.close()

            for line in lines:
                tokens = line.split('=')
                tokens = [x.strip() for x in tokens]
                if (tokens[0] == "locale"):
                    self.locale = tokens[1]
                elif (tokens[0] == "region"):
                    self.region = tokens[1]
                elif (tokens[0] == "realm"):
                    self.realm = tokens[1]
                elif (tokens[0] == "client_id"):
                    self.client_id = tokens[1]
                elif (tokens[0] == "client_secret"):
                    self.client_secret = tokens[1]
            
            if (self.locale == "" or
                self.region == "" or
                self.realm == "" or
                self.client_id == "" or
                self.client_secret == ""):
                raise ValueError("Missing information in file \'bliz_cred.txt\'.")

            self.api = WowApi(self.client_id, self.client_secret)

        except FileNotFoundError as e:
            print(e.args)
        except ValueError as e:
            print(e.args)
        except Exception as e:
            print(e.args)
            
    def getRealmID(self):
        data = self.api.get_realm_index(region=self.region, namespace='dynamic-us', locale=self.locale)
        for x in data['realms']:
            if x['name'] == self.realm:
                self.realm_id = x['id']
                return x['id']
        return -1

    def getRealmSlug(self):
        data = self.api.get_realm_index(region=self.region, namespace='dynamic-us', locale=self.locale)
        for x in data['realms']:
            if x['name'] == self.realm:
                self.realm_slug = x['slug']
                return x['slug']
        return -1

    def getConnectedRealm(self):
        data = None
        try:
            data = self.api.get_realm(region=self.region, namespace='dynamic-us', locale=self.locale, realm_slug=self.realm_slug)
            data = data['connected_realm']['href']
            data = re.search(r'\d+', data).group()
            self.connected_realm_id = int(data)
        except Exception as e:
            print(e.args)
        return int(data)

    def getAuctions(self):
        data = self.api.get_auctions(region=self.region, namespace='dynamic-us', locale=self.locale, connected_realm_id=self.connected_realm_id)
        return data

    def getLocale(self):
        return self.locale
    
    def getRegion(self):
        return self.region

    def getRealm(self):
        return self.realm

    def getClientID(self):
        return self.client_id

    def getClientSecret(self):
        return self.client_secret

def main():
    wow = WowDB()
    wow.getRealmID()
    wow.getRealmSlug()
    wow.getConnectedRealm()
    pprint(wow.getAuctions())

if __name__ == "__main__":
    main()