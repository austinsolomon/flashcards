const MASTERY_THRESHOLD = 2;

const state = {
  all: [],            // all cards
  inFilter: [],       // all cards matching the current category filter
  filtered: [],       // active pool: inFilter minus mastered
  direction: 'en-to-gr',
  category: '',
  categories: [],
  stats: { streak: 0, best: 0, correct: 0, total: 0 },
  correctCounts: {},  // {cardId: # correct since last wrong}
  currentAnswered: false,
  // navigation (replaces state.index)
  currentCard: null,
  history: [],        // chronological list of cards shown
  historyIdx: -1,     // pointer into history
  // mascot bookkeeping
  heartPlacements: [],// {left, top, color, size, rot} kept until next wrong answer
  kissCount: 0,       // increments on every correct answer; every 10 → profile kiss
};

const els = {
  deckName: document.getElementById('deckName'),
  dirToggle: document.getElementById('dirToggle'),
  cardIndex: document.getElementById('cardIndex'),
  cardTotal: document.getElementById('cardTotal'),
  concept: document.getElementById('concept'),
  prompt: document.getElementById('prompt'),
  mcOptions: document.getElementById('mcOptions'),
  feedback: document.getElementById('feedback'),
  answerRow: document.getElementById('answerRow'),
  answerBlocks: document.getElementById('answerBlocks'),
  notesWrap: document.getElementById('notesWrap'),
  notes: document.getElementById('notes'),
  tags: document.getElementById('tags'),
  nextBtn: document.getElementById('nextBtn'),
  shuffleBtn: document.getElementById('shuffleBtn'),
  categoryFilter: document.getElementById('categoryFilter'),
  instructionsStrip: document.getElementById('instructionsStrip'),
  statStreak: document.getElementById('statStreak'),
  statBest: document.getElementById('statBest'),
  statScore: document.getElementById('statScore'),
  topbarCompact: document.getElementById('topbarCompact'),
  dmLevel: document.getElementById('dmLevel'),
  dmDots: document.getElementById('dmDots'),
  dmHint: document.getElementById('dmHint'),
  resetStats: document.getElementById('resetStats'),
  completeOverlay: document.getElementById('completeOverlay'),
  completeTitle: document.getElementById('completeTitle'),
  completeSubtitle: document.getElementById('completeSubtitle'),
  completeRestart: document.getElementById('completeRestart'),
  completeClose: document.getElementById('completeClose'),
  confetti: document.getElementById('confetti'),
};

const INSTRUCTIONS = {
  Greeting: 'Pick the right greeting.',
  Politeness: 'Pick the polite phrase.',
  'Small talk': 'Pick what you would say.',
  Café: 'Pick the right café phrase.',
  Shopping: 'Pick the right shopping phrase.',
  Directions: 'Pick the correct direction phrase.',
  Travel: 'Pick the right travel phrase.',
  Time: 'Pick the matching time word.',
  Emergency: 'Pick the right emergency phrase.',
  Toast: 'Pick the correct toast.',
  Communication: 'Pick the right phrase.',
  Alphabet: 'Pick the matching Greek letter / name.',
  Number: 'Pick the matching number.',
  Connector: 'Pick the right connector.',
  Function: 'Pick the right word.',
  Noun: 'Pick the matching Greek noun / form.',
  Verb: 'Pick the matching verb form.',
};

function getInstruction(card) {
  const concept = card.concept || '';
  const m = concept.match(/^([^—]+)—/);
  const head = m ? m[1].trim() : '';
  return INSTRUCTIONS[head] || 'Pick the correct answer.';
}

