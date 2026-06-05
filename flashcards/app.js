/* ============================================================
   HISTORY CRUSH — flashcard PWA logic
   ============================================================ */
'use strict';

/* ---------- constants ---------- */
const LS_COUNTS = 'hf.correctCounts';
const LS_STATS  = 'hf.stats';
const MASTERY   = 2; // correct answers needed (since last wrong) to master a card
const PALETTE   = ['#ff2d95','#ffb3d9','#ffe600','#9d4edd','#3af0ff','#b6ff3a','#ff9a3a','#ffffff'];
const CAT_LABELS = {
  people_and_figures:   'People',
  events_and_battles:   'Events',
  ideas_and_movements:  'Ideas',
  treaties_and_documents:'Documents',
};

/* ---------- state ---------- */
const state = {
  cards: [],
  byId: {},
  byCat: {},
  category: null,
  direction: 'AB',          // 'AB' = prompt a → pick b ; 'BA' = prompt b → pick a
  current: null,            // current card id
  answered: false,
  history: [],              // visited card ids (for Prev)
  streak: 0,
  best: 0,
  correct: 0,
  total: 0,
  kissCount: 0,
  heartPlacements: [],
  lastRenderedLevel: null,
};

/* ---------- localStorage helpers ---------- */
function loadCounts(){
  try { return JSON.parse(localStorage.getItem(LS_COUNTS)) || {}; }
  catch(e){ return {}; }
}
function saveCounts(c){ localStorage.setItem(LS_COUNTS, JSON.stringify(c)); }
function getCount(id){ return loadCounts()[id] || 0; }
function setCount(id, n){ const c = loadCounts(); c[id] = n; saveCounts(c); }

function saveStats(){
  localStorage.setItem(LS_STATS, JSON.stringify({
    best: state.best, correct: state.correct, total: state.total, kissCount: state.kissCount,
  }));
}
function loadStats(){
  try {
    const s = JSON.parse(localStorage.getItem(LS_STATS));
    if (s){ state.best = s.best||0; state.correct = s.correct||0; state.total = s.total||0; state.kissCount = s.kissCount||0; }
  } catch(e){}
}

/* ---------- difficulty / streak (single source of truth) ---------- */
// streak 0-4 → L1, 5-9 → L2, 10-14 → L3, 15-19 → L4, 20+ → L5
function targetLevel(streak){
  return Math.min(5, Math.floor(streak / 5) + 1);
}

/* ---------- pools ---------- */
function catCards(cat){ return state.byCat[cat] || []; }
function activePool(cat){
  // cards in category not yet mastered
  return catCards(cat).filter(c => getCount(c.id) < MASTERY);
}
function masteredInCat(cat){
  return catCards(cat).filter(c => getCount(c.id) >= MASTERY);
}

/* ---------- weighted next-card picker ---------- */
function weightFor(diff, target){
  const dist = Math.abs(diff - target);
  if (dist === 0) return 5;     // target level
  if (dist === 1) return 2;     // neighbor
  return diff < target ? 0.6 : 0.4; // easier vs harder, distance >= 2
}
function pickNextCard(){
  const cat = state.category;
  const target = targetLevel(state.streak);
  let pool = activePool(cat).filter(c => c.id !== state.current); // exclude current → no immediate repeat
  if (pool.length === 0){
    // only the current card remains active (or none) — allow current as fallback
    pool = activePool(cat);
  }
  if (pool.length === 0) return null;
  const weights = pool.map(c => {
    let w = weightFor(c.difficulty, target);
    if (getCount(c.id) === MASTERY - 1) w *= 1.6; // 1/2 mastery progress bonus
    return w;
  });
  const totalW = weights.reduce((a,b)=>a+b, 0);
  let r = Math.random() * totalW;
  for (let i=0;i<pool.length;i++){
    r -= weights[i];
    if (r <= 0) return pool[i].id;
  }
  return pool[pool.length-1].id;
}

