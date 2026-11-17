import re
from html import escape
from typing import Optional, Dict

def clean_phone_number(raw_phone: str) -> Optional[str]:
    """
    Telefon raqamni tozalaydi va O'zbekiston formati (+998XXXXXXXXX) yoki xalqaro formatga keltiradi.
    Agar noto'g'ri bo'lsa None qaytaradi.
    """
    cleaned = re.sub(r"[^\d+]", "", raw_phone)
    if cleaned.startswith("998") and len(cleaned) == 12:
        cleaned = "+" + cleaned
    elif len(cleaned) == 9 and cleaned.isdigit():
        cleaned = "+998" + cleaned
    elif cleaned.startswith("+998") and len(cleaned) == 13:
        pass
    elif cleaned.startswith("+") and len(cleaned) >= 11:
        pass
    else:
        return None
    return cleaned

def format_lead_notification(lead: dict, lead_id: int, username: Optional[str] = None) -> str:
    """Sotuvchilar uchun yuboriladigan yangi lid xabari"""
    lead = {key: escape(str(value)) if value is not None else "" for key, value in lead.items()}
    user_tag = f"@{escape(username)}" if username else "Mavjud emas"
    course = lead.get("course_name") or "Umumiy konsultatsiya"
    time_pref = lead.get("time_preference") or "Ko'rsatilmagan"
    phone = lead.get("phone", "")

    # Telefon qilish uchun toza raqam
    tel_link = f"tel:{phone}"

    return (
        "🚨 <b>YANGI MUROJAAT TUSHDI!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Lid raqami:</b> #{lead_id}\n"
        f"👤 <b>Mijoz:</b> {lead.get('full_name')}\n"
        f"📞 <b>Telefon:</b> <code>{phone}</code>\n"
        f"🎂 <b>Yoshi:</b> {lead.get('age')} yosh\n"
        f"📍 <b>Hudud:</b> {lead.get('region')}\n"
        f"💻 <b>Qiziqqan kursi:</b> <b>{course}</b>\n"
        f"⏰ <b>Qulay dars vaqti:</b> {time_pref}\n"
        f"✈️ <b>Telegram:</b> {user_tag}\n"
        f"📅 <b>Vaqti:</b> {str(lead.get('created_at', 'Hozir'))[:19]}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡️ <i>Hurmatli sotuvchi, mijoz bilan iloji boricha tezroq bog'laning va quyidagi tugmalar orqali holatni yangilang!</i>"
    )

def format_lead_summary_card(lead: dict) -> str:
    """Admin yoki sotuvchi uchun bitta lid haqida batafsil karta"""
    lead = {key: escape(str(value)) if value is not None else "" for key, value in lead.items()}
    status_icons = {
        "YANGI": "🆕 Yangi",
        "BOGLANILDI": "📞 Bog'lanildi",
        "YOZILDI": "✅ O'qishga yozildi",
        "BEKOR_QILINDI": "❌ Bekor qilindi"
    }
    status = status_icons.get(lead.get("status"), lead.get("status"))

    return (
        f"📋 <b>Ariza #{lead.get('id')} tafsiloti</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Ism:</b> {lead.get('full_name')}\n"
        f"📞 <b>Telefon:</b> <code>{lead.get('phone')}</code>\n"
        f"🎂 <b>Yoshi:</b> {lead.get('age')} yosh\n"
        f"📍 <b>Hudud:</b> {lead.get('region')}\n"
        f"💻 <b>Kurs:</b> {lead.get('course_name') or 'Umumiy'}\n"
        f"⏰ <b>Vaqt tanlovi:</b> {lead.get('time_preference') or '-'}\n"
        f"📊 <b>Holati:</b> <b>{status}</b>\n"
        f"💬 <b>Izoh:</b> {lead.get('sales_notes') or 'Izoh kiritilmagan'}\n"
        f"📅 <b>Sana:</b> {str(lead.get('created_at', ''))[:19]}\n"
    )

FAQ_ITEMS = [
    {
        "q": "1. Kurslarda o'qish uchun oldindan bilim talab qilinadimi?",
        "a": "Yo'q! Bizning barcha asosiy kurslarimiz 0 dan boshlanadi. Agar kompyuterni umuman tushunmasangiz, avval maxsus IT Foundation bosqichidan o'tishingiz mumkin."
    },
    {
        "q": "2. Darslar qaysi shaklda o'tiladi?",
        "a": "Darslarimiz zamonaviy jihozlangan xonalarda, to'liq amaliyot shaklida olib boriladi. Darslarning 80% amaliy loyihalar va vazifalardan iborat."
    },
    {
        "q": "3. O'qishni tugatgach sertifikat beriladimi?",
        "a": "Ha, kursni muvaffaqiyatli tugatgan, barcha imtihon va amaliy loyihalarni topshirgan o'quvchilarga ITLive ning xalqaro darajadagi sertifikati taqdim etiladi."
    },
    {
        "q": "4. Markaz ish bilan ta'minlashga yordam beradimi?",
        "a": "Albatta! ITLive Karyera Markazi o'quvchilarga rezyume tayyorlash, intervyulardan muvaffaqiyatli o'tish bo'yicha yordam beradi va eng yaxshi bitiruvchilarni hamkor IT kompaniyalarga tavsiya etadi."
    },
    {
        "q": "5. O'zim bilan noutbuk olib kelishim shartmi?",
        "a": "O'quv markazimiz har bir o'quvchi uchun barcha kerakli dasturlar o'rnatilgan zamonaviy kompyuterlar bilan ta'minlangan. Biroq, uyda mustaqil ishlash va topshiriqlarni bajarish uchun o'zingizda noutbuk bo'lishi tavsiya etiladi."
    },
    {
        "q": "6. To'lovni bo'lib to'lash imkoniyati bormi?",
        "a": "Ha, to'lovlar har oyma-oy amalga oshiriladi. Shuningdek, to'lovni Payme, Click, naqd yoki bank o'tkazmasi orqali to'lashingiz mumkin."
    }
]

MENTORS_LIST = [
    {
        "name": "Abbosbek Karimov",
        "role": "Senior Python & Backend Mentor",
        "experience": "7+ yil tijoriy tajriba",
        "companies": "Xorijiy FinTech kompaniyasi va yirik bank tizimlari ishlab chiquvchisi"
    },
    {
        "name": "Sardorbek Rahimov",
        "role": "Lead Frontend Engineer",
        "experience": "5+ yil tajriba",
        "companies": "React, Next.js, TypeScript bo'yicha 50 dan ortiq yirik loyihalar muallifi"
    },
    {
        "name": "Dilnoza Olimova",
        "role": "Senior UI/UX Designer & Art Director",
        "experience": "6+ yil tajriba",
        "companies": "Xalqaro brendlar uchun brending va mobil ilovalar interfeyslari dizayneri"
    },
    {
        "name": "Farxod Saidov",
        "role": "Senior Flutter Developer",
        "experience": "4+ yil tajriba",
        "companies": "Play Market va App Store da 200,000+ yuklab olingan mobil ilovalar yaratuvchisi"
    }
]
