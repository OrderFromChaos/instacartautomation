from ingredient import Ingredient
import json

request = [
    ['Egg Drop Soup', 2],
    ['Orange French Toast', 2],
    ['Asian Noodle Bowl with Poached Egg', 2],
    ['Eggs Blackstone', 1]
]

with open('../databases/recipedata.json', 'r') as f:
    db = json.load(f)

request = [[x,1] for x in list(db) if x not in ["Pineapple Fried Rice",
            "Breakfast Burrito", "Velvet Chicken", "Easy Egg Fried Rice",
            "General Tso's Chicken", "Easy Sesame Chicken", "Twice-Cooked Pork"]]
# Traceback (most recent call last):
#   File "grocerylister.py", line 34, in <module>
#     ingredients[ing] += ingobj
#   File "/home/order/Dropbox/Python_Code/Utility/Meal_Planning/src/ingredient.py", line 100, in __add__
#     self.quantity += other.quantity
# AttributeError: 'NoneType' object has no attribute 'quantity'

# Exception: sweet onion
# Exception: chicken
# Exception: garlic

with open('../databases/ingdata.json', 'r') as f:
    ingdata = json.load(f)

ingredients = dict()

for recipe, quant in request:
    print(recipe)
    for ing in db[recipe]['ingredients']:
        data = db[recipe]['ingredients'][ing]
        ingobj = Ingredient(
            name=ing,
            quantity=data['quantity']*quant,
            qtype=data['qtype'],
            liquid=ingdata[ing]['liquid']
        )
        if ing in ingredients:
            try:
                ingredients[ing] += ingobj
            except AttributeError:
                raise Exception(f'{ing}')
        else:
            ingredients[ing] = ingobj

for ing, obj in ingredients.items():
    print('{:<20} {} {}'.format(obj.name, round(obj.quantity, 2), obj.qtype))