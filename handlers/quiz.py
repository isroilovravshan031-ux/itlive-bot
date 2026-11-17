from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import QuizStates
from keyboards.inline import get_quiz_options_inline
from keyboards.reply import get_main_keyboard, get_cancel_keyboard
from database.models import Database
from config import ADMINS

router = Router(name="quiz")

QUIZ_QUESTIONS = [
    {
        "q": "1️⃣ <b>Sizga qaysi jarayon ko'proq zavq bag'ishlaydi?</b>",
        "options": [
            ("🧠 Murakkab mantiqiy masalalar va serverlar bilan ishlash", "backend"),
            ("🎨 Chiroyli ko'rinish, saytlar va foydalanuvchi interfeysi", "frontend"),
            ("📱 Har kuni ishlatiladigan qulay mobil ilovalar yaratish", "mobile"),
            ("✨ Ijodkorlik, rasmlar, ranglar va brend dizayni", "design")
        ]
    },
    {
        "q": "2️⃣ <b>Matematika va mantiqiy fikrlashga qiziqishingiz qanday?</b>",
        "options": [
            ("🔥 Juda kuchli, algoritmlar va hisob-kitoblarni yaxshi ko'raman", "backend"),
            ("⚡️ O'rtacha, ko'proq amaliy va vizual natijani ko'rishni xohlayman", "frontend"),
            ("🛡 Xavfsizlik, tizim zaifliklari va himoya qiziqtiradi", "security"),
            ("🖌 Matematikadan ko'ra ijodiy g'oyalar ko'proq ustun", "design")
        ]
    },
    {
        "q": "3️⃣ <b>Siz uchun eng faxrlanarli natija qaysi bo'lar edi?</b>",
        "options": [
            ("💳 Bank yoki to'lov tizimining to'xtovsiz xavfsiz ishlashi", "backend"),
            ("📱 App Store / Google Play da yuz minglab yuklangan mobil ilova", "mobile"),
            ("🌐 Barcha qurilmalarda tez va silliq ochiladigan zamonaviy veb-sayt", "frontend"),
            ("🏆 Xalqaro tan olingan brendning unikal logotipi va interfeysi", "design")
        ]
    },
    {
        "q": "4️⃣ <b>Ish joyingizda qanday vazifa sizga ko'proq mos?</b>",
        "options": [
            ("💻 Chuqur konsentratsiya, kod yozish va arxitektura qurish", "backend"),
            ("🎨 Mahsulotning foydalanuvchiga qulayligi (UX) va chiroyi (UI)", "design"),
            ("🚀 Tezkor mahsulot chiqarish va mijozlar bilan interaktivlik", "frontend"),
            ("🔐 Serverlar barqarorligi va kiber-hujumlarni qaytarish", "security")
        ]
    },
    {
        "q": "5️⃣ <b>IT sohasini qanday maqsadda o'rganmoqchisiz?</b>",
        "options": [
            ("💵 Yuqori oylik va xalqaro masofaviy (Remote) ish", "backend"),
            ("🚀 O'z shaxsiy startapim yoki biznesimni ishga tushirish", "mobile"),
            ("⚡️ Qisqa muddatda talabgir kasb egasi bo'lib daromadga chiqish", "frontend"),
            ("🎨 Erkin grafik (Frilans) orqali dunyo bo'ylab sayohat qilib ishlash", "design")
        ]
    }
]

# Kvizni boshlash
@router.message(F.text == "💡 IT Kasb tanlash testi")
async def start_quiz(message: Message, state: FSMContext):
    await state.clear()
    first_q = QUIZ_QUESTIONS[0]
    await message.answer(
        "💡 <b>IT Kasb tanlash testiga xush kelibsiz!</b>\n\n"
        "Qaysi IT yo'nalishi aynan sizning qobiliyatingiz, xarakteringiz va maqsadlaringizga mos "
        "kelishini 5 ta qisqa savol orqali aniqlab beramiz.\n\n"
        f"{first_q['q']}",
        reply_markup=get_quiz_options_inline(1, first_q["options"])
    )
    await state.set_state(QuizStates.q1)
    await state.update_data(scores={"backend": 0, "frontend": 0, "mobile": 0, "design": 0, "security": 0})

