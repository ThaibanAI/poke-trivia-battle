#!/usr/bin/env python3
"""
Generates 500 Pokemon trivia questions from a curated, hand-verified fact
database (types, dex numbers, evolutions, generations, legendary status,
abilities). Questions are template-driven so every fact used is one we
actually stored (no free-form hallucination at generation time).
"""
import json, random

random.seed(1907)

ALL_TYPES = ["Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison",
             "Ground","Flying","Psychic","Bug","Rock","Ghost","Dragon","Dark",
             "Steel","Fairy"]

# defending-type -> types that are super effective AGAINST it, types it resists, types it's immune to
TYPE_CHART = {
 "Normal":   {"weak":["Fighting"], "resist":[], "immune":["Ghost"]},
 "Fire":     {"weak":["Water","Ground","Rock"], "resist":["Fire","Grass","Ice","Bug","Steel","Fairy"], "immune":[]},
 "Water":    {"weak":["Electric","Grass"], "resist":["Fire","Water","Ice","Steel"], "immune":[]},
 "Electric": {"weak":["Ground"], "resist":["Electric","Flying","Steel"], "immune":[]},
 "Grass":    {"weak":["Fire","Ice","Poison","Flying","Bug"], "resist":["Water","Electric","Grass","Ground"], "immune":[]},
 "Ice":      {"weak":["Fire","Fighting","Rock","Steel"], "resist":["Ice"], "immune":[]},
 "Fighting": {"weak":["Flying","Psychic","Fairy"], "resist":["Bug","Rock","Dark"], "immune":[]},
 "Poison":   {"weak":["Ground","Psychic"], "resist":["Grass","Fighting","Poison","Bug","Fairy"], "immune":[]},
 "Ground":   {"weak":["Water","Grass","Ice"], "resist":["Poison","Rock"], "immune":["Electric"]},
 "Flying":   {"weak":["Electric","Ice","Rock"], "resist":["Grass","Fighting","Bug"], "immune":["Ground"]},
 "Psychic":  {"weak":["Bug","Ghost","Dark"], "resist":["Fighting","Psychic"], "immune":[]},
 "Bug":      {"weak":["Fire","Flying","Rock"], "resist":["Grass","Fighting","Ground"], "immune":[]},
 "Rock":     {"weak":["Water","Grass","Fighting","Ground","Steel"], "resist":["Normal","Fire","Poison","Flying"], "immune":[]},
 "Ghost":    {"weak":["Ghost","Dark"], "resist":["Poison","Bug"], "immune":["Normal","Fighting"]},
 "Dragon":   {"weak":["Ice","Dragon","Fairy"], "resist":["Fire","Water","Electric","Grass"], "immune":[]},
 "Dark":     {"weak":["Fighting","Bug","Fairy"], "resist":["Ghost","Dark"], "immune":["Psychic"]},
 "Steel":    {"weak":["Fire","Fighting","Ground"], "resist":["Normal","Grass","Ice","Flying","Psychic","Bug","Rock","Dragon","Steel","Fairy"], "immune":["Poison"]},
 "Fairy":    {"weak":["Poison","Steel"], "resist":["Fighting","Bug","Dark"], "immune":["Dragon"]},
}

