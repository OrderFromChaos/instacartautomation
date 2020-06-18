# liquids need to be treated differently to non-liquids
# some solids are regularly converted between measures (eg ginger)
#    and need special conversions
# conversions need to work both ways (tsp -> tbsp, tbsp -> tsp)
# some quantities are preferred for human convenience/purchasing

# TODO: Support grams (g)
# TODO: Support gallons/pints

from collections import defaultdict # emulates C++ multimap

# Source: https://www.foodnetwork.ca/kitchen-basics/blog/your-ultimate-guide-to-cooking-and-baking-conversions/

special_ingredients = {
    'ginger',
    'peanut butter',
    'garlic',
    'sugar',
    'sweet onion',
    'yellow onion',
    'bacon',
    'cremini mushrooms',
    'chicken'
}
# dict of string: defaultdict
special_rules = {i: defaultdict(list) for i in special_ingredients}

# Source: personal experience
special_rules['ginger']['lb'].append(('tbsp', 20))
special_rules['ginger']['lb'].append(('tsp', 60))
special_rules['ginger']['lb'].append(('cup', 20/16))
# TODO: Add "inches" of ginger

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

# Source: https://www.atcoblueflamekitchen.com/en-ca/how-to/cups-medium-large-onion.html
special_rules['sweet onion'][''].append(('cup', 2))

special_rules['chicken']['cup'].append(('lb', 5.25/16))

# defaultdict
liquid_rules = defaultdict(list)
liquid_rules['oz'].append(('tbsp', 2))
liquid_rules['oz'].append(('tsp', 6))
liquid_rules['oz'].append(('cup', 1/8))

# defaultdict
# keep same unit type, like volume -> volume

general_rules = defaultdict(list)
general_rules['tbsp'].append(('tsp', 3))
general_rules['lb'].append(('oz', 16))
general_rules['cup'].append(('tbsp', 16))

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
    'peanut butter': 'lb',
    'garlic': '',
    'sugar': 'lb',
    'sweet onion': '',
    'yellow onion': '',
    'bacon': 'oz',
    'cremini mushrooms': '',
    'chicken': 'lb'
}
# TODO: Rewrite Ingredient class to still call this without SPECIALFLAG

liquid_preferred = 'oz'