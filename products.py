
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, Category, Supplier
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    InventoryValueResponse,
)
from app.exceptions import commit_or_raise, get_or_404

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    get_or_404(db, Category, data.category_id, "Category")
    get_or_404(db, Supplier, data.supplier_id, "Supplier")

    product = Product(**data.model_dump())
    db.add(product)
    commit_or_raise(db, "Product could not be created")
    db.refresh(product)
    return product


@router.get("/inventory-value", response_model=InventoryValueResponse)
def inventory_value(db: Session = Depends(get_db)):
    value = db.scalar(
        select(func.coalesce(func.sum(Product.price * Product.quantity), 0))
    )
    return InventoryValueResponse(total_inventory_value=value)


@router.get("", response_model=list[ProductResponse])
def get_products(
    search: str | None = Query(default=None, min_length=1),
    category_id: int | None = Query(default=None, gt=0),
    supplier_id: int | None = Query(default=None, gt=0),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                422, "min_price cannot be greater than max_price"
            )

    stmt = select(Product)

    if search:
        stmt = stmt.where(Product.product_name.ilike(f"%{search.strip()}%"))
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if supplier_id is not None:
        stmt = stmt.where(Product.supplier_id == supplier_id)
    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    stmt = stmt.order_by(Product.product_id).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Product, product_id, "Product")


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = get_or_404(db, Product, product_id, "Product")
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(400, "Provide at least one field to update")

    if changes.get("category_id") is not None:
        get_or_404(db, Category, changes["category_id"], "Category")
    if changes.get("supplier_id") is not None:
        get_or_404(db, Supplier, changes["supplier_id"], "Supplier")

    for key, value in changes.items():
        setattr(product, key, value)

    commit_or_raise(db, "Product could not be updated")
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = get_or_404(db, Product, product_id, "Product")
    db.delete(product)
    commit_or_raise(db, "Product could not be deleted")
    return None
