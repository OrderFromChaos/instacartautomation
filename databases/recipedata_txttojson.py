# Dan Dan Noodles|1tbsp peanut oil,16oz bacon,3tbsp ginger,1.125cups chicken broth,3tbsp chili sauce,1.5tbsp rice vinegar,3tbsp soy sauce,3tbsp peanut butter,1.5tsp sichuan peppercorns,pinch salt,pinch pepper,12oz egg noodles,0.5oz roasted peanuts,4.5 scallions
# Sweet Chili Shrimp|8oz cellophane noodles,1lb shrimp,2tsp cornstarch,0.5tsp salt,0.25tsp black pepper,1tbsp soy sauce,1tbsp honey,1tbsp rice vinegar,2tbsp chili sauce,1tbsp Shaoxing rice wine,1tbsp peanut oil,2tbsp minced garlic,1tsp ginger
# Shrimp With Lobster Sauce|2tbsp peanut oil,3 garlic cloves,16oz shrimp,4tsp Shaoxing rice wine,2cups chicken broth,0.5tsp sesame oil,0.66tsp sugar,0.66tsp salt,pinch white pepper,0.66cups peas,4tsp cornstarch,2 eggs,2 scallions
# Egg Drop Soup|6cups chicken broth,1tsp Shaoxing rice wine,0.25tsp ginger,1tsp sugar,0.25tsp white pepper,1tbsp cornstarch,2 eggs,pinch salt,1 scallions

# This should be converted to json for readability/ease of access

# fmt:
# [
#   "Dan Dan Noodles": {
#     "ingredients": [
#       ["peanut oil", 1, "tbsp"],
#       ["bacon", 16, "oz"],
#       ...
#     ],
#     (could include subjective rating, etc. here, good for extensibility)
#   },
#   ...
# ]

import re
import json

with open('recipedata.txt', 'r') as f:
    lines = f.readlines()

findict = dict()
infore = re.compile('(\d+)(\.\d+)?(\w+)? (.+)')

for line in lines:
    separated = line.split('|')
    recipename = separated[0]
    inglist = separated[1]
    # There are comments sometimes in later | paritions; ignore these

    linedict = dict()
    linedict['ingredients'] = dict()
    for ing in inglist.split(','):
        m = re.match(infore, ing)
        if not m:
            temp = ing.split(' ')
            if temp[0] == 'pinch':
                linedict['ingredients'][' '.join(temp[1:]).strip()] = {
                    'quantity': 1,
                    'qtype': 'pinch'
                }
            else:
                raise Exception(f"Ingredient parsing failed on \"{ing}\"")
        else:
            cap = list(m.groups())
            if cap[1] == None:
                cap[1] = '.0'
            if cap[2] == None:
                cap[2] = ''
            # cap example:
            # ('8', '0', 'oz', 'cellophane noodles')
            linedict['ingredients'][cap[3].strip()] = {
                'quantity': float(f'{cap[0]}{cap[1]}'),
                'qtype': cap[2]
            }
    
    findict[recipename] = linedict

with open('recipedata.json', 'w') as f:
    json.dump(findict, f, indent=4)

# print(json.dumps(findict, indent=4))