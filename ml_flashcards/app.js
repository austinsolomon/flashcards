/* ===========================================================
   ML — Neural Net Evolution · Flashcards
   Minimalist quiz engine: MC, two-correct mastery, adaptive
   difficulty meter, chronological timeline. No mascots, no fluff.
   =========================================================== */
"use strict";

/* ----- category metadata (ids must match cards.json) ----- */
const CATEGORIES = [
  { id:"foundations",       label:"Foundations",  short:"Foundations",  instruction:"From ML basics to deep neural nets" },
  { id:"vision_sequence",   label:"Vision & Seq", short:"Vision & Seq", instruction:"CNNs, RNNs, LSTMs & GRUs" },
  { id:"representations",   label:"Represent.",   short:"Represent.",   instruction:"Embeddings, attention & vector search" },
  { id:"transformers_llms", label:"Transf. & LLM",short:"Transf. & LLM",instruction:"Transformers, GPT-3, Claude & agents" },
];

const LS_COUNTS = "nn.correctCounts";
const LS_STATE  = "nn.state";

/* ===========================================================
   Pure logic (mirrored in verify.js — keep identical)
   =========================================================== */

/** streak -> target difficulty tier 1..5 (5 in a row per level). */
function targetLevel(streak){
  return Math.min(5, Math.floor(streak / 5) + 1);
}

/** weight a candidate card by its difficulty vs target + mastery bonus. */
function cardWeight(card, target, count){
  const d = card.difficulty;
  let w;
  if (d === target) w = 5;
  else if (Math.abs(d - target) === 1) w = 2;
  else if (d < target) w = 0.6;   // easier than target
  else w = 0.4;                    // harder than target
  if (count === 1) w *= 1.6;       // 1 of 2 mastery progress
  return w;
}

/** build 4 distinct MC options for a card in a given direction.
    direction "ab": prompt=a, answer=b (options are b-sides)
    direction "ba": prompt=b, answer=a (options are a-sides)        */
function buildOptions(card, pool, direction, rnd){
  rnd = rnd || Math.random;
  const ansKey = direction === "ab" ? "b" : "a";
  const correct = card[ansKey][0];
  const seen = new Set([correct]);
  const distract = [];
  const others = pool.filter(c => c.id !== card.id);
  // shuffle others
  for (let i = others.length - 1; i > 0; i--){
    const j = Math.floor(rnd() * (i + 1));
    [others[i], others[j]] = [others[j], others[i]];
  }
  for (const c of others){
    if (distract.length >= 3) break;
    const v = c[ansKey][0];
    if (!seen.has(v)){ seen.add(v); distract.push(v); }
  }
  const opts = [correct, ...distract];
  // shuffle final options
  for (let i = opts.length - 1; i > 0; i--){
    const j = Math.floor(rnd() * (i + 1));
    [opts[i], opts[j]] = [opts[j], opts[i]];
  }
  return { options: opts, correct };
}

/* exported for node verify */
if (typeof module !== "undefined" && module.exports){
  module.exports = { targetLevel, cardWeight, buildOptions };
}

/* ===========================================================
   App state
   =========================================================== */
const state = {
  cards: [],
  byId: {},
  catId: CATEGORIES[0].id,
  direction: "ab",
  current: null,
  history: [],            // previous card ids for Prev
  answered: false,        // current card has been scored/revealed
  counts: loadCounts(),
  streak: 0,
  best: 0,
  correct: 0,
  total: 0,
  lastRenderedLevel: 1,
  minYear: 1940,
  maxYear: 2025,
};

function loadCounts(){
  try { return JSON.parse(localStorage.getItem(LS_COUNTS)) || {}; }
  catch { return {}; }
}
function saveCounts(){ localStorage.setItem(LS_COUNTS, JSON.stringify(state.counts)); }
function loadStats(){
  try{
    const s = JSON.parse(localStorage.getItem(LS_STATE)) || {};
    state.best = s.best || 0;
    state.catId = (s.catId && CATEGORIES.some(c=>c.id===s.catId)) ? s.catId : state.catId;
    state.direction = s.direction === "ba" ? "ba" : "ab";
  }catch{}
}
function saveStats(){
  localStorage.setItem(LS_STATE, JSON.stringify({
    best: state.best, catId: state.catId, direction: state.direction,
  }));
}

