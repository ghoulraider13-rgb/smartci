from src.pricing import apply_discount, add_tax


class Cart:
    def __init__(self):
        self.items = []

    def add(self, name, price, qty=1):
        self.items.append((name, price, qty))

    def total(self, discount=0):
        subtotal = sum(p * q for _, p, q in self.items)
        return add_tax(apply_discount(subtotal, discount))