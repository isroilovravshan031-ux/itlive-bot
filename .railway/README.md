# Railway infrastructure

GitHub orqali odatiy deploy qilish uchun `docs/railway-deploy.md` yo‘riqnomasidan foydalaning. Ushbu papka CLI orqali boshqarishni xohlaganlar uchun qo‘shimcha yo‘l.

1. Railway’da **alohida ITLive loyihasini** tanlang. Mavjud boshqa servislarni ushbu fayl bilan boshqarmang; IaC’da resursni chiqarib tashlash uning o‘chirilishi deb talqin qilinishi mumkin.
2. `.railway` ichida `npm ci` va `npm run check`.
3. Repo ildizida `railway login` va `railway link`.
4. Servisdagi `BOT_TOKEN`, `ADMINS`, `APP_URL` qiymatlarini Railway Variables orqali kiriting. `preserve()` mavjud qiymatlarni saqlaydi; maxfiy qiymatlar faylga yozilmaydi.
5. `railway config plan` orqali rejalashtirilgan o‘zgarishlarni ko‘ring, keyin `railway config apply` orqali qo‘llang. Yangi servis yaratilsa, unda Variables va domenni sozlab deploy qiling.

Fayl Singapore regionida bitta servis va 1 GB volume tavsiflaydi. Yangi loyiha uchun mo‘ljallangan. Oldindan GUI orqali yaratilgan servislarni boshqarishga o‘tishda avval `railway config pull` bilan **o‘sha loyiha** konfiguratsiyasini import qilish kerak.

`.railway/railway.ts` deploy paytida avtomatik o‘qilmaydi; uni CLI `config plan/apply` boshqaradi. Kod deployi GitHub orqali Dockerfile bilan davom etadi.

Rasmiy manba: https://docs.railway.com/infrastructure-as-code
