# Some ingredients are liquid, some are not.
# This file is intended to gather that information from the user
#     as new recipes are input.

import json

with open('recipedata.json', 'r') as f:
    db = json.load(f)

uniqueing = set()

for recipe in db:
    for ing in db[recipe]['ingredients']:
        uniqueing.add(ing)

with open('ingdata.json', 'r') as f:
    existing = json.load(f)

uniqueing -= set(existing)

print('For each of the following ingredients, enter 1 if the ingredient')
print('  is not a liquid and 2 if it is. Any other entry will halt the program.')
uniqueorder = list(uniqueing)
for ing in uniqueorder:
    res = input(f'{ing}? ')
    if res in ('1', '2'):
        if res == '1':
            state = False
        else:
            state = True
        
        existing[ing] = {
            'liquid': state
        }
    else:
        break

with open('ingdata.json', 'w') as f:
    json.dump(existing, f, indent=4)
