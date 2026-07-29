// ---------------------------------------------------------------------------
// App shell: screen management, question flow, animation + PWA plumbing.
// ---------------------------------------------------------------------------

let ALL_QUESTIONS = [];
let qbank = null;
let save = loadSave();

const session = {
  mode: null,          // 'campaign' | 'endless'
  pendingMode: null,
  stageIndex: 0,       // campaign stage OR endless win-count
  battle: null,
  timerId: null,
  locked: false,
  weights: { easy: 0.4, medium: 0.35, hard: 0.25 },
  currentQuestion: null,
};

const $ = (id) => document.getElementById(id);

function showScreen(id){
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  $(id).classList.add("active");
  $(id).scrollTop = 0;
}

function typeBadgesHTML(types){
  return types.map(t => `<span class="type-badge" style="background:${TYPE_COLORS[t]}">${t}</span>`).join("");
}

/* --------------------------- Boot --------------------------- */
document.addEventListener("DOMContentLoaded", init);

async function init(){
  wireHomeButtons();
  wireInstallPrompt();
  registerServiceWorker();

  try{
    const res = await fetch("data/questions.json");
    ALL_QUESTIONS = await res.json();
  }catch(e){
    ALL_QUESTIONS = [];
    console.error("Failed to load questions.json", e);
  }
  qbank = new QuestionBank(ALL_QUESTIONS);

  renderHomeStats();
  showScreen("screen-home");
}

/* --------------------------- Home --------------------------- */
function renderHomeStats(){
  const accuracy = save.totalAsked ? Math.round((save.totalCorrect / save.totalAsked) * 100) + "%" : "—";
  $("homeStats").innerHTML = `
    <div class="stat-pill"><span class="n">${save.campaignComplete ? "10/10" : save.campaignStage + "/10"}</span><span class="l">Campaign</span></div>
    <div class="stat-pill"><span class="n">${save.bestStreak}</span><span class="l">Best Streak</span></div>
    <div class="stat-pill"><span class="n">${accuracy}</span><span class="l">Accuracy</span></div>
    <div class="stat-pill"><span class="n">${save.endlessBest}</span><span class="l">Endless Best</span></div>
  `;
  const btn = $("btnCampaign");
  if (save.campaignComplete) btn.textContent = "🔁 Replay Campaign";
  else if (save.campaignStage > 0) btn.textContent = `▶ Continue — Stage ${save.campaignStage + 1}/10`;
  else btn.textContent = "▶ Start Campaign";
}

function wireHomeButtons(){
  $("btnCampaign").onclick = () => {
    if (save.campaignComplete || save.campaignStage === 0 || !save.starter){
      session.pendingMode = "campaign";
      openSelect();
    } else {
      session.mode = "campaign";
      session.stageIndex = save.campaignStage;
      startCampaignBattle(session.stageIndex);
    }
  };
  $("btnEndless").onclick = () => {
    session.pendingMode = "endless";
    openSelect();
  };
  $("btnHow").onclick = () => showScreen("screen-how");
  $("btnBackHome2").onclick = () => showScreen("screen-home");
  $("btnBackHome").onclick = () => showScreen("screen-home");
  $("btnResetSave").onclick = () => {
    if (confirm("Reset all campaign progress and stats? This can't be undone.")){
      resetSave();
      save = loadSave();
      renderHomeStats();
    }
  };
  $("btnResultMenu").onclick = () => { showScreen("screen-home"); renderHomeStats(); };
}

/* --------------------------- Starter select --------------------------- */
function openSelect(){
  const grid = $("starterGrid");
  grid.innerHTML = "";
  STARTER_KEYS.forEach(key => {
    const mon = getMon(key);
    const card = document.createElement("div");
    card.className = "starter-card";
    card.tabIndex = 0;
    card.innerHTML = `
      <div class="mon-svg">${svgFor(mon, { facing: "right" })}</div>
      <div class="s-name">${mon.name}</div>
      <div class="type-badges">${typeBadgesHTML(mon.types)}</div>
    `;
    card.onclick = () => chooseStarter(key);
    grid.appendChild(card);
  });
  showScreen("screen-select");
}

