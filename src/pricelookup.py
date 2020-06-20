from grocerylister import generateGroceryList
import json
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta

PRICECOOLDOWN = 12*60 # 12 hrs (minutes)
# Some ingredients are usually used in pinch quantities and don't
#     really make sense to compute. Or they might be on a non-instacart
#     site, which this code doesn't support. Here they are:
IGNORE = {
    'sichuan peppercorns', # non-Instacart
    'salt', # pinch
    'pepper', # pinch
    'black pepper', #pinch
    'sea salt', # pinch
    'Shaoxing rice wine' # non-Instacart
}

def updatePrices(inglist, store):
    # Updates products outside of the PRICECOOLDOWN range
    #     and asks for info as needed
    with open('../databases/ingdata.json', 'r') as f:
        ingdata = json.load(f)

    with open('../databases/passwords.json', 'r') as f:
        passwords = json.load(f)

    # First check if running the browser is necessary
    for ing in inglist:
        if ing in IGNORE:
            continue
        # Check to see if the price was updated within PRICECOOLDOWN
        elif 'price' in ingdata[ing]:
            if store in ingdata[ing]['price']:
                if datetime.strptime(ingdata[ing]['price'][store]['updated'], r'%Y-%m-%d %H:%M:%S') >= datetime.now() - timedelta(hours=PRICECOOLDOWN):
                    continue
        else:
            break
    else:
        print('All prices updated within PRICECOOLDOWN.')
        return
    
    # Initialize browser
    browser = webdriver.Chrome(passwords['seleniumloc'])
    find_css = browser.find_element_by_css_selector
    find_xpath = browser.find_element_by_xpath
    login_url = 'https://www.instacart.com/#login'

    # Log into instacart using user info
    browser.get(login_url)
    browser.implicitly_wait(2)
    username_box = find_css("#nextgen-authenticate\.all\.log_in_email")
    password_box = find_css("#nextgen-authenticate\.all\.log_in_password")
    logininfo = passwords['instacart']
    username_box.send_keys(logininfo['email'])
    password_box.send_keys(logininfo['password'])
    time.sleep(2)
    submit_button = find_xpath(r'//*[@id="main-content"]/div[2]/form/div[3]/button')
    submit_button.click()
    time.sleep(5)

    # Go to the URLs for every ingredient in "inglist"
    for ing in inglist:
        if ing in IGNORE:
            continue

        # Get URL if it doesn't already exist
        if 'URLs' not in ingdata[ing]:
            print(f'Instacart URL needed for "{ing}" at store {store}!')
            print('Enter the URL below:')
            inputurl = input()
            inputurl = inputurl.strip()
            if inputurl == "ignore":
                continue
            ingdata[ing]['URLs'] = dict()
            ingdata[ing]['URLs'][store] = inputurl
        
        # Check to see if the price was updated within PRICECOOLDOWN
        if 'price' in ingdata[ing]:
            if store in ingdata[ing]['price']:
                if datetime.strptime(ingdata[ing]['price'][store]['updated'], r'%Y-%m-%d %H:%M:%S') >= datetime.now() - timedelta(hours=PRICECOOLDOWN):
                    continue

        # Get the price from the page
        browser.get(ingdata[ing]['URLs'][store])
        browser.implicitly_wait(5)
        quantdivfound = False
        name = find_xpath('//*[@id="react-views-container"]/div/div/div/div[1]/div/div/div/div/div[1]/div/div[4]/div[1]/h2').text
        print(name)
        try: 
            quantinfo = find_xpath('//*[@id="react-views-container"]/div/div/div/div[1]/div/div/div/div/div[1]/div/div[4]/div[1]/div[1]/p').text
            quantdivfound = True
            print(quantinfo)
        except NoSuchElementException:
            # The quantity info is in the price div
            pass
        price = find_xpath('//*[@id="react-views-container"]/div/div/div/div[1]/div/div/div/div/div[1]/div/div[4]/div[1]/div[2]/div/div[1]/span[2]').text
        print(price)
        
        # Types:
        # Info is in quantity and price div (eg scallions, "bunch" and "each")
        #   Green Onions (Scallions)
        #   1 bunch
        #   $0.99 /each
        # Info is in price div only (eg ginger root). No quant div exists
        #   Ginger Root
        #   $3.49 /lb
        # Info is in quantity div only (sushi chef pickled ginger https://www.instacart.com/store/items/item_497495884)
        #   Sushi Chef Pickled Ginger
        #   6 oz
        #   $4.69

        # Differentiate between types
        if quantdivfound:
            quantinfo = quantinfo.split(' ')
            quant = int(quantinfo[0])
            qtype = ' '.join(quantinfo[1:]).strip()
        else:
            quant = 1
            qtype = price.split('/')[1].strip()
        if '/' in price:
            price = price.split('/')[0].strip()
        price = float(price[1:]) # TODO: Make prices not stored as float internally

        ingdata[ing]['price'] = dict()
        ingdata[ing]['price'][store] = {
            'quantity': quant,
            'qtype': qtype,
            'price': price,
            'updated': datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')
        }

        # ingdata should now have all the relevant info
        with open('../databases/ingdata.json', 'w') as f:
            json.dump(ingdata, f, indent=4)

        time.sleep(5)

def computePrice(inglist, store):
    # Actually does the computation and adds everything together
    updatePrices(inglist, store)

    

if __name__ == "__main__":

    # Generate a list to work with
    request = [
        ['Egg Drop Soup', 2]
    ]
    ingredients = generateGroceryList(request)
    computePrice(ingredients, "stater bros")

# New ingdata.json format:
#   "ground cumin": {
#       "liquid": false,
#       "priceurls": {
#           "stater bros": [
#               "https://youtu.be/9nPVkpWMH9k"
#           ],
#           "ralphs": [
# 
#           ]
#       },
#       "price": {
#           "current": 4.56,
#           "date": <some date format, dunno>
#       }
#   },