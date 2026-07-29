// ---------------------------------------------------------------------------
// Battle engine — pure logic, no DOM access. app.js renders what this returns.
// ---------------------------------------------------------------------------

const DIFF_BONUS = { easy: 0, medium: 0.15, hard: 0.32 };

function scaledMon(mon, multiplier){
  const hp = Math.round(mon.hp * multiplier);
  return {
    key: mon.key, name: mon.name, types: mon.types, shape: mon.shape, moveName: mon.moveName,
    atk: Math.round(mon.atk * multiplier),
    def: Math.round(mon.def * multiplier),
    spd: Math.round(mon.spd * multiplier),
    maxHp: hp, curHp: hp
  };
}

function stageDifficultyWeights(stageIndex, totalStages){
  const t = stageIndex / Math.max(1, totalStages - 1); // 0..1
  const easy = Math.max(0.08, 0.65 - t * 0.6);
  const hard = Math.min(0.62, 0.06 + t * 0.55);
  const medium = Math.max(0.05, 1 - easy - hard);
  return { easy, medium, hard };
}

class QuestionBank {
  constructor(allQuestions){
    this.byDiff = { easy: [], medium: [], hard: [] };
    for (const q of allQuestions) (this.byDiff[q.difficulty] || this.byDiff.medium).push(q);
    this.used = new Set();
  }
  pick(weights){
    let r = Math.random();
    let diff = "easy";
    if (r < weights.hard) diff = "hard";
    else if (r < weights.hard + weights.medium) diff = "medium";
    else diff = "easy";

    const pools = [diff, "medium", "easy", "hard"]; // fallback order if a pool runs dry
    for (const d of pools){
      const pool = this.byDiff[d].filter(q => !this.used.has(q.id));
      if (pool.length){
        const q = pool[Math.floor(Math.random() * pool.length)];
        this.used.add(q.id);
        if (this.used.size >= 480) this.used.clear(); // recycle after heavy play
        return q;
      }
    }
    // everything used — reset and retry
    this.used.clear();
    return this.pick(weights);
  }
}

class Battle {
  constructor(playerMonBase, opponentMonBase, opts){
    opts = opts || {};
    this.player = scaledMon(playerMonBase, 1);
    this.opponent = scaledMon(opponentMonBase, opts.opponentMultiplier || 1);
    this.streak = 0;
    this.bestStreak = 0;
    this.turn = 0;
    this.correctCount = 0;
    this.askedCount = 0;
    this.over = false;
    this.winner = null;
  }

  // Resolve one turn given whether the player answered correctly.
  resolveTurn(isCorrect, difficulty, timedOut){
    this.turn++;
    this.askedCount++;
    const result = { isCorrect, timedOut: !!timedOut, events: [] };

    if (isCorrect){
      this.correctCount++;
      this.streak++;
      this.bestStreak = Math.max(this.bestStreak, this.streak);
      const mult = bestTypeMultiplier(this.player.types, this.opponent.types);
      const streakBonus = Math.min(this.streak * 0.05, 0.5);
      const dmg = this._damage(this.player, this.opponent, mult, DIFF_BONUS[difficulty] || 0, streakBonus);
      this.opponent.curHp = Math.max(0, this.opponent.curHp - dmg.amount);
      result.attacker = "player";
      result.damage = dmg.amount;
      result.crit = dmg.crit;
      result.multiplier = mult;
      result.streak = this.streak;
      result.moveName = this.player.moveName;
      if (this.opponent.curHp <= 0){ this.over = true; this.winner = "player"; }
    } else {
      this.streak = 0;
      const mult = bestTypeMultiplier(this.opponent.types, this.player.types);
      const dmg = this._damage(this.opponent, this.player, mult, 0, 0, 0.85);
      this.player.curHp = Math.max(0, this.player.curHp - dmg.amount);
      result.attacker = "opponent";
      result.damage = dmg.amount;
      result.crit = dmg.crit;
      result.multiplier = mult;
      result.streak = 0;
      result.moveName = this.opponent.moveName;
      if (this.player.curHp <= 0){ this.over = true; this.winner = "opponent"; }
    }
    return result;
  }

  // Damage is expressed as a fraction of the DEFENDER's own max HP (scaled by an
  // attack/defense ratio), so pacing stays consistent no matter which two mons
  // are fighting — roughly 5-9 clean hits to KO at a neutral matchup. The raw
  // type multiplier is compressed (see compressMultiplier) so no matchup is a
  // literal unwinnable wall, while the raw value still drives the flavor text.
  _damage(atkMon, defMon, rawMultiplier, difficultyBonus, streakBonus, flatScale){
    flatScale = flatScale || 1;
    const appliedMultiplier = compressMultiplier(rawMultiplier);

    const ratio = Math.sqrt(atkMon.atk / Math.max(1, defMon.def));
    const ratioClamped = Math.min(1.35, Math.max(0.75, ratio));
    const crit = Math.random() < 0.07;

    let frac = 0.15 * ratioClamped;
    frac *= (0.9 + Math.random() * 0.2);
    frac *= appliedMultiplier;
    frac *= (1 + difficultyBonus + streakBonus);
    frac *= flatScale;
    if (crit) frac *= 1.5;

    const amount = Math.max(1, Math.round(defMon.maxHp * frac));
    return { amount, crit };
  }
}

// Picks the more effective of the attacker's own type(s) against the defender
// (a mon "chooses" its best move) and returns the raw effectiveness multiplier.
function bestTypeMultiplier(atkTypes, defTypes){
  let best = -1;
  for (const t of atkTypes) best = Math.max(best, typeMultiplier(t, defTypes));
  return best;
}

// Softens the real type chart's extremes (0x / 4x) into a bounded range so no
// single matchup is ever a literal unwinnable wall, while keeping the raw
// multiplier around for the "Super effective!" flavor text.
function compressMultiplier(rawMult){
  if (rawMult === 0) return 0.35;
  return Math.pow(rawMult, 0.55);
}

function effectivenessLabel(mult){
  if (mult === 0) return "It barely has any effect...";
  if (mult >= 2) return "It's super effective!";
  if (mult <= 0.5) return "It's not very effective...";
  return null;
}
