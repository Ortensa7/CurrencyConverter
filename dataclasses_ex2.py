from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    quantity: int = 0

    def total_cost(self):
        return self.price * self.quantity

print(Product("Notebook", 4.99, 3).total_cost())
print(Product("Pen", 1.50, 10).total_cost())