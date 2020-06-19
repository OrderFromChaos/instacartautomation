from grocerylister import generateGroceryList

PRICECOOLDOWN = 12*60 # 12 hrs (minutes)

def updatePrices(inglist):
    # Updates products outside of the PRICECOOLDOWN range

    pass

if __name__ == "__main__":

    # Generate a list to work with
    request = [
        ['Egg Drop Soup', 2],
        ['Orange French Toast', 2],
        ['Asian Noodle Bowl with Poached Egg', 2],
        ['Eggs Blackstone', 1]
    ]
    ingredients = generateGroceryList(request)
    updatePrices(ingredients)

# New ingdata.json format:
#   "ground cumin": {
#       "liquid": false,
#       "priceurls": {
#           "stater bros": [
#               "https://youtu.be/9nPVkpWMH9k"
#           ],
#           "ralphs": [
# 
#           ]
#       },
#       "price": {
#           "current": 4.56,
#           "date": <some date format, dunno>
#       }
#   },