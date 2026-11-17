import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import BOT_TOKEN, ADMINS
from database.db import init_db
from middlewares.user_tracker import UserTrackerMiddleware
from handlers import (
    user_router,
    registration_router,
    quiz_router,
    feedback_router,
    sales_router,
    admin_router,
    admin_courses_router,
    admin_sales_router
)

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def setup_bot_commands(bot: Bot):
    """Telegram menyusida chiqadigan asosiy buyruqlar"""
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="help", description="❓ Yordam va savol-javoblar"),
        BotCommand(command="sales", description="💼 Sotuvchilar kabineti"),
        BotCommand(command="admin", description="👑 Admin panel")
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewarelarni ro'yxatdan o'tkazish
    dp.message.outer_middleware(UserTrackerMiddleware())
    dp.callback_query.outer_middleware(UserTrackerMiddleware())

    # Routerlarni tartib bilan ulash
    # 1. Admin routerlar
    dp.include_router(admin_router)
    dp.include_router(admin_courses_router)
    dp.include_router(admin_sales_router)
    # 2. Sotuvchilar routeri
    dp.include_router(sales_router)
    # 3. Ro'yxatdan o'tish (Lead yig'ish) routeri
    dp.include_router(registration_router)
    # 4. Kviz va Fikr-mulohaza routerlari
    dp.include_router(quiz_router)
    dp.include_router(feedback_router)
    # 5. Asosiy foydalanuvchi routeri
    dp.include_router(user_router)

    return dp


async def main():
    logger.info("ITLive Telegram Boti ishga tushirilmoqda...")

    # Bot tokeni tekshiruvi
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "XATOLIK: BOT_TOKEN aniqlanmadi!\n"
            "Iltimos, .env fayliga haqiqiy bot tokeningizni kiriting.\n"
            "Masalan: BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRstuVWXyz\n"
            + "=" * 60
        )
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    await init_db()

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = create_dispatcher()

    # Bot buyruqlarini o'rnatish
    try:
        await setup_bot_commands(bot)
    except Exception as e:
        logger.warning(f"Buyruqlarni o'rnatishda xatolik: {e}")

    # Adminlarga bot ishga tushganligi haqida xabar yuborish
    for admin_id in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="🚀 <b>ITLive Telegram Boti muvaffaqiyatli ishga tushirildi!</b>"
            )
        except Exception:
            pass

    logger.info("Bot polling rejimi ishga tushdi.")
    # Eski update larni tozalab yangilarini kutish
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
