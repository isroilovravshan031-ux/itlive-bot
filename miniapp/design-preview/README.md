# ITLive — oltita Mini App dizayn maketi

Bu bosqich — dizayn tanlash uchun interaktiv namuna. Haqiqiy Telegram autentifikatsiyasi, API yoki bot bazasiga ulanmagan. Role switch faqat ko‘rgazma uchun, ishlab turgan avtorizatsiya emas. Namuna ma’lumotlari xotirada ishlaydi; sahifa yangilanganda tiklanadi. Faqat dizayn tanlovi brauzerda saqlanadi.

## Ochish

Node.js bilan:

```powershell
node miniapp/design-preview/server.mjs
```

Manzil: http://127.0.0.1:4173

`dist` ichidagi fayllar oddiy statik hostingga ham mos. NPM paketlari va build kerak emas. Shriftlar lokal joylangan, tashqi font CDN kerak emas.

## Variantlar

1. Pulse — yorug‘ ko‘k, universal mobil interfeys.
2. Midnight — to‘q texnologik, terminal motivlari.
3. Campus — sariq grafik, katta tipografika.
4. Studio — nafis binafsha, serif sarlavhalar.
5. Atlas — yashil va tartibli, ta’lim yo‘li.
6. Orbit — korall va yumaloq, do‘stona bloklar.

Har bir variantda foydalanuvchi, sotuvchi va admin paneli bor. Keng ekran ko‘rinishini ham almashtirish mumkin.

## Sinash mumkin

- Kurslar, filtrlar, kurs tafsiloti va namuna ariza formasi.
- 5 savolli kasb tanlash testi va natija.
- O‘z arizalari, FAQ, mentorlar, kontakt va fikr formasi.
- Admin / sotuvchida lid qidirish, filtr, status va izohni yangilash.
- Admin statistikasi yangilanadi; namuna CSV eksport haqiqatan fayl beradi.
- Admin kurs qo‘shish, tahrirlash, yashirish va namunadan o‘chirish.
- Sotuvchilarni namunaga qo‘shish / olib tashlash.
- Ommaviy xabarning ko‘rinishini tayyorlash; xabar jo‘natilmaydi.
- Sozlamalar va fikrlar ekranlari — vizual namuna.

To‘liq ish rejasi: `docs/miniapp-plan.md`. Haqiqiy appda Excel `.xlsx`, Telegram orqali shaxsni tekshirish, serverdagi rol nazorati va botning barcha amallari qo‘shiladi.
