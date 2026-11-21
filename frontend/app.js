'use strict';

/* Buildless bilingual frontend. Selected guides are educational references. */
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const safeStore = {
  get(key, fallback) { try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; } }
};
let lang = safeStore.get('cc-language', 'en');
if (!['en', 'bn'].includes(lang)) lang = 'en';
let reports = safeStore.get('cc-observations-v2', []);
if (!Array.isArray(reports)) reports = [];
reports = reports.filter(r => r && r.mode === 'guide' && DISEASES.some(d => d.id === r.disease) && typeof r.id === 'string' && Number.isFinite(Date.parse(r.date))).slice(0, 100);
let tasks = safeStore.get('cc-tasks', [false, false, false]);
tasks = Array.from({ length: 3 }, (_, i) => Array.isArray(tasks) && tasks[i] === true);
let route = 'dashboard', filter = 'all', query = '', file = null, preview = '', result = null;
let analyzing = false, runId = 0, uploadId = 0, lastFocus = null;
let selection = DISEASES[0].id, fieldNote = '';
const L = (en, bn) => lang === 'bn' ? bn : en;
const A = value => value[lang === 'bn' ? 1 : 0];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const n = value => new Intl.NumberFormat(lang === 'bn' ? 'bn-BD' : 'en-US').format(value);
const date = value => new Intl.DateTimeFormat(lang === 'bn' ? 'bn-BD' : 'en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Asia/Dhaka' }).format(new Date(value));
const projectTitle = () => 'AI-Based Crop Disease Detection and Smart Farming Assistance System';

const API_BASE = (() => {
  const configured = String(window.CROPCARE_API_BASE || '').trim().replace(/\/+$/, '');
  if (configured) return configured;

  // When the frontend is opened through a local static dev server (for example :5501),
  // send API requests to the local FastAPI server. In production, use the same origin.
  const isLocalHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  if (isLocalHost && window.location.port && window.location.port !== '8000') {
    return 'http://127.0.0.1:8000';
  }
  return '';
})();

let historyPageNumber = 1;
const HISTORY_PAGE_SIZE = 10;
const icons = {
  leaf: 'M20 4C8 2 3 8 5 15c4 9 16 2 15-11ZM4 21 16 9m-7 7-1-5m5 1 5-1',
  grid: 'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
  scan: 'M8 3H3v5m13-5h5v5M3 16v5h5m8 0h5v-5M7 12h10m-5-5v10',
  book: 'M12 5C8 2 3 3 3 3v16s5-1 9 2m0-16c4-3 9-2 9-2v16s-5-1-9 2V5',
  chart: 'M4 3v18h17M8 16v-4m5 4V7m5 9v-6',
  file: 'M14 3H5v18h14V8l-5-5Zm0 0v5h5M8 12h8m-8 4h5',
  help: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm-3-12a3 3 0 1 1 5 2c-2 1-2 2-2 3m0 3h.01',
  arrow: 'M4 12h15m-6-6 6 6-6 6', upload: 'M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6',
  camera: 'M3 7h4l2-3h6l2 3h4v14H3V7Zm9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z',
  check: 'm5 12 4 4L19 6', search: 'M10 17a7 7 0 1 0 0-14 7 7 0 0 0 0 14Zm5-2 6 6',
  calendar: 'M4 5h16v16H4V5Zm3-3v6m10-6v6M4 10h16',
  sun: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm0-6v2m0 16v2M2 12h2m16 0h2M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2',
  info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-10v6m0-10h.01',
  globe: 'M3 12h18M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 0c-5 6-5 12 0 18 5-6 5-12 0-18Z',
  menu: 'M3 6h18M3 12h18M3 18h18', close: 'm6 6 12 12M6 18 18 6',
  download: 'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4',
  trash: 'M3 6h18M6 6l1 15h10l1-15M9 6V3h6v3m-5 4v7m4-7v7',
  clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-14v5l4 2',
  shield: 'm12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6',
  database: 'M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3Zm0 0v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6m-16 6c0 1.7 3.6 3 8 3s8-1.3 8-3',
  spark: 'm12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z'
};
const icon = key => `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${icons[key] || icons.leaf}"/></svg>`;
const navs = [
  ['dashboard', 'grid', ['Overview', 'সংক্ষিপ্ত চিত্র']],
  ['diagnose', 'scan', ['AI crop diagnosis', 'AI ফসল রোগ শনাক্তকরণ']],
  ['history', 'chart', ['AI prediction history', 'AI পূর্বাভাসের ইতিহাস']],
  ['library', 'book', ['Disease library', 'রোগের তথ্যভান্ডার']],
  ['reports', 'file', ['Field notes', 'মাঠের নোট']],
  ['research', 'book', ['Research results', 'গবেষণার ফলাফল']],
  ['about', 'help', ['About the system', 'সিস্টেম পরিচিতি']]
];
const btn = (label, action, style = '', ico = 'arrow') => `<button class="btn ${style}" data-action="${action}">${label}${icon(ico)}</button>`;
const cropOf = disease => CROP_DATA.find(c => c.id === disease.crop);
const motionEnabled = () => safeStore.get('cc-motion', true) && !matchMedia('(prefers-reduced-motion: reduce)').matches;

