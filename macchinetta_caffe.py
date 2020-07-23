class Item:  # define class Item with  2 parameters (name, price)

    def __init__(self, name, price):
        self.name = name
        self.price = price


class VendingMachine:  # define VendingMachine class and initialize with all the vending machine items

    def __init__(self):

        self.items = [
            Item("Caffè", 0.45),
            Item("Cappuccino", 0. ),
            Item("Caffè Macchiato", 1.00),
            Item("Caffè lungo", 0.80),
            Item("Caffè Ristretto", 0.60),
            Item("Latte macchiato", 1.50),
            Item("Americano", 1.80),
            Item("Cioccolata", 2.00),
            Item("té nero", 1.20)
        ]

        self.money_inserted = 0.00  # initialize the money available in the vending machine

    def display_items(self):  # function to display the items with their price
        print("##################################")
        print(" Buongiorno, scegli pure la bevanda per visualizzarne il prezzo")
        for code, item in enumerate(self.items, start=1):
            print(f"[{code}] - {item.name} (€{item.price:.2f})")
        print("##################################")

    def insert_money(self, money):  # function for money insert
        if money <= 0.00:
            raise ValueError
        self.money_inserted += money


def main():

    vending_machine = VendingMachine()
    vending_machine.display_items()

    def switch(choice):  # switch function in order to display preparation of the item
        switcher = {
            1: "Preparing High Quality coffee beans...\n"
               "Brewing coffee...\n"
               "Caffè is served",
            2: "Making Cappucino...\n"
               "Steaming the milk...\n"
               "Frothing the milk...\n"
               "Making espresso...\n"
               "Adding the milk to the espresso...\n"
               "Cappuccino is served",
            3: "Making milk...\n"
               "Making espresso...\n"
               "Steaming the milk...\n"
               "Adding the milk to the espresso...\n"
               "Caffè Macchiato is served",
            4: "Making 40 ml of coffee...\n"
               "Caffè lungo is served",
            5: "Making 20 ml of coffee...\n"
               "Caffè Ristretto is served",
            6: "Making Latte...\n"
               "Adding 20 ml of coffee to Latte...\n"
               "Latte macchiato is ready",
            7: "Making espresso...\n"
               "Adding 70 ml of water...\n"
               "Americano is served",
            8: "Making milk...\n"
               "Preparing cocoa ...\n"
               "Adding cocoa to milk...\n"
               "Cioccolata is served",
            8: "Heating whater...\n"
               "Preparing dust of tea ...\n"
               "Add whater and tea to plastic cup...\n"
               "tè nero is served",
        }
        print(switcher.get(choice, "Invalid item"))

        return 0

    while True:
        try: 
            user_selection = int(input("Please enter the desired item code: "));
            if user_selection not in range(1, len(vending_machine.items)+1):
                print("Invalid item code, please try again...")
        except ValueError:
            continue
        if user_selection in range(1, len(vending_machine.items)+1):
            break
    item = vending_machine.items[user_selection - 1]
    print(f"You've selected \"{item.name}\" - the price is €{item.price:.2f}")
    print("Sugar: 1-Less, 2-Medium, 3-Maximum")
    sugar_choice = input("Please choose sugar quantity: ")
    if sugar_choice == '1':
        print("You choose less quantity of sugar")
    elif sugar_choice == '2':
        print("You choose medium quantity of sugar")
    elif sugar_choice == '3':
        print("You choose maximum quantity of sugar")
    while vending_machine.money_inserted < item.price:
        print(f"You've inserted €{vending_machine.money_inserted:.2f} into the machine so far.")
        while True:
            try:
                money_to_insert = float(input("Please enter the amount of money you'd like to insert: "))
                vending_machine.insert_money(money_to_insert)
            except ValueError:
                continue
            else:
                break
    switch(user_selection)
    print(f"Thank you! Please take your \"{item.name}\".")
    print(f"The remaining change in the machine is €{vending_machine.money_inserted - item.price:.2f}.")
    print("Have a nice day!")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())