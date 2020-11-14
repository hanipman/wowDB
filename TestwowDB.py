import pytest
from wowDB import WowDB
from wowapi.exceptions import *
from dbConnect import config
from PIL import Image, ImageChops
import io

locale = 'en_US'
region = 'us'
realm = 'Arathor'
bnetcred = config('settings.ini', 'bnetcred')
client_id = bnetcred['client_id']
client_secret = bnetcred['client_secret']

class TestwowDB():

    bnetcred = config('settings.ini', 'bnetcred')
    client_id = bnetcred['client_id']
    client_secret = bnetcred['client_secret']

    def test_init(self):
        '''Test init constructor with existing inputs'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        assert wow.locale == locale
        assert wow.region == region
        assert wow.realm == realm
        assert wow.realm_slug == 'arathor'
        assert wow.connected_realm_id == 1138
    
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

    def test_findItemName(self):
        wow = WowDB(locale, region, realm, client_id, client_secret)
        item_name = wow.findItemName(19019)
        assert item_name == 'Thunderfury, Blessed Blade of the Windseeker'

    @pytest.mark.parametrize(
        "item_id,expected",
        [
            (10000000,pytest.raises(WowApiException)),
            ('blah',pytest.raises(WowApiException))
        ])
    def test_bad_findItemName(self, item_id, expected):
        '''Test getting the item name corresponding to a given item ID'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        with expected:
            assert wow.findItemName(item_id) is not None

    def test_findItemPic(self):
        wow = WowDB(locale, region, realm, client_id, client_secret)
        ba = wow.findItemPic(19019)
        # with open('picture.jpg', 'rb') as im:
        #     b = bytearray(im.read())
        image1 = Image.open(io.BytesIO(ba))
        image2 = Image.open('test_picture.jpg')
        diff = ImageChops.difference(image1, image2)
        assert not diff.getbbox()

    @pytest.mark.parametrize(
        "item_id,expected",
        [
            (10000000,pytest.raises(WowApiException)),
            ('blah',pytest.raises(WowApiException))
        ])
    def test_bad_findItemPic(self, item_id, expected):
        '''Test getting the item name corresponding to a given item ID'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        with expected:
            assert wow.findItemPic(item_id) is not None

    def test_findAuctions(self):
        '''Test getting auction house results'''
        wow = WowDB(locale, region, realm, client_id, client_secret)
        data = wow.findAuctions()
        assert 'id' in data[0].keys()

    # def test_sortListings(self):
    #     '''Test sorting auction house results'''
    #     wow = WowDB(locale, region, realm, client_id, client_secret)
    #     data = wow.findAuctions()
    #     sorted_list = wow.sortListings(data)
    #     # assert all (k in sorted_list[0] for k in (
    #     #     'item_id',
    #     #     'quantity',
    #     #     'avg_unit_price',
    #     #     'std_dev',
    #     #     'high_price',
    #     #     'low_price',
    #     #     'num'
    #     # ))
    #     for i in range(len(sorted_list) - 1):
    #         assert sorted_list[i]['item_id'] < sorted_list[i+1]['item_id']
        