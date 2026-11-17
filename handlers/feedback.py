from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database.models import Database
from states.user_states import FeedbackStates
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from config import ADMINS
import logging

logger = logging.getLogger(__name__)

router = Router(name="feedback")

@router.message(F.text == "✍️ Fikr va takliflar")
async def start_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✍️ <b>Hurmatli foydalanuvchi!</b>\n\n"
        "ITLive o'quv markazi faoliyati, kurslarimiz sifati yoki botimiz haqidagi har qanday "
        "fikr, taklif yoki e'tirozingizni yozib qoldirishingiz mumkin.\n\n"
        "Sizning fikringiz biz uchun juda muhim! Iltimos, xabaringizni yozing:\n"
        "<i>(Bekor qilish uchun pastdagi tugmani bosing)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(FeedbackStates.waiting_for_feedback)

@router.message(FeedbackStates.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext):
    user = message.from_user
    feedback_text = message.text.strip()
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    # 1. Bazaga saqlash
    await Database.add_feedback(
        user_id=user.id,
        full_name=full_name,
        username=user.username,
        message=feedback_text
    )

    # 2. Barcha adminlarga yuborish
    admin_notify = (
        "💬 <b>YANGI FIKR / TAKLIF QOLDIRILDI!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Foydalanuvchi:</b> {full_name}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"✈️ <b>Telegram:</b> @{user.username if user.username else 'yoq'}\n\n"
        f"📝 <b>Xabar matni:</b>\n<i>{feedback_text}</i>\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    for admin_id in ADMINS:
        try:
            await message.bot.send_message(chat_id=admin_id, text=admin_notify)
        except Exception as e:
            logger.error(f"Fikrni adminga yuborishda xatolik ({admin_id}): {e}")

    await state.clear()
    is_admin = user.id in ADMINS
    is_sales = await Database.is_sales_rep(user.id)

    await message.answer(
        "✅ <b>Katta rahmat!</b> Sizning fikringiz muvaffaqiyatli qabul qilindi va "
        "o'quv markazimiz rahbariyatiga yetkazildi. Biz har doim xizmatlarimizni yanada "
        "yaxshilashga intilamiz! 🚀",
        reply_markup=get_main_keyboard(is_admin=is_admin, is_sales=is_sales)
    )
