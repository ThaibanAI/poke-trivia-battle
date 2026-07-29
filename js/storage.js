// Simple localStorage-backed save data
const SAVE_KEY = "pt_save_v1";

function defaultSave(){
  return {
    starter: null,
    campaignStage: 0,        // next stage index to play (0..CAMPAIGN_KEYS.length)
    campaignComplete: false,
    bestStreak: 0,
    totalCorrect: 0,
    totalAsked: 0,
    endlessBest: 0,
    lastPlayed: null
  };
}

function loadSave(){
  try{
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return defaultSave();
    const parsed = JSON.parse(raw);
    return Object.assign(defaultSave(), parsed);
  }catch(e){
    return defaultSave();
  }
}

function saveSave(data){
  try{
    localStorage.setItem(SAVE_KEY, JSON.stringify(data));
  }catch(e){ /* storage unavailable — game still works, just won't persist */ }
}

function resetSave(){
  try{ localStorage.removeItem(SAVE_KEY); }catch(e){}
}
