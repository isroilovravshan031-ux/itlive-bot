from .user_handlers import router as user_router
from .registration import router as registration_router
from .quiz import router as quiz_router
from .feedback import router as feedback_router
from .sales_handlers import router as sales_router
from .admin_handlers import router as admin_router
from .admin_courses import router as admin_courses_router
from .admin_sales import router as admin_sales_router

__all__ = [
    "user_router",
    "registration_router",
    "quiz_router",
    "feedback_router",
    "sales_router",
    "admin_router",
    "admin_courses_router",
    "admin_sales_router"
]
