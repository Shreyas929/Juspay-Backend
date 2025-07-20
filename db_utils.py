from db import users_col

def get_user(username):
    return users_col.find_one({"username": username})
