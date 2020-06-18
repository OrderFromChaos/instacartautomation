from fuzzywuzzy import fuzz # Implements Levenshtein Distance
import json
from itertools import islice

# Step 1: Find similar (likely mistyped) ingredients in recipedata.json

with open('../databases/recipedata.json', 'r') as f:
    db = json.load(f)

uniqueing = set()

for recipe in db:
    for ing in db[recipe]['ingredients']:
        uniqueing.add(ing)

order = list(uniqueing)
first = True
for index, s1 in enumerate(order):
    for s2 in islice(order, index+1, None):
        similarity = fuzz.ratio(s1, s2)
        if similarity > 85:
            if first:
                print('[Warning] Similarly named ingredients, potential typos:')
                first = False
            print(f'    {similarity} | "{s1}" | "{s2}"')

if first:
    print('No similarly named ingredients found.')

# Step 2: Find ingredients or recipes without metadata
# TODO

# Step 3: ???
# TODO
