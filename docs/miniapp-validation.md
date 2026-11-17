# Dizayn maketlarini tekshirish

Sana: 2026-11-17. Ushbu tekshiruvlar dizayn prototipiga tegishli; haqiqiy botning server qismi yoki ishlab turgan bazasi ishga tushirilmadi.

- JavaScript sintaksisi: `node --check` — `dist/app.js` va `server.mjs` uchun o‘tdi.
- Lokal server HTML, JS, CSS va shriftlarni HTTP 200 bilan qaytardi.
- 7 ta shrift oilasining fayllari va litsenziyalari mavjudligi tekshirildi.
- Brauzerda olti variantning foydalanuvchi sahifalari 375 × 812 o‘lchamda ochildi, kontentda gorizontal overflow topilmadi.
- Olti variantning admin va sotuvchi sahifalari ham shu o‘lchamda tekshirildi: 12 ko‘rinishda overflow topilmadi; admin navigatsiyasida 5, sotuvchida 3 bo‘lim bor.
- Kurs tafsilotidan ariza formasi ochildi. `123` telefon raqami rad etildi; namuna telefon, ism va yosh bilan ariza yaratildi, “Arizalarim” bo‘limida ko‘rindi.
- Shu arizaning holati admin orqali “O‘qishga yozildi”ga o‘zgartirildi va izoh saqlandi. Statistika 6 jami / 2 yangi / 1 bog‘lanilgan / 2 yozilgan bo‘lib yangilandi.
- Yangi namuna kurs qo‘shildi va katalogda ko‘rindi.
- 5 savolli kasb testi yakunlandi va javoblarga mos Python Backend tavsiyasi chiqdi.
- Namuna CSV brauzer orqali yuklandi; ustun nomlari va sun’iy lidlar faylda tekshirildi.
- Atlas admin paneli 1440 × 1100 o‘lchamdagi keng rejimda tekshirildi, gorizontal overflow topilmadi.
- Galereya 375, 768, 1024 va 812 piksel (landshaft) kengliklarda tekshirildi; 6 variant saqlandi va gorizontal overflow kuzatilmadi.
- Modal oynalarda native dialog, Escape, yopish tugmasi va klaviatura fokusi bor; animatsiyalar reduced motion sozlamasini hurmat qiladi.

Rasmlar: `miniapp-designs.jpg`, `miniapp-admin-desktop.jpg` va har bir variant uchun `miniapp-*.jpg`.

Chegaralar: haqiqiy Telegram ichida qurilma sinovi, Telegram initData validatsiyasi, serverdagi rol nazorati, API, Excel `.xlsx` va haqiqiy botga xabar yuborish dizayn tanlovidan keyingi bosqichga tegishli.
