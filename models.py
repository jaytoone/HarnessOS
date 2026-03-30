"""Product and Category data models with to_dict/from_dict serialization."""
from dataclasses import dataclass
from typing import Any, TypeAlias


CategoryDict: TypeAlias = dict[str, str]
ProductDict: TypeAlias = dict[str, Any]


@dataclass(frozen=True)
class Category:
    """Product category with a name and description."""

    name: str
    description: str

    def to_dict(self) -> CategoryDict:
        """Serialize to a plain dict."""
        return {
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: CategoryDict) -> 'Category':
        """Deserialize from a plain dict."""
        return cls(
            name=data['name'],
            description=data['description']
        )


@dataclass(frozen=True)
class Product:
    """Store product with name, price, quantity, and optional category."""

    name: str
    price: float
    quantity: int
    category: Category | None = None

    def to_dict(self) -> ProductDict:
        """Serialize to a plain dict."""
        return {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'category': self.category.to_dict() if self.category else None
        }

    @classmethod
    def from_dict(cls, data: ProductDict) -> 'Product':
        """Deserialize from a plain dict."""
        category_data: CategoryDict | None = data.get('category')
        category = Category.from_dict(category_data) if category_data else None
        return cls(
            name=data['name'],
            price=data['price'],
            quantity=data['quantity'],
            category=category
        )
