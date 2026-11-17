const designs = [
  { id: 'pulse', number: '01', name: 'Pulse', tagline: 'Sodda. Ravon. Zamonaviy.', description: 'Yorug‘ fon, aniq ko‘k aksent va tanish mobil navigatsiya. Kurs tanlashdan ariza topshirishgacha qulay yo‘l.', tags: ['Yorug‘', 'Minimal', 'Universal'], colors: ['#2255f5', '#eef3ff', '#172343'], font: 'Manrope', recommend: true },
  { id: 'midnight', number: '02', name: 'Midnight', tagline: 'IT muhiti, birinchi ekrandan.', description: 'To‘q ko‘k muhit, yalpiz rang aksent va kod muharririga ishora. Texnologiyani yaxshi ko‘radiganlar uchun.', tags: ['To‘q', 'Texnologik', 'Ixcham'], colors: ['#0b1520', '#80e5ce', '#ebf6f4'], font: 'Sora + IBM Plex Mono' },
  { id: 'campus', number: '03', name: 'Campus', tagline: 'Katta maqsadlarga yorqin start.', description: 'Katta sarlavhalar, sariq aksent va dadil grafik chiziqlar. Yoshlar uchun energiyali, esda qoladigan uslub.', tags: ['Grafik', 'Dadil', 'Yoshlar uchun'], colors: ['#ffde59', '#20201e', '#fffdf4'], font: 'Outfit' },
  { id: 'studio', number: '04', name: 'Studio', tagline: 'O‘rganish ham bir san’at.', description: 'Nafis harflar, binafsha ohanglar va keng nafas oladigan kompozitsiya. Ijodiy, sokin ta’lim muhiti.', tags: ['Nafis', 'Ijodiy', 'Premium'], colors: ['#65509a', '#eee9f7', '#28213f'], font: 'Fraunces + DM Sans' },
  { id: 'atlas', number: '05', name: 'Atlas', tagline: 'Har qadam aniq.', description: 'Yashil aksent, tartibli katalog va bosqichma-bosqich yo‘l. Ta’lim va boshqaruvni birdek qulay qiladi.', tags: ['Tartibli', 'Sokin', 'Ishchan'], colors: ['#17644b', '#eef5ef', '#17382d'], font: 'Plus Jakarta Sans' },
  { id: 'orbit', number: '06', name: 'Orbit', tagline: 'Kelajagingiz atrofida.', description: 'Iliq korall rang, yumaloq shakllar va turli hajmdagi bloklar. Do‘stona, jonli va telefonga mos.', tags: ['Iliq', 'Yumshoq', 'Mobil'], colors: ['#cb513a', '#fff0ea', '#242e49'], font: 'Outfit' },
];

const iconPaths = {
  code: '<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-14-2 18"/>',
  home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
  book: '<path d="M12 5v16M3 3c4-1 7 0 9 2 2-2 5-3 9-2v16c-4-1-7 0-9 2-2-2-5-3-9-2z"/>',
  files: '<rect x="6" y="3" width="14" height="17" rx="2"/><path d="M3 7v13a3 3 0 0 0 3 3m4-15h6m-6 4h6m-6 4h4"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
  back: '<path d="m14 6-6 6 6 6"/>',
  down: '<path d="m6 9 6 6 6-6"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  spark: '<path d="m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3z"/>',
  users: '<circle cx="9" cy="8" r="3"/><path d="M2 21v-3a7 7 0 0 1 14 0v3m0-17a3 3 0 0 1 0 6m4 11v-3a7 7 0 0 0-3-6"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
  chart: '<path d="M3 3v18h18M7 16v-4m5 4V7m5 9V4"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-12 9h12m-9 3a3 3 0 0 0 6 0"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  phone: '<path d="m5 3 4 1 1 5-3 2a15 15 0 0 0 6 6l2-3 5 1 1 4c0 2-2 3-4 2C9 20 4 15 3 7c-1-2 0-4 2-4z"/>',
  pin: '<path d="M19 10c0 6-7 11-7 11S5 16 5 10a7 7 0 0 1 14 0z"/><circle cx="12" cy="10" r="2"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
  gift: '<path d="M3 9h18v4H3zm2 4v8h14v-8M12 9v12m0-12C5 9 4 2 8 3c3 0 4 6 4 6s1-6 4-6c4-1 3 6-4 6"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5m0 3h.01"/>',
  heart: '<path d="M20 5a5 5 0 0 0-8 1 5 5 0 0 0-8-1c-5 6 8 15 8 15s13-9 8-15z"/>',
  settings: '<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3"/><circle cx="15" cy="17" r="3"/>',
  send: '<path d="m22 2-7 20-4-9-9-4zM11 13 22 2"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  laptop: '<rect x="4" y="3" width="16" height="12" rx="2"/><path d="m4 15-3 5h22l-3-5"/>',
  mobile: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/>',
  shield: '<path d="m12 2 9 4v6c0 6-9 10-9 10S3 18 3 12V6z"/><path d="m8 12 3 3 5-6"/>',
  palette: '<path d="M12 3a9 9 0 1 0 0 18h1c3 0 3-3 1-4-2-2 0-4 2-3h2c5 0 3-11-6-11z"/><path d="M7 10h.01M10 6h.01M15 7h.01M6 14h.01"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  globe: '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
  external: '<path d="M14 3h7v7m0-7L10 14M10 3H3v18h18v-7"/>',
};
const icon = (name, cls = '') => `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.code}</svg>`;
const esc = (s = '') => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const courses = [
  { id: 1, name: 'Python Backend', category: 'Dasturlash', duration: '6 oy', price: '1 200 000', icon: 'code', tint: 'blue', tech: 'Python · Django · FastAPI', description: 'Serverlar, API va ma’lumotlar bazasi bilan ishlashni amaliy loyihalar orqali o‘rganing.', active: true },
  { id: 2, name: 'Frontend dasturlash', category: 'Dasturlash', duration: '6 oy', price: '1 100 000', icon: 'globe', tint: 'peach', tech: 'HTML · JavaScript · React', description: 'Tezkor, chiroyli va barcha qurilmalarga mos veb-ilovalar yarating.', active: true },
  { id: 3, name: 'Flutter Mobile', category: 'Dasturlash', duration: '5 oy', price: '1 300 000', icon: 'mobile', tint: 'mint', tech: 'Dart · Flutter · Firebase', description: 'Bitta kod yordamida Android va iOS ilovalarini yarating.', active: true },
  { id: 4, name: 'Grafik dizayn & UI/UX', category: 'Dizayn', duration: '4 oy', price: '1 000 000', icon: 'palette', tint: 'lilac', tech: 'Figma · Photoshop · Illustrator', description: 'Brendlar, vizual g‘oyalar va qulay interfeyslarni loyihalang.', active: true },
  { id: 5, name: 'Kiberxavfsizlik', category: 'Xavfsizlik', duration: '6 oy', price: '1 400 000', icon: 'shield', tint: 'mint', tech: 'Linux · Tarmoqlar · Web security', description: 'Tarmoqlar va veb-ilovalarni himoya qilishning amaliy asoslari.', active: true },
  { id: 6, name: 'IT Foundation', category: 'Boshlang‘ich', duration: '2 oy', price: '800 000', icon: 'laptop', tint: 'blue', tech: 'Kompyuter · Algoritmlar · Python', description: 'IT sohasida ilk qadamingiz: kompyuter savodxonligi va algoritmlar.', active: true },
  { id: 7, name: 'SMM & Marketing', category: 'Marketing', duration: '3 oy', price: '900 000', icon: 'chart', tint: 'peach', tech: 'Meta Ads · Kontent · Kopirayting', description: 'Ijtimoiy tarmoqlarda brendni rivojlantirish va reklama boshqaruvi.', active: true },
];
let leads = [
  { id: 1042, name: 'Namuna foydalanuvchi A', initials: 'NA', course: 'Python Backend', status: 'YANGI', time: '10:42', note: '', own: true },
  { id: 1041, name: 'Namuna foydalanuvchi B', initials: 'NB', course: 'Grafik dizayn & UI/UX', status: 'BOGLANILDI', time: '10:18', note: 'Kechki guruh bo‘yicha ma’lumot so‘radi.' },
  { id: 1040, name: 'Namuna foydalanuvchi C', initials: 'NC', course: 'Frontend dasturlash', status: 'YOZILDI', time: '09:56', note: '' },
  { id: 1039, name: 'Namuna foydalanuvchi D', initials: 'ND', course: 'Flutter Mobile', status: 'YANGI', time: '09:31', note: '' },
  { id: 1038, name: 'Namuna foydalanuvchi E', initials: 'NE', course: 'IT Foundation', status: 'BEKOR_QILINDI', time: '09:10', note: '' },
];
const statuses = { YANGI: 'Yangi', BOGLANILDI: 'Bog‘lanildi', YOZILDI: 'O‘qishga yozildi', BEKOR_QILINDI: 'Bekor qilindi' };
let team = [{ name: 'Namuna sotuvchi A', id: 'demo-sales-a' }, { name: 'Namuna sotuvchi B', id: 'demo-sales-b' }];
const params = new URLSearchParams(location.search);
let design = designs.find(d => d.id === params.get('design'));
let role = ['user', 'admin', 'sales'].includes(params.get('role')) ? params.get('role') : 'user';
const embedded = params.get('embed') === '1';
let page = 'home';
let courseFilter = 'Barchasi';
let leadFilter = 'ALL';
let search = '';
let quizStep = 0;
let quizScores = {};
let toastTimer;
const root = document.querySelector('#root');
const modal = document.querySelector('#modal');

