from wowDB import WowDB
from dbConnect import *

def main():
    bnetcred = config('settings.ini', 'bnetcred')
    wow = WowDB(**bnetcred)
    data = wow.findAuctions()
    data = wow.sortListings(data)

    db_params = config('settings.ini', 'wowdb')
    dbcon = dbConnect()
    dbcon.connect(**db_params)
    dbcon.checkTableExists(wow.getRealmSlug())
    for i in data:
        dbcon.addItem(i)

if __name__ == "__main__":
    main()