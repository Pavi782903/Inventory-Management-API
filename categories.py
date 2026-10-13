
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.exceptions import commit_or_raise, get_or_404

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.scalar(
        select(Category).where(Category.category_name == data.category_name)
    )
    if existing:
        raise HTTPException(409, "Category name already exists")

    category = Category(**data.model_dump())
    db.add(category)
    commit_or_raise(db, "Category name already exists")
    db.refresh(category)
    return category


@router.get("", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.scalars(
        select(Category).order_by(Category.category_id)
    ).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Category, category_id, "Category")


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = get_or_404(db, Category, category_id, "Category")
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(400, "Provide at least one field to update")

    if "category_name" in changes:
        duplicate = db.scalar(
            select(Category).where(
                Category.category_name == changes["category_name"],
                Category.category_id != category_id,
            )
        )
        if duplicate:
            raise HTTPException(409, "Category name already exists")

    for key, value in changes.items():
        setattr(category, key, value)

    commit_or_raise(db, "Category name already exists")
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = get_or_404(db, Category, category_id, "Category")

    if category.products:
        raise HTTPException(
            409, "Cannot delete category while products reference it"
        )

    db.delete(category)
    commit_or_raise(db, "Cannot delete category while products reference it")
    return None