function shortType(card) {
  const m = (card.concept || '').match(/^([^—]+)—\s*(.+?)(?:\s*\(|$)/);
  return m ? `${m[1].trim()} — ${m[2].trim()}` : (card.concept || 'Tip');
}

function lines(v) { return Array.isArray(v) ? v.join('\n') : (v || ''); }
function coreAnswer(card, key) { const v = card[key]; return Array.isArray(v) ? (v[0] || '') : (v || ''); }
function categoryLabel(id) { const c = state.categories.find(c => c.id === id); return c ? c.label : (id || '').replace(/_/g, ' '); }

const LABELS = { en: 'English', gr: 'Greek', phon: 'Phonetic' };

// ---------- persistence ----------
function loadStats() {
  return {
    streak: parseInt(localStorage.getItem('gf.streak') || '0', 10),
    best: parseInt(localStorage.getItem('gf.best') || '0', 10),
    correct: parseInt(localStorage.getItem('gf.correct') || '0', 10),
    total: parseInt(localStorage.getItem('gf.total') || '0', 10),
  };
}
function saveStats() {
  localStorage.setItem('gf.streak', state.stats.streak);
  localStorage.setItem('gf.best', state.stats.best);
  localStorage.setItem('gf.correct', state.stats.correct);
  localStorage.setItem('gf.total', state.stats.total);
}
// Streak → difficulty tier. The single source of truth, shown in the
// big Difficulty Meter under the stats bar. 5 correct in a row per level.
function targetDifficulty(streak) {
  if (streak >= 20) return 5;
  if (streak >= 15) return 4;
  if (streak >= 10) return 3;
  if (streak >= 5)  return 2;
  return 1;
}
// Streak at which the NEXT level kicks in (or null if at max).
function streakForNextLevel(lvl) {
  if (lvl >= 5) return null;
  return [null, 5, 10, 15, 20][lvl];
}

let lastRenderedLevel = 1;

function renderStats() {
  els.statStreak.textContent = state.stats.streak;
  els.statBest.textContent = state.stats.best;
  els.statScore.textContent = state.stats.correct + ' / ' + state.stats.total;
  els.statStreak.classList.toggle('hot', state.stats.streak >= 5);
  renderDifficultyMeter();
}

function renderDifficultyMeter() {
  const bar = els.topbarCompact;
  if (!bar) return;
  const streak = state.stats.streak;
  const lvl = targetDifficulty(streak);

  // Level chip
  els.dmLevel.textContent = 'L' + lvl;
  els.dmLevel.classList.toggle('max', lvl === 5);

  // 5-dot progress
  let dotsHtml = '';
  for (let i = 1; i <= 5; i++) {
    dotsHtml += `<span class="${i <= lvl ? 'on' : 'off'}">●</span>`;
  }
  els.dmDots.innerHTML = dotsHtml;

  // Hint = just the threshold number for next level, or "MAX"
  els.dmHint.textContent = lvl >= 5 ? 'MAX' : String(streakForNextLevel(lvl));

  // Animate the level chip on change
  if (lvl > lastRenderedLevel) {
    bar.classList.remove('dm-up', 'dm-down');
    void bar.offsetWidth;
    bar.classList.add('dm-up');
    setTimeout(() => bar.classList.remove('dm-up'), 720);
  } else if (lvl < lastRenderedLevel) {
    bar.classList.remove('dm-up', 'dm-down');
    void bar.offsetWidth;
    bar.classList.add('dm-down');
    setTimeout(() => bar.classList.remove('dm-down'), 720);
  }
  lastRenderedLevel = lvl;
}
function loadCounts() {
  try {
    const raw = localStorage.getItem('gf.correctCounts');
    if (raw) return JSON.parse(raw);
    // migrate from old gf.mastered key (each mastered card → MASTERY_THRESHOLD)
    const old = JSON.parse(localStorage.getItem('gf.mastered') || '[]');
    const out = {};
    for (const id of old) out[id] = MASTERY_THRESHOLD;
    if (old.length) localStorage.setItem('gf.correctCounts', JSON.stringify(out));
    return out;
  } catch (e) { return {}; }
}
function saveCounts() {
  localStorage.setItem('gf.correctCounts', JSON.stringify(state.correctCounts));
}
function isMastered(id) { return (state.correctCounts[id] || 0) >= MASTERY_THRESHOLD; }
function getCount(id)   { return state.correctCounts[id] || 0; }

function recordAnswer(isCorrect) {
  if (isCorrect) {
    state.stats.streak++;
    state.stats.correct++;
    if (state.stats.streak > state.stats.best) state.stats.best = state.stats.streak;
  } else {
    state.stats.streak = 0;
  }
  state.stats.total++;
  saveStats();
  renderStats();
}

function resetStats() {
  if (!confirm('Reset streak, best, score AND all mastery progress?')) return;
  state.stats = { streak: 0, best: 0, correct: 0, total: 0 };
  state.correctCounts = {};
  state.kissCount = 0;
  clearHearts();
  saveStats();
  saveCounts();
  renderStats();
  applyCategoryFilter(state.category);
}

// ---------- mastery ----------
function bumpCorrect(cardId) {
  const cur = getCount(cardId);
  const next = cur + 1;
  state.correctCounts[cardId] = next;
  saveCounts();
  return { prev: cur, next, justMastered: cur < MASTERY_THRESHOLD && next >= MASTERY_THRESHOLD };
}
function resetCardCount(cardId) {
  delete state.correctCounts[cardId];
  saveCounts();
}
function demoteOneMastered(categoryId) {
  // pick a random mastered card from the same category and reset its count
  const cands = state.inFilter.filter(c => isMastered(c.id) && (!categoryId || c.category === categoryId));
  if (!cands.length) return null;
  const pick = cands[Math.floor(Math.random() * cands.length)];
  resetCardCount(pick.id);
  return pick;
}

function rebuildActivePool() {
  state.filtered = state.inFilter.filter(c => !isMastered(c.id));
}

// Adaptive next-card pick. Higher streak → bias toward higher difficulty.
// Cards with partial progress (count=1) get a small bonus so they reach
// mastery quicker; the just-shown card is excluded if alternatives exist.
function pickNextCard() {
  if (!state.filtered.length) return null;
  if (state.filtered.length === 1) return state.filtered[0];

  const target = targetDifficulty(state.stats.streak);
  const currentId = state.currentCard && state.currentCard.id;

  const weights = state.filtered.map(c => {
    if (c.id === currentId) return 0;             // no immediate repeat
    const d = c.difficulty || 1;
    let w;
    if (d === target)            w = 5;            // strong pull to target
    else if (Math.abs(d - target) === 1) w = 2;    // neighbors
    else if (d < target)         w = 0.6;          // easier — keep some sprinkling
    else                          w = 0.4;          // too-hard — rare peek-ahead
    if ((state.correctCounts[c.id] || 0) === 1) w *= 1.6; // boost partials
    return w;
  });

  const total = weights.reduce((a, b) => a + b, 0);
  if (total <= 0) return state.filtered[Math.floor(Math.random() * state.filtered.length)];
  let r = Math.random() * total;
  for (let i = 0; i < weights.length; i++) {
    r -= weights[i];
    if (r <= 0) return state.filtered[i];
  }
  return state.filtered[state.filtered.length - 1];
}

// ---------- mascot kiss animation ----------
function triggerKiss(profile) {
  const svg = document.querySelector('.mascot-svg');
  if (!svg) return;
  svg.classList.remove('kiss-fire', 'kiss-fire-profile');
  void svg.offsetWidth; // force reflow so animation restarts cleanly on rapid retrigger
  svg.classList.add(profile ? 'kiss-fire-profile' : 'kiss-fire');
  const cleanup = profile ? 'kiss-fire-profile' : 'kiss-fire';
  // remove the class after the animation so it can re-trigger next time
  setTimeout(() => svg.classList.remove(cleanup), profile ? 950 : 520);
}

// Hearts are persistent — every correct answer adds one to the stage and
// it stays in state.heartPlacements + the DOM until the user gets a
// question WRONG (then all hearts clear together).
const HEART_COLORS = ['#ff2d95','#ff6ec7','#ffe600','#c77dff','#00e1ff','#b6ff3a','#ff8a3d','#ffffff'];
function makeHeartEl(p) {
  const h = document.createElement('div');
  h.className = 'heart-burst';
  h.textContent = '♥';
  h.style.left = p.left;
  h.style.top  = p.top;
  h.style.color = p.color;
  h.style.fontSize = p.size;
  h.style.setProperty('--rot', p.rot);
  return h;
}
function spawnHeart() {
  const layer = document.getElementById('heartLayer');
  if (!layer) return;
  // Confine hearts to the empty bands on EITHER SIDE of the bears so
  // they never land in front of the bear/panda. In the 440x150 viewBox
  // brown bear spans ~18-46% and panda spans ~53-81%, so we paint into
  // 0-16% on the left and 84-100% on the right (with a little spill
  // past the SVG bounds since the heart-layer overflows visible).
  const side = Math.random() < 0.5 ? 'left' : 'right';
  const xPct = side === 'left'
    ? (-4 + Math.random() * 18)   // -4% .. 14%
    : (86 + Math.random() * 18);  // 86% .. 104%
  const placement = {
    left: xPct + '%',
    top:  (10 + Math.random() * 75) + '%',
    color: HEART_COLORS[Math.floor(Math.random() * HEART_COLORS.length)],
    size: (16 + Math.random() * 18) + 'px',
    rot:  (Math.random() * 50 - 25) + 'deg',
  };
  state.heartPlacements.push(placement);
  layer.appendChild(makeHeartEl(placement));
}
function spawnHeartBurst(n) {
  for (let i = 0; i < n; i++) spawnHeart();
}
function clearHearts() {
  state.heartPlacements = [];
  const layer = document.getElementById('heartLayer');
  if (!layer) return;
  // animate the existing hearts out, then remove
  [...layer.children].forEach(h => {
    h.classList.add('clearing');
    setTimeout(() => h.remove(), 400);
  });
}
// Re-paint heart layer from state (used when category changes etc.)
function repaintHearts() {
  const layer = document.getElementById('heartLayer');
  if (!layer) return;
  layer.innerHTML = '';
  for (const p of state.heartPlacements) layer.appendChild(makeHeartEl(p));
}

// ---------- multiple choice ----------
function buildOptions(card, answerKey, n = 4) {
  const correct = coreAnswer(card, answerKey);
  if (!correct) return { options: [], correct: '' };
  const sameCat = state.all.filter(c => c.id !== card.id && c.category === card.category);
  const allOthers = state.all.filter(c => c.id !== card.id);
  const pool = sameCat.length >= n - 1 ? sameCat : allOthers;
  const shuffled = pool.slice().sort(() => Math.random() - 0.5);
  const distractors = [];
  const seen = new Set([correct]);
  for (const c of shuffled) {
    if (distractors.length >= n - 1) break;
    const t = coreAnswer(c, answerKey);
    if (t && !seen.has(t)) { distractors.push(t); seen.add(t); }
  }
  const opts = [correct, ...distractors].sort(() => Math.random() - 0.5);
  return { options: opts, correct };
}

function renderMC(card, answerKey) {
  els.mcOptions.innerHTML = '';
  els.feedback.classList.add('hidden');
  els.feedback.textContent = '';
  state.currentAnswered = false;
  const { options, correct } = buildOptions(card, answerKey);
  options.forEach(text => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'mc-option';
    btn.textContent = text;
    btn.addEventListener('click', () => onOptionClick(btn, text, correct, card));
    els.mcOptions.appendChild(btn);
  });
}

