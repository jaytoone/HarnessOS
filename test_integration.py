"""
Integration tests for the entire system.
Tests the full flow: Add product → Cache check → Event triggering → API query.
"""
import json
import time
import threading
import unittest
from http.client import HTTPConnection
from typing import Any

from store import InMemoryStore, BaseStore
from cache import CachedStore
from events import event_manager, Event, EventType
from api import create_app
from models import Product, Category
from app import DIContainer


class IntegrationTest(unittest.TestCase):
    """Integration tests for the complete system flow."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the test server once for all tests."""
        # Use port 57924 from the runtime information
        cls.server_port = 57924
        cls.base_url = f'http://localhost:{cls.server_port}'
        
        # Create a fresh container with cache enabled
        cls.container = DIContainer(use_cache=True, cache_ttl=60.0)
        cls.container.setup_event_listeners()
        
        # Create API handler
        cls.handler_class = cls.container.create_api_handler()
        
        # Start the server in a background thread
        from http.server import HTTPServer
        cls.server = HTTPServer(('0.0.0.0', cls.server_port), cls.handler_class)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(0.5)
        
        # Track events for verification
        cls.events_received = []
        
        # Add custom listener to track events
        def track_event(event: Event) -> None:
            cls.events_received.append(event)
        
        event_manager.subscribe(EventType.PRODUCT_ADDED, track_event)
        event_manager.subscribe(EventType.PRODUCT_REMOVED, track_event)

    @classmethod
    def tearDownClass(cls) -> None:
        """Shut down the test server."""
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self) -> None:
        """Clear state before each test."""
        # Clear events
        self.events_received.clear()
        
        # Create fresh store for each test
        self.store = InMemoryStore()
        self.cached_store = CachedStore(self.store, ttl=60.0)
        
        # Update API handler's store
        IntegrationTest.handler_class.store = self.cached_store
        
        # Clear event listeners and re-add tracking
        event_manager.clear_listeners()
        
        def track_event(event: Event) -> None:
            self.events_received.append(event)
        
        event_manager.subscribe(EventType.PRODUCT_ADDED, track_event)
        event_manager.subscribe(EventType.PRODUCT_REMOVED, track_event)

    def _make_request(self, method: str, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make an HTTP request to the test server."""
        conn = HTTPConnection('localhost', self.server_port)
        headers = {'Content-Type': 'application/json'}
        
        if data:
            body = json.dumps(data).encode('utf-8')
            if method == 'GET':
                conn.request(method, path, headers=headers)
            else:
                conn.request(method, path, body=body, headers=headers)
        else:
            conn.request(method, path, headers=headers)
        
        response = conn.getresponse()
        response_body = response.read().decode('utf-8')
        conn.close()
        
        return {
            'status': response.status,
            'body': json.loads(response_body) if response_body else {}
        }

    def test_full_flow_add_product_check_cache_trigger_event_query_api(self) -> None:
        """Test the complete flow: Add product → Check cache → Event triggered → Query API."""
        
        # Step 1: Add a product via API
        new_product = {
            'name': 'TestProduct',
            'price': 10.0,
            'quantity': 50,
            'category': {
                'name': 'Electronics',
                'description': 'Electronic devices'
            }
        }
        
        # Make POST request to add product
        response = self._make_request('POST', '/products', new_product)
        self.assertEqual(response['status'], 201, f"Failed to add product: {response}")
        self.assertIn('product', response['body'])
        self.assertEqual(response['body']['product']['name'], 'TestProduct')
        
        # Step 2: Verify cache behavior - first call should cache the result
        # Get total value (this will be cached)
        initial_total = self.cached_store.get_total_value()
        self.assertEqual(initial_total, 500.0)  # 10.0 * 50 = 500.0
        
        # Add another product to invalidate cache
        second_product = {
            'name': 'TestProduct2',
            'price': 5.0,
            'quantity': 20,
            'category': {
                'name': 'Electronics',
                'description': 'Electronic devices'
            }
        }
        self.cached_store.add_product(Product.from_dict(second_product))
        
        # Step 3: Verify events were triggered
        # Check that PRODUCT_ADDED events were fired
        product_added_events = [
            e for e in self.events_received 
            if e.event_type == EventType.PRODUCT_ADDED
        ]
        self.assertGreaterEqual(len(product_added_events), 2, 
            f"Expected at least 2 PRODUCT_ADDED events, got {len(product_added_events)}")
        
        # Verify event data contains product information
        for event in product_added_events:
            self.assertIn('product', event.data)
            self.assertIsNotNone(event.data['product'])
        
        # Step 4: Query API to verify data
        response = self._make_request('GET', '/products')
        self.assertEqual(response['status'], 200)
        self.assertIn('products', response['body'])
        
        products = response['body']['products']
        self.assertEqual(len(products), 2)
        
        # Verify the products are correct
        product_names = [p['name'] for p in products]
        self.assertIn('TestProduct', product_names)
        self.assertIn('TestProduct2', product_names)

    def test_cache_invalidation_on_product_removal(self) -> None:
        """Test that cache is properly invalidated when a product is removed."""
        
        # Add a product
        product = Product(
            name='CacheTestProduct',
            price=15.0,
            quantity=10,
            category=Category(name='Test', description='Test category')
        )
        self.cached_store.add_product(product)
        
        # Get total value (should be cached)
        total1 = self.cached_store.get_total_value()
        self.assertEqual(total1, 150.0)
        
        # Get total value again (should use cache)
        total2 = self.cached_store.get_total_value()
        self.assertEqual(total1, total2)
        
        # Remove the product
        self.cached_store.remove_product('CacheTestProduct')
        
        # Get total value again (cache should be invalidated)
        total3 = self.cached_store.get_total_value()
        self.assertEqual(total3, 0.0)

    def test_event_data_structure(self) -> None:
        """Test that events contain correct data structure."""
        
        # Clear events
        self.events_received.clear()
        
        # Add a product
        product = Product(
            name='EventTestProduct',
            price=20.0,
            quantity=5,
            category=Category(name='Events', description='Event test')
        )
        self.cached_store.add_product(product)
        
        # Verify event was triggered
        self.assertEqual(len(self.events_received), 1)
        
        event = self.events_received[0]
        self.assertEqual(event.event_type, EventType.PRODUCT_ADDED)
        self.assertIn('product', event.data)
        
        event_product = event.data['product']
        self.assertEqual(event_product.name, 'EventTestProduct')
        self.assertEqual(event_product.price, 20.0)
        self.assertEqual(event_product.quantity, 5)

    def test_api_reflects_store_changes(self) -> None:
        """Test that API correctly reflects changes made to the store."""
        
        # Initial API call - should be empty
        response = self._make_request('GET', '/products')
        self.assertEqual(len(response['body']['products']), 0)
        
        # Add products directly to store
        self.cached_store.add_product(Product(
            name='APITest1',
            price=1.0,
            quantity=10,
            category=Category(name='Test', description='Test')
        ))
        self.cached_store.add_product(Product(
            name='APITest2',
            price=2.0,
            quantity=20,
            category=Category(name='Test', description='Test')
        ))
        
        # API should reflect the changes
        response = self._make_request('GET', '/products')
        self.assertEqual(len(response['body']['products']), 2)
        
        # Delete a product via API
        response = self._make_request('DELETE', '/products/APITest1')
        self.assertEqual(response['status'], 200)
        
        # API should reflect the deletion
        response = self._make_request('GET', '/products')
        self.assertEqual(len(response['body']['products']), 1)
        self.assertEqual(response['body']['products'][0]['name'], 'APITest2')


if __name__ == '__main__':
    unittest.main()