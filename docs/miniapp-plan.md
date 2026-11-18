# ITLive Telegram Mini App

> Bu dastlabki dizayn tanlovining rejasi. Foydalanuvchi 4-variantni tanlaganidan keyin ishlaydigan Studio Neumorphism ilovasi `miniapp/app` va `webapp` ichida qurildi. Amaldagi qo‘llanma: [Railway deploy](railway-deploy.md), [tekshiruv hisoboti](studio-neumorphism-validation.md).

## Ish tartibi

1. Oltita vizual yo‘nalishni interaktiv maketda solishtirish.
2. Foydalanuvchi tanlagan yo‘nalishni yagona dizayn tizimiga aylantirish.
3. Bot bilan bir bazada ishlaydigan API va Telegram Mini Appni qurish.
4. Rollar, ruxsatlar, bot bildirishnomalari, eksport va mobil qurilmalarda tekshirish.
5. HTTPS manzilga joylash va Telegram menyusiga ulash.

Hozirgi `miniapp/design-preview` — birinchi bosqich. Barcha ma’lumotlar sun’iy; o‘zgarishlar faqat brauzer xotirasida. Rol almashtirgich faqat maketni ko‘rish uchun. Bu ishlab turgan botning avtorizatsiyasi emas.

## Mavjud funksiyalar va kelajakdagi qamrov

| Funksiya | Foydalanuvchi | Sotuvchi | Admin |
|---|---|---|---|
| Faol kurslar, tafsilot va narxlar | Ha | Ha | Ha |
| Kursga / bepul sinov darsiga ariza | O‘ziniki | O‘ziniki | O‘ziniki |
| Arizalar holatini ko‘rish | O‘ziniki | Barcha lidlar | Barcha lidlar |
| Ism, telefon, yosh, hudud, kurs, vaqt | Ariza formasi | Lid kartasi | Lid kartasi |
| Kasb tanlash testi, 5 savol | Ha | Ha | Ha |
| Manzil, xarita, kontakt, FAQ | Ha | Ha | Ha |
| Mentorlar, markaz haqida, aksiyalar | Ha | Ha | Ha |
| Fikr va taklif yuborish | Ha | Ha | Ha |
| Statistika, status va sotuvchi izohi | Yo‘q | Ha | Ha |
| Excel eksport | Yo‘q | Yo‘q | Ha |
| Kurs qo‘shish, tahrirlash, holat, o‘chirish | Yo‘q | Yo‘q | Ha |
| Sotuvchi qo‘shish / o‘chirish | Yo‘q | Yo‘q | Ha |
| Ommaviy matn, rasm, video xabarnomalar | Yo‘q | Yo‘q | Ha |
| Telefon, manzil, matn va havolalar sozlamasi | Yo‘q | Yo‘q | Ha |

## Arxitektura qarorlari

- Botning Python / aiogram / SQLite qismini saqlash; `database.models.Database` amallarini API servis qatlamida qayta ishlatish.
- Bot va API bir xil `DATABASE_PATH` orqali ishlaydi. Avval alohida test bazasida tekshiriladi.
- Telegram `initData` serverda HMAC bilan tekshiriladi; `auth_date` amal qilish muddati cheklanadi. Brauzer yuborgan rolga ishonilmaydi.
- Admin: `config.ADMINS`; sotuvchi: faol `sales_team` yozuvi; qolganlar foydalanuvchi. Har bir API amali serverda tekshiriladi. O‘z arizasiga kirish `user_id` bilan cheklanadi.
- Bot tokeni faqat serverda. `.env`, mijozlar va eksport fayllari frontendga kiritilmaydi.
- Yangi ariza, fikr va xabarnoma oqimlari bot orqali yuboriladi. API mutatsiyalariga validatsiya, chegaralar va takroriy yuborishga qarshi himoya qo‘shiladi.
- Mini app uchun HTTPS hosting va Telegram menyu tugmasi kerak bo‘ladi. Dizayn ko‘rgazmasining Sites manzili haqiqiy bot backendining o‘rnini bosmaydi.

Telegram protokoli uchun asosiy manba: [Mini Apps — initData validatsiyasi](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app).

## Dizayn manbalari

2026-11-17 kuni GitHub API orqali tekshirildi:

- [Anthropic Frontend Design](https://github.com/anthropics/skills/tree/main/skills/frontend-design): `anthropics/skills` — 196 362 yulduz. Bu son butun skill to‘plamiga tegishli.
- [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill): 150 643 yulduz.

Ikkalasi mahalliy Codex skill katalogiga `skill-installer` yordamchisi orqali o‘rnatildi va o‘qildi. Education qidiruvining tekis dizayn, mobil navigatsiya va teal palitrasi bo‘yicha tavsiyalari qo‘llanildi. Bolalar uchun shrift juftligi ushbu o‘quv markazi auditoriyasiga mos kelmadi; professional developer qidiruvi ham IDE mahsulotiga og‘di. Shuning uchun shrift va sahifa kompozitsiyalari quyidagi loyiha rejasidan olindi; avtomatik natija tayyor mahsulot dizayni sifatida qabul qilinmadi.

## Oltita variantning boshlang‘ich dizayn rejasi

| Variant | Ranglar | Shrift | Kompozitsiya | Asosiy xarakter |
|---|---|---|---|---|
| 1 Pulse | #2255F5, #EEF3FF, #172343, #FFFFFF, #65728A | Manrope | Yuqorida ko‘k kursga kirish bloki, pastda aniq vertikal kurs kartalari | Keng auditoriya uchun ravon, yorug‘ xizmat |
| 2 Midnight | #0B1520, #122330, #80E5CE, #EBF6F4, #A4B6C2 | Sora + IBM Plex Mono | Terminal motivi, ixcham ikki ustunli kurs panellari | IT muhitiga yaqin, to‘q va texnik |
| 3 Campus | #FFDE59, #20201E, #FFFDF4, #FFFFFF, #626258 | Outfit | Kuchli tipografika, qalin chiziqlar, plakatga o‘xshash kirish | Yoshlar uchun dadil va grafik |
| 4 Studio | #65509A, #EEE9F7, #28213F, #FFFFFF, #726780 | DM Sans + Fraunces | Serif sarlavha, assimetrik vizual va tahririy kurs ro‘yxati | Nafis, ijodiy va sokin |
| 5 Atlas | #17644B, #EEF5EF, #17382D, #FFFFFF, #62756A | Plus Jakarta Sans | Bosqichli o‘qish yo‘li, ixcham katalog va tartibli boshqaruv | Tushunarli, ishonchli, ishchan |
| 6 Orbit | #CB513A, #FFF0EA, #242E49, #FFFFFF, #786A6A | Outfit | Yonma-yon turli o‘lchamdagi bloklar, katta yumaloq aksent | Iliq, do‘stona, mobilga mos |

Birinchi reja tahlili: olti bir xil kartali sahifani faqat rang bilan farqlash yetarli emas. Shuning uchun har bir variantning bosh sahifa DOM tuzilishi, hero, kurs taqdimoti, radiusi va tipografik ierarxiyasi alohida qilindi. Admin va sotuvchi ekranlarida esa ma’lumotlarni solishtirish oson bo‘lishi uchun asosiy ish oqimlari bir xil saqlandi.
