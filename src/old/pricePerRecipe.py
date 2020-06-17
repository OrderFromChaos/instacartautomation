# I tried my best to not use Selenium here, but Instacart requires logins and Javascript loading for prices.
# At a certain point, it really wasn't worth it to learn an entirely new framework (scrapy) and figure out dynamic loading.
import re       # Some easy parsing; see getInfo(sliceIngredients()).
from selenium import webdriver # Getting price data
import datetime # To prevent overdoing the price updates
from time import sleep # Manual cooldowns for requesting
from datetime import datetime

PRICECOOLDOWN = 12*60 # In minutes

addrules = [
    # Format:
    # (type1, type2), number, when_allowed
    # Examples:
    # ('tbsp', 'tsp'), 3, ('any')
    # ('lb', 'tbsp'), 16, ('ginger')
    # List is searched through from top to bottom and first match works, so put all specific ones at the top
    # Leftmost qtype is given priority and all units will be converted to it during addition
    (('lb','tbsp'),16,('ginger')),
    (('lb','tsp'),48,('ginger')),
    (('lb','cups'),1,('ginger')),
    (('lb','tbsp'),36.29,('sugar')),
    (('lb','tsp'),36.29*3,('sugar')),
    (('lb','cups'),36.29/16,('sugar')),
    (('oz','tbsp'),1.77,('peanut butter')),
    (('tbsp',''),3,('garlic')),
    (('lb',''),2,('sweet onion','yellow onion')),
    (('oz','tbsp'),2,('any')),
    (('oz','tsp'),6,('any')),
    (('tbsp','tsp'),3,('any')),
    (('cups','oz'),8,('any')),
    (('lb','oz'),16,('any'))
]

# conversions = {
#    'lbtbsp': 15, # Just for ginger
#    'lbtsp': 45, # Also just for ginger
#    'lbcup': 15/16, # Also just ginger again
#    'cupscup':1,
#    'cupcups':1
#    # 'sliceoz': 1 # Specifically for thick cut bacon
# }

# TODO: Might need a "descriptor" attribute later for something like "liquid", but ignoring this for now
# TODO: qtype coercion (will be needed to compute prices)
class Ingredient:
    def __init__(self, name='', quantity=0, qtype=''):
        self.name = name
        self.quantity = quantity
        self.qtype = qtype
    def __add__(self,other):
        # Intelligently deal with stuff
        assert type(other) == Ingredient, 'Can only add together two Ingredient objects'
        assert self.name == other.name, 'Cannot add together two different ingredients: (' + repr(self.name) + ') AND (' + repr(other.name) + ')'
        if self.qtype == other.qtype: # Easy!
            return Ingredient(self.name,self.quantity+other.quantity,self.qtype)
        else: # Harder. Needs unit conversion.
            conversions = {(self.qtype,other.qtype),(other.qtype,self.qtype)} # So you can get both directions (tbsp -> tsp) and (tsp -> tbsp)
            for rule in addrules:
                if rule[0] in conversions and ('any' in rule[2]  or  self.name in rule[2]): # Correct conversion (tbsp -> tsp) and allowed for type of ingredient
                    relevant_rule = rule
                    break
            else: # Runs only if no conversion was found
                raise Exception('Failed to add together (' + repr(self.name) + ') AND (' + repr(other.name) + ') due to quant type mismatch: (' + repr(self.qtype) + ') AND (' + repr(other.qtype) + ')')
            
            priority_qtype = [self.qtype,other.qtype].index(relevant_rule[0][0]) # For example, 'tbsp' is preferred in rule ('tbsp','tsp')
            if priority_qtype == 0:
                return Ingredient(self.name,self.quantity + other.quantity/relevant_rule[1], self.qtype)
            else:
                return Ingredient(self.name,other.quantity + self.quantity/relevant_rule[1], other.qtype)
    def __truediv__(self, bottom): # The other one is __floordiv__
        ''' Returns a float ratio after doing correct unit conversion. Units cancel when dividing. '''
        assert type(bottom) == Ingredient, 'Can\'t divide by a non-Ingredient object'
        assert self.name == bottom.name, 'Can\'t divide apples and oranges ;)'
        if self.qtype == bottom.qtype: # Easy!
            return self.quantity / bottom.quantity
        else: # Harder. Needs unit conversion.
            conversions = {(self.qtype,bottom.qtype),(bottom.qtype,self.qtype)} # So you can get both directions (tbsp -> tsp) and (tsp -> tbsp)
            for rule in addrules:
                if rule[0] in conversions and ('any' in rule[2]  or  self.name in rule[2]): # Correct conversion (tbsp -> tsp) and allowed for type of ingredient
                    relevant_rule = rule
                    break
            else: # Runs only if no conversion was found
                raise Exception('Failed to divide (' + repr(self.name) + ') due to quant type mismatch: (' + repr(self.qtype) + ') AND (' + repr(bottom.qtype) + ')')
            
            # Ratio doesn't depend on units, so just use an arbitrary one. I use the same priority_qtype rule as __add__.
            priority_qtype = [self.qtype,bottom.qtype].index(relevant_rule[0][0]) # For example, 'tbsp' is preferred in rule ('tbsp','tsp')
            if priority_qtype == 0: # Convert denominator
                return self.quantity / (bottom.quantity / relevant_rule[1])
            else:                   # Convert numerator
                return (self.quantity/relevant_rule[1]) / bottom.quantity
    def __repr__(self):
        return str((self.name,self.quantity,self.qtype)) # Done the lazy way
    def __mul__(self,integer): # Scalar multiplication on the right
        return Ingredient(self.name,self.quantity*integer,self.qtype)

