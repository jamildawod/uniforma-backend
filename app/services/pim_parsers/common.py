from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class NormalizedVariant:
    sku: str
    ean: str | None = None
    size: str | None = None
    color: str | None = None
    price: Decimal | None = None
    stock_quantity: int = 0
    is_active: bool = True


@dataclass(slots=True)
class NormalizedProduct:
    name: str
    description: str | None = None
    brand: str | None = None
    category: str | None = None
    external_id: str | None = None
    variants: list[NormalizedVariant] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)