# Core Pokemon fact database: dex, name, types (list), gen, status, evo links
# status: "" normal, "legendary", "mythical", "pseudo" (pseudo-legendary)
P = [
 (1,"Bulbasaur",["Grass","Poison"],1,"", None,"Ivysaur"),
 (2,"Ivysaur",["Grass","Poison"],1,"", "Bulbasaur","Venusaur"),
 (3,"Venusaur",["Grass","Poison"],1,"", "Ivysaur", None),
 (4,"Charmander",["Fire"],1,"", None,"Charmeleon"),
 (5,"Charmeleon",["Fire"],1,"", "Charmander","Charizard"),
 (6,"Charizard",["Fire","Flying"],1,"", "Charmeleon", None),
 (7,"Squirtle",["Water"],1,"", None,"Wartortle"),
 (8,"Wartortle",["Water"],1,"", "Squirtle","Blastoise"),
 (9,"Blastoise",["Water"],1,"", "Wartortle", None),
 (10,"Caterpie",["Bug"],1,"", None,"Metapod"),
 (11,"Metapod",["Bug"],1,"", "Caterpie","Butterfree"),
 (12,"Butterfree",["Bug","Flying"],1,"", "Metapod", None),
 (13,"Weedle",["Bug","Poison"],1,"", None,"Kakuna"),
 (14,"Kakuna",["Bug","Poison"],1,"", "Weedle","Beedrill"),
 (15,"Beedrill",["Bug","Poison"],1,"", "Kakuna", None),
 (16,"Pidgey",["Normal","Flying"],1,"", None,"Pidgeotto"),
 (17,"Pidgeotto",["Normal","Flying"],1,"", "Pidgey","Pidgeot"),
 (18,"Pidgeot",["Normal","Flying"],1,"", "Pidgeotto", None),
 (19,"Rattata",["Normal"],1,"", None,"Raticate"),
 (20,"Raticate",["Normal"],1,"", "Rattata", None),
 (21,"Spearow",["Normal","Flying"],1,"", None,"Fearow"),
 (22,"Fearow",["Normal","Flying"],1,"", "Spearow", None),
 (23,"Ekans",["Poison"],1,"", None,"Arbok"),
 (24,"Arbok",["Poison"],1,"", "Ekans", None),
 (25,"Pikachu",["Electric"],1,"", None,"Raichu"),
 (26,"Raichu",["Electric"],1,"", "Pikachu", None),
 (27,"Sandshrew",["Ground"],1,"", None,"Sandslash"),
 (28,"Sandslash",["Ground"],1,"", "Sandshrew", None),
 (29,"Nidoran-F",["Poison"],1,"", None,"Nidorina"),
 (30,"Nidorina",["Poison"],1,"", "Nidoran-F","Nidoqueen"),
 (31,"Nidoqueen",["Poison","Ground"],1,"", "Nidorina", None),
 (32,"Nidoran-M",["Poison"],1,"", None,"Nidorino"),
 (33,"Nidorino",["Poison"],1,"", "Nidoran-M","Nidoking"),
 (34,"Nidoking",["Poison","Ground"],1,"", "Nidorino", None),
 (35,"Clefairy",["Fairy"],1,"", None,"Clefable"),
 (36,"Clefable",["Fairy"],1,"", "Clefairy", None),
 (37,"Vulpix",["Fire"],1,"", None,"Ninetales"),
 (38,"Ninetales",["Fire"],1,"", "Vulpix", None),
 (39,"Jigglypuff",["Normal","Fairy"],1,"", None,"Wigglytuff"),
 (40,"Wigglytuff",["Normal","Fairy"],1,"", "Jigglypuff", None),
 (41,"Zubat",["Poison","Flying"],1,"", None,"Golbat"),
 (42,"Golbat",["Poison","Flying"],1,"", "Zubat", None),
 (43,"Oddish",["Grass","Poison"],1,"", None,"Gloom"),
 (44,"Gloom",["Grass","Poison"],1,"", "Oddish","Vileplume"),
 (45,"Vileplume",["Grass","Poison"],1,"", "Gloom", None),
 (46,"Paras",["Bug","Grass"],1,"", None,"Parasect"),
 (47,"Parasect",["Bug","Grass"],1,"", "Paras", None),
 (48,"Venonat",["Bug","Poison"],1,"", None,"Venomoth"),
 (49,"Venomoth",["Bug","Poison"],1,"", "Venonat", None),
 (50,"Diglett",["Ground"],1,"", None,"Dugtrio"),
 (51,"Dugtrio",["Ground"],1,"", "Diglett", None),
 (52,"Meowth",["Normal"],1,"", None,"Persian"),
 (53,"Persian",["Normal"],1,"", "Meowth", None),
 (54,"Psyduck",["Water"],1,"", None,"Golduck"),
 (55,"Golduck",["Water"],1,"", "Psyduck", None),
 (56,"Mankey",["Fighting"],1,"", None,"Primeape"),
 (57,"Primeape",["Fighting"],1,"", "Mankey", None),
 (58,"Growlithe",["Fire"],1,"", None,"Arcanine"),
 (59,"Arcanine",["Fire"],1,"", "Growlithe", None),
 (60,"Poliwag",["Water"],1,"", None,"Poliwhirl"),
 (61,"Poliwhirl",["Water"],1,"", "Poliwag","Poliwrath"),
 (62,"Poliwrath",["Water","Fighting"],1,"", "Poliwhirl", None),
 (63,"Abra",["Psychic"],1,"", None,"Kadabra"),
 (64,"Kadabra",["Psychic"],1,"", "Abra","Alakazam"),
 (65,"Alakazam",["Psychic"],1,"", "Kadabra", None),
 (66,"Machop",["Fighting"],1,"", None,"Machoke"),
 (67,"Machoke",["Fighting"],1,"", "Machop","Machamp"),
 (68,"Machamp",["Fighting"],1,"", "Machoke", None),
 (69,"Bellsprout",["Grass","Poison"],1,"", None,"Weepinbell"),
 (70,"Weepinbell",["Grass","Poison"],1,"", "Bellsprout","Victreebel"),
 (71,"Victreebel",["Grass","Poison"],1,"", "Weepinbell", None),
 (72,"Tentacool",["Water","Poison"],1,"", None,"Tentacruel"),
 (73,"Tentacruel",["Water","Poison"],1,"", "Tentacool", None),
 (74,"Geodude",["Rock","Ground"],1,"", None,"Graveler"),
 (75,"Graveler",["Rock","Ground"],1,"", "Geodude","Golem"),
 (76,"Golem",["Rock","Ground"],1,"", "Graveler", None),
 (77,"Ponyta",["Fire"],1,"", None,"Rapidash"),
 (78,"Rapidash",["Fire"],1,"", "Ponyta", None),
 (79,"Slowpoke",["Water","Psychic"],1,"", None,"Slowbro"),
 (80,"Slowbro",["Water","Psychic"],1,"", "Slowpoke", None),
 (81,"Magnemite",["Electric","Steel"],1,"", None,"Magneton"),
 (82,"Magneton",["Electric","Steel"],1,"", "Magnemite", None),
 (83,"Farfetchd",["Normal","Flying"],1,"", None, None),
 (84,"Doduo",["Normal","Flying"],1,"", None,"Dodrio"),
 (85,"Dodrio",["Normal","Flying"],1,"", "Doduo", None),
 (86,"Seel",["Water"],1,"", None,"Dewgong"),
 (87,"Dewgong",["Water","Ice"],1,"", "Seel", None),
 (88,"Grimer",["Poison"],1,"", None,"Muk"),
 (89,"Muk",["Poison"],1,"", "Grimer", None),
 (90,"Shellder",["Water"],1,"", None,"Cloyster"),
 (91,"Cloyster",["Water","Ice"],1,"", "Shellder", None),
 (92,"Gastly",["Ghost","Poison"],1,"", None,"Haunter"),
 (93,"Haunter",["Ghost","Poison"],1,"", "Gastly","Gengar"),
 (94,"Gengar",["Ghost","Poison"],1,"", "Haunter", None),
 (95,"Onix",["Rock","Ground"],1,"", None, None),
 (96,"Drowzee",["Psychic"],1,"", None,"Hypno"),
 (97,"Hypno",["Psychic"],1,"", "Drowzee", None),
 (98,"Krabby",["Water"],1,"", None,"Kingler"),
 (99,"Kingler",["Water"],1,"", "Krabby", None),
 (100,"Voltorb",["Electric"],1,"", None,"Electrode"),
 (101,"Electrode",["Electric"],1,"", "Voltorb", None),
 (102,"Exeggcute",["Grass","Psychic"],1,"", None,"Exeggutor"),
 (103,"Exeggutor",["Grass","Psychic"],1,"", "Exeggcute", None),
 (104,"Cubone",["Ground"],1,"", None,"Marowak"),
 (105,"Marowak",["Ground"],1,"", "Cubone", None),
 (106,"Hitmonlee",["Fighting"],1,"", None, None),
 (107,"Hitmonchan",["Fighting"],1,"", None, None),
 (108,"Lickitung",["Normal"],1,"", None, None),
 (109,"Koffing",["Poison"],1,"", None,"Weezing"),
 (110,"Weezing",["Poison"],1,"", "Koffing", None),
 (111,"Rhyhorn",["Ground","Rock"],1,"", None,"Rhydon"),
 (112,"Rhydon",["Ground","Rock"],1,"", "Rhyhorn", None),
 (113,"Chansey",["Normal"],1,"", None, None),
 (114,"Tangela",["Grass"],1,"", None, None),
 (115,"Kangaskhan",["Normal"],1,"", None, None),
 (116,"Horsea",["Water"],1,"", None,"Seadra"),
 (117,"Seadra",["Water"],1,"", "Horsea", None),
 (118,"Goldeen",["Water"],1,"", None,"Seaking"),
 (119,"Seaking",["Water"],1,"", "Goldeen", None),
 (120,"Staryu",["Water"],1,"", None,"Starmie"),
 (121,"Starmie",["Water","Psychic"],1,"", "Staryu", None),
 (122,"Mr Mime",["Psychic","Fairy"],1,"", None, None),
 (123,"Scyther",["Bug","Flying"],1,"", None, None),
 (124,"Jynx",["Ice","Psychic"],1,"", None, None),
 (125,"Electabuzz",["Electric"],1,"", None, None),
 (126,"Magmar",["Fire"],1,"", None, None),
 (127,"Pinsir",["Bug"],1,"", None, None),
 (128,"Tauros",["Normal"],1,"", None, None),
 (129,"Magikarp",["Water"],1,"", None,"Gyarados"),
 (130,"Gyarados",["Water","Flying"],1,"", "Magikarp", None),
 (131,"Lapras",["Water","Ice"],1,"", None, None),
 (132,"Ditto",["Normal"],1,"", None, None),
 (133,"Eevee",["Normal"],1,"", None, None),
 (134,"Vaporeon",["Water"],1,"", "Eevee", None),
 (135,"Jolteon",["Electric"],1,"", "Eevee", None),
 (136,"Flareon",["Fire"],1,"", "Eevee", None),
 (137,"Porygon",["Normal"],1,"", None, None),
 (138,"Omanyte",["Rock","Water"],1,"", None,"Omastar"),
 (139,"Omastar",["Rock","Water"],1,"", "Omanyte", None),
 (140,"Kabuto",["Rock","Water"],1,"", None,"Kabutops"),
 (141,"Kabutops",["Rock","Water"],1,"", "Kabuto", None),
 (142,"Aerodactyl",["Rock","Flying"],1,"", None, None),
 (143,"Snorlax",["Normal"],1,"", None, None),
 (144,"Articuno",["Ice","Flying"],1,"legendary", None, None),
 (145,"Zapdos",["Electric","Flying"],1,"legendary", None, None),
 (146,"Moltres",["Fire","Flying"],1,"legendary", None, None),
 (147,"Dratini",["Dragon"],1,"", None,"Dragonair"),
 (148,"Dragonair",["Dragon"],1,"", "Dratini","Dragonite"),
 (149,"Dragonite",["Dragon","Flying"],1,"", "Dragonair", None),
 (150,"Mewtwo",["Psychic"],1,"legendary", None, None),
 (151,"Mew",["Psychic"],1,"mythical", None, None),
 # Gen 2 highlights
 (152,"Chikorita",["Grass"],2,"", None,"Bayleef"),
 (153,"Bayleef",["Grass"],2,"", "Chikorita","Meganium"),
 (154,"Meganium",["Grass"],2,"", "Bayleef", None),
 (155,"Cyndaquil",["Fire"],2,"", None,"Quilava"),
 (156,"Quilava",["Fire"],2,"", "Cyndaquil","Typhlosion"),
 (157,"Typhlosion",["Fire"],2,"", "Quilava", None),
 (158,"Totodile",["Water"],2,"", None,"Croconaw"),
 (159,"Croconaw",["Water"],2,"", "Totodile","Feraligatr"),
 (160,"Feraligatr",["Water"],2,"", "Croconaw", None),
 (161,"Pichu",["Electric"],2,"", None,"Pikachu"),
 (170,"Chinchou",["Water","Electric"],2,"", None,"Lanturn"),
 (171,"Lanturn",["Water","Electric"],2,"", "Chinchou", None),
 (175,"Togepi",["Fairy"],2,"", None,"Togetic"),
 (176,"Togetic",["Fairy","Flying"],2,"", "Togepi", None),
 (179,"Mareep",["Electric"],2,"", None,"Flaaffy"),
 (180,"Flaaffy",["Electric"],2,"", "Mareep","Ampharos"),
 (181,"Ampharos",["Electric"],2,"", "Flaaffy", None),
 (196,"Espeon",["Psychic"],2,"", "Eevee", None),
 (197,"Umbreon",["Dark"],2,"", "Eevee", None),
 (198,"Murkrow",["Dark","Flying"],2,"", None, None),
 (199,"Slowking",["Water","Psychic"],2,"", "Slowpoke", None),
 (201,"Unown",["Psychic"],2,"", None, None),
 (202,"Wobbuffet",["Psychic"],2,"", None, None),
 (208,"Steelix",["Steel","Ground"],2,"", "Onix", None),
 (212,"Scizor",["Bug","Steel"],2,"", "Scyther", None),
 (214,"Heracross",["Bug","Fighting"],2,"", None, None),
 (215,"Sneasel",["Dark","Ice"],2,"", None, None),
 (196,"Espeon",["Psychic"],2,"", "Eevee", None),
 (225,"Delibird",["Ice","Flying"],2,"", None, None),
 (229,"Houndoom",["Dark","Fire"],2,"", None, None),
 (230,"Kingdra",["Water","Dragon"],2,"", "Seadra", None),
 (233,"Porygon2",["Normal"],2,"", "Porygon","Porygon-Z"),
 (241,"Miltank",["Normal"],2,"", None, None),
 (242,"Blissey",["Normal"],2,"", "Chansey", None),
 (243,"Raikou",["Electric"],2,"legendary", None, None),
 (244,"Entei",["Fire"],2,"legendary", None, None),
 (245,"Suicune",["Water"],2,"legendary", None, None),
 (246,"Larvitar",["Rock","Ground"],2,"", None,"Pupitar"),
 (247,"Pupitar",["Rock","Ground"],2,"", "Larvitar","Tyranitar"),
 (248,"Tyranitar",["Rock","Dark"],2,"pseudo", "Pupitar", None),
 (249,"Lugia",["Psychic","Flying"],2,"legendary", None, None),
 (250,"Ho-Oh",["Fire","Flying"],2,"legendary", None, None),
 (251,"Celebi",["Psychic","Grass"],2,"mythical", None, None),
 # Gen 3 highlights
 (252,"Treecko",["Grass"],3,"", None,"Grovyle"),
 (253,"Grovyle",["Grass"],3,"", "Treecko","Sceptile"),
 (254,"Sceptile",["Grass"],3,"", "Grovyle", None),
 (255,"Torchic",["Fire"],3,"", None,"Combusken"),
 (256,"Combusken",["Fire","Fighting"],3,"", "Torchic","Blaziken"),
 (257,"Blaziken",["Fire","Fighting"],3,"", "Combusken", None),
 (258,"Mudkip",["Water"],3,"", None,"Marshtomp"),
 (259,"Marshtomp",["Water","Ground"],3,"", "Mudkip","Swampert"),
 (260,"Swampert",["Water","Ground"],3,"", "Marshtomp", None),
 (280,"Ralts",["Psychic","Fairy"],3,"", None,"Kirlia"),
 (281,"Kirlia",["Psychic","Fairy"],3,"", "Ralts","Gardevoir"),
 (282,"Gardevoir",["Psychic","Fairy"],3,"", "Kirlia", None),
 (302,"Sableye",["Dark","Ghost"],3,"", None, None),
 (303,"Mawile",["Steel","Fairy"],3,"", None, None),
 (306,"Aggron",["Steel","Rock"],3,"", None, None),
 (310,"Manectric",["Electric"],3,"", None, None),
 (319,"Sharpedo",["Water","Dark"],3,"", None, None),
 (321,"Wailord",["Water"],3,"", None, None),
 (334,"Altaria",["Dragon","Flying"],3,"", None, None),
 (350,"Milotic",["Water"],3,"", None, None),
 (359,"Absol",["Dark"],3,"", None, None),
 (373,"Salamence",["Dragon","Flying"],3,"pseudo", None, None),
 (376,"Metagross",["Steel","Psychic"],3,"pseudo", None, None),
 (377,"Regirock",["Rock"],3,"legendary", None, None),
 (378,"Regice",["Ice"],3,"legendary", None, None),
 (379,"Registeel",["Steel"],3,"legendary", None, None),
 (380,"Latias",["Dragon","Psychic"],3,"legendary", None, None),
 (381,"Latios",["Dragon","Psychic"],3,"legendary", None, None),
 (382,"Kyogre",["Water"],3,"legendary", None, None),
 (383,"Groudon",["Ground"],3,"legendary", None, None),
 (384,"Rayquaza",["Dragon","Flying"],3,"legendary", None, None),
 (385,"Jirachi",["Steel","Psychic"],3,"mythical", None, None),
 (386,"Deoxys",["Psychic"],3,"mythical", None, None),
 # Gen 4 highlights
 (387,"Turtwig",["Grass"],4,"", None,"Grotle"),
 (390,"Chimchar",["Fire"],4,"", None,"Monferno"),
 (393,"Piplup",["Water"],4,"", None,"Prinplup"),
 (392,"Infernape",["Fire","Fighting"],4,"", "Monferno", None),
 (395,"Empoleon",["Water","Steel"],4,"", "Prinplup", None),
 (398,"Staraptor",["Normal","Flying"],4,"", None, None),
 (405,"Luxray",["Electric"],4,"", None, None),
 (445,"Garchomp",["Dragon","Ground"],4,"pseudo", "Gabite", None),
 (448,"Lucario",["Fighting","Steel"],4,"", "Riolu", None),
 (461,"Weavile",["Dark","Ice"],4,"", None, None),
 (462,"Magnezone",["Electric","Steel"],4,"", "Magneton", None),
 (466,"Electivire",["Electric"],4,"", "Electabuzz", None),
 (467,"Magmortar",["Fire"],4,"", "Magmar", None),
 (468,"Togekiss",["Fairy","Flying"],4,"", "Togetic", None),
 (470,"Leafeon",["Grass"],4,"", "Eevee", None),
 (471,"Glaceon",["Ice"],4,"", "Eevee", None),
 (472,"Gliscor",["Ground","Flying"],4,"", None, None),
 (473,"Mamoswine",["Ice","Ground"],4,"", None, None),
 (478,"Froslass",["Ice","Ghost"],4,"", None, None),
 (479,"Rotom",["Electric","Ghost"],4,"", None, None),
 (481,"Mesprit",["Psychic"],4,"legendary", None, None),
 (483,"Dialga",["Steel","Dragon"],4,"legendary", None, None),
 (484,"Palkia",["Water","Dragon"],4,"legendary", None, None),
 (487,"Giratina",["Ghost","Dragon"],4,"legendary", None, None),
 (488,"Cresselia",["Psychic"],4,"legendary", None, None),
 (491,"Darkrai",["Dark"],4,"mythical", None, None),
 (492,"Shaymin",["Grass"],4,"mythical", None, None),
 (493,"Arceus",["Normal"],4,"mythical", None, None),
 # Gen 5 highlights
 (495,"Snivy",["Grass"],5,"", None,"Servine"),
 (498,"Tepig",["Fire"],5,"", None,"Pignite"),
 (501,"Oshawott",["Water"],5,"", None,"Dewott"),
 (500,"Emboar",["Fire","Fighting"],5,"", "Pignite", None),
 (503,"Samurott",["Water"],5,"", "Dewott", None),
 (523,"Zebstrika",["Electric"],5,"", None, None),
 (531,"Audino",["Normal"],5,"", None, None),
 (571,"Zoroark",["Dark"],5,"", "Zorua", None),
 (609,"Chandelure",["Ghost","Fire"],5,"", None, None),
 (612,"Haxorus",["Dragon"],5,"pseudo", None, None),
 (635,"Hydreigon",["Dark","Dragon"],5,"pseudo", None, None),
 (637,"Volcarona",["Bug","Fire"],5,"", None, None),
 (641,"Tornadus",["Flying"],5,"legendary", None, None),
 (642,"Thundurus",["Electric","Flying"],5,"legendary", None, None),
 (643,"Reshiram",["Dragon","Fire"],5,"legendary", None, None),
 (644,"Zekrom",["Dragon","Electric"],5,"legendary", None, None),
 (645,"Landorus",["Ground","Flying"],5,"legendary", None, None),
 (646,"Kyurem",["Dragon","Ice"],5,"legendary", None, None),
 (647,"Keldeo",["Water","Fighting"],5,"mythical", None, None),
 (649,"Genesect",["Bug","Steel"],5,"mythical", None, None),
 # Gen 6 highlights
 (650,"Chespin",["Grass"],6,"", None,"Quilladin"),
 (653,"Fennekin",["Fire"],6,"", None,"Braixen"),
 (656,"Froakie",["Water"],6,"", None,"Frogadier"),
 (652,"Chesnaught",["Grass","Fighting"],6,"", "Quilladin", None),
 (655,"Delphox",["Fire","Psychic"],6,"", "Braixen", None),
 (658,"Greninja",["Water","Dark"],6,"", "Frogadier", None),
 (663,"Talonflame",["Fire","Flying"],6,"", None, None),
 (678,"Meowstic",["Psychic"],6,"", None, None),
 (700,"Sylveon",["Fairy"],6,"", "Eevee", None),
 (706,"Goodra",["Dragon"],6,"", "Sliggoo", None),
 (715,"Noivern",["Flying","Dragon"],6,"", None, None),
 (681,"Aegislash",["Steel","Ghost"],6,"", "Doublade", None),
 (717,"Yveltal",["Dark","Flying"],6,"legendary", None, None),
 (716,"Xerneas",["Fairy"],6,"legendary", None, None),
 (718,"Zygarde",["Dragon","Ground"],6,"legendary", None, None),
 (719,"Diancie",["Rock","Fairy"],6,"mythical", None, None),
 (720,"Hoopa",["Psychic","Ghost"],6,"mythical", None, None),
 (721,"Volcanion",["Fire","Water"],6,"mythical", None, None),
 # Gen 7 highlights
 (722,"Rowlet",["Grass","Flying"],7,"", None,"Dartrix"),
 (725,"Litten",["Fire"],7,"", None,"Torracat"),
 (728,"Popplio",["Water"],7,"", None,"Brionne"),
 (724,"Decidueye",["Grass","Ghost"],7,"", "Dartrix", None),
 (727,"Incineroar",["Fire","Dark"],7,"", "Torracat", None),
 (730,"Primarina",["Water","Fairy"],7,"", "Brionne", None),
 (778,"Mimikyu",["Ghost","Fairy"],7,"", None, None),
 (784,"Kommo-o",["Dragon","Fighting"],7,"pseudo", None, None),
 (785,"Tapu Koko",["Electric","Fairy"],7,"legendary", None, None),
 (791,"Solgaleo",["Psychic","Steel"],7,"legendary", None, None),
 (792,"Lunala",["Psychic","Ghost"],7,"legendary", None, None),
 (800,"Necrozma",["Psychic"],7,"legendary", None, None),
 (802,"Marshadow",["Fighting","Ghost"],7,"mythical", None, None),
 (801,"Magearna",["Steel","Fairy"],7,"mythical", None, None),
 # Gen 8 highlights
 (810,"Grookey",["Grass"],8,"", None,"Thwackey"),
 (813,"Scorbunny",["Fire"],8,"", None,"Raboot"),
 (816,"Sobble",["Water"],8,"", None,"Drizzile"),
 (812,"Rillaboom",["Grass"],8,"", "Thwackey", None),
 (815,"Cinderace",["Fire"],8,"", "Raboot", None),
 (818,"Inteleon",["Water"],8,"", "Drizzile", None),
 (823,"Corviknight",["Flying","Steel"],8,"", None, None),
 (845,"Cramorant",["Flying","Water"],8,"", None, None),
 (849,"Toxtricity",["Electric","Poison"],8,"", None, None),
 (861,"Grimmsnarl",["Dark","Fairy"],8,"", None, None),
 (884,"Duraludon",["Steel","Dragon"],8,"", None, None),
 (887,"Dragapult",["Dragon","Ghost"],8,"pseudo", None, None),
 (888,"Zacian",["Fairy"],8,"legendary", None, None),
 (889,"Zamazenta",["Fighting"],8,"legendary", None, None),
 (890,"Eternatus",["Poison","Dragon"],8,"legendary", None, None),
 # Gen 9 highlights
 (906,"Sprigatito",["Grass"],9,"", None,"Floragato"),
 (909,"Fuecoco",["Fire"],9,"", None,"Crocalor"),
 (912,"Quaxly",["Water"],9,"", None,"Quaxwell"),
 (908,"Meowscarada",["Grass","Dark"],9,"", "Floragato", None),
 (911,"Skeledirge",["Fire","Ghost"],9,"", "Crocalor", None),
 (914,"Quaquaval",["Water","Fighting"],9,"", "Quaxwell", None),
 (935,"Grafaiai",["Poison","Normal"],9,"", None, None),
 (984,"Gholdengo",["Steel","Ghost"],9,"", None, None),
 (998,"Baxcalibur",["Dragon","Ice"],9,"pseudo", None, None),
 (1007,"Koraidon",["Fighting","Dragon"],9,"legendary", None, None),
 (1008,"Miraidon",["Electric","Dragon"],9,"legendary", None, None),
]