def getInfo():
    '''Pulls from grocery info, which is formatted as recipe|ingredient 1,ingredient 2,...
    Output is a dictionary of {recipe name:(Ingredient object,Ingredient object),...}'''
    with open('./_INFO.txt','r') as f:
        info = f.readlines()
    
    info = [line.split('|') for line in info] # Sometimes I'll leave inspection hints in the _INFO.txt file as well

    # Example info line:
    # "Asian Noodle Bowl with Poached Egg|1.5lb udon noodles,4 eggs,4slice bacon,3tbsp soy sauce,2tsp mirin,1tsp sugar,3 green onion|https://some_url"

    def sliceIngredients(ingredients):
        ingredients = ingredients.split(',')
        classed = []
        for ing in ingredients:
            separator = ing.index(' ')
            quantplustype = ing[:separator]
            quant = ''.join(re.compile('[0-9.]+').findall(quantplustype))
            quant = float(quant) if quant != '' else 0
            ingtype = ''.join(re.compile('[a-z]+').findall(quantplustype))
            classed.append( Ingredient(ing[separator+1:].strip('\n'), quant, ingtype) )
            # Had to strip \n because it was keeping it from the end of lines
        return tuple(classed)
    
    info = {line[0]:sliceIngredients(line[1]) for line in info}
    return info

def makeGroceryList(user_request):
    '''Input: [[recipe name, quantity],...]
       Output: A list of [Ingredient obj, ...]'''
    recipes = getInfo()
    ingredientLoc = {}
    ingredientPile = []
    for meal, amount in user_request:
        for ing in recipes[meal]:
            try:
                loc = ingredientLoc[ing.name]
                ingredientPile[loc] += ing * amount
            except:
                ingredientLoc[ing.name] = len(ingredientPile)
                ingredientPile.append(ing * amount)
    return ingredientPile