function shell() {
  document.documentElement.lang = lang;
  document.title = projectTitle();
  $('#sidebar').innerHTML = `
    <a class="brand" href="#dashboard"><img src="assets/logo.svg" alt=""><div><strong>CropCare <span>AI</span></strong><small>${L('SMART FARMING RESEARCH', 'স্মার্ট কৃষি গবেষণা')}</small></div></a>
    <div class="nav-label">${L('YOUR WORKSPACE', 'আপনার কর্মক্ষেত্র')}</div>
    <nav class="nav" aria-label="${L('Main navigation', 'প্রধান নেভিগেশন')}">${navs.map(([id, i, t]) => `<a href="#${id}" class="${route === id ? 'active' : ''}" ${route === id ? 'aria-current="page"' : ''}>${icon(i)}${A(t)}${id === 'reports' ? `<span class="count">${n(reports.length)}</span>` : ''}</a>`).join('')}</nav>
    <div class="sidebar-bottom">
      <div class="sidebar-note"><div class="sprout">${icon('leaf')}</div><h3>${L('Small steps.<br>Healthier crops.', 'ছোট পদক্ষেপে<br>সুস্থ ফসল।')}</h3><p>${L('Every healthy harvest starts with a closer look.', 'ভালো ফলনের শুরু ফসলের প্রতি একটু বাড়তি নজর থেকে।')}</p><a href="#diagnose">${L('Start an observation', 'পর্যবেক্ষণ শুরু করুন')}${icon('arrow')}</a></div>
      <a class="project-signature" href="#about">${icon('spark')}<strong>${projectTitle()}</strong></a>
    </div>`;
  $('#topbar').innerHTML = `
    <button class="menu-button" data-action="menu" aria-label="${L('Open navigation', 'মেনু খুলুন')}" aria-controls="sidebar" aria-expanded="false">${icon('menu')}</button>
    <div class="crumb"><span>${L('Workspace', 'কর্মক্ষেত্র')}</span><span>/</span><b>${A(navs.find(x => x[0] === route)[2])}</b></div>
    <div class="top-actions"><a class="top-search" href="#library" aria-label="${L('Find a crop guide', 'ফসলের গাইড খুঁজুন')}">${icon('search')}<span>${L('Find a crop guide', 'ফসলের গাইড খুঁজুন')}</span></a>
    <button class="motion-toggle" data-action="motion" aria-pressed="${motionEnabled()}" aria-label="${L('Toggle animation effects', 'অ্যানিমেশন চালু বা বন্ধ করুন')}" title="${L('Animation effects', 'অ্যানিমেশন')}">${icon('spark')}</button>
    <div class="language" role="group" aria-label="${L('Website language', 'ওয়েবসাইটের ভাষা')}"><button data-lang="en" lang="en" class="${lang === 'en' ? 'selected' : ''}" aria-pressed="${lang === 'en'}">EN</button><button data-lang="bn" lang="bn" class="${lang === 'bn' ? 'selected' : ''}" aria-pressed="${lang === 'bn'}">বাংলা</button></div></div>`;
}
function head(title, sub, extra = '') {
  return `<div class="page-head"><div><div class="section-kicker">${L('AI CROP HEALTH / RESEARCH SYSTEM', 'AI ফসল স্বাস্থ্য / গবেষণা সিস্টেম')}</div><h1>${title}</h1><p>${sub}</p></div>${extra || `<span class="date">${icon('calendar')}${date(new Date())}</span>`}</div>`;
}
function cropCards() {
  return CROP_DATA.map(c => `<a class="crop-card" href="#library/${c.id}"><div class="photo"><img src="assets/${c.image}" alt="${A(c.name)}" loading="lazy"><span>${L('CROP GUIDE', 'ফসলের গাইড')}</span></div><div class="crop-info"><div><h3>${A(c.name)}</h3><small>${A(c.desc)}</small></div><span class="arrow-circle">${icon('arrow')}</span></div></a>`).join('');
}
function checklist() {
  const labels = [['Look closely at both sides of leaves', 'পাতার দুই পাশ ভালোভাবে দেখুন'], ['Photograph any new spots or changes', 'নতুন দাগ বা পরিবর্তনের ছবি তুলুন'], ['Keep a dated record of observations', 'তারিখসহ পর্যবেক্ষণ লিখে রাখুন']];
  return `<div class="panel-head"><div><h2>${L('Your field checklist', 'মাঠ পর্যবেক্ষণের তালিকা')}</h2><p>${L('A little attention goes a long way', 'নিয়মিত নজরদারিতে ফসলের যত্ন')}</p></div><span class="panel-icon">${icon('sun')}</span></div><div class="task-list">${labels.map((x, i) => `<label class="task"><input type="checkbox" data-task="${i}" ${tasks[i] ? 'checked' : ''}><span>${A(x)}</span></label>`).join('')}</div><div class="progress-track"><span style="width:${tasks.filter(Boolean).length / 3 * 100}%"></span></div><div class="task-foot"><span>${n(tasks.filter(Boolean).length)} / ${n(3)} ${L('completed', 'সম্পন্ন')}</span><button class="link" data-action="reset-tasks">${L('Reset', 'রিসেট')}</button></div>`;
}
function dashboard() {
  return head(projectTitle(), L('A research-driven smart farming workspace for crop disease prediction, explainability and field guidance.', 'ফসলের রোগ শনাক্তকরণ, ব্যাখ্যাযোগ্যতা ও মাঠপর্যায়ের তথ্যের জন্য গবেষণাভিত্তিক স্মার্ট ফার্মিং Workspace।')) + `
    <div class="hero"><section class="hero-main"><img src="assets/field.jpg" alt="${L('Lush green paddy field in Bangladesh', 'বাংলাদেশের সবুজ ধানক্ষেত')}"><div class="hero-orbit" aria-hidden="true"><span></span><i></i></div><div class="hero-copy"><span class="eyebrow">${L('SMARTER CARE, FROM THE FIRST LEAF', 'পাতার প্রথম লক্ষণ থেকেই যত্ন')}</span><h2>${L('AI-based crop disease detection.<br><em>Smarter farming decisions.</em>', 'AI-ভিত্তিক ফসলের রোগ শনাক্তকরণ।<br><em>স্মার্ট কৃষি সিদ্ধান্ত।</em>')}</h2><p>${L('Explore crop symptoms, capture a clear photo, and keep your next steps close at hand.', 'ফসলের লক্ষণ চিনুন, পরিষ্কার ছবি তুলুন এবং প্রয়োজনীয় করণীয় হাতের কাছে রাখুন।')}</p><a class="btn lime" href="#diagnose">${icon('scan')}${L('Check your crop', 'ফসল পরীক্ষা করুন')}${icon('arrow')}</a></div><div class="hero-stamp">${icon('leaf')}${L('ROOTED IN BETTER CARE', 'সচেতন চাষির সঙ্গী')}</div></section>
    <aside class="hero-side"><span class="eyebrow">${L('THE FIELD NOTE', 'মাঠের কথা')}</span><div class="field-note-number">01 <span>/ ${L('GROW BETTER', 'ভালো ফলন')}</span></div><h3>${L('Look early.<br>Act thoughtfully.', 'আগে দেখুন।<br>বুঝে ব্যবস্থা নিন।')}</h3><p>${L('Similar symptoms can have different causes. A clear photo helps you discuss what you see with an expert.', 'একই লক্ষণের ভিন্ন কারণ হতে পারে। পরিষ্কার ছবি নিয়ে কৃষি বিশেষজ্ঞের সঙ্গে আলোচনা করুন।')}</p><a class="field-note-link" href="#library">${L('Explore crop care', 'ফসলের যত্ন জানুন')}${icon('arrow')}</a><div class="note-leaf" aria-hidden="true">${icon('leaf')}</div></aside></div>
    <div class="stats">${[['leaf', '39', L('Trained model classes', 'প্রশিক্ষিত Model Class')], ['chart', '98.86%', L('Recorded test accuracy', 'নথিভুক্ত Test Accuracy')], ['scan', '300×300', L('Model input size', 'Model Input Size')], ['database', 'PostgreSQL', L('Prediction history store', 'Prediction History Database')]].map(([i, v, t]) => `<div class="stat"><span class="stat-icon">${icon(i)}</span><div><b>${v}</b><small>${t}</small></div><span class="stat-spark">↗</span></div>`).join('')}</div>
    <section class="panel section ai-overview-panel"><div class="panel-head"><div><h2>${L('Live research system status', 'লাইভ গবেষণা সিস্টেমের অবস্থা')}</h2><p>${L('Backend, trained model and database connectivity', 'Backend, Trained Model ও Database Connection')}</p></div><span class="badge" id="dashboard-api-status">${L('Checking…', 'যাচাই হচ্ছে…')}</span></div><div class="ai-status-grid"><div><small>FastAPI</small><b id="dashboard-api-detail">Checking</b></div><div><small>EfficientNet-B3</small><b>39 classes</b></div><div><small>PostgreSQL</small><b id="dashboard-db-detail">Checking</b></div><div><small>Explainability</small><b>Grad-CAM</b></div></div><div class="actions"><a class="btn" href="#diagnose">${L('Start AI diagnosis', 'AI রোগ শনাক্তকরণ শুরু করুন')}${icon('arrow')}</a><a class="btn outline" href="#history">${L('Open prediction history', 'Prediction History খুলুন')}${icon('chart')}</a></div></section>
    <div class="grid-main"><section class="panel"><div class="panel-head"><div><h2>${L('Start with a leaf photo', 'শুরু করুন পাতার ছবি দিয়ে')}</h2><p>${L('A simple space to observe, learn and keep notes', 'পর্যবেক্ষণ, তথ্য ও নোট রাখার সহজ জায়গা')}</p></div><span class="panel-icon">${icon('scan')}</span></div><div class="upload-preview"><div class="upload-icon">${icon('upload')}</div><div><h3>${L('Something unusual on your crop?', 'ফসলে অস্বাভাবিক কিছু দেখছেন?')}</h3><p>${L('JPG, PNG or WebP · up to 10 MB', 'JPG, PNG বা WebP · সর্বোচ্চ ১০ মেগাবাইট')}</p><a class="btn small" href="#diagnose">${L('Upload a photo', 'ছবি আপলোড করুন')}${icon('arrow')}</a></div></div><div class="workflow">${[[1, L('Add a photo', 'ছবি দিন')], [2, L('Explore a guide', 'গাইড দেখুন')], [3, L('Save your notes', 'নোট রাখুন')]].map(([v, t], i) => `${i ? '<i></i>' : ''}<div><span>${n(v)}</span>${t}</div>`).join('')}</div></section><section class="panel" id="checklist">${checklist()}</section></div>
    <section class="section"><div class="section-head"><div><h2>${L('Know your crops', 'আপনার ফসল সম্পর্কে জানুন')}</h2><p>${L('Practical guides for the plants you grow', 'চাষ করা ফসলের প্রয়োজনীয় গাইড')}</p></div><a class="link" href="#library">${L('All guides', 'সব গাইড')}${icon('arrow')}</a></div><div class="crop-grid">${cropCards()}</div></section>
    <div class="bottom-grid section"><section class="panel"><div class="panel-head"><h2>${L('Recent observations', 'সাম্প্রতিক পর্যবেক্ষণ')}</h2><a class="link" href="#reports">${L('View all', 'সব দেখুন')}${icon('arrow')}</a></div>${reports.length ? reports.slice(0, 2).map(r => reportRow(r, true)).join('') : `<div class="empty">${icon('file')}<h3>${L('Your crop story starts here', 'এখানেই শুরু আপনার ফসলের গল্প')}</h3><p>${L('Save a guide with your notes to build an observation history.', 'গাইডের সঙ্গে নোট রেখে পর্যবেক্ষণের ইতিহাস তৈরি করুন।')}</p></div>`}</section><aside class="tip"><div>${icon('camera')}</div><div><h3>${L('A better photo. A better starting point.', 'ভালো ছবি, ভালোভাবে বোঝার শুরু।')}</h3><p>${L('Use natural light. Fill the frame with one leaf. Keep the affected area sharp and include both sides when possible.', 'প্রাকৃতিক আলো ব্যবহার করুন। একটি পাতা ফ্রেমে রাখুন। আক্রান্ত অংশ স্পষ্ট করুন; সম্ভব হলে দুই পাশের ছবি নিন।')}</p><a class="link" href="#diagnose">${L('See photo tips', 'ছবি তোলার পরামর্শ')}${icon('arrow')}</a></div></aside></div>`;
}
function diagnose() {
  return head(
    L('AI-powered crop disease detection', 'AI-ভিত্তিক ফসলের রোগ শনাক্তকরণ'),
    L('Upload a leaf image and analyze it with the trained EfficientNet-B3 research model.', 'পাতার ছবি আপলোড করে প্রশিক্ষিত EfficientNet-B3 গবেষণা মডেল দিয়ে বিশ্লেষণ করুন।')
  ) + `
    <div class="service-note ai-note">${icon('info')}<span>${L(
      'The model predicts one of 39 PlantVillage classes. Results are decision-support information, not a confirmed field diagnosis. Background-class predictions are rejected as non-leaf inputs.',
      'মডেলটি PlantVillage-এর ৩৯টি ক্লাসের একটি পূর্বাভাস দেয়। ফলাফল সিদ্ধান্তে সহায়ক তথ্য, নিশ্চিত মাঠ-পর্যায়ের রোগ নির্ণয় নয়। Background ক্লাস এলে সেটিকে রোগ নির্ণয় হিসেবে দেখানো হবে না।'
    )}</span></div>
    <div class="ai-service-status" id="ai-service-status">${L('Checking backend and model status…', 'ব্যাকএন্ড ও মডেলের অবস্থা যাচাই হচ্ছে…')}</div>
    <div class="diagnose-grid">
      <section class="panel">
        <div class="panel-head">
          <h2>${L('01 · Upload a crop leaf image', '০১ · ফসলের পাতার ছবি আপলোড করুন')}</h2>
          <span class="badge neutral">${icon('shield')}${L('Private upload', 'নিরাপদ আপলোড')}</span>
        </div>
        <div class="upload-zone" id="dropzone">
          ${preview
            ? `<img src="${preview}" alt="${L('Selected crop image preview', 'নির্বাচিত ফসলের ছবির প্রিভিউ')}"><small>${esc(file?.name || L('Sample leaf image', 'নমুনা পাতার ছবি'))}</small>`
            : `<div class="upload-icon">${icon('upload')}</div><h3>${L('Drop your leaf photo here', 'পাতার ছবি এখানে ছাড়ুন')}</h3><p>${L('or choose a photo from your device', 'অথবা ডিভাইস থেকে ছবি বাছুন')}</p>`}
          <button class="btn outline small" data-action="choose">${icon('upload')}${L('Choose image', 'ছবি বাছুন')}</button>
          <small class="muted">JPG, PNG, WebP, BMP · ${L('maximum 10 MB', 'সর্বোচ্চ ১০ মেগাবাইট')}</small>
        </div>
        <input class="hidden" id="image-input" type="file" accept="image/jpeg,image/png,image/webp,image/bmp">
        <input class="hidden" id="camera-input" type="file" accept="image/jpeg,image/png,image/webp,image/bmp" capture="environment">
        <div class="file-row">
          ${btn(L('Use sample photo', 'নমুনা ছবি ব্যবহার করুন'), 'sample', 'light', 'leaf')}
          ${btn(L('Use camera', 'ক্যামেরা ব্যবহার করুন'), 'camera', 'outline', 'camera')}
        </div>
        <div class="field">
          <label class="small-label" for="field-note">${L('02 · Field notes', '০২ · মাঠের পর্যবেক্ষণ')} <span class="muted">${L('(optional)', '(ঐচ্ছিক)')}</span></label>
          <textarea id="field-note" rows="2" maxlength="500" placeholder="${L('Crop name, location or symptoms you observed…', 'ফসলের নাম, স্থান বা যে লক্ষণ দেখেছেন…')}">${esc(fieldNote)}</textarea>
        </div>
        <div class="field">
          <button class="btn full" data-action="analyze" ${analyzing || !file ? 'disabled' : ''}>
            ${icon('scan')}${analyzing ? L('Analyzing image…', 'ছবি বিশ্লেষণ হচ্ছে…') : L('Analyze with AI model', 'AI মডেল দিয়ে বিশ্লেষণ করুন')}
          </button>
        </div>
        <p class="muted ai-model-foot">${L('Model: EfficientNet-B3 · 39 classes · 300 × 300 input · ImageNet normalization', 'মডেল: EfficientNet-B3 · ৩৯ ক্লাস · ৩০০ × ৩০০ ইনপুট · ImageNet normalization')}</p>
      </section>
      <section class="panel" id="result-panel" aria-live="polite">
        ${result ? resultHTML(result) : waitingHTML()}
      </section>
    </div>
    <section class="section panel">
      <div class="panel-head"><h2>${L('How to capture a useful leaf image', 'কার্যকর পাতার ছবি তোলার নিয়ম')}</h2>${icon('camera')}</div>
      <div class="team">
        ${[
          [L('Use natural, even light', 'প্রাকৃতিক ও সমান আলো ব্যবহার করুন'), L('Avoid harsh shadows and flash reflections.', 'তীব্র ছায়া ও ফ্ল্যাশের প্রতিফলন এড়িয়ে চলুন।')],
          [L('Focus on one leaf', 'একটি পাতায় ফোকাস করুন'), L('Keep the leaf sharp and the background simple.', 'পাতাটি স্পষ্ট রাখুন এবং পেছনের অংশ সহজ রাখুন।')],
          [L('Follow up with field inspection', 'মাঠে পর্যবেক্ষণ করুন'), L('Compare the predicted class with visible symptoms and local expert advice.', 'দৃশ্যমান লক্ষণ ও স্থানীয় কৃষি বিশেষজ্ঞের পরামর্শের সঙ্গে পূর্বাভাস মিলিয়ে দেখুন।')]
        ].map(([t, p]) => `<div><h3>${t}</h3><p>${p}</p></div>`).join('')}
      </div>
    </section>`;
}
function waitingHTML() {
  return `<div class="panel-head"><h2>${L('Your crop workspace', 'আপনার ফসলের তথ্য')}</h2>${icon('leaf')}</div><div class="empty waiting-visual"><div class="leaf-orbit" aria-hidden="true"><span>${icon('leaf')}</span><i></i></div><h3>${L('Every leaf tells a story', 'প্রতিটি পাতায় ফসলের কথা')}</h3><p>${L('Add a photo and select a guide to bring your observations together.', 'ছবি ও গাইড বেছে পর্যবেক্ষণের তথ্য এক জায়গায় আনুন।')}</p></div><div class="analysis-steps">${[[1, L('Preview your leaf photo', 'পাতার ছবি দেখুন')], [2, L('Read symptoms and care', 'লক্ষণ ও পরিচর্যা জানুন')], [3, L('Save your field observation', 'মাঠের পর্যবেক্ষণ রাখুন')]].map(([v, t]) => `<div><span class="step-n">${n(v)}</span>${t}</div>`).join('')}</div><div class="waiting-foot">${icon('shield')}${L('Private photos. Source-linked guidance.', 'ব্যক্তিগত ছবি। সূত্রসহ তথ্য।')}</div>`;
}
function resultHTML(record) {
  const ai = record.ai || {};
  const info = ai.disease_info || {};
  const list = value => Array.isArray(value) ? value : [];
  const background = ai.diagnosis_status === 'background_rejected' || ai.is_background;
  const healthy = ai.is_healthy;
  const uncertain = ai.review_required && !background;
  const statusLabel = background
    ? L('Background rejected · no disease diagnosis', 'Background শনাক্ত · রোগ নির্ণয় করা হয়নি')
    : healthy
      ? L('Healthy class predicted', 'সুস্থ গাছের ক্লাস শনাক্ত')
      : uncertain
        ? L('Low / uncertain confidence · review required', 'কম / অনিশ্চিত Confidence · পুনরায় যাচাই প্রয়োজন')
        : L('Disease class predicted', 'রোগের ক্লাস শনাক্ত');
  const statusClass = background || uncertain ? 'warning' : 'success';
  const top = list(ai.top_5_predictions).map(item => `
    <div class="ai-prediction-row">
      <div class="ai-prediction-head"><strong>${item.rank}. ${esc(item.label)}</strong><b>${Number(item.confidence_percent).toFixed(2)}%</b></div>
      <div class="ai-progress"><span style="width:${Math.max(0, Math.min(100, Number(item.confidence_percent)))}%"></span></div>
    </div>`).join('');
  const infoBlock = background
    ? `<div class="notice amber"><h3>${L('Please upload a clear plant leaf photo', 'অনুগ্রহ করে পাতার পরিষ্কার ছবি দিন')}</h3><p>${L('The model selected its Background_without_leaves class. No disease name or treatment recommendation is issued for this image.', 'মডেল Background_without_leaves ক্লাস নির্বাচন করেছে। এই ছবির জন্য কোনো রোগের নাম বা চিকিৎসা পরামর্শ দেওয়া হচ্ছে না।')}</p></div>`
    : `<div class="ai-info-grid">
        <div class="result-block"><h3>${L('Symptoms to compare', 'যে লক্ষণগুলো মিলিয়ে দেখবেন')}</h3><ul>${list(info.symptoms).map(x => `<li>${esc(x)}</li>`).join('') || `<li>${L('No symptom details are available.', 'লক্ষণ সম্পর্কিত তথ্য নেই।')}</li>`}</ul></div>
        <div class="result-block"><h3>${L('Possible causes', 'সম্ভাব্য কারণ')}</h3><ul>${list(info.causes).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
        <div class="result-block"><h3>${L('Prevention', 'প্রতিরোধ')}</h3><ul>${list(info.prevention).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
        <div class="result-block"><h3>${L('Management guidance', 'ব্যবস্থাপনার পরামর্শ')}</h3><ul>${list(info.management).map(x => `<li>${esc(x)}</li>`).join('')}</ul></div>
      </div>
      <p class="result-context">${esc(info.note || L('Confirm the suspected disease with a local agricultural expert.', 'স্থানীয় কৃষি বিশেষজ্ঞের মাধ্যমে রোগ নিশ্চিত করুন।'))}</p>`;
  const gradcamBlock = record.gradcam ? `
    <div class="ai-gradcam">
      <h3>${L('Grad-CAM explainability', 'Grad-CAM ব্যাখ্যাযোগ্যতা')}</h3>
      <p>${L('The heatmap shows image regions that contributed to the selected model class. It is not proof of disease.', 'Heatmap-এ নির্বাচিত Model Class-এ অবদান রাখা ছবির অঞ্চল দেখানো হয়েছে। এটি রোগের প্রমাণ নয়।')}</p>
      <div class="ai-gradcam-grid">
        <figure><img src="${API_BASE}${record.gradcam.input_image_url}" alt="Model input crop"><figcaption>${L('Model input crop', 'মডেলের ইনপুট ছবি')}</figcaption></figure>
        <figure><img src="${API_BASE}${record.gradcam.heatmap_url}" alt="Grad-CAM heatmap"><figcaption>${L('Grad-CAM heatmap', 'Grad-CAM Heatmap')}</figcaption></figure>
        <figure><img src="${API_BASE}${record.gradcam.overlay_url}" alt="Grad-CAM overlay"><figcaption>${L('Overlay', 'ওভারলে')}</figcaption></figure>
      </div>
      <small>${L('Target layer:', 'Target Layer:')} ${esc(record.gradcam.target_layer || 'model.features[-1]')}</small>
    </div>` : `<div class="ai-gradcam"><h3>${L('Grad-CAM explainability', 'Grad-CAM ব্যাখ্যাযোগ্যতা')}</h3><p>${record.gradcam_pending ? L('Generating the model attention heatmap…', 'Model Attention Heatmap তৈরি হচ্ছে…') : L('Grad-CAM could not be generated for this request. The prediction remains available.', 'এই অনুরোধের জন্য Grad-CAM তৈরি করা যায়নি। Prediction ফলাফল পাওয়া যাচ্ছে।')}</p></div>`;
  return `
    <div class="panel-head"><h2>${L('AI analysis result', 'AI বিশ্লেষণের ফলাফল')}</h2><span class="badge ${statusClass}">${statusLabel}</span></div>
    <div class="ai-result-main">
      <span class="eyebrow">${esc(info.plant || L('Model prediction', 'মডেলের পূর্বাভাস'))}</span>
      <h2>${esc(ai.predicted_label || L('Prediction unavailable', 'পূর্বাভাস পাওয়া যায়নি'))}</h2>
      <p>${esc(info.type || ai.reliability_status || '')}</p>
      <div class="ai-confidence">${Number(ai.confidence_percent || 0).toFixed(2)}<small>%</small></div>
      <p class="muted">${L('Top-1 softmax score', 'Top-1 Softmax Score')} · ${L('Confidence margin', 'Confidence Margin')}: ${Number(ai.confidence_margin || 0).toFixed(2)} ${L('points', 'পয়েন্ট')}</p>
    </div>
    ${uncertain ? `<div class="notice amber">${L('The prediction did not meet the project’s provisional confidence and margin review thresholds. Retake the image or seek expert confirmation.', 'পূর্বাভাসটি প্রকল্পের প্রাথমিক Confidence ও Margin যাচাইয়ের সীমা পূরণ করেনি। নতুন ছবি তুলুন বা বিশেষজ্ঞের পরামর্শ নিন।')}</div>` : ''}
    <div class="result-block"><h3>${L('Top-5 model predictions', 'Top-5 Model Prediction')}</h3>${top}</div>
    ${infoBlock}
    ${gradcamBlock}
    <div class="ai-save-status">
      <span>${record.database_saved ? L('Saved to PostgreSQL history', 'PostgreSQL History-তে সংরক্ষিত') : L('Database save unavailable — prediction still completed', 'Database-এ সংরক্ষণ হয়নি — Prediction সম্পন্ন হয়েছে')}</span>
      <span>${esc(record.filename || '')}</span>
    </div>
    <div class="actions"><button class="btn" data-action="download">${L('Download AI report', 'AI রিপোর্ট ডাউনলোড')}${icon('download')}</button><a class="btn outline" href="#history">${L('View prediction history', 'Prediction History দেখুন')}${icon('arrow')}</a></div>
    <p class="result-context">${L('Research disclaimer: PlantVillage-trained models can be affected by lighting, background, camera quality and field conditions. Confirm important decisions with an agricultural officer.', 'গবেষণা সতর্কতা: আলো, পটভূমি, ক্যামেরার মান ও মাঠের পরিবেশে PlantVillage-প্রশিক্ষিত মডেলের ফল বদলাতে পারে। গুরুত্বপূর্ণ সিদ্ধান্ত কৃষি কর্মকর্তার সঙ্গে যাচাই করুন।')}</p>`;
}
function library() {
  return head(L('A field guide, always nearby', 'হাতের কাছেই ফসলের গাইড'), L('Explore common symptoms and source-backed prevention practices.', 'সাধারণ লক্ষণ ও সূত্রভিত্তিক প্রতিরোধের উপায় জানুন।')) + `<div class="toolbar"><div class="search-wrap">${icon('search')}<input class="input" id="disease-search" aria-label="${L('Search disease guides', 'রোগের গাইড খুঁজুন')}" placeholder="${L('Search crops, diseases or symptoms…', 'ফসল, রোগ বা লক্ষণ খুঁজুন…')}" value="${esc(query)}"></div><div class="filter">${[['all', L('All crops', 'সব ফসল')], ...CROP_DATA.map(c => [c.id, A(c.name)])].map(([v, t]) => `<button data-filter="${v}" class="${filter === v ? 'active' : ''}" aria-pressed="${filter === v}">${t}</button>`).join('')}</div></div><div class="service-note">${icon('info')}<span>${L('Photos illustrate the crop. Symptoms can overlap; confirm suspected disease with a local expert.', 'ছবিগুলো ফসল বোঝায়। একাধিক রোগের লক্ষণ মিলতে পারে; স্থানীয় বিশেষজ্ঞের মাধ্যমে নিশ্চিত করুন।')}</span></div><div class="disease-grid" id="disease-grid">${diseaseCards()}</div>`;
}
function diseaseCards() {
  const ds = DISEASES.filter(d => (filter === 'all' || d.crop === filter) && [...d.name, ...d.symptom, ...cropOf(d).name].join(' ').toLowerCase().includes(query.toLowerCase()));
  return ds.length ? ds.map(d => `<article class="disease-card"><img src="assets/${d.image}" alt="${A(cropOf(d).name)} — ${L('crop illustration', 'ফসলের ছবি')}" loading="lazy"><div class="body"><span class="badge neutral">${A(cropOf(d).name)}</span><h3>${A(d.name)}</h3><p>${A(d.symptom)}</p><button class="link" data-disease="${d.id}">${L('Symptoms & care', 'লক্ষণ ও যত্ন')}${icon('arrow')}</button><div class="meta">${A(d.type)}</div></div></article>`).join('') : `<div class="empty"><h3>${L('No matching guides', 'মিল পাওয়া যায়নি')}</h3><p>${L('Try another crop or a shorter search.', 'অন্য ফসল বা ছোট শব্দ দিয়ে খুঁজুন।')}</p></div>`;
}
function reportRow(record, compact = false) {
  const d = DISEASES.find(x => x.id === record.disease);
  return `<div class="report-row"><span class="report-icon">${icon('file')}</span><div><h3>${A(d.name)} · ${A(cropOf(d).name)}</h3><small>${date(record.date)} · ${L('Saved observation', 'সংরক্ষিত পর্যবেক্ষণ')}</small></div><div class="actions"><button class="btn small light" data-report="${esc(record.id)}">${L('View', 'দেখুন')}</button>${compact ? '' : `<button class="btn small outline" data-export="${esc(record.id)}" aria-label="${L('Download report', 'রিপোর্ট ডাউনলোড')}">${icon('download')}</button><button class="btn small danger" data-delete="${esc(record.id)}" aria-label="${L('Delete report', 'রিপোর্ট মুছুন')}">${icon('trash')}</button>`}</div></div>`;
}
function reportsPage() {
  const counts = CROP_DATA.map(c => reports.filter(r => DISEASES.find(d => d.id === r.disease).crop === c.id).length);
  const max = Math.max(1, ...counts);
  return head(L('Your observation journal', 'আপনার পর্যবেক্ষণের খাতা'), L('Your saved notes and reference guides, organised in one place.', 'সংরক্ষিত নোট ও তথ্যের গাইড—গুছিয়ে এক জায়গায়।'), reports.length ? btn(L('Export all', 'সব ডাউনলোড'), 'export-all', 'outline', 'download') : '') + `<div class="service-note">${icon('shield')}<span>${L('Records stay in this browser. Photos are not saved. The chart counts your observations, not confirmed disease cases.', 'রেকর্ড এই ব্রাউজারে থাকে। ছবি সংরক্ষিত হয় না। চার্ট পর্যবেক্ষণের সংখ্যা দেখায়, নিশ্চিত রোগের সংখ্যা নয়।')}</span></div><div class="grid-main"><section class="panel"><div class="panel-head"><h2>${L('Saved reports', 'সংরক্ষিত রিপোর্ট')} <span class="muted">(${n(reports.length)})</span></h2><a class="link" href="#diagnose">${L('New observation', 'নতুন পর্যবেক্ষণ')} +</a></div>${reports.length ? reports.map(r => reportRow(r)).join('') : `<div class="empty">${icon('file')}<h3>${L('No observations saved yet', 'এখনো পর্যবেক্ষণ রাখা হয়নি')}</h3><p>${L('Open a crop guide, add your notes and save an observation.', 'ফসলের গাইড খুলে নোটসহ পর্যবেক্ষণ রাখুন।')}</p><a href="#diagnose" class="btn empty-action">${L('Start an observation', 'পর্যবেক্ষণ শুরু করুন')}${icon('arrow')}</a></div>`}</section><section class="panel"><div class="panel-head"><div><h2>${L('Observations by crop', 'ফসল অনুযায়ী পর্যবেক্ষণ')}</h2><p>${L('Calculated from your saved records', 'সংরক্ষিত রেকর্ড থেকে গণনা')}</p></div>${icon('chart')}</div><div class="chart" role="img" aria-label="${esc(CROP_DATA.map((c, i) => A(c.name) + ': ' + n(counts[i])).join(', '))}">${counts.map(v => `<div class="chart-col"><b>${n(v)}</b><div class="bar" style="height:${v / max * 105}px"></div></div>`).join('')}</div><div class="chart-labels">${CROP_DATA.map(c => `<span>${A(c.name)}</span>`).join('')}</div><div class="result-block"><h3>${L('Private by design', 'ডেটা আপনার ব্রাউজারেই')}</h3><p>${L('Export a copy before clearing browser data. Changing the browser or localhost address opens a separate history.', 'ব্রাউজারের ডেটা মোছার আগে কপি ডাউনলোড করুন। ব্রাউজার বা localhost ঠিকানা বদলালে আলাদা ইতিহাস দেখাবে।')}</p></div></section></div>`;
}
function researchPage() {
  return head(
    L('Research methodology & model results', 'গবেষণা পদ্ধতি ও মডেলের ফলাফল'),
    L('Recorded evaluation results from the supplied PlantVillage research files.', 'আপলোড করা PlantVillage গবেষণা ফাইলের নথিভুক্ত মূল্যায়নের ফলাফল।')
  ) + `
    <section class="panel section">
      <div class="panel-head"><div><h2>${L('Model and dataset', 'মডেল ও Dataset')}</h2><p>${L('Training notebook and exported metadata', 'Training Notebook ও Exported Metadata')}</p></div><span class="badge">${L('Research record', 'গবেষণা রেকর্ড')}</span></div>
      <div class="research-metric-grid">
        <div><small>Architecture</small><b>EfficientNet-B3</b></div>
        <div><small>Dataset</small><b>PlantVillage</b></div>
        <div><small>Classes</small><b>39</b></div>
        <div><small>Input size</small><b>300 × 300</b></div>
        <div><small>Training images</small><b>43,030</b></div>
        <div><small>Validation images</small><b>9,213</b></div>
        <div><small>Testing images</small><b>9,243</b></div>
        <div><small>Grad-CAM layer</small><b>model.features[-1]</b></div>
      </div>
    </section>
    <section class="panel section">
      <div class="panel-head"><div><h2>${L('Recorded test-split metrics', 'নথিভুক্ত Test-Split Metrics')}</h2><p>${L('Values read from outputs/final_research_metrics.csv', 'outputs/final_research_metrics.csv থেকে নেওয়া মান')}</p></div></div>
      <div id="research-metrics" class="research-metric-grid">
        <div><small>Test Accuracy</small><b>98.86%</b></div>
        <div><small>Macro F1-Score</small><b>98.63%</b></div>
        <div><small>Macro Precision</small><b>98.62%</b></div>
        <div><small>Macro Recall</small><b>98.66%</b></div>
        <div><small>ECE</small><b>0.00289</b></div>
        <div><small>Brier Score</small><b>0.01818</b></div>
        <div><small>Negative Log-Likelihood</small><b>0.03607</b></div>
      </div>
      <p class="research-footnote">${L('These are recorded evaluation metrics on the project’s PlantVillage test split. They must not be presented as real-world field accuracy; external field validation is still required.', 'এগুলো প্রকল্পের PlantVillage Test Split-এর নথিভুক্ত মূল্যায়ন। এগুলোকে বাস্তব মাঠের Accuracy হিসেবে উপস্থাপন করা যাবে না; External Field Validation প্রয়োজন।')}</p>
    </section>
    <section class="panel section">
      <div class="panel-head"><div><h2>${L('Research figures', 'গবেষণার চিত্র')}</h2><p>${L('Generated during model evaluation', 'Model Evaluation-এর সময় তৈরি')}</p></div></div>
      <div class="research-figure-grid">
        <figure><img src="${API_BASE}/research-assets/confusion_matrix.png" loading="lazy" alt="Confusion matrix"><figcaption>Confusion Matrix</figcaption></figure>
        <figure><img src="${API_BASE}/research-assets/reliability_diagram.png" loading="lazy" alt="Reliability diagram"><figcaption>Reliability Diagram</figcaption></figure>
        <figure><img src="${API_BASE}/research-assets/accuracy_curve.png" loading="lazy" alt="Accuracy curve"><figcaption>Accuracy Curve</figcaption></figure>
        <figure><img src="${API_BASE}/research-assets/loss_curve.png" loading="lazy" alt="Loss curve"><figcaption>Loss Curve</figcaption></figure>
        <figure><img src="${API_BASE}/research-assets/gradcam_visualization.png" loading="lazy" alt="Grad-CAM examples"><figcaption>Grad-CAM Examples</figcaption></figure>
        <figure><img src="${API_BASE}/research-assets/worst_10_classes.png" loading="lazy" alt="Weakest ten classes"><figcaption>Weakest 10 Classes</figcaption></figure>
      </div>
    </section>
    <section class="panel section">
      <div class="panel-head"><h2>${L('System pipeline', 'সিস্টেম Pipeline')}</h2></div>
      <div class="pipeline">${[
        ['camera', L('Image upload', 'ছবি আপলোড'), L('JPG / PNG / WebP', 'JPG / PNG / WebP')],
        ['scan', L('Preprocessing', 'Preprocessing'), L('Resize 320 → CenterCrop 300', 'Resize 320 → CenterCrop 300')],
        ['spark', L('EfficientNet-B3', 'EfficientNet-B3'), L('39-class inference', '৩৯-ক্লাস Inference')],
        ['chart', L('Grad-CAM', 'Grad-CAM'), L('features[-1] heatmap', 'features[-1] Heatmap')],
        ['database', L('PostgreSQL', 'PostgreSQL'), L('Prediction history', 'Prediction History')]
      ].map(([i, t, s], index) => `<div class="pipeline-node"><span class="pipeline-step">${n(index + 1)}</span>${icon(i)}<h3>${t}</h3><small>${s}</small></div>`).join('')}</div>
    </section>`;
}

