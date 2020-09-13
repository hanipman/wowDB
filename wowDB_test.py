import pytest
from wowDB import WowDB

class wowDB_test(unittest.TestCase):
    locale = 'en_US'
    realm = 'Area 52'
    region = 'us'
    WOW_CLIENT_ID = ''
    WOW_CLIENT_SECRET = ''

    wow = WowDB(WOW_CLIENT_ID, WOW_CLIENT_SECRET)

    def test_getRealmID(self):
        data = wow.getRealmID()
        assert data == 1566