function toast(message) {
  const el = document.querySelector('#toast');
  el.textContent = message;
  el.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('visible'), 3500);
}
function badge(status) { return `<span class="badge status-${status.toLowerCase()}"><i></i>${statuses[status]}</span>`; }
function openModal(title, content, wide = false) {
  modal.className = `theme-${design?.id || 'pulse'} ${wide ? 'wide-modal' : ''}`;
  modal.innerHTML = `<div class="modal-head"><h2 id="modal-title">${esc(title)}</h2><button type="button" class="icon-button" data-action="close" aria-label="Oynani yopish">${icon('close')}</button></div><div class="modal-body">${content}</div>`;
  if (!modal.open) modal.showModal();
  modal.querySelector('.icon-button')?.focus();
}
function closeModal() { modal.close(); }

function renderGallery() {
  document.body.className = 'gallery-body';
  root.innerHTML = `<header class="gallery-header"><a class="gallery-brand" href="./">${icon('code')}<span>itlive<span class="brand-dot">.</span><small>Dizayn studiyasi</small></span></a><span class="gallery-top-note"><i></i> Telegram Mini App</span></header>
    <section class="gallery-intro"><div><p class="intro-label">Birgalikda tanlaymiz</p><h1>Bitta akademiya.<br>Olti xil xarakter.</h1><p>ITLive mini appingiz qanday ko‘rinsin? Bir uslubni oching,<br class="desktop-break"> foydalanuvchi va boshqaruv panellarini sinab ko‘ring.</p></div><aside class="intro-aside"><span class="sketch-arrows">${icon('mobile')}${icon('arrow')}${icon('laptop')}</span><strong>Chiroyli ko‘rinish.<br>Qulay boshqaruv.</strong><span>6 dizayn &nbsp; / &nbsp; 3 rol &nbsp; / &nbsp; Mobil va desktop</span></aside></section>
    <section class="gallery-grid" aria-label="Dizayn variantlari">${designs.map(d => `<article class="design-card"><a href="?design=${d.id}" class="design-preview preview-${d.id}" aria-label="${d.number} ${d.name} dizaynini ko‘rish"><div class="preview-label"><span>${d.number}</span>${d.recommend ? '<span class="recommended">Tavsiya qilaman</span>' : `<span>${d.tags[0]}</span>`}</div><div class="mini-browser"><div class="mini-camera"></div><iframe src="?design=${d.id}&embed=1" title="${d.name} bosh sahifa namunasi" tabindex="-1" aria-hidden="true" loading="${d.number === '01' ? 'eager' : 'lazy'}"></iframe></div><span class="preview-open">${icon('external')}</span></a><div class="design-card-info"><div class="card-title-line"><a href="?design=${d.id}"><h2>${d.name}</h2></a><div class="swatches">${d.colors.map(c => `<i style="background:${c}"></i>`).join('')}</div></div><p>${d.tagline}</p><a class="card-link" href="?design=${d.id}">Dizaynni ko‘rish ${icon('arrow')}</a></div></article>`).join('')}</section>
    <footer class="gallery-footer"><div>${icon('shield')}<span>Ko‘rgazma namuna ma’lumotlari bilan ishlaydi.</span></div><span>Yoqgan variant raqamini chatga yozing.</span></footer>`;
}

function renderViewer() {
  document.body.className = 'viewer-body';
  const chosen = readChoice();
  root.innerHTML = `<header class="viewer-header"><a href="./" class="back-link">${icon('back')}<span>Barcha dizaynlar</span></a><a class="viewer-brand" href="./">itlive.</a><span class="prototype-label"><i></i> Interaktiv maket</span></header>
  <section class="viewer-controls"><div class="design-select-wrap"><label for="design-select">Dizayn</label><select id="design-select">${designs.map(d => `<option value="${d.id}" ${d.id === design.id ? 'selected' : ''}>${d.number} / ${d.name}</option>`).join('')}</select></div><div class="role-switch" role="group" aria-label="Panel ko‘rinishi">${[['user', 'Foydalanuvchi', 'user'], ['sales', 'Sotuvchi', 'users'], ['admin', 'Admin', 'shield']].map(([r, label, ico]) => `<button class="${role === r ? 'active' : ''}" aria-pressed="${role === r}" data-role="${r}">${icon(ico)}<span>${label}</span></button>`).join('')}</div><div class="device-switch" role="group" aria-label="Ekran o‘lchami"><button class="active" data-device="mobile" aria-label="Mobil ko‘rinish" aria-pressed="true">${icon('mobile')}</button><button data-device="desktop" aria-label="Keng ko‘rinish" aria-pressed="false">${icon('laptop')}</button></div></section>
  <div class="viewer-stage"><aside class="design-notes"><span class="design-index">Dizayn ${design.number}</span><h1>${design.name}</h1><h2>${design.tagline}</h2><p>${design.description}</p><div class="tag-list">${design.tags.map(t => `<span>${t}</span>`).join('')}</div><div class="notes-section"><h3>Ranglar va shrift</h3><div class="large-swatches">${design.colors.map(c => `<span><i style="background:${c}"></i><small>${c.toUpperCase()}</small></span>`).join('')}</div><p class="font-caption">${design.font}</p></div><div class="notes-section"><h3>Ichida sinab ko‘ring</h3><ul><li>Kurs tafsiloti va ariza formasi</li><li>5 savollik kasb tanlash testi</li><li>Admin statistikasi va kurslar</li><li>Sotuvchida lid holati va izoh</li></ul></div><button class="choose-button ${chosen === design.id ? 'chosen' : ''}" data-action="choose">${icon(chosen === design.id ? 'check' : 'heart')} ${chosen === design.id ? 'Tanlangan dizayn' : 'Shu dizaynni tanlash'}</button><p class="notes-hint">Tanlovdan keyin variant raqamini chatga yozing.</p></aside><div class="device-area"><div class="device-caption"><span>${roleLabel()} paneli</span><span>Namuna ma’lumotlari</span></div><div class="device-frame" id="device-frame"><div class="telegram-bar"><span>9:41</span><span class="dynamic-island"></span><span class="phone-signals">▮▮▮ &nbsp; ▰</span></div><div class="telegram-title"><span>${icon('close')}</span><strong>ITLive Academy <small>mini app</small></strong><span>•••</span></div><div id="app" class="app theme-${design.id}"></div></div><p class="device-footer">${icon('shield')} Haqiqiy bot va mijozlar bazasiga ulanmagan.</p></div></div>`;
  renderApp();
}
function roleLabel() { return role === 'admin' ? 'Admin' : role === 'sales' ? 'Sotuvchi' : 'Foydalanuvchi'; }
function readChoice() { try { return localStorage.getItem('itlive-design-choice'); } catch { return null; } }

