import { api, setToken, ApiError } from "./api.js";
import { icon, esc } from "./icons.js";

const root = document.querySelector("#root");
const modal = document.querySelector("#modal");
const tg = window.Telegram?.WebApp;
const state = {
  boot: null,
  view: "learn",
  page: "home",
  data: null,
  filter: "",
  query: "",
  offset: 0,
  category: "Barchasi",
  quizAnswers: [],
  busy: false,
};
const statusLabels = {
  YANGI: "Yangi",
  BOGLANILDI: "Bog‘lanildi",
  YOZILDI: "O‘qishga yozildi",
  BEKOR_QILINDI: "Bekor qilindi",
};
const regions = [
  "Toshkent shahri",
  "Toshkent viloyati",
  "Samarqand",
  "Farg‘ona",
  "Andijon",
  "Namangan",
  "Buxoro",
  "Qashqadaryo",
  "Surxondaryo",
  "Xorazm",
  "Navoiy",
  "Jizzax",
  "Sirdaryo",
  "Qoraqalpog‘iston",
  "Boshqa hudud",
];
const times = ["Ertalab", "Tushdan keyin", "Kechki", "Farqi yo‘q"];
const settingsLabels = {
  center_name: "Markaz nomi",
  phone_1: "Asosiy telefon",
  phone_2: "Qo‘shimcha telefon",
  address: "Manzil",
  landmark: "Mo‘ljal",
  latitude: "Kenglik (latitude)",
  longitude: "Uzunlik (longitude)",
  working_hours: "Ish vaqti",
  instagram: "Instagram",
  telegram: "Telegram",
  website: "Veb-sayt",
  youtube: "YouTube",
  about_text: "Markaz haqida",
  discounts_text: "Chegirma va aksiyalar",
};
const plain = (text) =>
  String(text || "")
    .replace(/<[^>]*>/g, "")
    .replace(
      /&(amp|lt|gt|quot|apos|#39);/gi,
      (_, key) =>
        ({ amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", "#39": "'" })[
          key.toLowerCase()
        ],
    );
const cleanTitle = (text) => String(text || "").replace(/^[^\p{L}\p{N}]+/u, "");
const initials = (text) =>
  String(text || "")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((x) => x[0])
    .join("")
    .toUpperCase();
const fmt = (n) => new Intl.NumberFormat("uz-UZ").format(n || 0);
const safeUrl = (value) => {
  try {
    const u = new URL(value);
    return u.protocol === "https:" ? u.href : "#";
  } catch {
    return "#";
  }
};
const date = (value) => {
  if (!value) return "";
  const d = new Date(
    value.includes("T") ? value : value.replace(" ", "T") + "Z",
  );
  if (isNaN(d)) return "";
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Tashkent",
    })
      .formatToParts(d)
      .map((part) => [part.type, part.value]),
  );
  const months = [
    "yanvar",
    "fevral",
    "mart",
    "aprel",
    "may",
    "iyun",
    "iyul",
    "avgust",
    "sentabr",
    "oktabr",
    "noyabr",
    "dekabr",
  ];
  return `${parts.day} ${months[Number(parts.month) - 1]}, ${parts.hour}:${parts.minute}`;
};
let pageSequence = 0,
  toastTimeout,
  pendingDraft = null,
  objectUrl = null,
  searchTimeout;
const canWork = () => Boolean(state.boot && state.boot.user.role !== "user");
const isAdmin = () => state.boot?.user.role === "admin";
const activeCourses = () =>
  (state.boot?.courses || []).filter((c) => c.is_active);
function toast(text) {
  const el = document.querySelector("#toast");
  el.textContent = text;
  el.classList.add("visible");
  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => el.classList.remove("visible"), 4500);
}
function statusBadge(status) {
  return `<span class="badge status-${status.toLowerCase()}">${icon(status === "YOZILDI" ? "check" : status === "BOGLANILDI" ? "phone" : status === "BEKOR_QILINDI" ? "close" : "clock")}${esc(statusLabels[status] || status)}</span>`;
}
function button(label, action, ico = "arrow", cls = "primary") {
  return `<button class="button ${cls}" data-action="${action}">${icon(ico)}<span>${label}</span></button>`;
}
function field(
  label,
  name,
  value = "",
  { type = "text", required = true, max = 200, extra = "" } = {},
) {
  return `<div class="field"><label for="field-${name}">${label}</label><input id="field-${name}" name="${name}" type="${type}" value="${esc(value)}" ${required ? "required" : ""} maxlength="${max}" aria-describedby="error-${name}" ${extra}><small id="error-${name}" class="field-error" data-error="${name}"></small></div>`;
}
function selectField(label, name, options, value) {
  return `<div class="field"><label for="field-${name}">${label}</label><select id="field-${name}" name="${name}" required aria-describedby="error-${name}">${options
    .map((o) => {
      const [v, t] = Array.isArray(o) ? o : [o, o];
      return `<option value="${esc(v)}" ${String(v) === String(value) ? "selected" : ""}>${esc(t)}</option>`;
    })
    .join(
      "",
    )}</select><small id="error-${name}" class="field-error" data-error="${name}"></small></div>`;
}
function textField(
  label,
  name,
  value = "",
  rows = 4,
  max = 3000,
  required = true,
) {
  return `<div class="field"><label for="field-${name}">${label}</label><textarea id="field-${name}" name="${name}" rows="${rows}" ${required ? "required" : ""} maxlength="${max}" aria-describedby="error-${name}">${esc(value)}</textarea><small id="error-${name}" class="field-error" data-error="${name}"></small></div>`;
}
const formError =
  '<div class="form-error" role="alert" tabindex="-1" hidden></div>';
const submitButton = (label) =>
  `<button type="submit" class="button primary full">${icon("check")}<span>${label}</span></button>`;
function showModal(title, html, wide = false) {
  modal.className = wide ? "wide" : "";
  modal.innerHTML = `<div class="modal-head"><h2 id="modal-title">${esc(title)}</h2><button class="icon-button" data-action="close-modal" aria-label="Oynani yopish">${icon("close")}</button></div><div class="modal-body">${html}</div>`;
  if (!modal.open) modal.showModal();
  modal.querySelector(".icon-button").focus();
}
function closeModal() {
  modal.close();
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
    objectUrl = null;
  }
}
function showError(error, form = null) {
  const message = error.message || "Amal bajarilmadi. Qayta urinib ko‘ring.";
  if (error.status === 401) {
    closeModal();
    return showGate(
      "Sessiya tugadi. Mini appni Telegram ichidan qayta oching.",
    );
  }
  if (form) {
    const el = form.querySelector(".form-error");
    el.hidden = false;
    el.textContent = message;
    el.focus();
    form.querySelectorAll(".field-error").forEach((e) => (e.textContent = ""));
    form
      .querySelectorAll("[aria-invalid]")
      .forEach((e) => e.removeAttribute("aria-invalid"));
    for (const item of error.errors || []) {
      const label = form.querySelector(
        `[data-error="${CSS.escape(item.field)}"]`,
      );
      if (label) label.textContent = item.message;
      form.elements.namedItem(item.field)?.setAttribute("aria-invalid", "true");
    }
    return;
  }
  toast(message);
}