price_urls = {
    'bacon':[[16,'oz'],'https://www.instacart.com/store/items/item_108973350'],
    'egg noodles':[[12,'oz'],'https://www.instacart.com/store/items/item_108553799'],
    'scallions':[[8,''],'https://www.instacart.com/store/items/item_108484287'],
    'eggs':[[18,''],'https://www.instacart.com/store/items/item_109072924'],
    'ginger':[[1,'lb'],'https://www.instacart.com/store/items/item_108486456'],
    'chicken broth':[[4,'cups'],'https://www.instacart.com/store/items/item_108973920'],
    'cornstarch':[[16,'oz'],'https://www.instacart.com/store/items/item_109085698'],
    'peanut butter':[[40,'oz'],'https://www.instacart.com/store/items/item_109086253'],
    'chili sauce':[[28,'oz'],'https://www.instacart.com/store/items/item_108624011'],
    'rice vinegar':[[12,'oz'],'https://www.instacart.com/store/items/item_109015389'],
    'soy sauce':[[20,'oz'],'https://www.instacart.com/store/items/item_108823742'],
    'peanut oil':[[24,'oz'],'https://www.instacart.com/store/items/item_109098705'],
    'sweet onion':[[1,'lb'],'https://www.instacart.com/store/items/item_108484676'],
    'bell pepper':[[1,''],'https://www.instacart.com/store/items/item_108484343'],
    'honey':[[22,'oz'],'https://www.instacart.com/store/items/item_109064018'],
    'sugar':[[4,'lb'],'https://www.instacart.com/store/items/item_109118803'],
    'carrots':[[1,''],'https://www.instacart.com/store/items/item_108484851'],
    'roasted peanuts':[[16,'oz'],'https://www.instacart.com/store/items/item_108658401'],
    'packet gelatin':[[4,''],'https://www.instacart.com/store/items/item_108852952'],
    'fresh parsley':[[1,''],'https://www.instacart.com/store/items/item_108488110'],
    'egg roll wrappers':[[50,''],'https://www.instacart.com/store/items/item_109128941'],
    'Gruyere cheese':[[6,'oz'],'https://www.instacart.com/store/items/item_123023680'],
    'fresh chives':[[5,'tbsp'],'https://www.instacart.com/store/items/item_108681955'],
    'evaporated milk':[[12,'oz'],'https://www.instacart.com/store/items/item_109072388'],
    'sesame seed':[[1,'oz'],'https://www.instacart.com/store/items/item_108888657'],
    'sesame seeds':[[1,'oz'],'https://www.instacart.com/store/items/item_108888657'],
    'yellow onion':[[1,'lb'],'https://www.instacart.com/store/items/item_108484676'],
    'mirin':[[10,'oz'],'https://www.instacart.com/store/items/item_108495558'],
    'mint':[[1,'lb'],'https://www.instacart.com/store/items/item_108682426'],
    'red bell pepper':[[1,''],'https://www.instacart.com/store/items/item_108484343'],
    'strawberry jam':[[13,'oz'],'https://www.instacart.com/store/items/item_109220408'],
    'fish sauce':[[8.45,'oz'],'https://www.instacart.com/store/items/item_109301773'],
    'garlic cloves':[[18,''],'https://www.instacart.com/store/items/item_109311229'],
    'green bell pepper':[[0.99,''],'https://www.instacart.com/store/items/item_108486791'],
    'arugula':[[5,'oz'],'https://www.instacart.com/store/items/item_602681354'],
    'mango chunks':[[16,'oz'],'https://www.instacart.com/store/items/item_108488582'],
    'rice stick noodles':[[6.75,'oz'],'https://www.instacart.com/store/items/item_108495482'],
    'olive oil':[[16.9,'oz'],'https://www.instacart.com/store/items/item_109062617'],
    'celery stalk':[[10,''],'https://www.instacart.com/store/items/item_109062018'],
    'shrimp':[[1,'lb'],'https://www.instacart.com/store/items/item_109244536'],
    'crimini mushrooms':[[1,'lb'],'https://www.instacart.com/store/items/item_108485597'],
    'cremini mushrooms':[[1,'lb'],'https://www.instacart.com/store/items/item_108485597'],
    'garlic':[[18,''],'https://www.instacart.com/store/items/item_109311229'],
    'chicken':[[1.99,'lb'],'https://www.instacart.com/store/items/item_109245900'],
    'chicken breasts':[[1.99,'lb'],'https://www.instacart.com/store/items/item_109245900'],
    'egg':[[18,''],'https://www.instacart.com/store/items/item_109072924'],
    'cellophane noodles':[[6.75,'oz'],'https://www.instacart.com/store/items/item_108495482'],
    'sesame oil':[[5,'oz'],'https://www.instacart.com/store/items/item_108495659'],
    'peas':[[10,'oz'],'https://www.instacart.com/store/items/item_108546114'],
    'wonton wrappers':[[50,''],'https://www.instacart.com/store/items/item_109129795'],
    'garlic clove':[[18,''],'https://www.instacart.com/store/items/item_109311229'],
    'green onions':[[8,''],'https://www.instacart.com/store/items/item_108484287'],
    'pork shoulder':[[1,'lb'],'https://www.instacart.com/store/items/item_109237473'],
    'raspberries':[[6,'oz'],'https://www.instacart.com/store/items/item_109292833'],
    'cabbage':[[1,''],'https://www.instacart.com/store/items/item_108485738'],
}