function appHeader() {
  return `<header class="app-header"><a href="#" data-page="home" class="app-brand">${icon('code')}<span>itlive<span>.</span><small>${role === 'user' ? 'academy' : role === 'admin' ? 'boshqaruv' : 'sotuv bo‘limi'}</small></span></a><button class="avatar" data-action="profile" aria-label="${roleLabel()} profili">${role === 'admin' ? 'AD' : role === 'sales' ? 'ST' : 'ME'}</button></header>`;
}
function nav() {
  const items = role === 'user' ? [['home', 'home', 'Asosiy'], ['courses', 'book', 'Kurslar'], ['applications', 'files', 'Arizalarim'], ['more', 'grid', 'Yana']]
    : role === 'admin' ? [['home', 'chart', 'Umumiy'], ['leads', 'files', 'Lidlar'], ['courses', 'book', 'Kurslar'], ['team', 'users', 'Jamoa'], ['more', 'grid', 'Yana']]
    : [['home', 'chart', 'Umumiy'], ['leads', 'files', 'Lidlar'], ['more', 'user', 'Profil']];
  return `<nav class="app-nav" aria-label="${roleLabel()} navigatsiyasi">${items.map(([p, ico, label]) => `<button data-page="${p}" class="${page === p ? 'active' : ''}" ${page === p ? 'aria-current="page"' : ''}>${icon(ico)}<span>${label}</span></button>`).join('')}</nav>`;
}
function renderApp() {
  const app = document.querySelector('#app');
  if (!app) return;
  app.innerHTML = `${appHeader()}<div class="app-content">${pageContent()}</div>${nav()}`;
  if (!embedded) document.querySelector('.device-caption span').textContent = `${roleLabel()} paneli`;
}
function pageContent() {
  if (page === 'courses') return coursesPage();
  if (page === 'applications') return applicationsPage();
  if (page === 'leads' && role !== 'user') return leadsPage();
  if (page === 'team' && role === 'admin') return teamPage();
  if (page === 'more') return morePage();
  return role === 'user' ? userHome() : dashboard();
}
function sectionTitle(title, link = 'Barchasi', target = 'courses') {
  return `<div class="section-title"><h3>${title}</h3><button data-page="${target}">${link} ${icon('arrow')}</button></div>`;
}
function courseCard(c, layout = 'row') {
  return `<button class="course-card ${layout}" data-course="${c.id}"><span class="course-icon tint-${c.tint}">${icon(c.icon)}</span><span class="course-copy"><strong>${esc(c.name)}</strong><small>${esc(c.tech)}</small><span class="course-meta">${icon('clock')}${c.duration}<span>${c.price} <small>so‘m / oy</small></span></span></span><span class="course-go">${icon('arrow')}</span></button>`;
}
function quickLinks() {
  return `<div class="quick-links"><button data-action="trial"><span>${icon('gift')}</span><strong>Sinov darsi</strong><small>Bepul qatnashing</small></button><button data-action="quiz"><span>${icon('spark')}</span><strong>Kasb testi</strong><small>Yo‘nalish tanlang</small></button><button data-action="contacts"><span>${icon('pin')}</span><strong>Bog‘lanish</strong><small>Bizni toping</small></button></div>`;
}
function userHome() {
  const shared = `<div class="home-greeting"><span>Salom, bo‘lajak mutaxassis!</span><span class="tiny-dot">ITLive bilan</span></div>`;
  if (design.id === 'pulse') return `${shared}<section class="hero hero-pulse"><div class="hero-copy"><span class="hero-pill">Kelajakka birinchi qadam</span><h1>ITdagi yo‘lingiz<br>shu yerdan boshlanadi.</h1><p>O‘zingizga mos kasbni tanlang.<br>Qolganini birga o‘rganamiz.</p><button class="hero-button" data-page="courses">Kurslarni ko‘rish ${icon('arrow')}</button></div><div class="pulse-art" aria-hidden="true"><span class="pulse-tile tile-one">${icon('code')}</span><span class="pulse-tile tile-two">${icon('palette')}</span><span class="pulse-tile tile-three">${icon('mobile')}</span><span class="orbit-line"></span></div></section>${quickLinks()}${sectionTitle('Ommabop kurslar')}${courses.slice(0, 3).map(c => courseCard(c)).join('')}<div class="quiet-banner">${icon('shield')}<span>Amaliy bilim. Tajribali mentor. Yangi imkoniyat.</span></div>`;
  if (design.id === 'midnight') return `<div class="terminal-status"><i></i> ITLive learning environment <span>v.2026</span></div><section class="hero hero-midnight"><span class="terminal-line"><span>const</span> yourFuture =</span><h1>Build.<br>Learn.<br><span>Become.</span></h1><p>Birinchi kodingizdan<br>birinchi loyihangizgacha.</p><button class="hero-button" data-page="courses">O‘rganishni boshlash ${icon('arrow')}</button><div class="code-orb" aria-hidden="true">&lt;/&gt;</div></section><div class="terminal-divider"><span>// yo‘nalishingizni tanlang</span><b>07 kurs</b></div><div class="course-grid midnight-courses">${courses.slice(0, 4).map(c => courseCard(c, 'tile')).join('')}</div><button class="quiz-strip" data-action="quiz">${icon('spark')}<span>Qaysi IT kasbi sizga mos?<small>5 savol orqali aniqlang</small></span>${icon('arrow')}</button>`;
  if (design.id === 'campus') return `<section class="hero hero-campus"><div class="campus-kicker"><span>Yangi bilim. Yangi siz.</span>${icon('spark')}</div><h1>O‘Z<br>YO‘LINGIZNI<br>YARATING<span>*</span></h1><div class="campus-bottom"><p>IT kasblari.<br>Real imkoniyatlar.</p><button data-page="courses" class="round-arrow" aria-label="Kurslarni ko‘rish">${icon('arrow')}</button></div><div class="campus-sticker">O‘rgan.<br>Yarat.<br>O‘s.</div></section><div class="campus-ticker"><span>Dasturlash</span><b>✳</b><span>Dizayn</span><b>✳</b><span>Kelajak</span></div>${sectionTitle('Nimadan boshlaymiz?')}<div class="campus-course-list">${courses.slice(0, 3).map((c, i) => `<button data-course="${c.id}"><span>0${i + 1}</span><strong>${c.name}</strong>${icon('arrow')}</button>`).join('')}</div><button class="quiz-strip" data-action="trial">${icon('gift')}<span>Sinab ko‘ring. Bepul.<small>Birinchi darsga yoziling</small></span>${icon('arrow')}</button>`;
  if (design.id === 'studio') return `<section class="hero hero-studio"><span class="studio-kicker">Bilimga yangi nigoh</span><h1>Kelajagingizni<br>loyihalang.</h1><p>Texnologiya va ijod uchrashgan joyda<br>sizning yangi kasbingiz boshlanadi.</p><div class="studio-composition"><div class="studio-ring" aria-hidden="true"></div><div class="studio-label">O‘z salohiyatingizni<br>kashf eting.</div><span class="studio-seal" aria-hidden="true">${icon('spark')}</span></div><button class="hero-button" data-page="courses">Yo‘nalishlarni kashf etish ${icon('arrow')}</button></section><div class="studio-editorial"><span>Qiziqishdan kasbgacha</span><span>ITLive Academy</span></div>${sectionTitle('Tanlangan yo‘nalishlar')}${[courses[3], courses[1]].map(c => courseCard(c)).join('')}<button class="quiz-strip" data-action="quiz">${icon('spark')}<span>Sizning kuchli tomoningiz qaysi?<small>Kasb tanlash testi</small></span>${icon('arrow')}</button>`;
  if (design.id === 'atlas') return `${shared}<section class="hero hero-atlas"><div><span class="hero-pill">Ta’limga aniq yo‘l</span><h1>Maqsad sari,<br>bir qadamdan.</h1><p>Yangi kasbni o‘rganish uchun<br>hammasi bir joyda.</p></div><div class="atlas-path" aria-hidden="true"><span>1</span><i></i><span>2</span><i></i><span>${icon('check')}</span></div><button class="hero-button" data-page="courses">Yo‘nalishimni tanlayman ${icon('arrow')}</button></section><div class="learning-path"><div><b>1</b><span>Kurs tanlang</span></div><div><b>2</b><span>Sinab ko‘ring</span></div><div><b>3</b><span>O‘rganing</span></div></div>${sectionTitle('Kurslar katalogi')}<div class="atlas-courses">${courses.slice(0, 4).map(c => courseCard(c)).join('')}</div><button class="quiz-strip" data-action="quiz">${icon('target')}<span>Hali yo‘nalish tanlamadingizmi?<small>Qisqa test yordam beradi</small></span>${icon('arrow')}</button>`;
  return `<section class="hero hero-orbit"><span class="hero-pill">Bugun boshlang</span><h1>Kichik qadam.<br>Katta kelajak.</h1><p>Yangi kasbingiz —<br>yangi imkoniyatlaringiz.</p><button class="hero-button" data-page="courses">O‘zimga mos kurs ${icon('arrow')}</button><div class="orbit-sculpture" aria-hidden="true"><i></i><b></b><span>${icon('spark')}</span></div></section><div class="orbit-bento"><button data-action="trial" class="orbit-trial">${icon('gift')}<strong>Birinchi dars?<br>Bizdan.</strong><span>Bepul yozilish ${icon('arrow')}</span></button><button data-action="quiz" class="orbit-quiz">${icon('spark')}<strong>Kasbingizni<br>toping.</strong><span>5 savollik test ${icon('arrow')}</span></button></div>${sectionTitle('Siz uchun yo‘nalishlar')}<div class="orbit-course-grid">${courses.slice(0, 2).map(c => courseCard(c, 'tile')).join('')}</div>`;
}

