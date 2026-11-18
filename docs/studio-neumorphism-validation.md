# Studio Neumorphism — tekshiruv hisoboti

2026-11-17. Haqiqiy lokal `.env` va mijozlar bazasi sinovlarda ishlatilmadi.

## Avtomatik tekshiruvlar

- `python -m pytest`: **37 test o‘tdi**. Kutubxonaning test transporti bo‘yicha bitta deprecation ogohlantirishi bor, production kodga taalluqli emas.
- `node --check`: frontend modullari sintaksisi to‘g‘ri.
- `python -m compileall`: API, bot, repository va helperlar sintaksisi to‘g‘ri.
- `pip check`: dependency konflikti topilmadi.
- `.railway` ichida `npm run check`: Railway **3.17.0** SDK bilan IaC TypeScript tekshiruvi o‘tdi.
- [GitHub Actions — Linux tekshiruvi](https://github.com/isroilovravshan031-ux/itlive-bot/actions/runs/44078976731): 37 ta test, frontend sintaksisi va IaC tekshiruvi o‘tdi. Production Docker image muvaffaqiyatli yig‘ildi; shu image ichida servis ishga tushirilib, `/healthz` HTTP 200 qaytargani tasdiqlandi. Tekshirilgan kod commit’i: `6430f44341ca645d1df90f9c6cbbaf7a4e51e737`.

Testlar Telegram HMAC imzosi, eskirgan/future auth sanasi, duplicate maydonlar, soxta admin roli, sessiyani bekor qilish, sotuvchi ruxsatining darhol bekor bo‘lishi, begona arizaga kira olmaslik, ichki izohlar maxfiyligi, input chegaralari, takroriy ariza, eskirgan tahrirga 409, kurslarni yashirish/CRUD, qidirish va sahifalash, sozlamalardagi kalit/havola allowlisti, kasb testi, Excel formula injection, fayl turi, xabarnoma tasdig‘i/idempotency/navbati/cancel va retry holatlarini qamraydi.

Excelni faqat tasdiqlangan adminning o‘z Telegramiga yuborish va Telegram contact’ida boshqa odamning raqamini o‘ziga yozib olmaslik ham tekshirildi. Telegram chaqiruvlari testlarda AsyncMock bilan bajarildi.

## Brauzer

- Studio ranglari va Fraunces / DM Sans bilan neumorphism bosh sahifasi ko‘rildi.
- Haqiqiy HTTP API va alohida sun’iy SQLite bazada sinov darsi arizasi yaratildi; “Arizalarim”da paydo bo‘ldi.
- 5 savolli kasb testi yakunlanib, Python Backend tavsiyasi olindi.
- Admin yangi ariza holatini “Bog‘lanildi”ga o‘zgartirdi va ichki izoh saqladi; “Yangi” ko‘rsatkichi 3 dan 2 ga tushdi.
- Admin API orqali namuna kurs qo‘shildi va keyin foydalanuvchilardan yashirildi.
- Excel brauzer orqali yuklab olindi va faylda 6 ta namuna ariza borligi openpyxl bilan tekshirildi.
- Forma label, klaviatura fokusi, native dialog / Escape va ko‘rinadigan validatsiya xabarlari ishlatildi.
- Mobil hamda keng ekran ko‘rinishlari rasmlarga saqlandi. Asosiy ranglar saqlangan; matn kontrasti uchun mavjud `#65509A` va `#28213F` ishlatiladi. `#65509A` / `#EEE9F7` kontrasti 5.57:1, oq / asosiy binafsha 6.63:1.
- Admin sahifasi 375, 768, 1024, 1440 va 812 piksel landshaft kengliklarida tekshirildi; gorizontal overflow topilmadi.

## Tekshirish chegaralari

Bu kompyuterda Docker CLI mavjud emas; Docker build va container ishga tushirish GitHub Actions’ning Linux muhitida bajarildi. Railway akkauntiga production deploy qilinmadi; domen, Variables va volume’ni akkaunt egasi sozlashi uchun `railway-deploy.md` tayyorlandi. Haqiqiy Telegram orqali xabar yuborish va native Android/iOS ichidagi qurilma sinovi bajarilmadi. Server protokoli, ruxsatlar va Telegram yuborish kodi izolyatsiyalangan testlar bilan tekshirildi.
