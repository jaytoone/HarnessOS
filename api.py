"""
REST API layer for Store using pure Python (no FastAPI).
Uses routing dictionary approach.
"""
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse

from store import BaseStore, Store
from models import Category, Product


class APIRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler with routing dictionary."""

    store: BaseStore | None = None  # Will be set when server starts

    def _send_json_response(self, status_code: int, data: Any) -> None:
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _get_request_body(self) -> dict[str, Any]:
        """Parse JSON body from request."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))
        return {}
    
    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self) -> None:
        """Handle GET requests using routing dictionary."""
        # Routing dictionary for GET
        routes = {
            '/products': self._get_products,
        }
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        handler = routes.get(path)
        if handler:
            handler()
        else:
            self._send_json_response(404, {'error': 'Not found'})
    
    def do_POST(self) -> None:
        """Handle POST requests using routing dictionary."""
        # Routing dictionary for POST
        routes = {
            '/products': self._post_products,
        }
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        handler = routes.get(path)
        if handler:
            handler()
        else:
            self._send_json_response(404, {'error': 'Not found'})
    
    def do_DELETE(self) -> None:
        """Handle DELETE requests using routing dictionary."""
        # Routing dictionary for DELETE
        # Format: /products/{name}
        
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Match pattern /products/{name}
        if path.startswith('/products/'):
            product_name = path[len('/products/'):]
            self._delete_product(product_name)
        else:
            self._send_json_response(404, {'error': 'Not found'})
    
    def _get_products(self) -> None:
        """GET /products - Get all products."""
        products = self.store.products
        product_list = [p.to_dict() for p in products]
        self._send_json_response(200, {'products': product_list})
    
    def _post_products(self) -> None:
        """POST /products - Add a new product."""
        try:
            data = self._get_request_body()
            
            # Parse category if provided
            category = None
            if 'category' in data and data['category']:
                category_data = data['category']
                category = Category(
                    name=category_data.get('name', ''),
                    description=category_data.get('description', '')
                )
            
            # Create product
            product = Product(
                name=data.get('name', ''),
                price=float(data.get('price', 0)),
                quantity=int(data.get('quantity', 0)),
                category=category
            )
            
            # Add to store
            self.store.add_product(product)
            
            self._send_json_response(201, {'message': 'Product added', 'product': product.to_dict()})
        except (ValueError, KeyError) as e:
            self._send_json_response(400, {'error': f'Invalid request: {str(e)}'})
    
    def _delete_product(self, product_name: str) -> None:
        """DELETE /products/{name} - Delete a product by name."""
        # URL decode the product name
        import urllib.parse
        product_name = urllib.parse.unquote(product_name)
        
        success = self.store.remove_product(product_name)
        
        if success:
            self._send_json_response(200, {'message': f'Product "{product_name}" deleted'})
        else:
            self._send_json_response(404, {'error': f'Product "{product_name}" not found'})


def create_app(store: BaseStore) -> type:
    """Create the API application with the given store."""
    APIRequestHandler.store = store
    return APIRequestHandler


def run_server(store: BaseStore, host: str = '0.0.0.0', port: int = 8000) -> None:
    """Run the API server."""
    handler_class = create_app(store)
    server = HTTPServer((host, port), handler_class)
    print(f'Starting server on http://{host}:{port}')
    print('Available endpoints:')
    print('  GET    /products')
    print('  POST   /products')
    print('  DELETE /products/{name}')
    server.serve_forever()


if __name__ == '__main__':
    # Create a store and run the server
    store = Store()
    
    # Add some sample data
    store.add_product(Product(
        name='Apple',
        price=1.5,
        quantity=100,
        category=Category(name='Fruit', description='Fresh fruits')
    ))
    store.add_product(Product(
        name='Banana',
        price=0.8,
        quantity=150,
        category=Category(name='Fruit', description='Fresh fruits')
    ))
    
    run_server(store, host='0.0.0.0', port=8000)