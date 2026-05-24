from fastapi import APIRouter

# every router will start from /auth
router = APIRouter(
    prefix = "/auth",
    tags = ["Auth"]
)

@router.get("/test")
def test_auth():
    return {"message" : "Auth is working"}