function chooseStarter(key){
  if (session.pendingMode === "campaign"){
    save.starter = key;
    if (save.campaignComplete){ save.campaignComplete = false; save.campaignStage = 0; }
    saveSave(save);
    session.mode = "campaign";
    session.stageIndex = save.campaignStage;
    startCampaignBattle(session.stageIndex);
  } else {
    session.mode = "endless";
    session.endlessStarterKey = key;
    session.stageIndex = 0;
    startEndlessBattle();
  }
}

/* --------------------------- Battle setup --------------------------- */
const CAMPAIGN_LABELS = [
  "Trainer Battle · 1/10","Trainer Battle · 2/10","Trainer Battle · 3/10","Trainer Battle · 4/10",
  "Trainer Battle · 5/10","Trainer Battle · 6/10","Trainer Battle · 7/10","Trainer Battle · 8/10",
  "Elite Battle · 9/10","🏆 CHAMPION BATTLE · 10/10"
];

function startCampaignBattle(stageIndex){
  const playerMon = getMon(save.starter);
  const oppKey = CAMPAIGN_KEYS[stageIndex];
  const multiplier = 1 + stageIndex * 0.085;
  session.mode = "campaign";
  session.stageIndex = stageIndex;
  session.battle = new Battle(playerMon, getMon(oppKey), { opponentMultiplier: multiplier });
  session.weights = stageDifficultyWeights(stageIndex, CAMPAIGN_KEYS.length);
  $("stageBanner").textContent = CAMPAIGN_LABELS[stageIndex];
  enterBattleScreen();
}

function startEndlessBattle(){
  const playerMon = getMon(session.endlessStarterKey);
  const pool = ROSTER.filter(m => m.key !== session.endlessStarterKey);
  const oppMon = pool[Math.floor(Math.random() * pool.length)];
  const multiplier = 1 + session.stageIndex * 0.11;
  session.battle = new Battle(playerMon, oppMon, { opponentMultiplier: multiplier });
  session.weights = stageDifficultyWeights(Math.min(session.stageIndex, 9), 10);
  $("stageBanner").textContent = `Endless Run · Battle ${session.stageIndex + 1}`;
  enterBattleScreen();
}

function enterBattleScreen(){
  const b = session.battle;
  $("playerName").textContent = b.player.name;
  $("oppName").textContent = b.opponent.name;
  $("playerLv").textContent = `Lv.${Math.min(100, 28 + Math.round(session.stageIndex * 6))}`;
  $("oppLv").textContent = `Lv.${Math.min(100, 30 + Math.round(session.stageIndex * 7))}`;
  $("playerTypes").innerHTML = typeBadgesHTML(b.player.types);
  $("oppTypes").innerHTML = typeBadgesHTML(b.opponent.types);
  $("playerSprite").innerHTML = svgFor(b.player, { facing: "right" });
  $("oppSprite").innerHTML = svgFor(b.opponent, { facing: "left" });
  $("playerSprite").className = "sprite-wrap";
  $("oppSprite").className = "sprite-wrap";
  updateHpBars(true);
  $("battleLog").textContent = `Go, ${b.player.name}!`;
  $("streakChip").hidden = true;
  $("fxBanner").className = "fx-banner";
  showScreen("screen-battle");
  askNextQuestion();
}

function updateHpBars(instant){
  const b = session.battle;
  setHp("playerHpFill", b.player.curHp, b.player.maxHp, instant);
  setHp("oppHpFill", b.opponent.curHp, b.opponent.maxHp, instant);
  $("playerHpNum").textContent = `${Math.max(0,b.player.curHp)} / ${b.player.maxHp}`;
}

function setHp(elId, cur, max, instant){
  const el = $(elId);
  const pct = Math.max(0, Math.min(100, (cur / max) * 100));
  if (instant) el.style.transition = "none"; else el.style.transition = "";
  el.style.width = pct + "%";
  el.classList.remove("mid","low");
  if (pct <= 20) el.classList.add("low");
  else if (pct <= 50) el.classList.add("mid");
  if (instant) requestAnimationFrame(()=>{ el.style.transition = ""; });
}

