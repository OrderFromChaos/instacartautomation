
# Gives a high level interface to grocery list making.

def checkMenu():
    '''Prints all available recipes'''
    info = getInfo()
    for i,x in enumerate(info):
        print(str(i+1) + '. ' + str(x[0]))

def getInfo():
    '''Pulls from grocery info, which is formatted as recipe|ingredient 1,ingredient 2,...
    Output is a list of [recipe name,[[quantity,ingredient name 1],[quantity,ingredient name 2]]]'''
    with open('./_INFO.txt','r') as f:
        info = f.readlines()
        info = [line.split('|') for line in info] # Sometimes I'll leave inspection hints in the _INFO.txt file as well
        
        def sliceIngredients(ingredients):
            ingredients = ingredients.split(',')
            ingredients = [[x[:x.index(' ')],x[x.index(' ')+1:].strip('\n')] for x in ingredients]
            # Had to strip \n because it was keeping it from the end of lines
            return ingredients
        info = [[line[0],sliceIngredients(line[1])] for line in info]
        
    return info

def toIngredients(user_request):
    '''Takes in a list of [recipe name, quantity]
    Looks up ingredients in _INFO.txt, gets ingredients and adds them together.
    If it can\'t find a recipe, it will output that as an error, but will continue adding the rest of the recipes together.'''
    print('Total meals requested: ' + str(sum([x[1] for x in user_request])))
    info = getInfo() # Get "meal name":[ingredient list] 
    master_meals = [x[0] for x in info]
    ingredients, amounts, errors = [],[],[] # First one is list of strings, second is list of lists (of strings)
    
    # Expand (for example) 5 dan dan noodles to a 5 long list of ['dan dan noodles','dan dan noodles',...]
    # This is easier than trying to multiply the number parts of the ingredients
    new = []
    for meal in user_request:
        new += [[meal[0],1]]*meal[1]
    user_request = new
    
    for meal in user_request: # Check if meals are in the master meal list
        if meal[0] in master_meals: # If they are...
            loc = master_meals.index(meal[0])
            for part in info[loc][1]: # Put the ingredients on the amounts array. (part being ['18oz','ground pork'])
                if part[1] in ingredients:
                    amounts[ingredients.index(part[1])].append(part[0])
                else:
                    ingredients.append(part[1])
                    amounts.append([part[0]])
        else: # If they aren't, add them to the errors list.
            errors.append(meal[0])
    
    print('Finished looking up ingredients!\nLookup errors: ' + str(len(errors)))
    if len(errors) > 0:
        print(errors)
    
    return ingredients,amounts,errors

def unit_sum(amounts):
    '''Input: amounts list from toIngredients()
    Output: ingredient quantity sum list, in best quantity mentioned. Rounds to 2 decimal places in end.'''
    def quantity_unit(amounts): # Technically not good practice, but I don't modify the amounts list
        '''Splits list of ['1tbsp',...] into [[1,'tbsp'],...]
        Technically, it\'s doing the entire amounts array from toIngredients(), which adds a bit of additional complexity.'''
        numbers = {'0','1','2','3','4','5','6','7','8','9','.'} # Decimal place so it properly deals with '0.25'
        # These next lines could potentially be a bit confusing, but it's just creating a blank list for each ingredient value in the amounts list.
        # These lists will be later be replaced by lists like [1,'tbsp']
        sub_lengths = [len(x) for x in amounts]
        split_array = [[[]]*sub_lengths[x] for x in range(len(amounts))]
        
        for amount_index, ingredient in enumerate(amounts):
            for ingredient_index, sub_ingredient in enumerate(ingredient):
                number_part = ''.join([x for x in list(sub_ingredient) if x in numbers])
                if number_part == '': # Sometimes "pinch" is listed as an amount. I'm listing it as 0 so the indexes line up.
                    number_part = 0
                else:
                    number_part = float(number_part)
                
                string_part = ''.join([x for x in list(sub_ingredient) if x not in numbers])
                
                if string_part == 'cup':
                    string_part = 'cups' # Adding consistency
                
                split_array[amount_index][ingredient_index] = [number_part,string_part]
        return split_array
    
    preferred_units = ['tbsp','lb','oz','cups','tsp'] # In that order
    relationships = {
        # I could make something that keeps track of both sides of the relationship,
        # but there aren't that many kitchen quantities. 
        'cupsoz': 8,
        'tsptbsp': 0.33,
        'lboz': 16,
        'cupstbsp': 16,
        'oztbsp': 2,
        'ozlb': 0.125,
        'tspcups': 0.021,
    }
    
    unit_error_indexes = [] # Since this function doesn't have access to the names, just the indexes of errors, it'll save them for print output later.
    new_amounts = quantity_unit(amounts)
    sums = [[]]*len(new_amounts)
    for amount_index,ingredient in enumerate(new_amounts):
        # Scan over the sub_ingredients and choose a suitable unit
        # This looks for the lowest index in preferred_units and sets the default to that.
        # It's not a perfect system but quite good nonetheless.
        indexes = [0]*len(ingredient)
        for ingredient_index, sub_ingredient in enumerate(ingredient):
            try:
                index = preferred_units.index(sub_ingredient[1])
            except ValueError:
                index = 10 # Outside the bounds of preferred_units. Technically this would be better set to np.inf or something for extensibility
            indexes[ingredient_index] = index
        if min(indexes) < len(preferred_units):
            unit = preferred_units[min(indexes)]
        else:
            unit = ingredient[0][1]
        # Note: The above is tolerant to unnamed quantities, like 3 cabbages. This is because the unit type is set to ''
        totalsum = 0
        for sub_ingredient in ingredient:
            if sub_ingredient[1] == unit: # If it's the chosen unit, just add it to the running sum
                totalsum += sub_ingredient[0]
            else: # If it's not the chosen unit, look up the conversion and then add it
                if sub_ingredient[1] == 'pinch': # Pinch adds nothing to the final amount
                    pass
                else:
                    try:
                        totalsum += relationships[sub_ingredient[1] + unit] # Includes info on unit from and unit to
                    except KeyError: # Can't find unit conversion
                        # print('Can\'t find unit conversion!', '"' + sub_ingredient[1] + '" to "' + unit + '"','\n',ingredient)
                        unit_error_indexes.append(amount_index)
        sums[amount_index] = [totalsum,unit]
    sums = [[round(x[0],2),x[1]] for x in sums]
    
    return sums, unit_error_indexes

finals = toIngredients([
    ['Egg Drop Soup', 2],
    ['Orange French Toast', 2],
    ['Asian Noodle Bowl with Poached Egg', 2],
    ['Eggs Blackstone', 1]
])
# print('--------------------------------------------------------------')
sums, unit_error_indexes = unit_sum(finals[1])
print('Unit conversion errors:',len(unit_error_indexes))
print('--------------------------------------------------------------')
for i in range(len(finals[0])):
    print('{:<20} {}'.format(finals[0][i],str(sums[i][0]) + ' ' + str(sums[i][1])),end=' ')
    if i in unit_error_indexes:
        print(finals[1][i])
    else:
        print('')

# checkMenu()
