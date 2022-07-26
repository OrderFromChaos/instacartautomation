# Standard libraries
import json
import time
from pathlib import Path

# Pypi libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from termcolor import cprint

# Internal libraries
from .db import DBManager
from .misc import askBoolean
from .errors import InstacartError
from ..grocerylister import generateGroceryList



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

        self.browser.implicitly_wait(2)

        login_button = self.find_xpath('/html/body/div[1]/div/header/div[2]/nav/div[2]/button[1]/span')
        try:
            login_button.click()
        except WebDriverException as e:
            input('Likely pop-up! Please close pop-up and press ENTER when closed.')
            login_button.click()

        time.sleep(2)

        username_box_alternatives = [f'/html/body/div[{x}]/div/div/div/div/div[2]/div[1]/form/div[1]/div/div/input' for x in range(4, 9)]
        username_box, box_idx = self._tryAlternatives(
            username_box_alternatives,
            By.XPATH,
            list(range(4, 9)),
            purpose='username box'
        )

        password_box = self.find_xpath(f'/html/body/div[{box_idx}]/div/div/div/div/div[2]/div[1]/form/div[2]/div/div/input')
        login_info = self.behavior_config['instacart']
        username_box.send_keys(login_info['email'])
        password_box.send_keys(login_info['password'])

        time.sleep(2)

        submit_button = self.find_xpath(f'/html/body/div[{box_idx}]/div/div/div/div/div[2]/div[1]/form/div[4]/button')
        submit_button.click()

        time.sleep(3)

        # Handler for captcha
        if self.browser.current_url == login_url:
            # It didn't leave the page because something is blocking it - probably captcha
            cprint('Captcha detected! Please solve the captcha and press enter when complete.', 'red')
            _ = input()

            time.sleep(3)

        time.sleep(11) # This takes forever for some reason
        self.logged_in = True


    def logIn(self):
        if self.logged_in == False:
            self._logIn()


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

            # TODO: Check for pop-up on store page and close
            pass

            # Get list of stores
            store_path_alternatives = [
                '/html/body/div[1]/div[1]/div[2]/div/div/div[18]/div/ul',
                '/html/body/div[1]/div[2]/div[2]/div/div/div[18]/div/ul',
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
                store_element = self.find_xpath(f'/html/body/div[1]/div[{functioning_idx}]/div[2]/div/div/div[18]/div/ul/li[{idx}]/a/span/span[2]/span[1]/span')
                store_idx_lookup[store_element.text.strip().lower()] = idx

            # Click on store matching target name
            target_name = self.store.lower()
            if target_name in store_idx_lookup:
                target_idx = store_idx_lookup[target_name]
                print(f'Matched {target_name} to {target_idx}')
            else:
                for store_name, idx in store_idx_lookup.items():
                    print(idx, store_name)
                raise RuntimeError(f'Unable to locate store "{target_name}"! Valid names are printed above ^^')
            target_store = self.find_xpath(f'/html/body/div[1]/div[{functioning_idx}]/div[2]/div/div/div[18]/div/ul/li[{target_idx}]')
            target_store.click()

        time.sleep(5)
        if self.store not in self.known_store_urls:
            self.known_store_urls[self.store] = self.browser.current_url()


    def shopAtSingleStore(self, request, store):
        groceries = generateGroceryList(request)
        store_listings = self.DBManager.loadStoreListingDB()
        self.logIn()

        # 
        for ing in groceries.values():
            # Look up ing name
            #   If exists, go to page and add quantity
            #   If not exists, ask for page and store in DB
            pass


    def goToItem(self, store, item_name):
        # Check if item exists in DB
        #   if so, navigate to item
        #   if not, request user input
        # DOES NOT wait at the end - user is expected to handle timing for this fxn
        pass


    def _seekIngredientsInStore(self, ing):
        # Note: Assumes self.known_store_urls has been populated
        print(f'Looking up the item in {self.store}...')

        # Ensure we're on a searchable page for this store
        if self.store not in self.known_store_urls:
            raise RuntimeError('Unable to find store landing page URL in known_store_urls')
        self.browser.get(self.known_store_urls[self.store])
        time.sleep(10)

        time.sleep(1000000)

        # TODO:
        # Look up in search bar
        # Ask user to select a most preferred item and press enter when loaded
        # Write item to DB automatically
        # Ask if second most preferred items satisfy and loop until done

        pass


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
            time.sleep(10)

        # Assume behavior fxn will handle tail waits properly
        behavior_fxn(*args, **kwargs)


    def updatePrices(self, request, timeout_days=3):
        self.logIn()



if __name__ == "__main__":
    expected_config_loc = Path('databases/siteconfig.json')
    c = WebsiteController(expected_config_loc)
    request = [
        ['Dan Dan Noodles', 1]
    ]
    groceries = generateGroceryList(request)
    c.goToStore('Draeger\'s Market')

    def dummy():
        pass

    c._iterateOverHiPriItemsWithOnPageBehavior(groceries, dummy)

    # for ing in groc.values():
    #     print(ing)

    # c.updatePrices(groc)

    # c.shopAtSingleStore(request, "Draeger's Market")
