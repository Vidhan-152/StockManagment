from fastapi import APIRouter, HTTPException, Header
from app.schemas.auth import SignupRequest, LoginRequest, AuthResponse
from app.db import get_db_connection
from app.utils.security import hash_password, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

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
        (user.name, user.email, password_hash)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return {"message": "User registered successfully"}


@router.post("/login", response_model = AuthResponse)
def login(user: LoginRequest):
    connection = get_db_connection()

    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "Select id, name, email, password_hash from users where email = %s",
        (user.email,)
    )

    db_user = cursor.fetchone()

    if not db_user:
        cursor.close()
        connection.close()
        raise HTTPException(status_code = 401, detail="Invalid credentials")
    
    if not verify_password(user.password, db_user["password_hash"]):
        cursor.close()
        connection.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    cursor.close()
    connection.close()

    token = create_access_token({"sub": db_user["email"]})

    return AuthResponse(access_token=token)

@router.get("/me")
def me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "Select id, name, email from users where email = %s",
        (email,)
    )

    db_user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return{
        "id": db_user["id"],
        "name": db_user["name"],
        "email": db_user["email"]
    }