/* ---------- rendering helpers ---------- */
function starString(diff){
  let s = '';
  for (let i=1;i<=5;i++) s += (i<=diff) ? '★' : '✩';
  return s;
}
function starHTML(diff, onCls, offCls){
  let html = '';
  for (let i=1;i<=5;i++){
    if (i<=diff) html += `<span class="${onCls||''}">★</span>`;
    else html += `<span class="${offCls||'off'}">✩</span>`;
  }
  return html;
}

/* ---------- card rendering ---------- */
function promptSide(card){ return state.direction === 'AB' ? card.a[0] : card.b[0]; }
function answerSide(card){ return state.direction === 'AB' ? card.b[0] : card.a[0]; }

function buildOptions(card){
  const correctVal = answerSide(card);
  const others = catCards(card.category)
    .filter(c => c.id !== card.id)
    .map(c => answerSide(c))
    .filter(v => v !== correctVal);
  // unique distractors
  const uniq = [];
  const seen = new Set([correctVal]);
  const shuffled = shuffle(others.slice());
  for (const v of shuffled){
    if (!seen.has(v)){ seen.add(v); uniq.push(v); }
    if (uniq.length === 3) break;
  }
  const opts = shuffle([correctVal, ...uniq]);
  return { opts, correctVal };
}

function renderCard(id){
  const card = state.byId[id];
  if (!card) return;
  state.current = id;
  state.answered = false;

  const concept = card.concept;
  document.getElementById('cardConcept').textContent = concept;
  document.getElementById('cardStars').innerHTML = starHTML(card.difficulty, '', 'off');
  document.getElementById('cardPrompt').textContent = promptSide(card);

  // options
  const { opts, correctVal } = buildOptions(card);
  const optWrap = document.getElementById('options');
  optWrap.innerHTML = '';
  opts.forEach(val => {
    const b = document.createElement('button');
    b.className = 'opt';
    b.type = 'button';
    b.textContent = val;
    b.addEventListener('click', () => onAnswer(b, val, correctVal, false));
    optWrap.appendChild(b);
  });

  // answer block hidden
  const ab = document.getElementById('answerBlock');
  ab.hidden = true;
  document.getElementById('abA').textContent = card.a[0];
  document.getElementById('abB').textContent = card.b[0];
  document.getElementById('abNotes').textContent = card.notes;

  // tags row with per-card stars
  const tagsRow = document.getElementById('tagsRow');
  tagsRow.innerHTML = '';
  card.tags.forEach(t => {
    const p = document.createElement('span');
    p.className = 'tag-pill';
    p.textContent = t;
    tagsRow.appendChild(p);
  });
  const ts = document.createElement('span');
  ts.className = 't-stars';
  ts.innerHTML = starHTML(card.difficulty, '', 'off');
  tagsRow.appendChild(ts);

  renderInstructions(card);
  document.getElementById('stage').scrollTop = 0;
}

function renderInstructions(card){
  const dirText = state.direction === 'AB'
    ? 'pick the answer that matches the clue'
    : 'pick the clue that matches the answer';
  const stars = `<span class="s-stars">${starString(card.difficulty)
      .replace(/✩/g,'<span class="s-empty">✩</span>')}</span>`;
  document.getElementById('instructions').innerHTML =
    `${card.concept} ${stars} — ${dirText}`;
}

