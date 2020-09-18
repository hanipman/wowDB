import pytest
from wowDB import WowDB
from wowapi.exceptions import *

locale = 'en_US'
region = 'us'
realm = 'Area 52'
client_id = '4a85a96821f44ed483c41628ebf656f1'
client_secret = 'KHATRWXtHV2pIxK5jBbjV6tSyI87oycN'

class TestwowDB():

    def test_init(self):
        '''Test init constructor with existing inputs'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        assert wow.getLocale() == locale
        assert wow.getRegion() == region
        assert wow.getRealm() == realm
        assert wow.getRealmSlug() == 'area-52'
        assert wow.getConnectedRealmID() == 3676
    
    @pytest.mark.parametrize(
        "locale,region,realm,client_id,client_secret,expected", 
        [
            (locale,region,realm,'',client_secret,pytest.raises(WowApiOauthException)),
            (locale,region,realm,client_id,'',pytest.raises(WowApiOauthException)),
            ('',region,realm,client_id,client_secret,pytest.raises(ValueError)),
            (locale,'',realm,client_id,client_secret,pytest.raises(ValueError)),
            (locale,region,'',client_id,client_secret,pytest.raises(ValueError))
        ])
    def test_init_missing_server_info_client_cred(self, locale, region, realm, client_id, client_secret, expected):
        '''Test init constructor for missing locale, region or realm.'''
        with expected:
            assert WowDB(locale, region, realm, client_id, client_secret) is not None

    @pytest.mark.parametrize(
        "locale,region,realm,client_id,client_secret,expected", 
        [
            (locale,region,realm,'blah',client_secret,pytest.raises(WowApiOauthException)),
            (locale,region,realm,client_id,'blah',pytest.raises(WowApiOauthException)),
            ('blah',region,realm,client_id,client_secret,pytest.raises(WowApiException)),
            (locale,'blah',realm,client_id,client_secret,pytest.raises(WowApiException)),
            (locale,region,'blah',client_id,client_secret,pytest.raises(WowApiException))
        ])
    def test_init_bad_server_info_client_cred(self, locale, region, realm, client_id, client_secret, expected):
        '''Test init constructor for missing locale, region or realm.'''
        with expected:
            assert WowDB(locale, region, realm, client_id, client_secret) is not None

    def test_findAuctions(self):
        '''Test getting auction house results'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        data = wow.findAuctions()
        assert 'id' in data[0].keys()

    def test_sortListings(self):
        '''Test sorting auction house results'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        data = wow.findAuctions()
        sorted_list = wow.sortListings(data)
        assert all (k in sorted_list[0] for k in (
            'item_id',
            'quantity',
            'avg_unit_price',
            'high_price',
            'low_price',
            'num'
        ))
        for i in range(5):
            assert sorted_list[i]['item_id'] < sorted_list[i+1]['item_id']
        