

def askBoolean(question):
    ans = None
    valid_answers = ['y', 'Y', 'n', 'N']
    ans = input(f'  {question} [y/n] ')
    while ans not in valid_answers:
        ans = input(f'X {question} [y/n] ')
    
    ret = False
    if ans in 'yY':
        ret = True
    return ret