import re

addrules = [
    # Format:
    # (type1, type2), number, when_allowed
    # Examples:
    # ('tbsp', 'tsp'), 3, ('any')
    # ('lb', 'tbsp'), 16, ('ginger')
    # List is searched through from top to bottom and first match works, so put all specific ones at the top
    # Leftmost qtype is given priority and all units will be converted to it during addition
    (('lb','tbsp'),16,('ginger')),
    (('oz','tbsp'),1.77,('peanut butter')),
    (('oz','tbsp'),2,('any')),
    (('tbsp','tsp'),3,('any')),
    (('cups','oz'),8,('any')),
    (('lb','oz'),16,('any'))
]

class Ingredient:
    def __init__(self, name='', quantity=0, qtype=''):
        self.name = name
        self.quantity = quantity
        self.qtype = qtype
    def __add__(self,other):
        # Intelligently deal with stuff
        assert type(other) == Ingredient, 'Can only add together two Ingredient objects'
        assert self.name == other.name, 'Cannot add together two different ingredients: (' + self.name + ') AND (' + other.name + ')'
        if self.qtype == other.qtype: # Easy!
            return Ingredient(self.name,self.quantity+other.quantity,self.qtype)
        else: # Harder. Needs unit conversion.
            conversions = {(self.qtype,other.qtype),(other.qtype,self.qtype)} # So you can get both directions (tbsp -> tsp) and (tsp -> tbsp)
            for rule in addrules:
                if rule[0] in conversions and ('any' in rule[2]  or  self.name in rule[2]): # Correct conversion (tbsp -> tsp) and allowed for type of ingredient
                    relevant_rule = rule
                    break
            else: # Runs only if no conversion was found
                raise Exception('Failed to add together (' + self.name + ') AND (' + other.name + ') due to quant type mismatch: (' + self.qtype + ') AND (' + other.qtype + ')')
            
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
                raise Exception('Failed to divide (' + self.name + ') due to quant type mismatch: (' + self.qtype + ') AND (' + bottom.qtype + ')')
            
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
    'cabbage':[[1,''],'https://www.instacart.com/store/items/item_108485738']
}

recipes = getInfo()
for i in recipes:
    print(i)

NOT_INTERESTED = {'Vinegar-Glazed Chinese Cabbage',
                  'Hot and Sour Vegetable Soup',
                  'Teriyaki Turkey Rice Bowl',
                  'Stir-Fried Eggs with Tomato',
                  'Poached Eggs'}

newrecipes = dict()
for rec in recipes:
    if rec not in NOT_INTERESTED:
        newrecipes[rec] = recipes[rec]

allingredients = makeGroceryList([[x, 1] for x in list(newrecipes)])

IGNORE = {'sichuan peppercorns', 'salt', 'pepper', 'black pepper', 'sea salt', 'cinnamon', 'pinch black pepper', 
          'black pepper ', 'black bean sauce', 'udon noodles', 'minced garlic', 'rice', 'white pepper', 'Shaoxing rice wine',
          }
newingredients = []
for ing in allingredients:
    if ing.name not in IGNORE:
        newingredients.append(ing)

not_accounted = set()
for ing in newingredients:
    if ing.name not in price_urls:
        not_accounted.add(ing.name)

for na in not_accounted:
    print('No URL for:',repr(na))

# Find all possible recipes
print('----------------------------------------')
included_ings = IGNORE | set(list(price_urls))
for rec in recipes:
    if all([ing.name in included_ings for ing in recipes[rec]]):
        print('ALLOWED RECIPE:',rec)
    else:
        print('Disallowed recipe:',rec)
        print('    ',[ing.name for ing in recipes[rec] if ing.name not in included_ings])