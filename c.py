from math import ceil


MAX_HOTKEYS = 12    #seems same for OG and TS
CONTEXT_TIPS = 19   #seems same for OG and TS
JOURNAL_STATISTICS = 16 #code says 17, but why only 16 in the save/game?
                        #gog_steam assumed to have 17

SKILLS_STR_INT = {"SWORD" : 0,
                  "CLUB" : 1,
                  "HAMMER" : 2,
                  "AXE" : 3,
                  "SPEAR" : 4,
                  "STAFF" : 5,
                  "POLEARM" : 6,
                  "BOW" : 7,
                  "CRIT" : 8,
                  "SPELLCAST" : 9,
                  "DUAL" : 10,
                  "SHIELD" : 11,
                  "ATTACKMAG" : 12,
                  "DEFENSEMAG" : 13,
                  "CHARMMAG" : 14}

SKILLS_GAMESTR_INT = dict(zip(("SKILLSWORD",
	                            "SKILLCLUB",
	                            "SKILLHAMMER",
	                            "SKILLAXE",
	                            "SKILLSPEAR",
	                            "SKILLSTAFF",
	                            "SKILLPOLEARM",
	                            "SKILLBOW",
	                            "SKILLCRITICALSTRIKE",
	                            "SKILLSPELLCASTING",
	                            "SKILLDUALWIELD",
	                            "SKILLSHIELD",
	                            "SKILLATTACKMAGIC",
	                            "SKILLDEFENSEMAGIC",
	                            "SKILLCHARMMAGIC"), range(15)))
MAGIC_SPHERES = 3
MAX_SPELLS_PER_SPHERE = 6
ACTIVATION_TYPES = 2

def DMG_TYPES_STR_INT(wg) -> dict:
    ret = {"PIERCE": 0,
            "SLASH": 1,
            "CRUSH": 2,
            "MAGIC": 3,
            "FIRE": 4,
            "ICE": 5,
            "ELECTRIC": 6,
            "UNDEAD": 7}

    if wg in {'UR', 'TS'}:
        ret["HEROIC"] = 8
    return ret

def DMG_TYPES_INT_STR(wg) -> dict:
    ret = {0: "PIERCE",
            1: "SLASH",
            2: "CRUSH",
            3: "MAGIC",
            4: "FIRE",
            5: "ICE",
            6: "ELECTRIC",
            7: "UNDEAD"}

    if wg in {'UR', 'TS'}:
        ret[8] = "HEROIC"
    return ret

ENCHANTS_STR_INT = {"+STR": 0,
            "+DEX": 1,
            "+VIT": 2,
            "+MAG": 3,
            "+MAN": 4,
            "+HP": 5,
            "+STA": 6,
            "MANREGEN": 7,
            "HPREGEN": 8,
            "STAREGEN": 9,
            "+DEF": 10,
            "+ATT": 11,
            "+DMG": 12,
            "+DMGTAKEN": 13,
            "KNOCKBACK": 14,
            "SWORD": 15,
            "CLUB": 16,
            "HAMMER": 17,
            "AXE": 18,
            "SPEAR": 19,
            "STAFF": 20,
            "POLEARM": 21,
            "BOW": 22,
            "CRIT": 23,
            "SPELLCAST": 24,
            "DUAL": 25,
            "SHIELD": 26,
            "ATTACKMAG": 27,
            "DEFENSEMAG": 28,
            "CHARMMAG": 29,
            "%STR": 30,
            "%DEX": 31,
            "%VIT": 32,
            "%MAG": 33,
            "%MAN": 34,
            "%HP": 35,
            "%STA": 36,
            "SPEED": 37,
            "ATTSPEED": 38,
            "%DEF": 39,
            "%ATT": 40,
            "%DMG": 41,
            "%DMGTAKEN": 42,
            "MAGICDROP": 43,
            "GOLDDROP": 44,
            "CASTSPEED": 45,
            "LIFESTEAL": 46,    
            "MANSTEAL": 47,
            "DMGREFLECT": 48,
            "BLOCK": 49,
            "REDREQ": 50,
            "PIERCE": 51,
            "SLASH": 52,
            "CRUSH": 53,
            "MAGIC": 54,
            "FIRE": 55,
            "ICE": 56,
            "ELECTRIC": 57}

ENCHANTS_INT_STR = {v:k for k,v in ENCHANTS_STR_INT.items()}

