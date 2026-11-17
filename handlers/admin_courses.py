from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.models import Database
from states.user_states import AdminCourseStates
from keyboards.inline import get_admin_courses_inline, get_admin_course_detail_inline
from keyboards.reply import get_cancel_keyboard, get_main_keyboard
from config import ADMINS

router = Router(name="admin_courses")

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Kurslar ro'yxati
@router.callback_query(F.data == "admin:courses")
async def admin_list_courses(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    courses = await Database.get_all_courses()
    text = (
        "📚 <b>KURSLARNI BOSHQARISH</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🟢 - Faol kurs | 🔴 - O'chirilgan (ko'rinmaydi)\n\n"
        "Kurs holatini o'zgartirish yoki o'chirish uchun ustiga bosing:"
    )
    await call.message.edit_text(text, reply_markup=get_admin_courses_inline(courses))
    await call.answer()

# Bitta kurs tafsiloti va boshqaruvi
@router.callback_query(F.data.startswith("admin_course:"))
async def admin_course_detail(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    course_id = int(call.data.split(":")[1])
    course = await Database.get_course_by_id(course_id)
    if not course:
        await call.answer("Kurs topilmadi!", show_alert=True)
        return

    status_str = "🟢 Faol (Foydalanuvchilarga ko'rinadi)" if course.get("is_active") else "🔴 Faolsiz (Yashirilgan)"

    text = (
        f"⚙️ <b>{course['name']}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Holati:</b> {status_str}\n"
        f"⏳ <b>Davomiyligi:</b> {course['duration']}\n"
        f"💰 <b>Narxi:</b> {course['price']}\n"
        f"🛠 <b>Texnologiyalar:</b> {course.get('technologies') or '-'}\n\n"
        f"📝 <b>Tavsif:</b>\n{course['description']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    await call.message.edit_text(
        text,
        reply_markup=get_admin_course_detail_inline(course_id, bool(course.get("is_active")))
    )
    await call.answer()

# Kurs holatini yoqish/o'chirish
@router.callback_query(F.data.startswith("admin_toggle_course:"))
async def admin_toggle_course(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    course_id = int(call.data.split(":")[1])
    await Database.toggle_course_status(course_id)
    await call.answer("Kurs holati o'zgartirildi!")

    course = await Database.get_course_by_id(course_id)
    status_str = "🟢 Faol (Foydalanuvchilarga ko'rinadi)" if course.get("is_active") else "🔴 Faolsiz (Yashirilgan)"
    text = (
        f"⚙️ <b>{course['name']}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Holati:</b> {status_str}\n"
        f"⏳ <b>Davomiyligi:</b> {course['duration']}\n"
        f"💰 <b>Narxi:</b> {course['price']}\n"
        f"🛠 <b>Texnologiyalar:</b> {course.get('technologies') or '-'}\n\n"
        f"📝 <b>Tavsif:</b>\n{course['description']}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await call.message.edit_text(
        text,
        reply_markup=get_admin_course_detail_inline(course_id, bool(course.get("is_active")))
    )

# Kursni butunlay o'chirish
@router.callback_query(F.data.startswith("admin_delete_course:"))
async def admin_delete_course(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    course_id = int(call.data.split(":")[1])
    await Database.delete_course(course_id)
    await call.answer("Kurs butunlay o'chirildi!", show_alert=True)

    courses = await Database.get_all_courses()
    text = (
        "📚 <b>KURSLARNI BOSHQARISH</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kurs o'chirildi. Qolgan kurslar ro'yxati:"
    )
    await call.message.edit_text(text, reply_markup=get_admin_courses_inline(courses))

# ================= Yangi kurs qo'shish FSM =================
@router.callback_query(F.data == "admin:add_course")
async def start_add_course(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat berilmagan!", show_alert=True)
        return

    await state.clear()
    await call.message.answer(
        "➕ <b>YANGI KURS QO'SHISH</b>\n\n"
        "1-qadam: Kurs nomini kiriting:\n"
        "<i>(Masalan: 🤖 Sun'iy Intellekt va Data Science)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminCourseStates.name)
    await call.answer()

@router.message(AdminCourseStates.name)
async def process_course_name(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Kurs qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    await state.update_data(c_name=message.text.strip())
    await message.answer(
        "2-qadam: Kurs haqida qisqacha tavsif kiriting:\n"
        "<i>(Kurs kimlar uchun, nimani o'rganadi?)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminCourseStates.description)

@router.message(AdminCourseStates.description)
async def process_course_desc(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Kurs qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    await state.update_data(c_desc=message.text.strip())
    await message.answer(
        "3-qadam: Kurs davomiyligini kiriting:\n"
        "<i>(Masalan: 6 oy yoki 4 oy)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminCourseStates.duration)

@router.message(AdminCourseStates.duration)
async def process_course_duration(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Kurs qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    await state.update_data(c_duration=message.text.strip())
    await message.answer(
        "4-qadam: Kurs oylik to'lov narxini kiriting:\n"
        "<i>(Masalan: 1,200,000 so'm / oy)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminCourseStates.price)

@router.message(AdminCourseStates.price)
async def process_course_price(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Kurs qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    await state.update_data(c_price=message.text.strip())
    await message.answer(
        "5-qadam: O'rganiladigan asosiy texnologiyalar / dasturlarni kiriting:\n"
        "<i>(Masalan: Python, PyTorch, Pandas, NumPy, OpenCV)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminCourseStates.technologies)

@router.message(AdminCourseStates.technologies)
async def finalize_add_course(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Kurs qo'shish bekor qilindi.", reply_markup=get_main_keyboard(is_admin=True))
        return

    technologies = message.text.strip()
    data = await state.get_data()

    course_id = await Database.add_course(
        name=data["c_name"],
        description=data["c_desc"],
        duration=data["c_duration"],
        price=data["c_price"],
        technologies=technologies
    )
    await state.clear()

    await message.answer(
        f"✅ <b>\"{data['c_name']}\" kursi muvaffaqiyatli qo'shildi!</b>\n\n"
        f"🆔 Kurs ID: {course_id}\n"
        f"⏳ Davomiyligi: {data['c_duration']}\n"
        f"💰 Narxi: {data['c_price']}\n"
        f"🛠 Texnologiyalar: {technologies}\n\n"
        "Endi ushbu kurs barcha foydalanuvchilar menyusida ko'rinadi.",
        reply_markup=get_main_keyboard(is_admin=True)
    )
