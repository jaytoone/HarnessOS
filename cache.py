"""TTL-based caching decorator for Store using the Decorator pattern."""
import time
from typing import Any
from store import InMemoryStore, BaseStore
from models import Product


class CachedStore(BaseStore):
    """Decorator class that adds TTL-based caching to an InMemoryStore."""

    def __init__(self, store: InMemoryStore, ttl: float = 60.0) -> None:
        self._store = store
        self._ttl = ttl
        self._cache: dict[str, tuple[Any, float]] = {}

    def _get_cached(self, key: str) -> Any | None:
        """Get a value from cache if it exists and is not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        """Set a value in cache with current timestamp."""
        self._cache[key] = (value, time.time())

    @property
    def products(self) -> list[Product]:
        """Get all products from the underlying store."""
        return self._store.products
    
    def _invalidate_cache(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def add_product(self, product: Product) -> None:
        """Add a product to the store."""
        self._store.add_product(product)
        self._invalidate_cache()

    def remove_product(self, product_name: str) -> bool:
        """Remove a product by name. Returns True if product was found and removed."""
        result = self._store.remove_product(product_name)
        if result:
            self._invalidate_cache()
        return result

    def get_total_value(self) -> float:
        """Calculate the total value of all products (price * quantity)."""
        cache_key = "get_total_value"
        cached_result = self._get_cached(cache_key)
        if cached_result is not None:
            return cached_result

        result = self._store.get_total_value()
        self._set_cached(cache_key, result)
        return result

    def search_by_name(self, query: str) -> list[Product]:
        """Search for products by name (case-insensitive)."""
        cache_key = f"search_by_name:{query}"
        cached_result = self._get_cached(cache_key)
        if cached_result is not None:
            return cached_result

        result = self._store.search_by_name(query)
        self._set_cached(cache_key, result)
        return result