ENCHANTS_GAMESTR_STR = dict(zip(("STRENGTH",
    "DEXTERITY",
    "VITALITY",
    "MAGIC",
    "MANA",
    "HP",
    "STAMINA",
    "MANARECHARGE",
    "HPRECHARGE",
    "STAMINARECHARGE",
    "ARMORBONUS",
    "TOHITBONUS",
    "DAMAGEBONUS",
    "DAMAGETAKEN",
    "KNOCKBACK",
    "SKILLSWORD",
    "SKILLCLUB",
    "SKILLHAMMER",
    "SKILLAXE",
    "SKILLSPEAR",
    "SKILLSTAFF",
    "SKILLPOLEARM",
    "SKILLBOW",
    "SKILLCRITICALSTRIKE",
    "SKILLSPELLCASTING",
    "SKILLDUALWIELD",
    "SKILLSHIELD",
    "SKILLATTACKMAGIC",
    "SKILLDEFENSEMAGIC",
    "SKILLCHARMMAGIC",
    "PERCENTSTRENGTH",
    "PERCENTDEXTERITY",
    "PERCENTVITALITY",
    "PERCENTMAGIC",
    "PERCENTMANA",
    "PERCENTHP",
    "PERCENTSTAMINA",
    "PERCENTSPEED",
    "PERCENTATTACKSPEED",
    "PERCENTARMORBONUS",
    "PERCENTTOHITBONUS",
    "PERCENTDAMAGEBONUS",
    "PERCENTDAMAGETAKEN",
    "PERCENTMAGICALDROP",
    "PERCENTGOLDDROP",
    "PERCENTCASTSPEED",
    "PERCENTLIFESTOLEN",
    "PERCENTMANASTOLEN",
    "PERCENTDAMAGEREFLECTED",
    "PERCENTBLOCKCHANCE",
    "PERCENTITEMREQUIREMENTS",
    "PERCENTPIERCINGRESISTANCE",
    "PERCENTSLASHINGRESISTANCE",
    "PERCENTCRUSHINGRESISTANCE",
    "PERCENTMAGICALRESISTANCE",
    "PERCENTFIRERESISTANCE",
    "PERCENTICERESISTANCE",
    "PERCENTELECTRICRESISTANCE"), ENCHANTS_STR_INT))

ENCHANTS_STR_GAMESTR = {v:k for k,v in ENCHANTS_GAMESTR_STR.items()}

ENCHANT_TABLE = [
                    " STATS1 / STATS2 / RESIST / SKILL1 / SKILL2 / OTHER1 / OTHER2 ",
                    "%STR/+STR/%DMGTAKEN/SWORD/SPELLCAST/SPEED/KNOCKBACK",
                    "%DEX/+DEX/+DMGTAKEN/CLUB/CRIT/ATTSPEED/HPREGEN",
                    "%VIT/+VIT/SLASH/HAMMER/DUAL/CASTSPEED/MANREGEN",
                    "%MAG/+MAG/CRUSH/AXE/SHIELD/LIFESTEAL/STAREGEN",
                    "%DMG/+DMG/MAGIC/SPEAR/ATTACKMAG/MANSTEAL/REDREQ",
                    "%ATT/+ATT/FIRE/STAFF/DEFENSEMAG/BLOCK/MAGICDROP",
                    "%DEF/+DEF/ICE/POLEARM/CHARMMAG/DMGREFLECT/GOLDDROP",
                    "%HP/+HP/ELECTRIC/BOW/ / / ",
                    "%STA/+STA/PIERCE/ / / / ",
                    "%MAN/+MAN/ / / / / "
                    ]

OGUR_SHORTCUT_SLOT = {
        "HEAD": 0,
        "NECK": 6,
        "RHAND": 3,
        "LHAND": 2, #shield included
        "CHEST": 1,
        "GLOVES": 5,
        "RRING": 9,
        "LRING": 8,
        "BELT": 10,
        "BOOTS": 7
        }

TS_SHORTCUT_SLOT = dict(OGUR_SHORTCUT_SLOT, CLOAK = 11, EAR = 12)

URTS_REALMS_HISTORY_INT_STR = {None: "Grove",   4: "Master",    52: "Master",
                                                1: "Druantia",  49: "Druantia",
                                                2: "Typhon",    50: "Typhon",
                                                                48: "Grove",
                                                                53: "Chamber"}

def URTS_REALMS_QUEST_INT_STR(wg) -> dict:
    if wg == "OG":
        return {b'': "Grove"}
    if wg == "UR":
        return {1: "Druantia", 2: "Typhon", 4: "Master"}
    if wg == "TS":
        return {0: "Chamber", 1: "Druantia", 2: "Grove", 3: "Master", 4: "Typhon"}

