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

findict = dict()

with open('recipedata.txt', 'r') as f:
    lines = f.readlines()

for line in lines:
    recipename, inglist = line.split('|')
    for ing in inglist.split(','):
        infore = re.compile('(\d+)(\.\d+)?(\w+) (.+)')
        match = re.match(ing)
        if not match:
            raise Exception(f"Ingredient parsing failed on \"{ing}\"")
        else:
            