"""Product and Category data models with to_dict/from_dict serialization."""
from dataclasses import dataclass
from typing import Any, TypeAlias


CategoryDict: TypeAlias = dict[str, str]
ProductDict: TypeAlias = dict[str, Any]


@dataclass
class Category:
    name: str
    description: str

    def to_dict(self) -> CategoryDict:
        return {
            'name': self.name,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data: CategoryDict) -> 'Category':
        return cls(
            name=data['name'],
            description=data['description']
        )


@dataclass
class Product:
    name: str
    price: float
    quantity: int
    category: Category | None = None

    def to_dict(self) -> ProductDict:
        return {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'category': self.category.to_dict() if self.category else None
        }

    @classmethod
    def from_dict(cls, data: ProductDict) -> 'Product':
        category_data: CategoryDict | None = data.get('category')
        category = Category.from_dict(category_data) if category_data else None
        return cls(
            name=data['name'],
            price=data['price'],
            quantity=data['quantity'],
            category=category
        )