from auth import signup, login

def main():
    while True:
        print("\n=== Juspay Console App ===")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose: ")
        if choice == "1":
            signup()
        elif choice == "2":
            login()
        elif choice == "3":
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main()
