from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from mysql.connector import Error

from app.db import get_db_connection
from app.schemas.products import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


def _handle_db_error(exc: Error, fallback: str):
    if exc.errno == 1062:
        raise HTTPException(status_code=400, detail="SKU already exists")
    if exc.errno == 1452:
        raise HTTPException(status_code=400, detail="Invalid user_id or category_id")
    if exc.errno == 1048:
        raise HTTPException(status_code=400, detail=f"Missing required field: {exc.msg}")
    raise HTTPException(status_code=500, detail=fallback)


@router.post("/", response_model=ProductOut, status_code=201)
def create_product(product: ProductCreate):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            insert into products(
                user_id, category_id, name, sku, description, unit_price,
                stock, reorder_threshold, overstock_threshold
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                product.user_id,
                product.category_id,
                product.name,
                product.sku,
                product.description,
                product.unit_price,
                product.stock,
                product.reorder_threshold,
                product.overstock_threshold,
            )
        )
        product_id = cursor.lastrowid
        connection.commit()

        cursor.execute(
            """
            select id, user_id, category_id, name, sku, description, unit_price,
                   stock, reorder_threshold, overstock_threshold, created_at
            from products
            where id = %s
            """,
            (product_id,)
        )
        return cursor.fetchone()
    except Error as exc:
        _handle_db_error(exc, "Failed to create product")
    finally:
        cursor.close()
        connection.close()


@router.get("/", response_model=List[ProductOut])
def list_products(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None
):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        base_query = (
            "select id, user_id, category_id, name, sku, description, unit_price, "
            "stock, reorder_threshold, overstock_threshold, created_at "
            "from products"
        )
        params = []
        if search:
            base_query += " where name like %s or sku like %s"
            like_value = f"%{search}%"
            params.extend([like_value, like_value])

        base_query += " order by id desc limit %s offset %s"
        params.extend([limit, offset])

        cursor.execute(base_query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            select id, user_id, category_id, name, sku, description, unit_price,
                   stock, reorder_threshold, overstock_threshold, created_at
            from products
            where id = %s
            """,
            (product_id,)
        )
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        cursor.close()
        connection.close()


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, product: ProductUpdate):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        fields = []
        values = []
        for field_name, value in product.dict(exclude_unset=True).items():
            if value is not None:
                fields.append(f"{field_name} = %s")
                values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        query = f"update products set {', '.join(fields)} where id = %s"
        values.append(product_id)
        cursor.execute(query, tuple(values))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        connection.commit()
        cursor.execute(
            """
            select id, user_id, category_id, name, sku, description, unit_price,
                   stock, reorder_threshold, overstock_threshold, created_at
            from products
            where id = %s
            """,
            (product_id,)
        )
        return cursor.fetchone()
    except Error as exc:
        _handle_db_error(exc, "Failed to update product")
    finally:
        cursor.close()
        connection.close()


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("delete from products where id = %s", (product_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        connection.commit()
        return None
    except Error as exc:
        _handle_db_error(exc, "Failed to delete product")
    finally:
        cursor.close()
        connection.close()