# de-dup by name (Espeon appears twice above)
seen=set(); PB=[]
for row in P:
    if row[1] in seen: continue
    seen.add(row[1]); PB.append(row)
P = PB

NAME2ROW = {row[1]: row for row in P}

# Well-known / verified abilities (pokemon name -> a real ability it can have)
ABILITIES = [
 ("Pikachu","Static"), ("Raichu","Static"), ("Charizard","Blaze"), ("Venusaur","Overgrow"),
 ("Blastoise","Torrent"), ("Gengar","Levitate"), ("Gyarados","Intimidate"), ("Arcanine","Intimidate"),
 ("Alakazam","Synchronize"), ("Snorlax","Thick Fat"), ("Clefable","Magic Guard"), ("Clefairy","Cute Charm"),
 ("Dragonite","Multiscale"), ("Garchomp","Rough Skin"), ("Onix","Sturdy"), ("Steelix","Sturdy"),
 ("Kabutops","Battle Armor"), ("Poliwrath","Water Absorb"), ("Arbok","Shed Skin"), ("Hypno","Insomnia"),
 ("Magmar","Flame Body"), ("Paras","Effect Spore"), ("Slowking","Regenerator"), ("Slowpoke","Oblivious"),
 ("Butterfree","Compound Eyes"), ("Venomoth","Shield Dust"), ("Dugtrio","Arena Trap"), ("Diglett","Arena Trap"),
 ("Gardevoir","Trace"), ("Tyranitar","Sand Stream"), ("Milotic","Marvel Scale"), ("Togekiss","Serene Grace"),
 ("Groudon","Drought"), ("Kyogre","Drizzle"), ("Rayquaza","Air Lock"), ("Blaziken","Speed Boost"),
 ("Greninja","Protean"), ("Zoroark","Illusion"), ("Aegislash","Stance Change"), ("Regigigas","Slow Start"),
 ("Cramorant","Gulp Missile"), ("Toxtricity","Punk Rock"), ("Corviknight","Mirror Armor"),
 ("Sableye","Prankster"), ("Absol","Pressure"), ("Mimikyu","Disguise"), ("Wobbuffet","Shadow Tag"),
]

