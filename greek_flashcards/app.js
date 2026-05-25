const state = {
  all: [],
  filtered: [],
  index: 0,
  revealed: false,
  direction: 'en-to-gr',
  category: '',
  categories: [],
};

const els = {
  deckName: document.getElementById('deckName'),
  dirToggle: document.getElementById('dirToggle'),
  cardIndex: document.getElementById('cardIndex'),
  cardTotal: document.getElementById('cardTotal'),
  concept: document.getElementById('concept'),
  prompt: document.getElementById('prompt'),
  answer: document.getElementById('answer'),
  answerRow: document.getElementById('answerRow'),
  revealBtn: document.getElementById('revealBtn'),
  notesWrap: document.getElementById('notesWrap'),
  notes: document.getElementById('notes'),
  tags: document.getElementById('tags'),
  prevBtn: document.getElementById('prevBtn'),
  nextBtn: document.getElementById('nextBtn'),
  shuffleBtn: document.getElementById('shuffleBtn'),
  categoryFilter: document.getElementById('categoryFilter'),
};

function formatLines(value) {
  if (Array.isArray(value)) return value.join('\n');
  return value || '';
}

function categoryLabel(id) {
  const c = state.categories.find(c => c.id === id);
  return c ? c.label : (id || '').replace(/_/g, ' ');
}

function render() {
  const card = state.filtered[state.index];
  if (!card) {
    els.concept.textContent = 'No cards match this filter.';
    els.prompt.textContent = '';
    els.answer.textContent = '';
    els.revealBtn.classList.add('hidden');
    els.answerRow.classList.add('hidden');
    els.notesWrap.hidden = true;
    els.tags.innerHTML = '';
    els.cardIndex.textContent = '0';
    els.cardTotal.textContent = '0';
    return;
  }

  els.concept.textContent = card.concept || '';

  const promptArr = state.direction === 'en-to-gr' ? card.en : card.gr;
  const answerArr = state.direction === 'en-to-gr' ? card.gr : card.en;
  els.prompt.textContent = formatLines(promptArr);
  els.answer.textContent = formatLines(answerArr);

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
    const span = document.createElement('span');
    span.className = 'tag tag-category';
    span.textContent = categoryLabel(card.category);
    els.tags.appendChild(span);
  }
  (card.subcategories || []).forEach(sub => {
    const span = document.createElement('span');
    span.className = 'tag tag-sub';
    span.textContent = sub;
    els.tags.appendChild(span);
  });
  (card.tags || []).forEach(t => {
    const span = document.createElement('span');
    span.className = 'tag';
    span.textContent = t;
    els.tags.appendChild(span);
  });

  els.cardIndex.textContent = String(state.index + 1);
  els.cardTotal.textContent = String(state.filtered.length);
}

function reveal() {
  state.revealed = !state.revealed;
  els.answerRow.classList.toggle('hidden', !state.revealed);
  els.revealBtn.textContent = state.revealed ? 'Hide answer' : 'Tap to reveal answer';
}

function next() {
  if (!state.filtered.length) return;
  state.index = (state.index + 1) % state.filtered.length;
  render();
}

function prev() {
  if (!state.filtered.length) return;
  state.index = (state.index - 1 + state.filtered.length) % state.filtered.length;
  render();
}

function shuffle() {
  for (let i = state.filtered.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [state.filtered[i], state.filtered[j]] = [state.filtered[j], state.filtered[i]];
  }
  state.index = 0;
  render();
}

function toggleDirection() {
  state.direction = state.direction === 'en-to-gr' ? 'gr-to-en' : 'en-to-gr';
  els.dirToggle.textContent = state.direction === 'en-to-gr' ? 'EN → GR' : 'GR → EN';
  render();
}

function applyCategoryFilter(cat) {
  state.category = cat;
  state.filtered = cat
    ? state.all.filter(c => c.category === cat)
    : state.all.slice();
  state.index = 0;
  render();
}

function populateCategoryFilter() {
  state.categories.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.label;
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
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    btn.textContent = 'Copied';
    btn.classList.add('copied');
  } catch (e) {
    btn.textContent = 'Failed';
  }
  setTimeout(() => {
    btn.textContent = orig;
    btn.classList.remove('copied');
  }, 1200);
}

document.addEventListener('click', e => {
  const btn = e.target.closest('.copy-btn');
  if (!btn) return;
  e.preventDefault();
  e.stopPropagation();
  const key = btn.dataset.copy;
  const sourceEl = {
    concept: els.concept,
    prompt: els.prompt,
    answer: els.answer,
    notes: els.notes,
  }[key];
  if (sourceEl) copyText(sourceEl.textContent, btn);
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
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

load().catch(err => {
  els.concept.textContent = 'Failed to load cards.json';
  els.prompt.textContent = String(err);
});
