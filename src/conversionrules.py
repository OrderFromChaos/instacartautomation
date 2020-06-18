# liquids need to be treated differently to non-liquids
# some solids are regularly converted between measures (eg ginger)
#    and need special conversions
# conversions need to work both ways (tsp -> tbsp, tbsp -> tsp)
# some quantities are preferred for human convenience/purchasing

# TODO: Allow for grams (g)

from collections import defaultdict # emulates C++ multimap

# Source: https://www.foodnetwork.ca/kitchen-basics/blog/your-ultimate-guide-to-cooking-and-baking-conversions/

special_ingredients = {
    'ginger',
    'peanut butter',
    'garlic',
    'sugar',
    'sweet onion',
    'yellow onion'
}
# dict of string: defaultdict
special_rules = {i: defaultdict(list) for i in special_ingredients}

# Source: personal experience
special_rules['ginger']['lb'].append(('tbsp', 20))
# TODO: Add "inches" of ginger

# Source: old code
special_rules['peanut butter']['oz'].append(('tbsp', 1.77))
special_rules['garlic'][''].append(('tbsp', 3))
special_rules['sweet onion']['lb'].append(('', 2))
special_rules['yellow onion']['lb'].append(('', 2))

# Source: above foodnetwork link
special_rules['sugar']['tbsp'].append(('lb', 7/16/16))
special_rules['sugar']['tsp'].append(('lb', 7/16/16/3))
special_rules['sugar']['cup'].append(('lb', 7/16))

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

print(liquid_rules)

# Reverse all dictionaries so they work in the opposite order
for entry, to in list(liquid_rules.items()):
    for conv in to:
        liquid_rules[conv[0]] = (entry, 1/conv[1])
for entry, to in list(general_rules.items()):
    for conv in to:
        general_rules[conv[0]] = (entry, 1/conv[1])

for ing in list(special_rules):
    for entry, to in list(special_rules[ing].items()):
        print(entry, to)
        for conv in to:
            special_rules[ing][conv[0]] = (entry, 1/conv[1])

print(liquid_rules)
print(special_rules)