from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.models import Database
from states.user_states import RegistrationStates
from keyboards.reply import get_phone_keyboard, get_region_keyboard, get_time_preference_keyboard, get_main_keyboard, get_cancel_keyboard
from keyboards.inline import get_courses_choice_inline, get_sales_lead_actions
from utils.text_helpers import clean_phone_number, format_lead_notification
from config import ADMINS
import logging

logger = logging.getLogger(__name__)

router = Router(name="registration")

# ================= Ro'yxatdan o'tishni boshlash =================
@router.message(F.text.in_(["📝 Kursga yozilish", "🎁 Bepul sinov darsi"]))
@router.callback_query(F.data.in_(["start_registration", "enroll_trial"]))
async def start_registration(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()

    text = (
        "🎓 <b>ITLive o'quv markaziga xush kelibsiz!</b>\n\n"
        "Kurslarimizga yozilish va to'liq ma'lumot olish uchun bir nechta savollarga javob bering.\n\n"
        "Iltimos, <b>to'liq ism va familiyangizni</b> kiriting:\n"
        "<i>(Masalan: Jasur Karimov)</i>"
    )

    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=get_cancel_keyboard())
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_cancel_keyboard())

    await state.set_state(RegistrationStates.name)

# Alohida bitta kursdan "Yozilish" bosilganda
@router.callback_query(F.data.startswith("enroll_course:"))
async def enroll_specific_course(call: CallbackQuery, state: FSMContext):
    await state.clear()
    course_id = int(call.data.split(":")[1])
    course = await Database.get_course_by_id(course_id)
    course_name = course["name"] if course else "Umumiy konsultatsiya"

    await state.update_data(chosen_course=course_name)

    await call.message.answer(
        f"🎯 Siz <b>{course_name}</b> kursini tanladingiz!\n\n"
        "Ro'yxatdan o'tish uchun, iltimos, <b>to'liq ismingizni</b> kiriting:\n"
        "<i>(Masalan: Sardor Aliyev)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await call.answer()
    await state.set_state(RegistrationStates.name)

# 1-QADAM: Ismni qabul qilish
@router.message(RegistrationStates.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 3 or len(name) > 60:
        await message.answer(
            "⚠️ Iltimos, haqiqiy ism va familiyangizni to'liq kiriting (kamida 3 ta harf):",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(full_name=name)
    await message.answer(
        f"Rahmat, <b>{name}</b>!\n\n"
        "Endi siz bilan tezkor bog'lanishimiz uchun <b>telefon raqamingizni</b> yuboring.\n"
        "Quyidagi <b>«📱 Telefon raqamni ulashish»</b> tugmasini bosing yoki raqamingizni qo'lda yozing:\n"
        "<i>(Masalan: +998901234567)</i>",
        reply_markup=get_phone_keyboard()
    )
    await state.set_state(RegistrationStates.phone)

# 2-QADAM: Telefon raqamni qabul qilish
@router.message(RegistrationStates.phone, F.contact)
@router.message(RegistrationStates.phone, F.text)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = clean_phone_number(message.text)
        if not phone:
            await message.answer(
                "⚠️ <b>Noto'g'ri telefon raqami kiritildi!</b>\n\n"
                "Iltimos, pastdagi tugmani bosing yoki raqamingizni quyidagi formatda yozing:\n"
                "<code>+998901234567</code>",
                reply_markup=get_phone_keyboard()
            )
            return

    await state.update_data(phone=phone)
    await message.answer(
        "Yosh toifangizga mos guruh va dastur tavsiya qilishimiz uchun <b>yoshingizni</b> kiriting:\n"
        "<i>(Faqat son kiriting, masalan: 19)</i>",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(RegistrationStates.age)

# 3-QADAM: Yoshni qabul qilish
@router.message(RegistrationStates.age)
async def process_age(message: Message, state: FSMContext):
    age_text = message.text.strip()
    if not age_text.isdigit() or not (7 <= int(age_text) <= 90):
        await message.answer(
            "⚠️ Iltimos, yoshingizni to'g'ri son ko'rinishida kiriting (7 dan 90 gacha):\n"
            "<i>(Masalan: 21)</i>",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(age=int(age_text))
    await message.answer(
        "📍 <b>Qayerdansiz?</b> Yashash hududingiz yoki shahringizni tanlang / yozing:\n"
        "<i>(Quyidagi tugmalardan birini tanlashingiz yoki aniq tuman/manzilingizni yozib yuborishingiz mumkin)</i>",
        reply_markup=get_region_keyboard()
    )
    await state.set_state(RegistrationStates.region)

# 4-QADAM: Hududni qabul qilish
@router.message(RegistrationStates.region, F.location)
@router.message(RegistrationStates.region, F.text)
async def process_region(message: Message, state: FSMContext):
    if message.location:
        region = f"Lokatsiya: {message.location.latitude:.4f}, {message.location.longitude:.4f}"
    else:
        region = message.text.strip()

    await state.update_data(region=region)
    data = await state.get_data()

    # Agar foydalanuvchi allaqachon ma'lum bir kurs orqali kirgan bo'lsa
    if data.get("chosen_course"):
        await message.answer(
            "⏰ O'qish uchun sizga <b>qaysi vaqt qulay?</b>",
            reply_markup=get_time_preference_keyboard()
        )
        await state.set_state(RegistrationStates.time_preference)
        return

    # Bo'lmasa faol kurslar ro'yxatini ko'rsatish
    courses = await Database.get_active_courses()
    await message.answer(
        "💻 O'zingiz qiziqqan <b>IT yo'nalishini</b> tanlang:",
        reply_markup=get_courses_choice_inline(courses)
    )
    await state.set_state(RegistrationStates.course)

# 5-QADAM: Kursni qabul qilish
@router.callback_query(RegistrationStates.course, F.data.startswith("select_course:"))
async def process_course(call: CallbackQuery, state: FSMContext):
    course_name = call.data.split(":", 1)[1]
    await state.update_data(chosen_course=course_name)
    await call.message.delete()
    await call.message.answer(
        f"Tanlangan yo'nalish: <b>{course_name}</b>\n\n"
        "⏰ Darslarga qatnashish uchun sizga <b>qaysi vaqt qulay?</b>",
        reply_markup=get_time_preference_keyboard()
    )
    await call.answer()
    await state.set_state(RegistrationStates.time_preference)

# 6-QADAM: Qulay vaqt va tasdiqlash
@router.message(RegistrationStates.time_preference)
async def process_time_preference(message: Message, state: FSMContext):
    time_pref = message.text.strip()
    await state.update_data(time_preference=time_pref)
    data = await state.get_data()

    confirm_text = (
        "📋 <b>Arizangiz ma'lumotlarini tekshiring:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {data.get('full_name')}\n"
        f"📞 <b>Telefon:</b> {data.get('phone')}\n"
        f"🎂 <b>Yoshi:</b> {data.get('age')} yosh\n"
        f"📍 <b>Hudud:</b> {data.get('region')}\n"
        f"💻 <b>Kurs:</b> {data.get('chosen_course')}\n"
        f"⏰ <b>Qulay vaqt:</b> {data.get('time_preference')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Barcha ma'lumotlar to'g'rimi? Murojaatingizni yuboramizmi?"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    confirm_inline = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, yuborish", callback_data="confirm_lead_yes"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm_lead_no")
        ]
    ])

    await message.answer(confirm_text, reply_markup=confirm_inline)
    await state.set_state(RegistrationStates.confirm)

# 7-QADAM: Yakuniy tasdiqlash va Sotuvchilarga yetkazish
@router.callback_query(RegistrationStates.confirm, F.data == "confirm_lead_yes")
async def finalize_lead(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = call.from_user

    # 1. Ma'lumotlar bazasiga saqlash
    lead_id = await Database.create_lead(
        user_id=user.id,
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        age=data.get("age"),
        region=data.get("region"),
        course_name=data.get("chosen_course"),
        time_preference=data.get("time_preference")
    )

    # 2. Sotuvchilarni (Sales team) topish va yuborish
    active_sales = await Database.get_active_sales_reps()
    sales_text = format_lead_notification(
        lead={
            "full_name": data.get("full_name"),
            "phone": data.get("phone"),
            "age": data.get("age"),
            "region": data.get("region"),
            "course_name": data.get("chosen_course"),
            "time_preference": data.get("time_preference")
        },
        lead_id=lead_id,
        username=user.username
    )
    sales_keyboard = get_sales_lead_actions(lead_id=lead_id, current_status="YANGI")

    recipients_count = 0
    # Barcha faol sotuvchilar profiliga yuborish
    for sales_rep in active_sales:
        try:
            await call.bot.send_message(
                chat_id=sales_rep["telegram_id"],
                text=sales_text,
                reply_markup=sales_keyboard
            )
            recipients_count += 1
        except Exception as e:
            logger.error(f"Sotuvchiga lid yuborishda xatolik ({sales_rep['telegram_id']}): {e}")

    # Agar hali birorta ham sotuvchi belgilanmagan bo'lsa, xabar yo'qolmasligi uchun asosiy adminlarga yuboramiz
    if recipients_count == 0:
        for admin_id in ADMINS:
            try:
                await call.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ <i>Hozircha sotuvchilar biriktirilmaganligi sababli yangi murojaat sizga yuborildi:</i>\n\n{sales_text}",
                    reply_markup=sales_keyboard
                )
            except Exception as e:
                logger.error(f"Adminga lid yuborishda xatolik ({admin_id}): {e}")

    await state.clear()
    await call.message.delete()

    # Foydalanuvchiga muvaffaqiyat xabari
    is_admin = user.id in ADMINS
    is_sales = await Database.is_sales_rep(user.id)

    success_msg = (
        "🎉 <b>Arizangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
        f"Sizning ariza raqamingiz: <b>#{lead_id}</b>\n\n"
        "⚡️ ITLive o'quv markazining tajribali mutaxassisi tez orada siz bilan bog'lanadi va "
        "barcha savollaringizga batafsil javob beradi.\n\n"
        "Bizni tanlaganingiz uchun tashakkur! 🚀"
    )

    await call.message.answer(
        success_msg,
        reply_markup=get_main_keyboard(is_admin=is_admin, is_sales=is_sales)
    )
    await call.answer()

@router.callback_query(RegistrationStates.confirm, F.data == "confirm_lead_no")
async def cancel_lead_confirm(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    user = call.from_user
    is_admin = user.id in ADMINS
    is_sales = await Database.is_sales_rep(user.id)
    await call.message.answer(
        "❌ Ariza qoldirish bekor qilindi.",
        reply_markup=get_main_keyboard(is_admin=is_admin, is_sales=is_sales)
    )
    await call.answer()
