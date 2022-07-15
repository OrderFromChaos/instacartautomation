from src.conversionrules import *
    # These are the relevant variables:
    # "X" is either special, liquid, or general
    # X_rules
    # X_preferred
    # Note that there is no "general_preferred",
    #   it is assumed that recipes will mention the item in its buyable qtype
from copy import deepcopy


class Ingredient:
    def __init__(self, name='', quantity=0, qtype='', liquid=False):
        # qtype examples: "cup", "fl oz", "tbsp"
        self.name = name
        self.quantity = quantity
        self.qtype = qtype
        self.liquid = liquid

    def _convert(self, other):
        # Converts both sides, updates self, returns other
        assert type(other) == Ingredient, ('Can only do operations between '
             + 'two Ingredient objects. ' 
             + f'Right obj ({other}) is not of Ingredient class.')
        assert self.name == other.name, ('Cannot do operations between '
              + 'two different Ingredient objects: '
              + f'({self.name}) AND ({other.name})')

        SPECIALFLAG = self.name in special_ingredients
        LIQUIDFLAG = self.liquid

        # Pick preferred quantity
        preferred = None
        if self.name in specific_preferred:
            preferred = specific_preferred[self.name]
        elif LIQUIDFLAG:
            preferred = liquid_preferred

        all_conversions = deepcopy(general_rules)
        # print(all_conversions)
        # Merge specifically applicable defaultdicts
        if SPECIALFLAG:
            for key, convlist in special_rules[self.name].items():
                for conv in convlist:
                    # print(convlist)
                    all_conversions[key].append(conv)
        if LIQUIDFLAG:
            for key, convlist in liquid_rules.items():
                for conv in convlist:
                    all_conversions[key].append(conv)
        
        if preferred == None:
            if self.qtype == other.qtype:
                # Nothing left to do
                return other
            else:
                # Unit convert other's qtype into self
                totype = self.qtype
                fromtype = other.qtype
                for conv in all_conversions[fromtype]:
                    if conv[0] == totype:
                        return Ingredient(
                            name=other.name,
                            quantity=other.quantity*conv[1],
                            qtype=self.qtype,
                            liquid=other.liquid
                        )
                        break
                else:
                    raise Exception('(No preferred type)\n'
                                    + f'Unable to convert\n{other}\ninto\n{self}')
                return other
        else:
            # Convert both to preferred qtype
            
            # Self
            if self.qtype != preferred:
                for conv in all_conversions[self.qtype]:
                    if conv[0] == preferred:
                        self.quantity = self.quantity*conv[1]
                        self.qtype = preferred
                        break
                else:
                    raise Exception(f'(Preferred type: {preferred})\n'
                                    + f'Unable to convert\n{self}\ninto\n{preferred}')

            # Other
            if other.qtype != preferred:
                for conv in all_conversions[other.qtype]:
                    if conv[0] == preferred:
                        return Ingredient(
                            name=other.name,
                            quantity=other.quantity*conv[1],
                            qtype=self.qtype,
                            liquid=other.liquid
                        )
                        break
                else:
                    raise Exception(f'(Preferred type: {preferred})\n'
                                    + f'Unable to convert\n{other}\ninto\n{preferred}')
            return other

    def __add__(self, other):
        other = self._convert(other)
        self.quantity += other.quantity
        return self
    
    def __repr__(self):
        return str((self.name,round(self.quantity, 2),self.qtype)) # Done the lazy way
    
    def __mul__(self, factor): # Right multiplication by scalar
        self.quantity *= factor
        return self