###############################
recipes = getInfo()
ing = recipes['Dan Dan Noodles']
for i in ing:
    print(i)
###############################

to_construct = ['Dan Dan Noodles','Egg Drop Soup','Chicken and Ginger Noodle Soup','Easy Egg Fried Rice','Shrimp With Lobster Sauce',
                'Sweet Chili Shrimp','Succulent Shrimp Wontons', 'Easy Sesame Chicken','General Tso\'s Chicken', 'Braised Pork in Soy Sauce',
                'Mango Pudding','Vegetable Egg Rolls']
robot_prices = {'peanut oil': [[24, 'oz'], 3.99],
                'bacon': [[16, 'oz'], 6.99], 
                'ginger': [[1, 'lb'], 2.99], 
                'chicken broth': [[4, 'cups'], 2.79], 
                'chili sauce': [[28, 'oz'], 3.99], 
                'rice vinegar': [[12, 'oz'], 3.99], 
                'soy sauce': [[20, 'oz'], 4.49], 
                'peanut butter': [[40, 'oz'], 4.69], 
                'egg noodles': [[12, 'oz'], 2.69], 
                'roasted peanuts': [[16, 'oz'], 2.99], 
                'scallions': [[8, ''], 0.99],
                'sugar':[[4, 'lb'], 2.49],
                'cornstarch':[[16, 'oz'], 1.29],
                'eggs':[[18, ''], 3.99],
                'garlic': [[18, ''], 1.29],
                'cremini mushrooms': [[1, 'lb'], 3.99],
                'chicken': [[1.99, 'lb'], 1.99],
                'carrots': [[1, ''], 0.99],
                'rice stick noodles': [[6.75, 'oz'], 2.19],
                'sweet onion': [[1, 'lb'], 1.69],
                'sesame oil': [[5, 'oz'], 3.99],
                'garlic cloves': [[18, ''], 1.29],
                'shrimp': [[1, 'lb'], 11.99],
                'peas': [[10, 'oz'], 1.99],
                'cellophane noodles': [[6.75, 'oz'], 2.19],
                'honey': [[22, 'oz'], 7.99],
                'wonton wrappers': [[50, ''], 2.49],
                'egg': [[18, ''], 3.99],
                'garlic clove': [[18, ''], 1.29],
                'sesame seeds': [[1, 'oz'], 1.09],
                'pork shoulder': [[1, 'lb'], 1.99],
                'mango chunks': [[16, 'oz'], 1.99],
                'packet gelatin': [[4, ''], 2.49],
                'evaporated milk': [[12, 'oz'], 0.99],
                'raspberries': [[6, 'oz'], 3.99],
                'celery stalk': [[10, ''], 1.99],
                'cabbage': [[1, ''], 1.83],
                'egg roll wrappers': [[50, ''], 2.49]
                }

