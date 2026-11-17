import aiosqlite
from datetime import datetime
from typing import List, Optional, Dict, Any
from .db import get_db

class Database:
    """Barcha SQLite operatsiyalari uchun Repository klassi"""

    # ================= Foydalanuvchilar (Users) =================
    @staticmethod
    async def add_or_update_user(user_id: int, username: Optional[str], full_name: str, phone: Optional[str] = None):
        async with get_db() as db:
            await db.execute("""
                INSERT INTO users (user_id, username, full_name, phone, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name,
                    phone = COALESCE(excluded.phone, users.phone),
                    last_active = CURRENT_TIMESTAMP
            """, (user_id, username, full_name, phone))
            await db.commit()

    @staticmethod
    async def get_user_count() -> int:
        async with get_db() as db:
            cursor = await db.execute("SELECT COUNT(*) FROM users")
            row = await cursor.fetchone()
            return row[0] if row else 0

    @staticmethod
    async def get_all_users() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_user(user_id: int) -> Optional[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    # ================= Sotuvchilar (Sales Team) =================
    @staticmethod
    async def add_sales_rep(telegram_id: int, full_name: str, phone: Optional[str] = None) -> bool:
        try:
            async with get_db() as db:
                await db.execute("""
                    INSERT INTO sales_team (telegram_id, full_name, phone, is_active)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(telegram_id) DO UPDATE SET
                        full_name = excluded.full_name,
                        phone = excluded.phone,
                        is_active = 1
                """, (telegram_id, full_name, phone))
                await db.commit()
                return True
        except Exception:
            return False

    @staticmethod
    async def remove_sales_rep(telegram_id: int) -> bool:
        async with get_db() as db:
            await db.execute("DELETE FROM sales_team WHERE telegram_id = ?", (telegram_id,))
            await db.commit()
            return True

    @staticmethod
    async def get_active_sales_reps() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM sales_team WHERE is_active = 1")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_all_sales_reps() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM sales_team ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def is_sales_rep(telegram_id: int) -> bool:
        async with get_db() as db:
            cursor = await db.execute("SELECT id FROM sales_team WHERE telegram_id = ? AND is_active = 1", (telegram_id,))
            row = await cursor.fetchone()
            return row is not None

    # ================= Lidlar / Arizalar (Leads) =================
    @staticmethod
    async def create_lead(
        user_id: int,
        full_name: str,
        phone: str,
        age: int,
        region: str,
        course_name: str,
        time_preference: str
    ) -> int:
        async with get_db() as db:
            cursor = await db.execute("""
                INSERT INTO leads (user_id, full_name, phone, age, region, course_name, time_preference, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'YANGI')
            """, (user_id, full_name, phone, age, region, course_name, time_preference))
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def get_lead_by_id(lead_id: int) -> Optional[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def update_lead_status(lead_id: int, status: str, sales_id: Optional[int] = None) -> bool:
        async with get_db() as db:
            await db.execute("""
                UPDATE leads
                SET status = ?,
                    assigned_sales_id = COALESCE(?, assigned_sales_id),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, sales_id, lead_id))
            await db.commit()
            return True

    @staticmethod
    async def add_sales_note(lead_id: int, note: str, sales_id: Optional[int] = None) -> bool:
        async with get_db() as db:
            await db.execute("""
                UPDATE leads
                SET sales_notes = ?,
                    assigned_sales_id = COALESCE(?, assigned_sales_id),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (note, sales_id, lead_id))
            await db.commit()
            return True

    @staticmethod
    async def get_user_leads(user_id: int) -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM leads WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_leads_statistics() -> dict:
        async with get_db() as db:
            total_cursor = await db.execute("SELECT COUNT(*) FROM leads")
            total = (await total_cursor.fetchone())[0]

            today_cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE date(created_at) = date('now')")
            today = (await today_cursor.fetchone())[0]

            new_cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status = 'YANGI'")
            new_leads = (await new_cursor.fetchone())[0]

            contacted_cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status = 'BOGLANILDI'")
            contacted = (await contacted_cursor.fetchone())[0]

            enrolled_cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status = 'YOZILDI'")
            enrolled = (await enrolled_cursor.fetchone())[0]

            cancelled_cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status = 'BEKOR_QILINDI'")
            cancelled = (await cancelled_cursor.fetchone())[0]

            course_cursor = await db.execute("""
                SELECT course_name, COUNT(*) as cnt
                FROM leads
                WHERE course_name IS NOT NULL
                GROUP BY course_name
                ORDER BY cnt DESC
                LIMIT 5
            """)
            top_courses = [dict(r) for r in await course_cursor.fetchall()]

            return {
                "total": total,
                "today": today,
                "new": new_leads,
                "contacted": contacted,
                "enrolled": enrolled,
                "cancelled": cancelled,
                "top_courses": top_courses
            }

    @staticmethod
    async def get_all_leads_for_export() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("""
                SELECT
                    l.id, l.full_name, l.phone, l.age, l.region,
                    l.course_name, l.time_preference, l.status,
                    l.sales_notes, l.created_at, l.updated_at,
                    s.full_name as sales_person
                FROM leads l
                LEFT JOIN sales_team s ON l.assigned_sales_id = s.telegram_id
                ORDER BY l.id DESC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    # ================= Kurslar (Courses) =================
    @staticmethod
    async def get_active_courses() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM courses WHERE is_active = 1 ORDER BY sort_order ASC, id ASC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_all_courses() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM courses ORDER BY sort_order ASC, id ASC")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    async def get_course_by_id(course_id: int) -> Optional[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    async def add_course(name: str, description: str, duration: str, price: str, technologies: str = "") -> int:
        async with get_db() as db:
            cursor = await db.execute("""
                INSERT INTO courses (name, description, duration, price, technologies, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (name, description, duration, price, technologies))
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def update_course(course_id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        async with get_db() as db:
            set_clauses = [f"{k} = ?" for k in kwargs.keys()]
            values = list(kwargs.values()) + [course_id]
            sql = f"UPDATE courses SET {', '.join(set_clauses)} WHERE id = ?"
            await db.execute(sql, values)
            await db.commit()
            return True

    @staticmethod
    async def delete_course(course_id: int) -> bool:
        async with get_db() as db:
            await db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            await db.commit()
            return True

    @staticmethod
    async def toggle_course_status(course_id: int) -> bool:
        async with get_db() as db:
            await db.execute("UPDATE courses SET is_active = 1 - is_active WHERE id = ?", (course_id,))
            await db.commit()
            return True

    # ================= Sozlamalar (Bot Settings) =================
    @staticmethod
    async def get_setting(key: str, default: str = "") -> str:
        async with get_db() as db:
            cursor = await db.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
            row = await cursor.fetchone()
            return row[0] if row else default

    @staticmethod
    async def set_setting(key: str, value: str) -> bool:
        async with get_db() as db:
            await db.execute("""
                INSERT INTO bot_settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            await db.commit()
            return True

    @staticmethod
    async def get_all_settings() -> Dict[str, str]:
        async with get_db() as db:
            cursor = await db.execute("SELECT key, value FROM bot_settings")
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}

    # ================= Fikr-mulohazalar (Feedback) =================
    @staticmethod
    async def add_feedback(user_id: int, full_name: Optional[str], username: Optional[str], message: str) -> int:
        async with get_db() as db:
            cursor = await db.execute("""
                INSERT INTO feedback (user_id, full_name, username, message)
                VALUES (?, ?, ?, ?)
            """, (user_id, full_name, username, message))
            await db.commit()
            return cursor.lastrowid

    @staticmethod
    async def get_all_feedback() -> List[dict]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM feedback ORDER BY created_at DESC LIMIT 50")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
