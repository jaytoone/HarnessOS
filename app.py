"""
Main application that connects all components (Store, Cache, Events, API) 
using dependency injection pattern.
"""
from http.server import HTTPServer
from typing import Protocol

from store import InMemoryStore, BaseStore
from cache import CachedStore
from events import event_manager, Event, EventType
from api import APIRequestHandler, create_app
from models import Product, Category


# Protocol classes for dependency injection
class StoreProtocol(Protocol):
    """Protocol defining the store interface."""
    
    def add_product(self, product: Product) -> None: ...
    def remove_product(self, product_name: str) -> bool: ...
    def get_total_value(self) -> float: ...
    def search_by_name(self, query: str) -> list[Product]: ...


class CacheProtocol(Protocol):
    """Protocol defining the cache interface."""
    
    def add_product(self, product: Product) -> None: ...
    def remove_product(self, product_name: str) -> bool: ...
    def get_total_value(self) -> float: ...
    def search_by_name(self, query: str) -> list[Product]: ...


# Dependency Injection Container
class DIContainer:
    """
    Dependency Injection Container that manages component creation and wiring.
    """
    
    def __init__(self, use_cache: bool = True, cache_ttl: float = 60.0) -> None:
        self._use_cache = use_cache
        self._cache_ttl = cache_ttl
        self._store: BaseStore | None = None
        self._event_listeners_added = False
    
    @property
    def store(self) -> BaseStore:
        """Get or create the store instance with dependency injection."""
        if self._store is None:
            # Create the base store
            base_store = InMemoryStore()
            
            # Apply cache decorator if enabled (Dependency Injection)
            if self._use_cache:
                self._store = CachedStore(base_store, ttl=self._cache_ttl)
            else:
                self._store = base_store
        
        return self._store
    
    def setup_event_listeners(self) -> None:
        """Set up event listeners for logging/analytics."""
        if self._event_listeners_added:
            return
            
        def log_product_added(event: Event) -> None:
            product = event.data.get('product')
            print(f"[EVENT] Product added: {product.name if product else 'Unknown'}")
        
        def log_product_removed(event: Event) -> None:
            product = event.data.get('product')
            print(f"[EVENT] Product removed: {product.name if product else 'Unknown'}")
        
        # Subscribe event listeners to the event manager
        event_manager.subscribe(EventType.PRODUCT_ADDED, log_product_added)
        event_manager.subscribe(EventType.PRODUCT_REMOVED, log_product_removed)
        
        self._event_listeners_added = True
    
    def create_api_handler(self) -> type:
        """Create the API request handler with injected store dependency."""
        return create_app(self.store)
    
    def run_server(self, host: str = '0.0.0.0', port: int = 8000) -> None:
        """Run the API server with all components wired together."""
        # Set up event listeners
        self.setup_event_listeners()
        
        # Create API handler with injected store
        handler_class = self.create_api_handler()
        
        # Create and start HTTP server
        server = HTTPServer((host, port), handler_class)
        print(f"=" * 50)
        print(f"Starting Store API Server")
        print(f"=" * 50)
        print(f"Server running on http://{host}:{port}")
        print(f"Components wired:")
        print(f"  - Store: {'CachedStore (TTL=' + str(self._cache_ttl) + 's)' if self._use_cache else 'InMemoryStore'}")
        print(f"  - Events: EventManager with PRODUCT_ADDED and PRODUCT_REMOVED listeners")
        print(f"  - API: REST endpoints")
        print(f"=" * 50)
        print(f"Available endpoints:")
        print(f"  GET    /products")
        print(f"  POST   /products")
        print(f"  DELETE /products/{{name}}")
        print(f"=" * 50)
        server.serve_forever()


# Application Factory
def create_application(use_cache: bool = True, cache_ttl: float = 60.0) -> DIContainer:
    """
    Factory function to create the application with dependency injection.
    
    Args:
        use_cache: Whether to use caching
        cache_ttl: Cache time-to-live in seconds
    
    Returns:
        Configured DIContainer instance
    """
    container = DIContainer(use_cache=use_cache, cache_ttl=cache_ttl)
    return container


# Add sample data to the store
def add_sample_data(store: BaseStore) -> None:
    """Add sample products to the store."""
    sample_products = [
        Product(
            name='Apple',
            price=1.5,
            quantity=100,
            category=Category(name='Fruit', description='Fresh fruits')
        ),
        Product(
            name='Banana',
            price=0.8,
            quantity=150,
            category=Category(name='Fruit', description='Fresh fruits')
        ),
        Product(
            name='Orange',
            price=2.0,
            quantity=80,
            category=Category(name='Fruit', description='Fresh fruits')
        ),
        Product(
            name='Milk',
            price=3.5,
            quantity=50,
            category=Category(name='Dairy', description='Dairy products')
        ),
        Product(
            name='Bread',
            price=2.5,
            quantity=60,
            category=Category(name='Bakery', description='Baked goods')
        ),
    ]
    
    for product in sample_products:
        store.add_product(product)


# Main entry point
if __name__ == '__main__':
    # Create application with dependency injection
    # Use cache with 60 second TTL
    app = create_application(use_cache=True, cache_ttl=60.0)
    
    # Add sample data to demonstrate functionality
    add_sample_data(app.store)
    
    # Run the server on port 52930 (from runtime info)
    # Using 0.0.0.0 to allow access from any host
    app.run_server(host='0.0.0.0', port=52930)