/* ----- card pools ----- */
const isMastered = id => (state.counts[id] || 0) >= 2;
const catCards   = cat => state.cards.filter(c => c.category === cat);
const activePool = cat => catCards(cat).filter(c => !isMastered(c.id));

/* ===========================================================
   DOM
   =========================================================== */
const HAS_DOM = typeof document !== "undefined";
const $ = id => document.getElementById(id);
const el = {};
if (HAS_DOM){
  ["catTabs","instrStrip","streak","best","score","streakChip","resetBtn",
   "meter","meterBadge","meterDots","meterHint",
   "cardConcept","cardYear","timeline","tlMarker","tlMin","tlMax",
   "prompt","options","answerBlock","ansA","ansB","ansNotes","tagsRow",
   "nextBtn","revealBtn","prevBtn","shuffleBtn","dirToggle",
   "overlay","overlayTitle","overlaySub","restartBtn","overlayCloseBtn",
  ].forEach(k => el[k] = $(k));
}

function stars(n){
  return '<span class="stars">' + "★".repeat(n) + "✩".repeat(5 - n) + "</span>";
}
function catMeta(id){ return CATEGORIES.find(c => c.id === id); }

/* ===========================================================
   Rendering
   =========================================================== */
function renderTabs(){
  el.catTabs.innerHTML = "";
  CATEGORIES.forEach(cat => {
    const total = catCards(cat.id).length;
    const remaining = activePool(cat.id).length;
    const b = document.createElement("button");
    b.className = "cat-tab" + (remaining === 0 && total > 0 ? " done" : "");
    b.setAttribute("role","tab");
    b.setAttribute("aria-selected", String(cat.id === state.catId));
    b.innerHTML = `${cat.label}<span class="ct-count">${remaining}/${total}</span>`;
    b.addEventListener("click", () => {
      if (cat.id === state.catId) return;
      state.catId = cat.id;
      saveStats();
      renderTabs();
      renderInstr();
      nextCard(true);
    });
    el.catTabs.appendChild(b);
  });
}

function renderInstr(){
  const cat = catMeta(state.catId);
  const dirLabel = state.direction === "ab" ? "term" : "definition";
  el.instrStrip.innerHTML =
    `<strong>${cat.label}</strong><span class="sep">·</span>` +
    `${cat.instruction}<span class="sep">·</span>` +
    `tap the matching ${dirLabel}`;
}

function renderStats(){
  el.streak.textContent = state.streak;
  el.best.textContent = state.best;
  el.score.textContent = `${state.correct}/${state.total}`;
  el.streakChip.classList.toggle("hot", state.streak >= 5);
}

function renderMeter(){
  const lvl = targetLevel(state.streak);
  el.meterBadge.textContent = "L" + lvl;
  const within = state.streak % 5;             // 0..4 progress in level
  let dots = "";
  for (let i = 0; i < 5; i++){
    const on = (lvl === 5) ? true : i < within;
    dots += `<i class="${on ? "on" : ""}"></i>`;
  }
  el.meterDots.innerHTML = dots;
  el.meterHint.textContent = (lvl === 5)
    ? "MAX DIFFICULTY"
    : `${5 - within} in a row → L${lvl + 1}`;

  if (lvl !== state.lastRenderedLevel){
    const up = lvl > state.lastRenderedLevel;
    el.meter.classList.remove("lvl-up","lvl-down");
    void el.meter.offsetWidth;                 // reflow → retrigger
    el.meter.classList.add(up ? "lvl-up" : "lvl-down");
    setTimeout(() => el.meter.classList.remove("lvl-up","lvl-down"), 650);
    state.lastRenderedLevel = lvl;
  }
}

function renderTimeline(card){
  const span = Math.max(1, state.maxYear - state.minYear);
  const pct = Math.max(0, Math.min(1, (card.year - state.minYear) / span)) * 100;
  el.tlMarker.style.left = pct + "%";
  el.tlMin.textContent = state.minYear;
  el.tlMax.textContent = state.maxYear;
}

