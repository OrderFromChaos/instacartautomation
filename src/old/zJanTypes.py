from collections import OrderedDict

spent = {'Snacks':[3.59,2.50*2,2.99,5.98,2.99,2.54,3.96,2.99,5.98,5.99,2.99,2.99,5.99,5.98,2.99,4.99,1.99,1.99],
        'Special':[4.99,4.99,8.98],
        'Drinks':[9.49,5.99,5.99,6.49,9.49],
        'Household':[3.99,6.99,3.00,6.99,2.00,11.49,12.98],
        'Chicken Broth':[2.79*2,11.16,2.79,5.58,2.79,5.58],
        'Food':[0.69,2.69*2,2.99*2,16.99,1.98,11.97,7.98,5.38,0.72,2.99,4.99,3.69,5.38,2.99,2.99,7.98,11.96,5.38,1.12,5.38,3.99,1.98,1.38,3.99,5.99,6.98,7.97],
        'Bacon':[6.99*2,14.97,9.98,13.98,13.98],
        'Herbs':[2.79,1.99,2.50,7.98,1.98,2.98,5.07,6.16,3.99,.99,.76,2.99,2.49,3.99,2.99,4.74,2.49],
        'Sandwiches':[3.98,2.69,2.99,6.98,3.49,5.38,3.99,1.99,5.99,2.99,3.99,11.98,1.99,3.99,5.99],
        'Cereal/Milk':[7.99,6.69,5.18,2.59,7.98,5.18,2.59],
        'Tips':[2.00,3.65,2.00,2.62,3.31,2.87,2.27,3.27],
        'Tax/bag cost':[.88+.30,.45,1.70,.5,.3,.3,.3,3.31,.4]
}

for category in spent: # Sum amounts
    spent[category] = sum(spent[category])

print("Amount spent per category:") # Print per category
spent = OrderedDict(sorted(spent.items(), key=lambda x: x[1], reverse=True))
for category in spent:
    print(category, round(spent[category],2))

print('Total spent:',sum([spent[x] for x in spent]))
