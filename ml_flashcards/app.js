/* ===========================================================
   ML — Neural Net Evolution · Flashcards
   A sequential, chronological PRIMER.
   • Cards run in time order (oldest idea -> newest).
   • Multiple-choice with instant feedback + concept diagrams.
   • MISS ONE  ->  RESTART FROM THE BEGINNING of the section.
   • Run-progress meter tracks how far you got cleanly.
   =========================================================== */
"use strict";

const CATEGORIES = [
  { id:"foundations",       label:"Foundations",   instruction:"From ML basics to deep neural nets" },
  { id:"vision_sequence",   label:"Vision & Seq",  instruction:"CNNs, RNNs, LSTMs & GRUs" },
  { id:"representations",   label:"Represent.",    instruction:"Embeddings, attention & vector search" },
  { id:"transformers_llms", label:"Transf. & LLM", instruction:"Transformers, GPT-3, Claude & agents" },
];

const LS_STATE = "nn.state";

/* era label shown on the card (never the specific term — that's the answer) */
const CAT_LABEL = {
  origins:"Origins", foundations:"Foundations", vision_sequence:"Vision & Sequence",
  representations:"Representations", transformers_llms:"Transformers & LLMs",
};

/* ===========================================================
   Pure logic (also imported by verify.js — keep identical)
   =========================================================== */

/** Order cards strictly chronologically: year, then difficulty, then id.
    Omit catId (or pass null) for the full cross-category timeline. */
function buildSequence(cards, catId){
  return cards
    .filter(c => !catId || c.category === catId)
    .slice()
    .sort((a, b) =>
      (a.year - b.year) ||
      (a.difficulty - b.difficulty) ||
      a.id.localeCompare(b.id));
}

/** Build 4 distinct MC options for a card in a given direction.
    "ab": prompt=a, answer=b (options are b-sides)
    "ba": prompt=b, answer=a (options are a-sides) */
function buildOptions(card, pool, direction, rnd){
  rnd = rnd || Math.random;
  const ansKey = direction === "ab" ? "b" : "a";
  const correct = card[ansKey][0];
  const seen = new Set([correct]);
  const distract = [];
  const others = pool.filter(c => c.id !== card.id);
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
  for (let i = opts.length - 1; i > 0; i--){
    const j = Math.floor(rnd() * (i + 1));
    [opts[i], opts[j]] = [opts[j], opts[i]];
  }
  return { options: opts, correct };
}

if (typeof module !== "undefined" && module.exports){
  module.exports = { buildSequence, buildOptions, vizFor,
    get DIAGRAMS(){ return DIAGRAMS; } };
}

/* ===========================================================
   Concept diagrams — minimal inline SVG schematics.
   Small by design; legibility over decoration.
   =========================================================== */
const P = { c:"#5cd6ef", v:"#8b7bff", i:"#cdd7e6", m:"#5d6b82", g:"#36d399", b:"#f2557a", ln:"#2a3a57" };

const C  = (x,y,r,f,st) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${f||"none"}"${st?` stroke="${st}" stroke-width="1.4"`:""}/>`;
const L  = (x1,y1,x2,y2,st,w,ar) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${st}" stroke-width="${w||1.2}"${ar?' marker-end="url(#ah)"':""}/>`;
const RT = (x,y,w,h,f,st,rx) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx==null?5:rx}" fill="${f||"none"}"${st?` stroke="${st}" stroke-width="1.3"`:""}/>`;
const T  = (x,y,s,sz,f,an) => `<text x="${x}" y="${y}" font-size="${sz||9}" fill="${f||P.i}" text-anchor="${an||"middle"}" font-family="JetBrains Mono, ui-monospace, monospace">${s}</text>`;
const PA = (d,st,w,ar) => `<path d="${d}" fill="none" stroke="${st}" stroke-width="${w||1.5}"${ar?' marker-end="url(#ah)"':""}/>`;
const svg = inner => `<svg viewBox="0 0 320 96" class="viz-svg" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg"><defs><marker id="ah" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="${P.m}"/></marker></defs>${inner}</svg>`;

function grid(x,y,w,h,n,st){
  let s = RT(x,y,w,h,"none",st,2);
  for (let k=1;k<n;k++){
    s += L(x+w*k/n,y,x+w*k/n,y+h,st,0.5) + L(x,y+h*k/n,x+w,y+h*k/n,st,0.5);
  }
  return s;
}