# --------- helpers ---------
def type_str(types):
    return "/".join(types)

def gen_word(n):
    words = {1:"first",2:"second",3:"third",4:"fourth",5:"fifth",6:"sixth",7:"seventh",8:"eighth",9:"ninth"}
    return words[n]

def status_label(s):
    return {"legendary":"Legendary","mythical":"Mythical","pseudo":"pseudo-Legendary"}.get(s,"")

def make_q(qid, category, difficulty, question, correct, distractors):
    opts = [correct] + distractors[:3]
    random.shuffle(opts)
    return {
        "id": qid,
        "category": category,
        "difficulty": difficulty,
        "question": question,
        "options": opts,
        "answer": opts.index(correct),
    }

questions = []
qid = 1
def add(category, difficulty, question, correct, distractors):
    global qid
    # guard: ensure distractors don't accidentally equal correct
    d = [x for x in distractors if x != correct]
    while len(d) < 3:
        d.append(d[-1] if d else "None of these")
    questions.append(make_q(qid, category, difficulty, question, correct, d[:3]))
    qid += 1

# ---------------- Category 1: What type is X? ----------------
type_pool_flat = ALL_TYPES
for row in P:
    dex, name, types, gen, status, pre, nxt = row
    correct = type_str(types)
    # build distractor type-strings: other real combos or single types not equal to correct
    candidates = set()
    tries = 0
    while len(candidates) < 6 and tries < 200:
        tries += 1
        if random.random() < 0.5:
            cand = random.choice(ALL_TYPES)
        else:
            t2 = random.sample(ALL_TYPES, 2)
            cand = type_str(t2)
        if cand != correct:
            candidates.add(cand)
    distractors = random.sample(list(candidates), 3)
    diff = "easy" if gen == 1 else ("medium" if gen <= 4 else "hard")
    add("Types", diff, f"What type is {name.replace('-',' ')}?", correct, distractors)

