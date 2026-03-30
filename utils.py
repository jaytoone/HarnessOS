"""Store serialization utilities: CSV export (to_csv) and import (from_csv)."""
from store import BaseStore, InMemoryStore
from models import Product, Category


def from_csv(csv_string: str) -> InMemoryStore:
    """Convert a CSV format string to a Store."""
    store = InMemoryStore()
    
    lines = csv_string.strip().split('\n')
    if not lines:
        return store
    
    # Skip header if present
    if lines[0] == "name,price,quantity,category":
        lines = lines[1:]
    
    for line in lines:
        if not line.strip():
            continue
        
        parts = line.split(',')
        if len(parts) >= 4:
            name = parts[0]
            price = float(parts[1])
            quantity = int(parts[2])
            category_name = parts[3] if parts[3] else None
            
            category = Category(name=category_name, description="") if category_name else None
            store.add_product(Product(name=name, price=price, quantity=quantity, category=category))
    
    return store


def to_csv(store: BaseStore) -> str:
    """Convert a Store's product list to CSV format string."""
    if not store.products:
        return "name,price,quantity,category\n"
    
    lines = ["name,price,quantity,category"]
    for product in store.products:
        category_name = product.category.name if product.category else ""
        lines.append(f"{product.name},{product.price},{product.quantity},{category_name}")
    
    return "\n".join(lines)