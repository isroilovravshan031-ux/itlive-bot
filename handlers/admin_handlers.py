import asyncio
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.models import Database
from states.user_states import AdminBroadcastStates, AdminSettingStates
from keyboards.inline import get_admin_menu_inline, get_admin_settings_inline
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from utils.excel_export import export_leads_to_excel
from utils.text_helpers import format_lead_summary_card
from config import ADMINS
import logging

logger = logging.getLogger(__name__)

router = Router(name="admin_handlers")

# Admin tekshiruvi filtri yordamchisi
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# ================= Admin Panel Asosiy Menyu =================
@router.message(Command("admin"))
@router.message(F.text == "👑 Admin Panel")
async def cmd_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Kechirasiz, sizda admin huquqlari mavjud emas.")
        return

    text = (
        "👑 <b>ITLIVE BOT ADMIN BOSHQARUV PANELI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Quyidagi boshqaruv bo'limlaridan birini tanlang:\n\n"
        "• <b>Statistika:</b> Foydalanuvchilar va arizalar tahlili\n"
        "• <b>Lidlar:</b> Barcha tushgan arizalar ro'yxati\n"
        "• <b>Excel hisobot:</b> Barcha arizalarni jadval qilib yuklash\n"
        "• <b>Kurslar:</b> Yangi kurs qo'shish, o'chirish, tahrirlash\n"
        "• <b>Sotuvchilar:</b> Yangi menejerlarni biriktirish/o'chirish\n"
        "• <b>Xabarnoma:</b> Barcha a'zolarga ommaviy xabar yuborish\n"
        "• <b>Sozlamalar:</b> Telefon, manzil va matnlarni dinamik o'zgartirish"
    )

    await message.answer(text, reply_markup=get_admin_menu_inline())

@router.callback_query(F.data == "admin:main")
async def back_to_admin_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    text = (
        "👑 <b>ITLIVE BOT ADMIN BOSHQARUV PANELI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kerakli bo'limni tanlang:"
    )
    await call.message.edit_text(text, reply_markup=get_admin_menu_inline())
    await call.answer()

# ================= 📊 Statistika =================
@router.callback_query(F.data == "admin:stats")
async def admin_statistics(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    user_count = await Database.get_user_count()
    lead_stats = await Database.get_leads_statistics()
    sales_reps = await Database.get_active_sales_reps()

    text = (
        "📊 <b>ITLIVE BOT TO'LIQ STATISTIKASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Jami foydalanuvchilar soni:</b> {user_count} nafar\n"
        f"💼 <b>Faol sotuvchilar (Sales team):</b> {len(sales_reps)} nafar\n\n"
        "📥 <b>Arizalar (Lidlar) tahlili:</b>\n"
        f"• 📈 Jami arizalar: <b>{lead_stats['total']} ta</b>\n"
        f"• 📅 Bugun tushgan: <b>{lead_stats['today']} ta</b>\n"
        f"• 🆕 Ko'rib chiqilmagan (Yangi): <b>{lead_stats['new']} ta</b>\n"
        f"• 📞 Bog'lanilgan: <b>{lead_stats['contacted']} ta</b>\n"
        f"• ✅ O'qishga yozilgan (Mijoz bo'lgan): <b>{lead_stats['enrolled']} ta</b>\n"
        f"• ❌ Bekor qilingan: <b>{lead_stats['cancelled']} ta</b>\n\n"
        "🔥 <b>Eng ko'p tanlangan TOP kurslar:</b>\n"
    )

    if lead_stats["top_courses"]:
        for idx, tc in enumerate(lead_stats["top_courses"], 1):
            text += f"{idx}. {tc['course_name']}: <b>{tc['cnt']} ta ariza</b>\n"
    else:
        text += "<i>Hozircha arizalar yo'q.</i>\n"

    text += "━━━━━━━━━━━━━━━━━━━━━━"

    back_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📑 Excel hisobotni yuklab olish", callback_data="admin:export_excel")],
        [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")]
    ])

    await call.message.edit_text(text, reply_markup=back_markup)
    await call.answer()