function onOptionClick(btn, picked, correct, card) {
  if (state.currentAnswered) return;
  state.currentAnswered = true;
  const isCorrect = picked === correct;
  recordAnswer(isCorrect);

  [...els.mcOptions.children].forEach(b => {
    b.classList.add('disabled');
    if (b.textContent === correct) b.classList.add('correct');
    if (b === btn && !isCorrect) b.classList.add('wrong');
  });

  let msg;
  if (isCorrect) {
    state.kissCount++;
    const isProfileKiss = (state.kissCount % 10 === 0);
    triggerKiss(isProfileKiss);
    spawnHeart();
    if (isProfileKiss) spawnHeartBurst(6); // bonus shower on every 10th
    const { next, justMastered } = bumpCorrect(card.id);
    if (justMastered) {
      msg = 'Correct! ✩ Card MASTERED. ✩';
    } else if (next < MASTERY_THRESHOLD) {
      const remaining = MASTERY_THRESHOLD - next;
      msg = `Correct! (${remaining} more correct to master this card.)`;
    } else {
      msg = 'Correct!';
    }
  } else {
    resetCardCount(card.id);
    clearHearts();
    msg = 'Wrong — hearts cleared. Card progress reset.';
    const demoted = demoteOneMastered(card.category);
    if (demoted) msg += `  (Demoted "${demoted.concept || demoted.id}" back to the pool.)`;
  }

  els.feedback.textContent = msg;
  els.feedback.classList.remove('hidden');
  els.feedback.classList.toggle('ok', isCorrect);
  els.feedback.classList.toggle('bad', !isCorrect);

  els.answerRow.classList.remove('hidden');
  rebuildActivePool();
  renderProgressOnly();
  checkCompletion();
}

