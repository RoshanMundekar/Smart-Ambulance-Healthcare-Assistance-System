from .auth import router as auth_router
from .emergency import router as emergency_router
from .appointments import router as appointments_router
from .driver import router as driver_router
from .hospital import router as hospital_router
from .admin import router as admin_router

__all__ = [
    "auth_router", "emergency_router", "appointments_router",
    "driver_router", "hospital_router", "admin_router",
]
