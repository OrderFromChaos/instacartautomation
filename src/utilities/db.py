# Standard libraries
import atexit
import json
from pathlib import Path

# Pypi libraries
import jsonschema
import pendulum

# Local libraries
from .errors import InstacartError
from .misc import askBoolean



PAGE_SCHEMA = {
    'type': 'object',
    'properties': {
        'URL': {'type': 'string'},
        'quantity': {'type': 'number'},
        'qtype': {'type': 'string'},
        'price': {'type': 'number'},
        'updated': {
            'type': 'string',
            'pattern': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}-\d{2}:\d{2}$',
        },
        'preference': {'type': 'number'},
    },
    'additionalProperties': False
}



INGREDIENT_SCHEMA = {
    'type': 'object',
    'properties': {
        'liquid': {'type': 'boolean'},
        'instacart': {'type': 'boolean'},
        'URLs': {
            'type': 'object',
            'properties': {
                '^S_': {
                    'type': 'array',
                    'items': {
                        **PAGE_SCHEMA
                    }
                }
            }
        }
    },
    'additionalProperties': False
}



class DBManager:
    def __init__(self):
        self.store_listing_db = None
        self.store_listing_db_loc = Path('databases') / 'store_listings.json'

        def writeStoreListingDBToFile():
            if isinstance(self.store_listing_db, dict):
                with open(self.store_listing_db_loc, 'w') as f:
                    json.dump(self.store_listing_db, f, indent=4)
                print('Wrote to store listing DB!')

        atexit.register(writeStoreListingDBToFile)


    def loadStoreListingDB(self):
        # Load store_listing DB - tells where to get natural items
        if self.store_listing_db is None:
            db_path = Path('databases') / 'store_listing.json'
            if not db_path.exists():
                # Don't create here - this will happen later during write
                with open(db_path, 'w') as f:
                    json.dump({}, f)
                db = {}
            else:
                with open(db_path, 'r') as f:
                    db = json.load(f)
            
            self.store_listing_db = db


    def addExternalItemToStoreListingDB(self, ing, warn=True):
        # Items sent here will be marked as not purchasable on instacart
        self.loadStoreListingDB()

        assert isinstance(ing, str), f'ingredient must be of type str, got {type(ing)}'

        if ing in self.store_listing_db:
            if warn:
                ans = askBoolean('Disabling old ingredient entry, are you sure?')
                if not ans:
                    return
            self.store_listing_db[ing]['instacart'] = False
        else:
            liquid = askBoolean(f'Is "{ing}" a liquid?')
            write_dict = {
                'liquid': liquid,
                'instacart': False,
                'URLs': []
            }
            jsonschema.validate(write_dict, INGREDIENT_SCHEMA)
            self.store_listing_db[ing] = write_dict


    def addURLForStoreAndIngToStoreListingDB(self, ing, store, entry):
        # Add normal entry to store listing DB
        self.loadStoreListingDB()

        assert isinstance(ing, str), f'ingredient must be of type str, got {type(ing)}'
        assert isinstance(store, str), f'ingredient must be of type str, got {type(store)}'
        assert isinstance(entry, dict), f'ingredient must be of type dict, got {type(entry)}'

        if ing not in self.store_listing_db:
            liquid = askBoolean(f'Is "{ing}" a liquid?')

            write_dict = {
                'liquid': liquid,
                'instacart': True,
                'URLs': {
                    store: [entry]
                }
            }
            jsonschema.validate(write_dict, INGREDIENT_SCHEMA)
            self.store_listing_db[ing] = write_dict

        else:
            jsonschema.validate(entry, PAGE_SCHEMA)
            if store not in self.store_listing_db[ing]['URLs']:
                self.store_listing_db[ing]['URLs'][store] = []
            self.store_listing_db[ing]['URLs'][store].append(entry)
    
    def getHighestPri(self, ing, store):
        self.loadStoreListingDB()

        assert isinstance(ing, str), f'ingredient must be of type str, got {type(ing)}'
        assert isinstance(store, str), f'ingredient must be of type str, got {type(store)}'

        # If error (missing ing or store), return int indicating error code

        if ing in self.store_listing_db:
            if store in self.store_listing_db[ing]['URLs']:
                return sorted(self.store_listing_db[ing]['URLs'][store], key=lambda d: d['preference'])[0]
            else:
                return InstacartError(1)
        else:
            return InstacartError(0)



if __name__ == '__main__':
    dbm = DBManager()
    sample_args = [
        'fresh basil',
        'stater bros',
        {
            'URL': "https://www.instacart.com/store/items/item_497524991",
            "quantity": 1,
            "qtype": "each",
            "price": 2.99,
            "updated": pendulum.now().isoformat(),
            "preference": 5,
        }
    ] 

    # Case 1
    dbm.store_listing_db = {}
    try:
        dbm.addURLForStoreAndIngToStoreListingDB(*sample_args)
    except jsonschema.exceptions.SchemaError as e:
        raise e
    print('Successfully validated!')

    # Case 2
    dbm.store_listing_db['fresh basil']['URLs'] = {}
    try:
        dbm.addURLForStoreAndIngToStoreListingDB(*sample_args)
    except jsonschema.exceptions.SchemaError as e:
        raise e
    print('Successfully validated!')

    # Case 3
    dbm.store_listing_db['fresh basil']['URLs']['stater bros'] = []
    try:
        dbm.addURLForStoreAndIngToStoreListingDB(*sample_args)
    except jsonschema.exceptions.SchemaError as e:
        raise e
    print('Successfully validated!')
