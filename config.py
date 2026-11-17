import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ro'yxati (vergul bilan ajratilgan ID lar)
_admins_str = os.getenv("ADMINS", "")
ADMINS = [int(admin_id.strip()) for admin_id in _admins_str.split(",") if admin_id.strip().isdigit()]

DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "itlive_bot.db"))

# Ma'lumotlar bazasi papkasini yaratish
os.makedirs(Path(DATABASE_PATH).parent, exist_ok=True)

# Default sozlamalar (agar bazada bo'lmasa)
DEFAULT_SETTINGS = {
    "center_name": "ITLive Academy",
    "phone_1": "+998 71 200 00 00",
    "phone_2": "+998 90 123 45 67",
    "address": "Toshkent shahri, Yunusobod tumani, Amir Temur shoh ko'chasi, 107-uy",
    "landmark": "Metro: Shahriston bekati yaqinida, IT Park binosi ro'parasida",
    "latitude": "41.3653",
    "longitude": "69.2887",
    "working_hours": "Dushanba - Shanba: 09:00 dan 20:00 gacha\nYakshanba: Dam olish kuni",
    "instagram": "https://instagram.com/itlive_uz",
    "telegram": "https://t.me/itlive_admin",
    "website": "https://itlive.uz",
    "youtube": "https://youtube.com/@itlive",
    "about_text": (
        "🚀 <b>ITLive Academy</b> — zamonaviy IT kasblarini o'rgatuvchi yetakchi innovatsion ta'lim markazi!\n\n"
        "Bizning asosiy maqsadimiz — yoshlarni zamonaviy IT bozorida eng talabgir bo'lgan mutaxassis "
        "qilib tayyorlash va ularni nufuzli IT kompaniyalarga ishga joylashishiga ko'maklashishdir.\n\n"
        "✨ <b>Nima uchun aynan ITLive?</b>\n"
        "• 100% amaliyotga yo'naltirilgan darslar\n"
        "• Kuchli va tajribali Senior mentorlar\n"
        "• Zamonaviy noutbuklar va coworiking zonasi\n"
        "• Karyera markazi va ish bilan ta'minlash dasturi\n"
        "• Xalqaro standartdagi sertifikat\n"
        "• Portfolio yaratish va real startap loyihalarda qatnashish imkoniyati"
    ),
    "discounts_text": (
        "🎁 <b>ITLive Academy maxsus taklif va chegirmalari:</b>\n\n"
        "1️⃣ <b>\"Do'stingni olib kel\" aksiyasi:</b> O'zingiz bilan birga o'rtoqingizni olib kelsangiz, "
        "har ikkingizga <b>15% chegirma</b> beriladi!\n\n"
        "2️⃣ <b>To'liq to'lov uchun keshbek:</b> Kurs to'lovini to'liq 100% bir martada to'laganlar uchun "
        "<b>10% maxsus chegirma</b> mavjud!\n\n"
        "3️⃣ <b>Bepul sinov darsi:</b> Har bir yangi o'quvchi uchun 1-dars mutlaqo bepul! Kurs sifati bilan "
        "shaxsan tanishing."
    )
}
