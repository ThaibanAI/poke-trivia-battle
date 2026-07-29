// ---------------------------------------------------------------------------
// Pokemon roster + original stylized monster-art generator.
// Sprites are drawn procedurally as SVG shapes (not copies of any official
// artwork) and colored by type, so every mon has a distinct silhouette.
// ---------------------------------------------------------------------------

const TYPE_COLORS = {
  Normal:"#A8A878", Fire:"#F08030", Water:"#6890F0", Electric:"#F8D030",
  Grass:"#78C850", Ice:"#98D8D8", Fighting:"#C03028", Poison:"#A040A0",
  Ground:"#E0C068", Flying:"#A890F0", Psychic:"#F85888", Bug:"#A8B820",
  Rock:"#B8A038", Ghost:"#705898", Dragon:"#7038F8", Dark:"#705848",
  Steel:"#B8B8D0", Fairy:"#EE99AC"
};

const TYPE_CHART = {
  Normal:   { weak:["Fighting"], resist:[], immune:["Ghost"] },
  Fire:     { weak:["Water","Ground","Rock"], resist:["Fire","Grass","Ice","Bug","Steel","Fairy"], immune:[] },
  Water:    { weak:["Electric","Grass"], resist:["Fire","Water","Ice","Steel"], immune:[] },
  Electric: { weak:["Ground"], resist:["Electric","Flying","Steel"], immune:[] },
  Grass:    { weak:["Fire","Ice","Poison","Flying","Bug"], resist:["Water","Electric","Grass","Ground"], immune:[] },
  Ice:      { weak:["Fire","Fighting","Rock","Steel"], resist:["Ice"], immune:[] },
  Fighting: { weak:["Flying","Psychic","Fairy"], resist:["Bug","Rock","Dark"], immune:[] },
  Poison:   { weak:["Ground","Psychic"], resist:["Grass","Fighting","Poison","Bug","Fairy"], immune:[] },
  Ground:   { weak:["Water","Grass","Ice"], resist:["Poison","Rock"], immune:["Electric"] },
  Flying:   { weak:["Electric","Ice","Rock"], resist:["Grass","Fighting","Bug"], immune:["Ground"] },
  Psychic:  { weak:["Bug","Ghost","Dark"], resist:["Fighting","Psychic"], immune:[] },
  Bug:      { weak:["Fire","Flying","Rock"], resist:["Grass","Fighting","Ground"], immune:[] },
  Rock:     { weak:["Water","Grass","Fighting","Ground","Steel"], resist:["Normal","Fire","Poison","Flying"], immune:[] },
  Ghost:    { weak:["Ghost","Dark"], resist:["Poison","Bug"], immune:["Normal","Fighting"] },
  Dragon:   { weak:["Ice","Dragon","Fairy"], resist:["Fire","Water","Electric","Grass"], immune:[] },
  Dark:     { weak:["Fighting","Bug","Fairy"], resist:["Ghost","Dark"], immune:["Psychic"] },
  Steel:    { weak:["Fire","Fighting","Ground"], resist:["Normal","Grass","Ice","Flying","Psychic","Bug","Rock","Dragon","Steel","Fairy"], immune:["Poison"] },
  Fairy:    { weak:["Poison","Steel"], resist:["Fighting","Bug","Dark"], immune:["Dragon"] }
};

// effectiveness multiplier of an attack of `atkType` against a defender with `defTypes` (array)
function typeMultiplier(atkType, defTypes){
  let mult = 1;
  for (const dt of defTypes){
    const chart = TYPE_CHART[dt];
    if (!chart) continue;
    if (chart.immune.includes(atkType)) mult *= 0;
    else if (chart.weak.includes(atkType)) mult *= 2;
    else if (chart.resist.includes(atkType)) mult *= 0.5;
  }
  return mult;
}

// shape: round | spiky | winged | quad | serpent | humanoid | tall | armored
const ROSTER = [
  { key:"charizard", name:"Charizard", types:["Fire","Flying"], hp:78, atk:84, def:78, spd:100, shape:"winged", moveName:"Flare Blast" },
  { key:"blastoise", name:"Blastoise", types:["Water"], hp:79, atk:83, def:100, spd:78, shape:"armored", moveName:"Hydro Cannon" },
  { key:"venusaur", name:"Venusaur", types:["Grass","Poison"], hp:80, atk:82, def:83, spd:80, shape:"quad", moveName:"Petal Storm" },
  { key:"pikachu", name:"Pikachu", types:["Electric"], hp:70, atk:65, def:50, spd:112, shape:"round", moveName:"Thunder Shock" },
  { key:"snorlax", name:"Snorlax", types:["Normal"], hp:160, atk:105, def:70, spd:30, shape:"round", moveName:"Body Slam" },
  { key:"machamp", name:"Machamp", types:["Fighting"], hp:90, atk:118, def:80, spd:55, shape:"humanoid", moveName:"Focus Punch" },
  { key:"gengar", name:"Gengar", types:["Ghost","Poison"], hp:60, atk:65, def:60, spd:110, shape:"round", moveName:"Shadow Claw" },
  { key:"alakazam", name:"Alakazam", types:["Psychic"], hp:55, atk:50, def:45, spd:120, shape:"humanoid", moveName:"Psybeam" },
  { key:"golem", name:"Golem", types:["Rock","Ground"], hp:80, atk:108, def:112, spd:45, shape:"armored", moveName:"Rock Slide" },
  { key:"lapras", name:"Lapras", types:["Water","Ice"], hp:130, atk:85, def:85, spd:60, shape:"quad", moveName:"Ice Beam" },
  { key:"scizor", name:"Scizor", types:["Bug","Steel"], hp:70, atk:120, def:105, spd:65, shape:"winged", moveName:"Steel Wing" },
  { key:"dragonite", name:"Dragonite", types:["Dragon","Flying"], hp:91, atk:124, def:98, spd:80, shape:"winged", moveName:"Dragon Rush" },
  { key:"umbreon", name:"Umbreon", types:["Dark"], hp:95, atk:68, def:105, spd:65, shape:"quad", moveName:"Dark Pulse" },
  { key:"togekiss", name:"Togekiss", types:["Fairy","Flying"], hp:85, atk:58, def:95, spd:80, shape:"round", moveName:"Dazzling Wind" },
  { key:"steelix", name:"Steelix", types:["Steel","Ground"], hp:75, atk:92, def:145, spd:35, shape:"serpent", moveName:"Iron Tail" },
  { key:"crobat", name:"Crobat", types:["Poison","Flying"], hp:85, atk:92, def:80, spd:130, shape:"winged", moveName:"Cross Poison" },
  { key:"tyranitar", name:"Tyranitar", types:["Rock","Dark"], hp:100, atk:126, def:112, spd:61, shape:"armored", moveName:"Crunch" },
  { key:"gardevoir", name:"Gardevoir", types:["Psychic","Fairy"], hp:68, atk:70, def:68, spd:100, shape:"tall", moveName:"Moonblast" },
  { key:"mewtwo", name:"Mewtwo", types:["Psychic"], hp:106, atk:112, def:92, spd:132, shape:"tall", moveName:"Psystrike" },
];

