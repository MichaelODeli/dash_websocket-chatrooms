

def modal_login(mode):
    if mode not in ['login', 'register', 'reset']:
        raise ValueError
    else:
        return None