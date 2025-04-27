# hr-service/app/core/auth_client.py
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.AUTH_SERVICE_URL}/auth/login")

async def verify_token(token: str):
    """
    Verify token with the Auth Service
    """
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/users/me", 
                headers=headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Verify current user with Auth Service
    """
    user = await verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Check if the current user is active
    """
    if not current_user.get("is_active"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_pm_user(current_user: dict = Depends(get_current_active_user)):
    """
    Check if the current user has HR role
    """
    if current_user.get("role") not in ["admin", "pm"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. PM role required."
        )
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """
    Check if the current user is an administrator
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user