const STARTER_KEYS = ["charizard","blastoise","venusaur","pikachu","gengar","gardevoir"];

// Campaign order: 8 trainer battles + elite + champion
const CAMPAIGN_KEYS = ["crobat","golem","umbreon","togekiss","scizor","machamp","steelix","tyranitar","dragonite","mewtwo"];

function getMon(key){ return ROSTER.find(m=>m.key===key); }

function svgFor(mon, opts){
  opts = opts || {};
  const facing = opts.facing || "right"; // right = player mon (faces opponent), left = opponent mon
  const c1 = TYPE_COLORS[mon.types[0]];
  const c2 = TYPE_COLORS[mon.types[1] || mon.types[0]];
  const flip = facing === "left" ? "scale(-1,1) translate(-160,0)" : "";
  const id = "g" + mon.key;

  let body = "";
  switch(mon.shape){
    case "winged":
      body = `
        <path d="M20 95 C10 60 55 25 90 30 C82 15 60 5 45 8 C60 -5 95 -2 100 20 C130 5 155 25 150 55 C165 60 168 85 150 95 Z" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <ellipse cx="88" cy="70" rx="38" ry="34" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="102" cy="60" r="6" fill="#1b1f2a"/>
      `;
      break;
    case "quad":
      body = `
        <ellipse cx="85" cy="78" rx="52" ry="34" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="130" cy="55" r="28" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <rect x="45" y="95" width="14" height="26" rx="6" fill="${c2}"/>
        <rect x="105" y="98" width="14" height="26" rx="6" fill="${c2}"/>
        <circle cx="140" cy="48" r="5" fill="#1b1f2a"/>
      `;
      break;
    case "humanoid":
      body = `
        <ellipse cx="90" cy="80" rx="34" ry="42" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="95" cy="35" r="26" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <rect x="50" y="55" width="18" height="45" rx="9" fill="${c1}"/>
        <rect x="122" y="55" width="18" height="45" rx="9" fill="${c1}"/>
        <circle cx="87" cy="33" r="4" fill="#1b1f2a"/>
        <circle cx="105" cy="33" r="4" fill="#1b1f2a"/>
      `;
      break;
    case "armored":
      body = `
        <rect x="45" y="45" width="95" height="65" rx="18" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="95" cy="40" r="24" fill="${c2}" stroke="#00000030" stroke-width="3"/>
        <circle cx="70" cy="70" r="10" fill="#00000020"/>
        <circle cx="120" cy="70" r="10" fill="#00000020"/>
        <circle cx="87" cy="38" r="4" fill="#1b1f2a"/>
        <circle cx="103" cy="38" r="4" fill="#1b1f2a"/>
      `;
      break;
    case "serpent":
      body = `
        <path d="M20 100 C20 60 45 90 70 60 C95 30 60 15 85 5 C115 -5 150 25 130 55 C160 55 165 90 135 100 Z" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="128" cy="30" r="16" fill="${c2}"/>
        <circle cx="133" cy="25" r="3.5" fill="#1b1f2a"/>
      `;
      break;
    case "tall":
      body = `
        <ellipse cx="90" cy="95" rx="30" ry="22" fill="${c2}" opacity="0.9"/>
        <path d="M60 100 C55 55 65 20 90 12 C115 20 125 55 120 100 Z" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="90" cy="30" r="20" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="83" cy="28" r="4" fill="#1b1f2a"/>
        <circle cx="97" cy="28" r="4" fill="#1b1f2a"/>
      `;
      break;
    default: // round
      body = `
        <circle cx="90" cy="65" r="48" fill="url(#${id})" stroke="#00000030" stroke-width="3"/>
        <circle cx="55" cy="35" r="14" fill="${c2}"/>
        <circle cx="125" cy="35" r="14" fill="${c2}"/>
        <circle cx="76" cy="60" r="5" fill="#1b1f2a"/>
        <circle cx="104" cy="60" r="5" fill="#1b1f2a"/>
      `;
  }

  return `
  <svg viewBox="0 0 180 120" xmlns="http://www.w3.org/2000/svg" class="mon-svg">
    <defs>
      <linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="${c1}"/>
        <stop offset="100%" stop-color="${c2}"/>
      </linearGradient>
    </defs>
    <g transform="${flip}">${body}</g>
  </svg>`;
}
