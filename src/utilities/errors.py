ERROR_TYPES = {
    0: 'Missing ingredient',
    1: 'Ingredient OK, missing store',
}


class InstacartError:
    def __init__(self, id_code):
        self.id_code = id_code
    
    def getErrorType(self):
        return ERROR_TYPES[self.id_code]
    
    def __repr__(self):
        return f'ERROR {self.id_code}: {self.getErrorType()}'
