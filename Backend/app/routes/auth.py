from fastapi import APIRouter, HTTPException
from schemas.auth import SignupRequest
from db import get_db_connection
from utils.security import hash_password

# every router will start from /auth
router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)

@router.post("/signup")
def signup(user: SignupRequest):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(status_code = 500, detail = "Database connection failed")
    
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "Select id from users where email = %s",
        (user.email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        raise HTTPException(status_code = 400, detail="Email already registered")
    
    password_hash = hash_password(user.password)

    cursor.execute(
        """
        insert into users(name, email, password_hash)
        values (%s, %s, %s)
        """,

    )