# ================= 📑 Excel hisobot yuklash =================
@router.callback_query(F.data == "admin:export_excel")
async def admin_export_excel(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await call.answer("Excel fayl tayyorlanmoqda, kuting...", show_alert=False)

    leads = await Database.get_all_leads_for_export()
    if not leads:
        await call.message.answer("📭 Hozircha bazada arizalar mavjud emas.")
        return

    file_path = await export_leads_to_excel(leads)

    caption = (
        "📑 <b>ITLive O'quv Markazi — Lidlar hisoboti</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Jami arizalar soni: <b>{len(leads)} ta</b>\n"
        "Ushbu faylda har bir mijozning ismi, raqami, yoshi, hududi, kursi, holati va mas'ul sotuvchi to'liq kiritilgan."
    )

    doc = FSInputFile(path=file_path, filename=os.path.basename(file_path))
    await call.message.answer_document(document=doc, caption=caption)

# ================= 📥 Lidlar ro'yxatini ko'rish =================
@router.callback_query(F.data == "admin:leads")
async def admin_view_leads(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    leads = await Database.get_all_leads_for_export()
    if not leads:
        await call.message.edit_text(
            "📭 Hozircha birorta ham ariza tushmagan.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")]
            ])
        )
        await call.answer()
        return

    recent_leads = leads[:7]
    text = f"📥 <b>Oxirgi tushgan arizalar (Jami: {len(leads)} ta):</b>\n\n"

    for l in recent_leads:
        text += format_lead_summary_card(l) + "\n"

    buttons = [
        [InlineKeyboardButton(text="📑 Barchasini Excelda yuklash", callback_data="admin:export_excel")],
        [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")]
    ]
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await call.answer()

# ================= 📢 Ommaviy xabarnoma (Broadcast) =================
@router.callback_query(F.data == "admin:broadcast")
async def admin_broadcast_prompt(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    user_count = await Database.get_user_count()

    await call.message.answer(
        f"📢 <b>OMMAVIY XABARNOMA YUBORISH</b>\n"
        f"Bot a'zolari soni: <b>{user_count} nafar</b>\n\n"
        "Barcha bot foydalanuvchilariga yuboriladigan xabarni kiriting.\n"
        "<i>(Xabar sifatida oddiy matn, rasm yoki video ham yuborishingiz mumkin)</i>\n\n"
        "Bekor qilish uchun pastdagi tugmani bosing:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminBroadcastStates.waiting_for_message)
    await call.answer()

@router.message(AdminBroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Xabar yuborish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    # Xabarni saqlash
    await state.update_data(
        broadcast_msg_id=message.message_id,
        broadcast_from_chat=message.chat.id
    )

    confirm_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, barchaga yuborilsin", callback_data="confirm_broadcast_yes"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin:main")
        ]
    ])

    await message.answer(
        "❓ <b>Haqiqatdan ham ushbu xabarni barcha foydalanuvchilarga yuborasizmi?</b>",
        reply_markup=confirm_markup
    )
    await state.set_state(AdminBroadcastStates.confirm)

