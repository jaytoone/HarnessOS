"""Product store: BaseStore abstract class and InMemoryStore implementation with persistence."""
import json
from abc import ABC, abstractmethod
from models import Product, Category, ProductDict
from events import event_manager, Event, EventType


class BaseStore(ABC):
    """Abstract base class for store implementations."""

    @property
    @abstractmethod
    def products(self) -> list[Product]:
        """Get all products in the store."""
        pass

    @abstractmethod
    def add_product(self, product: Product) -> None:
        """Add a product to the store."""
        pass

    @abstractmethod
    def remove_product(self, product_name: str) -> bool:
        """Remove a product by name. Returns True if product was found and removed."""
        pass

    @abstractmethod
    def get_total_value(self) -> float:
        """Calculate the total value of all products (price * quantity)."""
        pass

    @abstractmethod
    def search_by_name(self, query: str) -> list[Product]:
        """Search for products by name (case-insensitive)."""
        pass


class InMemoryStore(BaseStore):
    """In-memory implementation of the store."""

    def __init__(self) -> None:
        self._products: list[Product] = []
    
    @property
    def products(self) -> list[Product]:
        """Get all products in the store."""
        return self._products

    def add_product(self, product: Product) -> None:
        """Add a product to the store."""
        self._products.append(product)
        event = Event(
            event_type=EventType.PRODUCT_ADDED,
            data={"product": product}
        )
        event_manager.notify(event)

    def remove_product(self, product_name: str) -> bool:
        """Remove a product by name. Returns True if product was found and removed."""
        for i, product in enumerate(self._products):
            if product.name == product_name:
                removed_product = self._products.pop(i)
                event = Event(
                    event_type=EventType.PRODUCT_REMOVED,
                    data={"product": removed_product}
                )
                event_manager.notify(event)
                return True
        return False

    def get_total_value(self) -> float:
        """Calculate the total value of all products (price * quantity)."""
        return sum(p.price * p.quantity for p in self._products)

    def search_by_name(self, query: str) -> list[Product]:
        """Search for products by name (case-insensitive)."""
        query_lower = query.lower()
        return [p for p in self._products if query_lower in p.name.lower()]

    def save_to_file(self, filepath: str) -> None:
        """Save the store data to a JSON file."""
        data = [product.to_dict() for product in self._products]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, filepath: str) -> None:
        """Load the store data from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._products = [Product.from_dict(item) for item in data]


# Backward compatibility alias
Store = InMemoryStore