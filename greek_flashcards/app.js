const state = {
  all: [], filtered: [], index: 0, revealed: false,
  direction: 'en-to-gr', category: '', categories: [],
  stats: { streak: 0, best: 0, correct: 0, total: 0 },
  currentAnswered: false,
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
  revealBtn: document.getElementById('revealBtn'),
  notesWrap: document.getElementById('notesWrap'),
  notes: document.getElementById('notes'),
  tags: document.getElementById('tags'),
  prevBtn: document.getElementById('prevBtn'),
  nextBtn: document.getElementById('nextBtn'),
  shuffleBtn: document.getElementById('shuffleBtn'),
  bottomRevealBtn: document.getElementById('bottomRevealBtn'),
  categoryFilter: document.getElementById('categoryFilter'),
  instructionsStrip: document.getElementById('instructionsStrip'),
  statStreak: document.getElementById('statStreak'),
  statBest: document.getElementById('statBest'),
  statScore: document.getElementById('statScore'),
  resetStats: document.getElementById('resetStats'),
};

const INSTRUCTIONS = {
  'Sentence Use': 'Pick the matching Greek form.',
  'Full Paradigm': 'Pick the correct 1st person form (full paradigm follows).',
  'Tense Flip': 'Pick the matching present form.',
  'Identify the Form': 'Pick the correct analysis.',
  'Identify the Case': 'Pick the correct case.',
  'Recognition + Gender': 'Pick the matching Greek noun.',
  'Full Declension': 'Pick the correct singular form.',
  'Singular → Plural': 'Pick the matching transformation.',
  'Phrase Translation': 'Pick the correct Greek phrase.',
  'Greeting + Reply': 'Pick the typical opener.',
  'Situational': 'Pick what you would say.',
  'Word + Example': 'Pick the matching Greek word.',
  'Negation Example': 'Pick the correct negation.',
  'Future Marker': 'Pick the correct future form.',
  'Past Simple': 'Pick the correct aorist form.',
  'Past Simple Example': 'Pick the correct past form.',
  'Recognize': 'Pick the correct translation.',
  'Modal / Infinitive Markers': 'Pick the correct marker.',
  'Demonstratives': 'Pick the correct demonstrative.',
  'Question Words': 'Pick the correct question word.',
  'Yes / No / OK': 'Pick the correct word.',
  'Time (relative)': 'Pick the correct time word.',
  'Time (day frame)': 'Pick the correct day word.',
  'Location & Direction': 'Pick the correct direction word.',
  'Boy / Girl': 'Pick the matching Greek noun.',
  'Travel Phrases': 'Pick the correct travel phrase.',
  'Days of the Week': 'Pick the correct day name.',
  'Numbers 1–10': 'Pick the correct number.',
  'Greek-origin Loanwords': 'Pick the matching Greek word.',
};

function getInstruction(card) {
  const concept = card.concept || '';
  const m = concept.match(/—\s*(.+?)(?:\s*\(|$)/);
  const key = m ? m[1].trim() : '';
  if (INSTRUCTIONS[key]) return INSTRUCTIONS[key];
  for (const k of Object.keys(INSTRUCTIONS)) {
    if (concept.includes(k)) return INSTRUCTIONS[k];
  }
  if (card.category === 'alphabet') return 'Pick the matching letter or name.';
  return 'Pick the correct answer.';
}

function questionType(card) {
  const m = (card.concept || '').match(/—\s*(.+?)(?:\s*\(|$)/);
  return m ? m[1].trim() : '';
}

function lines(v) { return Array.isArray(v) ? v.join('\n') : (v || ''); }

function coreAnswer(card, key) {
  const v = card[key];
  return Array.isArray(v) ? (v[0] || '') : (v || '');
}

function categoryLabel(id) {
  const c = state.categories.find(c => c.id === id);
  return c ? c.label : (id || '').replace(/_/g, ' ');
}

const LABELS = { en: 'English', gr: 'Greek', phon: 'Phonetic' };

// ----- stats -----
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

function renderStats() {
  els.statStreak.textContent = state.stats.streak;
  els.statBest.textContent = state.stats.best;
  els.statScore.textContent = state.stats.correct + ' / ' + state.stats.total;
  els.statStreak.classList.toggle('hot', state.stats.streak >= 5);
}

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
  if (!confirm('Reset streak, best, and score?')) return;
  state.stats = { streak: 0, best: 0, correct: 0, total: 0 };
  saveStats();
  renderStats();
}

// ----- multiple choice -----
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
  if (!options.length) return;

  options.forEach(text => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'mc-option';
    btn.textContent = text;
    btn.addEventListener('click', () => onOptionClick(btn, text, correct));
    els.mcOptions.appendChild(btn);
  });
}

function onOptionClick(btn, picked, correct) {
  if (state.currentAnswered) return;
  state.currentAnswered = true;
  const isCorrect = picked === correct;
  recordAnswer(isCorrect);

  [...els.mcOptions.children].forEach(b => {
    b.classList.add('disabled');
    if (b.textContent === correct) b.classList.add('correct');
    if (b === btn && !isCorrect) b.classList.add('wrong');
  });

  els.feedback.textContent = isCorrect ? 'Correct.' : 'Wrong — correct answer highlighted.';
  els.feedback.classList.remove('hidden');
  els.feedback.classList.toggle('ok', isCorrect);
  els.feedback.classList.toggle('bad', !isCorrect);

  showAnswer();
}

