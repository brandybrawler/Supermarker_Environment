import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time
import logging

logging.basicConfig(level=logging.INFO)

# Inventory Management
class Inventory:
    def __init__(self, initial_stock: Dict[str, int]):
        self.stock = initial_stock

    def update_stock(self, item: str, quantity: int):
        if item in self.stock:
            self.stock[item] += quantity
        else:
            self.stock[item] = quantity

    def low_stock_alert(self) -> List[str]:
        return [item for item, quantity in self.stock.items() if quantity < 5]

class AdvancedInventory(Inventory):
    def __init__(self, initial_stock: Dict[str, int]):
        super().__init__(initial_stock)
        self.expiration_dates = {}
        self.batch_numbers = {}
        self.seasonal_items = ["Watermelon", "Pumpkin"]

    def restock(self, item: str, quantity: int, expire_in_days: int=30, batch_number: Optional[str]=None):
        super().update_stock(item, quantity)
        expiration_date = datetime.now() + timedelta(days=expire_in_days)
        self.expiration_dates[item] = expiration_date
        if batch_number:
            self.batch_numbers[item] = batch_number

    def check_expiration(self):
        current_time = datetime.now()
        for item, expiration_date in self.expiration_dates.items():
            if current_time > expiration_date:
                logging.info(f"Oh no, {item} has expired. Let's remove it from the inventory!")
                self.update_stock(item, -self.stock[item])

# Customer Behavior
class Supplier:
    def __init__(self, name: str, available_items: Dict[str, float], delivery_time: int=1):
        self.name = name
        self.available_items = available_items
        self.delivery_time = delivery_time
    
    def deliver(self, order: Dict[str, int], inventory: Inventory):
        for item, quantity in order.items():
            if item in self.available_items:
                inventory.update_stock(item, quantity)
        logging.info(f"Great news! Your order has arrived: {order}")

class Customer:
    def __init__(self, name: str):
        self.name = name
        self.cart = {}

    def add_to_cart(self, item: str, quantity: int):
        if item in self.cart:
            self.cart[item] += quantity
        else:
            self.cart[item] = quantity

class AdvancedCustomer(Customer):
    def __init__(self, name: str, preferences: Optional[List[str]]=None, budget: Optional[float]=None):
        super().__init__(name)
        self.preferences = preferences if preferences else []
        self.budget = budget

    def advanced_browse_item(self, inventory: Inventory, pricing: Dict[str, float]):
        possible_items = [item for item in inventory.stock.keys() if item in self.preferences]
        if not possible_items:
            possible_items = list(inventory.stock.keys())
        item = random.choice(possible_items)
        quantity = random.randint(1, 3)
        if self.budget is not None:
            total_cost = pricing[item] * quantity
            if total_cost > self.budget:
                logging.info(f"Hmm, looks like I can't afford {item} right now. Let's skip that.")
                return
        self.add_to_cart(item, quantity)
        self.budget -= pricing[item] * quantity if self.budget is not None else 0

# Employee Simulation
class Employee:
    SALARY_PER_EMPLOYEE = 100

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    def perform_role(self, store: 'Store'):
        role_function = getattr(self, self.role.lower(), None)
        if role_function:
            role_function(store)
        else:
            logging.warning(f"Hey, just so you know, I'm not sure what to do with the role '{self.role}'. 🤷‍♂️")

    def cashier(self, store: 'Store'):
        logging.info(f"{self.name}, your friendly cashier, is here and ready to help you!")

    def stock_clerk(self, store: 'Store'):
        logging.info(f"Hey there, I'm {self.name}, your stock clerk. Time to restock those shelves!")
        self.restock(store.inventory)

    def manager(self, store: 'Store'):
        logging.info(f"Hello, I'm {self.name}, the manager in charge. Let's make sure things run smoothly.")
        self.manage_inventory(store.inventory)
        
    def restock(self, inventory: Inventory):
        for item in inventory.stock.keys():
            inventory.update_stock(item, 10)
        logging.info("Just giving you a heads-up: all items have been restocked.")

    def manage_inventory(self, inventory: Inventory):
        low_stock_items = inventory.low_stock_alert()
        if low_stock_items:
            logging.warning(f"Hey, just wanted to mention that we have low stock on: {low_stock_items}.")

# Store Operations
class Store:
    def __init__(self, inventory: Inventory, promotions: Dict[str, float]):
        self.inventory = inventory
        self.promotions = promotions

    def checkout_customer(self, customer: Customer):
        logging.info(f"{customer.name} has finished shopping. Their cart contains: {customer.cart}")