const DIAGRAMS = {
  perceptron(){
    let s = [22,48,74].map((y,k)=>C(28,y,4.5,P.c)+L(33,y,134,48,P.ln,1)+T(15,y+3,"x"+(k+1),8,P.m)).join("");
    s += C(150,48,15,"none",P.v)+T(150,52,"Σƒ",10,P.i);
    s += L(165,48,288,48,P.c,1.6,true)+C(298,48,4,P.v)+T(300,32,"ŷ",9,P.v);
    s += T(150,20,"weighted sum → activation",8,P.m);
    return svg(s);
  },
  mlp(){
    const inL=[24,48,72].map(y=>[44,y]), hid=[16,40,64,84].map(y=>[152,y]), out=[36,64].map(y=>[262,y]);
    let s="";
    inL.forEach(a=>hid.forEach(b=>s+=L(a[0],a[1],b[0],b[1],P.ln,0.5)));
    hid.forEach(a=>out.forEach(b=>s+=L(a[0],a[1],b[0],b[1],P.ln,0.5)));
    s += inL.map(p=>C(p[0],p[1],5,P.c)).join("")+hid.map(p=>C(p[0],p[1],5,P.v)).join("")+out.map(p=>C(p[0],p[1],5,P.c)).join("");
    s += T(44,94,"input",8,P.m)+T(152,94,"hidden",8,P.m)+T(262,94,"output",8,P.m);
    return svg(s);
  },
  activation(){
    let s = L(48,80,302,80,P.ln,1,true)+L(60,86,60,14,P.ln,1,true);
    s += PA("M48,80 L60,80 L292,28",P.c,1.9);
    s += PA("M48,76 C150,76 150,28 292,28",P.v,1.5);
    s += T(252,46,"ReLU",8,P.c)+T(250,20,"sigmoid",8,P.v)+T(60,94,"activation functions",8,P.m);
    return svg(s);
  },
  gradient(){
    let s = PA("M48,20 Q172,110 300,20",P.v,1.7);
    s += C(118,46,5,P.c)+PA("M122,50 L156,64",P.c,1.6,true);
    s += T(172,38,"loss",8,P.m)+T(172,92,"gradient descent → minimum",7,P.m);
    return svg(s);
  },
  cnn(){
    let s = grid(14,26,38,38,4,P.ln)+T(33,76,"image",8,P.m);
    s += L(54,45,80,45,P.m,1,true);
    s += RT(82,37,16,16,"rgba(139,123,255,.18)",P.v,3)+T(90,76,"filter",8,P.v);
    s += L(100,45,126,45,P.m,1,true);
    s += grid(128,29,32,32,3,P.ln)+T(144,76,"features",7,P.m);
    s += L(162,45,188,45,P.m,1,true);
    s += grid(190,33,22,22,2,P.c)+T(201,76,"pool",8,P.m);
    s += T(160,92,"local filters · weight sharing",7,P.m);
    return svg(s);
  },
  rnn(){
    const xs=[72,152,232]; let s="";
    xs.forEach((x,k)=>{
      s += RT(x-14,34,28,26,"none",P.v,5)+T(x,51,"h"+k,9,P.i);
      s += C(x,84,4,P.c)+L(x,80,x,61,P.ln,1,true);
      s += L(x,33,x,18,P.ln,1,true)+C(x,14,4,P.c);
    });
    s += L(86,47,136,47,P.c,1.5,true)+L(166,47,216,47,P.c,1.5,true);
    s += T(152,94,"hidden state carried across time",7,P.m);
    return svg(s);
  },
  lstm(){
    let s = RT(54,22,214,52,"rgba(139,123,255,.10)",P.v,9);
    s += L(38,30,300,30,P.c,2,true);
    ["forget","input","output"].forEach((g,k)=>{ const x=104+k*52;
      s += C(x,54,11,"rgba(92,214,239,.12)",P.c)+T(x,57,g[0],9,P.c); });
    s += T(160,16,"cell state (long-term memory)",8,P.c);
    s += T(160,90,"gates: forget · input · output",8,P.m);
    return svg(s);
  },
  seq2seq(){
    let s="";
    [42,68,94].forEach(x=>s+=RT(x,34,20,24,"none",P.c,4));
    s += L(116,46,140,46,P.m,1,true);
    s += RT(142,32,28,28,"rgba(139,123,255,.18)",P.v,4)+T(156,50,"c",10,P.v);
    s += L(172,46,196,46,P.m,1,true);
    [200,226,252].forEach(x=>s+=RT(x,34,20,24,"none",P.c,4));
    s += T(68,72,"encoder",8,P.m)+T(226,72,"decoder",8,P.m);
    s += T(156,92,"one fixed vector = bottleneck",7,P.b);
    return svg(s);
  },
  attention(){
    const ks=[16,40,64,84], w=[1,3.4,1.7,0.8]; let s="";
    ks.forEach((y,k)=>s+=L(80,y,238,50,P.c,w[k]));
    ks.forEach((y,k)=>s+=C(72,y,5,P.c)+T(56,y+3,"k"+(k+1),8,P.m));
    s += C(248,50,9,"none",P.v)+T(248,53,"q",9,P.v);
    s += T(160,14,"attention weights (softmax)",8,P.m);
    s += T(160,94,"focus on the relevant tokens",7,P.m);
    return svg(s);
  },
  embedding(){
    let s = L(34,84,302,84,P.ln,1)+L(44,88,44,12,P.ln,1);
    const pts=[["man",72,72,P.c],["king",150,60,P.v],["woman",106,40,P.c],["queen",184,30,P.v]];
    s += pts.map(p=>C(p[1],p[2],4,p[3])+T(p[1],p[2]-7,p[0],8,p[3])).join("");
    s += PA("M76,71 L146,61",P.m,1.2,true)+PA("M110,39 L180,31",P.m,1.2,true);
    s += T(250,72,"same",7,P.m)+T(250,82,"direction",7,P.m);
    s += T(150,12,"king − man + woman ≈ queen",7,P.m);
    return svg(s);
  },
  vectordb(){
    const far=[[58,26],[92,74],[252,24],[272,64],[214,78],[66,58],[238,70]];
    const near=[[150,40],[150,70],[122,42],[178,44]];
    let s = far.map(p=>C(p[0],p[1],3.2,P.ln)).join("") + near.map(p=>C(p[0],p[1],4,P.c)).join("");
    s += `<circle cx="150" cy="50" r="30" fill="none" stroke="${P.v}" stroke-width="1" stroke-dasharray="3 3"/>`;
    s += C(150,50,4,P.v)+T(150,40,"",8,P.v);
    s += T(150,14,"query vector",8,P.v);
    s += T(150,94,"k-nearest vectors = semantic matches",7,P.m);
    return svg(s);
  },
  rag(){
    const box=(x,w,t,col)=>RT(x,34,w,26,"none",col,5)+T(x+w/2,51,t,7.5,P.i);
    let s = box(6,46,"query",P.m)+L(52,47,64,47,P.m,1,true)
          + box(66,52,"embed",P.c)+L(118,47,130,47,P.m,1,true)
          + box(132,62,"vector DB",P.v)+L(194,47,208,47,P.m,1,true)
          + box(210,42,"LLM",P.c)+L(252,47,266,47,P.m,1,true)
          + box(268,46,"answer",P.m);
    s += T(163,26,"retrieve context",7,P.m);
    s += T(160,92,"retrieval-augmented generation",7,P.m);
    return svg(s);
  },
  transformer(){
    let s = T(161,11,"transformer block",7,P.m);
    s += RT(86,16,150,72,"none",P.v,8);
    s += RT(100,22,122,22,"rgba(92,214,239,.12)",P.c,4)+T(161,37,"multi-head self-attn",7,P.c);
    s += RT(100,52,122,22,"rgba(139,123,255,.12)",P.v,4)+T(161,67,"feed-forward",7.5,P.v);
    s += T(264,46,"× N",11,P.i)+T(264,62,"layers",7,P.m);
    s += T(44,48,"residual",7,P.m)+T(44,60,"+ norm",7,P.m);
    return svg(s);
  },
  scaling(){
    let s = L(48,82,302,82,P.ln,1,true)+L(58,86,58,12,P.ln,1,true);
    s += PA("M62,24 C120,40 210,66 296,74",P.c,2);
    s += T(50,18,"loss",8,P.m,"start")+T(298,94,"scale →",8,P.m,"end");
    s += T(180,42,"bigger model + more data",7,P.m)+T(180,54,"→ lower loss",7,P.m);
    return svg(s);
  },
  rlhf(){
    let s = RT(30,34,54,24,"none",P.c,5)+T(57,49,"model",8,P.i);
    s += RT(116,8,66,22,"none",P.v,5)+T(149,23,"ranked out",7,P.v);
    s += RT(208,34,66,24,"none",P.c,5)+T(241,49,"reward mdl",7,P.i);
    s += RT(120,62,60,22,"none",P.v,5)+T(150,77,"update",8,P.v);
    s += PA("M72,34 L118,24",P.m,1.2,true)+PA("M184,24 L226,34",P.m,1.2,true)
       + PA("M236,58 L178,68",P.m,1.2,true)+PA("M118,70 L74,58",P.m,1.2,true);
    s += T(150,94,"humans rank → reward → align",7,P.m);
    return svg(s);
  },
  agent(){
    let s = RT(28,20,62,24,"none",P.v,5)+T(59,35,"think",8,P.i);
    s += RT(212,20,64,24,"none",P.c,5)+T(244,35,"act · tool",7,P.i);
    s += RT(120,62,64,24,"none",P.v,5)+T(152,77,"observe",8,P.i);
    s += PA("M92,32 L208,32",P.m,1.3,true)+PA("M244,46 L184,64",P.m,1.3,true)+PA("M120,76 L74,46",P.m,1.3,true);
    s += T(152,12,"agent loop: reason → act → observe → repeat",7,P.m);
    return svg(s);
  },
  tokens(){
    const toks=[["un",201],["believ",5821],["able",112],["!",0]];
    let x=40, s="";
    toks.forEach(t=>{ const w=t[0].length*9+18;
      s += RT(x,32,w,24,"rgba(92,214,239,.10)",P.c,4)+T(x+w/2,48,t[0],10,P.i)+T(x+w/2,70,"#"+t[1],7,P.m); x+=w+8; });
    s += T(160,18,"text → tokens → ids",8,P.m);
    return svg(s);
  },
  supervised(){
    let s = T(48,12,"labelled data",7,P.m);
    s += RT(14,18,20,17,"rgba(92,214,239,.14)",P.c,3)+T(40,31,"→ dog",8,P.m,"start");
    s += RT(14,44,20,17,"rgba(139,123,255,.14)",P.v,3)+T(40,57,"→ cat",8,P.m,"start");
    s += L(92,40,120,40,P.m,1,true);
    s += RT(124,27,54,26,"none",P.c,6)+T(151,44,"model",8,P.i);
    s += L(180,40,204,40,P.m,1,true);
    s += T(218,16,"new",7,P.m)+RT(208,24,22,20,"rgba(139,123,255,.10)",P.v,3);
    s += L(232,34,250,34,P.m,1,true)+T(254,38,"cat",10,P.v,"start");
    s += T(160,92,"learn from labelled examples → predict",7,P.m);
    return svg(s);
  },
  clustering(){
    const groups=[
      [[[70,44],[84,54],[60,56],[78,40]], P.c],
      [[[150,66],[164,72],[140,70],[156,58]], P.v],
      [[[214,32],[228,40],[202,42],[224,28]], P.g],
    ];
    let s = T(160,14,"group by similarity — no labels",7,P.m);
    groups.forEach(([pts,col])=>{
      const xs=pts.map(p=>p[0]), ys=pts.map(p=>p[1]);
      const cx=(Math.min(...xs)+Math.max(...xs))/2, cy=(Math.min(...ys)+Math.max(...ys))/2;
      s += `<ellipse cx="${cx}" cy="${cy}" rx="22" ry="17" fill="none" stroke="${col}" stroke-width="1" stroke-dasharray="3 3" opacity="0.65"/>`;
      s += pts.map(p=>C(p[0],p[1],3.6,col)).join("");
    });
    s += T(160,92,"clustering · unsupervised learning",7,P.m);
    return svg(s);
  },
  overfit(){
    let s = L(46,80,300,80,P.ln,1)+L(56,84,56,16,P.ln,1);
    const pts=[[74,60],[104,52],[134,58],[164,44],[194,50],[224,36],[252,42]];
    s += pts.map(p=>C(p[0],p[1],3,P.i)).join("");
    s += PA("M68,64 L258,40",P.c,1.9);
    s += PA("M74,60 L104,52 L134,58 L164,44 L194,50 L224,36 L252,42",P.v,1.4);
    s += T(64,22,"good fit",8,P.c,"start")+T(64,34,"overfit",8,P.v,"start");
    return svg(s);
  },
  dropout(){
    const inL=[[44,26],[44,48],[44,70]], hid=[[152,20],[152,44],[152,68]], out=[[258,34],[258,58]];
    const drop = new Set(["152,44"]);
    let s="";
    inL.forEach(a=>hid.forEach(b=>{ if(drop.has(b.join(","))) return; s+=L(a[0],a[1],b[0],b[1],P.ln,0.5); }));
    hid.forEach(a=>{ if(drop.has(a.join(","))) return; out.forEach(b=>s+=L(a[0],a[1],b[0],b[1],P.ln,0.5)); });
    s += inL.map(p=>C(p[0],p[1],5,P.c)).join("");
    s += hid.map(p=>drop.has(p.join(",")) ? (C(p[0],p[1],5,"none",P.m)+T(p[0],p[1]+3.5,"×",11,P.b)) : C(p[0],p[1],5,P.v)).join("");
    s += out.map(p=>C(p[0],p[1],5,P.c)).join("");
    s += T(160,12,"randomly switch off neurons while training",7,P.m);
    s += T(160,92,"dropout → fights overfitting",7,P.m);
    return svg(s);
  },
  softmax(){
    let s = T(58,12,"logits",7,P.m)+T(256,12,"probabilities",7,P.m);
    [["1.0",1],["2.0",2],["3.0",3]].forEach((d,k)=>{ const x=38+k*26, h=8+d[1]*15;
      s += RT(x,76-h,16,h,"rgba(92,214,239,.20)",P.c,2)+T(x+8,88,d[0],7,P.m); });
    s += L(120,52,148,52,P.m,1,true)+T(170,42,"softmax",8,P.v);
    s += L(192,52,210,52,P.m,1,true);
    [["0.09",0.09],["0.24",0.24],["0.67",0.67]].forEach((d,k)=>{ const x=224+k*26, h=8+d[1]*46;
      s += RT(x,76-h,16,h,"rgba(139,123,255,.22)",P.v,2)+T(x+8,88,d[0],7,P.m); });
    return svg(s);
  },
  trainloop(){
    let s = RT(18,28,28,22,"none",P.c,4)+T(32,43,"in",8,P.i);
    s += L(46,39,70,39,P.m,1,true);
    s += RT(72,26,52,26,"none",P.v,6)+T(98,43,"model",8,P.i);
    s += L(124,39,146,39,P.m,1,true);
    s += RT(148,28,28,22,"none",P.c,4)+T(162,43,"ŷ",9,P.i);
    s += L(176,39,196,39,P.m,1,true);
    s += RT(198,26,42,26,"none",P.b,6)+T(219,43,"loss",8,P.b);
    s += T(248,43,"vs y",8,P.m,"start");
    s += PA("M219,52 L219,72 L98,72 L98,52",P.v,1.3,true);
    s += T(150,12,"forward pass → loss",7,P.m)+T(150,84,"backward pass → update weights",7,P.v);
    return svg(s);
  },
  rl(){
    let s = RT(26,30,66,30,"none",P.c,6)+T(59,49,"agent",8,P.i);
    s += RT(228,30,66,30,"none",P.v,6)+T(261,49,"environment",7,P.i);
    s += PA("M94,38 L226,38",P.m,1.3,true)+T(160,32,"action",7,P.m);
    s += PA("M226,52 L94,52",P.m,1.3,true)+T(160,64,"state · reward",7,P.m);
    s += T(160,14,"reinforcement learning loop",7,P.m);
    return svg(s);
  },
  arc(){
    const box=(x,w,t,col)=>RT(x,36,w,24,"none",col,5)+T(x+w/2,52,t,7.5,P.i);
    let s = box(8,52,"rules",P.m)+L(60,48,72,48,P.m,1,true)
          + box(74,42,"ML",P.c)+L(116,48,128,48,P.m,1,true)
          + box(130,74,"deep learning",P.v)+L(204,48,216,48,P.m,1,true)
          + box(218,52,"LLMs",P.c);
    s += T(160,20,"the arc of this deck",7,P.m);
    s += T(160,86,"hand-coded → learned → many layers → language",7,P.m);
    return svg(s);
  },
  compute(){
    let s = T(160,16,"what can be computed, step by step",7,P.m);
    s += T(42,52,"1011",9,P.c)+L(66,48,98,48,P.m,1,true);
    s += RT(100,33,118,32,"rgba(139,123,255,.12)",P.v,6)+T(159,53,"computation",8,P.i);
    s += L(220,48,252,48,P.m,1,true)+T(278,52,"0110",9,P.c);
    s += T(160,86,"algorithms · logic · the Turing machine",7,P.m);
    return svg(s);
  },
  network(){ return DIAGRAMS.mlp(); },
};

