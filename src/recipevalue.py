from grocerylister import generateGroceryList
from pricelookup import computePrice
import json

# Hyperparams
hourlyrate = 3 # in dollars

with open('../databases/recipedata.json', 'r') as f:
    recipes = json.load(f)

with open('../databases/recipemeta.json', 'r') as f:
    recipemeta = json.load(f)

pairs = []

for r in recipes:
    request = [[r, 1]]

    ingredients = generateGroceryList(request)
    itemized = computePrice(ingredients, "stater bros")

    pairs.append([
        r, 
        round(sum(x for x in itemized.values()), 2)
    ])

    if recipemeta[r]['reviewed']:
        meals = recipemeta[r]['meals']
        time = recipemeta[r]['time']
        rating = recipemeta[r]['rating']
        pairs[-1].extend([
            round(pairs[-1][1]/meals, 2),
            round(meals*rating/(hourlyrate*time/60+pairs[-1][1]), 2)
        ])
    else:
        pairs[-1].extend([0, 0])

    # print('{:<40} {}'.format(r, round(sum(x for x in itemized.values()), 2)))

pairs.sort(key=lambda x: x[1], reverse=True)

for p in pairs:
    print('{:<40} {:<7} {:<7} {:<7}'.format(*p))