/* ---------- answering ---------- */
function onAnswer(btn, val, correctVal, isReveal){
  if (state.answered) return;
  state.answered = true;
  const card = state.byId[state.current];

  // disable & reveal correctness on every option
  const buttons = [...document.getElementById('options').querySelectorAll('.opt')];
  buttons.forEach(b => {
    b.disabled = true;
    if (b.textContent === correctVal) b.classList.add('correct');
    else if (b === btn) b.classList.add('wrong');
    else b.classList.add('dim');
  });

  // reveal full answer block
  document.getElementById('answerBlock').hidden = false;

  if (isReveal) return; // Reveal button: no scoring

  const correct = (val === correctVal);
  state.total++;
  if (correct){
    state.correct++;
    state.streak++;
    if (state.streak > state.best) state.best = state.streak;
    state.kissCount++;
    const newCount = Math.min(MASTERY, getCount(card.id) + 1);
    setCount(card.id, newCount);
    spawnHeart();
    fireKiss();
    if (state.kissCount % 10 === 0) fireProfileKiss();
    updateDifficulty();
    renderStats();
    saveStats();
    if (activePool(state.category).length === 0){
      // mastered everything in this category
      setTimeout(showCategoryComplete, 600);
    }
  } else {
    state.streak = 0;
    setCount(card.id, 0);
    demoteRandomMastered(card.category);
    clearHearts();
    updateDifficulty();
    renderStats();
    saveStats();
  }
}

function demoteRandomMastered(cat){
  // wrong answer demotes one random mastered card from the same category back into the pool
  const mastered = masteredInCat(cat);
  if (mastered.length === 0) return;
  const victim = mastered[Math.floor(Math.random() * mastered.length)];
  setCount(victim.id, 0);
}

/* ---------- Reveal button (no scoring) ---------- */
function revealCurrent(){
  if (state.answered) return;
  const card = state.byId[state.current];
  const correctVal = answerSide(card);
  onAnswer(null, correctVal, correctVal, true);
}

/* ---------- stats bar ---------- */
function renderStats(){
  document.getElementById('statStreak').textContent = state.streak;
  document.getElementById('statBest').textContent = state.best;
  document.getElementById('statScore').textContent = `${state.correct}/${state.total}`;
  const chip = document.getElementById('streakChip');
  chip.classList.toggle('glow', state.streak >= 5);
}

/* ---------- difficulty meter ---------- */
function updateDifficulty(){
  const streak = state.streak;
  const level = targetLevel(streak);
  const within = streak % 5;
  const meter = document.getElementById('diffMeter');

  document.getElementById('dmBadge').textContent = 'L' + level;

  // dots
  const filled = (level === 5) ? 5 : within;
  let dots = '';
  for (let i=0;i<5;i++) dots += (i<filled) ? '<span class="on">●</span>' : '<span class="off">○</span>';
  document.getElementById('dmDots').innerHTML = dots;

  // hint
  document.getElementById('dmHint').textContent = (level === 5)
    ? 'MAX DIFFICULTY'
    : `${5 - within} more in a row → L${level + 1}`;

  // level change animation (fire exactly once per change)
  if (state.lastRenderedLevel !== null && level !== state.lastRenderedLevel){
    const cls = (level > state.lastRenderedLevel) ? 'level-up' : 'level-down';
    meter.classList.remove('level-up','level-down');
    void meter.offsetWidth; // reflow → retrigger
    meter.classList.add(cls);
    setTimeout(() => meter.classList.remove(cls), 450);
  }
  state.lastRenderedLevel = level;
}

/* ---------- hearts ---------- */
function spawnHeart(){
  const layer = document.getElementById('heartLayer');
  const onLeft = Math.random() < 0.5;
  const x = onLeft ? (-4 + Math.random()*18) : (86 + Math.random()*18); // bands, never on the characters
  const y = 10 + Math.random()*75;
  const size = 16 + Math.random()*18;
  const rot = -25 + Math.random()*50;
  const color = PALETTE[Math.floor(Math.random()*PALETTE.length)];
  const h = document.createElement('span');
  h.className = 'heart';
  h.textContent = '♥';
  h.style.left = x + '%';
  h.style.top = y + '%';
  h.style.fontSize = size + 'px';
  h.style.color = color;
  h.style.setProperty('--rot', rot + 'deg');
  layer.appendChild(h);
  state.heartPlacements.push({ x, y, size, rot, color });
}
function spawnHeartShower(n){ for (let i=0;i<n;i++) setTimeout(spawnHeart, i*70); }

