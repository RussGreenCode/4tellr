import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi import Request
from services.login_services import LoginServices

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


def get_login_helper(request: Request):
    return LoginServices(request.app.state.DB_HELPER, request.app.state.LOGG    ER)


@router.post("/api/login")
async def login(request: LoginRequest, req: Request, login_helper: LoginServices = Depends(get_login_helper)):
    email = request.email
    password = request.password

    try:
        user = login_helper.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return {"isAuthenticated": True, "user": user}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/logout")
async def logout():
    return {"message": "Logged out successfully"}
