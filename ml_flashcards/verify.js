/* Self-verification for the ML flashcard deck.
   Run: node ml_flashcards/verify.js
   Uses the REAL pure functions exported from app.js. */
const fs = require("fs");
const path = require("path");
const { buildSequence, buildOptions, vizFor, scene3dFor, answerType } = require("./app.js");

let fail = 0;
const ok  = m => console.log("  ✓ " + m);
const bad = m => { console.log("  ✗ " + m); fail++; };

const CATS = ["origins","foundations","vision_sequence","representations","transformers_llms"];
const VIZ = ["perceptron","mlp","activation","gradient","cnn","rnn","lstm","seq2seq",
             "attention","embedding","vectordb","rag","transformer","scaling","rlhf",
             "agent","tokens","network",
             "supervised","clustering","overfit","dropout","softmax","trainloop","rl",
             "arc","compute"];
const cards = JSON.parse(fs.readFileSync(path.join(__dirname, "cards.json"), "utf8"));

/* 1) schema + integrity ------------------------------------------------ */
console.log("\n[1] cards.json integrity");
const ids = new Set();
let schemaOK = true;
for (const c of cards){
  for (const f of ["id","category","difficulty","concept","a","b","notes","tags","year"]){
    if (!(f in c)){ bad(`card ${c.id||"?"} missing '${f}'`); schemaOK = false; }
  }
  if (ids.has(c.id)){ bad(`duplicate id: ${c.id}`); schemaOK = false; }
  ids.add(c.id);
  if (!Number.isInteger(c.difficulty) || c.difficulty < 1 || c.difficulty > 5){
    bad(`bad difficulty on ${c.id}: ${c.difficulty}`); schemaOK = false;
  }
  if (!CATS.includes(c.category)){ bad(`bad category on ${c.id}`); schemaOK = false; }
  if (!Array.isArray(c.a) || !c.a.length || !Array.isArray(c.b) || !c.b.length){
    bad(`a/b must be non-empty arrays on ${c.id}`); schemaOK = false;
  }
  if (!Number.isInteger(c.year)){ bad(`bad year on ${c.id}`); schemaOK = false; }
}
if (schemaOK) ok(`${cards.length} cards: fields present, no dup ids, difficulty 1-5, categories+years valid`);
for (const cat of CATS){
  const cc = cards.filter(c => c.category === cat);
  const tiers = [1,2,3,4,5].map(t => cc.filter(c => c.difficulty === t).length);
  ok(`${cat}: ${cc.length} cards  L1-L5 = ${tiers.join("/")}`);
}

/* 2) MC draws ---------------------------------------------------------- */
console.log("\n[2] MC options (exhaustive, both directions)");
let mcOK = true, typeOK = true;
for (const dir of ["ab","ba"]){
  for (const card of cards){
    const pool = cards.filter(c => c.category === card.category);
    const { options, correct } = buildOptions(card, pool, dir, undefined, cards);
    if (options.length !== 4 || new Set(options).size !== 4 || !options.includes(correct)){
      bad(`${dir} ${card.id}: bad options`); mcOK = false;
    }
    // A→B options must be the same TYPE as the answer (names with names, etc.)
    if (dir === "ab"){
      const want = answerType(correct);
      const mixed = options.filter(o => answerType(o) !== want);
      if (mixed.length){ bad(`type mix on ${card.id} (${want}): ${mixed.join(" | ")}`); typeOK = false; }
    }
  }
}
if (mcOK) ok(`every card in both A→B and B→A yields 4 distinct options incl. the answer`);
if (typeOK) ok(`A→B options are always the same type as the answer (person / model / term)`);

/* 3) ordering: Origins on-ramp first, then chronological ---------------- */
console.log("\n[3] ordering — Origins first, then chronological");
const seq = buildSequence(cards);
let seqOK = seq.length === cards.length;
if (!seqOK) bad(`sequence covers ${seq.length} of ${cards.length} cards`);
const firstNonOrigin = seq.findIndex(c => c.category !== "origins");
const lastOrigin = seq.map(c => c.category).lastIndexOf("origins");
if (lastOrigin > firstNonOrigin){ bad("Origins cards are not all at the front"); seqOK = false; }
for (let i = firstNonOrigin + 1; i < seq.length; i++){
  if (seq[i].year < seq[i-1].year){ bad(`out of chronological order at ${i}`); seqOK = false; break; }
}
if (seqOK) ok(`${firstNonOrigin} Origins cards first, then chronological (${seq[firstNonOrigin].year} → ${seq[seq.length-1].year})`);

/* 5) HARD REQUIREMENT: every 3D-demo card's question is about the demo --- */
console.log("\n[5] 3D demos are mechanism questions (hard requirement)");
const MECH = /neuron|node|weight|sum|bias|activation|layer|propagat|network|perceptron/;
let d3 = 0, d3OK = true;
for (const c of cards){
  if (scene3dFor(c)){
    d3++;
    const txt = ((c.a[0]||"") + " " + (c.concept||"")).toLowerCase();
    if (!MECH.test(txt)){ bad(`3D card not about its mechanism: ${c.id}`); d3OK = false; }
  }
}
if (d3OK) ok(`${d3} cards use a 3D demo, and every one is a mechanism question`);

/* 6) answer quality: options are proper nouns / concepts, not loose phrases */
console.log("\n[6] answers read as proper nouns / concepts (not phrases)");
const PHRASE = /→|\bvs\.?\b|n['’]t\b|\byou\b|\bevery\b|^[a-z]/;
let aqOK = true;
for (const c of cards){
  if (PHRASE.test(c.b[0])){ bad(`phrase-like answer on ${c.id}: "${c.b[0]}"`); aqOK = false; }
}
if (aqOK) ok(`all ${cards.length} answers are proper nouns / concepts (no arrows, contractions, "vs", or lowercase starts)`);

/* 4) diagram coverage -------------------------------------------------- */
console.log("\n[4] concept diagram coverage");
let vizOK = true;
const used = new Set();
for (const c of cards){
  const v = vizFor(c);
  used.add(v);
  if (!VIZ.includes(v)){ bad(`${c.id}: unknown viz '${v}'`); vizOK = false; }
}
if (vizOK) ok(`all ${cards.length} cards map to a known diagram (${used.size} diagram types in use)`);

/* result --------------------------------------------------------------- */
console.log(fail === 0 ? "\nALL CHECKS PASSED ✓\n" : `\n${fail} CHECK(S) FAILED ✗\n`);
process.exit(fail === 0 ? 0 : 1);