/* --------------------------- Question flow --------------------------- */
const DIFF_TIME = { easy: 18000, medium: 14000, hard: 11000 };

function askNextQuestion(){
  session.locked = false;
  const q = qbank.pick(session.weights);
  session.currentQuestion = q;
  $("qCategory").textContent = q.category;
  $("qText").textContent = q.question;
  $("battleLog").textContent = "What will you do?";
  $("fxBanner").className = "fx-banner";

  const grid = $("answersGrid");
  grid.innerHTML = "";
  const letters = ["A","B","C","D"];
  q.options.forEach((opt, i) => {
    const btn = document.createElement("button");
    btn.className = "answer-btn";
    btn.innerHTML = `<span class="letter">${letters[i]}</span><span>${opt}</span>`;
    btn.onclick = () => handleAnswer(i);
    grid.appendChild(btn);
  });

  startTimer(DIFF_TIME[q.difficulty] || 14000);
}

function startTimer(totalMs){
  clearInterval(session.timerId);
  const start = Date.now();
  const fill = $("timerFill");
  fill.classList.remove("warn","danger");
  fill.style.width = "100%";
  session.timerId = setInterval(() => {
    const elapsed = Date.now() - start;
    const remain = Math.max(0, totalMs - elapsed);
    const pct = (remain / totalMs) * 100;
    fill.style.width = pct + "%";
    fill.classList.toggle("warn", pct <= 40 && pct > 15);
    fill.classList.toggle("danger", pct <= 15);
    if (remain <= 0){
      clearInterval(session.timerId);
      if (!session.locked) handleAnswer(-1);
    }
  }, 100);
}

function handleAnswer(selectedIndex){
  if (session.locked) return;
  session.locked = true;
  clearInterval(session.timerId);

  const q = session.currentQuestion;
  const isCorrect = selectedIndex === q.answer;
  const buttons = Array.from($("answersGrid").children);
  buttons.forEach((btn, i) => {
    btn.classList.add("disabled");
    if (i === q.answer) btn.classList.add("correct");
    else if (i === selectedIndex) btn.classList.add("wrong");
  });

  save.totalAsked++;
  if (isCorrect) save.totalCorrect++;

  const result = session.battle.resolveTurn(isCorrect, q.difficulty, selectedIndex === -1);
  save.bestStreak = Math.max(save.bestStreak, session.battle.bestStreak);
  saveSave(save);

  if (result.streak > 1){
    $("streakChip").hidden = false;
    $("streakVal").textContent = result.streak;
  } else {
    $("streakChip").hidden = true;
  }

  setTimeout(() => playTurnAnimation(result), 700);
}

function playTurnAnimation(result){
  const b = session.battle;
  const attackerIsPlayer = result.attacker === "player";
  const attackerSprite = $(attackerIsPlayer ? "playerSprite" : "oppSprite");
  const defenderSprite = $(attackerIsPlayer ? "oppSprite" : "playerSprite");
  const attackerName = attackerIsPlayer ? b.player.name : b.opponent.name;

  attackerSprite.classList.add("attack-lunge");
  $("battleLog").textContent = result.timedOut
    ? `Time's up! ${attackerName} used ${result.moveName}!`
    : (attackerIsPlayer ? `Correct! ${attackerName} used ${result.moveName}!` : `Wrong! ${attackerName} used ${result.moveName}!`);

  setTimeout(() => {
    defenderSprite.classList.add("hit");
    updateHpBars(false);

    const label = effectivenessLabel(result.multiplier);
    const banner = $("fxBanner");
    let text = result.crit ? "Critical hit!" : (label || "");
    if (text){
      banner.textContent = text;
      banner.className = "fx-banner show";
    }

    setTimeout(() => {
      attackerSprite.classList.remove("attack-lunge");
      defenderSprite.classList.remove("hit");

      if (b.over){
        const defeatedSprite = b.winner === "player" ? $("oppSprite") : $("playerSprite");
        defeatedSprite.classList.add("faint");
        setTimeout(() => endBattle(b.winner), 700);
      } else {
        askNextQuestion();
      }
    }, 900);
  }, 300);
}