def ITEM_EXTS(wg) -> set:
    if wg == "OG": return {r"\ITEMS\en-US\items.dat"}
    if wg == "UR": return {r"\ITEMS\en-US\items.dat", r"\REALMS\Goldshare\ITEMS\en-us\items.dat"}
    if wg == "TS": return {r"\ITEMS\en-US\items.dat", r"\REALMS\Goldshare\ITEMS\en-us\items.dat", r"\REALMS\URGold\ITEMS\en-us\items.dat"}

def MONSTER_EXTS(wg) -> set:
   if wg == "OG":
       return {r'\MONSTERS\en-US\monsters.dat'}
   if wg == "UR":
       return {r'\MONSTERS\en-US\monsters.dat', r'\REALMS\Goldshare\MONSTERS\en-US\monsters.dat', r'\REALMS\Typhon\MONSTERS\en-US\monsters.dat', \
           r'\REALMS\Temple\MONSTERS\en-US\monsters.dat', r'\REALMS\Druantia\MONSTERS\en-US\monsters.dat'}
   if wg == "TS":
       return {r'\MONSTERS\en-US\monsters.dat', r'\REALMS\Goldshare\MONSTERS\en-US\monsters.dat', r'\REALMS\Typhon\MONSTERS\en-US\monsters.dat', \
           r'\REALMS\Temple\MONSTERS\en-US\monsters.dat', r'\REALMS\Druantia\MONSTERS\en-US\monsters.dat', r'\REALMS\Chamber\MONSTERS\en-us\monsters.dat'}


def SPELL_EXTS(wg) -> set:
    if wg == "OG":
        return {r'\SPELLS\en-US\spells.dat'}
    if wg == "UR":
        return {r'\SPELLS\en-US\spells.dat', r'\REALMS\Goldshare\SPELLS\en-US\spells.dat'}
    if wg == "TS":
        return {r'\SPELLS\en-US\spells.dat', r'\REALMS\Goldshare\SPELLS\en-US\spells.dat', r'\REALMS\URGold\SPELLS\en-US\spells.dat'}


def DIFFICULTIES_S_INTSTR(wg) -> dict:
    if wg == "OG":
        return {'P': (0, "Page"), 'A': (1, "Adventurer"), 'H': (2, "Hero"), 'L': (3, "Legend")}
    else:
        return {'P': (0, "Page"), 'A': (1, "Adventurer"), 'H': (2, "Hero"), 'L': (3, "Legend"), 'HA': (4, "Hardcore")}


RANK_TOHIT = {'': 1.0, "ELITE": 1.25, "LEGENDARY": 2.0}
RANK_POWER = {'': 1.0, "ELITE": 2.0, "LEGENDARY": 4.0}


def CRITSHIELD_SKILL_TO_PERC(n) -> float:
    perc = 50 - 50 / (n * 0.03 + 1)
    return 50 if perc > 50 else perc


def DUAL_SKILL_TO_MULT(n, hand: str) -> float:
    if (hand := hand.upper()) == "P":
        reduc = 50 - 50 / (n * 0.05 + 1)
        if reduc > 50: reduc = 50
        reduc /= 50
        reduc *= 0.25
        return 0.75 + reduc
    elif hand == "S":
        reduc = 50 - 50 / (n * 0.05 + 1)
        if reduc > 50: reduc = 50
        reduc /= 50
        reduc *= 0.5
        return 0.5 + reduc


RANKS_WITH_POSTSPACE = ("ELITE ", "LEGENDARY ")

#assumed same for all 3, but should also be verified already
# (fps in animation.dat, compressionfactor unapplied), (frames, compressionfactor, compressedframes in .sma)
# ATTACK_ANIMATION_INFO = {"SLASH":   (40, 33, 50, 17),
#                         "SLASH2":   (30, 21, 50, 11),
#                         "SPEAR":    (40, 33, 50, 17),
#                         "POLE":     (40, 37, 50, 19),
#                         "POLE2":    (40, 21, 50, 11),
#                         "BOW":      (45, 47, 50, 24),
#                         "CROSSBOW": (35, 37, 50, 19)}


ATTACKSPEEDS = {"SLOWEST": 0.6, "SLOW": 0.8, "NORMAL": 1.0, "FAST": 1.1, "FASTEST": 1.2}