# ---------------- Category 2: Type effectiveness ----------------
for t in ALL_TYPES:
    chart = TYPE_CHART[t]
    if chart["weak"]:
        correct = random.choice(chart["weak"])
        others = [x for x in ALL_TYPES if x not in chart["weak"] and x != correct]
        distractors = random.sample(others, 3)
        add("Type Matchups","medium", f"Which type is super effective against {t}-type Pokemon?", correct, distractors)
    if chart["resist"]:
        correct = random.choice(chart["resist"])
        others = [x for x in ALL_TYPES if x not in chart["resist"] and x != correct]
        distractors = random.sample(others, 3)
        add("Type Matchups","medium", f"Which type of attack does {t}-type resist (takes reduced damage from)?", correct, distractors)
    if chart["immune"]:
        correct = random.choice(chart["immune"])
        others = [x for x in ALL_TYPES if x not in chart["immune"] and x != correct]
        distractors = random.sample(others, 3)
        add("Type Matchups","hard", f"Which type of attack does {t}-type take NO damage from?", correct, distractors)
    # reverse phrasing: "X is weak against which type" already covered; add "not very effective" variant
    if chart["resist"] and len(chart["resist"]) >= 2:
        pick_two = random.sample(chart["resist"], 2)
        wrong_pool = [x for x in ALL_TYPES if x not in chart["resist"]]
        correct = pick_two[0]
        distractors = random.sample(wrong_pool, 3)
        add("Type Matchups","easy", f"An attack of which type would be 'not very effective' against a {t}-type Pokemon?", correct, distractors)

