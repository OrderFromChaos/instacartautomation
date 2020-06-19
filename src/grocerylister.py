from ingredient import Ingredient
import json

def generateGroceryList(request):
    with open('../databases/recipedata.json', 'r') as f:
        db = json.load(f)

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
                    raise Exception(f'Old:\n{ingredients[ing]}\nNew:\n{ingobj}')
            else:
                ingredients[ing] = ingobj
    
    return ingredients

if __name__ == "__main__":
    request = [
        ['Egg Drop Soup', 2],
        ['Orange French Toast', 2],
        ['Asian Noodle Bowl with Poached Egg', 2],
        ['Eggs Blackstone', 1]
    ]

    ingredients = generateGroceryList(request)

    for ing, obj in ingredients.items():
        print('{:<20} {} {}'.format(obj.name, round(obj.quantity, 2), obj.qtype))