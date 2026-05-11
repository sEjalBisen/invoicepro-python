import json
import os
from datetime import datetime

class Product:
    """Represents a product in the store catalog"""
    def __init__(self, product_id, name, price, stock):
        self.id = product_id
        self.name = name
        self.price = float(price)
        self.stock = int(stock)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "price": self.price, "stock": self.stock}

    @staticmethod
    def from_dict(data):
        return Product(data["id"], data["name"], data["price"], data["stock"])

    def __str__(self):
        return f"[{self.id}] {self.name} - ₹{self.price:.2f} | Stock: {self.stock}"

class InvoiceItem:
    """Represents one line item in an invoice"""
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = int(quantity)
        self.total_price = product.price * self.quantity

class Invoice:
    """Handles invoice creation, calculation, and formatting"""
    TAX_RATE = 0.18 # 18% GST

    def __init__(self, customer_name):
        self.customer_name = customer_name
        self.items = []
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.subtotal = 0
        self.tax = 0
        self.total = 0

    def add_item(self, item):
        self.items.append(item)

    def calculate_total(self):
        """Loop logic for invoice totals"""
        self.subtotal = sum(i.total_price for i in self.items)
        self.tax = round(self.subtotal * Invoice.TAX_RATE, 2)
        self.total = round(self.subtotal + self.tax, 2)

    def print_invoice(self):
        """String formatting for nice receipts"""
        lines = []
        lines.append("="*45)
        lines.append(f"{'InvoicePro - Invoice':^45}")
        lines.append("="*45)
        lines.append(f"Customer: {self.customer_name}")
        lines.append(f"Date: {self.date}")
        lines.append("-"*45)
        lines.append(f"{'Item':<15} {'Qty':<5} {'Price':<8} {'Total'}")
        lines.append("-"*45)
        for i in self.items:
            lines.append(f"{i.product.name:<15} {i.quantity:<5} ₹{i.product.price:<7.2f} ₹{i.total_price:.2f}")
        lines.append("-"*45)
        lines.append(f"{'Subtotal:':<30} ₹{self.subtotal:.2f}")
        lines.append(f"{'Tax (18%):':<30} ₹{self.tax:.2f}")
        lines.append(f"{'Total:':<30} ₹{self.total:.2f}")
        lines.append("="*45)
        lines.append("Thank you for shopping with us!")
        return "\n".join(lines)

class InventoryManager:
    """Manages product catalog and file I/O"""
    def __init__(self, filename="products.json"):
        self.filename = filename
        self.products = {}
        self.load_products()

    def add_product(self, product):
        self.products[product.id] = product
        self.save_products()

    def update_product(self, pid, price=None, stock=None):
        if pid in self.products:
            if price:
                self.products[pid].price = float(price)
            if stock is not None:
                self.products[pid].stock = int(stock)
            self.save_products()
            return True
        return False

    def load_products(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.products = {pid: Product.from_dict(p) for pid, p in data.items()}

    def save_products(self):
        with open(self.filename, "w") as f:
            json.dump({pid: p.to_dict() for pid, p in self.products.items()}, f, indent=2)

    def list_products(self):
        if not self.products:
            print("No products in catalog.")
            return
        print("\n--- Product Catalog ---")
        for p in self.products.values():
            print(p)

    def get_product(self, pid):
        return self.products.get(pid)

def save_invoice_to_file(invoice, filename):
    """Save invoice to.txt file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(invoice.print_invoice())
    print(f"\nInvoice saved to {filename}")

def manage_products(inv_mgr):
    while True:
        print("\n--- Manage Products ---")
        print("1. View Products")
        print("2. Add Product")
        print("3. Update Product")
        print("4. Back to Main Menu")
        choice = input("Choose: ")

        if choice == "1":
            inv_mgr.list_products()
        elif choice == "2":
            pid = input("Enter Product ID: ").strip()
            if pid in inv_mgr.products:
                print("Product ID already exists.")
                continue
            name = input("Enter Product Name: ").strip()
            price = input("Enter Price: ").strip()
            stock = input("Enter Stock: ").strip()
            try:
                inv_mgr.add_product(Product(pid, name, price, stock))
                print("Product added successfully.")
            except ValueError:
                print("Invalid price or stock value.")
        elif choice == "3":
            pid = input("Enter Product ID to update: ").strip()
            if pid not in inv_mgr.products:
                print("Product not found.")
                continue
            price = input("New Price (press Enter to skip): ").strip()
            stock = input("New Stock (press Enter to skip): ").strip()
            inv_mgr.update_product(pid, price or None, stock or None)
            print("Product updated.")
        elif choice == "4":
            break
        else:
            print("Invalid choice.")

def create_invoice(inv_mgr):
    customer = input("\nEnter Customer Name: ").strip()
    if not customer:
        customer = "Walk-in Customer"

    invoice = Invoice(customer)
    inv_mgr.list_products()

    while True:
        pid = input("\nEnter Product ID to add (or 'done' to finish): ").strip()
        if pid.lower() == "done":
            break
        if pid not in inv_mgr.products:
            print("Product not found.")
            continue

        product = inv_mgr.products[pid]
        if product.stock <= 0:
            print("Out of stock.")
            continue

        try:
            qty = int(input(f"Enter Quantity (Available: {product.stock}): "))
            if qty <= 0:
                print("Quantity must be positive.")
                continue
            if qty > product.stock:
                print(f"Not enough stock. Available: {product.stock}")
                continue

            item = InvoiceItem(product, qty)
            invoice.add_item(item)
            product.stock -= qty
            print(f"Added {qty} x {product.name}")
        except ValueError:
            print("Invalid quantity.")

    if not invoice.items:
        print("No items added. Invoice cancelled.")
        return

    invoice.calculate_total()
    bill_text = invoice.print_invoice()
    print("\n" + bill_text)

    # Save invoice to.txt file
    filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    save_invoice_to_file(invoice, filename)

    # Save updated stock
    inv_mgr.save_products()

def main():
    inv_mgr = InventoryManager()

    while True:
        print("\n" + "="*30)
        print(" InvoicePro - Main Menu")
        print("="*30)
        print("1. Manage Products")
        print("2. Create Invoice")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            manage_products(inv_mgr)
        elif choice == "2":
            create_invoice(inv_mgr)
        elif choice == "3":
            print("Exiting InvoicePro. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()