# ITLive bot va Mini Appni Railway’ga joylash

Python 3.12, FastAPI, aiogram va SQLite bitta servisda ishlaydi. Frontend ham shu servisdan ochiladi. Repo ildizidagi `Dockerfile` buildni bajaradi, `python run.py` API va botni birgalikda ishga tushiradi.

## 1. GitHub servis yarating

Railway’da **New Project → Deploy from GitHub repo** orqali `isroilovravshan031-ux/itlive-bot` reposining `main` branchini tanlang. Root directory — repo ildizi `/`. `miniapp/app` ichini alohida servis sifatida tanlamang.

Railway `Dockerfile`ni aniqlaydi. Build command yozish shart emas. Start command: `python run.py` (Dockerfile ichida ham bor).

## 2. Bazaga doimiy volume ulang

Servisga **Volume** qo‘shing va mount pathni `/data` qiling. Baza `/data/itlive_bot.db`, yuklangan media `/data/uploads` ichida saqlanadi. [Railway Volumes hujjati](https://docs.railway.com/volumes).

## 3. Domen va Variables

Servisning **Networking → Generate Domain** orqali HTTPS domen yarating. Variables bo‘limiga quyidagilarni kiriting:

| Nomi | Qiymati |
|---|---|
| `BOT_TOKEN` | BotFather bergan haqiqiy token |
| `ADMINS` | Admin Telegram ID’lari, vergul bilan: `123456789,987654321` |
| `APP_URL` | Yaratingan domen: `https://YOUR-SERVICE.up.railway.app` |
| `DATABASE_PATH` | `/data/itlive_bot.db` |
| `UPLOAD_DIR` | `/data/uploads` |
| `RUN_BOT` | `true` |

`BOT_USERNAME` ixtiyoriy: startupda Telegram `getMe` orqali aniqlanadi. `PORT` Railway tomonidan beriladi va `run.py` uni o‘qiydi. [Railway healthcheck va port hujjati](https://docs.railway.com/deployments/healthchecks).

Mahalliy `.env` GitHub’ga yuklanmagan. Undagi kerakli qiymatlarni Railway Variables’ga kiriting. Tokenni frontend yoki `.railway/railway.ts` ichiga yozmang.

## 4. Servis sozlamalari

- Healthcheck path: `/healthz`.
- Healthcheck timeout: `120` soniya.
- Replicas: **1**. Bitta regionda ishlating.
- Restart policy: `On Failure`, 5 ta qayta urinish.
- Serverless / App Sleeping: o‘chiq. Bot doimiy polling orqali ishlaydi.

`uvicorn` ichida bitta worker belgilangan. Alohida bot worker servisi yaratilmaydi. Shu token bilan ishlayotgan kompyuterdagi yoki boshqa hostingdagi eski polling botni Railway’ni ishga tushirishdan oldin to‘xtating. [aiogram long polling](https://docs.aiogram.dev/en/latest/dispatcher/long_polling.html).

## 5. Deploy va Telegram’da ochish

Variables va volume sozlangach deploy qiling. Startup mavjud bazani o‘chirmasdan yangi jadvallarni qo‘shadi; bo‘sh baza bo‘lsa standart kurslar va sozlamalar yaratiladi.

Startup botning **Mini app** menyu tugmasini `APP_URL` manziliga o‘rnatadi. Botni `/start` orqali qayta oching. Reply menyusida ham **📱 Mini app** tugmasi chiqadi.

- `ADMINS` ichidagi ID — admin kabineti.
- Admin qo‘shgan faol sotuvchi — sotuvchi kabineti.
- Qolganlar — foydalanuvchi kabineti.

Admin va sotuvchi “O‘quvchi ko‘rinishi” orqali oddiy foydalanuvchi amallarini ham bajaradi. Rolni o‘zgartiradigan ochiq URL yoki demo login endpoint yo‘q.

Oddiy brauzerda manzilni ochish Telegram orqali kirish sahifasini ko‘rsatadi. Shaxs [Telegram initData imzosi](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app) orqali serverda tekshiriladi.

## Mavjud mahalliy bazani ko‘chirish

Yangi, bo‘sh bazadan boshlamoqchi bo‘lsangiz bu qadam shart emas. Eski lidlar, kurslar va sotuvchilarni saqlash uchun:

1. Mahalliy botni to‘xtating.
2. Repo ildizida izchil snapshot yarating:

   ```powershell
   .\.venv\Scripts\python scripts/backup_db.py data/itlive_bot.db data/itlive-railway-backup.db
   ```

   Agar `.env` ichidagi `DATABASE_PATH` boshqa bo‘lsa, birinchi yo‘lni o‘shanga almashtiring. Skript mavjud destination faylini bosib yozmaydi; keyingi snapshot uchun yangi nom bering. Faol WAL yozuvlari ham snapshotga kiradi.

3. Railway CLI orqali login va project/service bog‘lanishini tanlang:

   ```powershell
   railway login
   railway link
   ```

4. **Birinchi ishga tushirishdan oldin yangi/bo‘sh volume** ichiga snapshotni yuklang:

   ```powershell
   railway volume files upload ./data/itlive-railway-backup.db /itlive_bot.db
   ```

   Volume ichidagi `/itlive_bot.db` servisda `/data/itlive_bot.db` sifatida ko‘rinadi. Fayl tanlangan ITLive volume’ga tushayotganini tekshiring. Allaqachon ishlab turgan Railway bazasi ustidan yuklamang; mavjud server ma’lumotlarini tiklashdan oldin uning ham snapshotini saqlash kerak. [Rasmiy volume fayl buyruqlari](https://docs.railway.com/cli/volume).

5. Servisni ishga tushiring. Migratsiyalar eski ma’lumotlar ustiga faqat kerakli jadvallar va ustunlarni qo‘shadi.

## Qayta deploy va xabarnomalar

Arizalar va fikrlar Telegramga yuborish navbati bilan bitta tranzaksiyada saqlanadi. Vaqtinchalik xatolar qayta sinab ko‘riladi. Ommaviy xabarnoma qabul qiluvchilari va natijalari ham bazada saqlanadi.

Servis Telegramga so‘rov yuborayotgan aniq paytda o‘chsa, Telegram o‘sha xabarni olganini tekshirishning idempotent usuli yo‘q. Ommaviy xabarda bunday qabul qiluvchi takror yuborilmasligi uchun `failed / InterruptedDelivery` sifatida belgilanadi. Oddiy bildirishnomalarda kamdan-kam takroriy xabar bo‘lishi mumkin.

Volume bilan deploylarda qisqa uzilish bo‘lishi mumkin. Railway’da volume backupini yoqish tavsiya etiladi. [Railway volume backup](https://docs.railway.com/volumes#backups).

## CLI orqali IaC — qo‘shimcha yo‘l

`.railway/railway.ts` va shu papkadagi `README.md` bitta servis, bitta replica va doimiy volume’ni tavsiflaydi. Bu yo‘lni tanlasangiz o‘sha yo‘riqnomani bajaring; yuqoridagi GUI usuli uchun qo‘shimcha Node paketlari kerak emas.

2026-11-17 holatidagi Railway hujjatiga ko‘ra yangi servislar eski `railway.json` / `railway.toml` konfiguratsiyasiga o‘ta olmaydi; uning o‘rniga IaC ishlatiladi. Shu sabab repo eskirayotgan konfiguratsiyaga tayanmaydi. [Railway IaC hujjati](https://docs.railway.com/infrastructure-as-code#iac-vs-config-as-code).

## Muammolarni tekshirish

| Holat | Tekshiring |
|---|---|
| Deploy boshlanishda yiqildi | `BOT_TOKEN`, HTTPS `APP_URL`, volume yozish ruxsati va servis loglari |
| “TelegramConflictError” | Shu tokenli eski polling jarayoni va boshqa replica ishlamayotganini |
| Admin paneli ochilmadi | `ADMINS` ichida username emas, raqamli Telegram ID borligini |
| Qayta deploydan keyin baza bo‘sh | `/data` volume ulangani va `DATABASE_PATH` shu volume ichida ekanini |
| Xabar yetib bormadi | Foydalanuvchi / sotuvchi botni `/start` qilgani va uni bloklamaganini |
| “Sessiya yaroqsiz yoki eskirgan” | Mini appni Telegram menyusidan qayta oching |
| Healthcheck javob bermadi | Portni `run.py` boshqarayotganini va path `/healthz` ekanini |