/** Map a card to a diagram type via keywords, with category fallback. */
function vizFor(card){
  const t = (card.concept + " " + (card.b[0]||"") + " " + (card.tags||[]).join(" ")).toLowerCase();
  const rules = [
    [/turing|computation|computer science|computable/, "compute"],
    [/pattern recognition/, "supervised"],
    [/unsupervised|clustering|\bcluster\b|k-means/, "clustering"],
    [/supervised/, "supervised"],
    [/dropout/, "dropout"],
    [/overfit|underfit|bias.?variance|regulari[sz]/, "overfit"],
    [/softmax/, "softmax"],
    [/perceptron|mcculloch|single.?layer|artificial neuron/, "perceptron"],
    [/relu|activation|sigmoid|saturation|tanh/, "activation"],
    [/gradient descent|\bsgd\b|loss function|learning rate|adam|vanishing gradient|exploding|clipping|optimi/, "gradient"],
    [/lstm|\bgru\b|gate|cell state|forget|carousel|peephole/, "lstm"],
    [/seq2seq|sequence-to-sequence|encoder.?decoder|encoder–decoder|teacher forcing|context vector|bottleneck/, "seq2seq"],
    [/\brnn\b|recurren|hidden state|bptt|bidirectional|long-range|jacobian/, "rnn"],
    [/cnn|convolution|filter|kernel|pooling|feature map|receptive|translation invariance|alexnet|lenet|vgg|resnet|residual|skip conn|channel|edge detect|stride|inception|neocognitron|dilated|identity mapping|highway|augmentation|captioning|imagenet/, "cnn"],
    [/\bexa\b|vector database|nearest neighbor|\bann\b|hnsw|faiss|quantization|curse of dimension|semantic search|hybrid search|pinecone|pgvector/, "vectordb"],
    [/\brag\b|retrieval-augmented|retrieval|chunk/, "rag"],
    [/attention|query \/ key|self-attention|multi-head|scaled dot|cross-attention|positional|rope|soft lookup|soft key/, "attention"],
    [/embedding|word2vec|glove|one-hot|analogy|distributional|latent|cosine|dot product|contextual|elmo|skip-gram|cbow|sentence embed|negative sampling|clip|image embed|harris|recommendation/, "embedding"],
    [/token|byte-pair|\bbpe\b/, "tokens"],
    [/scaling|chinchilla|kaplan|emergent/, "scaling"],
    [/rlhf|instruct|constitutional|rlaif|\bhhh\b|helpful, harmless/, "rlhf"],
    [/reinforcement/, "rl"],
    [/agent|tool use|react|claude code|\bmcp\b|agentic|chain-of-thought/, "agent"],
    [/transformer|attention is all|bert|gpt|\bt5\b|decoder-only|causal|masked|mixture of experts|kv cache|block anatomy|next-token|autoregressive/, "transformer"],
    [/backpropagation|\bepoch\b/, "trainloop"],
    [/mlp|multilayer|hidden layer|backprop|feedforward|credit assignment/, "mlp"],
  ];
  for (const [re, type] of rules) if (re.test(t)) return type;
  return { origins:"arc", foundations:"mlp", vision_sequence:"cnn", representations:"embedding", transformers_llms:"transformer" }[card.category] || "network";
}