function revealWithoutScoring() {
  if (state.currentAnswered) return;
  state.currentAnswered = true;
  [...els.mcOptions.children].forEach(b => b.classList.add('disabled'));
  els.answerRow.classList.remove('hidden');
}

// ---------- completion ----------
function spawnConfetti() {
  els.confetti.innerHTML = '';
  const colors = ['#ff2d95','#ffe600','#00e1ff','#b6ff3a','#c77dff','#ff6ec7'];
  const n = 80;
  for (let i = 0; i < n; i++) {
    const p = document.createElement('div');
    p.className = 'confetto';
    p.style.left = Math.random() * 100 + '%';
    p.style.background = colors[i % colors.length];
    p.style.animationDelay = (Math.random() * 1.2) + 's';
    p.style.animationDuration = (2.6 + Math.random() * 2) + 's';
    p.style.transform = `rotate(${Math.random()*360}deg)`;
    els.confetti.appendChild(p);
  }
}

function showCompletion(allComplete) {
  const catLabel = state.category ? categoryLabel(state.category) : 'all categories';
  const count = state.inFilter.length;
  els.completeTitle.textContent = allComplete && !state.category ? 'DECK COMPLETE!' : 'CATEGORY COMPLETE!';
  els.completeSubtitle.textContent = `You mastered all ${count} ${state.category ? catLabel : 'card'}${count===1?'':'s'}! ✩`;
  els.completeRestart.textContent = state.category ? `Restart ${catLabel}` : 'Restart the whole deck';
  els.completeOverlay.classList.remove('hidden');
  spawnConfetti();
}

