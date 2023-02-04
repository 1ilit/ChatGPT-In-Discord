import random

def handle_response(message):
    p_message=message.lower()

    if p_message=='hello':
        return 'sup'
    
    if p_message=='roll':
        return str(random.randint(1, 4))
    
    if p_message=='!help':
        return '`This is ur help`'

    return "fuk off"