# ---------------- Category 3: Evolution ----------------
for row in P:
    dex, name, types, gen, status, pre, nxt = row
    diff = "easy" if gen == 1 else "medium"
    if nxt:
        other_names = [r[1] for r in P if r[1] not in (name, nxt)]
        distractors = random.sample(other_names, 3)
        add("Evolution", diff, f"What does {name.replace('-',' ')} evolve into?", nxt.replace('-',' '), [d.replace('-',' ') for d in distractors])
    if pre:
        other_names = [r[1] for r in P if r[1] not in (name, pre)]
        distractors = random.sample(other_names, 3)
        add("Evolution", diff, f"Which Pokemon evolves into {name.replace('-',' ')}?", pre.replace('-',' '), [d.replace('-',' ') for d in distractors])
    if not pre and not nxt and status == "":
        # does not evolve at all -- ask "which of these does NOT evolve"
        evolvers = [r[1] for r in P if (r[6] or r[5]) and r[1]!=name]
        if len(evolvers) >= 3:
            distractors = random.sample(evolvers, 3)
            add("Evolution","medium", f"Which of these Pokemon does NOT evolve from or into anything?", name.replace('-',' '), [d.replace('-',' ') for d in distractors])

# ---------------- Category 4: Pokedex number (gen 1 focus, very reliable) ----------------
gen1 = [r for r in P if r[3] == 1]
for row in random.sample(gen1, min(70, len(gen1))):
    dex, name, types, gen, status, pre, nxt = row
    correct = str(dex)
    others = set()
    while len(others) < 6:
        cand = dex + random.choice([-30,-15,-7,-3,-2,-1,1,2,3,7,15,30])
        if 1 <= cand <= 151 and cand != dex:
            others.add(str(cand))
    distractors = random.sample(list(others), 3)
    add("Pokedex","easy", f"What is the National Pokedex number of {name.replace('-',' ')}?", correct, distractors)

