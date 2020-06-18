

import json

# Step 1: Find similar (likely mistyped) ingredients in recipedata.json

# TODO: Write implementation

with open('recipedata.json', 'r') as f:
    db = json.load(f)

uniqueing = set()

for recipe in db:
    for ing in db[recipe]['ingredients']:
        uniqueing.add(ing)

print(uniqueing)

# Step 2: Find ingredients or recipes without metadata
# TODO

# Step 3: 
# TODO
