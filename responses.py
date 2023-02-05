import random

def handle_response(message):
    print(message)

    if message == 'hello':
        return 'sup'
    
    if message == 'roll':
        return str(random.randint(1, 4))
    
    if message == 'help':
        return '`This is ur help`'
    
    if message == 'buniii':
        return 'beeee'

    return "fuk off"