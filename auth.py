import pwinput
from db import users_col
from user_actions import user_menu
from db_utils import get_user  

def get_user(username):
    return users_col.find_one({"username": username})

def signup():
    username = input("Enter username: ")
    if get_user(username):
        print("User already exists.")
        return
    password = pwinput.pwinput("Enter password: ", mask="*")
    user_doc = {
        "username": username,
        "password": password,
        "methods": {"cards": [], "upi": []},
        "history": [],
        "failed_attempts": 0
    }
    users_col.insert_one(user_doc)
    print("Signup successful!")

def login():
    username = input("Enter username: ")
    user = get_user(username)
    if not user:
        print("User does not exist.")
        return
    password = pwinput.pwinput("Enter password: ", mask="*")
    if user["password"] == password:
        print("Login successful!")
        users_col.update_one({"username": username}, {"$set": {"failed_attempts": 0}})
        user_menu(username)
    else:
        failed = user.get("failed_attempts", 0) + 1
        users_col.update_one({"username": username}, {"$set": {"failed_attempts": failed}})
        print("Invalid credentials.")
        if failed >= 3:
            print("⚠️  Too many failed attempts. Account temporarily locked.")