function historyPage() {
  return head(
    L('AI prediction history & analytics', 'AI পূর্বাভাসের ইতিহাস ও বিশ্লেষণ'),
    L('PostgreSQL-backed records from real image inference requests.', 'প্রকৃত Image Inference Request থেকে PostgreSQL-এ সংরক্ষিত রেকর্ড।')
  ) + `
    <div class="ai-service-status" id="history-api-status">${L('Loading database history…', 'Database History লোড হচ্ছে…')}</div>
    <section class="stats ai-history-stats">
      <div class="stat"><span class="stat-icon">${icon('file')}</span><div><b id="hist-total">—</b><small>${L('Total predictions', 'মোট Prediction')}</small></div></div>
      <div class="stat"><span class="stat-icon">${icon('leaf')}</span><div><b id="hist-disease">—</b><small>${L('Disease / healthy classes', 'রোগ / সুস্থ Class')}</small></div></div>
      <div class="stat"><span class="stat-icon">${icon('shield')}</span><div><b id="hist-background">—</b><small>${L('Background rejections', 'Background Rejection')}</small></div></div>
      <div class="stat"><span class="stat-icon">${icon('chart')}</span><div><b id="hist-average">—</b><small>${L('Average confidence', 'গড় Confidence')}</small></div></div>
    </section>
    <section class="panel section">
      <div class="panel-head"><div><h2>${L('Prediction records', 'Prediction Record')}</h2><p>${L('Search, filter by date and browse pages.', 'Search করুন, তারিখ অনুযায়ী Filter করুন এবং Page দেখুন।')}</p></div><button class="btn outline small" data-action="history-refresh">${L('Refresh', 'Refresh')}${icon('clock')}</button></div>
      <div class="history-filters">
        <input class="input" id="history-search" type="search" placeholder="${L('Search filename or predicted class…', 'Filename বা Predicted Class খুঁজুন…')}">
        <label>${L('From', 'শুরু')}<input class="input" id="history-from" type="date"></label>
        <label>${L('To', 'শেষ')}<input class="input" id="history-to" type="date"></label>
      </div>
      <div class="history-table-wrap"><table class="ai-history-table"><thead><tr><th>ID</th><th>${L('Filename', 'ফাইল')}</th><th>${L('Predicted class', 'শনাক্ত Class')}</th><th>${L('Confidence', 'Confidence')}</th><th>Device</th><th>${L('Date / time', 'তারিখ / সময়')}</th></tr></thead><tbody id="history-rows"><tr><td colspan="6">${L('Loading…', 'লোড হচ্ছে…')}</td></tr></tbody></table></div>
      <div class="history-pagination" id="history-pagination"></div>
    </section>
    <section class="panel section"><div class="panel-head"><div><h2>${L('Disease distribution', 'রোগের Distribution')}</h2><p>${L('Counts exclude Background_without_leaves.', 'Background_without_leaves বাদ দিয়ে গণনা করা হয়েছে।')}</p></div></div><div id="history-distribution" class="history-distribution"><p>${L('Loading analytics…', 'Analytics লোড হচ্ছে…')}</p></div></section>`;
}