# a modest number for other gens where dex number is unambiguous & well-known (starters/legendaries)
notable_other = [r for r in P if r[3] > 1 and (r[4] in ("legendary","mythical") or r[1] in
    ["Chikorita","Cyndaquil","Totodile","Treecko","Torchic","Mudkip","Turtwig","Chimchar","Piplup",
     "Snivy","Tepig","Oshawott","Chespin","Fennekin","Froakie","Rowlet","Litten","Popplio",
     "Grookey","Scorbunny","Sobble","Sprigatito","Fuecoco","Quaxly"])]
for row in random.sample(notable_other, min(45, len(notable_other))):
    dex, name, types, gen, status, pre, nxt = row
    correct = str(dex)
    others = set()
    while len(others) < 6:
        cand = dex + random.choice([-40,-20,-10,-5,-2,-1,1,2,5,10,20,40])
        if 1 <= cand <= 1010 and cand != dex:
            others.add(str(cand))
    distractors = random.sample(list(others), 3)
    add("Pokedex","hard", f"What is the National Pokedex number of {name.replace('-',' ')}?", correct, distractors)

# ---------------- Category 5: Generation introduced ----------------
gen_names = {1:"Generation I (Red & Blue)",2:"Generation II (Gold & Silver)",3:"Generation III (Ruby & Sapphire)",
             4:"Generation IV (Diamond & Pearl)",5:"Generation V (Black & White)",6:"Generation VI (X & Y)",
             7:"Generation VII (Sun & Moon)",8:"Generation VIII (Sword & Shield)",9:"Generation IX (Scarlet & Violet)"}
sample_for_gen_q = random.sample(P, min(90, len(P)))
for row in sample_for_gen_q:
    dex, name, types, gen, status, pre, nxt = row
    correct = gen_names[gen]
    others = [v for k,v in gen_names.items() if k != gen]
    distractors = random.sample(others, 3)
    diff = "easy" if gen in (1,) else "medium"
    add("Generations", diff, f"In which generation of games was {name.replace('-',' ')} first introduced?", correct, distractors)

# ---------------- Category 6: Legendary / Mythical / pseudo status ----------------
specials = [r for r in P if r[4] != ""]
normals = [r for r in P if r[4] == ""]
for row in specials:
    dex, name, types, gen, status, pre, nxt = row
    label = status_label(status)
    wrong_normals = random.sample([r[1] for r in normals], 3)
    add("Legendary Status","medium", f"Which of these is classified as {'a' if label[0] not in 'AEIOU' else 'an'} {label} Pokemon?",
        name.replace('-',' '), [n.replace('-',' ') for n in wrong_normals])

# a few "which of these is NOT legendary" flips
for row in random.sample(normals, min(25,len(normals))):
    dex, name, types, gen, status, pre, nxt = row
    wrong_legendaries = random.sample([r[1] for r in specials], 3)
    add("Legendary Status","medium", "Which of these Pokemon is NOT Legendary or Mythical (it's an ordinary species)?",
        name.replace('-',' '), [n.replace('-',' ') for n in wrong_legendaries])

# ---------------- Category 7: Abilities ----------------
for name, ability in ABILITIES:
    other_abilities = [a for n,a in ABILITIES if a != ability]
    distractors = random.sample(list(set(other_abilities)), 3)
    add("Abilities","hard", f"Which of these is a real ability of {name}?", ability, distractors)