function clearHearts(){
  const layer = document.getElementById('heartLayer');
  const hearts = [...layer.children];
  hearts.forEach(h => h.classList.add('out'));
  setTimeout(() => { layer.innerHTML = ''; }, 360);
  state.heartPlacements = [];
}

/* ---------- mascot kiss animations ---------- */
function fireKiss(){
  const right = document.getElementById('mRight');
  const cheek = document.getElementById('cheekL');
  right.classList.remove('kiss-fire');
  void right.offsetWidth; // reflow so it retriggers on rapid answering
  right.classList.add('kiss-fire');
  cheek.classList.remove('blush');
  void cheek.offsetWidth;
  cheek.classList.add('blush');
  setTimeout(() => { right.classList.remove('kiss-fire'); cheek.classList.remove('blush'); }, 950);
}
function fireProfileKiss(){
  const front = document.getElementById('mRight');
  const profile = document.getElementById('mRightProfile');
  const cheek = document.getElementById('cheekL');
  front.style.display = 'none';
  profile.style.display = 'block';
  profile.classList.remove('kiss-fire-profile');
  void profile.offsetWidth;
  profile.classList.add('kiss-fire-profile');
  cheek.classList.remove('blush');
  void cheek.offsetWidth;
  cheek.classList.add('blush');
  spawnHeartShower(6);
  setTimeout(() => {
    profile.classList.remove('kiss-fire-profile');
    profile.style.display = 'none';
    front.style.display = 'block';
    cheek.classList.remove('blush');
  }, 950);
}

/* ---------- category complete ---------- */
function showCategoryComplete(){
  const overlay = document.getElementById('completeOverlay');
  const cat = state.category;
  const n = catCards(cat).length;
  document.getElementById('completeSub').textContent =
    `You mastered all ${n} ${CAT_LABELS[cat]} cards!`;
  overlay.hidden = false;
  burstConfetti();
}
function burstConfetti(){
  const layer = document.getElementById('confettiLayer');
  layer.innerHTML = '';
  for (let i=0;i<80;i++){
    const c = document.createElement('span');
    c.className = 'confetti';
    c.style.left = Math.random()*100 + '%';
    c.style.background = PALETTE[Math.floor(Math.random()*PALETTE.length)];
    c.style.animationDuration = (1.8 + Math.random()*1.8) + 's';
    c.style.animationDelay = (Math.random()*0.7) + 's';
    c.style.transform = `rotate(${Math.random()*360}deg)`;
    layer.appendChild(c);
  }
}
function restartCategory(){
  const cat = state.category;
  const counts = loadCounts();
  catCards(cat).forEach(c => { counts[c.id] = 0; });
  saveCounts(counts);
  document.getElementById('completeOverlay').hidden = true;
  document.getElementById('confettiLayer').innerHTML = '';
  const next = pickNextCard();
  if (next) renderCard(next);
}

/* ---------- navigation ---------- */
function goNext(){
  if (state.current) state.history.push(state.current);
  const next = pickNextCard();
  if (next) renderCard(next);
  else setTimeout(showCategoryComplete, 100);
}
function goPrev(){
  if (state.history.length === 0) return;
  const prev = state.history.pop();
  renderCard(prev);
}
function goShuffle(){
  const pool = activePool(state.category).filter(c => c.id !== state.current);
  const src = pool.length ? pool : activePool(state.category);
  if (src.length === 0){ showCategoryComplete(); return; }
  if (state.current) state.history.push(state.current);
  renderCard(src[Math.floor(Math.random()*src.length)].id);
}
function toggleDirection(){
  state.direction = (state.direction === 'AB') ? 'BA' : 'AB';
  document.getElementById('dirBtn').textContent = (state.direction === 'AB') ? 'A→B' : 'B→A';
  if (state.current) renderCard(state.current);
}

