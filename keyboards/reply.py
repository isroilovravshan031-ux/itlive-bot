from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard(is_admin: bool = False, is_sales: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy foydalanuvchi menyusi (10 dan ortiq funksiyalar bilan)"""
    keyboard = [
        [
            KeyboardButton(text="📝 Kursga yozilish"),
            KeyboardButton(text="📚 Kurslarimiz")
        ],
        [
            KeyboardButton(text="🎁 Bepul sinov darsi"),
            KeyboardButton(text="💡 IT Kasb tanlash testi")
        ],
        [
            KeyboardButton(text="📍 Bizning lokatsiya"),
            KeyboardButton(text="📞 Bog'lanish va Raqamlar")
        ],
        [
            KeyboardButton(text="ℹ️ Biz haqimizda"),
            KeyboardButton(text="👨‍🏫 Mentorlarimiz")
        ],
        [
            KeyboardButton(text="🏷 Chegirmalar va Aksiyalar"),
            KeyboardButton(text="❓ FAQ (Savol-javoblar)")
        ],
        [
            KeyboardButton(text="✍️ Fikr va takliflar"),
            KeyboardButton(text="📂 Mening arizalarim")
        ]
    ]

    extra_buttons = []
    if is_admin:
        extra_buttons.append(KeyboardButton(text="👑 Admin Panel"))
    if is_sales:
        extra_buttons.append(KeyboardButton(text="💼 Sotuvchi Kabineti"))

    if extra_buttons:
        keyboard.append(extra_buttons)

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        persistent=True
    )

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni bitta tugma orqali ulashish klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni ulashish", request_contact=True)],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_region_keyboard() -> ReplyKeyboardMarkup:
    """Viloyat / hududni tanlash yoki lokatsiya yuborish klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Aniq lokatsiyamni yuborish", request_location=True)],
            [KeyboardButton(text="Toshkent shahri"), KeyboardButton(text="Toshkent viloyati")],
            [KeyboardButton(text="Samarqand"), KeyboardButton(text="Farg'ona")],
            [KeyboardButton(text="Andijon"), KeyboardButton(text="Namangan")],
            [KeyboardButton(text="Buxoro"), KeyboardButton(text="Qashqadaryo")],
            [KeyboardButton(text="Surxondaryo"), KeyboardButton(text="Xorazm")],
            [KeyboardButton(text="Navoiy"), KeyboardButton(text="Jizzax")],
            [KeyboardButton(text="Sirdaryo"), KeyboardButton(text="Qoraqalpog'iston")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_time_preference_keyboard() -> ReplyKeyboardMarkup:
    """Dars vaqtini tanlash klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌅 Ertalab (09:00 - 12:00)")],
            [KeyboardButton(text="☀️ Tushdan keyin (14:00 - 17:00)")],
            [KeyboardButton(text="🌙 Kechqurun (18:30 - 21:00)")],
            [KeyboardButton(text="🕒 Menga vaqtning farqi yo'q")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Faqat bekor qilish tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
