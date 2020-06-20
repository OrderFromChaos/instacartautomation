# liquids need to be treated differently to non-liquids
# some solids are regularly converted between measures (eg ginger)
#    and need special conversions
# conversions need to work both ways (tsp -> tbsp, tbsp -> tsp)
# some quantities are preferred for human convenience/purchasing

# TODO: Support grams (g)
# TODO: Support gallons/pints
# TODO: Rewrite to be a graph so no need to convert 
#         lb->tbsp to lb->tsp for special items (for example)

from collections import defaultdict # emulates C++ multimap

# Source: https://www.foodnetwork.ca/kitchen-basics/blog/your-ultimate-guide-to-cooking-and-baking-conversions/

# Preferred for categories
liquid_preferred = 'oz'
specific_preferred = {
    'ginger': 'lb',
    'peanut butter': 'oz',
    'garlic': '',
    'sugar': 'lb',
    'sweet onion': '',
    'yellow onion': '',
    'bacon': 'oz',
    'cremini mushrooms': 'lb',
    'chicken': 'lb',
    'white pepper': 'oz',
    'cornstarch': 'oz',
    'scallions': '',
    'minced garlic': 'oz',
    'garlic cloves': '',
    'peas': 'oz',
    'bean sprouts': 'oz',
    'egg roll wrappers': '',
    'sweet corn': 'oz',
    'rice': 'lb',
    'pineapple': 'lb',
    'cashews': 'oz',
    'broccoli florets': 'oz',
    'green beans': 'oz',
    'cinnamon': 'oz',
    'sesame seeds': 'oz',
    'shredded cheese': 'oz',
    'raspberries': 'oz container', # workaround
    'milk': 'gal',
    'white bread': 'oz',
    'wonton wrappers': 'oz',
    'chicken breasts': 'lb',
    'shallots': 'item',
    'medium tomatoes': 'lb',
    'whole milk': 'gal',
    'fresh basil': 'each',
    'fresh parsley': 'bunch',
    'Gruyere cheese': 'oz',
    'cherry tomatoes': 'lb',
    'arugula': 'oz container',
    'fresh mint': 'oz',
    'fresh chives': 'each',
    'ground cumin': 'oz',
    'smoked paprika': 'oz',
    'red pepper flakes': 'oz',
    'farro': 'oz',
    'tomato': 'lb',
    'thyme': 'oz',
    'country bread': 'oz'
}

special_ingredients = {
    'ginger',
    'peanut butter',
    'garlic',
    'sugar',
    'sweet onion',
    'yellow onion',
    'bacon',
    'cremini mushrooms',
    'chicken',
    'white pepper',
    'cornstarch',
    'scallions',
    'minced garlic',
    'garlic cloves',
    'peas',
    'bean sprouts',
    'egg roll wrappers',
    'sweet corn',
    'rice',
    'pineapple',
    'cashews',
    'broccoli florets',
    'green beans',
    'cinnamon',
    'sesame seeds',
    'shredded cheese',
    'raspberries',
    'milk',
    'white bread',
    'wonton wrappers',
    'chicken breasts',
    'shallots',
    'medium tomatoes',
    'whole milk',
    'fresh basil',
    'fresh parsley',
    'Gruyere cheese',
    'cherry tomatoes',
    'arugula',
    'fresh mint',
    'fresh chives',
    'ground cumin',
    'smoked paprika',
    'red pepper flakes',
    'farro',
    'tomato',
    'fresh thyme',
    'country bread'
}
# dict of string: defaultdict
special_rules = {i: defaultdict(list) for i in special_ingredients}

# Source: personal experience
special_rules['ginger']['lb'].append(('tbsp', 20))
special_rules['ginger']['lb'].append(('tsp', 60))
special_rules['ginger']['lb'].append(('cup', 20/16))
# TODO: Add "inches" of ginger
special_rules['scallions']['bunch'].append(('', 4))
special_rules['fresh basil']['each'].append(('tbsp', 7)) # guesstimate
special_rules['fresh parsley']['bunch'].append(('tbsp', 6)) # guesstimate
special_rules['fresh mint']['oz'].append(('tbsp', 4*4))
special_rules['fresh mint']['oz'].append(('tsp', 4*4*3))
special_rules['fresh chives']['each'].append(('tsp', 4*3))
special_rules['fresh thyme']['oz'].append(('tsp', 4*4*3))

# Source: old code
special_rules['peanut butter']['oz'].append(('tbsp', 1.77))
special_rules['garlic'][''].append(('tbsp', 3))
special_rules['garlic'][''].append(('tsp', 9))
special_rules['garlic'][''].append(('clove', 10))
special_rules['sweet onion']['lb'].append(('', 2))
special_rules['yellow onion']['lb'].append(('', 2))

# Source: above foodnetwork link
special_rules['sugar']['tbsp'].append(('lb', 7/16/16))
special_rules['sugar']['tsp'].append(('lb', 7/16/16/3))
special_rules['sugar']['cup'].append(('lb', 7/16))

# Source: http://www.cookitsimply.com/measurements/cups/bacon-raw-chopped-diced-0070-02b0.html
special_rules['bacon']['cup'].append(('oz', 8))
special_rules['bacon']['slice'].append(('oz', 1))

# Source: https://www.thespruceeats.com/mushroom-equivalents-measures-and-substitutions-1807471
special_rules['cremini mushrooms']['cup'].append(('', 4))
special_rules['cremini mushrooms']['oz'].append(('', 24/16))
special_rules['cremini mushrooms']['lb'].append(('', 24))

# Source: https://www.atcoblueflamekitchen.com/en-ca/how-to/cups-medium-large-onion.html
special_rules['sweet onion'][''].append(('cup', 2))

