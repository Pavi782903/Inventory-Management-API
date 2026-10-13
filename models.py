
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    Numeric,
    CheckConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    category_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    category_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="category"
    )


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    supplier_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_name: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="supplier"
    )


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint("price > 0", name="chk_product_price"),
        CheckConstraint("quantity >= 0", name="chk_product_quantity"),
        Index("idx_products_category", "category_id"),
        Index("idx_products_supplier", "supplier_id"),
    )

    product_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    product_name: Mapped[str] = mapped_column(
        String(150), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.category_id", ondelete="RESTRICT"),
        nullable=False,
    )
    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.supplier_id", ondelete="RESTRICT"),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    created_date: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        back_populates="products"
    )
    supplier: Mapped["Supplier"] = relationship(
        back_populates="products"
    )