/* ===========================================================
   Per-card 3D diagrams (canvas 2D wireframe, neon, animated)
   ~25%+ of cards render live in 3D; the rest use the SVGs above.
   =========================================================== */
let vizCtl = null;
function stopViz3D(){ if (vizCtl){ vizCtl.stop(); vizCtl = null; } }

const BOX_E = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
function boxVerts(X,Y,Z,sx,sy,sz){
  const x0=X-sx/2,x1=X+sx/2,y0=Y-sy/2,y1=Y+sy/2,z0=Z-sz/2,z1=Z+sz/2;
  return [[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
}
function proj3(p, a){
  const [x,y,z] = p;
  const cX=Math.cos(a.angX), sX=Math.sin(a.angX);
  const y2 = y*cX - z*sX, z2 = y*sX + z*cX;
  const cY=Math.cos(a.angY), sY=Math.sin(a.angY);
  const x2 = x*cY + z2*sY, z3 = -x*sY + z2*cY;
  const s = a.focal / (a.focal - z3);
  return [a.cx + x2*a.sw*s, a.cy - y2*a.sw*s, z3];
}
const v3line = (ctx,A,B,st,w)=>{ ctx.beginPath(); ctx.moveTo(A[0],A[1]); ctx.lineTo(B[0],B[1]); ctx.strokeStyle=st; ctx.lineWidth=w||1; ctx.stroke(); };
const v3node = (ctx,P,r,fill,stroke)=>{ ctx.beginPath(); ctx.arc(P[0],P[1],r,0,6.2832); if(fill){ctx.fillStyle=fill;ctx.fill();} if(stroke){ctx.lineWidth=1.5;ctx.strokeStyle=stroke;ctx.stroke();} };
const v3lerp = (A,B,t)=>[A[0]+(B[0]-A[0])*t, A[1]+(B[1]-A[1])*t];
const v3txt = (ctx,x,y,s,col,al,sz)=>{ ctx.fillStyle=col||"rgba(205,215,230,.95)"; ctx.font=`${sz||9}px 'JetBrains Mono', monospace`; ctx.textAlign=al||"center"; ctx.fillText(s,x,y); };
function drawBoxWire(ctx,verts,a,col){ const pv=verts.map(p=>proj3(p,a)); ctx.strokeStyle=col; ctx.lineWidth=1.1; ctx.beginPath(); BOX_E.forEach(([i,j])=>{ctx.moveTo(pv[i][0],pv[i][1]);ctx.lineTo(pv[j][0],pv[j][1]);}); ctx.stroke(); }

function mount3D(host, sceneFn){
  host.innerHTML = '<canvas class="viz3d"></canvas>';
  const cv = host.firstChild, ctx = cv.getContext("2d");
  let W=0, H=108, dpr=1, raf=0;
  const a = { angX:-0.32, angY:0.55, focal:5.2, sw:1, cx:0, cy:0 };
  function resize(){
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = host.clientWidth || 300;
    cv.style.width = "100%"; cv.style.height = H + "px";
    cv.width = Math.round(W*dpr); cv.height = Math.round(H*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    a.cx = W/2; a.cy = H/2; a.sw = Math.min(W*0.16, 46);
  }
  const scene = sceneFn();
  const t0 = performance.now();
  function frame(){
    a.angY += 0.006;
    ctx.clearRect(0,0,W,H);
    scene(ctx, a, performance.now()-t0, W, H);
    raf = requestAnimationFrame(frame);
  }
  resize(); window.addEventListener("resize", resize); frame();
  return { stop(){ cancelAnimationFrame(raf); window.removeEventListener("resize", resize); } };
}

/* --- scenes --- */
function scenePerceptron(){
  const inputs = [[-2.4,0.85,0],[-2.4,0,0],[-2.4,-0.85,0]];
  const neuron = [0,0,0], output = [2.4,0,0];
  return (ctx,a,t,W,H)=>{
    const N = proj3(neuron,a), O = proj3(output,a);
    const vals = inputs.map((_,i)=> Math.sin(t/950 + i*2.1)*0.9 );
    inputs.forEach(p => v3line(ctx, proj3(p,a), N, "rgba(120,140,170,.5)", 1));
    v3line(ctx, N, O, "rgba(120,140,170,.5)", 1);
    const ph = (t % 1500) / 1500;                       // signal pulse
    inputs.forEach(p => v3node(ctx, v3lerp(proj3(p,a), N, ph), 3, "#5cd6ef"));
    v3node(ctx, v3lerp(N, O, ph), 3, "#8b7bff");
    inputs.forEach((p,i)=>{ const P=proj3(p,a); v3node(ctx,P,6,"#5cd6ef"); v3txt(ctx,P[0]-16,P[1]+3, vals[i].toFixed(2), "rgba(138,152,173,.95)","end",9); });
    v3node(ctx, N, 13, "rgba(139,123,255,.18)", "#8b7bff"); v3txt(ctx, N[0], N[1]+4, "Σƒ", "#cdd7e6","center",11);
    const sum = vals.reduce((s,v)=>s+v,0), out = 1/(1+Math.exp(-sum));
    v3node(ctx, O, 7, null, "#8b7bff"); v3txt(ctx, O[0]+16, O[1]+3, out.toFixed(2), "#5cd6ef","start",10);
    v3txt(ctx, a.cx, H-6, "one neuron · weighted sum → activation", "rgba(138,152,173,.9)","center",9);
  };
}
function sceneMLP(){
  const L0=[[-2.2,0.9,0],[-2.2,0,0],[-2.2,-0.9,0]];
  const L1=[[0,1.25,0],[0,0.42,0],[0,-0.42,0],[0,-1.25,0]];
  const L2=[[2.2,0.6,0],[2.2,-0.6,0]];
  const layers=[L0,L1,L2];
  return (ctx,a,t,W,H)=>{
    L0.forEach(p=>L1.forEach(q=>v3line(ctx,proj3(p,a),proj3(q,a),"rgba(120,140,170,.32)",0.7)));
    L1.forEach(p=>L2.forEach(q=>v3line(ctx,proj3(p,a),proj3(q,a),"rgba(120,140,170,.32)",0.7)));
    const ph=(t%2400)/2400;
    layers.forEach((Lr,li)=>{ const active = ph>=li/3 && ph<(li+1)/3;
      Lr.forEach(p=>{ const P=proj3(p,a); v3node(ctx,P,6, li===1?"#8b7bff":"#5cd6ef"); if(active) v3node(ctx,P,9,null,"#ffffff"); });
    });
    v3txt(ctx, a.cx, H-6, "signal propagates layer → layer", "rgba(138,152,173,.9)","center",9);
  };
}
function sceneTransformer(){
  const slabs=[]; for(let i=0;i<5;i++) slabs.push(-0.95+i*0.46);
  return (ctx,a,t,W,H)=>{
    slabs.forEach(X=> drawBoxWire(ctx, boxVerts(X,0,0,0.3,1.45,1.15), a, "#8b7bff"));
    const ph=(t%2600)/2600, px=-1.15+ph*2.3;
    v3node(ctx, proj3([px,0,0],a), 4, "#5cd6ef");
    v3txt(ctx, a.cx, H-6, "transformer blocks × N", "rgba(138,152,173,.9)","center",9);
  };
}
const VIZ3D = { perceptron: scenePerceptron, mlp: sceneMLP, network: sceneMLP, transformer: sceneTransformer };

function renderViz(card){
  if (!HAS_DOM) return;
  stopViz3D();
  const type = vizFor(card);
  if (VIZ3D[type]){
    try { vizCtl = mount3D(el.viz, VIZ3D[type]); return; }
    catch(e){ /* fall back to SVG */ }
  }
  el.viz.innerHTML = (DIAGRAMS[type] || DIAGRAMS.network)();
}

/* ===========================================================
   App state
   =========================================================== */
const state = {
  cards: [], byId: {},
  direction: "ab",
  seq: [], index: 0,            // single global chronological sequence
  current: null,
  answered: false,
  pending: null,                // "advance" | "restart" | "finish"
  streak: 0, best: 0,           // streak = cleared-in-a-row this run; best = furthest ever
  correct: 0, total: 0,
  minYear: 1940, maxYear: 2025,
  mode: "intro",                // "intro" (3D overview) | "deck"
  autoTimer: null,              // pending auto-advance after a correct answer
};
function clearAuto(){ if (state.autoTimer){ clearTimeout(state.autoTimer); state.autoTimer = null; } }

function loadState(){
  try{
    const s = JSON.parse(localStorage.getItem(LS_STATE)) || {};
    state.best = s.best || 0;
    state.direction = s.direction === "ba" ? "ba" : "ab";
  }catch{}
}
function saveState(){
  localStorage.setItem(LS_STATE, JSON.stringify({
    best: state.best, direction: state.direction,
  }));
}

const catCards = id => state.cards.filter(c => c.category === id);

/* ===========================================================
   DOM
   =========================================================== */
const HAS_DOM = typeof document !== "undefined";
const $ = id => document.getElementById(id);
const el = {};
if (HAS_DOM){
  ["streak","best","score","streakChip","resetBtn",
   "meter","meterBadge","meterHint","posText","yearText",
   "tline","tlFill","tlTicks","tlMarker",
   "intro","vizCanvas","card",
   "cardConcept","cardYear","viz",
   "prompt","options","answerBlock","ansA","ansB","ansNotes","tagsRow",
   "nextBtn","revealBtn","prevBtn","restartRunBtn","dirToggle","introBtn",
   "overlay","overlayTitle","overlaySub","restartBtn","overlayCloseBtn",
  ].forEach(k => el[k] = $(k));
}

const stars = n => `<span class="stars">${"★".repeat(n)}${"✩".repeat(5-n)}</span>`;
const escapeHtml = s => String(s).replace(/[&<>"']/g, c =>
  ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));

/* ===========================================================
   Rendering
   =========================================================== */
function buildTicks(){
  const span = Math.max(1, state.maxYear - state.minYear);
  const nice = [1950,1970,1990,2010].filter(y => y > state.minYear && y < state.maxYear);
  const years = [state.minYear, ...nice, state.maxYear];
  el.tlTicks.innerHTML = years.map(y => {
    const pct = ((y - state.minYear) / span) * 100;
    const style = y === state.minYear ? "left:0;transform:translateX(0)"
                : y === state.maxYear ? "left:100%;transform:translateX(-100%)"
                : `left:${pct}%`;
    return `<span style="${style}">${y}</span>`;
  }).join("");
}

function renderStats(){
  el.streak.textContent = state.streak;
  el.best.textContent = state.best;
  el.score.textContent = `${state.correct}/${state.total}`;
  el.streakChip.classList.toggle("hot", state.streak >= 5);
}

function renderMeter(){
  const len = state.seq.length || 1;
  const pos = state.index + 1;
  el.meterBadge.textContent = pos;
  el.posText.textContent = `card ${pos}/${len}`;
}

function flashMeter(dir){
  const b = el.meterBadge;
  b.classList.remove("lvl-up","lvl-down");
  void b.offsetWidth;
  b.classList.add(dir === "up" ? "lvl-up" : "lvl-down");
  setTimeout(() => b.classList.remove("lvl-up","lvl-down"), 650);
}

function renderTimeline(card){
  const span = Math.max(1, state.maxYear - state.minYear);
  const pct = Math.max(0, Math.min(1, (card.year - state.minYear) / span)) * 100;
  el.tlMarker.style.left = pct + "%";
  el.tlFill.style.width = pct + "%";
  el.yearText.textContent = card.year;
}

function setNextLabel(){
  el.nextBtn.classList.remove("restart");
  if (!state.answered){ el.nextBtn.textContent = "Next ›"; el.nextBtn.classList.add("is-wait"); return; }
  el.nextBtn.classList.remove("is-wait");
  if (state.pending === "restart"){ el.nextBtn.textContent = "↺ Restart"; el.nextBtn.classList.add("restart"); }
  else if (state.pending === "finish"){ el.nextBtn.textContent = "Finish ✓"; }
  else { el.nextBtn.textContent = "Next ›"; }
}

function renderCard(){
  const card = state.byId[state.seq[state.index]];
  state.current = card;
  state.answered = false;
  state.pending = null;

  el.cardConcept.innerHTML = `${CAT_LABEL[card.category] || ""} ${stars(card.difficulty)}`;
  el.cardYear.textContent = card.year;
  renderTimeline(card);
  renderViz(card);

  el.prompt.textContent = state.direction === "ab" ? card.a[0] : card.b[0];

  const { options, correct } = buildOptions(card, catCards(card.category), state.direction);
  el.options.innerHTML = "";
  options.forEach((txt, i) => {
    const btn = document.createElement("button");
    btn.className = "opt";
    btn.innerHTML = `<span class="opt-key">${"ABCD"[i]}</span><span>${escapeHtml(txt)}</span>`;
    btn.addEventListener("click", () => onAnswer(btn, txt === correct, correct));
    el.options.appendChild(btn);
  });

  el.ansA.textContent = card.a[0];
  el.ansB.textContent = card.b[0];
  el.ansNotes.textContent = card.notes || "";
  el.answerBlock.hidden = true;

  el.tagsRow.innerHTML = stars(card.difficulty) +
    (card.tags || []).map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join("");

  el.stage.scrollTop = 0;
  setNextLabel();
  renderMeter();
}

function revealAnswerBlock(correctText){
  el.answerBlock.hidden = false;
  [...el.options.children].forEach(btn => {
    btn.classList.add("locked");
    if (btn.querySelector("span:last-child").textContent === correctText) btn.classList.add("correct");
  });
}

/* ===========================================================
   Answer handling — the miss-one-restart rule lives here
   =========================================================== */
function onAnswer(btn, isCorrect, correctText){
  if (state.answered) return;
  clearAuto();
  state.answered = true;
  state.total++;
  [...el.options.children].forEach(b => b.classList.add("locked"));

  if (isCorrect){
    btn.classList.add("correct");
    state.correct++;
    state.streak = state.index + 1;                  // cleared this many in a row
    if (state.streak > state.best){ state.best = state.streak; flashMeter("up"); }
    state.pending = (state.index + 1 >= state.seq.length) ? "finish" : "advance";
    saveState(); renderStats(); setNextLabel();
    // auto-advance on correct — no Next click needed (brief green flash first)
    state.autoTimer = setTimeout(() => {
      if (state.pending === "finish") showComplete();
      else goTo(state.index + 1);
    }, 650);
  } else {
    btn.classList.add("wrong");
    state.streak = 0;
    state.pending = "restart";
    flashMeter("down");
    revealAnswerBlock(correctText);                  // show the right answer to learn from
    saveState(); renderStats(); setNextLabel();
  }
}

/* reveal without scoring — does NOT consume the attempt */
function onReveal(){
  if (state.mode !== "deck" || state.answered || !state.current) return;
  el.answerBlock.hidden = false;
  const correct = state.direction === "ab" ? state.current.b[0] : state.current.a[0];
  [...el.options.children].forEach(btn => {
    if (btn.querySelector("span:last-child").textContent === correct) btn.classList.add("correct");
  });
}

/* ===========================================================
   Navigation
   =========================================================== */
function goTo(idx){
  clearAuto();
  state.index = Math.max(0, Math.min(state.seq.length - 1, idx));
  renderCard();
}

function nextAction(){
  if (state.mode === "intro"){ exitIntroToDeck(); return; }
  clearAuto();
  if (!state.answered){
    // nudge the learner to answer first
    el.options.classList.remove("nudge"); void el.options.offsetWidth; el.options.classList.add("nudge");
    return;
  }
  if (state.pending === "finish"){ showComplete(); return; }
  if (state.pending === "restart"){ state.streak = 0; goTo(0); renderStats(); return; }
  goTo(state.index + 1);
}

function prevCard(){ if (state.mode === "deck" && state.index > 0) goTo(state.index - 1); }

function restartRun(){
  if (state.mode === "intro") showDeck();
  el.overlay.hidden = true;
  state.streak = 0; goTo(0); renderStats();
}

/* ===========================================================
   Timeline-complete overlay
   =========================================================== */
function showComplete(){
  el.overlayTitle.textContent = "TIMELINE COMPLETE";
  el.overlaySub.textContent =
    `You traced all ${state.seq.length} ideas from ${state.minYear} to ${state.maxYear} — no misses.`;
  el.overlay.hidden = false;
}
function overlayRestart(){ el.overlay.hidden = true; restartRun(); }
function overlayNext(){ el.overlay.hidden = true; enterIntro(); }

/* ===========================================================
   Controls
   =========================================================== */
function toggleDirection(){
  state.direction = state.direction === "ab" ? "ba" : "ab";
  el.dirToggle.textContent = state.direction === "ab" ? "A→B" : "B→A";
  saveState();
  if (state.current) renderCard();
}

function resetAll(){
  if (!confirm("Reset your best run and stats?")) return;
  state.best = 0;
  state.streak = 0; state.correct = 0; state.total = 0; state.index = 0;
  saveState();
  renderStats(); renderCard();
}

/* ===========================================================
   Intro — dependency-free 3D LLM overview (canvas 2D wireframe)
   =========================================================== */
let introCtl = null;

function enterIntro(){
  stopViz3D();
  clearAuto();
  state.mode = "intro";
  document.body.classList.add("is-intro");
  el.intro.hidden = false; el.card.hidden = true;
  el.nextBtn.textContent = "Begin ›";
  el.nextBtn.classList.remove("is-wait","restart");
  stopIntroViz(); initIntroViz();
}
function showDeck(){
  stopIntroViz();
  state.mode = "deck";
  document.body.classList.remove("is-intro");
  el.intro.hidden = true; el.card.hidden = false;
}
function exitIntroToDeck(){ showDeck(); renderCard(); }
function stopIntroViz(){ if (introCtl){ introCtl.stop(); introCtl = null; } }

function initIntroViz(){
  const cv = el.vizCanvas;
  if (!cv || !cv.getContext) return;
  const ctx = cv.getContext("2d");
  let W = 0, H = 0, cx = 0, cy = 0, dpr = 1, raf = 0;
  let angY = 0.7, angX = -0.32, dragging = false, lastX = 0, lastY = 0;
  const focal = 5.4;

  function resize(){
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = cv.clientWidth || 320; H = cv.clientHeight || 240;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cx = W / 2; cy = H / 2;
  }

  // ---- scene: tokens -> embeddings -> transformer xN -> output ----
  const boxes = [], lines = [], labels = [];
  const addBox = (X,Y,Z,sx,sy,sz,col) => {
    const x0=X-sx/2,x1=X+sx/2,y0=Y-sy/2,y1=Y+sy/2,z0=Z-sz/2,z1=Z+sz/2;
    boxes.push({col, v:[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],
      e:[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]});
  };
  for (let i=0;i<4;i++) addBox(-2.7, 0.6-i*0.4, 0, 0.22,0.22,0.22, "c");      // tokens
  for (let i=0;i<4;i++) addBox(-1.75, 0.6-i*0.4, 0, 0.26,0.26,0.5, "v");      // embeddings
  for (let i=0;i<5;i++) addBox(-0.5+i*0.42, 0, 0, 0.28,1.5,1.2, "v");         // transformer stack
  [0.5,1.1,0.8,1.6].forEach((h,i)=> addBox(2.5, -0.85+h/2, -0.5+i*0.33, 0.18,h,0.18, "c")); // output bars
  lines.push([[-2.45,0,0],[-1.95,0,0]]);
  lines.push([[-1.5,0,0],[-0.75,0,0]]);
  lines.push([[1.25,0,0],[2.35,0,0]]);
  labels.push({p:[-2.7,-1.05,0],t:"tokens"});
  labels.push({p:[-1.75,-1.25,0],t:"embeddings"});
  labels.push({p:[0.35,-1.35,0],t:"transformer × N"});
  labels.push({p:[2.5,-1.5,0],t:"next-token"});

  function project(p){
    const [x,y,z] = p;
    const cX=Math.cos(angX), sX=Math.sin(angX);
    const y2 = y*cX - z*sX, z2 = y*sX + z*cX;
    const cY=Math.cos(angY), sY=Math.sin(angY);
    const x2 = x*cY + z2*sY, z3 = -x*sY + z2*cY;
    const world = Math.min(W,H) * 0.17;
    const scale = focal / (focal - z3);
    return [cx + x2*world*scale, cy - y2*world*scale, z3];
  }

  function frame(){
    if (!dragging) angY += 0.004;
    ctx.clearRect(0,0,W,H);
    ctx.lineWidth = 1; ctx.strokeStyle = "rgba(120,140,170,.45)";
    lines.forEach(Ln => { const a=project(Ln[0]), b=project(Ln[1]); ctx.beginPath(); ctx.moveTo(a[0],a[1]); ctx.lineTo(b[0],b[1]); ctx.stroke(); });
    boxes.map(B => { const pv=B.v.map(project); return {B,pv,az:pv.reduce((s,p)=>s+p[2],0)/8}; })
         .sort((a,b)=>a.az-b.az)
         .forEach(({B,pv}) => {
            ctx.strokeStyle = B.col==="c" ? "rgba(92,214,239,.92)" : "rgba(139,123,255,.92)";
            ctx.lineWidth = 1.1; ctx.beginPath();
            B.e.forEach(([i,j]) => { ctx.moveTo(pv[i][0],pv[i][1]); ctx.lineTo(pv[j][0],pv[j][1]); });
            ctx.stroke();
         });
    // a single data point travelling through the factory (North Star seed)
    const phase = (performance.now() % 5200) / 5200;       // 0..1 loop
    const px = -2.9 + phase * 5.5;                          // tokens -> output
    const py = 0.12 * Math.sin(phase * Math.PI * 6);        // slight wobble
    for (let k = 0; k < 5; k++){                            // short comet trail
      const tp = project([px - k * 0.16, py, 0]);
      const a = (1 - k / 5) * 0.9;
      ctx.beginPath(); ctx.arc(tp[0], tp[1], 3.4 - k * 0.5, 0, 6.2832);
      ctx.fillStyle = `rgba(92,214,239,${a})`; ctx.fill();
    }
    const head = project([px, py, 0]);
    ctx.beginPath(); ctx.arc(head[0], head[1], 5.2, 0, 6.2832);
    ctx.fillStyle = "rgba(255,255,255,.95)"; ctx.fill();
    ctx.shadowColor = "rgba(92,214,239,.9)"; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.arc(head[0], head[1], 3, 0, 6.2832); ctx.fillStyle = "#5cd6ef"; ctx.fill();
    ctx.shadowBlur = 0;

    ctx.fillStyle = "rgba(138,152,173,.92)"; ctx.font = "10px 'JetBrains Mono', monospace"; ctx.textAlign = "center";
    labels.forEach(Lb => { const p=project(Lb.p); ctx.fillText(Lb.t, p[0], p[1]); });
    raf = requestAnimationFrame(frame);
  }

  const onDown = e => { dragging=true; lastX=e.clientX; lastY=e.clientY; try{ cv.setPointerCapture(e.pointerId); }catch{} };
  const onMove = e => { if(!dragging) return; angY+=(e.clientX-lastX)*0.01; angX+=(e.clientY-lastY)*0.005; angX=Math.max(-1.2,Math.min(0.5,angX)); lastX=e.clientX; lastY=e.clientY; };
  const onUp = () => { dragging=false; };
  cv.addEventListener("pointerdown", onDown);
  cv.addEventListener("pointermove", onMove);
  window.addEventListener("pointerup", onUp);
  window.addEventListener("resize", resize);

  resize(); frame();
  introCtl = { stop(){
    cancelAnimationFrame(raf);
    cv.removeEventListener("pointerdown", onDown);
    cv.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", onUp);
    window.removeEventListener("resize", resize);
  }};
}

/* ===========================================================
   Boot
   =========================================================== */
async function boot(){
  loadState();
  el.dirToggle.textContent = state.direction === "ab" ? "A→B" : "B→A";

  try{
    const res = await fetch("cards.json", { cache: "no-store" });
    state.cards = await res.json();
  }catch{
    el.prompt.textContent = "Could not load deck (cards.json).";
    return;
  }
  state.byId = Object.fromEntries(state.cards.map(c => [c.id, c]));
  const years = state.cards.map(c => c.year).filter(Number.isFinite);
  if (years.length){ state.minYear = Math.min(...years); state.maxYear = Math.max(...years); }

  state.seq = buildSequence(state.cards).map(c => c.id);   // full chronological timeline
  buildTicks();

  el.nextBtn.addEventListener("click", nextAction);
  el.prevBtn.addEventListener("click", prevCard);
  el.revealBtn.addEventListener("click", onReveal);
  el.restartRunBtn.addEventListener("click", restartRun);
  el.introBtn.addEventListener("click", enterIntro);
  el.dirToggle.addEventListener("click", toggleDirection);
  el.resetBtn.addEventListener("click", resetAll);
  el.restartBtn.addEventListener("click", overlayRestart);
  el.overlayCloseBtn.addEventListener("click", overlayNext);

  document.addEventListener("keydown", e => {
    if (e.key === "ArrowRight" || e.key === "Enter") nextAction();
    else if (e.key === "ArrowLeft") prevCard();
    else if (e.key === " "){ e.preventDefault(); onReveal(); }
    else if (/^[1-4]$/.test(e.key)){
      const btn = el.options.children[+e.key - 1];
      if (btn && !state.answered) btn.click();
    }
  });

  renderStats();
  enterIntro();   // show the 3D LLM overview first; "Begin ›" starts the deck

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
}

if (HAS_DOM) boot();
