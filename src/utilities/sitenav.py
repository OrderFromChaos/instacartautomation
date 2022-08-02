# Standard libraries
import json
import math
import time
from pathlib import Path

# Pypi libraries
import pendulum
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from termcolor import cprint

# Internal libraries
from .db import DBManager
from .misc import askBoolean
from .errors import InstacartError
from ..grocerylister import generateGroceryList
from ..ingredient import Ingredient


class WebsiteController:
    """
    Controller class for web browser on Instacart. Keeps track of current URL, queue of next URLs,
    and other relevant data. Creates a browser on-demand if one doesn't exist (singleton).
    """


    def __init__(self, behavior_config):
        # Load config from either file path or
        if isinstance(behavior_config, Path):
            with open(behavior_config, 'r') as f:
                self.behavior_config = json.load(f)
        elif isinstance(behavior_config, dict):
            self.behavior_config = behavior_config
        else:
            raise RuntimeError(f'Unrecognized "behavior_config" type: {type(behavior_config)}')

        self.browser = None
        self.logged_in = False
        self.store = None
        self.store_domain = None # Tracks what store subpage currently on - just the name of store
        self.known_store_urls = {}
        self.DBManager = DBManager()


    def _startBrowser(self):
        if self.browser is None:
            # Initialize browser
            self.browser = webdriver.Chrome() # Assumes chromedriver is on system PATH
            self.find_css = lambda path: self.browser.find_element(By.CSS_SELECTOR, path)
            self.find_xpath = lambda path: self.browser.find_element(By.XPATH, path)


    def _logIn(self):
        self._startBrowser()

        login_url = 'https://www.instacart.com/'
        self.browser.get(login_url)

        time.sleep(5)

        self._checkForReaKitPopup()

        login_button = self.find_xpath('/html/body/div[1]/div/header/div[2]/nav/div[2]/button[1]/span')
        login_button.click()

        time.sleep(2)

        # Note that Instacart will switch between two alternative login boxes - one with only email and one with
        #   email and password. The code needs to detect between these with some xpath location fuzzing on top.
        #   Fortunately the username location stays the same.
        login_info = self.behavior_config['instacart']

        username_box_alternatives = [
            f'/html/body/div[{x}]/div/div/div/div/div[2]/div[1]/form/div[1]/div/div/input' for x in range(4, 9)
        ]
        username_box, box_idx = self._tryAlternatives(
            username_box_alternatives,
            By.XPATH,
            list(range(4, 9)),
            purpose='username box'
        )
        username_box.send_keys(login_info['email'])

        # Sometimes Instacart will serve a dynamic pop-out password box - need to wait for it to show up
        # This try-catch determines whether we're in that regime
        password_xpath = f'/html/body/div[{box_idx}]/div/div/div/div/div[2]/div[1]/form/div[2]/div/div/input'
        try:
            password_box = self.find_xpath(password_xpath)
        except NoSuchElementException:
            cprint('Detected Type 2 Login: Dynamic Password Box', 'blue')
            password_xpath = f'/html/body/div[{box_idx}]/div/div/div/div/div[2]/div[1]/form/div[2]/div[1]/div/div/input'

        time.sleep(2) 

        password_box = self.find_xpath(password_xpath)
        password_box.send_keys(login_info['password'])

        time.sleep(2)

        submit_button = self.find_xpath(f'/html/body/div[{box_idx}]/div/div/div/div/div[2]/div[1]/form/div[4]/button')
        submit_button.click()

        time.sleep(3)

        # Handler for captcha
        if self.browser.current_url == login_url:
            # It didn't leave the page because something is blocking it - probably captcha
            cprint('CAPTCHA detected! Please solve the captcha and press ENTER when complete.', 'red', end='')
            _ = input()

            time.sleep(3)

        time.sleep(11) # This takes forever for some reason
        self.logged_in = True


    def logIn(self):
        if self.logged_in == False:
            self._logIn()


    def _checkForReaKitPopup(self):
        # TODO: Automatically close instead of prompting user
        #   Note that for auto closing, there are 4 __reakit-portal class instances, but
        #   all the fake ones have a hidden data-dialog-ref under them. 
        #   Could possibly distinguish real one this way.
        try:
            elts = self.browser.find_elements(By.CLASS_NAME, '__reakit-focus-trap')
            cprint('Popup detected! Please close and press ENTER to continue.', 'red', end='')
            input()
        except NoSuchElementException as e:
            pass


    def _tryAlternatives(self, paths, selector, related_idxs, purpose=''):
        """
        Given a list of paths, try each one. Meant to defeat sites with div location fuzzing.

        Selector is a selenium.webdriver.common.by.By object (ex. By.XPATH)
        Related_idxs lets _tryAlternatives to know what information to return with each path - eg. an index.
            (In the future it could automatically detect what makes each path unique, but this would be complex behavior.)
        Purpose is for error logging.
        """
        assert len(paths) == len(related_idxs)

        functioning_idx = None
        for idx, alternative in zip(related_idxs, paths):
            try:
                alternative_obj = self.browser.find_element(selector, alternative)
                functioning_idx = idx
                break
            except NoSuchElementException:
                continue

        if functioning_idx is None:
            raise RuntimeError(f'No alternatives worked{" for " if purpose else ""}{purpose}')

        return alternative_obj, functioning_idx


    def goToStore(self, store):
        """
        Go to the "store" landing page and set self.store.
        """
        self.store = store
        self.logIn()

        if self.store in self.known_store_urls:
            self.browser.get(self.known_store_urls[self.store])
        else:
            # Go to store listing page
            store_url = 'https://www.instacart.com/store'
            if self.browser.current_url != store_url:
                self.browser.get(store_url)
                time.sleep(5)

            # Check for pop-up on store page and close
            self._checkForReaKitPopup()

            # Get list of stores
            store_path_alternatives = [
                # Previously:
                #                                            18
                '/html/body/div[1]/div[1]/div[2]/div/div/div[19]/div/ul',
                '/html/body/div[1]/div[2]/div[2]/div/div/div[19]/div/ul',
            ]
            store_list_obj, functioning_idx = self._tryAlternatives(
                store_path_alternatives,
                By.XPATH,
                [1, 2],
                purpose='store name lookup'
            )

            # Get store names from list
            found_elt = store_list_obj.find_elements(By.TAG_NAME, 'li')
            store_idx_lookup = {}
            for idx in range(1, len(found_elt) + 1):
                store_element = store_list_obj.find_element(By.XPATH, f'li[{idx}]/a/span/span[2]/span[1]/span')
                store_idx_lookup[store_element.text.strip().lower()] = idx

            # TODO: Also gather "bulk" stores like Costco - they're not in the main grocery list

            # Click on store matching target name
            target_name = self.store.lower()
            if target_name in store_idx_lookup:
                target_idx = store_idx_lookup[target_name]
                cprint(f'Matched "{target_name.title()}" to {target_idx}', 'green')
            else:
                for store_name, idx in store_idx_lookup.items():
                    print(idx, store_name)
                raise RuntimeError(f'Unable to locate store "{target_name}"! Valid names are printed above ^^')
            target_store = self.find_xpath(f'/html/body/div[1]/div[{functioning_idx}]/div[2]/div/div/div[19]/div/ul/li[{target_idx}]')
            target_store.click()

        time.sleep(5)
        self.store_domain = self.store
        if self.store not in self.known_store_urls:
            self.known_store_urls[self.store] = self.browser.current_url


    def goToItem(self, store, item_name):
        # Check if item exists in DB
        #   if so, navigate to item
        #   if not, request user input
        # DOES NOT wait at the end - user is expected to handle timing for this fxn
        pass


    def _getIngredientInfo(self, direct=False):
        # Get write dict from ingredient
        #   direct = True means the ingredient URL was loaded directly
        #   direct = False means it was navigated to by clicking on an item entry (so it's a pop-up)

        # Find root div with pricing and quantity info
        if direct == False:
            root_info_alternatives = [
                '/html/body/div[16]/div/div/div/div[2]/div[1]/div[2]',
                '/html/body/div[17]/div/div/div/div[2]/div[1]/div[2]',
                '/html/body/div[18]/div/div/div/div[2]/div[1]/div[2]',
            ]
            root_info_element, functioning_idx = self._tryAlternatives(
                root_info_alternatives,
                By.XPATH,
                [16, 17, 18],
                purpose='root info lookup for item'
            )
        else:
            root_info_element = self.find_xpath('/html/body/div[1]/div[2]/div/div/div/div/div/div[1]/div/div[2]/div[2]/div[2]/div[1]/div[2]')

        # Detect type of item page
        gettxt = lambda subpath: root_info_element.find_element(By.XPATH, subpath).text
        currency_to_100s = lambda dollarstr: int(float(dollarstr.strip('$'))*100)
        product_name = gettxt('div[1]/h2/span')
        try:
            # Vegetable/fruits: estimated weight and number quantity
            #   https://www.instacart.com/store/items/item_565643965
            # "$5.88 each (est.)"
            each_est = gettxt('div[2]/div[1]/div[1]/div[1]/div[1]/span')
            # "$14.69 / lb" or "$0.79/oz"
            price_per_weight = gettxt('div[2]/div[1]/div[1]/div[1]/div[2]')

            price_parts = price_per_weight.split('/')
            weight_price = currency_to_100s(price_parts[0].strip())
            each_price = currency_to_100s(each_est.split(' ')[0].strip())

            quantity = round(each_price / weight_price, 0)
            qtype = price_parts[-1]
            price = each_price

        except NoSuchElementException:
            # Standard: product name, quantity and qtype, price, number of self
            #   https://www.instacart.com/store/items/item_552059888
            quantity_and_qtype = gettxt('div[1]/div[2]/span')
            price = currency_to_100s(gettxt('div[2]/div[1]/div[1]/div/div[1]/span'))
            number_of_self = gettxt('div[2]/div[1]/div[2]/button[1]/span/span')

            qparts = quantity_and_qtype.split(' ')
            quantity, qtype = qparts[0], ' '.join(qparts[1:])


        write_dict = {
            'URL': self.browser.current_url,
            'quantity': int(quantity),
            'qtype': qtype,
            'price': price,
            # 'preference': preference_counter,
            'product_name': product_name,
        }
        return write_dict


    def _seekIngredientsInStore(self, ing):
        # Note: Assumes self.known_store_urls has been populated
        assert isinstance(ing, str), f'ingredient must be of type str, got {type(ing)}'
        click_count = 1

        print(f'Looking up the item in {self.store}...')

        # Ensure we're on a searchable page for this store
        if self.store not in self.known_store_urls:
            raise RuntimeError('Unable to find store landing page URL in known_store_urls')
        store_landing_url = self.known_store_urls[self.store]
        if self.store_domain != self.store:
            self.browser.get(store_landing_url)
            self.store_domain = self.store
        else:
            click_count = 2
        time.sleep(5)

        # Look up in search bar
        search_alternatives = [
            '/html/body/div[1]/div[1]/div[1]/div[2]/div[1]/div/div/form/input',
            '/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/div/form/input',
        ]
        search_box, functioning_idx = self._tryAlternatives(
            search_alternatives,
            By.XPATH,
            [1, 2],
            purpose='search box lookup'
        )
        for i in range(click_count+1):
            # Get search box focus, even if there's a pop-up
            # https://stackoverflow.com/questions/48665001/can-not-click-on-a-element-elementclickinterceptedexception-in-splinter-selen
            self.browser.execute_script('arguments[0].click();', search_box)
        time.sleep(1)

        search_box.clear()

        time.sleep(1)

        search_box.send_keys(ing)
        search_box.send_keys(Keys.RETURN)

        time.sleep(5)

        preference_counter = 1
        while True:
            # Ask user to select a most preferred item and press enter when loaded
            cprint(f'Please select your #{preference_counter} option by clicking on it, then hit ENTER here.', 'green', end='')
            input()

            write_dict = self._getIngredientInfo(direct=False)
            write_dict['preference'] = preference_counter

            # Write item to DB automatically
            self.DBManager.addURLForStoreAndIngToStoreListingDB(ing, self.store, write_dict)
            cprint('Wrote this to store listing DB:', 'blue')
            print(json.dumps(write_dict, indent=4))

            # Ask if second most preferred items satisfy and loop until done
            ans = askBoolean('Do you have more alternative items?')
            if not ans:
                break
            preference_counter += 1


    def _iterateOverUnseenItems(self, groceries):
        self.logIn()
        self.DBManager.loadStoreListingDB() # initialized to self.store_listing_db

        for ing in groceries.values():
            if ing.name not in self.DBManager.store_listing_db:
                ans = askBoolean(f'Unknown ingredient "{ing.name}"! Is this purchasable from instacart?')
                if not ans:
                    self.DBManager.addExternalItemToStoreListingDB(ing.name)
                    continue
                else:
                    # Get data with user
                    self._seekIngredientsInStore(ing.name)


    def _iterateOverHiPriItemsWithOnPageBehavior(self, groceries, behavior_fxn, *args, **kwargs):
        # Defines a generic iterator over ingredients at a store
        # Uses store from self.store
        self.logIn()
        self.DBManager.loadStoreListingDB() # initialized to self.store_listing_db

        for ing in groceries.values():
            if ing.name not in self.DBManager.store_listing_db:
                ans = askBoolean(f'Unknown ingredient "{ing.name}"! Is this purchasable from instacart?')
                if not ans:
                    self.DBManager.addExternalItemToStoreListingDB(ing.name)
                    continue
                else:
                    # Get data with user
                    self._seekIngredientsInStore(ing.name)

            # Now get highest priority item the user added and nav to the page
            entry = self.DBManager.getHighestPri(ing.name, self.store)
            if isinstance(entry, InstacartError):
                if not self.DBManager.store_listing_db[ing.name]['instacart']:
                    continue
                raise RuntimeError(f'Encountered unexpected missing data. {entry}')

            self.browser.get(entry['URL'])
            time.sleep(5)

            # Assume behavior fxn will handle tail waits properly
            kwargs['ing'] = ing
            behavior_fxn(*args, **kwargs)


    def shopAtSingleStoreHighestPri(self, request, store):
        groceries = generateGroceryList(request)
        store_listings = self.DBManager.loadStoreListingDB()
        self.logIn()

        def shopperBehavior(*args, **kwargs):
            ### Compute required amount of items given request

            # Load entry from DB
            request_ing = kwargs['ing']
            sldb = self.DBManager.store_listing_db
            entry = sldb.getHighestPri(request_ing.name, self.store)

            # Compare to actual data on website and print differences
            write_dict = self._getIngredientInfo(direct=True)

            for key, new_value in write_dict.items():
                old_value = entry[key]
                if old_value != new_value:
                    cprint(f'{key}: {old_value} -> {new_value}', 'yellow')
                    # FIXME: For now, directly modify old entry. It will be written on program exit.
                    entry[key] = new_value
            entry['updated'] = pendulum.now().isoformat()

            # Use actual data to compute required amount of items
            # Construct ingredient from web data
            web_ing = Ingredient(
                request_ing.name,
                quantity=write_dict['quantity'],
                qtype=write_dict['qtype'],
                liquid=request_ing.liquid,
            )
            n = web_ing / request_ing
            print(f'Need {n} items...')
            actual = math.ceil(n)
            # FIXME: Implement div for Ingredient class

            # Select quantity from drop-down
            # TODO:

            # Submit
            # TODO:

            print('Waiting forever...')
            input()

        self._iterateOverHiPriItemsWithOnPageBehavior(groceries, shopperBehavior)


    def updatePrices(self, request, timeout_days=3):
        self.logIn()
        # TODO: Check for hidden Instacart API to make this faster



if __name__ == "__main__":
    expected_config_loc = Path('databases/siteconfig.json')
    c = WebsiteController(expected_config_loc)
    request = [
        ['Dan Dan Noodles', 1]
    ]
    groceries = generateGroceryList(request)
    c.goToStore('Draeger\'s Market')
    c._iterateOverUnseenItems(groceries)
    c.shopAtSingleStoreHighestPri(request, "Draeger's Market")