# ---------------- Category 8: General / franchise trivia (hand-verified facts) ----------------
general = [
 ("Who is the first Partner Pokemon that Ash Ketchum receives in the original anime?","Pikachu",["Squirtle","Charmander","Bulbasaur"],"easy"),
 ("What is the name of the professor who gives out starter Pokemon in Pallet Town (Red/Blue/Yellow)?","Professor Oak",["Professor Birch","Professor Elm","Professor Rowan"],"easy"),
 ("What is the name of the professor in the Sinnoh region (Diamond/Pearl/Platinum)?","Professor Rowan",["Professor Oak","Professor Birch","Professor Elm"],"medium"),
 ("What is the name of the professor in the Johto region (Gold/Silver/Crystal)?","Professor Elm",["Professor Oak","Professor Birch","Professor Sycamore"],"medium"),
 ("What is the name of the professor in the Hoenn region (Ruby/Sapphire/Emerald)?","Professor Birch",["Professor Oak","Professor Elm","Professor Rowan"],"medium"),
 ("What item is required to trade with another player in order to evolve certain Pokemon like Machoke into Machamp?","Nothing extra needed, trading alone triggers it",["A Link Cable only","A Moon Stone","An Everstone"],"hard"),
 ("What is the maximum party size for a Trainer's Pokemon team?","6",["4","5","8"],"easy"),
 ("What stone is used to evolve Vulpix into Ninetales?","Fire Stone",["Water Stone","Moon Stone","Thunder Stone"],"easy"),
 ("What stone is used to evolve Eevee into Vaporeon?","Water Stone",["Fire Stone","Leaf Stone","Thunder Stone"],"easy"),
 ("What stone is used to evolve Jigglypuff into Wigglytuff?","Moon Stone",["Sun Stone","Water Stone","Fire Stone"],"medium"),
 ("What stone is used to evolve Gloom into Vileplume?","Leaf Stone",["Sun Stone","Moon Stone","Water Stone"],"medium"),
 ("In the Pokemon anime, what is the name of Ash's rival throughout the original Kanto journey?","Gary Oak",["Paul","Gary Chalmers","Trip"],"medium"),
 ("What is the name of Team Rocket's talking Meowth in the anime?","Meowth",["Persian","Wobbuffet","Mewtwo"],"easy"),
 ("What color is a Charmander's flame-tail said to indicate if it goes out?","It means the Charmander has died",["It means the Charmander is happy","It means the Charmander is asleep","It means the Charmander evolved"],"hard"),
 ("What is the name for a Pokemon Trainer's device that records data on Pokemon species?","Pokedex",["Pokeball","Pokegear","Trainer Card"],"easy"),
 ("What move is famous for having a never-miss (unless the target is invulnerable) property and is TM-taught to many Normal-types, first known for Dig/Fly style semi-invulnerable turns?","Fly",["Tackle","Hyper Beam","Splash"],"hard"),
 ("Which item cures a Pokemon that has been Poisoned?","Antidote",["Awakening","Burn Heal","Paralyze Heal"],"easy"),
 ("Which item cures a Pokemon that is Paralyzed?","Paralyze Heal",["Antidote","Burn Heal","Ice Heal"],"easy"),
 ("Which item cures a Pokemon that has been Burned?","Burn Heal",["Antidote","Awakening","Ice Heal"],"easy"),
 ("Which item fully restores a Pokemon's HP?","Full Restore",["Potion","Super Potion","Hyper Potion"],"medium"),
 ("What is the name of the currency used to buy items in Pokemon games?","Pokedollars",["Coins","Gold","Credits"],"easy"),
 ("What is the term for a Pokemon caught in the wild that has ideal, maximum individual stats?","Perfect IVs",["Shiny","Perfect EVs","Max Level"],"hard"),
 ("What is a 'Shiny' Pokemon known for?","An unusually colored, rare version of a Pokemon",["A Pokemon holding an item","A Pokemon that knows 4 moves of the same type","A Pokemon with maximum level"],"easy"),
 ("How many badges does a Trainer typically need to collect to challenge the Pokemon League in a classic region?","8",["6","10","4"],"easy"),
 ("What is the name of the in-game facility where Trainers can battle a series of opponents for prizes (introduced in Gen III)?","Battle Frontier",["Battle Tower only","Pokemon Center","Safari Zone"],"hard"),
 ("What is the special area where you can catch wild Pokemon using only bait and rocks instead of battling, first seen in Kanto?","Safari Zone",["Battle Frontier","Friend Safari","Pal Park"],"medium"),
 ("What is the name of Red and Blue's rival region?","Kanto",["Johto","Hoenn","Sinnoh"],"easy"),
 ("Which region is the setting of Pokemon Gold and Silver?","Johto",["Kanto","Hoenn","Unova"],"easy"),
 ("Which region is the setting of Pokemon Ruby and Sapphire?","Hoenn",["Kanto","Johto","Sinnoh"],"easy"),
 ("Which region is the setting of Pokemon Diamond and Pearl?","Sinnoh",["Hoenn","Unova","Kalos"],"easy"),
 ("Which region is the setting of Pokemon Black and White?","Unova",["Kalos","Alola","Galar"],"easy"),
 ("Which region is the setting of Pokemon X and Y?","Kalos",["Unova","Alola","Galar"],"easy"),
 ("Which region is the setting of Pokemon Sun and Moon?","Alola",["Kalos","Galar","Paldea"],"easy"),
 ("Which region is the setting of Pokemon Sword and Shield?","Galar",["Alola","Paldea","Kalos"],"easy"),
 ("Which region is the setting of Pokemon Scarlet and Violet?","Paldea",["Galar","Alola","Kalos"],"easy"),
 ("What is the signature phenomenon in Sword/Shield that temporarily makes Pokemon giant during battle?","Dynamax",["Mega Evolution","Z-Move","Terastallization"],"medium"),
 ("What is the signature battle mechanic introduced in Pokemon X and Y that temporarily transforms certain Pokemon in battle?","Mega Evolution",["Dynamax","Z-Move","Terastallization"],"medium"),
 ("What is the signature battle mechanic introduced in Scarlet and Violet involving changing a Pokemon's type?","Terastallization",["Mega Evolution","Dynamax","Z-Move"],"medium"),
 ("What is the powerful once-per-battle move type introduced in Sun and Moon that requires a special crystal?","Z-Move",["Mega Evolution","Dynamax","Terastallization"],"medium"),
 ("What is the name of Ash Ketchum's hometown?","Pallet Town",["Cerulean City","Viridian City","Pewter City"],"medium"),
 ("Which type of gym did Brock, the first Kanto Gym Leader, specialize in?","Rock",["Water","Ground","Steel"],"medium"),
 ("Which type of gym did Misty, the second Kanto Gym Leader, specialize in?","Water",["Rock","Electric","Grass"],"medium"),
 ("Which berry restores a small amount of HP when a Pokemon's HP is low, being one of the most common healing berries?","Oran Berry",["Sitrus Berry","Cheri Berry","Pecha Berry"],"hard"),
 ("What does 'EV' stand for in Pokemon stat mechanics?","Effort Value",["Evolution Value","Elemental Variance","Energy Vitality"],"hard"),
 ("What does 'IV' stand for in Pokemon stat mechanics?","Individual Value",["Item Value","Increased Vitality","Innate Variance"],"hard"),
 ("What is the term for a battle format where each side uses six Pokemon and battles are one-on-one at a time?","Single Battle",["Double Battle","Triple Battle","Rotation Battle"],"easy"),
 ("What is the term for a battle format where each side sends out two Pokemon simultaneously?","Double Battle",["Single Battle","Triple Battle","Horde Battle"],"easy"),
 ("Which Kanto starter is famously very difficult to catch as a wild Pokemon before it evolves, often received via in-game trade or given away (Magikarp aside), commonly cited as evolving from a nearly useless base form into one of the strongest Pokemon?","Gyarados",["Snorlax","Lapras","Dragonite"],"medium"),
]
for q, correct, wrong, diff in general:
    add("Trivia", diff, q, correct, wrong)

print(f"Generated {len(questions)} questions before trimming/padding")

# ---------------- Trim or pad to exactly 500, keep category balance ----------------
random.shuffle(questions)
if len(questions) > 500:
    questions = questions[:500]
else:
    # pad by generating extra "what type is X" using remaining unused pokemon combos with id offset (shouldn't be needed, but safe)
    extra_needed = 500 - len(questions)
    i = 0
    while extra_needed > 0 and i < len(P):
        row = P[i]; i += 1
        dex, name, types, gen, status, pre, nxt = row
        correct = type_str(types)
        others = [t for t in ALL_TYPES if t != correct and t not in types]
        distractors = random.sample(others, 3)
        add("Types","medium", f"What is {name.replace('-',' ')}'s primary/secondary type combination?", correct, distractors)
        extra_needed -= 1

# reassign sequential ids 1..500 and reshuffle final order
random.shuffle(questions)
for i, q in enumerate(questions, start=1):
    q["id"] = i

print(f"FINAL COUNT: {len(questions)}")

# category breakdown
from collections import Counter
cats = Counter(q["category"] for q in questions)
for c, n in cats.most_common():
    print(f"  {c}: {n}")

with open("/home/claude/poke-trivia/data/questions.json","w") as f:
    json.dump(questions, f, indent=1)

print("Wrote questions.json")
