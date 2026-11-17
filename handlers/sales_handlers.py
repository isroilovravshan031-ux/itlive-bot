from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.models import Database
from states.user_states import SalesNoteStates
from keyboards.inline import get_sales_lead_actions
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from config import ADMINS
import logging

logger = logging.getLogger(__name__)

router = Router(name="sales_handlers")

# ================= Sotuvchi tomonidan status o'zgartirilishi =================
@router.callback_query(F.data.startswith("lead_status:"))
async def handle_lead_status_change(call: CallbackQuery):
    parts = call.data.split(":")
    lead_id = int(parts[1])
    new_status = parts[2]
    if new_status not in {"YANGI", "BOGLANILDI", "YOZILDI", "BEKOR_QILINDI"}:
        await call.answer("Noto‘g‘ri holat.", show_alert=True)
        return
    sales_user = call.from_user

    # Foydalanuvchi sotuvchi yoki admin ekanligini tekshirish
    is_sales = await Database.is_sales_rep(sales_user.id)
    is_admin = sales_user.id in ADMINS
    if not (is_sales or is_admin):
        await call.answer("⛔️ Siz sotuvchilar ro'yxatida emassiz!", show_alert=True)
        return

    # Bazada statusni yangilash
    await Database.update_lead_status(lead_id=lead_id, status=new_status, sales_id=sales_user.id)

    status_labels = {
        "BOGLANILDI": "📞 Bog'lanildi",
        "YOZILDI": "✅ O'qishga yozildi (Muvaffaqiyatli)",
        "BEKOR_QILINDI": "❌ Bekor qilindi"
    }
    label = status_labels.get(new_status, new_status)

    # Xabardagi tugmalarni yangi holat bilan yangilash
    new_markup = get_sales_lead_actions(lead_id=lead_id, current_status=new_status)

    sales_name = f"{sales_user.first_name or ''} {sales_user.last_name or ''}".strip()
    status_suffix = f"\n\n🔄 <b>Holat yangilandi:</b> {label}\n👤 <b>Mas'ul xodim:</b> {sales_name}"

    current_text = call.message.html_text
    # Agar avval holat qo'shilgan bo'lsa, eskisini almashtiramiz
    if "🔄 <b>Holat yangilandi:</b>" in current_text:
        base_text = current_text.split("\n\n🔄 <b>Holat yangilandi:</b>")[0]
    else:
        base_text = current_text

    try:
        await call.message.edit_text(
            text=base_text + status_suffix,
            reply_markup=new_markup
        )
    except Exception as e:
        logger.warning(f"Xabarni tahrirlashda xatolik: {e}")

    await call.answer(f"Status yangilandi: {label}", show_alert=False)

# ================= Sotuvchi tomonidan izoh qo'shish =================
@router.callback_query(F.data.startswith("lead_note:"))
async def handle_lead_add_note_prompt(call: CallbackQuery, state: FSMContext):
    lead_id = int(call.data.split(":")[1])
    sales_user = call.from_user

    is_sales = await Database.is_sales_rep(sales_user.id)
    is_admin = sales_user.id in ADMINS
    if not (is_sales or is_admin):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await state.set_state(SalesNoteStates.waiting_for_note)
    await state.update_data(note_lead_id=lead_id, original_msg_id=call.message.message_id)

    await call.message.answer(
        f"✍️ <b>#{lead_id} raqamli murojaat uchun izohingizni yozing:</b>\n"
        "<i>(Masalan: Mijoz bilan gaplashildi, ertaga soat 14:00 da ochiq darsga keladi)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await call.answer()

@router.message(SalesNoteStates.waiting_for_note)
async def process_lead_note(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS and not await Database.is_sales_rep(message.from_user.id):
        await state.clear()
        await message.answer("⛔️ Ruxsat berilmagan!")
        return
    if not message.text:
        await message.answer("Iltimos, izohni matn ko‘rinishida yuboring.")
        return
    note_text = message.text.strip()
    data = await state.get_data()
    lead_id = data.get("note_lead_id")
    user = message.from_user

    await Database.add_sales_note(lead_id=lead_id, note=note_text, sales_id=user.id)
    await state.clear()

    is_admin = user.id in ADMINS
    is_sales = await Database.is_sales_rep(user.id)

    await message.answer(
        f"✅ <b>#{lead_id} raqamli ariza uchun izoh muvaffaqiyatli saqlandi!</b>\n\n"
        f"💬 <b>Izoh:</b> <i>{note_text}</i>",
        reply_markup=get_main_keyboard(is_admin=is_admin, is_sales=is_sales)
    )

# ================= Sotuvchi Kabineti / Dashboard =================
@router.message(F.text.in_(["💼 Sotuvchi Kabineti", "/sales"]))
async def sales_cabinet(message: Message):
    user_id = message.from_user.id
    is_sales = await Database.is_sales_rep(user_id)
    is_admin = user_id in ADMINS

    if not (is_sales or is_admin):
        await message.answer("⛔️ Siz sotuvchilar ro'yxatida emassiz.")
        return

    stats = await Database.get_leads_statistics()

    text = (
        "💼 <b>SOTUVCHILAR BOSHQARUV KABINETI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆕 <b>Yangi ko'rib chiqilmagan lidlar:</b> {stats['new']} ta\n"
        f"📞 <b>Aloqaga chiqilganlar:</b> {stats['contacted']} ta\n"
        f"✅ <b>O'qishga yozilganlar:</b> {stats['enrolled']} ta\n"
        f"❌ <b>Rad etilganlar:</b> {stats['cancelled']} ta\n"
        f"📅 <b>Bugungi jami lidlar:</b> {stats['today']} ta\n"
        f"📊 <b>Umumiy barcha lidlar:</b> {stats['total']} ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡️ Yangi arizalar to'g'ridan-to'g'ri profilingizga kelib tushadi."
    )
    await message.answer(text)
