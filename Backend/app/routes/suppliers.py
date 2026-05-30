from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from mysql.connector import Error

from app.db import get_db_connection
from app.schemas.suppliers import SupplierCreate, SupplierOut, SupplierUpdate

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)


def _handle_db_error(exc: Error, fallback: str):
    if exc.errno == 1062:
        raise HTTPException(status_code=400, detail="Duplicate value violates unique constraint")
    if exc.errno == 1452:
        raise HTTPException(status_code=400, detail="Invalid foreign key reference")
    if exc.errno == 1048:
        raise HTTPException(status_code=400, detail=f"Missing required field: {exc.msg}")
    raise HTTPException(status_code=500, detail=fallback)


@router.post("/", response_model=SupplierOut, status_code=201)
def create_supplier(supplier: SupplierCreate):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            insert into suppliers(
                name, contact_name, email, phone, avg_lead_days, reliability_score
            )
            values (%s, %s, %s, %s, %s, %s)
            """,
            (
                supplier.name,
                supplier.contact_name,
                supplier.email,
                supplier.phone,
                supplier.avg_lead_days,
                supplier.reliability_score,
            )
        )
        supplier_id = cursor.lastrowid
        connection.commit()

        cursor.execute(
            """
            select id, name, contact_name, email, phone, avg_lead_days,
                   reliability_score, created_at
            from suppliers
            where id = %s
            """,
            (supplier_id,)
        )
        return cursor.fetchone()
    except Error as exc:
        _handle_db_error(exc, "Failed to create supplier")
    finally:
        cursor.close()
        connection.close()


@router.get("/", response_model=List[SupplierOut])
def list_suppliers(
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
            "select id, name, contact_name, email, phone, avg_lead_days, "
            "reliability_score, created_at "
            "from suppliers"
        )
        params = []
        if search:
            base_query += " where name like %s or email like %s or phone like %s"
            like_value = f"%{search}%"
            params.extend([like_value, like_value, like_value])

        base_query += " order by id desc limit %s offset %s"
        params.extend([limit, offset])

        cursor.execute(base_query, tuple(params))
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            select id, name, contact_name, email, phone, avg_lead_days,
                   reliability_score, created_at
            from suppliers
            where id = %s
            """,
            (supplier_id,)
        )
        supplier = cursor.fetchone()
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        return supplier
    finally:
        cursor.close()
        connection.close()


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, supplier: SupplierUpdate):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        fields = []
        values = []
        for field_name, value in supplier.dict(exclude_unset=True).items():
            if value is not None:
                fields.append(f"{field_name} = %s")
                values.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        query = f"update suppliers set {', '.join(fields)} where id = %s"
        values.append(supplier_id)
        cursor.execute(query, tuple(values))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Supplier not found")

        connection.commit()
        cursor.execute(
            """
            select id, name, contact_name, email, phone, avg_lead_days,
                   reliability_score, created_at
            from suppliers
            where id = %s
            """,
            (supplier_id,)
        )
        return cursor.fetchone()
    except Error as exc:
        _handle_db_error(exc, "Failed to update supplier")
    finally:
        cursor.close()
        connection.close()


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int):
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("delete from suppliers where id = %s", (supplier_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Supplier not found")
        connection.commit()
        return None
    except Error as exc:
        _handle_db_error(exc, "Failed to delete supplier")
    finally:
        cursor.close()
        connection.close()