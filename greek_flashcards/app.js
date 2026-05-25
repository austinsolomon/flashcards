const state = {
  all: [],
  filtered: [],
  index: 0,
  revealed: false,
};

const els = {
  deckName: document.getElementById('deckName'),
  cardIndex: document.getElementById('cardIndex'),
  cardTotal: document.getElementById('cardTotal'),
  concept: document.getElementById('concept'),
  example: document.getElementById('example'),
  answer: document.getElementById('answer'),
  revealBtn: document.getElementById('revealBtn'),
  notesWrap: document.getElementById('notesWrap'),
  notes: document.getElementById('notes'),
  tags: document.getElementById('tags'),
  prevBtn: document.getElementById('prevBtn'),
  nextBtn: document.getElementById('nextBtn'),
  shuffleBtn: document.getElementById('shuffleBtn'),
  tagFilter: document.getElementById('tagFilter'),
};

function formatLines(value) {
  if (Array.isArray(value)) {
    return value
      .map((line, i) => (value.length > 1 ? `${i + 1}. ${line}` : line))
      .join('\n');
  }
  return value || '';
}

function render() {
  const card = state.filtered[state.index];
  if (!card) {
    els.concept.textContent = 'No cards match this filter.';
    els.example.textContent = '';
    els.answer.textContent = '';
    els.revealBtn.classList.add('hidden');
    els.answer.classList.add('hidden');
    els.notesWrap.hidden = true;
    els.tags.innerHTML = '';
    els.cardIndex.textContent = '0';
    els.cardTotal.textContent = '0';
    return;
  }

  els.concept.textContent = card.concept || '';
  els.example.textContent = formatLines(card.example);
  els.answer.textContent = formatLines(card.answer);

  state.revealed = false;
  els.answer.classList.add('hidden');
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
  els.answer.classList.toggle('hidden', !state.revealed);
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

function applyTagFilter(tag) {
  state.filtered = tag
    ? state.all.filter(c => (c.tags || []).includes(tag))
    : state.all.slice();
  state.index = 0;
  render();
}

function populateTagFilter() {
  const tags = new Set();
  state.all.forEach(c => (c.tags || []).forEach(t => tags.add(t)));
  [...tags].sort().forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t;
    els.tagFilter.appendChild(opt);
  });
}

async function load() {
  const res = await fetch('cards.json', { cache: 'no-cache' });
  const data = await res.json();
  els.deckName.textContent = data.deck || 'Flashcards';
  state.all = data.cards || [];
  state.filtered = state.all.slice();
  populateTagFilter();
  render();
}

els.revealBtn.addEventListener('click', reveal);
els.example.addEventListener('click', reveal);
els.nextBtn.addEventListener('click', next);
els.prevBtn.addEventListener('click', prev);
els.shuffleBtn.addEventListener('click', shuffle);
els.tagFilter.addEventListener('change', e => applyTagFilter(e.target.value));

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') next();
  else if (e.key === 'ArrowLeft') prev();
  else if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); reveal(); }
});

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

load().catch(err => {
  els.concept.textContent = 'Failed to load cards.json';
  els.example.textContent = String(err);
});
