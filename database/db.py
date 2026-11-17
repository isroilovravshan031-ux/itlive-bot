import aiosqlite
import logging
from contextlib import asynccontextmanager
from config import DATABASE_PATH, DEFAULT_SETTINGS

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db():
    """SQLite asinxron ulanishini xavfsiz boshqaruvchi context manager"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db

async def init_db():
    """Barcha jadvallarni yaratish va boshlang'ich ma'lumotlarni kiritish"""
    async with get_db() as db:
        await db.execute("PRAGMA foreign_keys = ON;")

        # 1. Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Sotuvchilar (Sales Team) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sales_team (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Kurslar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                duration TEXT NOT NULL,
                price TEXT NOT NULL,
                technologies TEXT,
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0
            );
        """)

        # 4. Lidlar (Murojaatlar) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                age INTEGER NOT NULL,
                region TEXT NOT NULL,
                course_name TEXT,
                time_preference TEXT,
                status TEXT DEFAULT 'YANGI',
                assigned_sales_id INTEGER,
                sales_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 5. Dinamik Bot Sozlamalari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        # 6. Fikr-mulohazalar (Feedback) jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT,
                username TEXT,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Standart sozlamalarni kiritish (agar bo'sh bo'lsa)
        for key, value in DEFAULT_SETTINGS.items():
            await db.execute(
                "INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)",
                (key, value)
            )

        # Standart ITLive kurslarini kiritish (agar bo'sh bo'lsa)
        cursor = await db.execute("SELECT COUNT(*) FROM courses")
        count = (await cursor.fetchone())[0]
        if count == 0:
            default_courses = [
                (
                    "🐍 Python Backend Dasturlash",
                    "Zamonaviy veb-ilovalarning orqa tomoni (Backend), API va ma'lumotlar bazasi bilan ishlashni 0 dan professional darajagacha o'rganing.",
                    "6 oy",
                    "1,200,000 so'm / oy",
                    "Python, Django, FastAPI, PostgreSQL, Docker, Git, REST API",
                    1,
                    1
                ),
                (
                    "🌐 Frontend Veb Dasturlash",
                    "Chiroyli, tezkor va interaktiv saytlar, veb-ilovalarni yaratish sirlarini mukammal egallang.",
                    "6 oy",
                    "1,100,000 so'm / oy",
                    "HTML5, CSS3, Tailwind CSS, JavaScript (ES6+), React.js, Next.js, Redux",
                    1,
                    2
                ),
                (
                    "📱 Flutter & Android/iOS Mobile",
                    "Bitta kod yozish orqali ham Android, ham iOS tizimlari uchun zamonaviy mobil ilovalar ishlab chiqish.",
                    "5 oy",
                    "1,300,000 so'm / oy",
                    "Dart, Flutter, Bloc, Riverpod, Firebase, REST API, App Store & Google Play deploy",
                    1,
                    3
                ),
                (
                    "🎨 Grafik Dizayn & UI/UX",
                    "Logotiplar, brending, ijtimoiy tarmoq postlari va veb-saytlar uchun qulay hamda jozibali foydalanuvchi interfeyslari chizish.",
                    "4 oy",
                    "1,000,000 so'm / oy",
                    "Adobe Photoshop, Adobe Illustrator, Figma, UI/UX tamoyillari, Behance",
                    1,
                    4
                ),
                (
                    "🛡 Kiberxavfsizlik (Ethical Hacking)",
                    "Tarmoqlar, serverlar va dasturiy ta'minotdagi zaifliklarni aniqlash va himoyalash bo'yicha amaliy bilimlar.",
                    "6 oy",
                    "1,400,000 so'm / oy",
                    "Linux, Bash, Kali Linux, Wireshark, Metasploit, Tarmoq xavfsizligi, Web Security",
                    1,
                    5
                ),
                (
                    "💻 IT Foundation (Kompyuter savodxonligi)",
                    "Dasturlashni yangi boshlayotganlar uchun kompyuter arxitekturasi, algoritmlar va dasturlash asoslari.",
                    "2 oy",
                    "800,000 so'm / oy",
                    "Windows/Linux OS, Algoritmlash, C++/Python asoslari, Ofis dasturlari",
                    1,
                    6
                ),
                (
                    "📈 SMM & Raqamli Marketing",
                    "Ijtimoiy tarmoqlarda biznesni rivojlantirish, target reklama sozlash va sotuvlarni oshirish strategiyalari.",
                    "3 oy",
                    "900,000 so'm / oy",
                    "Meta Ads (Facebook/Instagram), Telegram marketing, Kontent-plan, Kopirayting",
                    1,
                    7
                )
            ]
            await db.executemany("""
                INSERT INTO courses (name, description, duration, price, technologies, is_active, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, default_courses)

        await db.commit()
    logger.info("SQLite ma'lumotlar bazasi va jadvallar muvaffaqiyatli ishga tushirildi.")
