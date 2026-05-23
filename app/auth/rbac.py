from fastapi import Depends, HTTPException, status
from typing import List
from app.auth.jwt import get_current_active_user
from app.models.user import User


def require_roles(*roles: str):
    """Dependency factory that checks if the current user has one of the required roles."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}",
            )
        return current_user
    return role_checker


def require_patient(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in ("patient", "system_admin"):
        raise HTTPException(status_code=403, detail="Patient access required")
    return current_user


def require_driver(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in ("driver", "system_admin"):
        raise HTTPException(status_code=403, detail="Driver access required")
    return current_user


def require_doctor(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in ("doctor", "system_admin"):
        raise HTTPException(status_code=403, detail="Doctor access required")
    return current_user


def require_hospital_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role not in ("hospital_admin", "system_admin"):
        raise HTTPException(status_code=403, detail="Hospital admin access required")
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "system_admin":
        raise HTTPException(status_code=403, detail="System admin access required")
    return current_user
