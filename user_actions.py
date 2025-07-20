import random
from datetime import datetime
from db import users_col
from utils import mask_card
from db_utils import get_user

def add_payment_method(username):
    user = get_user(username)
    print("1. Add Card")
    print("2. Add UPI")
    choice = input("Choose: ")

    if choice == "1":
        card = input("Enter card number (16 digits): ")
        if len(card) == 16 and card.isdigit():
            expiry = input("Enter expiry date (MM/YY): ")
            cvv = input("Enter 3-digit CVV: ")
            pin = input("Enter a 4-digit card PIN: ")
            if len(cvv) != 3 or not cvv.isdigit() or len(pin) != 4 or not pin.isdigit():
                print("Invalid CVV or PIN. Card not saved.")
                return
            masked = mask_card(card)
            user["methods"]["cards"].append({
                "card": masked,
                "expiry": expiry,
                "cvv": cvv,
                "pin": pin
            })
            users_col.update_one({"username": username}, {"$set": {"methods": user["methods"]}})
            print("Card saved:", masked)
        else:
            print("Invalid card.")
    elif choice == "2":
        upi = input("Enter UPI ID (e.g., user@upi): ")
        upi_pin = input("Set a 4 or 6 digit UPI PIN: ")
        if not (len(upi_pin) in [4, 6] and upi_pin.isdigit()):
            print("Invalid UPI PIN. UPI not saved.")
            return
        user["methods"]["upi"].append({
            "upi": upi,
            "pin": upi_pin
        })
        users_col.update_one({"username": username}, {"$set": {"methods": user["methods"]}})
        print("UPI saved:", upi)

def make_payment(username):
    user = get_user(username)
    methods = user["methods"]
    if not methods["cards"] and not methods["upi"]:
        print("No payment methods available.")
        return

    print("\nSelect method:")
    options = []
    card_indices = []
    upi_indices = []

    for idx, c in enumerate(methods["cards"]):
        options.append(f"Card: {c['card']}")
        card_indices.append(idx)
    for idx, u in enumerate(methods["upi"]):
        options.append(f"UPI: {u['upi']}")
        upi_indices.append(idx)

    for i, m in enumerate(options):
        print(f"{i+1}. {m}")
    choice = int(input("Choose: ")) - 1

    if 0 <= choice < len(options):
        amount = float(input("Enter amount: ₹"))
        method = options[choice]
        status = "Failed"

        if method.startswith("Card:"):
            card_idx = card_indices[choice] if choice < len(card_indices) else None
            if card_idx is not None:
                c = methods["cards"][card_idx]
                pin = input("Enter 4-digit card PIN: ")
                if pin != c["pin"]:
                    print("Incorrect PIN. Payment Failed!")
                else:
                    otp = str(random.randint(100000, 999999))
                    with open("otp.txt", "w") as f:
                        f.write(f"Your OTP is: {otp}\n")
                    print("OTP has been written to otp.txt")
                    entered = input("Enter OTP: ")
                    if entered != otp:
                        print("Incorrect OTP.")
                    else:
                        print("Processing...")
                        status = "Success" if random.random() > 0.2 else "Failed"
                        print(f"Payment {status}!")
        else:
            upi_idx = choice - len(card_indices)
            if 0 <= upi_idx < len(upi_indices):
                u = methods["upi"][upi_indices[upi_idx]]
                upi_pin = input("Enter your UPI PIN: ")
                if upi_pin != u["pin"]:
                    print("Incorrect UPI PIN.")
                else:
                    print("Processing...")
                    status = "Success"
                    print(f"Payment {status}!")

        user["history"].append({
            "method": method,
            "amount": amount,
            "status": status,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        users_col.update_one({"username": username}, {"$set": {"history": user["history"]}})
    else:
        print("Invalid choice.")

def view_history(username):
    user = get_user(username)
    history = user["history"]
    if not history:
        print("No transactions yet.")
        return
    print("\n--- Payment History ---")
    for i, h in enumerate(history, 1):
        print(f"{i}. {h['time']} | ₹{h['amount']} | {h['method']} | {h['status']}")

def user_menu(username):
    while True:
        print(f"\nWelcome {username}")
        print("1. Add Payment Method")
        print("2. Make Payment")
        print("3. View History")
        print("4. Logout")
        choice = input("Choose: ")
        if choice == "1":
            add_payment_method(username)
        elif choice == "2":
            make_payment(username)
        elif choice == "3":
            view_history(username)
        elif choice == "4":
            break
        else:
            print("Invalid input.")