def apply_promotions(cart: Dict[str, int], promotions: Dict[str, float], pricing: Dict[str, float]) -> float:
    total_price = sum(pricing[item] * quantity for item, quantity in cart.items())
    for item, discount in promotions.items():
        if item in cart:
            total_price -= discount * cart[item]
    return total_price

class EmployeeManagedStore(Store):
    def __init__(self, inventory: Inventory, promotions: Dict[str, float], employees: List[Employee]):
        super().__init__(inventory, promotions)
        self.employees = employees
    
    def start_shift(self):
        logging.info("\n=== Let's get to work! Starting a new shift. ===")
        for employee in self.employees:
            employee.perform_role(self)

class FinancialManagedStore(EmployeeManagedStore):
    def __init__(self, inventory: Inventory, promotions: Dict[str, float], employees: List[Employee], supplier: Supplier):
        super().__init__(inventory, promotions, employees)
        self.supplier = supplier
        self.cash_flow = {'revenue': 0, 'expenses': 0, 'net_profit': 0}
        self.ordering_cost = 0
        self.salary_expense = 0

    def checkout_customer(self, customer: Customer, pricing: Dict[str, float]):
        total_price = apply_promotions(customer.cart, self.promotions, pricing)
        self.cash_flow['revenue'] += total_price
        super().checkout_customer(customer)
    
    def place_order(self, order: Dict[str, int], supplier_pricing: Dict[str, float]):
        order_cost = sum(supplier_pricing[item] * quantity for item, quantity in order.items())
        self.cash_flow['expenses'] += order_cost
        self.ordering_cost += order_cost
        self.supplier.deliver(order, self.inventory)
    
    def pay_salaries(self, duration):
        if duration % 5 == 0:  # Change this to 5 or any number that fits your testing duration
            total_salaries = Employee.SALARY_PER_EMPLOYEE * len(self.employees)
            self.cash_flow['expenses'] += total_salaries
            self.salary_expense += total_salaries

    def generate_financial_report(self) -> Dict[str, float]:
        self.cash_flow['net_profit'] = self.cash_flow['revenue'] - self.cash_flow['expenses']
        return self.cash_flow

# Real-time Simulation Function
def real_time_simulation(store, duration=60):  # Extend the duration for better financial realism
    print("\n=== Let's dive into a realistic supermarket simulation! ===")
    for i in range(1, duration + 1):  # Start from 1 to match your existing code
        print(f"\n--- Minute {i} of Simulation ---")
        customer_name = f"Customer_{i}"
        customer = AdvancedCustomer(customer_name, preferences=["Apple", "Milk"], budget=20)
        for _ in range(3):
            customer.advanced_browse_item(store.inventory, supermarket_items)
        store.checkout_customer(customer, supermarket_items)
        
        # Pay salaries based on the time elapsed
        store.pay_salaries(i)

        # Rest of your existing code
        store.start_shift()
        low_stock_items = store.inventory.low_stock_alert()
        if low_stock_items:
            order = {item: 10 for item in low_stock_items}
            store.place_order(order, supplier1.available_items)
        time.sleep(1)
    
    final_financial_report = store.generate_financial_report()
    print("\n=== Comprehensive Financial Report ===")
    print(f"Total Revenue: ${final_financial_report['revenue']:.2f}")
    print(f"Total Expenses: ${final_financial_report['expenses']:.2f}")
    print(f"Net Profit: ${final_financial_report['net_profit']:.2f}")

# Initialize and Test the Simulation

# Initial stock and promotions
initial_stock = {'Apple': 10, 'Banana': 10, 'Milk': 10}
supermarket_items = {'Apple': 1.2, 'Banana': 0.5, 'Milk': 2.0}  # Pricing info
active_promotions = {'Apple': 0.1, 'Milk': 0.2}

# Initialize advanced inventory
advanced_inventory = AdvancedInventory(initial_stock)

# Initialize employees
employees = [Employee("Alice", "Cashier"), Employee("Bob", "stock_clerk"), Employee("Eve", "Manager")]

# Initialize supplier
supplier1 = Supplier("FruitCo", {"Apple": 1.0, "Banana": 0.4, "Milk": 1.8}, delivery_time=1)

# Initialize the store
final_store = FinancialManagedStore(advanced_inventory, active_promotions, employees, supplier1)

# Run the real-time simulation for 5 minutes (For demo, 1 real second = 1 simulation minute)
real_time_simulation(final_store, duration=5)
