
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Supplier, Product
from app.schemas import (
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
    ProductResponse,
)
from app.exceptions import commit_or_raise, get_or_404

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    existing = db.scalar(
        select(Supplier).where(func_lower_email() == email)
    )
    if existing:
        raise HTTPException(409, "Supplier email already exists")

    values = data.model_dump()
    values["email"] = email
    supplier = Supplier(**values)
    db.add(supplier)
    commit_or_raise(db, "Supplier email already exists")
    db.refresh(supplier)
    return supplier


@router.get("", response_model=list[SupplierResponse])
def get_suppliers(db: Session = Depends(get_db)):
    return db.scalars(
        select(Supplier).order_by(Supplier.supplier_id)
    ).all()


@router.get("/{supplier_id}/products", response_model=list[ProductResponse])
def get_supplier_products(
    supplier_id: int, db: Session = Depends(get_db)
):
    get_or_404(db, Supplier, supplier_id, "Supplier")
    return db.scalars(
        select(Product)
        .where(Product.supplier_id == supplier_id)
        .order_by(Product.product_id)
    ).all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Supplier, supplier_id, "Supplier")


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
):
    supplier = get_or_404(db, Supplier, supplier_id, "Supplier")
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(400, "Provide at least one field to update")

    if "email" in changes and changes["email"] is not None:
        changes["email"] = str(changes["email"]).lower()
        duplicate = db.scalar(
            select(Supplier).where(
                Supplier.email == changes["email"],
                Supplier.supplier_id != supplier_id,
            )
        )
        if duplicate:
            raise HTTPException(409, "Supplier email already exists")

    for key, value in changes.items():
        setattr(supplier, key, value)

    commit_or_raise(db, "Supplier email already exists")
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = get_or_404(db, Supplier, supplier_id, "Supplier")

    if supplier.products:
        raise HTTPException(
            409, "Cannot delete supplier while products reference it"
        )

    db.delete(supplier)
    commit_or_raise(db, "Cannot delete supplier while products reference it")
    return None
