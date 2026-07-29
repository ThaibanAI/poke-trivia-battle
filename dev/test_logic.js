// Headless logic test — loads the actual game scripts in a sandboxed context
// and exercises battle math, question bank, and sprite generation.
const fs = require("fs");
const vm = require("vm");

const sandbox = {
  console,
  localStorage: (() => {
    const store = {};
    return {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; },
    };
  })(),
};
vm.createContext(sandbox);

for (const file of ["js/pokemon.js", "js/storage.js", "js/battle.js"]){
  vm.runInContext(fs.readFileSync(file, "utf8"), sandbox, { filename: file });
}
// `class`/`const` top-level declarations don't auto-attach to the global object
// (only `var`/`function` do) — bridge the names the test needs explicitly.
vm.runInContext(
  `this.ROSTER=ROSTER; this.STARTER_KEYS=STARTER_KEYS; this.CAMPAIGN_KEYS=CAMPAIGN_KEYS;
   this.QuestionBank=QuestionBank; this.Battle=Battle; this.TYPE_CHART=TYPE_CHART;`,
  sandbox
);

const questions = JSON.parse(fs.readFileSync("data/questions.json", "utf8"));
console.log("Loaded questions:", questions.length);

// --- QuestionBank sanity ---
const QuestionBank = sandbox.QuestionBank;
const bank = new QuestionBank(questions);
const seen = new Set();
for (let i = 0; i < 600; i++){
  const q = bank.pick({ easy: 0.4, medium: 0.35, hard: 0.25 });
  if (!q || !q.options || q.options.length !== 4) throw new Error("Bad question shape: " + JSON.stringify(q));
  seen.add(q.id);
}
console.log("QuestionBank.pick worked 600x, unique ids drawn:", seen.size);

// --- Roster / SVG sanity ---
const ROSTER = sandbox.ROSTER, svgFor = sandbox.svgFor, getMon = sandbox.getMon;
for (const mon of ROSTER){
  const svg = svgFor(mon, { facing: "right" });
  if (!svg.includes("<svg")) throw new Error("Bad svg for " + mon.name);
}
console.log("All", ROSTER.length, "roster sprites render OK. Shapes used:",
  [...new Set(ROSTER.map(m=>m.shape))].join(", "));

// --- Type effectiveness sanity ---
const typeMultiplier = sandbox.typeMultiplier;
console.assert(typeMultiplier("Water", ["Fire"]) === 2, "Water should be 2x vs Fire");
console.assert(typeMultiplier("Electric", ["Ground"]) === 0, "Electric should be 0x vs Ground");
console.assert(typeMultiplier("Fire", ["Fire"]) === 0.5, "Fire should resist Fire (0.5x)");
console.assert(typeMultiplier("Normal", ["Ghost"]) === 0, "Normal should be 0x vs Ghost");
console.log("Type chart spot checks passed.");

// --- Full simulated campaign run (random answers) ---
const Battle = sandbox.Battle;
const CAMPAIGN_KEYS = sandbox.CAMPAIGN_KEYS;
const stageDifficultyWeights = sandbox.stageDifficultyWeights;

let stagesWon = 0, longestBattle = 0;
for (let stage = 0; stage < CAMPAIGN_KEYS.length; stage++){
  const player = getMon("charizard");
  const opp = getMon(CAMPAIGN_KEYS[stage]);
  const battle = new Battle(player, opp, { opponentMultiplier: 1 + stage * 0.085 });
  const weights = stageDifficultyWeights(stage, CAMPAIGN_KEYS.length);
  let turns = 0;
  while (!battle.over && turns < 500){
    const q = bank.pick(weights);
    const correct = Math.random() < 0.6; // simulate a decent player
    battle.resolveTurn(correct, q.difficulty, false);
    turns++;
  }
  if (turns >= 500) throw new Error("Battle never ended at stage " + stage);
  longestBattle = Math.max(longestBattle, turns);
  if (battle.winner === "player") stagesWon++;
}
console.log(`Simulated full campaign: player won ${stagesWon}/${CAMPAIGN_KEYS.length} stages (random 60% accuracy). Longest battle: ${longestBattle} turns.`);

// --- Damage never negative / HP never below 0 ---
for (let i = 0; i < 50; i++){
  const battle = new Battle(getMon("pikachu"), getMon("tyranitar"), { opponentMultiplier: 1.5 });
  let turns = 0;
  while (!battle.over && turns < 300){
    battle.resolveTurn(Math.random() < 0.5, "medium", false);
    if (battle.player.curHp < 0 || battle.opponent.curHp < 0) throw new Error("Negative HP!");
    turns++;
  }
}
console.log("HP bounds check passed (no negative HP across 50 simulated battles).");

console.log("\nALL LOGIC TESTS PASSED");
