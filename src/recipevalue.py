from grocerylister import generateGroceryList
from pricelookup import computePrice
import json

# Hyperparams
hourlyrate = 3 # in dollars

with open('../databases/recipedata.json', 'r') as f:
    recipes = json.load(f)

pairs = []

for r in recipes:
    request = [[r, 1]]

    ingredients = generateGroceryList(request)
    itemized = computePrice(ingredients, "stater bros")

    pairs.append((r, round(sum(x for x in itemized.values()), 2)))

    # print('{:<40} {}'.format(r, round(sum(x for x in itemized.values()), 2)))

pairs.sort(key=lambda x: x[1], reverse=True)

for p in pairs:
    print('{:<40} {}'.format(*p))