function hideCompletion() { els.completeOverlay.classList.add('hidden'); }

function restartCurrentCategory() {
  // un-master all cards in current filter (reset their counts)
  state.inFilter.forEach(c => { delete state.correctCounts[c.id]; });
  saveCounts();
  hideCompletion();
  applyCategoryFilter(state.category);
}

function checkCompletion() {
  if (state.inFilter.length > 0 && state.filtered.length === 0) {
    const allMastered = state.all.every(c => isMastered(c.id));
    setTimeout(() => showCompletion(allMastered), 350);
  }
}

// ---------- render ----------
function renderProgressOnly() {
  const masteredCount = state.inFilter.filter(c => isMastered(c.id)).length;
  els.cardIndex.textContent = String(masteredCount);
  els.cardTotal.textContent = String(state.inFilter.length);
}

function render() {
  const card = state.currentCard;
  const masteredCount = state.inFilter.filter(c => isMastered(c.id)).length;

  if (!card) {
    if (state.inFilter.length > 0 && masteredCount === state.inFilter.length) {
      // Already complete — keep showing overlay
      els.concept.textContent = 'Category complete.';
      els.prompt.textContent = 'Tap "Restart" or pick another category.';
    } else {
      els.concept.textContent = 'No cards match this filter.';
      els.prompt.textContent = '';
    }
    els.mcOptions.innerHTML = '';
    els.answerBlocks.innerHTML = '';
    els.answerRow.classList.add('hidden');
    els.feedback.classList.add('hidden');
    els.notesWrap.hidden = true;
    els.tags.innerHTML = '';
    renderProgressOnly();
    els.instructionsStrip.innerHTML = '<strong>Tip:</strong> Pick a category.';
    return;
  }

  els.concept.textContent = card.concept || '';
  const stars = '★'.repeat(card.difficulty || 1);
  els.instructionsStrip.innerHTML =
    `<strong>${shortType(card)}</strong> <span class="card-stars">${stars}</span> — ${getInstruction(card)}`;

  const promptKey = state.direction === 'en-to-gr' ? 'en' : 'gr';
  const answerKey = state.direction === 'en-to-gr' ? 'gr' : 'en';
  els.prompt.textContent = (card[promptKey] || [])[0] || '';

  // build full-answer blocks (shown after MC answer)
  els.answerBlocks.innerHTML = '';
  els.answerRow.classList.add('hidden');
  state.currentAnswered = false;
  ['en', 'gr', 'phon'].filter(k => card[k]).forEach(k => {
    const block = document.createElement('div');
    block.className = 'ans-block';
    const label = document.createElement('div');
    label.className = 'ans-label';
    label.textContent = LABELS[k];
    const row = document.createElement('div');
    row.className = 'row ans-row';
    const text = document.createElement('div');
    text.className = 'ans-text ans-' + k;
    text.textContent = lines(card[k]);
    const copy = document.createElement('button');
    copy.className = 'copy-btn';
    copy.type = 'button';
    copy.dataset.copyText = lines(card[k]);
    copy.textContent = 'Copy';
    row.appendChild(text);
    row.appendChild(copy);
    block.appendChild(label);
    block.appendChild(row);
    els.answerBlocks.appendChild(block);
  });

  renderMC(card, answerKey);

  if (card.notes) {
    els.notes.textContent = card.notes;
    els.notesWrap.hidden = false;
    els.notesWrap.open = false;
  } else {
    els.notesWrap.hidden = true;
  }

  els.tags.innerHTML = '';
  if (card.category) {
    const s = document.createElement('span');
    s.className = 'tag tag-category';
    s.textContent = categoryLabel(card.category) + ' ' + '★'.repeat(card.difficulty || 1);
    els.tags.appendChild(s);
  }
  const masteryTag = document.createElement('span');
  masteryTag.className = 'tag tag-mastery';
  masteryTag.textContent = `${masteredCount}/${state.inFilter.length} mastered`;
  els.tags.appendChild(masteryTag);

  const progress = getCount(card.id);
  if (progress > 0 && progress < MASTERY_THRESHOLD) {
    const p = document.createElement('span');
    p.className = 'tag tag-progress';
    p.textContent = `${progress}/${MASTERY_THRESHOLD} on this card`;
    els.tags.appendChild(p);
  }
  (card.tags || []).slice(0,3).forEach(t => {
    const s = document.createElement('span');
    s.className = 'tag';
    s.textContent = t;
    els.tags.appendChild(s);
  });

  renderProgressOnly();
}

