class Ingredient:
    def __init__(self, name='', quantity=0, qtype=''):
        # qtype examples: "cup", "fl oz", "tbsp"
        self.name = name
        self.quantity = quantity
        self.qtype = qtype
    def __add__(self,other):
        # Proper usage assertions
        assert type(other) == Ingredient, 'Can only add together two Ingredient objects'
        assert self.name == other.name, 'Cannot add together two different ingredients: (' + repr(self.name) + ') AND (' + repr(other.name) + ')'
        
        if self.qtype == other.qtype: # Easy!
            return Ingredient(self.name,self.quantity+other.quantity,self.qtype)
        else: # Harder. Needs unit conversion.
            conversions = {(self.qtype,other.qtype),(other.qtype,self.qtype)} # So you can get both directions (tbsp -> tsp) and (tsp -> tbsp)
            for rule in addrules:
                if rule[0] in conversions and ('any' in rule[2]  or  self.name in rule[2]): # Correct conversion (tbsp -> tsp) and allowed for type of ingredient
                    relevant_rule = rule
                    break
            else: # Runs only if no conversion was found
                raise Exception('Failed to add together (' + repr(self.name) + ') AND (' + repr(other.name) + ') due to quant type mismatch: (' + repr(self.qtype) + ') AND (' + repr(other.qtype) + ')')
            
            priority_qtype = [self.qtype,other.qtype].index(relevant_rule[0][0]) # For example, 'tbsp' is preferred in rule ('tbsp','tsp')
            if priority_qtype == 0:
                return Ingredient(self.name,self.quantity + other.quantity/relevant_rule[1], self.qtype)
            else:
                return Ingredient(self.name,other.quantity + self.quantity/relevant_rule[1], other.qtype)
    def __truediv__(self, bottom): # The other one is __floordiv__
        ''' Returns a float ratio after doing correct unit conversion. Units cancel when dividing. '''
        assert type(bottom) == Ingredient, 'Can\'t divide by a non-Ingredient object'
        assert self.name == bottom.name, 'Can\'t divide apples and oranges ;)'
        if self.qtype == bottom.qtype: # Easy!
            return self.quantity / bottom.quantity
        else: # Harder. Needs unit conversion.
            conversions = {(self.qtype,bottom.qtype),(bottom.qtype,self.qtype)} # So you can get both directions (tbsp -> tsp) and (tsp -> tbsp)
            for rule in addrules:
                if rule[0] in conversions and ('any' in rule[2]  or  self.name in rule[2]): # Correct conversion (tbsp -> tsp) and allowed for type of ingredient
                    relevant_rule = rule
                    break
            else: # Runs only if no conversion was found
                raise Exception('Failed to divide (' + repr(self.name) + ') due to quant type mismatch: (' + repr(self.qtype) + ') AND (' + repr(bottom.qtype) + ')')
            
            # Ratio doesn't depend on units, so just use an arbitrary one. I use the same priority_qtype rule as __add__.
            priority_qtype = [self.qtype,bottom.qtype].index(relevant_rule[0][0]) # For example, 'tbsp' is preferred in rule ('tbsp','tsp')
            if priority_qtype == 0: # Convert denominator
                return self.quantity / (bottom.quantity / relevant_rule[1])
            else:                   # Convert numerator
                return (self.quantity/relevant_rule[1]) / bottom.quantity
    def __repr__(self):
        return str((self.name,self.quantity,self.qtype)) # Done the lazy way
    def __mul__(self,integer): # Scalar multiplication on the right
        return Ingredient(self.name,self.quantity*integer,self.qtype)