async function boot() {
  try {
    tg?.ready();
    tg?.expand();
    try {
      tg?.setHeaderColor("#eee9f7");
      tg?.setBackgroundColor("#eee9f7");
      tg?.setBottomBarColor?.("#eee9f7");
    } catch {}
    let initData =
      tg?.initData ||
      new URLSearchParams(location.hash.slice(1)).get("tgWebAppData");
    if (!initData) return showGate();
    const login = await api("/auth/telegram", {
      method: "POST",
      body: { init_data: initData },
    });
    setToken(login.token);
    state.boot = await api("/bootstrap");
    const route = new URLSearchParams(location.search);
    state.view = canWork() && route.get("view") !== "learn" ? "work" : "learn";
    const allowed =
      state.view === "learn"
        ? ["home", "courses", "applications", "more"]
        : isAdmin()
          ? [
              "home",
              "leads",
              "courses",
              "team",
              "more",
              "settings",
              "broadcasts",
              "feedbacks",
            ]
          : ["home", "leads", "more"];
    state.page = allowed.includes(route.get("page"))
      ? route.get("page")
      : "home";
    history.replaceState(
      { view: state.view, page: state.page },
      "",
      `${location.pathname}?page=${state.page}&view=${state.view}`,
    );
    tg?.BackButton?.onClick(() => {
      if (modal.open) closeModal();
      else history.back();
    });
    renderShell();
    await loadPage();
  } catch (error) {
    showGate(error.message);
  }
}
async function showGate(
  message = "Kurslar va kabinetingizga kirish uchun mini appni Telegram ichidan oching.",
) {
  state.boot = null;
  setToken("");
  const config = await api("/config").catch(() => ({}));
  const username = /^[A-Za-z0-9_]{5,32}$/.test(config.bot_username || "")
    ? config.bot_username
    : "";
  root.innerHTML = `<main class="gate" id="page"><div class="gate-mark neu">${icon("code")}</div><span class="brand large">itlive.</span><h1>O‘rganish uchun<br>yangi makon.</h1><p>${esc(message)}</p>${username ? `<a class="button primary" href="https://t.me/${username}" target="_blank" rel="noopener">${icon("send")}<span>Telegramda ochish</span></a>` : '<p class="quiet">Botdagi “Mini app” tugmasini bosing.</p>'}<button class="button subtle" data-action="reload">${icon("arrow")} Qayta urinish</button><div class="gate-ring" aria-hidden="true"></div></main>`;
}
function navigation() {
  if (state.view === "learn")
    return [
      ["home", "home", "Asosiy"],
      ["courses", "book", "Kurslar"],
      ["applications", "files", "Arizalarim"],
      ["more", "grid", "Yana"],
    ];
  return isAdmin()
    ? [
        ["home", "chart", "Umumiy"],
        ["leads", "files", "Lidlar"],
        ["courses", "book", "Kurslar"],
        ["team", "users", "Jamoa"],
        ["more", "grid", "Yana"],
      ]
    : [
        ["home", "chart", "Umumiy"],
        ["leads", "files", "Lidlar"],
        ["more", "user", "Profil"],
      ];
}
function renderShell() {
  const user = state.boot.user;
  const nav = navigation();
  root.innerHTML = `<div class="app-shell"><aside class="sidebar"><a class="logo" href="#" data-page="home">${icon("code")}<span class="brand">itlive.<small>academy</small></span></a><div class="sidebar-label">${state.view === "learn" ? "Sizning ta’lim makoningiz" : isAdmin() ? "Boshqaruv markazi" : "Sotuvlar markazi"}</div><nav class="desktop-nav" aria-label="Asosiy navigatsiya">${navMarkup(nav)}</nav><div class="sidebar-bottom"><div class="small-seal">${icon("spark")}</div><p>Bilimdan<br>imkoniyat sari.</p>${canWork() ? `<button class="view-switch" data-action="switch-view">${icon(state.view === "work" ? "book" : "shield")}<span>${state.view === "work" ? "O‘quvchi ko‘rinishi" : "Ish kabineti"}</span></button>` : ""}</div></aside><div class="main-column"><header class="topbar"><a class="mobile-logo logo" href="#" data-page="home">${icon("code")}<span class="brand">itlive.</span></a><div class="topbar-context"><span>${esc(state.boot.settings.center_name)}</span><small>${state.view === "learn" ? "Shaxsiy kabinet" : isAdmin() ? "Admin kabineti" : "Sotuvchi kabineti"}</small></div><div class="topbar-actions">${canWork() ? `<button class="icon-button view-button" data-action="switch-view" aria-label="${state.view === "work" ? "O‘quvchi ko‘rinishiga o‘tish" : "Ish kabinetiga o‘tish"}">${icon(state.view === "work" ? "book" : "shield")}</button>` : ""}<button class="icon-button" data-action="refresh" aria-label="Ma’lumotlarni yangilash">${icon("clock")}</button><button class="avatar neu" data-action="profile" aria-label="Profilni ko‘rish">${esc(initials(user.full_name))}</button></div></header><main id="page" class="page" tabindex="-1"></main><footer class="app-footer">ITLive Academy <span>O‘rganishdan yarating.</span></footer></div><nav class="bottom-nav" aria-label="Mobil navigatsiya">${navMarkup(nav)}</nav></div>`;
  updateNav();
}
function navMarkup(items) {
  return items
    .map(
      ([p, i, t]) =>
        `<button data-page="${p}" class="nav-item ${state.page === p ? "active" : ""}" ${state.page === p ? 'aria-current="page"' : ""}>${icon(i)}<span>${t}</span></button>`,
    )
    .join("");
}
function updateNav() {
  document.querySelectorAll(".nav-item").forEach((b) => {
    const current =
      b.dataset.page === state.page ||
      ((state.page === "settings" ||
        state.page === "broadcasts" ||
        state.page === "feedbacks") &&
        b.dataset.page === "more");
    b.classList.toggle("active", current);
    if (current) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
  if (state.page !== "home") tg?.BackButton?.show();
  else tg?.BackButton?.hide();
}
async function navigate(page, { replace = false } = {}) {
  state.page = page;
  state.offset = 0;
  state.query = "";
  state.filter = "";
  state.category = "Barchasi";
  if (!replace)
    history.pushState(
      { page, view: state.view },
      "",
      location.pathname + "?page=" + page + "&view=" + state.view,
    );
  updateNav();
  await loadPage();
  window.scrollTo({ top: 0, behavior: "instant" });
  document.querySelector("#page")?.focus({ preventScroll: true });
}
async function loadPage() {
  const sequence = ++pageSequence;
  const container = document.querySelector("#page");
  if (!container) return;
  container.innerHTML =
    '<div class="page-loading" role="status"><span class="spinner"></span>Yuklanmoqda…</div>';
  try {
    let data = null;
    if (state.page === "home" && state.view === "work") {
      const [stats, recent] = await Promise.all([
        api("/staff/statistics"),
        api("/staff/leads?limit=5"),
      ]);
      data = { stats, recent };
    } else if (state.page === "leads" && state.view === "work")
      data = await api(
        "/staff/leads?" +
          new URLSearchParams({
            q: state.query,
            status: state.filter,
            offset: state.offset,
            limit: 30,
          })
            .toString()
            .replace("status=&", ""),
      );
    else if (state.page === "applications")
      data = await api("/my/applications");
    else if (state.page === "team" && isAdmin())
      data = await api("/admin/sales");
    else if (state.page === "feedbacks" && isAdmin())
      data = await api("/admin/feedback?offset=" + state.offset);
    else if (state.page === "broadcasts" && isAdmin()) {
      const [jobs, stats] = await Promise.all([
        api("/admin/broadcasts"),
        api("/staff/statistics"),
      ]);
      data = { jobs: jobs.items, stats };
    }
    if (sequence !== pageSequence) return;
    state.data = data;
    container.innerHTML = pageHTML();
    updateNav();
  } catch (error) {
    if (sequence !== pageSequence) return;
    container.innerHTML = `<section class="empty neu">${icon("help")}<h1>Ma’lumotlar yuklanmadi</h1><p>${esc(error.message)}</p>${button("Qayta urinish", "refresh", "arrow")}</section>`;
    if (error.status === 401) showError(error);
  }
}
async function refreshBoot() {
  state.boot = await api("/bootstrap");
  if (!canWork()) state.view = "learn";
}
async function refreshAll() {
  await refreshBoot();
  renderShell();
  await loadPage();
}
function pageHeading(kicker, title, description = "", action = "") {
  return `<div class="page-heading"><div><p class="kicker">${kicker}</p><h1>${title}</h1>${description ? `<p class="heading-description">${description}</p>` : ""}</div>${action}</div>`;
}
function empty(title, description, action = "") {
  return `<section class="empty neu">${icon("book")}<h2>${title}</h2><p>${description}</p>${action}</section>`;
}
function section(title, action = "") {
  return `<div class="section-heading"><h2>${title}</h2>${action}</div>`;
}
function courseType(c) {
  const n = c.name.toLowerCase();
  if (n.includes("dizayn")) return ["palette", "Dizayn"];
  if (n.includes("flutter")) return ["mobile", "Dasturlash"];
  if (n.includes("kiber")) return ["shield", "Xavfsizlik"];
  if (n.includes("foundation")) return ["laptop", "Boshlang‘ich"];
  if (n.includes("smm")) return ["chart", "Marketing"];
  return [n.includes("frontend") ? "globe" : "code", "Dasturlash"];
}
function courseCard(c, admin = false) {
  const [ico, category] = courseType(c);
  return `<article class="course-card neu"><button class="course-open" data-course="${c.id}"><span class="course-card-top"><span class="course-symbol neu-inset">${icon(ico)}</span><span class="course-duration">${icon("clock")}${esc(c.duration)}</span></span><span class="course-category">${category}</span><h3>${esc(cleanTitle(c.name))}</h3><p>${esc(c.description)}</p><span class="course-tech">${esc(c.technologies)}</span><span class="course-card-bottom"><strong>${esc(c.price)}</strong><span class="course-arrow">${icon("arrow")}</span></span></button>${admin ? `<div class="course-admin"><span class="badge ${c.is_active ? "status-yozildi" : "status-bekor_qilindi"}">${c.is_active ? "Faol" : "Yashirilgan"}</span><button data-edit-course="${c.id}" class="text-button">Tahrirlash</button><button data-toggle-course="${c.id}" class="text-button">${c.is_active ? "Yashirish" : "Faollashtirish"}</button></div>` : ""}</article>`;
}
function pageHTML() {
  if (state.page === "home")
    return state.view === "learn" ? home() : dashboard();
  if (state.page === "courses") return coursesPage();
  if (state.page === "applications") return applicationsPage();
  if (state.page === "leads" && canWork()) return leadsPage();
  if (state.page === "team" && isAdmin()) return teamPage();
  if (state.page === "settings" && isAdmin()) return settingsPage();
  if (state.page === "feedbacks" && isAdmin()) return feedbacksPage();
  if (state.page === "broadcasts" && isAdmin()) return broadcastsPage();
  return morePage();
}
function home() {
  const name = state.boot.user.full_name.split(" ")[0];
  return `<div class="home-intro"><p>Salom, ${esc(name)}.</p><span>${icon("spark")} O‘zingizga yangi imkoniyat yarating</span></div><section class="studio-hero neu"><div class="hero-text"><span class="hero-tag">ITLive Academy bilan</span><h1>Kelajagingizni<br>loyihalang.</h1><p>Qiziqishingizni yangi kasbga aylantiring.<br>Birinchi qadamingizni birga boshlaymiz.</p><button class="button primary" data-page="courses"><span>Yo‘nalishimni tanlayman</span>${icon("arrow")}</button></div><div class="hero-sculpture" aria-hidden="true"><div class="sculpture-disc"></div><div class="sculpture-ring"></div><span class="sculpture-star neu">${icon("spark")}</span><p>O‘rganing.<br>Yarating.</p></div></section><div class="quick-actions">${[
    ["trial", "gift", "Bepul sinov darsi", "Avval ta’lim bilan tanishing"],
    ["quiz", "spark", "Kasbingizni toping", "5 savolda mos yo‘nalish"],
    ["contacts", "pin", "Bizga tashrif buyuring", "Manzil va bog‘lanish"],
  ]
    .map(
      ([a, i, t, d]) =>
        `<button class="quick-card neu" data-action="${a}"><span class="quick-symbol neu-inset">${icon(i)}</span><span><strong>${t}</strong><small>${d}</small></span>${icon("arrow")}</button>`,
    )
    .join(
      "",
    )}</div>${section("Yangi kasbingiz shu yerda", `<button class="text-button" data-page="courses">Barcha kurslar ${icon("arrow")}</button>`)}<div class="courses-grid">${
    activeCourses()
      .slice(0, 4)
      .map((c) => courseCard(c))
      .join("") ||
    empty(
      "Hozircha kurslar yo‘q",
      "Yangi yo‘nalishlar haqida bilish uchun biz bilan bog‘laning.",
      button("Bog‘lanish", "contacts", "phone"),
    )
  }</div><section class="gentle-banner neu-inset"><span class="small-seal">${icon("heart")}</span><div><h2>Qiziqishdan ishonchli qadamgacha.</h2><p>Tajribali mentorlar bilan amaliy bilim oling.</p></div><button class="text-button" data-action="about">ITLive haqida ${icon("arrow")}</button></section>`;
}
function coursesPage() {
  const admin = state.view === "work" && isAdmin();
  const list = admin ? state.boot.courses : activeCourses();
  const visible = list.filter(
    (c) => state.category === "Barchasi" || courseType(c)[1] === state.category,
  );
  return `${pageHeading(admin ? "Ta’lim yo‘nalishlari" : "Yangi ko‘nikma, yangi imkoniyat", admin ? "Kurslar boshqaruvi" : "O‘zingizga mosini toping.", admin ? "Katalog va kurslar holatini boshqaring." : "Dasturlashdan dizayngacha — qiziqishingizdan boshlang.", admin ? button("Kurs qo‘shish", "add-course", "plus") : button("Bepul sinov darsi", "trial", "gift", "secondary"))}<div class="filter-tabs" role="group" aria-label="Kurs yo‘nalishi">${["Barchasi", ...new Set(list.map((c) => courseType(c)[1]))].map((x) => `<button class="filter-tab ${state.category === x ? "active" : ""}" aria-pressed="${state.category === x}" data-category="${x}">${x}</button>`).join("")}</div><div class="list-description">${visible.length} ta yo‘nalish</div><div class="courses-grid">${visible.map((c) => courseCard(c, admin)).join("") || empty("Kurslar topilmadi", "Boshqa yo‘nalishni tanlang.")}</div>`;
}
function applicationsPage() {
  const items = state.data.items;
  return `${pageHeading("O‘qish sari bir qadam", "Mening arizalarim", "Arizalaringiz va ularning hozirgi holati.", `<button class="button secondary" data-page="courses">${icon("plus")} Yangi ariza</button>`)}<div class="applications-grid">${items.map((l) => `<article class="application-card neu"><div class="application-top"><span>#${l.id} ${l.kind === "trial" ? "· Sinov darsi" : ""}</span>${statusBadge(l.status)}</div><h2>${esc(cleanTitle(l.course_name))}</h2><dl><div><dt>Qulay vaqt</dt><dd>${esc(l.time_preference)}</dd></div><div><dt>Ariza sanasi</dt><dd>${date(l.created_at)}</dd></div></dl><div class="application-track"><span class="complete">${icon("check")} Ariza qabul qilindi</span><span class="${l.status === "BOGLANILDI" || l.status === "YOZILDI" ? "complete" : ""}">${icon("phone")} Bog‘lanish</span></div><button class="button subtle full" data-action="contacts">${icon("phone")} Savolim bor</button></article>`).join("") || empty("Birinchi qadamingiz hali oldinda.", "Kurs tanlang va arizangizni bir necha daqiqada qoldiring.", `<button class="button primary" data-page="courses">${icon("book")} Kurslarni ko‘rish</button>`)}</div>`;
}
function dashboard() {
  const { stats: s, recent } = state.data;
  return `${pageHeading(isAdmin() ? "Boshqaruv markazi" : "Sotuvchi kabineti", isAdmin() ? "Hammasi nazoratda." : "Har bir lid — imkoniyat.", "Bugungi natijalar va keyingi qadamlar.", `<span class="date-chip neu-inset">${icon("clock")}${date(new Date().toISOString()).split(",")[0]}</span>`)}<div class="stats-grid">${[
    ["Jami arizalar", s.total, "files", "Barcha murojaatlar"],
    ["Bugun", s.today, "spark", "Bugun kelgan arizalar"],
    ["Yangi", s.statuses.YANGI || 0, "clock", "Bog‘lanish kutilmoqda"],
    [
      "O‘qishga yozildi",
      s.statuses.YOZILDI || 0,
      "check",
      "Muvaffaqiyatli arizalar",
    ],
  ]
    .map(
      ([label, value, i, detail], idx) =>
        `<article class="stat-card ${idx === 0 ? "primary-stat" : "neu"}"><span>${icon(i)}${label}</span><strong>${fmt(value)}</strong><small>${detail}</small></article>`,
    )
    .join(
      "",
    )}</div><div class="dashboard-panels"><section class="analytics neu">${section("Yo‘nalishlar bo‘yicha")}<div class="bars">${s.top_courses.map((c) => `<div class="bar-item"><span>${esc(cleanTitle(c.course_name))}</span><strong>${fmt(c.count)}</strong><div class="bar-track neu-inset"><i style="width:${Math.max(2, (c.count / Math.max(s.total, 1)) * 100)}%"></i></div></div>`).join("") || '<p class="quiet">Birinchi arizadan keyin statistika shu yerda ko‘rinadi.</p>'}</div></section><section class="status-panel neu">${section("Arizalar holati")}<div class="status-summary">${Object.entries(
    statusLabels,
  )
    .map(
      ([k, v]) =>
        `<button data-status-open="${k}">${statusBadge(k)}<strong>${fmt(s.statuses[k] || 0)}</strong>${icon("arrow")}</button>`,
    )
    .join(
      "",
    )}</div><div class="users-total">${icon("users")} ${fmt(s.users)} ta foydalanuvchi</div></section></div>${section("So‘nggi arizalar", '<button class="text-button" data-page="leads">Barcha lidlar ' + icon("arrow") + "</button>")}<div class="lead-table neu">${recent.items.map(leadRow).join("") || empty("Hali ariza yo‘q", "Yangi murojaatlar shu yerda ko‘rinadi.")}</div>${isAdmin() ? `<div class="admin-tools">${button("Excel eksport", "export", "download", "secondary")}<button class="button secondary" data-page="broadcasts">${icon("send")} Xabarnoma</button></div>` : ""}`;
}
function leadRow(l) {
  return `<button class="lead-row" data-lead="${l.id}"><span class="lead-avatar neu-inset">${esc(initials(l.full_name))}</span><span class="lead-name"><strong>${esc(l.full_name)}</strong><small>#${l.id} · ${esc(cleanTitle(l.course_name))}</small></span><span class="lead-row-status">${statusBadge(l.status)}</span><span class="lead-row-date">${date(l.created_at)}</span>${icon("arrow")}</button>`;
}
function leadsPage() {
  const d = state.data;
  return `${pageHeading("Murojaatlar bilan ishlash", "Lidlar", "Qidiring, bog‘laning va natijani qayd qiling.", isAdmin() ? button("Excel eksport", "export", "download", "secondary") : "")}<div class="lead-controls"><label class="search-box neu-inset">${icon("search")}<input id="lead-search" type="search" placeholder="Ism, telefon, kurs yoki ariza raqami" aria-label="Lidlarni qidirish" maxlength="100" value="${esc(state.query)}"></label><div class="filter-tabs" role="group" aria-label="Ariza holati">${[["", "Barchasi"], ...Object.entries(statusLabels)].map(([k, v]) => `<button class="filter-tab ${state.filter === k ? "active" : ""}" data-filter="${k}" aria-pressed="${state.filter === k}">${v}</button>`).join("")}</div></div><div class="list-description"><span>${fmt(d.total)} ta ariza</span><span>${d.total ? state.offset + 1 : 0}–${Math.min(state.offset + d.items.length, d.total)}</span></div><div class="lead-table neu" id="lead-results">${d.items.map(leadRow).join("") || empty("Mos ariza topilmadi.", "Boshqa so‘z yoki holat bilan qidirib ko‘ring.")}</div>${pagination(d.total, 30)}`;
}
function pagination(total, limit) {
  if (total <= limit) return "";
  return `<div class="pagination"><button class="button secondary" data-offset="${Math.max(0, state.offset - limit)}" ${state.offset === 0 ? "disabled" : ""}>${icon("back")} Oldingi</button><span>${Math.floor(state.offset / limit) + 1} / ${Math.ceil(total / limit)}</span><button class="button secondary" data-offset="${state.offset + limit}" ${state.offset + limit >= total ? "disabled" : ""}>Keyingi ${icon("arrow")}</button></div>`;
}
function teamPage() {
  return `${pageHeading("Sotuvlar jamoasi", "Birga ishlaymiz.", "Sotuvchilarning mini app va botga kirishini boshqaring.", button("Sotuvchi qo‘shish", "add-sales", "plus"))}<div class="team-grid">${state.data.items.map((p) => `<article class="team-card neu"><div class="lead-avatar neu-inset">${esc(initials(p.full_name))}</div><h2>${esc(p.full_name)}</h2><p>${esc(p.phone || "Telefon kiritilmagan")}</p><span class="quiet">Telegram ID: ${p.telegram_id}</span><span class="badge status-yozildi">Faol sotuvchi</span><button class="button subtle full" data-remove-sales="${p.telegram_id}" data-name="${esc(p.full_name)}">${icon("close")} Kirishni bekor qilish</button></article>`).join("") || empty("Hozircha sotuvchilar yo‘q.", "Jamoangizning birinchi a’zosini qo‘shing.", button("Sotuvchi qo‘shish", "add-sales", "plus"))}</div>`;
}
function menuCard(action, i, title, description, page = false) {
  return `<button class="menu-card neu" ${page ? "data-page" : "data-action"}="${action}"><span class="menu-symbol neu-inset">${icon(i)}</span><span><strong>${title}</strong><small>${description}</small></span>${icon("arrow")}</button>`;
}
function morePage() {
  if (state.view === "work" && isAdmin())
    return `${pageHeading("Markaz boshqaruvi", "Ishingizga kerakli vositalar.")}<div class="menu-grid">${menuCard("broadcasts", "send", "Ommaviy xabarnoma", "Matn, rasm yoki video", true)}${menuCard("settings", "settings", "Markaz sozlamalari", "Kontakt, manzil va matnlar", true)}${menuCard("feedbacks", "mail", "Fikr va takliflar", "Foydalanuvchilar murojaatlari", true)}${menuCard("export", "download", "Excel eksport", "Barcha lidlarni yuklab olish")}${menuCard("switch-view", "book", "O‘quvchi ko‘rinishi", "Kurslar va shaxsiy arizalar")}${menuCard("profile", "user", "Profilim", "Hisob va kirish ma’lumotlari")}</div>`;
  if (state.view === "work")
    return `${pageHeading("Sotuvchi kabineti", "Ish joyingiz.")}<div class="menu-grid">${menuCard("leads", "files", "Arizalar bilan ishlash", "Holat va suhbat tafsilotlari", true)}${menuCard("switch-view", "book", "O‘quvchi ko‘rinishi", "Kurslar va markaz haqida")}${menuCard("profile", "user", "Profilim", "Telegram hisobingiz")}${menuCard("contacts", "phone", "Markaz bilan bog‘lanish", "Manzil va kontaktlar")}</div>`;
  return `${pageHeading("ITLive siz bilan", "Yana nimalar bor?", "O‘rganish yo‘lingiz uchun kerakli ma’lumotlar.")}<div class="menu-grid">${menuCard("quiz", "spark", "IT kasb tanlash testi", "5 savolda mos yo‘nalish")}${menuCard("trial", "gift", "Bepul sinov darsi", "Avval tanishing, keyin tanlang")}${menuCard("mentors", "users", "Mentorlarimiz", "Tajriba ulashadigan jamoa")}${menuCard("discounts", "heart", "Chegirmalar va aksiyalar", "Ta’lim uchun qulay imkoniyatlar")}${menuCard("contacts", "pin", "Manzil va kontaktlar", "Bizni topish oson")}${menuCard("about", "book", "ITLive haqida", "Markaz va ta’lim yondashuvi")}${menuCard("faq", "help", "Savol-javoblar", "Ko‘p so‘raladigan savollar")}${menuCard("feedback", "mail", "Fikr va taklif", "Sizni eshitishga tayyormiz")}</div>`;
}
function settingsPage() {
  return `${pageHeading("Markaz ma’lumotlari", "Sozlamalar", "Bu ma’lumotlar bot va mini appda birgalikda yangilanadi.")}<form id="settings-form" class="settings-form">${formError}${[
    [
      "Asosiy ma’lumotlar",
      ["center_name", "phone_1", "phone_2", "working_hours"],
    ],
    ["Manzil va xarita", ["address", "landmark", "latitude", "longitude"]],
    ["Havolalar", ["telegram", "instagram", "website", "youtube"]],
    ["Markaz matnlari", ["about_text", "discounts_text"]],
  ]
    .map(
      ([title, keys]) =>
        `<section class="settings-group neu"><h2>${title}</h2><div class="settings-fields">${keys.map((k) => (k.endsWith("_text") ? textField(settingsLabels[k], k, state.boot.settings[k], 8) : field(settingsLabels[k], k, state.boot.settings[k] || "", { type: ["telegram", "instagram", "website", "youtube"].includes(k) ? "url" : "text", max: 500 }))).join("")}</div></section>`,
    )
    .join(
      "",
    )}<div class="save-bar">${submitButton("Sozlamalarni saqlash")}</div></form>`;
}
function feedbacksPage() {
  const d = state.data;
  return `${pageHeading("Foydalanuvchilarni eshitamiz", "Fikr va takliflar", fmt(d.total) + " ta murojaat")}<div class="feedback-grid">${d.items.map((f) => `<article class="feedback-card neu"><div><span class="lead-avatar neu-inset">${esc(initials(f.full_name))}</span><span><strong>${esc(f.full_name)}</strong><small>${date(f.created_at)}</small></span></div><p>${esc(f.message)}</p><a class="text-button" href="tg://user?id=${f.user_id}">${icon("send")} Telegramda javob berish</a></article>`).join("") || empty("Hozircha fikrlar yo‘q.", "Foydalanuvchilar yuborgan xabarlar shu yerda paydo bo‘ladi.")}</div>${pagination(d.total, 30)}`;
}
function broadcastsPage() {
  const data = state.data;
  const labels = {
    queued: "Navbatda",
    running: "Yuborilmoqda",
    finished: "Yakunlangan",
    cancelled: "To‘xtatilgan",
  };
  return `${pageHeading("Foydalanuvchilar bilan aloqa", "Ommaviy xabarnoma", fmt(data.stats.users) + " ta foydalanuvchi mavjud.", button("Xabar tayyorlash", "new-broadcast", "plus"))}<div class="broadcast-list">${data.jobs.map((j) => `<article class="broadcast-card neu"><div class="broadcast-heading"><span class="badge">${labels[j.status] || j.status}</span><small>${date(j.created_at)}</small></div><p>${esc(j.message)}</p>${j.upload_id ? `<div class="quiet">${icon("files")} Media fayl biriktirilgan</div>` : ""}<div class="broadcast-counts"><span><b>${fmt(j.total)}</b> Jami</span><span><b>${fmt(j.sent)}</b> Yetkazildi</span><span><b>${fmt(j.failed)}</b> Yetmadi</span><span><b>${fmt(j.remaining)}</b> Kutilmoqda</span></div>${j.remaining > 0 && j.status !== "cancelled" ? `<button class="button secondary" data-cancel-job="${j.id}">${icon("close")} Yuborishni to‘xtatish</button>` : ""}</article>`).join("") || empty("Birinchi xabaringizni tayyorlang.", "Yangiliklar va yangi kurslar haqida foydalanuvchilarga xabar bering.", button("Xabar tayyorlash", "new-broadcast", "plus"))}</div>`;
}

function showCourse(id) {
  const c = state.boot.courses.find((c) => c.id === Number(id));
  if (!c) return;
  const [ico, cat] = courseType(c);
  showModal(
    cleanTitle(c.name),
    `<div class="course-detail-art neu-inset">${icon(ico)}<span>${cat}</span></div><p class="detail-description">${esc(c.description)}</p><div class="detail-facts"><div><span>Davomiyligi</span><strong>${esc(c.duration)}</strong></div><div><span>Kurs narxi</span><strong>${esc(c.price)}</strong></div></div><h3>O‘rganadigan texnologiyalaringiz</h3><div class="tech-chips">${c.technologies
      .split(/,|·/)
      .filter(Boolean)
      .map((t) => `<span class="neu-inset">${esc(t.trim())}</span>`)
      .join(
        "",
      )}</div>${c.is_active ? `<button class="button primary full" data-enroll="${c.id}">${icon("files")} Kursga yozilish</button><button class="button secondary full spaced" data-trial-course="${c.id}">${icon("gift")} Bepul sinov darsi</button>` : '<p class="notice">Kurs hozir yashirilgan.</p>'}${isAdmin() && state.view === "work" ? `<button class="text-button spaced" data-edit-course="${c.id}">Kursni tahrirlash</button>` : ""}`,
  );
}
function registration(id = null, kind = "course") {
  const list = activeCourses();
  if (!list.length)
    return toast("Hozircha faol kurs yo‘q. Markaz bilan bog‘laning.");
  const user = state.boot.user;
  showModal(
    kind === "trial" ? "Bepul sinov darsiga yozilish" : "Kursga yozilish",
    `<p class="form-intro">Ma’lumotlaringizni qoldiring. Jamoamiz siz bilan bog‘lanadi.</p><form id="application-form" data-kind="${kind}" data-key="${crypto.randomUUID()}">${formError}${field("Ism va familiya", "full_name", user.full_name, { max: 100, extra: 'minlength="3" autocomplete="name"' })}${field("Telefon raqamingiz", "phone", user.phone || "", { type: "tel", max: 30, extra: 'placeholder="+998901234567" autocomplete="tel"' })}${tg?.requestContact ? '<button type="button" class="text-button contact-request" data-action="request-contact">' + icon("phone") + " Telegram raqamimni ulashish</button>" : ""}<div class="form-grid">${field("Yoshingiz", "age", "", { type: "number", extra: 'min="7" max="90" inputmode="numeric" placeholder="18"' })}${selectField("Hududingiz", "region", regions, regions[0])}</div><button type="button" class="text-button" data-action="locate">${icon("pin")} Lokatsiyamni belgilash</button>${selectField(
      "Tanlagan kursingiz",
      "course_id",
      list.map((c) => [c.id, cleanTitle(c.name)]),
      id || list[0].id,
    )}${selectField("Sizga qulay vaqt", "time_preference", times, "Kechki")}<p class="form-intro">Arizani yuborish orqali markaz siz bilan bog‘lanishi uchun ushbu ma’lumotlarni taqdim etasiz.</p>${submitButton("Arizani yuborish")}</form>`,
  );
}
async function showLead(id) {
  const l = await api("/staff/leads/" + id);
  showModal(
    "Ariza #" + l.id,
    `<div class="lead-detail-header"><span class="lead-avatar neu-inset">${esc(initials(l.full_name))}</span><div><h3>${esc(l.full_name)}</h3>${statusBadge(l.status)}</div></div><dl class="lead-facts">${[
      ["Kurs", cleanTitle(l.course_name)],
      ["Telefon", l.phone],
      ["Yosh", l.age + " yosh"],
      ["Hudud", l.region],
      ["Qulay vaqt", l.time_preference],
      ["Turi", l.kind === "trial" ? "Bepul sinov darsi" : "Kursga yozilish"],
      ["Ariza sanasi", date(l.created_at)],
    ]
      .map(([k, v]) => `<div><dt>${k}</dt><dd>${esc(v)}</dd></div>`)
      .join(
        "",
      )}</dl><div class="lead-contact-actions"><a class="button secondary" href="tel:${esc(l.phone.replace(/[^+0-9]/g, ""))}">${icon("phone")} Qo‘ng‘iroq</a><a class="button secondary" href="tg://user?id=${l.user_id}">${icon("send")} Telegram</a></div><form id="lead-form" data-id="${l.id}" data-version="${esc(l.updated_at)}">${formError}${selectField("Ariza holati", "status", Object.entries(statusLabels), l.status)}${textField("Suhbat tafsiloti va izoh", "sales_notes", l.sales_notes || "", 4, 2000, false)}<p class="form-intro">Holat o‘zgarsa, foydalanuvchiga bot orqali xabar beriladi.</p>${submitButton("O‘zgarishlarni saqlash")}</form>`,
  );
}
function courseForm(id) {
  const c = state.boot.courses.find((c) => c.id === Number(id));
  showModal(
    c ? "Kursni tahrirlash" : "Yangi kurs qo‘shish",
    `<form id="course-form" data-id="${c?.id || ""}">${formError}${field("Kurs nomi", "name", c?.name || "", { max: 120, extra: 'minlength="3"' })}${textField("Kurs tavsifi", "description", c?.description || "", 5, 2500)}<div class="form-grid">${field("Davomiyligi", "duration", c?.duration || "", { max: 60, extra: 'placeholder="6 oy"' })}${field("Narxi", "price", c?.price || "", { max: 80, extra: 'placeholder="1 200 000 so‘m / oy"' })}</div>${textField("Texnologiyalar", "technologies", c?.technologies || "", 2, 500, false)}${field("Ro‘yxatdagi tartib", "sort_order", c?.sort_order || 0, { type: "number", extra: 'min="0" max="10000"' })}<label class="check-field"><input name="is_active" type="checkbox" ${!c || c.is_active ? "checked" : ""}>Kurs foydalanuvchilarga ko‘rinsin</label>${submitButton("Kursni saqlash")}</form>${c ? `<button class="button danger full spaced" data-delete-course="${c.id}">${icon("close")} Kursni o‘chirish</button>` : ""}`,
  );
}
function showQuiz() {
  const q = state.boot.quiz[state.quizAnswers.length];
  showModal(
    "Sizga qaysi IT kasbi mos?",
    `<div class="quiz-progress"><span>${state.quizAnswers.length + 1} / 5 savol</span><span>${state.quizAnswers.length * 20}%</span><div class="bar-track neu-inset"><i style="width:${state.quizAnswers.length * 20}%"></i></div></div><h3 class="quiz-question">${esc(cleanTitle(q.question).replace(/^\d+[^\p{L}]+/u, ""))}</h3><div class="quiz-options">${q.options.map((o, i) => `<button class="neu" data-quiz-choice="${i}"><span class="answer-letter neu-inset">${String.fromCharCode(65 + i)}</span><span>${esc(cleanTitle(o))}</span>${icon("arrow")}</button>`).join("")}</div><div class="quiz-bottom">${state.quizAnswers.length ? '<button class="text-button" data-action="quiz-back">' + icon("back") + " Oldingi savol</button>" : ""}<p>O‘zingizga yaqin javobni tanlang.</p></div>`,
  );
}
async function quizAnswer(value) {
  state.quizAnswers.push(value);
  if (state.quizAnswers.length < 5) return showQuiz();
  try {
    const result = await api("/quiz/result", {
      method: "POST",
      body: { answers: state.quizAnswers },
    });
    showModal(
      "Yo‘nalishingizni kashf etdingiz.",
      `<div class="quiz-result"><span class="result-seal neu">${icon("spark")}</span><p>Javoblaringizga ko‘ra</p><h3>${esc(result.title)}</h3><p>${esc(result.description)}</p><small>Bu test tanishuv uchun tavsiya beradi. Yakuniy tanlov sizniki.</small>${result.course_id ? `<button class="button primary full spaced" data-course="${result.course_id}">${icon("book")} Kurs bilan tanishish</button>` : `<button class="button primary full spaced" data-action="trial">${icon("gift")} Bepul maslahatga yozilish</button>`}<button class="text-button spaced" data-action="quiz">Testni qayta boshlash</button></div>`,
    );
  } catch (error) {
    state.quizAnswers.pop();
    showError(error);
  }
}
async function action(name) {
  if (name === "close-modal") return closeModal();
  if (name === "show-my-applications") {
    closeModal();
    return navigate("applications");
  }
  if (name === "reload") return location.reload();
  if (name === "refresh") {
    await refreshAll();
    return toast("Ma’lumotlar yangilandi.");
  }
  if (name === "switch-view") {
    state.view = state.view === "work" ? "learn" : "work";
    if (!canWork()) state.view = "learn";
    state.page = "home";
    renderShell();
    return navigate("home");
  }
  if (name === "trial") return registration(null, "trial");
  if (name === "quiz") {
    state.quizAnswers = [];
    return showQuiz();
  }
  if (name === "quiz-back") {
    state.quizAnswers.pop();
    return showQuiz();
  }
  if (name === "profile") {
    const u = state.boot.user;
    return showModal(
      "Shaxsiy profil",
      `<div class="profile-panel"><span class="avatar neu">${esc(initials(u.full_name))}</span><h3>${esc(u.full_name)}</h3><p>${esc(u.username ? "@" + u.username : "Telegram foydalanuvchisi")}</p><span class="badge">${{ admin: "Admin", sales: "Sotuvchi", user: "Foydalanuvchi" }[u.role]}</span></div><div class="notice">Hisobingiz Telegram orqali tasdiqlangan. Sizga tegishli ma’lumotlar shaxsiy kabinetingizda ko‘rinadi.</div>${button("Hisobdan chiqish", "logout", "user", "secondary full")}`,
    );
  }
  if (name === "logout") {
    await api("/auth/logout", { method: "POST" });
    closeModal();
    return showGate(
      "Hisobdan chiqdingiz. Qayta kirish uchun Telegramdagi mini appni oching.",
    );
  }
  if (name === "feedback")
    return showModal(
      "Fikr va taklif",
      `<p class="form-intro">Kurslar, ta’lim yoki xizmatimiz haqida fikringizni yozing.</p><form id="feedback-form">${formError}${textField("Xabaringiz", "message", "", 6, 3000)}${submitButton("Xabarni yuborish")}</form>`,
    );
  if (name === "faq")
    return showModal(
      "Ko‘p so‘raladigan savollar",
      `<div class="faq-list">${state.boot.faq.map((f) => `<details><summary>${esc(f.q)}${icon("plus")}</summary><p>${esc(f.a)}</p></details>`).join("")}</div><button class="button secondary full spaced" data-action="feedback">${icon("mail")} Boshqa savolim bor</button>`,
    );
  if (name === "mentors")
    return showModal(
      "Mentorlarimiz",
      `<div class="mentor-list">${state.boot.mentors.map((m) => `<article class="mentor-card"><span class="lead-avatar neu-inset">${esc(initials(m.name))}</span><div><h3>${esc(m.name)}</h3><strong>${esc(m.role)}</strong><p>${esc(m.experience)}</p><small>${esc(m.companies)}</small></div></article>`).join("")}</div>`,
      true,
    );
  if (name === "about" || name === "discounts")
    return showModal(
      name === "about" ? "ITLive Academy haqida" : "Chegirmalar va aksiyalar",
      `<div class="about-mark neu-inset">${icon(name === "about" ? "code" : "gift")}<span>${name === "about" ? "itlive." : "Siz uchun"}</span></div><p class="rich-text">${esc(plain(state.boot.settings[name === "about" ? "about_text" : "discounts_text"]))}</p><button class="button primary full" data-action="trial">${icon("gift")} Bepul sinov darsiga yozilish</button>`,
    );
  if (name === "contacts") {
    const s = state.boot.settings;
    const geo = Number(s.latitude) + "," + Number(s.longitude);
    return showModal(
      "Manzil va bog‘lanish",
      `<div class="map-card neu-inset">${icon("pin")}<h3>${esc(s.center_name)}</h3><p>${esc(s.address)}</p><small>${esc(s.landmark)}</small></div><div class="contact-info"><div>${icon("clock")}<span>${esc(s.working_hours)}</span></div>${[
        s.phone_1,
        s.phone_2,
      ]
        .filter(Boolean)
        .map(
          (p) =>
            `<a href="tel:${esc(p.replace(/[^+0-9]/g, ""))}">${icon("phone")}<span>${esc(p)}</span>${icon("arrow")}</a>`,
        )
        .join(
          "",
        )}</div><div class="contact-maps"><a class="button secondary" href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(geo)}" target="_blank" rel="noopener">${icon("pin")} Google Maps</a><a class="button secondary" href="https://yandex.uz/maps/?pt=${encodeURIComponent(Number(s.longitude) + "," + Number(s.latitude))}&z=16&l=map" target="_blank" rel="noopener">${icon("pin")} Yandex Maps</a></div><div class="social-links">${[
        "telegram",
        "instagram",
        "website",
        "youtube",
      ]
        .filter((k) => safeUrl(s[k]) !== "#")
        .map(
          (k) =>
            `<a href="${esc(safeUrl(s[k]))}" target="_blank" rel="noopener">${{ telegram: "Telegram", instagram: "Instagram", website: "Veb-sayt", youtube: "YouTube" }[k]} ${icon("external")}</a>`,
        )
        .join("")}</div>`,
    );
  }
  if (name === "locate") {
    if (!navigator.geolocation)
      return toast(
        "Bu qurilmada lokatsiya mavjud emas. Hududni qo‘lda tanlang.",
      );
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const select = modal.querySelector('[name="region"]');
        if (!select) return;
        const value = `Lokatsiya: ${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)}`;
        select.add(new Option(value, value, true, true));
        toast("Lokatsiyangiz belgilandi.");
      },
      () => toast("Lokatsiya olinmadi. Hududni qo‘lda tanlang."),
      { timeout: 10000, maximumAge: 60000 },
    );
    return;
  }
  if (name === "request-contact") {
    tg?.requestContact(async (ok) => {
      if (!ok) return toast("Telefonni qo‘lda kiritishingiz mumkin.");
      await new Promise((r) => setTimeout(r, 1200));
      await refreshBoot();
      const input = modal.querySelector('[name="phone"]');
      if (input && state.boot.user.phone) input.value = state.boot.user.phone;
      else toast("Telefon raqamingizni maydonga kiriting.");
    });
    return;
  }
  if (!isAdmin()) return;
  if (name === "add-course") return courseForm();
  if (name === "add-sales")
    return showModal(
      "Sotuvchi qo‘shish",
      `<form id="sales-form">${formError}${field("Ism va familiya", "full_name", "", { max: 100, extra: 'minlength="3"' })}${field("Telegram ID", "telegram_id", "", { extra: 'inputmode="numeric" pattern="[0-9]{5,16}" placeholder="123456789"' })}${field("Telefon", "phone", "", { type: "tel", required: false, max: 30 })}<p class="form-intro">Sotuvchi avval botni /start orqali ishga tushirgan bo‘lishi kerak.</p>${submitButton("Sotuvchini qo‘shish")}</form>`,
    );
  if (name === "export") {
    return showModal(
      "Excel eksport",
      `<p class="form-intro">Barcha arizalar, holatlar va sotuvchi izohlari Excel faylga jamlanadi.</p>${button("Qurilmaga yuklab olish", "download-excel", "download", "primary full")}${button("Telegramimga yuborish", "send-excel", "send", "secondary full spaced")}`,
    );
  }
  if (name === "send-excel") {
    const b = modal.querySelector('[data-action="send-excel"]');
    b.disabled = true;
    try {
      await api("/admin/export/telegram", { method: "POST" });
      closeModal();
      toast("Excel fayl Telegramingizga yuborildi.");
    } finally {
      if (b.isConnected) b.disabled = false;
    }
    return;
  }
  if (name === "download-excel") {
    const blob = await api("/admin/export.xlsx", { blob: true });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "itlive-leads.xlsx";
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
    closeModal();
    return toast("Excel fayl tayyorlandi.");
  }
  if (name === "new-broadcast") {
    pendingDraft = null;
    return showModal(
      "Xabarnoma tayyorlash",
      `<form id="broadcast-form">${formError}${textField("Xabar matni", "message", "", 7, 4096)}<label class="field">Rasm yoki video (ixtiyoriy)<input name="media" type="file" accept="image/jpeg,image/png,video/mp4"><small>JPG/PNG — 10 MB gacha. MP4 — 20 MB gacha. Media izohi 1024 belgigacha.</small></label><p class="form-intro">Yuborishdan oldin xabar va qabul qiluvchilarni ko‘rib chiqasiz.</p>${submitButton("Xabarni ko‘rib chiqish")}</form>`,
    );
  }
  if (name === "send-broadcast") {
    if (!pendingDraft) return;
    const b = modal.querySelector('[data-action="send-broadcast"]');
    b.disabled = true;
    b.querySelector("span").textContent = "Yuborish navbatiga qo‘shilmoqda…";
    try {
      if (pendingDraft.file && !pendingDraft.upload_id) {
        const form = new FormData();
        form.append("file", pendingDraft.file);
        const upload = await api("/admin/uploads", {
          method: "POST",
          body: form,
        });
        pendingDraft.upload_id = upload.id;
      }
      await api("/admin/broadcasts", {
        method: "POST",
        body: {
          message: pendingDraft.message,
          upload_id: pendingDraft.upload_id || null,
          confirmed: true,
          request_key: pendingDraft.key,
        },
      });
      closeModal();
      pendingDraft = null;
      await navigate("broadcasts");
      toast("Xabarnoma yuborish navbatiga qo‘shildi.");
    } catch (error) {
      b.disabled = false;
      b.querySelector("span").textContent =
        "Barcha foydalanuvchilarga yuborish";
      const errorEl = modal.querySelector(".form-error");
      errorEl.hidden = false;
      errorEl.textContent = error.message;
    }
    return;
  }
}

