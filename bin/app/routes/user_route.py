from fastapi import APIRouter
from app.service import register_user
from app.models import RegisterUser

user_route = APIRouter(
    prefix="/api/v1/usr",
    tags=["userRouter"]
)

@user_route.post("/signup")
def main(user:RegisterUser):
    # return "hello"
    return register_user(user)