async function loadAIStatus() {
  const targets = ['ai-service-status', 'dashboard-api-status'];
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    const dbResponse = await fetch(`${API_BASE}/api/v1/database-health`);
    const db = await dbResponse.json();
    const text = response.ok
      ? L(`API online · ${data.architecture} · ${data.device}`, `API Online · ${data.architecture} · ${data.device}`)
      : L('Model unavailable', 'Model পাওয়া যাচ্ছে না');
    targets.forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.textContent = text; el.classList.toggle('online', response.ok); el.classList.toggle('offline', !response.ok); }
    });
    const apiDetail = document.getElementById('dashboard-api-detail');
    const dbDetail = document.getElementById('dashboard-db-detail');
    if (apiDetail) apiDetail.textContent = response.ok ? 'Online' : 'Unavailable';
    if (dbDetail) dbDetail.textContent = db.connected ? 'Connected' : 'Not connected';
  } catch (error) {
    targets.forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.textContent = L('Backend offline — start the project launcher.', 'Backend Offline — Project Launcher চালু করুন।'); el.classList.add('offline'); }
    });
    const apiDetail = document.getElementById('dashboard-api-detail');
    const dbDetail = document.getElementById('dashboard-db-detail');
    if (apiDetail) apiDetail.textContent = 'Offline';
    if (dbDetail) dbDetail.textContent = 'Unknown';
  }
}