document.addEventListener("click", async (event) => {
  const el = event.target.closest("button,a");
  if (!el || el.disabled) return;
  try {
    if (el.hasAttribute("data-page")) {
      event.preventDefault();
      return await navigate(el.dataset.page);
    }
    if (el.dataset.action) return await action(el.dataset.action);
    if (el.dataset.course) return showCourse(el.dataset.course);
    if (el.dataset.enroll) return registration(Number(el.dataset.enroll));
    if (el.dataset.trialCourse)
      return registration(Number(el.dataset.trialCourse), "trial");
    if (el.hasAttribute("data-quiz-choice"))
      return await quizAnswer(Number(el.dataset.quizChoice));
    if (el.dataset.lead) return await showLead(el.dataset.lead);
    if (el.dataset.category) {
      state.category = el.dataset.category;
      document.querySelector("#page").innerHTML = coursesPage();
      return;
    }
    if (el.hasAttribute("data-filter")) {
      state.filter = el.dataset.filter;
      state.offset = 0;
      return await loadPage();
    }
    if (el.dataset.statusOpen) {
      state.page = "leads";
      state.filter = el.dataset.statusOpen;
      state.offset = 0;
      updateNav();
      return await loadPage();
    }
    if (el.hasAttribute("data-offset")) {
      state.offset = Number(el.dataset.offset);
      return await loadPage();
    }
    if (!isAdmin()) return;
    if (el.dataset.editCourse) return courseForm(el.dataset.editCourse);
    if (el.dataset.toggleCourse) {
      const c = state.boot.courses.find(
        (c) => c.id === Number(el.dataset.toggleCourse),
      );
      await api("/admin/courses/" + c.id, {
        method: "PUT",
        body: {
          name: c.name,
          description: c.description,
          duration: c.duration,
          price: c.price,
          technologies: c.technologies || "",
          sort_order: c.sort_order || 0,
          is_active: !c.is_active,
        },
      });
      await refreshAll();
      return toast("Kurs holati yangilandi.");
    }
    if (el.dataset.deleteCourse) {
      const id = el.dataset.deleteCourse;
      return showModal(
        "Kursni o‘chirish",
        `<p>Kurs katalogdan butunlay o‘chiriladi. Avvalgi arizalarda uning nomi saqlanadi.</p><p class="notice">Kursni vaqtincha ko‘rsatmaslik uchun “Yashirish” amalidan foydalanishingiz mumkin.</p><button class="button danger full" data-confirm-delete-course="${id}">${icon("close")} Kursni butunlay o‘chirish</button>${button("Bekor qilish", "close-modal", "back", "secondary full spaced")}`,
      );
    }
    if (el.dataset.confirmDeleteCourse) {
      await api("/admin/courses/" + el.dataset.confirmDeleteCourse, {
        method: "DELETE",
      });
      closeModal();
      await refreshAll();
      return toast("Kurs o‘chirildi.");
    }
    if (el.dataset.removeSales)
      return showModal(
        "Sotuvchi kirishini bekor qilish",
        `<p><strong>${esc(el.dataset.name)}</strong> endi sotuvchi kabinetiga kira olmaydi. Oldingi arizalar saqlanadi.</p><button class="button danger full" data-confirm-remove-sales="${el.dataset.removeSales}">${icon("close")} Kirishni bekor qilish</button>${button("Ortga", "close-modal", "back", "secondary full spaced")}`,
      );
    if (el.dataset.confirmRemoveSales) {
      await api("/admin/sales/" + el.dataset.confirmRemoveSales, {
        method: "DELETE",
      });
      closeModal();
      await loadPage();
      return toast("Sotuvchi kirishi bekor qilindi.");
    }
    if (el.dataset.cancelJob)
      return showModal(
        "Yuborishni to‘xtatish",
        `<p>Navbatdagi xabarlar yuborilmaydi. Allaqachon yetkazilgan xabarlar saqlanadi; hozir yuborilayotgan bitta xabar yetib borishi mumkin.</p><button class="button danger full" data-confirm-cancel-job="${el.dataset.cancelJob}">${icon("close")} Yuborishni to‘xtatish</button>${button("Davom ettirish", "close-modal", "arrow", "secondary full spaced")}`,
      );
    if (el.dataset.confirmCancelJob) {
      await api(
        "/admin/broadcasts/" + el.dataset.confirmCancelJob + "/cancel",
        { method: "POST" },
      );
      closeModal();
      await loadPage();
      return toast("Xabarnoma to‘xtatildi.");
    }
  } catch (error) {
    showError(error);
  }
});
document.addEventListener("input", (event) => {
  if (event.target.id === "lead-search") {
    state.query = event.target.value;
    state.offset = 0;
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
      const input = document.querySelector("#lead-search");
      const position = input?.selectionStart;
      await loadPage();
      const next = document.querySelector("#lead-search");
      if (next) {
        next.focus();
        try {
          next.setSelectionRange(position, position);
        } catch {}
      }
    }, 400);
  }
});
document.addEventListener("submit", async (event) => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;
  event.preventDefault();
  if (form.dataset.pending) return;
  const data = Object.fromEntries(new FormData(form));
  const submit = form.querySelector('[type="submit"]');
  const original = submit?.innerHTML;
  form.dataset.pending = "1";
  if (submit) {
    submit.disabled = true;
    submit.innerHTML = '<span class="spinner"></span> Saqlanmoqda…';
  }
  try {
    if (form.id === "application-form") {
      const result = await api("/applications", {
        method: "POST",
        key: form.dataset.key,
        body: {
          ...data,
          age: Number(data.age),
          course_id: Number(data.course_id),
          kind: form.dataset.kind,
        },
      });
      showModal(
        "Arizangiz qabul qilindi.",
        `<div class="success-panel"><span class="result-seal neu">${icon("check")}</span><h3>Yaxshi boshlanish!</h3><p>Ariza raqamingiz <strong>#${result.id}</strong>. Jamoamiz tez orada siz bilan bog‘lanadi.</p><button class="button primary full" data-action="show-my-applications">${icon("files")} Arizalarimni ko‘rish</button></div>`,
      );
      return;
    }
    if (form.id === "lead-form") {
      await api("/staff/leads/" + form.dataset.id, {
        method: "PATCH",
        body: {
          status: data.status,
          sales_notes: data.sales_notes,
          updated_at: form.dataset.version,
        },
      });
      closeModal();
      await loadPage();
      return toast("Ariza holati va izoh saqlandi.");
    }
    if (form.id === "feedback-form") {
      await api("/feedback", { method: "POST", body: data });
      closeModal();
      return toast("Xabaringiz qabul qilindi. Rahmat!");
    }
    if (form.id === "course-form") {
      const id = form.dataset.id;
      await api("/admin/courses" + (id ? "/" + id : ""), {
        method: id ? "PUT" : "POST",
        body: {
          ...data,
          is_active: form.elements.is_active.checked,
          sort_order: Number(data.sort_order),
        },
      });
      closeModal();
      await refreshAll();
      return toast("Kurs saqlandi.");
    }
    if (form.id === "sales-form") {
      await api("/admin/sales", {
        method: "POST",
        body: { ...data, telegram_id: Number(data.telegram_id) },
      });
      closeModal();
      await loadPage();
      return toast("Sotuvchi qo‘shildi.");
    }
    if (form.id === "settings-form") {
      await api("/admin/settings", { method: "PUT", body: { values: data } });
      await refreshAll();
      return toast("Sozlamalar saqlandi.");
    }
    if (form.id === "broadcast-form") {
      const file = form.elements.media.files[0];
      if (
        file &&
        file.size > (file.type.startsWith("image/") ? 10 : 20) * 1024 * 1024
      )
        throw new Error("Tanlangan media fayl hajmi juda katta.");
      if (file && data.message.length > 1024)
        throw new Error("Media bilan xabar matni 1024 belgidan oshmasin.");
      const stats = await api("/staff/statistics");
      pendingDraft = { message: data.message, file, key: crypto.randomUUID() };
      if (file) objectUrl = URL.createObjectURL(file);
      showModal(
        "Xabarnomani tekshiring",
        `${formError}<div class="broadcast-preview neu-inset">${file ? (file.type.startsWith("video/") ? `<video controls playsinline src="${objectUrl}" aria-label="Xabarnoma videosi"></video>` : `<img src="${objectUrl}" alt="Xabarnoma rasmi">`) : ""}<p>${esc(data.message)}</p><small>${esc(state.boot.settings.center_name)}</small></div><p class="notice">Xabar botni ishga tushirgan <strong>${fmt(stats.users)} ta foydalanuvchiga</strong> yuboriladi.</p>${button("Barcha foydalanuvchilarga yuborish", "send-broadcast", "send", "primary full")}${button("Bekor qilish", "close-modal", "back", "secondary full spaced")}`,
      );
      return;
    }
  } catch (error) {
    showError(error, form);
  } finally {
    delete form.dataset.pending;
    if (submit && submit.isConnected) {
      submit.disabled = false;
      submit.innerHTML = original;
    }
  }
});
modal.addEventListener("click", (event) => {
  if (event.target === modal) {
    const r = modal.getBoundingClientRect();
    if (
      event.clientX < r.left ||
      event.clientX > r.right ||
      event.clientY < r.top ||
      event.clientY > r.bottom
    )
      closeModal();
  }
});
modal.addEventListener("cancel", () => {
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
    objectUrl = null;
  }
});
window.addEventListener("popstate", async (event) => {
  if (!state.boot) return;
  state.view = event.state?.view === "work" && canWork() ? "work" : "learn";
  state.page = event.state?.page || "home";
  renderShell();
  await loadPage();
});
document.addEventListener("visibilitychange", () => {
  if (
    !document.hidden &&
    state.boot &&
    !modal.open &&
    !document.querySelector("#page form")
  )
    refreshAll().catch(showError);
});
setInterval(() => {
  if (
    !document.hidden &&
    state.boot &&
    state.view === "work" &&
    !modal.open &&
    ["home", "broadcasts"].includes(state.page)
  )
    loadPage();
}, 30000);
boot();