# Savollarga javob berish
@router.callback_query(QuizStates.q1, F.data.startswith("quiz:1:"))
@router.callback_query(QuizStates.q2, F.data.startswith("quiz:2:"))
@router.callback_query(QuizStates.q3, F.data.startswith("quiz:3:"))
@router.callback_query(QuizStates.q4, F.data.startswith("quiz:4:"))
@router.callback_query(QuizStates.q5, F.data.startswith("quiz:5:"))
async def process_quiz_answer(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    step = int(parts[1])
    chosen_tag = parts[2]

    data = await state.get_data()
    scores = data.get("scores", {"backend": 0, "frontend": 0, "mobile": 0, "design": 0, "security": 0})
    scores[chosen_tag] = scores.get(chosen_tag, 0) + 1
    await state.update_data(scores=scores)

    if step < 5:
        next_step = step + 1
        next_q = QUIZ_QUESTIONS[next_step - 1]

        state_map = {
            2: QuizStates.q2,
            3: QuizStates.q3,
            4: QuizStates.q4,
            5: QuizStates.q5
        }
        await state.set_state(state_map[next_step])

        await call.message.edit_text(
            f"{next_q['q']}",
            reply_markup=get_quiz_options_inline(next_step, next_q["options"])
        )
        await call.answer()
    else:
        # Kviz yakunlandi — Natijani hisoblash
        best_direction = max(scores, key=scores.get)

        results_info = {
            "backend": {
                "title": "🐍 Python & Backend Dasturlash",
                "desc": (
                    "Sizda kuchli mantiqiy tahlil, tizimli fikrlash va muammolarni ildizi bilan hal qilish "
                    "qobiliyati yuqori! Siz uchun eng optimal yo'nalish — <b>Python Backend</b>. Bu sohada siz "
                    "veb-saytlar, mobil ilovalar va yirik bank tizimlarining asosiy yuragini yaratasiz."
                ),
                "course_name": "🐍 Python Backend Dasturlash"
            },
            "frontend": {
                "title": "🌐 Frontend Veb Dasturlash",
                "desc": (
                    "Siz amaliy natijalarni darhol ko'rishni, interaktiv va tezkor veb-ilovalarni yaratishni "
                    "yoqtirasiz! Siz uchun eng mos soha — <b>Frontend Dasturlash (React / Next.js)</b>. "
                    "Bu sohada har bir yozgan kodingiz jozibador ekranda jonlanadi."
                ),
                "course_name": "🌐 Frontend Veb Dasturlash"
            },
            "mobile": {
                "title": "📱 Flutter & Mobil Dasturlash",
                "desc": (
                    "Siz doimo harakatdasiz va har bir insonning cho'ntagidagi smartfonda ishlaydigan dasturlar "
                    "yaratishni xohlaysiz! Siz uchun eng to'g'ri tanlov — <b>Flutter Mobil Dasturlash</b>."
                ),
                "course_name": "📱 Flutter & Android/iOS Mobile"
            },
            "design": {
                "title": "🎨 Grafik Dizayn & UI/UX",
                "desc": (
                    "Sizda ajoyib vizual did, ijodiy fantaziya va go'zallikni his qilish tuyg'usi bor! "
                    "Siz uchun eng mukammal yo'nalish — <b>Grafik Dizayn va UI/UX</b>. Siz odamlar sevib "
                    "ishlatadigan qulay va maftunkor interfeyslar yaratasiz."
                ),
                "course_name": "🎨 Grafik Dizayn & UI/UX"
            },
            "security": {
                "title": "🛡 Kiberxavfsizlik (Ethical Hacking)",
                "desc": (
                    "Siz qiziquvchan, zaifliklarni topishga usta va himoyalashga ishtiyoqmand insonsiz! "
                    "Siz uchun ideal soha — <b>Kiberxavfsizlik</b>. IT olamida eng talabgir va nufuzli kasb."
                ),
                "course_name": "🛡 Kiberxavfsizlik (Ethical Hacking)"
            }
        }

        res = results_info.get(best_direction, results_info["backend"])

        result_text = (
            "🎉 <b>TEST NATIJASI TAYYOR!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 <b>Sizga eng mos yo'nalish:</b>\n"
            f"👉 <b>{res['title']}</b>\n\n"
            f"📝 <b>Xulosa:</b>\n{res['desc']}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ushbu yo'nalish bo'yicha ITLive o'quv markazida 0 dan boshlab professional darajagacha o'rganishingiz mumkin!"
        )

        enroll_inline = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ushbu kursga yozilish", callback_data="start_registration")],
            [InlineKeyboardButton(text="🎁 Bepul sinov darsiga qatnashish", callback_data="enroll_trial")],
            [InlineKeyboardButton(text="🔄 Testni qayta topshirish", callback_data="restart_quiz")]
        ])

        await state.clear()
        await call.message.edit_text(result_text, reply_markup=enroll_inline)
        await call.answer()

@router.callback_query(F.data == "restart_quiz")
async def restart_quiz_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
    first_q = QUIZ_QUESTIONS[0]
    await call.message.edit_text(
        "💡 <b>IT Kasb tanlash testi (Qayta boshlash):</b>\n\n"
        f"{first_q['q']}",
        reply_markup=get_quiz_options_inline(1, first_q["options"])
    )
    await state.set_state(QuizStates.q1)
    await state.update_data(scores={"backend": 0, "frontend": 0, "mobile": 0, "design": 0, "security": 0})
    await call.answer()