# Length( void )		{ return (float32)CompressedFrames() * FrameLength();	};
ATTACKTYPE_ANIMATIONLENGTHS = {"SLASH":   [17 * (1 / (40/2)), 11 * (1 / (30/2))],
                              "SPEAR":    [17 * (1 / (40/2))],
                              "POLE":     [19 * (1 / (40/2)), 11 * (1 / (40/2))],
                              "BOW":      [24 * (1 / (45/2))],
                              "CROSSBOW": [19 * (1 / (35/2))]}


WEAPONTYPE_ATTACKTYPE = {"SWORD":   "SLASH",
                        "CLUB":     "SLASH",
                        "HAMMER":   "SLASH",
                        "AXE":      "SLASH",
                        "SPEAR":    "SPEAR",
                        "STAFF":    "POLE",
                        "POLEARM":  "POLE",
                        "BOW":      "BOW",
                        "CROSSBOW": "CROSSBOW"}

# ASSUMPTION this is just a guess for what is nonconforming
TS_NONCONFOM = {"POTION",
            "SCROLL",
            "BOOK",
            "SPELL",
            "PETFOOD",
            "TAROT"}


RANK_MULTIPLIERS = {'': 1, "ELITE": 2, "LEGENDARY": 4}
GRADE_MULTIPLIERS = {0: 0.0, 1: 0.2, 2: 0.4, 3: 0.6}

def DMG_APPLY_RANK_GRADE(baseRange: tuple[int], rank: str, grade: int) -> tuple[int]:
    rankRange = (baseRange[0] * RANK_MULTIPLIERS[rank], baseRange[1] * RANK_MULTIPLIERS[rank])
    gradeBonus = ceil(rankRange[1] * GRADE_MULTIPLIERS[grade])
    if grade and gradeBonus < 1: gradeBonus = 1 #in game code, only matters when maxDmg < 1
    return (rankRange[0] + gradeBonus, rankRange[1] + gradeBonus)


def ENCHANTS_STR_LOOKUP(s, wg) -> int | str:
    return ENCHANTS_STR_INT[s] if wg in {"OG", "UR"} else ENCHANTS_STR_GAMESTR[s]

#flat, percent
RACE_STRENGTH_BONUSES = {b"HALFORC": (15, 5), b"GOLEM": (0, 5)}

#flat, percent
RACE_DEXTERITY_BONUSES = {b"SHADOWELF": (15, 5)}

#all flat 5
RACE_SKILL_BONUSES = {b"HUMAN":     {"STAFF", "ATTACKMAG", "DEFENSEMAG", "CHARMMAG", "SPELLCAST"},
                      b"SHADOWELF": {"BOW", "SPEAR", "DUAL", "SWORD"},
                      b"HALFORC":   {"AXE", "CLUB", "POLEARM", "HAMMER", "SHIELD"},
                      b"GOLEM":     {"CRIT"}}

#TODO theres also crit and dual you forgot ... WEBDEEV show different colors!
_C__DMGWHATIF_COLS1_DUAL = ( [(9, "ID"), (6, "Swap"), (12, "Strength"), (12, "Dexterity"), (21, "[+/%]DMG"), (14, "Attack")], \
                             [(12, "%ATTSPEED"), (12, "Defense")] )
def DMGWHATIF_COLS1_DUAL(skillStr):
    return _C__DMGWHATIF_COLS1_DUAL[0] + [(13, skillStr)] +  _C__DMGWHATIF_COLS1_DUAL[1]

_C__DMGWHATIF_COLS1_NODUAL = ( [(10, "ID"), (13, "Strength"), (13, "Dexterity"), (22, "[+/%]DMG"), (15, "Attack")], \
                             [(13, "%ATTSPEED"), (13, "Defense")] )
def DMGWHATIF_COLS1_NODUAL(skillStr):
    return _C__DMGWHATIF_COLS1_NODUAL[0] + [(13, skillStr)] +  _C__DMGWHATIF_COLS1_NODUAL[1]

DMGWHATIF_COLS2_NODUAL = ((10, "ID"), (24, "Actual Range"), (13, "Crit%"), (13, "HPS"), (13, "Hit%"), (22, "Stats Menu"), (18, "DPS"))
DMGWHATIF_COLS2_DUAL = ((6, "ID"), (3, "?"), (30, "Menu Range(Other Hand Bonus)"), (19, "Actual Range"), (8, "Crit%"), (8, "HPS"), (8, "Hit%"), (19, "Stats Menu"), (10, "DPS"))