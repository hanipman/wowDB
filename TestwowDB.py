import pytest
from wowDB import WowDB

class TestwowDB():

    def test_init(self):
        wow = WowDB()
        assert wow.getLocale() == 'en_US'
        assert wow.getRegion() == 'us'
        assert wow.getRealm() == 'Area 52'

    def test_getRealmID(self):
        wow = WowDB()
        data = wow.getRealmID()
        assert data == 1566

    def test_getRealmSlug(self):
        wow = WowDB()
        data = wow.getRealmSlug()
        assert data == 'area-52'

    def test_getConnectedRealm(self):
        wow = WowDB()
        wow.getRealmSlug()
        data = wow.getConnectedRealm()
        assert data == 3676

    def test_getAuctions(self):
        wow = WowDB()
        wow.getRealmID()
        wow.getRealmSlug()
        wow.getConnectedRealm()
        data = wow.getAuctions()
        assert 'auctions' in data
        

    # def test_getAuctions(self):
    #     wow = WowDB()
    #     data = wow.getAuction