function gotoCard(card) {
  state.currentCard = card;
  render();
}

function next() {
  // Walk forward through history if user previously hit prev
  if (state.historyIdx < state.history.length - 1) {
    state.historyIdx++;
    gotoCard(state.history[state.historyIdx]);
    return;
  }
  const card = pickNextCard();
  if (!card) { render(); return; }
  state.history.push(card);
  if (state.history.length > 60) state.history.shift();
  state.historyIdx = state.history.length - 1;
  gotoCard(card);
}

function prev() {
  if (state.historyIdx > 0) {
    state.historyIdx--;
    gotoCard(state.history[state.historyIdx]);
  }
}

function shuffle() {
  // With weighted-random selection, "shuffle" = force-pick a new card
  // (resets the forward-history walk so next() draws fresh).
  state.history = state.history.slice(0, state.historyIdx + 1);
  next();
}
function toggleDirection() {
  state.direction = state.direction === 'en-to-gr' ? 'gr-to-en' : 'en-to-gr';
  els.dirToggle.textContent = state.direction === 'en-to-gr' ? 'EN → GR' : 'GR → EN';
  render();
}

// ---------- ordering & filter ----------
function sortByDifficulty(cards) {
  return cards.slice().sort((a, b) => {
    const d = (a.difficulty || 99) - (b.difficulty || 99);
    if (d !== 0) return d;
    return (a.id || '').localeCompare(b.id || '');
  });
}
function applyCategoryFilter(cat) {
  state.category = cat;
  state.inFilter = sortByDifficulty(cat ? state.all.filter(c => c.category === cat) : state.all.slice());
  state.filtered = state.inFilter.filter(c => !isMastered(c.id));
  state.history = [];
  state.historyIdx = -1;
  state.currentCard = null;
  hideCompletion();
  if (state.filtered.length) {
    next(); // adaptive first pick
  } else {
    render();
  }
  checkCompletion();
}
function populateCategoryFilter() {
  state.categories.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id; opt.textContent = c.label;
    els.categoryFilter.appendChild(opt);
  });
}

