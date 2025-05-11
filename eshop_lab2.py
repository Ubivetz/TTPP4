class Product:
    def __init__(self, name, price, available_amount):
        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, requested_amount):
        return self.available_amount >= requested_amount

    def buy(self, requested_amount):
        if self.is_available(requested_amount):
            self.available_amount -= requested_amount
        else:
            raise ValueError(
                f"Not enough items available. Requested: {requested_amount}, Available: {self.available_amount}")

    def update_price(self, new_price):
        if new_price <= 0:
            raise ValueError("Price must be greater than zero")
        self.price = new_price

    def restock(self, additional_amount):
        if additional_amount <= 0:
            raise ValueError("Restock amount must be greater than zero")
        self.available_amount += additional_amount

    def __eq__(self, other):
        if other is None or not isinstance(other, Product):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Product(name='{self.name}', price={self.price}, available_amount={self.available_amount})"


class ShoppingCart:
    def __init__(self):
        self.products = dict()

    def contains_product(self, product):
        return product in self.products

    def calculate_total(self):
        return sum([p.price * count for p, count in self.products.items()])

    def add_product(self, product: Product, amount: int):
        if not product:
            raise ValueError("Product cannot be None")
        if not isinstance(amount, int):
            raise ValueError(f"Amount must be an integer, got {type(amount)}")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if not product.is_available(amount):
            raise ValueError(f"Product {product} has only {product.available_amount} items")
        self.products[product] = amount

    def remove_product(self, product):
        if product in self.products:
            del self.products[product]

    def get_product_quantity(self, product):
        return self.products.get(product, 0)

    def update_product_quantity(self, product, new_quantity):
        if not product:
            raise ValueError("Product cannot be None")
        if not isinstance(new_quantity, int) or new_quantity <= 0:
            raise ValueError("New quantity must be a positive integer")
        if product in self.products and product.is_available(new_quantity):
            self.products[product] = new_quantity
        else:
            raise ValueError(f"Cannot update quantity for {product}")

    def clear(self):
        self.products.clear()

    def submit_cart_order(self):
        if not self.products:
            raise ValueError("Cart is empty")

        for product, count in self.products.items():
            product.buy(count)

        self.products = dict()

class Order:
    def __init__(self, cart):
        self.cart = cart
    def place_order(self):
        self.cart.submit_cart_order()