function renderCard(card){
  state.current = card;
  state.answered = false;
  const cat = catMeta(card.category);

  el.cardConcept.innerHTML = `${card.concept} ${stars(card.difficulty)}`;
  el.cardYear.textContent = card.year;
  renderTimeline(card);

  const promptText = state.direction === "ab" ? card.a[0] : card.b[0];
  el.prompt.textContent = promptText;

  // options
  const { options, correct } = buildOptions(card, catCards(card.category), state.direction);
  el.options.innerHTML = "";
  options.forEach((txt, i) => {
    const btn = document.createElement("button");
    btn.className = "opt";
    btn.innerHTML = `<span class="opt-key">${"ABCD"[i]}</span><span>${escapeHtml(txt)}</span>`;
    btn.addEventListener("click", () => onAnswer(btn, txt === correct, correct));
    el.options.appendChild(btn);
  });

  // answer block (hidden until answered/revealed)
  el.ansA.textContent = card.a[0];
  el.ansB.textContent = card.b[0];
  el.ansNotes.textContent = card.notes || "";
  el.answerBlock.hidden = true;

  // tags row with per-card difficulty stars
  const tagHtml = (card.tags || []).map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join("");
  el.tagsRow.innerHTML = stars(card.difficulty) + tagHtml;

  el.stage.scrollTop = 0;
}

function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, c =>
    ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

function revealAnswerBlock(correctText){
  el.answerBlock.hidden = false;
  // mark the correct option
  [...el.options.children].forEach(btn => {
    btn.classList.add("locked");
    const label = btn.querySelector("span:last-child").textContent;
    if (label === correctText) btn.classList.add("correct");
  });
}

/* ===========================================================
   Answer handling + mastery
   =========================================================== */
function onAnswer(btn, isCorrect, correctText){
  if (state.answered) return;
  state.answered = true;
  state.total++;

  [...el.options.children].forEach(b => b.classList.add("locked"));

  if (isCorrect){
    btn.classList.add("correct");
    state.correct++;
    state.streak++;
    if (state.streak > state.best) state.best = state.streak;
    const id = state.current.id;
    state.counts[id] = (state.counts[id] || 0) + 1;
    saveCounts();
  } else {
    btn.classList.add("wrong");
    state.streak = 0;
    handleWrong(state.current);
    // also surface the correct option
    [...el.options.children].forEach(b => {
      if (b.querySelector("span:last-child").textContent === correctText)
        b.classList.add("correct");
    });
  }

  revealAnswerBlock(correctText);
  saveStats();
  renderStats();
  renderMeter();
  renderTabs();
}

/** WRONG: reset this card's count, demote one random mastered card
    in the same category back into the pool. */
function handleWrong(card){
  state.counts[card.id] = 0;
  const masteredSameCat = catCards(card.category)
    .filter(c => c.id !== card.id && isMastered(c.id));
  if (masteredSameCat.length){
    const victim = masteredSameCat[Math.floor(Math.random() * masteredSameCat.length)];
    state.counts[victim.id] = 0;
  }
  saveCounts();
}

/* reveal without scoring */
function onReveal(){
  if (state.answered || !state.current) return;
  state.answered = true;
  const correct = state.direction === "ab" ? state.current.b[0] : state.current.a[0];
  revealAnswerBlock(correct);
}

/* ===========================================================
   Card selection
   =========================================================== */
function pickWeighted(pool, excludeId){
  const candidates = pool.filter(c => c.id !== excludeId);
  const list = candidates.length ? candidates : pool;
  if (!list.length) return null;
  const target = targetLevel(state.streak);
  const weights = list.map(c => cardWeight(c, target, state.counts[c.id] || 0));
  const sum = weights.reduce((a, b) => a + b, 0);
  let r = Math.random() * sum;
  for (let i = 0; i < list.length; i++){
    r -= weights[i];
    if (r <= 0) return list[i];
  }
  return list[list.length - 1];
}

function nextCard(fromTabSwitch){
  const pool = activePool(state.catId);
  if (!pool.length){ showComplete(); return; }
  if (state.current && !fromTabSwitch) state.history.push(state.current.id);
  const next = pickWeighted(pool, state.current ? state.current.id : null);
  renderCard(next || pool[0]);
}