function showAnswer() {
  els.answerRow.classList.remove('hidden');
}

function revealWithoutScoring() {
  if (state.currentAnswered) return;
  state.currentAnswered = true;
  [...els.mcOptions.children].forEach(b => b.classList.add('disabled'));
  showAnswer();
}

// ----- render card -----
function render() {
  const card = state.filtered[state.index];
  if (!card) {
    els.concept.textContent = 'No cards match this filter.';
    els.prompt.textContent = '';
    els.mcOptions.innerHTML = '';
    els.answerBlocks.innerHTML = '';
    els.answerRow.classList.add('hidden');
    els.feedback.classList.add('hidden');
    els.notesWrap.hidden = true;
    els.tags.innerHTML = '';
    els.cardIndex.textContent = '0';
    els.cardTotal.textContent = '0';
    els.instructionsStrip.innerHTML = '<strong>Tip:</strong> Adjust filter.';
    return;
  }

  els.concept.textContent = card.concept || '';
  els.instructionsStrip.innerHTML =
    '<strong>' + (questionType(card) || 'Tip') + ':</strong> ' + getInstruction(card);

  const promptKey = state.direction === 'en-to-gr' ? 'en' : 'gr';
  const answerKey = state.direction === 'en-to-gr' ? 'gr' : 'en';
  els.prompt.textContent = lines(card[promptKey]);

  // Build full-answer blocks (revealed after answering)
  els.answerBlocks.innerHTML = '';
  ['en', 'gr', 'phon'].filter(k => k !== promptKey && card[k]).forEach(k => {
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
  els.answerRow.classList.add('hidden');

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
    s.textContent = categoryLabel(card.category);
    els.tags.appendChild(s);
  }
  (card.subcategories || []).forEach(sub => {
    const s = document.createElement('span');
    s.className = 'tag tag-sub';
    s.textContent = sub;
    els.tags.appendChild(s);
  });
  (card.tags || []).forEach(t => {
    const s = document.createElement('span');
    s.className = 'tag';
    s.textContent = t;
    els.tags.appendChild(s);
  });

  els.cardIndex.textContent = String(state.index + 1);
  els.cardTotal.textContent = String(state.filtered.length);
  els.bottomRevealBtn.textContent = 'Reveal';
  els.bottomRevealBtn.classList.remove('revealed');
}

function next() { if (state.filtered.length) { state.index = (state.index + 1) % state.filtered.length; render(); } }
function prev() { if (state.filtered.length) { state.index = (state.index - 1 + state.filtered.length) % state.filtered.length; render(); } }

function shuffle() {
  for (let i = state.filtered.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [state.filtered[i], state.filtered[j]] = [state.filtered[j], state.filtered[i]];
  }
  state.index = 0; render();
}

function toggleDirection() {
  state.direction = state.direction === 'en-to-gr' ? 'gr-to-en' : 'en-to-gr';
  els.dirToggle.textContent = state.direction === 'en-to-gr' ? 'EN → GR' : 'GR → EN';
  render();
}

function applyCategoryFilter(cat) {
  state.category = cat;
  state.filtered = cat ? state.all.filter(c => c.category === cat) : state.all.slice();
  state.index = 0; render();
}

function populateCategoryFilter() {
  state.categories.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id; opt.textContent = c.label;
    els.categoryFilter.appendChild(opt);
  });
}

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

function sortByCategoryAndType(cards) {
  const catOrder = state.categories.reduce((acc, c, i) => { acc[c.id] = i; return acc; }, {});
  return cards.slice().sort((a, b) => {
    const ca = catOrder[a.category] ?? 999;
    const cb = catOrder[b.category] ?? 999;
    if (ca !== cb) return ca - cb;
    const ta = questionType(a), tb = questionType(b);
    if (ta !== tb) return ta.localeCompare(tb);
    return (a.id || '').localeCompare(b.id || '');
  });
}

async function load() {
  const res = await fetch('cards.json', { cache: 'no-cache' });
  const data = await res.json();
  els.deckName.textContent = data.deck || 'Flashcards';
  state.categories = data.categories || [];
  state.all = sortByCategoryAndType(data.cards || []);
  state.filtered = state.all.slice();
  state.stats = loadStats();
  populateCategoryFilter();
  renderStats();
  render();
}

els.revealBtn.addEventListener('click', revealWithoutScoring);
els.bottomRevealBtn.addEventListener('click', revealWithoutScoring);
els.nextBtn.addEventListener('click', next);
els.prevBtn.addEventListener('click', prev);
els.shuffleBtn.addEventListener('click', shuffle);
els.dirToggle.addEventListener('click', toggleDirection);
els.categoryFilter.addEventListener('change', e => applyCategoryFilter(e.target.value));
els.resetStats.addEventListener('click', resetStats);

document.addEventListener('keydown', e => {
  if (e.target.matches('input, textarea, select')) return;
  if (e.key === 'ArrowRight') next();
  else if (e.key === 'ArrowLeft') prev();
  else if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); revealWithoutScoring(); }
  else if (e.key.toLowerCase() === 'd') toggleDirection();
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}

load().catch(err => {
  els.concept.textContent = 'Failed to load cards.json';
  els.prompt.textContent = String(err);
});