function renderHistoryRows(records) {
  const body = document.getElementById('history-rows');
  if (!body) return;
  body.replaceChildren();
  if (!records || !records.length) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 6;
    cell.textContent = L('No prediction records found for these filters.', 'এই Filter-এ কোনো Prediction Record পাওয়া যায়নি।');
    row.appendChild(cell); body.appendChild(row); return;
  }
  records.forEach(item => {
    const row = document.createElement('tr');
    const values = [
      item.id,
      item.filename,
      item.predicted_label,
      `${Number(item.confidence_percent).toFixed(2)}%`,
      item.device,
      new Date(item.created_at).toLocaleString(lang === 'bn' ? 'bn-BD' : 'en-GB')
    ];
    values.forEach((value, index) => {
      const cell = document.createElement('td');
      cell.textContent = String(value ?? '—');
      if (index === 3) cell.className = 'history-confidence';
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
}

function renderHistoryPagination(data) {
  const holder = document.getElementById('history-pagination');
  if (!holder) return;
  const totalPages = Math.max(1, Number(data.total_pages || 1));
  holder.innerHTML = `
    <span>${L('Showing page', 'Page')} ${data.page} / ${totalPages} · ${Number(data.total_records || 0)} ${L('records', 'টি Record')}</span>
    <div><button class="btn outline small" data-history-page="${Math.max(1, data.page - 1)}" ${data.page <= 1 ? 'disabled' : ''}>← ${L('Previous', 'আগের')}</button>
    <button class="btn outline small" data-history-page="${Math.min(totalPages, data.page + 1)}" ${data.page >= totalPages ? 'disabled' : ''}>${L('Next', 'পরের')} →</button></div>`;
}

async function loadHistoryDashboard(page = 1) {
  historyPageNumber = page;
  const status = document.getElementById('history-api-status');
  if (status) status.textContent = L('Loading PostgreSQL analytics…', 'PostgreSQL Analytics লোড হচ্ছে…');
  const search = document.getElementById('history-search')?.value.trim() || '';
  const startDate = document.getElementById('history-from')?.value || '';
  const endDate = document.getElementById('history-to')?.value || '';
  const params = new URLSearchParams({ page: String(page), limit: String(HISTORY_PAGE_SIZE) });
  if (search) params.set('search', search);
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);

  try {
    const [historyResponse, analyticsResponse] = await Promise.all([
      fetch(`${API_BASE}/api/v1/history?${params.toString()}`),
      fetch(`${API_BASE}/api/v1/analytics`)
    ]);
    const historyData = await historyResponse.json();
    const analyticsData = await analyticsResponse.json();
    if (!historyResponse.ok) throw new Error(historyData.detail || `History API error (${historyResponse.status})`);
    if (!analyticsResponse.ok) throw new Error(analyticsData.detail || `Analytics API error (${analyticsResponse.status})`);

    document.getElementById('hist-total').textContent = analyticsData.total_predictions;
    document.getElementById('hist-disease').textContent = analyticsData.disease_predictions;
    document.getElementById('hist-background').textContent = analyticsData.background_rejections;
    document.getElementById('hist-average').textContent = `${Number(analyticsData.average_confidence_percent).toFixed(2)}%`;
    renderHistoryRows(historyData.history);
    renderHistoryPagination(historyData);

    const distribution = document.getElementById('history-distribution');
    if (distribution) {
      distribution.replaceChildren();
      const items = analyticsData.distribution || [];
      if (!items.length) {
        distribution.textContent = L('No disease-class predictions have been saved yet.', 'এখনো কোনো Disease Class Prediction সংরক্ষিত হয়নি।');
      } else {
        const max = Math.max(...items.map(x => x.count), 1);
        items.forEach(item => {
          const row = document.createElement('div'); row.className = 'distribution-row';
          const head = document.createElement('div'); head.className = 'distribution-head';
          const name = document.createElement('span'); name.textContent = item.label;
          const count = document.createElement('b'); count.textContent = item.count;
          head.append(name, count);
          const track = document.createElement('div'); track.className = 'distribution-track';
          const fill = document.createElement('span'); fill.style.width = `${item.count / max * 100}%`;
          track.appendChild(fill); row.append(head, track); distribution.appendChild(row);
        });
      }
    }
    if (status) { status.textContent = L('PostgreSQL connected · History loaded.', 'PostgreSQL Connected · History লোড হয়েছে।'); status.classList.add('online'); }
  } catch (error) {
    if (status) { status.textContent = error.message; status.classList.add('offline'); }
    const body = document.getElementById('history-rows');
    if (body) body.innerHTML = `<tr><td colspan="6">${esc(error.message)}</td></tr>`;
  }
}

function downloadAIReport(record) {
  if (!record?.ai) return;
  const ai = record.ai;
  const info = ai.disease_info || {};
  const top = (ai.top_5_predictions || []).map(x => `<li>${esc(x.label)} — ${Number(x.confidence_percent).toFixed(2)}%</li>`).join('');
  const sections = ['symptoms', 'causes', 'prevention', 'management'];
  const details = sections.map(key => `<h3>${key[0].toUpperCase() + key.slice(1)}</h3><ul>${(info[key] || []).map(x => `<li>${esc(x)}</li>`).join('')}</ul>`).join('');
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${esc(projectTitle())}</title><style>body{font:16px/1.7 Arial,sans-serif;max-width:850px;margin:35px auto;padding:24px;color:#172033}h1{font-size:25px}h2{color:#1e40af}.note{background:#eff6ff;padding:14px;border-radius:8px}li{margin:7px 0}small{color:#64748b}</style></head><body><small>${esc(projectTitle())}</small><h1>AI Crop Disease Analysis Report</h1><p>${new Date(record.date).toLocaleString()}</p><h2>${esc(ai.predicted_label)}</h2><p><b>Confidence:</b> ${Number(ai.confidence_percent).toFixed(2)}% · <b>Margin:</b> ${Number(ai.confidence_margin).toFixed(2)} points</p><p><b>Status:</b> ${esc(ai.reliability_status)}</p><p class="note">This report contains a model prediction, not a confirmed field diagnosis. Confirm with an agricultural expert before treatment.</p><h3>Top-5 model predictions</h3><ol>${top}</ol>${details}<p><small>Model: EfficientNet-B3 · Dataset: PlantVillage · 39 classes · Device: ${esc(ai.device)}</small></p></body></html>`;
  downloadBlob(html, `CropCare-AI-Report-${Date.now()}.html`, 'text/html;charset=utf-8');
}

function aboutPage() {
  return head(
    L('About the research system', 'গবেষণা সিস্টেম পরিচিতি'),
    L('A web-based crop disease decision-support application built around a trained deep-learning model.', 'প্রশিক্ষিত Deep Learning মডেলভিত্তিক Web-Based ফসলের রোগ শনাক্তকরণ ও সিদ্ধান্ত-সহায়ক Application।')
  ) + `
    <section class="panel about-intro">
      <span class="eyebrow">${L('FINAL YEAR RESEARCH PROJECT', 'ফাইনাল ইয়ার রিসার্চ প্রজেক্ট')}</span>
      <h2>${esc(projectTitle())}</h2>
      <p class="muted">${L('The application combines the CropCare bilingual interface with a FastAPI backend, a fine-tuned EfficientNet-B3 model trained on 39 PlantVillage classes, Grad-CAM explainability and PostgreSQL prediction history.', 'এই Application-এ CropCare-এর দ্বিভাষিক Interface, FastAPI Backend, PlantVillage-এর ৩৯টি ক্লাসে Fine-tuned EfficientNet-B3 Model, Grad-CAM Explainability এবং PostgreSQL Prediction History যুক্ত করা হয়েছে।')}</p>
      <div class="architecture">
        ${[['camera', 'HTML · CSS · JavaScript'], ['scan', 'FastAPI · Python'], ['spark', 'PyTorch · EfficientNet-B3'], ['chart', 'Grad-CAM'], ['file', 'PostgreSQL']].map(([i, t], j) => `${j ? '<span>→</span>' : ''}<div>${icon(i)}${t}</div>`).join('')}
      </div>
    </section>
    <section class="panel section faq">
      <h2>${L('Important research limitations', 'গুরুত্বপূর্ণ গবেষণা সীমাবদ্ধতা')}</h2>
      <details open><summary>${L('Does the model guarantee a correct field diagnosis?', 'মডেল কি মাঠে সঠিক রোগ নির্ণয়ের নিশ্চয়তা দেয়?')}</summary><p>${L('No. The model was evaluated on the recorded PlantVillage test split. Field images may differ in lighting, background, camera quality, crop variety and disease stage. Confirm important decisions with an agricultural expert.', 'না। মডেলটি নথিভুক্ত PlantVillage Test Split-এ মূল্যায়িত। মাঠের ছবিতে আলো, পটভূমি, ক্যামেরা, জাত ও রোগের পর্যায় ভিন্ন হতে পারে। গুরুত্বপূর্ণ সিদ্ধান্ত কৃষি বিশেষজ্ঞের মাধ্যমে নিশ্চিত করুন।')}</p></details>
      <details><summary>${L('What does Background Rejection mean?', 'Background Rejection কী?')}</summary><p>${L('Background_without_leaves is one of the trained dataset classes. When it is the top prediction, the application does not issue a plant disease diagnosis. It is not a universal out-of-distribution detector.', 'Background_without_leaves প্রশিক্ষিত Dataset-এর একটি Class। এটি Top Prediction হলে Application রোগ নির্ণয় দেয় না। তবে এটি সব ধরনের Out-of-Distribution Image শনাক্ত করার নিশ্চয়তা নয়।')}</p></details>
      <details><summary>${L('What does Grad-CAM show?', 'Grad-CAM কী দেখায়?')}</summary><p>${L('Grad-CAM highlights image regions that influenced a selected class score. It helps inspect model attention, but it does not prove that the highlighted region is the biological cause of a disease.', 'Grad-CAM নির্বাচিত Class Score-এ প্রভাব ফেলা ছবির অঞ্চল দেখায়। এটি Model-এর Attention বোঝাতে সাহায্য করে, তবে Highlight করা অংশ রোগের জৈবিক কারণ—এমন প্রমাণ নয়।')}</p></details>
    </section>`;
}
function render() {
  shell();
  const pages = { dashboard, diagnose, history: historyPage, library, reports: reportsPage, research: researchPage, about: aboutPage };
  $('#main').innerHTML = `<div class="page-enter">${pages[route]()}</div>`;
  if (route === 'diagnose') {
    bindUpload();
    loadAIStatus();
  }
  if (route === 'dashboard') loadAIStatus();
  if (route === 'history') {
    loadHistoryDashboard(1);
    $('#history-search')?.addEventListener('input', () => loadHistoryDashboard(1));
    $('#history-from')?.addEventListener('change', () => loadHistoryDashboard(1));
    $('#history-to')?.addEventListener('change', () => loadHistoryDashboard(1));
  }
  if (route === 'research') loadAIStatus();
  document.dispatchEvent(new CustomEvent('cropcare:render'));
}
function closeNavigation() {
  $('#sidebar').classList.remove('open');
  $('[data-action="menu"]')?.setAttribute('aria-expanded', 'false');
}
function navigate() {
  const [page, param] = (location.hash.slice(1) || 'dashboard').split('/');
  route = navs.some(x => x[0] === page) ? page : 'dashboard';
  if (route === 'library') { filter = CROP_DATA.some(c => c.id === param) ? param : 'all'; query = ''; }
  analyzing = false; runId++; uploadId++; closeNavigation(); render(); window.scrollTo(0, 0);
}
function toast(text) {
  $('#toast').textContent = text; $('#toast').classList.add('visible');
  clearTimeout(toast.timer); toast.timer = setTimeout(() => $('#toast').classList.remove('visible'), 3500);
}
function openModal(title, body) {
  lastFocus = document.activeElement;
  $('#detail-content').innerHTML = `<div class="modal-head"><h2 id="dialog-title">${title}</h2><button data-action="close" aria-label="${L('Close dialog', 'ডায়ালগ বন্ধ করুন')}">${icon('close')}</button></div><div class="modal-body">${body}</div>`;
  $('#detail').setAttribute('aria-labelledby', 'dialog-title'); $('#detail').showModal();
}
function showDisease(id) {
  const d = DISEASES.find(x => x.id === id); if (!d) return;
  openModal(A(d.name), `<span class="badge neutral">${A(cropOf(d).name)} · ${A(d.type)}</span><h3>${L('Recognize the symptoms', 'লক্ষণ চিনুন')}</h3><p>${A(d.symptom)}</p><h3>${L('Care and prevention', 'যত্ন ও প্রতিরোধ')}</h3><ul>${d.care.map(x => `<li>${A(x)}</li>`).join('')}</ul><div class="notice">${icon('info')}${L('Similar symptoms can have different causes. Seek local confirmation before treatment.', 'একই লক্ষণের ভিন্ন কারণ হতে পারে। ব্যবস্থা নেওয়ার আগে স্থানীয়ভাবে নিশ্চিত করুন।')}</div><a class="link" href="${d.source}" target="_blank" rel="noopener">${d.sourceName} ↗</a>`);
}
function showReport(id) {
  const r = reports.find(x => x.id === id); if (!r) return;
  const d = DISEASES.find(x => x.id === r.disease);
  openModal(L('Saved observation', 'সংরক্ষিত পর্যবেক্ষণ'), `<span class="badge">${L('Selected reference guide', 'নির্বাচিত তথ্যের গাইড')}</span><p>${date(r.date)}</p><h3>${A(cropOf(d).name)} · ${A(d.name)}</h3><p>${A(d.symptom)}</p><ul>${d.care.map(x => `<li>${A(x)}</li>`).join('')}</ul>${r.note ? `<h3>${L('Your notes', 'আপনার নোট')}</h3><p class="saved-note">${esc(r.note)}</p>` : ''}<div class="service-note">${L('This record contains the reference guide you selected; it is not a confirmed diagnosis.', 'এই রেকর্ডে আপনার নির্বাচিত তথ্যের গাইড আছে; এটি নিশ্চিত রোগ নির্ণয় নয়।')}</div><a class="link" href="${d.source}" target="_blank" rel="noopener">${d.sourceName} ↗</a><div class="actions"><button class="btn" data-export="${esc(r.id)}">${L('Download report', 'রিপোর্ট ডাউনলোড')}${icon('download')}</button></div>`);
}
function releasePreview() { if (preview.startsWith('blob:')) URL.revokeObjectURL(preview); }
function acceptFile(f) {
  if (!f) return;
  if (!['image/jpeg', 'image/png', 'image/webp', 'image/bmp'].includes(f.type)) { toast(L('Choose a JPG, PNG or WebP image.', 'JPG, PNG বা WebP ছবি বেছে নিন।')); return; }
  if (f.size > 10 * 1024 * 1024) { toast(L('This image exceeds the 10 MB limit.', 'ছবিটি ১০ মেগাবাইট সীমার বেশি।')); return; }
  const token = ++uploadId, url = URL.createObjectURL(f), img = new Image();
  img.onload = () => {
    if (token !== uploadId || route !== 'diagnose') { URL.revokeObjectURL(url); return; }
    if (img.width < 64 || img.height < 64) { URL.revokeObjectURL(url); toast(L('Choose an image at least 64 × 64 pixels.', 'অন্তত ৬৪ × ৬৪ পিক্সেলের ছবি দিন।')); return; }
    releasePreview(); preview = url; file = f; result = null; runId++; analyzing = false; render();
  };
  img.onerror = () => { URL.revokeObjectURL(url); if (token === uploadId) toast(L('This file could not be decoded as an image.', 'ফাইলটি ছবি হিসেবে পড়া যাচ্ছে না।')); };
  img.src = url;
}
function bindUpload() {
  ['image-input', 'camera-input'].forEach(id => $('#' + id).addEventListener('change', e => acceptFile(e.target.files[0])));
  const zone = $('#dropzone');
  ['dragover', 'dragenter'].forEach(type => zone.addEventListener(type, e => { e.preventDefault(); zone.classList.add('dragging'); }));
  ['dragleave', 'drop'].forEach(type => zone.addEventListener(type, e => { e.preventDefault(); zone.classList.remove('dragging'); }));
  zone.addEventListener('drop', e => acceptFile(e.dataTransfer.files[0]));
}

async function useSampleImage() {
  try {
    const response = await fetch('assets/leaf-demo.jpg');
    if (!response.ok) throw new Error('Sample image asset could not be loaded.');
    const blob = await response.blob();
    const sampleFile = new File([blob], 'leaf-demo.jpg', { type: blob.type || 'image/jpeg' });
    acceptFile(sampleFile);
    toast(L('Sample leaf image loaded. Run AI analysis to view the model prediction.', 'নমুনা পাতার ছবি এসেছে। AI Analysis চালিয়ে Model Prediction দেখুন।'));
  } catch (error) {
    toast(error.message);
  }
}

async function analyze() {
  if (analyzing) return;
  if (!file) {
    toast(L('Choose or capture a leaf image first.', 'আগে পাতার ছবি বাছুন বা তুলুন।'));
    return;
  }

  const token = ++runId;
  analyzing = true;
  result = null;
  const panel = $('#result-panel');
  if (panel) {
    panel.innerHTML = `<div class="waiting-visual"><div class="leaf-orbit"><span>${icon('scan')}</span><i></i></div><h3>${L('Running EfficientNet-B3 inference…', 'EfficientNet-B3 দিয়ে বিশ্লেষণ হচ্ছে…')}</h3><p>${L('The image is being preprocessed and evaluated by the trained 39-class model.', 'ছবিটি Preprocess করে প্রশিক্ষিত ৩৯-ক্লাস মডেল দিয়ে মূল্যায়ন করা হচ্ছে।')}</p></div>`;
  }
  $('[data-action="analyze"]')?.setAttribute('disabled', 'disabled');

  try {
    const form = new FormData();
    form.append('file', file, file.name || 'crop-image.jpg');

    const response = await fetch(`${API_BASE}/api/v1/predict`, {
      method: 'POST',
      body: form
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || `Prediction API error (${response.status})`);
    if (token !== runId || route !== 'diagnose') return;

    result = {
      mode: 'ai',
      id: payload.record_id || `ai-${Date.now()}`,
      date: new Date().toISOString(),
      filename: payload.filename || file.name,
      note: fieldNote.trim(),
      ai: payload.result,
      database_saved: Boolean(payload.database_saved),
      record_id: payload.record_id || null,
      gradcam: null,
      gradcam_pending: true
    };
    analyzing = false;
    render();

    // Grad-CAM is an additional explainability request; it does not invalidate prediction.
    try {
      const camForm = new FormData();
      camForm.append('file', file, file.name || 'crop-image.jpg');
      camForm.append('target_class', payload.result.predicted_class);
      const camResponse = await fetch(`${API_BASE}/api/v1/gradcam`, {
        method: 'POST',
        body: camForm
      });
      const camPayload = await camResponse.json();
      if (camResponse.ok && camPayload.success && token === runId && route === 'diagnose') {
        result.gradcam = camPayload;
        result.gradcam_pending = false;
        render();
      } else if (!camResponse.ok) {
        console.warn('Grad-CAM unavailable:', camPayload.detail || camResponse.status);
        if (result && token === runId && route === 'diagnose') { result.gradcam_pending = false; render(); }
      }
    } catch (camError) {
      console.warn('Grad-CAM request failed:', camError);
      if (result && token === runId && route === 'diagnose') { result.gradcam_pending = false; render(); }
    }

    toast(result.database_saved
      ? L('AI prediction completed and saved to PostgreSQL.', 'AI Prediction সম্পন্ন ও PostgreSQL-এ সংরক্ষিত হয়েছে।')
      : L('AI prediction completed. Database history is currently unavailable.', 'AI Prediction সম্পন্ন হয়েছে। Database History বর্তমানে পাওয়া যাচ্ছে না।'));
  } catch (error) {
    analyzing = false;
    if (token === runId && route === 'diagnose') {
      const panelNow = $('#result-panel');
      if (panelNow) panelNow.innerHTML = `<div class="notice amber"><h3>${L('Could not complete AI analysis', 'AI বিশ্লেষণ সম্পন্ন হয়নি')}</h3><p>${esc(error.message)}</p><p>${L('Check that the backend API is reachable and the trained model checkpoint is configured on the server.', 'Backend API চালু আছে এবং সার্ভারে Trained Model Checkpoint সঠিকভাবে কনফিগার করা আছে কি না দেখুন।')}</p></div>`;
      $('[data-action="analyze"]')?.removeAttribute('disabled');
    }
  }
}
function saveReport() {
  if (!result) return;
  if (reports.some(r => r.id === result.id)) { toast(L('This observation is already saved.', 'এই পর্যবেক্ষণ আগেই রাখা আছে।')); return; }
  reports = [{ ...result }, ...reports].slice(0, 100);
  const ok = safeStore.set('cc-observations-v2', reports); shell();
  toast(ok ? L('Observation saved on this device.', 'পর্যবেক্ষণ এই ডিভাইসে রাখা হয়েছে।') : L('Saved for this session; browser storage is unavailable.', 'এই সেশনে রাখা হয়েছে; ব্রাউজারের স্থায়ী স্টোরেজ পাওয়া যায়নি।'));
}
function downloadBlob(text, name, type) {
  const url = URL.createObjectURL(new Blob([text], { type })), anchor = document.createElement('a');
  anchor.href = url; anchor.download = name; document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
function exportReport(r) {
  if (!r) return;
  const d = DISEASES.find(x => x.id === r.disease);
  downloadBlob(`<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${L('AI Crop Disease Research — Field Observation', 'AI ফসল রোগ গবেষণা — মাঠ পর্যবেক্ষণ')}</title><style>body{font:17px/1.8 system-ui,sans-serif;max-width:760px;margin:45px auto;padding:24px;color:#172033}h1{font-size:30px}small{color:#475569}.note{padding:16px;background:#eff6ff;border-radius:8px}li{margin:10px 0}a{overflow-wrap:anywhere}.user-note{white-space:pre-wrap}@media print{body{margin:0}}</style></head><body><small>${projectTitle()}</small><h1>${esc(projectTitle())}</h1><h2>${L('Field observation', 'মাঠের পর্যবেক্ষণ')}</h2><small>${date(r.date)}</small><p class="note">${L('Reference guide selected by the user. No automatic image diagnosis was performed; this is not a confirmed diagnosis.', 'ব্যবহারকারীর নির্বাচিত তথ্যের গাইড। এটি স্বয়ংক্রিয় বা নিশ্চিত রোগ নির্ণয় নয়।')}</p><h2>${A(cropOf(d).name)} · ${A(d.name)}</h2><p>${A(d.symptom)}</p>${r.note ? `<h3>${L('Your field notes', 'আপনার পর্যবেক্ষণ')}</h3><p class="user-note">${esc(r.note)}</p>` : ''}<h3>${L('General care', 'সাধারণ পরিচর্যা')}</h3><ul>${d.care.map(x => `<li>${A(x)}</li>`).join('')}</ul><p>${L('Confirm suspected disease and local management with an agricultural expert.', 'সন্দেহজনক রোগ ও স্থানীয় ব্যবস্থাপনা কৃষি বিশেষজ্ঞের মাধ্যমে নিশ্চিত করুন।')}</p><p>${L('Source', 'সূত্র')}: <a href="${d.source}">${d.sourceName}</a></p><small>${L('Open in a browser and use Print → Save as PDF if needed.', 'প্রয়োজনে ব্রাউজারে খুলে Print → Save as PDF করুন।')}</small></body></html>`, 'CropCare-Observation-' + r.id.replace(/[^a-zA-Z0-9-]/g, '') + '.html', 'text/html;charset=utf-8');
  toast(L('Report downloaded. Open it to read or print.', 'রিপোর্ট ডাউনলোড হয়েছে। খুলে পড়ুন বা প্রিন্ট করুন।'));
}
document.addEventListener('click', event => {
  const el = event.target.closest('button,a'); if (!el) return;
  if (el.dataset.lang) { lang = el.dataset.lang; safeStore.set('cc-language', lang); analyzing = false; runId++; render(); return; }
  if (el.dataset.filter) { filter = el.dataset.filter; render(); return; }
  if (el.dataset.disease) { showDisease(el.dataset.disease); return; }
  if (el.dataset.report) { showReport(el.dataset.report); return; }
  if (el.dataset.export) { exportReport(reports.find(r => r.id === el.dataset.export)); return; }
  if (el.dataset.historyPage) { loadHistoryDashboard(Number(el.dataset.historyPage)); return; }
  if (el.dataset.delete) { reports = reports.filter(r => r.id !== el.dataset.delete); safeStore.set('cc-observations-v2', reports); render(); toast(L('Observation removed.', 'পর্যবেক্ষণ মুছে ফেলা হয়েছে।')); return; }
  switch (el.dataset.action) {
    case 'menu': $('#sidebar').classList.toggle('open'); el.setAttribute('aria-expanded', String($('#sidebar').classList.contains('open'))); break;
    case 'motion': safeStore.set('cc-motion', !safeStore.get('cc-motion', true)); document.dispatchEvent(new CustomEvent('cropcare:motion')); el.setAttribute('aria-pressed', String(motionEnabled())); toast(motionEnabled() ? L('Motion effects on', 'অ্যানিমেশন চালু') : L('Motion effects off', 'অ্যানিমেশন বন্ধ')); break;
    case 'close': $('#detail').close(); break;
    case 'reset-tasks': tasks = [false, false, false]; safeStore.set('cc-tasks', tasks); $('#checklist').innerHTML = checklist(); break;
    case 'choose': $('#image-input').click(); break;
    case 'camera': $('#camera-input').click(); break;
    case 'sample': useSampleImage(); break;
    case 'analyze': analyze(); break;
    case 'save': saveReport(); break;
    case 'download': if (result?.mode === 'ai') downloadAIReport(result); else exportReport(result); break;
    case 'history-refresh': loadHistoryDashboard(historyPageNumber); break;
    case 'export-all': downloadBlob(JSON.stringify({ project: projectTitle(), schema: 2, mode: 'guide', note: 'User-selected reference guides and observations, not confirmed diagnoses.', reports }, null, 2), 'CropCare-observations.json', 'application/json'); break;
  }
  if (el.closest('.nav') || (el.closest('#sidebar') && el.matches('a'))) closeNavigation();
});
document.addEventListener('change', event => {
  if (event.target.dataset.task !== undefined) { tasks[Number(event.target.dataset.task)] = event.target.checked; safeStore.set('cc-tasks', tasks); const activeTask = event.target.dataset.task; $('#checklist').innerHTML = checklist(); $(`[data-task="${activeTask}"]`)?.focus(); }
  if (event.target.id === 'scenario') { selection = event.target.value; result = null; runId++; analyzing = false; $('#result-panel').innerHTML = waitingHTML(); $('[data-action="analyze"]').disabled = false; }
});
document.addEventListener('input', event => {
  if (event.target.id === 'disease-search') { query = event.target.value; $('#disease-grid').innerHTML = diseaseCards(); }
  if (event.target.id === 'field-note') { fieldNote = event.target.value; if (result || analyzing) { result = null; runId++; analyzing = false; $('#result-panel').innerHTML = waitingHTML(); $('[data-action="analyze"]').disabled = false; } }
});
document.addEventListener('click', e => { if ($('#sidebar').classList.contains('open') && !e.target.closest('#sidebar') && !e.target.closest('[data-action="menu"]')) closeNavigation(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && $('#sidebar').classList.contains('open')) { closeNavigation(); $('[data-action="menu"]')?.focus(); } });
$('#detail').addEventListener('click', e => { if (e.target === $('#detail')) $('#detail').close(); });
$('#detail').addEventListener('close', () => lastFocus?.focus());
window.addEventListener('hashchange', navigate);
window.addEventListener('beforeunload', releasePreview);
navigate();
