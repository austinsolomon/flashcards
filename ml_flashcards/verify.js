/* Self-verification for the ML flashcard deck.
   Run: node ml_flashcards/verify.js
   Uses the REAL pure functions exported from app.js. */
const fs = require("fs");
const path = require("path");
const { buildSequence, buildOptions, vizFor } = require("./app.js");

let fail = 0;
const ok  = m => console.log("  ✓ " + m);
const bad = m => { console.log("  ✗ " + m); fail++; };

const CATS = ["foundations","vision_sequence","representations","transformers_llms"];
const VIZ = ["perceptron","mlp","activation","gradient","cnn","rnn","lstm","seq2seq",
             "attention","embedding","vectordb","rag","transformer","scaling","rlhf",
             "agent","tokens","network",
             "supervised","clustering","overfit","dropout","softmax","trainloop","rl"];
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
let mcOK = true;
for (const dir of ["ab","ba"]){
  for (const card of cards){
    const pool = cards.filter(c => c.category === card.category);
    const { options, correct } = buildOptions(card, pool, dir);
    if (options.length !== 4 || new Set(options).size !== 4 || !options.includes(correct)){
      bad(`${dir} ${card.id}: bad options`); mcOK = false;
    }
  }
}
if (mcOK) ok(`every card in both A→B and B→A yields 4 distinct options incl. the answer`);

/* 3) chronological sequence -------------------------------------------- */
console.log("\n[3] chronological sequence ordering");
let seqOK = true;
for (const cat of CATS){
  const seq = buildSequence(cards, cat);
  if (seq.length !== cards.filter(c => c.category === cat).length){
    bad(`${cat}: sequence does not cover all cards`); seqOK = false;
  }
  for (let i = 1; i < seq.length; i++){
    if (seq[i].year < seq[i-1].year){ bad(`${cat}: out of order at ${i}`); seqOK = false; break; }
  }
}
if (seqOK){
  const f = buildSequence(cards, "foundations");
  ok(`each section sorted oldest→newest (foundations: ${f[0].year} … ${f[f.length-1].year})`);
}

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