@router.callback_query(AdminBroadcastStates.confirm, F.data == "confirm_broadcast_yes")
async def send_broadcast(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_id = data.get("broadcast_msg_id")
    from_chat = data.get("broadcast_from_chat")

    await call.message.edit_text("⏳ Xabarnoma yuborilmoqda, kuting...")

    users = await Database.get_all_users()
    success = 0
    failed = 0

    for u in users:
        try:
            await call.bot.copy_message(
                chat_id=u["user_id"],
                from_chat_id=from_chat,
                message_id=msg_id
            )
            success += 1
            await asyncio.sleep(0.05) # Telegram spam protection
        except Exception:
            failed += 1

    await state.clear()
    result_text = (
        "📢 <b>XABARNOMA YAKUNLANDI!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Muvaffaqiyatli yetkazildi:</b> {success} ta\n"
        f"❌ <b>Yetib bormadi (bloklagan):</b> {failed} ta\n"
        f"📊 <b>Jami urinishlar:</b> {len(users)} ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    await call.message.answer(
        result_text,
        reply_markup=get_main_keyboard(is_admin=True)
    )
    await call.answer()

# ================= 💬 Fikr va takliflar ro'yxati =================
@router.callback_query(F.data == "admin:feedback")
async def admin_view_feedback(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    feedbacks = await Database.get_all_feedback()
    if not feedbacks:
        await call.message.edit_text(
            "📭 Hozircha hech qanday fikr va taklif kelib tushmagan.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")]
            ])
        )
        await call.answer()
        return

    text = f"💬 <b>Oxirgi fikr va takliflar (Jami: {len(feedbacks)} ta):</b>\n\n"
    for f in feedbacks[:8]:
        text += (
            f"👤 <b>{f['full_name']}</b> (@{f['username'] or 'yoq'})\n"
            f"📝 <i>\"{f['message']}\"</i>\n"
            f"📅 {str(f['created_at'])[:16]}\n"
            "───────────────\n"
        )

    await call.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")]
        ])
    )
    await call.answer()

# ================= ⚙️ Dinamik Bot Sozlamalari =================
@router.callback_query(F.data == "admin:settings")
async def admin_view_settings(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    settings = await Database.get_all_settings()
    text = (
        "⚙️ <b>BOTNING DINAMIK SOZLAMALARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏢 <b>Markaz nomi:</b> {settings.get('center_name')}\n"
        f"📞 <b>Telefon 1:</b> {settings.get('phone_1')}\n"
        f"📞 <b>Telefon 2:</b> {settings.get('phone_2')}\n"
        f"📍 <b>Manzil:</b> {settings.get('address')}\n"
        f"🧭 <b>Mo'ljal:</b> {settings.get('landmark')}\n"
        f"⏰ <b>Ish vaqti:</b> {settings.get('working_hours')}\n"
        f"📸 <b>Instagram:</b> {settings.get('instagram')}\n"
        f"🌐 <b>Veb-sayt:</b> {settings.get('website')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "O'zgartirmoqchi bo'lgan parametr tugmasini bosing:"
    )

    await call.message.edit_text(text, reply_markup=get_admin_settings_inline())
    await call.answer()

@router.callback_query(F.data.startswith("admin_set:"))
async def admin_change_setting_prompt(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    setting_key = call.data.split(":")[1]
    current_val = await Database.get_setting(setting_key)

    setting_names = {
        "center_name": "Markaz nomi",
        "phone_1": "1-telefon raqami",
        "phone_2": "2-telefon raqami",
        "address": "Manzil matni",
        "landmark": "Mo'ljal matni",
        "working_hours": "Ish vaqti",
        "instagram": "Instagram havolasi",
        "website": "Veb-sayt havolasi",
        "about_text": "Biz haqimizda matni",
        "discounts_text": "Aksiyalar va chegirmalar matni"
    }

    await state.set_state(AdminSettingStates.waiting_for_value)
    await state.update_data(setting_key=setting_key)

    await call.message.answer(
        f"✏️ <b>{setting_names.get(setting_key, setting_key)} parametrini o'zgartirish:</b>\n\n"
        f"Hozirgi qiymat:\n<code>{current_val}</code>\n\n"
        "Yangi qiymatni yozib yuboring:",
        reply_markup=get_cancel_keyboard()
    )
    await call.answer()

@router.message(AdminSettingStates.waiting_for_value)
async def process_setting_value(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Sozlamani o'zgartirish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    data = await state.get_data()
    setting_key = data.get("setting_key")
    new_value = message.text.strip()

    await Database.set_setting(setting_key, new_value)
    await state.clear()

    await message.answer(
        f"✅ <b>{setting_key} parametri muvaffaqiyatli saqlandi!</b>\n\n"
        f"Yangi qiymat:\n<i>{new_value}</i>",
        reply_markup=get_main_keyboard(is_admin=True)
    )
