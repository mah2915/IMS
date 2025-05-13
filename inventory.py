import json
from abc import ABC, abstractmethod
from datetime import datetime

# Custom Exceptions
class OutOfStockError(Exception):
    pass

class DuplicateProductError(Exception):
    pass

class InvalidProductDataError(Exception):
    pass

# Abstract Product Class
class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    def restock(self, amount):
        self._quantity_in_stock += amount

    def sell(self, quantity):
        if quantity > self._quantity_in_stock:
            raise OutOfStockError("Not enough stock available.")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock

    @abstractmethod
    def __str__(self):
        pass

    def to_dict(self):
        return self.__dict__

# Subclasses
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity, warranty_years, brand):
        super().__init__(product_id, name, price, quantity)
        self.warranty_years = warranty_years
        self.brand = brand

    def __str__(self):
        return f"Electronics: {self._name} ({self.brand}) - ${self._price} [{self._quantity_in_stock} in stock]"

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity, expiry_date):
        super().__init__(product_id, name, price, quantity)
        self.expiry_date = expiry_date  # in 'YYYY-MM-DD'

    def is_expired(self):
        return datetime.strptime(self.expiry_date, "%Y-%m-%d") < datetime.now()

    def __str__(self):
        status = "Expired" if self.is_expired() else "Fresh"
        return f"Grocery: {self._name} - ${self._price} [{self._quantity_in_stock} in stock, {status}]"

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity, size, material):
        super().__init__(product_id, name, price, quantity)
        self.size = size
        self.material = material

    def __str__(self):
        return f"Clothing: {self._name} ({self.size}, {self.material}) - ${self._price} [{self._quantity_in_stock} in stock]"

# Inventory Class
class Inventory:
    def __init__(self):
        self._products = {}

    def add_product(self, product):
        if product._product_id in self._products:
            raise DuplicateProductError("Product ID already exists.")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        if product_id in self._products:
            del self._products[product_id]

    def search_by_name(self, name):
        result = []
        for product in self._products.values():
            if name.lower() in product._name.lower():
                result.append(product)
        return result

    def search_by_type(self, product_type):
        result = []
        for product in self._products.values():
            if product.__class__.__name__.lower() == product_type.lower():
                result.append(product)
        return result

    def list_all_products(self):
        return list(self._products.values())

    def sell_product(self, product_id, quantity):
        if product_id in self._products:
            self._products[product_id].sell(quantity)

    def restock_product(self, product_id, quantity):
        if product_id in self._products:
            self._products[product_id].restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        to_remove = [pid for pid, p in self._products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in to_remove:
            del self._products[pid]
    def load_from_file(self, filename):
     try:
        with open(filename, 'r') as f:
            data = json.load(f)

        for item in data:
            ptype = item.pop('type')
            if ptype == 'Electronics':
                product = Electronics(
                    item["product_id"],
                    item["name"],
                    item["price"],
                    item["quantity_in_stock"],
                    item["warranty_years"],
                    item["brand"]
                )
            elif ptype == 'Grocery':
                product = Grocery(
                    item["product_id"],
                    item["name"],
                    item["price"],
                    item["quantity_in_stock"],
                    item["expiry_date"]
                )
            elif ptype == 'Clothing':
                product = Clothing(
                    item["product_id"],
                    item["name"],
                    item["price"],
                    item["quantity_in_stock"],
                    item["size"],
                    item["material"]
                )
            else:
                raise InvalidProductDataError("Unknown product type.")

            self._products[product._product_id] = product

     except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise InvalidProductDataError(f"Error loading product: {e}")

  
    def save_to_file(self, filename):
     data = []
     for p in self._products.values():
        item = {
            "product_id": p._product_id,
            "name": p._name,
            "price": p._price,
            "quantity_in_stock": p._quantity_in_stock,
            "type": p.__class__.__name__
        }
        if isinstance(p, Electronics):
            item["warranty_years"] = p.warranty_years
            item["brand"] = p.brand
        elif isinstance(p, Grocery):
            item["expiry_date"] = p.expiry_date
        elif isinstance(p, Clothing):
            item["size"] = p.size
            item["material"] = p.material
        data.append(item)

     with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

    
# CLI Menu

def main():
    inventory = Inventory()

    while True:
        print("\nInventory Management System")
        print("1. Add Product")
        print("2. Sell Product")
        print("3. Search/View Product")
        print("4. List All Products")
        print("5. Restock Product")
        print("6. Remove Expired Groceries")
        print("7. Total Inventory Value")
        print("8. Save Inventory")
        print("9. Load Inventory")
        print("0. Exit")

        choice = input("Enter choice: ")

        try:
            if choice == '1':
                ptype = input("Enter product type (Electronics/Grocery/Clothing): ").strip().lower()
                pid = input("Product ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))
                if ptype == 'electronics':
                    warranty = int(input("Warranty Years: "))
                    brand = input("Brand: ")
                    product = Electronics(pid, name, price, qty, warranty, brand)
                elif ptype == 'grocery':
                    expiry = input("Expiry Date (YYYY-MM-DD): ")
                    product = Grocery(pid, name, price, qty, expiry)
                elif ptype == 'clothing':
                    size = input("Size: ")
                    material = input("Material: ")
                    product = Clothing(pid, name, price, qty, size, material)
                else:
                    print("Invalid product type!")
                    continue
                inventory.add_product(product)
                print("Product added successfully.")

            elif choice == '2':
                pid = input("Product ID to sell: ")
                qty = int(input("Quantity to sell: "))
                inventory.sell_product(pid, qty)
                print("Product sold.")

            elif choice == '3':
                search = input("Search by name or type? (name/type): ")
                keyword = input("Enter keyword: ")
                if search == 'name':
                    results = inventory.search_by_name(keyword)
                else:
                    results = inventory.search_by_type(keyword)
                if results:
                    for p in results:
                        print(p)
                else:
                    print("No products found.")

            elif choice == '4':
                for p in inventory.list_all_products():
                    print(p)

            elif choice == '5':
                pid = input("Product ID to restock: ")
                qty = int(input("Quantity to add: "))
                inventory.restock_product(pid, qty)
                print("Product restocked.")

            elif choice == '6':
                inventory.remove_expired_products()
                print("Expired groceries removed.")

            elif choice == '7':
                total = inventory.total_inventory_value()
                print(f"Total inventory value: ${total:.2f}")

            elif choice == '8':
                fname = input("Filename to save: ")
                inventory.save_to_file(fname)
                print("Inventory saved.")

            elif choice == '9':
                fname = input("Filename to load: ")
                inventory.load_from_file(fname)
                print("Inventory loaded.")

            elif choice == '0':
                print("Exiting...")
                break

            else:
                print("Invalid choice.")

        except Exception as e:
            print("Error:", e)

if __name__ == '__main__':
    main()