/* ---------- category switching ---------- */
function buildCategoryTabs(){
  const wrap = document.getElementById('catTabs');
  wrap.innerHTML = '';
  Object.keys(CAT_LABELS).forEach(cat => {
    if (!state.byCat[cat]) return;
    const tab = document.createElement('button');
    tab.className = 'cat-tab' + (cat === state.category ? ' active' : '');
    tab.type = 'button';
    tab.dataset.cat = cat;
    tab.innerHTML = `${CAT_LABELS[cat]} <span class="ct-count">${catCards(cat).length}</span>`;
    tab.addEventListener('click', () => switchCategory(cat));
    wrap.appendChild(tab);
  });
}
function switchCategory(cat){
  state.category = cat;
  state.current = null;
  state.history = [];
  [...document.querySelectorAll('.cat-tab')].forEach(t =>
    t.classList.toggle('active', t.dataset.cat === cat));
  const pool = activePool(cat);
  if (pool.length === 0){ showCategoryComplete(); return; }
  const next = pickNextCard();
  if (next) renderCard(next);
}

/* ---------- reset ---------- */
function resetStats(){
  saveCounts({});
  state.streak = 0; state.best = 0; state.correct = 0; state.total = 0; state.kissCount = 0;
  state.lastRenderedLevel = null;
  clearHearts();
  saveStats();
  renderStats();
  updateDifficulty();
  switchCategory(state.category);
}

/* ---------- util ---------- */
function shuffle(arr){
  for (let i=arr.length-1;i>0;i--){
    const j = Math.floor(Math.random()*(i+1));
    [arr[i],arr[j]] = [arr[j],arr[i]];
  }
  return arr;
}

/* ---------- marquee ---------- */
function buildMarquee(){
  const bits = [
    '<span>★ FROM PYRAMIDS TO PARTITION ★</span>',
    '<span class="pink">♥ MASTER EACH CARD TWICE ♥</span>',
    '<span class="cyan">▲ KEEP YOUR STREAK ALIVE ▲</span>',
    '<span>✦ 201 CARDS · 4 CATEGORIES ✦</span>',
    '<span class="pink">♥ HISTORY CRUSH ♥</span>',
  ].join('');
  document.getElementById('marqueeTrack').innerHTML = bits + bits; // duplicate for seamless loop
}

/* ---------- wire up controls ---------- */
function wireControls(){
  document.getElementById('prevBtn').addEventListener('click', goPrev);
  document.getElementById('nextBtn').addEventListener('click', goNext);
  document.getElementById('shuffleBtn').addEventListener('click', goShuffle);
  document.getElementById('revealBtn').addEventListener('click', revealCurrent);
  document.getElementById('dirBtn').addEventListener('click', toggleDirection);
  document.getElementById('resetBtn').addEventListener('click', resetStats);
  document.getElementById('restartCatBtn').addEventListener('click', restartCategory);
}

/* ---------- boot ---------- */
async function boot(){
  loadStats();
  wireControls();
  buildMarquee();
  try {
    const res = await fetch('cards.json', { cache: 'no-cache' });
    const cards = await res.json();
    state.cards = cards;
    cards.forEach(c => {
      state.byId[c.id] = c;
      (state.byCat[c.category] = state.byCat[c.category] || []).push(c);
    });
  } catch(e){
    document.getElementById('instructions').textContent = 'Failed to load deck: ' + e.message;
    return;
  }
  state.category = Object.keys(CAT_LABELS).find(c => state.byCat[c]) || Object.keys(state.byCat)[0];
  buildCategoryTabs();
  renderStats();
  updateDifficulty();
  const first = pickNextCard();
  if (first) renderCard(first);
  else showCategoryComplete();
}

/* ---------- service worker ---------- */
if ('serviceWorker' in navigator){
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

document.addEventListener('DOMContentLoaded', boot);