function dashboard() {
  const count = status => leads.filter(l => l.status === status).length;
  return `<div class="page-heading"><div><p>${role === 'admin' ? 'Boshqaruv markazi' : 'Sotuvlar markazi'}</p><h1>${role === 'admin' ? 'Hammasi nazoratda.' : 'Har bir lid — imkoniyat.'}</h1></div><span class="dashboard-date">17 noyabr <small>Namuna kuni</small></span></div><div class="demo-inline">${icon('help')} Quyidagi ko‘rsatkichlar sun’iy namuna.</div><section class="stats-grid"><article class="stat-card stat-primary"><span>${icon('files')} Jami arizalar</span><strong>${leads.length}</strong><small>Ko‘rgazmadagi barcha arizalar</small><div class="stat-sparkline" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div></article><article class="stat-card"><span>${icon('clock')} Yangi</span><strong>${count('YANGI')}</strong><small>Ko‘rib chiqish kutilmoqda</small></article><article class="stat-card"><span>${icon('phone')} Bog‘lanildi</span><strong>${count('BOGLANILDI')}</strong><small>Muloqot davom etmoqda</small></article><article class="stat-card"><span>${icon('check')} O‘qishga yozildi</span><strong>${count('YOZILDI')}</strong><small>Muvaffaqiyatli arizalar</small></article></section><section class="analytics-card"><div class="section-title"><h3>Yo‘nalishlar bo‘yicha</h3><span class="subtle">Namuna</span></div>${courses.slice(0, 4).map(c => { const n = leads.filter(l => l.course === c.name).length; return `<div class="bar-row"><span>${c.name}</span><b>${n}</b><div class="bar-track"><i style="width:${n / Math.max(leads.length, 1) * 100}%"></i></div></div>`; }).join('')}</section>${sectionTitle('So‘nggi arizalar', 'Barchasi', 'leads')}<div class="lead-list">${leads.slice(0, 3).map(leadRow).join('')}</div>${role === 'admin' ? `<div class="admin-shortcuts"><button class="outline-button" data-action="export">${icon('download')} Namuna CSV</button><button class="outline-button" data-action="broadcast">${icon('send')} Xabarnoma</button></div>` : ''}`;
}
function leadRow(l) {
  return `<button class="lead-row" data-lead="${l.id}"><span class="lead-avatar">${l.initials}</span><span class="lead-copy"><strong>${esc(l.name)}</strong><small>${esc(l.course)}</small>${badge(l.status)}</span><span class="lead-time">${l.time}${icon('arrow')}</span></button>`;
}
function leadsPage() {
  const filtered = leads.filter(l => (leadFilter === 'ALL' || l.status === leadFilter) && `${l.name} ${l.course} ${l.id}`.toLowerCase().includes(search.toLowerCase()));
  return `<div class="page-heading"><div><p>Arizalar boshqaruvi</p><h1>Lidlar <span class="count-pill">${leads.length}</span></h1></div>${role === 'admin' ? `<button class="icon-button" data-action="export" aria-label="Namuna CSV yuklab olish">${icon('download')}</button>` : ''}</div><label class="search-field">${icon('search')}<input id="lead-search" type="search" placeholder="Ism, kurs yoki ariza raqami" aria-label="Lidlarni qidirish" value="${esc(search)}"></label><div class="filter-tabs" aria-label="Holat bo‘yicha saralash">${[['ALL', 'Barchasi'], ['YANGI', 'Yangi'], ['BOGLANILDI', 'Bog‘lanildi'], ['YOZILDI', 'Yozildi'], ['BEKOR_QILINDI', 'Bekor']].map(([s, label]) => `<button class="${leadFilter === s ? 'active' : ''}" data-filter="${s}" aria-pressed="${leadFilter === s}">${label}</button>`).join('')}</div><div class="list-caption"><span>${filtered.length} ta ariza</span><span>Namuna ma’lumotlari</span></div><div class="lead-list" id="lead-results">${filtered.length ? filtered.map(leadRow).join('') : emptyState('Mos ariza topilmadi', 'Boshqa so‘z yoki holatni tanlab ko‘ring.')}</div>`;
}
function coursesPage() {
  const admin = role === 'admin';
  const available = courses.filter(c => admin || c.active);
  const filtered = available.filter(c => courseFilter === 'Barchasi' || c.category === courseFilter);
  return `<div class="page-heading"><div><p>${admin ? 'Ta’lim yo‘nalishlari' : 'O‘zingizga mosini tanlang'}</p><h1>${admin ? 'Kurslar boshqaruvi' : 'Yangi kasbingiz shu yerda.'}</h1></div></div>${admin ? `<button class="primary-button full-width" data-action="add-course">${icon('plus')} Kurs qo‘shish</button>` : `<button class="trial-banner" data-action="trial">${icon('gift')}<span>Avval sinab ko‘ring<small>Birinchi dars — bepul</small></span>${icon('arrow')}</button>`}<div class="filter-tabs">${['Barchasi', 'Dasturlash', 'Dizayn', 'Xavfsizlik', 'Boshlang‘ich', 'Marketing'].map(c => `<button data-category="${c}" aria-pressed="${courseFilter === c}" class="${courseFilter === c ? 'active' : ''}">${c}</button>`).join('')}</div><div class="list-caption"><span>${filtered.length} ta yo‘nalish</span><span>${admin ? 'Namuna katalog' : 'Amaliy ta’lim'}</span></div><div class="course-catalog">${filtered.map(c => admin ? `<article class="admin-course">${courseCard(c)}<div class="admin-course-actions"><span class="badge ${c.active ? 'status-yozildi' : 'status-bekor_qilindi'}">${c.active ? 'Faol' : 'Yashirilgan'}</span><button class="text-button" data-toggle-course="${c.id}">${c.active ? 'Yashirish' : 'Faollashtirish'}</button><button class="text-button" data-edit-course="${c.id}">Tahrirlash</button></div></article>` : courseCard(c)).join('')}</div>`;
}
function applicationsPage() {
  const own = leads.filter(l => l.own);
  return `<div class="page-heading"><div><p>O‘qish sari bir qadam</p><h1>Mening arizalarim</h1></div></div><p class="page-subtitle">Yuborgan arizalaringiz va ularning joriy holati.</p>${own.length ? own.map(l => `<article class="application-card"><div class="section-title"><span>#${l.id}</span>${badge(l.status)}</div><h3>${esc(l.course)}</h3><p>Afzal vaqt: ${esc(l.preference || 'Kechki')}</p><div class="application-timeline"><span class="done">${icon('check')} Ariza qabul qilindi</span><span class="${l.status !== 'YANGI' ? 'done' : ''}">${icon('phone')} Admin bilan bog‘lanish</span></div><button class="outline-button full-width" data-action="contacts">${icon('phone')} Savolim bor</button></article>`).join('') : emptyState('Hali arizangiz yo‘q', 'Kurs tanlang va birinchi arizangizni qoldiring.')}<button class="primary-button full-width" data-page="courses">${icon('plus')} Yangi kursga yozilish</button>`;
}
function emptyState(title, text) { return `<div class="empty-state">${icon('files')}<h3>${title}</h3><p>${text}</p></div>`; }
function menuItem(action, ico, title, text) { return `<button class="menu-item" data-action="${action}"><span>${icon(ico)}</span><span><strong>${title}</strong><small>${text}</small></span>${icon('arrow')}</button>`; }
function morePage() {
  if (role === 'admin') return `<div class="page-heading"><div><p>Admin uchun</p><h1>Boshqaruv vositalari</h1></div></div><div class="menu-list">${menuItem('broadcast', 'send', 'Ommaviy xabarnoma', 'Matn, rasm yoki video')}${menuItem('settings', 'settings', 'Markaz sozlamalari', 'Manzil, kontakt va havolalar')}${menuItem('feedbacks', 'mail', 'Fikr va takliflar', 'Kelgan murojaatlar')}${menuItem('export', 'download', 'Namuna CSV eksport', 'Haqiqiy appda Excel bo‘ladi')}</div><div class="demo-card">${icon('shield')}<p>Bu dizayn ko‘rgazmasi. O‘zgarishlar faqat shu sahifada ko‘rinadi va botga yuborilmaydi.</p></div>`;
  if (role === 'sales') return `<div class="page-heading"><div><p>Sotuvchi kabineti</p><h1>Ish joyingiz</h1></div></div><div class="profile-card"><span class="avatar">ST</span><h3>Namuna sotuvchi</h3><p>Sotuv bo‘limi</p><span class="badge status-yozildi">Faol</span></div><div class="menu-list">${menuItem('sales-help', 'help', 'Lidlar bilan ishlash', 'Holatni yangilash va izoh yozish')}${menuItem('contacts', 'phone', 'Markaz bilan bog‘lanish', 'Qo‘llab-quvvatlash')}</div>`;
  return `<div class="page-heading"><div><p>ITLive siz bilan</p><h1>Yana nimalar bor?</h1></div></div><div class="menu-list">${menuItem('quiz', 'spark', 'IT kasb tanlash testi', '5 savol, sizga mos yo‘nalish')}${menuItem('trial', 'gift', 'Bepul sinov darsi', 'Avval tanishing, keyin tanlang')}${menuItem('mentors', 'users', 'Mentorlar', 'Tajriba ulashadigan jamoa')}${menuItem('discounts', 'heart', 'Aksiya va chegirmalar', 'O‘qish uchun qulay imkoniyatlar')}${menuItem('contacts', 'pin', 'Manzil va bog‘lanish', 'Bizni topish oson')}${menuItem('about', 'book', 'ITLive haqida', 'Markaz va ta’lim yondashuvi')}${menuItem('faq', 'help', 'Savol-javoblar', 'Ko‘p so‘raladigan savollar')}${menuItem('feedback', 'mail', 'Fikr va taklif', 'Sizni eshitishga tayyormiz')}</div>`;
}
function teamPage() {
  return `<div class="page-heading"><div><p>Sotuvlar jamoasi</p><h1>Birga ishlaymiz.</h1></div></div><button class="primary-button full-width" data-action="add-sales">${icon('plus')} Sotuvchi qo‘shish</button><div class="list-caption"><span>${team.length} ta sotuvchi</span><span>Namuna</span></div>${team.map((p, i) => `<article class="team-card"><span class="lead-avatar">S${i + 1}</span><div><strong>${esc(p.name)}</strong><small>${esc(p.id)}</small><span class="badge status-yozildi">Faol</span></div><button class="text-button" data-remove-sales="${i}">Olib tashlash</button></article>`).join('')}`;
}

