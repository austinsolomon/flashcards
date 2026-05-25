const state = {
  all: [], filtered: [], index: 0, revealed: false,
  direction: 'en-to-gr', category: '', categories: [],
};

const els = {
  deckName: document.getElementById('deckName'),
  dirToggle: document.getElementById('dirToggle'),
  cardIndex: document.getElementById('cardIndex'),
  cardTotal: document.getElementById('cardTotal'),
  concept: document.getElementById('concept'),
  prompt: document.getElementById('prompt'),
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
};

function lines(v) { return Array.isArray(v) ? v.join('\n') : (v || ''); }

function categoryLabel(id) {
  const c = state.categories.find(c => c.id === id);
  return c ? c.label : (id || '').replace(/_/g, ' ');
}

const LABELS = { en: 'English', gr: 'Greek', phon: 'Phonetic' };

function render() {
  const card = state.filtered[state.index];
  if (!card) {
    els.concept.textContent = 'No cards match this filter.';
    els.prompt.textContent = '';
    els.answerBlocks.innerHTML = '';
    els.revealBtn.classList.add('hidden');
    els.answerRow.classList.add('hidden');
    els.notesWrap.hidden = true;
    els.tags.innerHTML = '';
    els.cardIndex.textContent = '0';
    els.cardTotal.textContent = '0';
    return;
  }

  els.concept.textContent = card.concept || '';

  const promptKey = state.direction === 'en-to-gr' ? 'en' : 'gr';
  els.prompt.textContent = lines(card[promptKey]);

  // Answer side: show the other formats, with labels + copy buttons
  els.answerBlocks.innerHTML = '';
  const answerKeys = ['en', 'gr', 'phon'].filter(k => k !== promptKey && card[k]);
  answerKeys.forEach(k => {
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

  state.revealed = false;
  els.answerRow.classList.add('hidden');
  els.revealBtn.classList.remove('hidden');
  els.revealBtn.textContent = 'Tap to reveal answer';

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
}

function reveal() {
  state.revealed = !state.revealed;
  els.answerRow.classList.toggle('hidden', !state.revealed);
  els.revealBtn.textContent = state.revealed ? 'Hide answer' : 'Tap to reveal answer';
  els.bottomRevealBtn.textContent = state.revealed ? 'Hide' : 'Reveal';
  els.bottomRevealBtn.classList.toggle('revealed', state.revealed);
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
  // dynamic answer blocks store text in data attr; static buttons reference an element id
  let text = btn.dataset.copyText;
  if (!text) {
    const key = btn.dataset.copy;
    const map = { concept: els.concept, prompt: els.prompt, notes: els.notes };
    if (map[key]) text = map[key].textContent;
  }
  if (text) copyText(text, btn);
});

async function load() {
  const res = await fetch('cards.json', { cache: 'no-cache' });
  const data = await res.json();
  els.deckName.textContent = data.deck || 'Flashcards';
  state.all = data.cards || [];
  state.categories = data.categories || [];
  state.filtered = state.all.slice();
  populateCategoryFilter();
  render();
}

els.revealBtn.addEventListener('click', reveal);
els.prompt.addEventListener('click', reveal);
els.bottomRevealBtn.addEventListener('click', reveal);
els.nextBtn.addEventListener('click', next);
els.prevBtn.addEventListener('click', prev);
els.shuffleBtn.addEventListener('click', shuffle);
els.dirToggle.addEventListener('click', toggleDirection);
els.categoryFilter.addEventListener('change', e => applyCategoryFilter(e.target.value));

document.addEventListener('keydown', e => {
  if (e.target.matches('input, textarea, select')) return;
  if (e.key === 'ArrowRight') next();
  else if (e.key === 'ArrowLeft') prev();
  else if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); reveal(); }
  else if (e.key.toLowerCase() === 'd') toggleDirection();
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}

load().catch(err => {
  els.concept.textContent = 'Failed to load cards.json';
  els.prompt.textContent = String(err);
});
