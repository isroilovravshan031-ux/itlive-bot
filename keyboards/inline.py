from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= Kurslar uchun Inline tugmalar =================
def get_courses_inline(courses: List[dict]) -> InlineKeyboardMarkup:
    """Barcha kurslar ro'yxati inline tugmalari"""
    buttons = []
    for c in courses:
        buttons.append([InlineKeyboardButton(text=c["name"], callback_data=f"course_view:{c['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_course_detail_inline(course_id: int) -> InlineKeyboardMarkup:
    """Kurs batafsil ko'rinishidagi yozilish va orqaga tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ushbu kursga yozilish", callback_data=f"enroll_course:{course_id}")],
            [InlineKeyboardButton(text="🔙 Barcha kurslar", callback_data="courses_list")]
        ]
    )

def get_courses_choice_inline(courses: List[dict]) -> InlineKeyboardMarkup:
    """Ro'yxatdan o'tish jarayonida kurs tanlash inline tugmalari"""
    buttons = []
    for c in courses:
        buttons.append([InlineKeyboardButton(text=c["name"], callback_data=f"select_course:{c['name']}")])
    buttons.append([InlineKeyboardButton(text="💡 Maslahat kerak (Aniq bilmayman)", callback_data="select_course:Umumiy konsultatsiya")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================= Sotuvchilar (Sales Reps) uchun Lead boshqaruv tugmalari =================
def get_sales_lead_actions(lead_id: int, current_status: str = "YANGI") -> InlineKeyboardMarkup:
    """Sotuvchi o'z profilida lid statusini o'zgartirishi uchun tugmalar"""
    status_icons = {
        "YANGI": "🆕",
        "BOGLANILDI": "📞",
        "YOZILDI": "✅",
        "BEKOR_QILINDI": "❌"
    }

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{'👉 ' if current_status == 'BOGLANILDI' else ''}📞 Bog'lanildi",
                callback_data=f"lead_status:{lead_id}:BOGLANILDI"
            ),
            InlineKeyboardButton(
                text=f"{'👉 ' if current_status == 'YOZILDI' else ''}✅ O'qishga yozildi",
                callback_data=f"lead_status:{lead_id}:YOZILDI"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{'👉 ' if current_status == 'BEKOR_QILINDI' else ''}❌ Bekor qilindi",
                callback_data=f"lead_status:{lead_id}:BEKOR_QILINDI"
            ),
            InlineKeyboardButton(
                text="💬 Izoh yozish",
                callback_data=f"lead_note:{lead_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================= Admin Panel Asosiy Menyu =================
def get_admin_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats"),
                InlineKeyboardButton(text="📥 Barcha Lidlar", callback_data="admin:leads")
            ],
            [
                InlineKeyboardButton(text="📑 Excel hisobot yuklash", callback_data="admin:export_excel"),
                InlineKeyboardButton(text="📚 Kurslarni boshqarish", callback_data="admin:courses")
            ],
            [
                InlineKeyboardButton(text="👥 Sotuvchilar guruhi", callback_data="admin:sales"),
                InlineKeyboardButton(text="📢 Xabarnoma yuborish", callback_data="admin:broadcast")
            ],
            [
                InlineKeyboardButton(text="⚙️ Bot sozlamalari", callback_data="admin:settings"),
                InlineKeyboardButton(text="💬 Fikrlar & Takliflar", callback_data="admin:feedback")
            ]
        ]
    )

# ================= Admin Kurslar Menyu =================
def get_admin_courses_inline(courses: List[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for c in courses:
        status = "🟢" if c.get("is_active", 1) else "🔴"
        buttons.append([
            InlineKeyboardButton(
                text=f"{status} {c['name']}",
                callback_data=f"admin_course:{c['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Yangi kurs qo'shish", callback_data="admin:add_course")])
    buttons.append([InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_course_detail_inline(course_id: int, is_active: bool) -> InlineKeyboardMarkup:
    toggle_text = "🔴 O'chirish (Faolsizlantirish)" if is_active else "🟢 Yoqish (Faollashtirish)"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_text, callback_data=f"admin_toggle_course:{course_id}")],
            [InlineKeyboardButton(text="🗑 Kursni butunlay o'chirish", callback_data=f"admin_delete_course:{course_id}")],
            [InlineKeyboardButton(text="🔙 Kurslar ro'yxatiga", callback_data="admin:courses")]
        ]
    )

# ================= Admin Sotuvchilar Menyu =================
def get_admin_sales_inline(sales_reps: List[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for s in sales_reps:
        buttons.append([
            InlineKeyboardButton(
                text=f"👤 {s['full_name']} (ID: {s['telegram_id']})",
                callback_data=f"sales_view:{s['telegram_id']}"
            ),
            InlineKeyboardButton(
                text="❌ O'chirish",
                callback_data=f"sales_delete:{s['telegram_id']}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="➕ Sotuvchi qo'shish", callback_data="admin:add_sales")])
    buttons.append([InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================= Admin Sozlamalar Menyu =================
def get_admin_settings_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏢 Markaz nomi", callback_data="admin_set:center_name"),
                InlineKeyboardButton(text="📞 Telefon 1", callback_data="admin_set:phone_1")
            ],
            [
                InlineKeyboardButton(text="📞 Telefon 2", callback_data="admin_set:phone_2"),
                InlineKeyboardButton(text="📍 Manzil matni", callback_data="admin_set:address")
            ],
            [
                InlineKeyboardButton(text="🧭 Mo'ljal matni", callback_data="admin_set:landmark"),
                InlineKeyboardButton(text="⏰ Ish vaqti", callback_data="admin_set:working_hours")
            ],
            [
                InlineKeyboardButton(text="📸 Instagram", callback_data="admin_set:instagram"),
                InlineKeyboardButton(text="🌐 Veb-sayt", callback_data="admin_set:website")
            ],
            [
                InlineKeyboardButton(text="ℹ️ Biz haqimizda matni", callback_data="admin_set:about_text"),
                InlineKeyboardButton(text="🎁 Aksiyalar matni", callback_data="admin_set:discounts_text")
            ],
            [
                InlineKeyboardButton(text="🔙 Admin menyu", callback_data="admin:main")
            ]
        ]
    )

# ================= Ijtimoiy tarmoqlar va kontaktlar tugmalari =================
def get_social_links_inline(settings: Dict[str, str]) -> InlineKeyboardMarkup:
    buttons = []

    row1 = []
    if settings.get("instagram"):
        row1.append(InlineKeyboardButton(text="📸 Instagram", url=settings["instagram"]))
    if settings.get("telegram"):
        row1.append(InlineKeyboardButton(text="✈️ Telegram Admin", url=settings["telegram"]))
    if row1:
        buttons.append(row1)

    row2 = []
    if settings.get("website"):
        row2.append(InlineKeyboardButton(text="🌐 Rasmiy sayt", url=settings["website"]))
    if settings.get("youtube"):
        row2.append(InlineKeyboardButton(text="▶️ YouTube", url=settings["youtube"]))
    if row2:
        buttons.append(row2)

    buttons.append([InlineKeyboardButton(text="📝 Kursga ro'yxatdan o'tish", callback_data="start_registration")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================= Kviz / Test uchun tugmalar =================
def get_quiz_options_inline(step: int, options: List[tuple]) -> InlineKeyboardMarkup:
    """
    options: list of (button_text, value)
    """
    buttons = []
    for text, val in options:
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"quiz:{step}:{val}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