function showCourse(id) {
  const c = courses.find(c => c.id === Number(id));
  if (!c) return;
  openModal(c.name, `<div class="course-detail-art tint-${c.tint}">${icon(c.icon)}<span>${esc(c.category)}</span></div><p class="detail-description">${esc(c.description)}</p><div class="detail-facts"><div><span>Davomiyligi</span><strong>${esc(c.duration)}</strong></div><div><span>Oylik to‘lov</span><strong>${esc(c.price)} so‘m</strong></div></div><h3>Nimalarni o‘rganasiz?</h3><p class="tech-chips">${c.tech.split(' · ').map(t => `<span>${esc(t)}</span>`).join('')}</p><div class="detail-benefits"><p>${icon('check')} Amaliy loyihalar orqali ta’lim</p><p>${icon('check')} Tajribali mentor yordami</p><p>${icon('check')} Boshlashdan oldin bepul sinov darsi</p></div><button class="primary-button full-width" data-enroll="${c.id}">Kursga yozilish ${icon('arrow')}</button>${role === 'admin' ? `<button class="outline-button full-width spaced" data-edit-course="${c.id}">Kursni tahrirlash</button>` : ''}`);
}
function registration(courseId, trial = false) {
  const c = courses.find(c => c.id === Number(courseId));
  openModal(trial ? 'Bepul sinov darsiga yozilish' : 'Kursga yozilish', `<p class="form-intro">${trial ? 'Birinchi darsda ta’lim bilan tanishing.' : 'Ma’lumotlaringizni qoldiring, siz bilan bog‘lanamiz.'}</p><div class="form-notice">Bu namuna forma. Ma’lumotlar serverga yuborilmaydi.</div><form id="enroll-form"><label>Ism va familiya<input name="name" required minlength="3" maxlength="100" autocomplete="name" placeholder="Ism va familiyangiz"></label><label>Telefon raqamingiz<input name="phone" required type="tel" pattern="[+]998[0-9]{9}" placeholder="+998901234567" autocomplete="tel"><small>+998 va 9 ta raqam. Namuna uchun o‘ylab topilgan ma’lumot ishlating.</small></label><div class="form-grid"><label>Yoshingiz<input name="age" type="number" required min="7" max="90" placeholder="18"></label><label>Hududingiz<select name="region"><option>Toshkent shahri</option><option>Toshkent viloyati</option><option>Samarqand</option><option>Farg‘ona</option><option>Andijon</option><option>Namangan</option><option>Buxoro</option><option>Qashqadaryo</option><option>Surxondaryo</option><option>Jizzax</option><option>Sirdaryo</option><option>Navoiy</option><option>Xorazm</option><option>Qoraqalpog‘iston</option><option>Boshqa hudud</option></select></label></div><label>Qiziqqan kursingiz<select name="course">${courses.filter(c => c.active).map(x => `<option value="${x.id}" ${x.id === c?.id ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select></label><label>Qulay vaqt<select name="preference"><option>Ertalab</option><option>Tushdan keyin</option><option>Kechki</option><option>Farqi yo‘q</option></select></label><button class="primary-button full-width" type="submit">Namuna ariza yuborish ${icon('send')}</button></form>`);
}
const quiz = [
  { q: 'Sizga qaysi jarayon ko‘proq zavq bag‘ishlaydi?', options: [['Mantiqiy masalalar va serverlar', 'backend'], ['Sayt va foydalanuvchi interfeysi', 'frontend'], ['Qulay mobil ilovalar yaratish', 'mobile'], ['Ranglar, rasmlar va brend dizayni', 'design']] },
  { q: 'Matematika va mantiqqa qiziqishingiz qanday?', options: [['Algoritmlar va hisob-kitobni yoqtiraman', 'backend'], ['Amaliy va vizual natijani ko‘rmoqchiman', 'frontend'], ['Tizimlarni himoyalash qiziqtiradi', 'security'], ['Ijodiy g‘oyalar menga yaqinroq', 'design']] },
  { q: 'Qaysi natija bilan ko‘proq faxrlanardingiz?', options: [['To‘xtovsiz ishlaydigan to‘lov tizimi', 'backend'], ['Ko‘pchilik ishlatadigan mobil ilova', 'mobile'], ['Tez va qulay zamonaviy sayt', 'frontend'], ['Taniqli brendning vizual ko‘rinishi', 'design']] },
  { q: 'Qaysi vazifa sizga mosroq?', options: [['Chuqur kod va arxitektura yaratish', 'backend'], ['Mahsulotning qulayligini loyihalash', 'design'], ['Interaktiv mahsulotni tez chiqarish', 'frontend'], ['Kiberhujumlar oldini olish', 'security']] },
  { q: 'IT sohasini qanday maqsadda o‘rganmoqchisiz?', options: [['Xalqaro masofaviy ish', 'backend'], ['O‘z startapimni boshlash', 'mobile'], ['Talabgir kasb egasi bo‘lish', 'frontend'], ['Ijodiy loyihalar bilan erkin ishlash', 'design']] },
];
function showQuiz() {
  const q = quiz[quizStep];
  openModal('Sizga qaysi IT kasbi mos?', `<div class="quiz-progress"><span>${quizStep + 1} / 5 savol</span><span>${Math.round(quizStep / 5 * 100)}%</span><i><b style="width:${quizStep / 5 * 100}%"></b></i></div><h3 class="quiz-question">${q.q}</h3><div class="quiz-options">${q.options.map(([label, value], i) => `<button data-quiz-answer="${value}"><span>${String.fromCharCode(65 + i)}</span>${label}${icon('arrow')}</button>`).join('')}</div><p class="form-intro">To‘g‘ri yoki noto‘g‘ri javob yo‘q. O‘zingizga yaqinini tanlang.</p>`);
}
function showLead(id) {
  if (role === 'user') return;
  const l = leads.find(l => l.id === Number(id));
  if (!l) return;
  openModal(`Ariza #${l.id}`, `<div class="lead-detail-heading"><span class="lead-avatar">${l.initials}</span><div><h3>${esc(l.name)}</h3>${badge(l.status)}</div></div><dl class="lead-facts"><div><dt>Kurs</dt><dd>${esc(l.course)}</dd></div><div><dt>Telefon</dt><dd>Namuna ma’lumoti</dd></div><div><dt>Hudud</dt><dd>Toshkent shahri</dd></div><div><dt>Vaqt</dt><dd>${esc(l.preference || 'Kechki')}</dd></div></dl><form id="lead-form" data-id="${l.id}"><label>Ariza holati<select name="status">${Object.entries(statuses).map(([key, label]) => `<option value="${key}" ${l.status === key ? 'selected' : ''}>${label}</option>`).join('')}</select></label><label>Sotuvchi izohi<textarea name="note" rows="3" maxlength="2000" placeholder="Suhbat tafsilotlarini yozing">${esc(l.note)}</textarea></label><button class="primary-button full-width" type="submit">${icon('check')} Namunada saqlash</button></form><p class="form-intro">O‘zgarish statistikada ham aks etadi. Botga yuborilmaydi.</p>`);
}
function courseForm(id) {
  if (role !== 'admin') return;
  const c = courses.find(c => c.id === Number(id));
  openModal(c ? 'Kursni tahrirlash' : 'Yangi kurs qo‘shish', `<form id="course-form" data-id="${c?.id || ''}"><label>Kurs nomi<input name="name" required maxlength="100" value="${esc(c?.name || '')}" placeholder="Masalan: Python Backend"></label><label>Tavsif<textarea name="description" required rows="3" maxlength="2000">${esc(c?.description || '')}</textarea></label><div class="form-grid"><label>Davomiyligi<input name="duration" required maxlength="30" value="${esc(c?.duration || '')}" placeholder="6 oy"></label><label>Oylik narxi (so‘m)<input name="price" required inputmode="numeric" maxlength="30" value="${esc(c?.price || '')}" placeholder="1 200 000"></label></div><label>Texnologiyalar<input name="tech" required maxlength="300" value="${esc(c?.tech || '')}" placeholder="Python · Django · SQL"></label><button type="submit" class="primary-button full-width">${icon('check')} Namunada saqlash</button></form>${c ? `<button class="danger-button full-width spaced" data-delete-course="${c.id}">Kursni namunadan o‘chirish</button>` : ''}`);
}
function showAction(action) {
  if (action === 'close') return closeModal();
  if (action === 'trial') return registration(null, true);
  if (action === 'quiz') { quizStep = 0; quizScores = {}; return showQuiz(); }
  if (action === 'choose') {
    try { localStorage.setItem('itlive-design-choice', design.id); } catch { /* Selection still works without browser storage. */ }
    const b = document.querySelector('.choose-button');
    if (b) b.innerHTML = `${icon('check')} Tanlangan dizayn`;
    return openModal('Dizayn tanlandi', `<div class="choice-confirmation"><div class="choice-number">${design.number}</div><h3>${design.name}</h3><p>${design.tagline}</p><p>Tanlov shu brauzerda saqlandi. Endi chatga <strong>“${design.number} — ${design.name}”</strong> deb yozing. Keyingi bosqichda shu uslubda to‘liq mini app quriladi.</p><button class="primary-button full-width" data-action="close">Ko‘rishni davom ettirish</button></div>`);
  }
  if (action === 'profile') return openModal(roleLabel() + ' profili', `<div class="profile-card"><span class="avatar">${role === 'admin' ? 'AD' : role === 'sales' ? 'ST' : 'ME'}</span><h3>Namuna ${roleLabel().toLowerCase()}</h3><p>Dizaynni sinash uchun yaratilgan profil.</p></div><div class="form-notice">Haqiqiy mini appda shaxs Telegram orqali aniqlanadi. Admin va sotuvchi ruxsatlari serverda tekshiriladi.</div>`);
  if (action === 'contacts') return openModal('Biz bilan bog‘laning', `<div class="map-preview">${icon('pin')}<span>ITLive Academy</span><small>Xarita uchun namuna joy</small><div class="map-grid"></div></div><div class="contact-block"><h3>Markaz kontaktlari</h3><p>Haqiqiy manzil, ish vaqti va telefonlar bot sozlamalaridan olinadi.</p><div class="info-row">${icon('clock')}<span>Dushanba – Shanba, 09:00–20:00<small>Namuna ish vaqti</small></span></div></div><button class="primary-button full-width" data-action="feedback">Savol qoldirish ${icon('mail')}</button>`);
  if (action === 'about') return openModal('ITLive Academy haqida', `<div class="about-mark">${icon('code')} itlive.</div><h3>Texnologiyani amalda o‘rganamiz.</h3><p class="detail-description">ITLive — dasturlash, dizayn va raqamli kasblarni o‘rganish uchun ta’lim markazi.</p><div class="detail-benefits"><p>${icon('check')} Amaliyotga yo‘naltirilgan darslar</p><p>${icon('check')} Tajribali mentorlar</p><p>${icon('check')} Loyihalar va portfolio</p></div><button class="primary-button full-width" data-action="trial">Bepul sinov darsiga yozilish</button>`);
  if (action === 'mentors') return openModal('Tajriba ulashadigan mentorlar', `<p class="form-intro">Maket uchun namuna yo‘nalishlar. Haqiqiy mentor ma’lumotlari keyin ulanadi.</p>${[['PB', 'Backend mentori', 'Python, Django, API'], ['FE', 'Frontend mentori', 'JavaScript, React'], ['UX', 'Dizayn mentori', 'Figma, UI/UX']].map(([a, n, t]) => `<div class="mentor-row"><span class="lead-avatar">${a}</span><div><h3>${n}</h3><p>${t}</p></div>${icon('check')}</div>`).join('')}`);
  if (action === 'discounts') return openModal('Aksiya va chegirmalar', `<article class="offer-card">${icon('gift')}<h3>Birinchi dars — bepul</h3><p>Kursni tanlashdan oldin ta’lim bilan tanishing.</p><button class="primary-button full-width" data-action="trial">Sinov darsiga yozilish</button></article><p class="form-intro">Boshqa amaldagi chegirmalar va shartlar botdagi sozlamalardan ko‘rsatiladi.</p>`);
  if (action === 'faq') return openModal('Ko‘p so‘raladigan savollar', `<div class="faq-list">${[['Boshlang‘ich bilim kerakmi?', 'Boshlang‘ich kurslar noldan boshlovchilar uchun. Yo‘nalish tanlashda markaz sizga yordam beradi.'], ['Darslarni avval sinab ko‘rsam bo‘ladimi?', 'Bepul sinov darsiga ariza qoldirishingiz mumkin.'], ['Qaysi kursni tanlashni bilmayapman.', '5 savollik kasb testini sinab ko‘ring yoki maslahat uchun murojaat qoldiring.'], ['O‘qish vaqtlari qanday?', 'Arizada o‘zingizga qulay vaqtni belgilang. Guruh jadvali markaz bilan kelishiladi.']].map(([q, a]) => `<details><summary>${q}${icon('plus')}</summary><p>${a}</p></details>`).join('')}</div><button class="outline-button full-width spaced" data-action="feedback">Boshqa savolim bor</button>`);
  if (action === 'feedback') return openModal('Fikr va taklifingiz', `<p class="form-intro">Ta’lim, kurslar yoki xizmatimiz haqida yozing.</p><form id="feedback-form"><label>Xabaringiz<textarea name="message" required minlength="5" maxlength="4000" rows="5" placeholder="Fikringizni yozing..."></textarea></label><button class="primary-button full-width" type="submit">${icon('send')} Namunada yuborish</button></form><p class="form-intro">Bu forma haqiqiy xabar yubormaydi.</p>`);
  if (action === 'sales-help') return openModal('Lidlar bilan ishlash', `<div class="detail-benefits"><p>${icon('files')} Lidlar sahifasidan arizani tanlang.</p><p>${icon('phone')} Mijoz bilan bog‘langach holatini yangilang.</p><p>${icon('mail')} Suhbat natijasini izohga yozing.</p><p>${icon('check')} Saqlang — statistika yangilanadi.</p></div>`);
  if (role !== 'admin') return;
  if (action === 'add-course') return courseForm();
  if (action === 'export') {
    const csv = '\ufeff' + [['Ariza', 'Ism', 'Kurs', 'Holat', 'Izoh'], ...leads.map(l => [l.id, l.name, l.course, statuses[l.status], l.note])].map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
    const a = document.createElement('a'); a.href = url; a.download = 'itlive-namuna-lidlar.csv'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    return toast('Namuna CSV tayyor. To‘liq appda Excel eksport bo‘ladi.');
  }
  if (action === 'add-sales') return openModal('Sotuvchi qo‘shish', `<form id="sales-form"><label>Ism va familiya<input name="name" required minlength="3" maxlength="100" placeholder="Namuna sotuvchi"></label><label>Telegram ID<input name="id" required inputmode="numeric" pattern="[0-9]{5,16}" placeholder="123456789"></label><button type="submit" class="primary-button full-width">${icon('plus')} Namunaga qo‘shish</button></form>`);
  if (action === 'broadcast') return openModal('Ommaviy xabarnoma', `<div class="form-notice">Faqat xabarning ko‘rinishini tayyorlaydi. Hech kimga yuborilmaydi.</div><form id="broadcast-form"><label>Xabar matni<textarea name="message" rows="5" required maxlength="4000" placeholder="Yangi kurs boshlanmoqda..."></textarea></label><label>Rasm yoki video (ixtiyoriy)<input name="media" type="file" accept="image/*,video/*"></label><button class="primary-button full-width" type="submit">${icon('send')} Xabarni ko‘rib chiqish</button></form>`);
  if (action === 'settings') return openModal('Markaz sozlamalari', `<form id="settings-form"><label>Markaz nomi<input name="center" required maxlength="100" value="ITLive Academy"></label><label>Telefon raqam<input name="phone" type="tel" placeholder="+998..."></label><label>Manzil<textarea name="address" rows="2" placeholder="Markaz manzili"></textarea></label><label>Ish vaqti<input name="hours" value="Dushanba – Shanba, 09:00–20:00"></label><label>Instagram havolasi<input type="url" name="instagram" placeholder="https://instagram.com/..."></label><button type="submit" class="primary-button full-width">${icon('check')} Namunada saqlash</button></form><p class="form-intro">Haqiqiy appda barcha bot sozlamalari shu yerda bo‘ladi.</p>`);
  if (action === 'feedbacks') return openModal('Fikr va takliflar', `<article class="feedback-message"><span class="badge">Namuna</span><h3>Namuna foydalanuvchi</h3><p>Frontend kursi haqida batafsil ma’lumot bersangiz.</p><small>Bugun, 10:30</small></article>`);
}

document.addEventListener('click', event => {
  const target = event.target.closest('button, a');
  if (!target) return;
  if (target.dataset.page) {
    event.preventDefault(); page = target.dataset.page; search = ''; renderApp();
    document.querySelector('.app-content')?.scrollTo(0, 0);
  } else if (target.dataset.role) {
    role = target.dataset.role; page = 'home';
    const url = new URL(location.href); url.searchParams.set('role', role); history.replaceState(null, '', url);
    document.querySelectorAll('[data-role]').forEach(b => { b.classList.toggle('active', b.dataset.role === role); b.setAttribute('aria-pressed', String(b.dataset.role === role)); });
    renderApp();
  } else if (target.dataset.device) {
    const desktop = target.dataset.device === 'desktop';
    document.querySelector('.viewer-stage').classList.toggle('desktop-view', desktop);
    document.querySelectorAll('[data-device]').forEach(b => { b.classList.toggle('active', b === target); b.setAttribute('aria-pressed', String(b === target)); });
  } else if (target.dataset.course) showCourse(target.dataset.course);
  else if (target.dataset.enroll) registration(target.dataset.enroll);
  else if (target.dataset.lead) showLead(target.dataset.lead);
  else if (target.dataset.filter) { leadFilter = target.dataset.filter; renderApp(); }
  else if (target.dataset.category) { courseFilter = target.dataset.category; renderApp(); }
  else if (target.dataset.action) showAction(target.dataset.action);
  else if (target.dataset.quizAnswer) {
    const value = target.dataset.quizAnswer;
    quizScores[value] = (quizScores[value] || 0) + 1;
    quizStep++;
    if (quizStep < quiz.length) return showQuiz();
    const winner = Object.entries(quizScores).sort((a, b) => b[1] - a[1])[0][0];
    const c = courses.find(c => c.id === ({ backend: 1, frontend: 2, mobile: 3, design: 4, security: 5 }[winner]));
    openModal('Sizning yo‘nalishingiz', `<div class="quiz-result"><span class="result-icon">${icon(c.icon)}</span><p>Javoblaringizga ko‘ra</p><h3>${c.name}</h3><p>${c.description}</p><small>Bu tavsiya tanishuv uchun. Yakuniy tanlov sizniki.</small><button class="primary-button full-width spaced" data-course="${c.id}">Kurs bilan tanishish ${icon('arrow')}</button><button class="text-button spaced" data-action="quiz">Testni qayta boshlash</button></div>`);
  } else if (target.dataset.toggleCourse && role === 'admin') { const c = courses.find(c => c.id === Number(target.dataset.toggleCourse)); c.active = !c.active; renderApp(); toast('Kurs holati namunada yangilandi.'); }
  else if (target.dataset.editCourse) courseForm(target.dataset.editCourse);
  else if (target.dataset.deleteCourse && role === 'admin') {
    const c = courses.find(c => c.id === Number(target.dataset.deleteCourse));
    openModal('Kursni namunadan o‘chirish', `<p><strong>${esc(c.name)}</strong> namuna katalogidan olib tashlanadi. Sahifani yangilash orqali tiklash mumkin.</p><button class="danger-button full-width" data-confirm-delete="${c.id}">Namunadan o‘chirish</button><button class="outline-button full-width spaced" data-action="close">Bekor qilish</button>`);
  } else if (target.dataset.confirmDelete && role === 'admin') { const i = courses.findIndex(c => c.id === Number(target.dataset.confirmDelete)); if (i >= 0) courses.splice(i, 1); closeModal(); renderApp(); toast('Kurs namunadan o‘chirildi.'); }
  else if (target.hasAttribute('data-remove-sales') && role === 'admin') { team.splice(Number(target.dataset.removeSales), 1); renderApp(); toast('Sotuvchi namunadan olib tashlandi.'); }
});
document.addEventListener('change', event => {
  if (event.target.id === 'design-select') location.href = `?design=${event.target.value}&role=${role}`;
});
document.addEventListener('input', event => {
  if (event.target.id === 'lead-search') {
    search = event.target.value;
    const filtered = leads.filter(l => (leadFilter === 'ALL' || l.status === leadFilter) && `${l.name} ${l.course} ${l.id}`.toLowerCase().includes(search.toLowerCase()));
    document.querySelector('#lead-results').innerHTML = filtered.length ? filtered.map(leadRow).join('') : emptyState('Mos ariza topilmadi', 'Boshqa so‘z yoki holatni tanlab ko‘ring.');
    document.querySelector('.list-caption span').textContent = `${filtered.length} ta ariza`;
  }
});
document.addEventListener('submit', event => {
  const form = event.target;
  if (!(form instanceof HTMLFormElement)) return;
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form));
  if (form.id === 'enroll-form') {
    const c = courses.find(c => c.id === Number(data.course));
    const id = Math.max(1042, ...leads.map(l => l.id)) + 1;
    leads.unshift({ id, name: data.name, initials: data.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase(), course: c.name, status: 'YANGI', time: 'Hozir', note: '', own: true, preference: data.preference });
    openModal('Namuna ariza qabul qilindi', `<div class="success-state"><span>${icon('check')}</span><h3>Yaxshi boshlanish!</h3><p>${esc(c.name)} bo‘yicha namuna arizangiz yaratildi.</p><p>Uni “Arizalarim” bo‘limida ko‘rishingiz mumkin. Haqiqiy ariza yuborilmadi.</p><button class="primary-button full-width" data-action="close">Tayyor</button></div>`);
    renderApp();
  } else if (form.id === 'lead-form' && role !== 'user') {
    const l = leads.find(l => l.id === Number(form.dataset.id));
    if (!statuses[data.status]) return;
    l.status = data.status; l.note = data.note; closeModal(); renderApp(); toast('Holat va izoh namunada saqlandi.');
  } else if (form.id === 'course-form' && role === 'admin') {
    const existing = courses.find(c => c.id === Number(form.dataset.id));
    if (existing) Object.assign(existing, data);
    else courses.push({ ...data, id: Math.max(0, ...courses.map(c => c.id)) + 1, category: 'Dasturlash', icon: 'code', tint: 'blue', active: true });
    closeModal(); renderApp(); toast('Kurs namunada saqlandi.');
  } else if (form.id === 'sales-form' && role === 'admin') { team.push(data); closeModal(); renderApp(); toast('Sotuvchi namunaga qo‘shildi.'); }
  else if (form.id === 'broadcast-form' && role === 'admin') {
    const file = form.elements.media.files[0];
    openModal('Xabarnoma ko‘rinishi', `<div class="broadcast-preview">${file ? `<div class="form-notice">${icon('files')} ${esc(file.name)} <small>Tanlangan fayl yuklanmadi.</small></div>` : ''}<p>${esc(data.message).replace(/\n/g, '<br>')}</p><small>ITLive Academy</small></div><div class="form-notice">Xabar hech kimga yuborilmadi. Haqiqiy appda qabul qiluvchilar soni va yuborish tasdig‘i bo‘ladi.</div><button class="primary-button full-width" data-action="close">Tayyor</button>`);
  } else if (form.id === 'feedback-form') { closeModal(); toast('Fikringiz namunada qabul qilindi. Haqiqiy xabar yuborilmadi.'); }
  else if (form.id === 'settings-form' && role === 'admin') { closeModal(); toast('Sozlamalar ko‘rinishi sinab ko‘rildi. Bot sozlamalari o‘zgarmadi.'); }
});
modal.addEventListener('click', event => { if (event.target === modal) { const r = modal.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeModal(); } });

if (embedded && design) {
  document.body.className = 'embed-body';
  root.innerHTML = `<div id="app" class="app theme-${design.id}"></div>`;
  renderApp();
} else if (design) renderViewer();
else renderGallery();