// ---------- copy ----------
async function copyText(text, btn) {
  const orig = btn.textContent;
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
    }
    btn.textContent = 'Copied'; btn.classList.add('copied');
  } catch (e) { btn.textContent = 'Failed'; }
  setTimeout(() => { btn.textContent = orig; btn.classList.remove('copied'); }, 1200);
}
document.addEventListener('click', e => {
  const btn = e.target.closest('.copy-btn');
  if (!btn) return;
  e.preventDefault(); e.stopPropagation();
  let text = btn.dataset.copyText;
  if (!text) {
    const key = btn.dataset.copy;
    const map = { concept: els.concept, prompt: els.prompt, notes: els.notes };
    if (map[key]) text = map[key].textContent;
  }
  if (text) copyText(text, btn);
});

// ---------- load ----------
async function load() {
  const res = await fetch('cards.json', { cache: 'no-cache' });
  const data = await res.json();
  els.deckName.textContent = data.deck || 'Flashcards';
  state.categories = data.categories || [];
  state.all = sortByDifficulty(data.cards || []);
  state.correctCounts = loadCounts();
  state.stats = loadStats();
  populateCategoryFilter();
  renderStats();
  applyCategoryFilter('');
}

els.nextBtn.addEventListener('click', next);
els.shuffleBtn.addEventListener('click', shuffle);
els.dirToggle.addEventListener('click', toggleDirection);
els.categoryFilter.addEventListener('change', e => applyCategoryFilter(e.target.value));
els.resetStats.addEventListener('click', resetStats);
els.completeRestart.addEventListener('click', restartCurrentCategory);
els.completeClose.addEventListener('click', hideCompletion);

document.addEventListener('keydown', e => {
  if (e.target.matches('input, textarea, select')) return;
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter') { e.preventDefault(); next(); }
  else if (e.key === 'ArrowLeft') prev();
  else if (e.key.toLowerCase() === 'd') toggleDirection();
  else if (e.key === 'Escape') hideCompletion();
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}

load().catch(err => {
  els.concept.textContent = 'Failed to load cards.json';
  els.prompt.textContent = String(err);
});
