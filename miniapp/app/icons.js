const iconPaths = {
  code: '<path d="m8 7-5 5 5 5m8-10 5 5-5 5m-3-14-2 18"/>',
  home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
  book: '<path d="M12 5v16M3 3c4-1 7 0 9 2 2-2 5-3 9-2v16c-4-1-7 0-9 2-2-2-5-3-9-2z"/>',
  files:
    '<rect x="6" y="3" width="14" height="17" rx="2"/><path d="M3 7v13a3 3 0 0 0 3 3m4-15h6m-6 4h6m-6 4h4"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
  back: '<path d="m14 6-6 6 6 6"/>',
  down: '<path d="m6 9 6 6 6-6"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  spark:
    '<path d="m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3z"/>',
  users:
    '<circle cx="9" cy="8" r="3"/><path d="M2 21v-3a7 7 0 0 1 14 0v3m0-17a3 3 0 0 1 0 6m4 11v-3a7 7 0 0 0-3-6"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
  chart: '<path d="M3 3v18h18M7 16v-4m5 4V7m5 9V4"/>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9m-12 9h12m-9 3a3 3 0 0 0 6 0"/>',
  search: '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  phone:
    '<path d="m5 3 4 1 1 5-3 2a15 15 0 0 0 6 6l2-3 5 1 1 4c0 2-2 3-4 2C9 20 4 15 3 7c-1-2 0-4 2-4z"/>',
  pin: '<path d="M19 10c0 6-7 11-7 11S5 16 5 10a7 7 0 0 1 14 0z"/><circle cx="12" cy="10" r="2"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>',
  gift: '<path d="M3 9h18v4H3zm2 4v8h14v-8M12 9v12m0-12C5 9 4 2 8 3c3 0 4 6 4 6s1-6 4-6c4-1 3 6-4 6"/>',
  help: '<circle cx="12" cy="12" r="9"/><path d="M9 9a3 3 0 0 1 6 0c0 2-3 2-3 5m0 3h.01"/>',
  heart:
    '<path d="M20 5a5 5 0 0 0-8 1 5 5 0 0 0-8-1c-5 6 8 15 8 15s13-9 8-15z"/>',
  settings:
    '<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3"/><circle cx="15" cy="17" r="3"/>',
  send: '<path d="m22 2-7 20-4-9-9-4zM11 13 22 2"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  laptop:
    '<rect x="4" y="3" width="16" height="12" rx="2"/><path d="m4 15-3 5h22l-3-5"/>',
  mobile:
    '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/>',
  shield:
    '<path d="m12 2 9 4v6c0 6-9 10-9 10S3 18 3 12V6z"/><path d="m8 12 3 3 5-6"/>',
  palette:
    '<path d="M12 3a9 9 0 1 0 0 18h1c3 0 3-3 1-4-2-2 0-4 2-3h2c5 0 3-11-6-11z"/><path d="M7 10h.01M10 6h.01M15 7h.01M6 14h.01"/>',
  target:
    '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  globe:
    '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
  external: '<path d="M14 3h7v7m0-7L10 14M10 3H3v18h18v-7"/>',
};
export const icon = (name, cls = "") =>
  `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name] || iconPaths.code}</svg>`;
export const esc = (s = "") =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