# Source: https://www.aqua-calc.com/calculate/food-volume-to-weight
special_rules['white pepper']['oz'].append(('tsp', 42.25/3.53))
special_rules['cornstarch']['oz'].append(('tbsp', 0.12))
special_rules['cornstarch']['oz'].append(('tsp', 0.12*3))
special_rules['minced garlic']['oz'].append(('tbsp', 16/8.47))
special_rules['peas']['cup'].append(('oz', 6.35))
special_rules['bean sprouts']['cup'].append(('oz', 8.11))
special_rules['bean sprouts']['cup'].append(('oz bag', 8.11))
special_rules['bean sprouts']['oz bag'].append(('oz', 1))
special_rules['sweet corn']['cup'].append(('oz', 4.76))
special_rules['rice']['cup'].append(('lb', 0.49))
special_rules['pineapple']['item'].append(('lb', 4.16))
special_rules['pineapple']['cup'].append(('lb', 0.55))
special_rules['pineapple']['item'].append(('cup', 4.16*2))
special_rules['cashews']['cup'].append(('oz', 5.27))
special_rules['broccoli florets']['cup'].append(('oz', 2.57))
special_rules['green beans']['cup'].append(('oz', 2.93))
special_rules['cinnamon']['tsp'].append(('oz', 5.42/48))
special_rules['sesame seeds']['tsp'].append(('oz', 9.03/48))
special_rules['shredded cheese']['tbsp'].append(('oz', 3.95/16))
special_rules['milk']['gal'].append(('oz', 45.5))
special_rules['whole milk']['gal'].append(('oz', 45.5))
special_rules['Gruyere cheese']['cup'].append(('oz', 7.64))
special_rules['cherry tomatoes']['cup'].append(('lb', 0.33))
special_rules['arugula']['cup'].append(('oz container', 0.71))
special_rules['smoked paprika']['tsp'].append(('oz', 3.84/48))
special_rules['red pepper flakes']['tsp'].append(('oz', 2.99/48))
special_rules['farro']['cup'].append(('oz', 4.77))

# Source: https://grocery.walmart.com/ip/Wonder-Classic-White-Bread-20-oz-Loaf/37858875
special_rules['white bread']['oz'].append(('slices', 1))

# Source: https://www.seriouseats.com/2012/10/ask-the-food-lab-on-sizing-shallots-and-frying-curry.html#:~:text=1%20Large%20Shallot%20%3D%201%2F2,2%20tablespoons%20minced%20or%20sliced
special_rules['shallots']['item'].append(('tbsp', 4)) # assuming medium shallot

# Source: https://www.thespruceeats.com/tomato-equivalents-1807482
special_rules['medium tomatoes']['lb'].append(('', 3))
special_rules['tomato']['lb'].append(('', 3))

# Source: https://www.alliedkenco.com/pdf/Spice%20Conversions.pdf
special_rules['ground cumin']['oz'].append(('tbsp', 4))
special_rules['ground cumin']['oz'].append(('tsp', 4*3))

# Source: ????
special_rules['chicken']['cup'].append(('lb', 5.25/16))
special_rules['garlic cloves']['count bag'].append(('', 3*10))
special_rules['egg roll wrappers']['oz'].append(('', 50/18))
special_rules['raspberries']['pinch'].append(('oz container', 2)) # workaround for raspberries
special_rules['wonton wrappers']['oz'].append(('', 40/14))
special_rules['chicken breasts']['lb'].append(('', 2))
special_rules['country bread']['oz'].append(('', 15/22))

# defaultdict
liquid_rules = defaultdict(list)
liquid_rules['oz'].append(('tbsp', 2))
liquid_rules['oz'].append(('tsp', 6))
liquid_rules['oz'].append(('cup', 1/8))
liquid_rules['fl oz'].append(('oz', 1))
liquid_rules['oz']

# defaultdict
# keep same unit type, like volume -> volume

general_rules = defaultdict(list)
general_rules['tbsp'].append(('tsp', 3))
general_rules['lb'].append(('oz', 16))
general_rules['cup'].append(('tbsp', 16))
general_rules['ct'].append(('', 1))
general_rules['item'].append(('', 1))
general_rules['count bag'].append(('', 1))
general_rules['each'].append(('', 1))

general_rules['pinch'].append(('tsp', 0))
general_rules['pinch'].append(('tbsp', 0))
general_rules['pinch'].append(('cup', 0))
general_rules['pinch'].append(('oz', 0))
general_rules['pinch'].append(('', 0))

if __name__ == "__main__":
    print(general_rules)
    print(liquid_rules)

# Reverse all dictionaries so they work in the opposite order
for entry, to in list(liquid_rules.items()):
    for conv in to:
        liquid_rules[conv[0]].append((entry, 1/conv[1] if conv[1] != 0 else 0))
for entry, to in list(general_rules.items()):
    for conv in to:
        general_rules[conv[0]].append((entry, 1/conv[1] if conv[1] != 0 else 0))

for ing in list(special_rules):
    for entry, to in list(special_rules[ing].items()):
        for conv in to:
            special_rules[ing][conv[0]].append((entry, 1/conv[1] if conv[1] != 0 else 0))

if __name__ == "__main__":
    print(special_rules)
    print(liquid_rules)
    print(general_rules)


specific_preferred = {
    'ginger': 'lb',
    'peanut butter': 'oz',
    'garlic': '',
    'sugar': 'lb',
    'sweet onion': '',
    'yellow onion': '',
    'bacon': 'oz',
    'cremini mushrooms': '',
    'chicken': 'lb',
    'white pepper': 'oz',
    'cornstarch': 'oz',
    'scallions': '',
    'minced garlic': 'oz'
}
# TODO: Rewrite Ingredient class to still call this without SPECIALFLAG