def obtain_needed(needed):
    ''' Updates robot_prices with needed ingredients '''
    if needed == []:
        return # No further action required

    ### 0. Definitions for login/browsing
    login_url = 'https://www.instacart.com/#login'
    browser = webdriver.Chrome('/home/order/Videos/chromedriver/chromedriver') # Linux
    find_css = browser.find_element_by_css_selector
    find_xpath = browser.find_element_by_xpath

    ### 1. Login into Instacart account
    browser.get(login_url)
    browser.implicitly_wait(2)
    username_box = find_css('#login_with_password_form_email')
    password_box = find_css('#login_with_password_form_password')
    username_box.send_keys('snore001@ucr.edu')
    password_box.send_keys('Ww9H3MbZUze4jhR')
    sleep(1) # So it doesn't look like I'm a robot
    submit_button = find_xpath('//*[@id="signup-widget"]/div/div/div/div[4]/form/div/button')
    submit_button.click()
    sleep(2) # Let the submission be sent to the server
    priceloc = '//*[@id="react-views-container"]/div/div/div/div[1]/div/div/div/div[1]/div/div[3]/div[1]/div/div/div[1]/span[2]'
    for ing in needed:
        ### TODO: Implement price cooldown
        if ing.name not in IGNORE:
            ingData = price_urls[ing.name]
            browser.get(ingData[1])
            browser.implicitly_wait(4)
            price = find_xpath(priceloc)

            nums = set('0123456789.')
            robot_prices[ing.name] = [ingData[0],float(''.join([x for x in price.text if x in nums]))]
            print(repr(ing.name) + str(':'),str(robot_prices[ing.name]) + ',')

recipes = getInfo()
ingprice_per_recipe = dict() # { Recipe name: {ingname: price, ...}, ... }
IGNORE = {'sichuan peppercorns', 'salt', 'pepper', 'black pepper', 'sea salt', 'cinnamon', 'pinch black pepper', 
          'black pepper ', 'black bean sauce', 'udon noodles', 'minced garlic', 'rice', 'white pepper', 'Shaoxing rice wine',
          'raspberries'}
for recipe in to_construct:
    ingList = list(recipes[recipe]) # Output is a tuple; I need a mutable list
    newIngList = []
    # Remove ignore ingredients
    for index, ing in enumerate(ingList):
        if ing.name not in IGNORE:
            newIngList.append(ing)
    
    needed = [x for x in newIngList if x.name not in robot_prices]
    obtain_needed(needed) # Looks up everything not already in robot_prices for the given recipe
    # ingredient_objects ####################
    storeList = []
    for ing in newIngList:
        store_qdata = robot_prices[ing.name][0]
        storeList.append( Ingredient(ing.name, store_qdata[0], store_qdata[1]) )
    ingprice_per_recipe[recipe] = {ing.name: ing / storeIng * robot_prices[ing.name][1] for ing,storeIng in zip(newIngList,storeList)}

with open('recipePrice.txt','w') as f:
    f.write('Prices compiled on',str(datetime.today))

for i in ingprice_per_recipe:
    print('--------------------------------')
    print('{:<24} {}'.format(i,round(sum([ingprice_per_recipe[i][x] for x in ingprice_per_recipe[i]]),2)))
    sorted_ing_costs = sorted(ingprice_per_recipe[i],key=lambda x: ingprice_per_recipe[i][x], reverse=True)
    for subIng in sorted_ing_costs:
        print('    ','{:<20} {}'.format(subIng, round(ingprice_per_recipe[i][subIng],2)))
    
    with open('recipePrice.txt','r') as f: # Copy of the above, but write to file instead
        f.write('--------------------------------\n')
        f.write('{:<24} {}'.format(i,round(sum([ingprice_per_recipe[i][x] for x in ingprice_per_recipe[i]]),2)) + '\n')
        for subIng in sorted_ing_costs:
            f.write('    ','{:<20} {}'.format(subIng, round(ingprice_per_recipe[i][subIng],2)) + '\n')