from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from database.models import Database
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_courses_inline, get_course_detail_inline, get_social_links_inline
from utils.text_helpers import FAQ_ITEMS, MENTORS_LIST
from config import ADMINS
import logging

logger = logging.getLogger(__name__)

router = Router(name="user_handlers")

# ================= /start komandasi =================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    is_admin = user.id in ADMINS
    is_sales = await Database.is_sales_rep(user.id)

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    await Database.add_or_update_user(user.id, user.username, full_name)

    center_name = await Database.get_setting("center_name", "ITLive Academy")

    welcome_text = (
        f"Assalomu alaykum, <b>{user.first_name}</b>! 👋\n\n"
        f"<b>{center_name}</b> rasmiy Telegram botiga xush kelibsiz!\n\n"
        "Biz orqali zamonaviy IT kasblarini o'rganishingiz, ochiq darslarga yozilishingiz, "
        "o'zingizga mos sohani aniqlashingiz va kurslarimiz bo'yicha to'liq ma'lumot olishingiz mumkin.\n\n"
        "👇 Kerakli bo'limni tanlash uchun quyidagi menyudan foydalaning:"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(is_admin=is_admin, is_sales=is_sales)
    )

# ================= /help va FAQ =================
@router.message(Command("help"))
@router.message(F.text.in_(["❓ FAQ (Savol-javoblar)", "help", "Yordam"]))
async def cmd_help(message: Message):
    text = "❓ <b>ENG KO'P BERILADIGAN SAVOLLAR (FAQ)</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for item in FAQ_ITEMS:
        text += f"🔹 <b>{item['q']}</b>\n{item['a']}\n\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💡 <i>Boshqa savollaringiz bo'lsa, mutaxassisimiz bilan bog'lanishingiz mumkin.</i>"

    enroll_inline = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Biz bilan bog'lanish", callback_data="show_contacts")],
        [InlineKeyboardButton(text="📝 Kursga yozilish", callback_data="start_registration")]
    ])

    await message.answer(text, reply_markup=enroll_inline)

# ================= ❌ Bekor qilish =================
@router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    is_admin = user.id in ADMINS
    is_sales = await Database.is_sales_rep(user.id)

    await message.answer(
        "Amal bekor qilindi. Bosh menyudasiz.",
        reply_markup=get_main_keyboard(is_admin=is_admin, is_sales=is_sales)
    )

# ================= 📚 Kurslarimiz =================
@router.message(F.text == "📚 Kurslarimiz")
@router.callback_query(F.data == "courses_list")
async def show_courses_list(event: Message | CallbackQuery):
    courses = await Database.get_active_courses()
    if not courses:
        text = "Hozircha faol kurslar mavjud emas."
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text)
            await event.answer()
        else:
            await event.answer(text)
        return

    text = (
        "📚 <b>ITLive Academy professional o'quv kurslari:</b>\n\n"
        "Bizda barcha darslar noldan amaliyot asosida o'rgatiladi. "
        "O'zingizni qiziqtirgan kurs haqida batafsil (narxi, davomiyligi, texnologiyalari) "
        "bilish uchun quyidagi tugmalardan birini bosing:"
    )

    markup = get_courses_inline(courses)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=markup)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup)

# Kurs haqida batafsil ma'lumot ko'rish
@router.callback_query(F.data.startswith("course_view:"))
async def view_course_detail(call: CallbackQuery):
    course_id = int(call.data.split(":")[1])
    course = await Database.get_course_by_id(course_id)
    if not course:
        await call.answer("Kurs topilmadi!", show_alert=True)
        return

    text = (
        f"📖 <b>{course['name']}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Kurs haqida:</b>\n{course['description']}\n\n"
        f"⏳ <b>Davomiyligi:</b> {course['duration']}\n"
        f"💰 <b>Narxi:</b> {course['price']}\n"
        f"🛠 <b>O'rganiladigan texnologiyalar:</b>\n<code>{course.get('technologies') or 'Amaliy dasturlar'}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎓 <i>Bitiruvchilarga xalqaro sertifikat va ishga joylashishda ko'mak beriladi!</i>"
    )

    await call.message.edit_text(text, reply_markup=get_course_detail_inline(course_id))
    await call.answer()

# ================= 📍 Bizning lokatsiya =================
@router.message(F.text == "📍 Bizning lokatsiya")
async def show_location(message: Message):
    settings = await Database.get_all_settings()
    address = settings.get("address", "Toshkent shahri, Yunusobod tumani")
    landmark = settings.get("landmark", "Metro: Shahriston bekati yaqinida")
    lat_str = settings.get("latitude", "41.3653")
    lon_str = settings.get("longitude", "69.2887")

    try:
        lat = float(lat_str)
        lon = float(lon_str)
        # Telegram xaritasi orqali nuqtani yuborish
        await message.answer_location(latitude=lat, longitude=lon)
    except Exception as e:
        logger.warning(f"Lokatsiyani yuborishda xatolik: {e}")

    location_text = (
        "📍 <b>ITLive Academy o'quv markazi manzili:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏢 <b>Manzil:</b> {address}\n"
        f"🧭 <b>Mo'ljal:</b> {landmark}\n"
        f"⏰ <b>Ish vaqtlari:</b> {settings.get('working_hours', '09:00 - 20:00')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Kelishingizdan oldin ro'yxatdan o'tishingizni tavsiya qilamiz!"
    )

    map_links_inline = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗺 Yandex Xarita", url=f"https://yandex.uz/maps/?pt={lon_str},{lat_str}&z=16&l=map"),
            InlineKeyboardButton(text="🗺 Google Maps", url=f"https://www.google.com/maps/search/?api=1&query={lat_str},{lon_str}")
        ],
        [
            InlineKeyboardButton(text="📝 Kursga yozilish", callback_data="start_registration")
        ]
    ])

    await message.answer(location_text, reply_markup=map_links_inline)