function prevCard(){
  if (!state.history.length) return;
  const id = state.history.pop();
  const card = state.byId[id];
  if (card) renderCard(card);
}

function shuffleCard(){
  const pool = activePool(state.catId);
  if (!pool.length){ showComplete(); return; }
  if (state.current) state.history.push(state.current.id);
  let pick;
  do { pick = pool[Math.floor(Math.random() * pool.length)]; }
  while (pool.length > 1 && state.current && pick.id === state.current.id);
  renderCard(pick);
}

/* ===========================================================
   Category complete overlay
   =========================================================== */
function showComplete(){
  const cat = catMeta(state.catId);
  const n = catCards(state.catId).length;
  el.overlayTitle.textContent = "CATEGORY COMPLETE";
  el.overlaySub.textContent = `You mastered all ${n} ${cat.label} cards.`;
  el.overlay.hidden = false;
  renderTabs();
}

function restartCategory(){
  catCards(state.catId).forEach(c => { state.counts[c.id] = 0; });
  saveCounts();
  el.overlay.hidden = true;
  state.current = null;
  state.history = [];
  renderTabs();
  nextCard(true);
}

function closeOverlayPickAnother(){
  // jump to first category that still has cards
  const open = CATEGORIES.find(c => activePool(c.id).length > 0);
  el.overlay.hidden = true;
  if (open){
    state.catId = open.id;
    saveStats();
    state.current = null; state.history = [];
    renderTabs(); renderInstr(); nextCard(true);
  }
}

/* ===========================================================
   Controls
   =========================================================== */
function toggleDirection(){
  state.direction = state.direction === "ab" ? "ba" : "ab";
  el.dirToggle.textContent = state.direction === "ab" ? "A→B" : "B→A";
  saveStats();
  renderInstr();
  if (state.current) renderCard(state.current);
}

function resetAll(){
  if (!confirm("Reset all mastery and stats for every category?")) return;
  state.counts = {};
  state.streak = 0; state.best = 0; state.correct = 0; state.total = 0;
  state.lastRenderedLevel = 1; state.history = []; state.current = null;
  saveCounts(); saveStats();
  renderTabs(); renderInstr(); renderStats(); renderMeter();
  nextCard(true);
}

/* ===========================================================
   Boot
   =========================================================== */
async function boot(){
  loadStats();
  el.dirToggle.textContent = state.direction === "ab" ? "A→B" : "B→A";

  try{
    const res = await fetch("cards.json", { cache: "no-store" });
    state.cards = await res.json();
  }catch(e){
    el.prompt.textContent = "Could not load deck (cards.json).";
    return;
  }
  state.byId = Object.fromEntries(state.cards.map(c => [c.id, c]));
  const years = state.cards.map(c => c.year).filter(Number.isFinite);
  if (years.length){ state.minYear = Math.min(...years); state.maxYear = Math.max(...years); }

  // wire controls
  el.nextBtn.addEventListener("click", () => nextCard(false));
  el.prevBtn.addEventListener("click", prevCard);
  el.revealBtn.addEventListener("click", onReveal);
  el.shuffleBtn.addEventListener("click", shuffleCard);
  el.dirToggle.addEventListener("click", toggleDirection);
  el.resetBtn.addEventListener("click", resetAll);
  el.restartBtn.addEventListener("click", restartCategory);
  el.overlayCloseBtn.addEventListener("click", closeOverlayPickAnother);

  // keyboard niceties (desktop)
  document.addEventListener("keydown", e => {
    if (e.key === "ArrowRight" || e.key === "Enter") nextCard(false);
    else if (e.key === "ArrowLeft") prevCard();
    else if (e.key === " ") { e.preventDefault(); onReveal(); }
    else if (/^[1-4]$/.test(e.key)){
      const btn = el.options.children[+e.key - 1];
      if (btn && !state.answered) btn.click();
    }
  });

  renderTabs();
  renderInstr();
  renderStats();
  renderMeter();
  nextCard(true);

  // PWA service worker
  if ("serviceWorker" in navigator){
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }
}

if (HAS_DOM) boot();