/* --------------------------- End of battle --------------------------- */
function endBattle(winner){
  const b = session.battle;
  const won = winner === "player";
  const accuracy = b.askedCount ? Math.round((b.correctCount / b.askedCount) * 100) : 0;

  $("resultIcon").textContent = won ? "🏆" : "💫";
  $("resultStats").innerHTML = `
    <div class="stat-pill"><span class="n">${accuracy}%</span><span class="l">Accuracy</span></div>
    <div class="stat-pill"><span class="n">${b.bestStreak}</span><span class="l">Best Streak</span></div>
    <div class="stat-pill"><span class="n">${b.askedCount}</span><span class="l">Questions</span></div>
  `;

  const nextBtn = $("btnResultNext");
  const retryBtn = $("btnResultRetry");

  if (session.mode === "campaign"){
    if (won){
      save.campaignStage = Math.min(CAMPAIGN_KEYS.length, session.stageIndex + 1);
      const isChampion = session.stageIndex === CAMPAIGN_KEYS.length - 1;
      if (isChampion) save.campaignComplete = true;
      saveSave(save);

      $("resultTitle").textContent = isChampion ? "You are the Champion!" : "Victory!";
      $("resultSubtitle").textContent = isChampion
        ? `${b.opponent.name} has fallen. Your trivia mastery is legendary.`
        : `${b.opponent.name} was defeated.`;
      retryBtn.hidden = true;
      nextBtn.hidden = false;
      nextBtn.textContent = isChampion ? "Return to Menu" : "Next Battle ▶";
      nextBtn.onclick = () => {
        if (isChampion){ showScreen("screen-home"); renderHomeStats(); }
        else startCampaignBattle(save.campaignStage);
      };
    } else {
      $("resultTitle").textContent = "Defeat...";
      $("resultSubtitle").textContent = `${b.player.name} couldn't finish the battle. Give it another shot.`;
      nextBtn.hidden = true;
      retryBtn.hidden = false;
      retryBtn.textContent = "Retry Battle";
      retryBtn.onclick = () => startCampaignBattle(session.stageIndex);
    }
  } else { // endless
    if (won) session.stageIndex++;
    save.endlessBest = Math.max(save.endlessBest, session.stageIndex);
    saveSave(save);

    if (won){
      $("resultTitle").textContent = "Victory!";
      $("resultSubtitle").textContent = `${b.opponent.name} was defeated. Streak: ${session.stageIndex} win${session.stageIndex===1?"":"s"}.`;
      retryBtn.hidden = true;
      nextBtn.hidden = false;
      nextBtn.textContent = "Continue Run ▶";
      nextBtn.onclick = () => startEndlessBattle();
    } else {
      $("resultTitle").textContent = "Run Over";
      $("resultSubtitle").textContent = `You made it ${session.stageIndex} win${session.stageIndex===1?"":"s"} deep.`;
      nextBtn.hidden = true;
      retryBtn.hidden = false;
      retryBtn.textContent = "New Run";
      retryBtn.onclick = () => { session.stageIndex = 0; startEndlessBattle(); };
    }
  }

  showScreen("screen-result");
  renderHomeStats();
}

/* --------------------------- PWA plumbing --------------------------- */
function registerServiceWorker(){
  if ("serviceWorker" in navigator){
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("service-worker.js").catch(() => {});
    });
  }
}

let deferredInstallPrompt = null;
function wireInstallPrompt(){
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    $("btnInstall").hidden = false;
  });
  $("btnInstall").onclick = async () => {
    if (!deferredInstallPrompt) return;
    deferredInstallPrompt.prompt();
    await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    $("btnInstall").hidden = true;
  };
  window.addEventListener("appinstalled", () => { $("btnInstall").hidden = true; });
}