# ================= 📞 Bog'lanish va Raqamlar =================
@router.message(F.text == "📞 Bog'lanish va Raqamlar")
@router.callback_query(F.data == "show_contacts")
async def show_contacts(event: Message | CallbackQuery):
    settings = await Database.get_all_settings()

    text = (
        "📞 <b>ITLive Academy bilan aloqa:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"☎️ <b>Telefon 1:</b> <code>{settings.get('phone_1', '+998 71 200 00 00')}</code>\n"
        f"📱 <b>Telefon 2:</b> <code>{settings.get('phone_2', '+998 90 123 45 67')}</code>\n"
        f"⏰ <b>Ish vaqtlari:</b>\n{settings.get('working_hours', 'Har kuni 09:00 dan 20:00 gacha')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ijtimoiy tarmoqlarimiz orqali ham yangiliklarni kuzatib boring:"
    )

    markup = get_social_links_inline(settings)

    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=markup)
        await event.answer()
    else:
        await event.answer(text, reply_markup=markup)

# ================= ℹ️ Biz haqimizda =================
@router.message(F.text == "ℹ️ Biz haqimizda")
async def show_about(message: Message):
    about_text = await Database.get_setting("about_text", "")
    settings = await Database.get_all_settings()

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Kurslar bilan tanishish", callback_data="courses_list")],
        [InlineKeyboardButton(text="🎁 Bepul sinov darsi", callback_data="enroll_trial")]
    ])

    await message.answer(about_text, reply_markup=markup)

# ================= 👨‍🏫 Mentorlarimiz =================
@router.message(F.text == "👨‍🏫 Mentorlarimiz")
async def show_mentors(message: Message):
    text = (
        "👨‍🏫 <b>ITLive Academy kuchli mentorlar jamoasi:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    for m in MENTORS_LIST:
        text += (
            f"👤 <b>{m['name']}</b>\n"
            f"💼 <b>Yo'nalish:</b> {m['role']}\n"
            f"⏳ <b>Tajriba:</b> {m['experience']}\n"
            f"🏢 <b>Loyiha va kompaniyalar:</b> {m['companies']}\n\n"
        )
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "<i>Bizning ustozlarimiz amaliyotchi mutaxassislar bo'lib, har bir o'quvchiga individual yondashadilar!</i>"

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Ushbu mentorlarda o'qish", callback_data="start_registration")]
    ])

    await message.answer(text, reply_markup=markup)

# ================= 🏷 Chegirmalar va Aksiyalar =================
@router.message(F.text == "🏷 Chegirmalar va Aksiyalar")
async def show_discounts(message: Message):
    discounts = await Database.get_setting("discounts_text", "Chegirmalar mavjud.")

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎉 Chegirma bilan yozilish", callback_data="start_registration")]
    ])

    await message.answer(discounts, reply_markup=markup)

# ================= 📂 Mening arizalarim =================
@router.message(F.text == "📂 Mening arizalarim")
async def show_my_applications(message: Message):
    user_id = message.from_user.id
    leads = await Database.get_user_leads(user_id)

    if not leads:
        await message.answer(
            "📭 Siz hali birorta ham kursga ariza qoldirmagansiz.\n\n"
            "Kurslarimizga ro'yxatdan o'tish uchun quyidagi tugmani bosing:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Kursga ariza qoldirish", callback_data="start_registration")]
            ])
        )
        return

    status_labels = {
        "YANGI": "🆕 Yangi (Ko'rib chiqilmoqda)",
        "BOGLANILDI": "📞 Bog'lanildi (Menejer sizga aloqaga chiqqan)",
        "YOZILDI": "✅ Muvaffaqiyatli qabul qilindi",
        "BEKOR_QILINDI": "❌ Bekor qilingan"
    }

    text = "📂 <b>Sizning arizalaringiz ro'yxati:</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for idx, lead in enumerate(leads, 1):
        stat = status_labels.get(lead["status"], lead["status"])
        course = lead.get("course_name") or "Umumiy"
        time_c = lead.get("time_preference") or "-"
        created = str(lead.get("created_at", ""))[:16]

        text += (
            f"<b>{idx}. Ariza #{lead['id']}</b>\n"
            f"💻 Kurs: <b>{course}</b>\n"
            f"⏰ Qulay vaqt: {time_c}\n"
            f"📊 Holati: <b>{stat}</b>\n"
            f"📅 Yuborilgan: {created}\n\n"
        )

    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "Savollaringiz bo'lsa, call-markazimiz bilan bog'lanishingiz mumkin."

    await message.answer(text)
