
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
)


Name = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=150),
]
CategoryName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=100),
]
Description = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]
PositivePrice = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
NonNegativeQuantity = Annotated[int, Field(ge=0)]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------- CATEGORIES ----------------

class CategoryCreate(BaseModel):
    category_name: CategoryName
    description: str | None = None


class CategoryUpdate(BaseModel):
    category_name: CategoryName | None = None
    description: str | None = None


class CategoryResponse(ORMModel):
    category_id: int
    category_name: str
    description: str | None
    created_date: datetime


# ---------------- SUPPLIERS ----------------

class SupplierCreate(BaseModel):
    supplier_name: Name
    email: EmailStr
    phone_number: str | None = Field(default=None, max_length=30)
    address: str | None = None
    company_name: str | None = Field(default=None, max_length=150)


class SupplierUpdate(BaseModel):
    supplier_name: Name | None = None
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=30)
    address: str | None = None
    company_name: str | None = Field(default=None, max_length=150)


class SupplierResponse(ORMModel):
    supplier_id: int
    supplier_name: str
    email: EmailStr
    phone_number: str | None
    address: str | None
    company_name: str | None
    created_date: datetime


# ---------------- PRODUCTS ----------------

class ProductCreate(BaseModel):
    product_name: Name
    description: str | None = None
    category_id: int = Field(gt=0)
    supplier_id: int = Field(gt=0)
    price: PositivePrice
    quantity: NonNegativeQuantity = 0


class ProductUpdate(BaseModel):
    product_name: Name | None = None
    description: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    supplier_id: int | None = Field(default=None, gt=0)
    price: PositivePrice | None = None
    quantity: NonNegativeQuantity | None = None


class ProductResponse(ORMModel):
    product_id: int
    product_name: str
    description: str | None
    category_id: int
    supplier_id: int
    price: Decimal
    quantity: int
    created_date: datetime
    updated_date: datetime


class InventoryValueResponse(BaseModel):
    total_inventory_value: Decimal
    currency: str = "database price units"
