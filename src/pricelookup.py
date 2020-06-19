from grocerylister import generateGroceryList

PRICECOOLDOWN = 12*60 # 12 hrs (minutes)

def updatePrices(inglist):
    # Updates products outside of the PRICECOOLDOWN range

    pass

def computePrice(inglist):
    # Actually does the computation and adds everything together
    # Some ingredients are usually used in pinch quantities and don't
    #     really make sense to compute. Or they might be on a non-instacart
    #     site, which this code doesn't support. Here they are:
    IGNORE = {
        'sichuan peppercorns', # non-Instacart
        'salt', # pinch
        'pepper', # pinch
        'black pepper', #pinch
        'sea salt' # pinch
    }

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