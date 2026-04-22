current_user = None
current_role = None

def login(user, role):
    global current_user, current_role
    current_user = user
    current_role = role

def logout():
    global current_user, current_role
    current_user = None
    current_role = None