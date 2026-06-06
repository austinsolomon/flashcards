/* Self-verification for the ML flashcard deck.
   Run: node ml_flashcards/verify.js
   Uses the REAL pure functions exported from app.js. */
const fs = require("fs");
const path = require("path");
const { targetLevel, cardWeight, buildOptions } = require("./app.js");

let fail = 0;
const ok  = m => console.log("  ✓ " + m);
const bad = m => { console.log("  ✗ " + m); fail++; };

const CATS = ["foundations","vision_sequence","representations","transformers_llms"];
const cards = JSON.parse(fs.readFileSync(path.join(__dirname, "cards.json"), "utf8"));

/* 1) schema + integrity ------------------------------------------------ */
console.log("\n[1] cards.json integrity");
const ids = new Set();
let schemaOK = true;
for (const c of cards){
  const need = ["id","category","difficulty","concept","a","b","notes","tags"];
  for (const f of need){
    if (!(f in c)){ bad(`card ${c.id||"?"} missing field '${f}'`); schemaOK = false; }
  }
  if (ids.has(c.id)){ bad(`duplicate id: ${c.id}`); schemaOK = false; }
  ids.add(c.id);
  if (!Number.isInteger(c.difficulty) || c.difficulty < 1 || c.difficulty > 5){
    bad(`bad difficulty on ${c.id}: ${c.difficulty}`); schemaOK = false;
  }
  if (!CATS.includes(c.category)){ bad(`bad category on ${c.id}: ${c.category}`); schemaOK = false; }
  if (!Array.isArray(c.a) || !c.a.length || !Array.isArray(c.b) || !c.b.length){
    bad(`a/b must be non-empty arrays on ${c.id}`); schemaOK = false;
  }
}
if (schemaOK) ok(`${cards.length} cards, all fields present, no dup ids, difficulty 1-5, categories valid`);

/* distribution report */
for (const cat of CATS){
  const cc = cards.filter(c => c.category === cat);
  const tiers = [1,2,3,4,5].map(t => cc.filter(c => c.difficulty === t).length);
  ok(`${cat}: ${cc.length} cards  L1-L5 = ${tiers.join("/")}`);
}

/* 2) MC draw simulation ------------------------------------------------ */
console.log("\n[2] 60 random MC draws (30 A→B, 30 B→A)");
function byCat(cat){ return cards.filter(c => c.category === cat); }
let drawsOK = true;
function simulate(direction, n){
  for (let i = 0; i < n; i++){
    const card = cards[Math.floor(Math.random() * cards.length)];
    const pool = byCat(card.category);
    const { options, correct } = buildOptions(card, pool, direction);
    if (options.length !== 4){ bad(`${direction} ${card.id}: ${options.length} options (need 4)`); drawsOK = false; }
    if (new Set(options).size !== 4){ bad(`${direction} ${card.id}: options not distinct`); drawsOK = false; }
    if (!options.includes(correct)){ bad(`${direction} ${card.id}: correct answer missing`); drawsOK = false; }
  }
}
simulate("ab", 30);
simulate("ba", 30);
if (drawsOK) ok("all 60 draws produced 4 distinct options containing the correct answer");

/* 3) difficulty function walk ------------------------------------------ */
console.log("\n[3] difficulty function walk");
const walk = [[0,1],[4,1],[5,2],[9,2],[10,3],[14,3],[15,4],[19,4],[20,5]];
let diffOK = true;
const got = [];
for (const [streak, want] of walk){
  const lvl = targetLevel(streak);
  got.push(lvl);
  if (lvl !== want){ bad(`streak ${streak}: got L${lvl}, want L${want}`); diffOK = false; }
}
if (diffOK) ok(`streaks 0,4,5,9,10,14,15,19,20 → L${got.join(",L")}`);

/* 4) weight sanity ----------------------------------------------------- */
console.log("\n[4] weighting sanity");
const sample = cards.find(c => c.difficulty === 3);
const wTarget = cardWeight({difficulty:3}, 3, 0);
const wNeighbor = cardWeight({difficulty:2}, 3, 0);
const wHard = cardWeight({difficulty:5}, 3, 0);
const wBonus = cardWeight({difficulty:3}, 3, 1);
if (wTarget === 5 && wNeighbor === 2 && wHard === 0.4 && Math.abs(wBonus - 8) < 1e-9){
  ok("target=5, neighbor=2, far-harder=0.4, mastery-bonus ×1.6 applied");
} else {
  bad(`weights off: target=${wTarget} neighbor=${wNeighbor} hard=${wHard} bonus=${wBonus}`);
}

/* result --------------------------------------------------------------- */
console.log(fail === 0 ? "\nALL CHECKS PASSED ✓\n" : `\n${fail} CHECK(S) FAILED ✗\n`);
process.exit(fail === 0 ? 0 : 1);
