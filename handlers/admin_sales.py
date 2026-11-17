from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.models import Database
from states.user_states import AdminSalesStates
from keyboards.inline import get_admin_sales_inline
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from config import ADMINS

router = Router(name="admin_sales")

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Sotuvchilar ro'yxati
@router.callback_query(F.data == "admin:sales")
async def admin_list_sales(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    sales_reps = await Database.get_all_sales_reps()
    text = (
        "👥 <b>SOTUVCHILAR JAMOASI (SALES TEAM)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Bu yerdagi har bir xodimga o'quv markaziga tushgan yangi arizalar "
        "(Ism, telefon, yosh, hudud, kurs) <b>avtomatik ravishda yuboriladi</b>.\n\n"
        f"Hozirda ro'yxatda: <b>{len(sales_reps)} nafar xodim</b>\n"
    )
    await call.message.edit_text(text, reply_markup=get_admin_sales_inline(sales_reps))
    await call.answer()

# Sotuvchini o'chirish
@router.callback_query(F.data.startswith("sales_delete:"))
async def admin_delete_sales(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    tg_id = int(call.data.split(":")[1])
    await Database.remove_sales_rep(tg_id)
    await call.answer("Sotuvchi ro'yxatdan o'chirildi!", show_alert=True)

    sales_reps = await Database.get_all_sales_reps()
    text = (
        "👥 <b>SOTUVCHILAR JAMOASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Xodim muvaffaqiyatli o'chirildi. Yangilangan ro'yxat:"
    )
    await call.message.edit_text(text, reply_markup=get_admin_sales_inline(sales_reps))

# Yangi sotuvchi qo'shish FSM
@router.callback_query(F.data == "admin:add_sales")
async def start_add_sales(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await state.clear()
    await call.message.answer(
        "➕ <b>YANGI SOTUVCHI QO'SHISH</b>\n\n"
        "1-qadam: Sotuvchi xodimning <b>Telegram ID raqamini</b> kiriting:\n"
        "<i>(Xodim o'z ID raqamini @userinfobot orqali bilib olishi mumkin. Masalan: 123456789)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminSalesStates.enter_id)
    await call.answer()

@router.message(AdminSalesStates.enter_id)
async def process_sales_id(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Sotuvchi qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    tg_id_text = message.text.strip()
    if not tg_id_text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqamlardan iborat Telegram ID kiriting:")
        return

    await state.update_data(sales_tg_id=int(tg_id_text))
    await message.answer(
        "2-qadam: Xodimning <b>to'liq ism va familiyasini</b> kiriting:\n"
        "<i>(Masalan: Otabek Jo'rayev)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminSalesStates.enter_name)

@router.message(AdminSalesStates.enter_name)
async def process_sales_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Sotuvchi qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    await state.update_data(sales_name=message.text.strip())
    await message.answer(
        "3-qadam: Xodimning <b>telefon raqamini</b> kiriting:\n"
        "<i>(Masalan: +998901234567)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminSalesStates.enter_phone)

@router.message(AdminSalesStates.enter_phone)
async def finalize_add_sales(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Sotuvchi qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    phone = message.text.strip()
    data = await state.get_data()

    await Database.add_sales_rep(
        telegram_id=data["sales_tg_id"],
        full_name=data["sales_name"],
        phone=phone
    )
    await state.clear()

    # Yangi sotuvchiga bildirishnoma yuborishga urinish
    try:
        await message.bot.send_message(
            chat_id=data["sales_tg_id"],
            text=(
                f"🎉 Tabriklaymiz, <b>{data['sales_name']}</b>!\n\n"
                "Siz ITLive botida <b>Sotuvchi menejer</b> sifatida biriktirildingiz.\n"
                "Endi yangi tushgan barcha lidlar (murojaatlar) to'g'ridan-to'g'ri sizning "
                "Telegram profilingizga yetib keladi."
            )
        )
    except Exception:
        pass

    await message.answer(
        f"✅ <b>Yangi sotuvchi muvaffaqiyatli qo'shildi!</b>\n\n"
        f"👤 <b>Xodim:</b> {data['sales_name']}\n"
        f"🆔 <b>Telegram ID:</b> <code>{data['sales_tg_id']}</code>\n"
        f"📞 <b>Telefon:</b> {phone}\n\n"
        "Endi markazga tushgan har bir ariza ushbu xodimga darhol yuboriladi.",
        reply_markup=get_main_keyboard(is_admin=True)
    )
