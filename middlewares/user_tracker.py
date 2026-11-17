from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from database.models import Database

class UserTrackerMiddleware(BaseMiddleware):
    """
    Har bir foydalanuvchi harakatini kuzatib, uni ma'lumotlar bazasiga
    avtomatik ravishda qo'shib/yangilab boruvchi middleware.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user and not user.is_bot:
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            await Database.add_or_update_user(
                user_id=user.id,
                username=user.username,
                full_name=full_name
            )

        return await handler(event, data)
