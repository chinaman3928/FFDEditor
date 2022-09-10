from struct import pack
from random import uniform, randint
from string import capwords
from math import ceil

from u import btos, full, sToFull, bToFull, padLst, get
from c import RANK_TOHIT, RANK_POWER, ENCHANTS_STR_LOOKUP, RACE_STRENGTH_BONUSES, RACE_DEXTERITY_BONUSES, SKILLS_STR_INT, RACE_SKILL_BONUSES


I = '    ' #four spaces, but cant import from ui otherwise circular import

#  for each of the others too


class Character:
    def __init__(self):
        self.urts_firstFour = b''
        #self.templateName
        #self.origTemplateName
        #self.existenceTime
        #self.isPlayer
        #self.journal
        #self.transformationDuration
        #self.lifeDuration
        #self.townTimer
        #self.difficulty
        #self.scale
        #self.bravery
        #self.masInDungSeed
        #self.name
        #self.ancestorName
        #self.lineage
        #self.merchantStuff
        #self.gender, self.head, self.hair
        #self.dungLevel
        #self.portalGarbage
        #self._3d3xStuff
        #self.level
        #self.experience
        #self.hp, self.max_hp
        #self.fameStuff
        #self.stam, self.max_stam
        #self.mana, self.max_mana
        #self.attack, self.origAttack
        #self.natArmor, self. origNatArmor
        #self.expFameAwrd
        #self.unspentStats
        #self.unspentSkills
        #self.unique
        #self.resists
        #self.skills
        #self.spellNames
        #self.str
        #self.ostr
        #self.dex
        #self.odex
        #self.vit
        #self.ovit
        #self.mag
        #self.omag
        #self.walkSpeed, self.runSpeed
        #self.gold

        self.charEnchants = {"PASSIVE": [], "USAGE": []}

        self.items = {"EQUIPPED": [], "INVENTORY": []}

        self.quests = {"REGULAR": [], "MASTER": None}
        
        self.urts_charEndingGarbage1 = b''
        self.urts_realmsComplete = []
        self.urts_resists = []
        self.urts_charEndingGarbage2 = b''
        self.urts_deaths = b''
        self.ts_race = b''
        self.ts_spells: dict[bytes:list[bytes]] = dict()
        self.ts_29chunks = b''
        self.ts_charEndingGarbage14 = b''
        self.ts_30chunks = b''
        self.ts_charEndingLastThree = b''

    def __repr__(self) -> str:
        return f"<{btos(self.name)}>"


    def levelFullTemplateName(self) -> str:
        return f"Lv{self.level} {btos(self.name)} [{capwords(self.templateName.decode('utf-8'))}]"


    def urts_realmInt(self, wg) -> int|None:
        """None if OG."""
        if wg == "OG":
            return None
        return int.from_bytes(self.urts_charEndingGarbage1[:4], "little") if wg == "UR" else self.urts_charEndingGarbage1[6]


    #FUTURE TODO test that naturally summoned pets are exactly consistent with these stats
    def newPetHere(self, corpusChar: "CorpusCharacter", rank: str, level: int, time: float, wg: str) -> "Character":
        """self should be a preexisting PET.
        ranks: '', 'ELITE', 'LEGENDARY'"""
        
        adjLevel = (level - corpusChar.baseLevel) if level > corpusChar.baseLevel else corpusChar.baseLevel

        #applying rank changes
        rank_min_max_hp = (int(corpusChar.min_max_hp[0] * RANK_TOHIT[rank]), int(corpusChar.min_max_hp[1] * RANK_TOHIT[rank]))
        rank_str = int(corpusChar.str * RANK_POWER[rank])
        rank_dex = int(corpusChar.dex * RANK_POWER[rank])
        rank_vit = int(corpusChar.vit * RANK_POWER[rank])
        rank_mag = int(corpusChar.mag * RANK_POWER[rank])
        rank_attack = int(corpusChar.attack * RANK_TOHIT[rank])
        rank_skills = dict(corpusChar.skills)
        for skill in rank_skills:
            rank_skills[skill] = int(corpusChar.skills[skill] * RANK_POWER[rank])

        char = Character()

        if wg in {'UR', 'TS'}:
            char.urts_firstFour = self.urts_firstFour

        char.templateName = char.origTemplateName = f"{capwords(rank) + (' ' if rank else '')}{corpusChar.name}".encode('utf-8')
        char.existenceTime = 0.0
        char.isPlayer = False
        char.journal = b''
        char.transformationDuration = bytes(4)
        char.lifeDuration = time #TODO FUTURE i think if you make this <= 0, it doesnt count as a summon
        char.townTimer = bytes(4)
        char.difficulty = 1
        char.scale = uniform(*corpusChar.scaleRange)
        char.bravery = corpusChar.bravery
        char.masInDungSeed = self.masInDungSeed 
        char.name = char.ancestorName = "Summoned".encode('utf-8') + capwords(f"{' ' if rank else ''}{rank} {corpusChar.name}", ' ').encode('utf-8')
        char.lineage = bytes(4)

        char.merchantStuff = self.merchantStuff
        char.gender, char.head, char.hair = self.gender, self.head, self.hair
        char.dungLevel = self.dungLevel
        char.portalGarbage = self.portalGarbage
        char._3d3xStuff = self._3d3xStuff
        char.level = level
        char.experience = 0
        char.max_hp = rank_min_max_hp[1] + ceil( rank_min_max_hp[0] * adjLevel * 0.5 )
        char.hp = float(char.max_hp)
        char.fameStuff = self.fameStuff
        char.stam, char.max_stam = 0.0, 0 #seems to work itself out
        char.mana, char.max_mana = 0.0, 0 #seems to work itself out
        char.attack, char.origAttack = rank_attack + randint(3, 5)*adjLevel, 0
        char.natArmor, char.origNatArmor = corpusChar.natArmor + 2*adjLevel, 0
        char.expFameAward, char.unspentStats, char.unspentSkills, char.unique = \
            self.expFameAward, self.unspentStats, self.unspentSkills, self.unique
        char.resists = [corpusChar.resists.get(i, 0) for i in range(8)]
        if not corpusChar.isUndead: char.resists[7] = 100

        char.skills = [rank_skills.get(i, 0) for i in range(15)]
        for i in (9, 12, 13, 14):
            char.skills[i] += adjLevel // 3
        if char.skills[9] > 10: char.skills[9] = 10

        char.spellNames = b''.join( (b''.join(sToFull(s) for s in corpusChar.spells[key]) + bytes(2*(6-len(corpusChar.spells[key])))) \
            for key in ("ATTACK", "DEFENSE", "CHARM") ) + bytes(2)
        char.str = rank_str + 3*adjLevel
        char.ostr = 0
        char.dex = rank_dex + 3*adjLevel
        char.odex = 0
        char.vit = rank_vit + 3*adjLevel
        char.ovit = 0
        char.mag = rank_mag + 3*adjLevel
        char.omag = 0
        char.walkSpeed, char.runSpeed = corpusChar.walkSpeed, corpusChar.runSpeed
        char.gold = 0

        char.charEnchants = {"PASSIVE": [], "USAGE": []}

        char.items = {"EQUIPPED": [], "INVENTORY": []}

        char.quests = {"REGULAR": [], "MASTER": None}

        char.urts_charEndingGarbage1 = self.urts_charEndingGarbage1
        char.urts_realmsComplete = self.urts_realmsComplete
        if wg in {'UR', 'TS'}:
            char.urts_resists = [corpusChar.resists.get(i, 0) for i in range(9)]
            if not corpusChar.isUndead: char.urts_resists[7] = 100
        char.urts_charEndingGarbage2 = self.urts_charEndingGarbage2
        char.urts_deaths = self.urts_deaths
        char.ts_race = self.ts_race
        if wg in {'UR', 'TS'}:
            char.ts_spells = { sphere.encode('utf-8'):padLst([spell.encode('utf-8') for spell in corpusChar.spells[sphere]], bytes(2), 6) \
                for sphere in ("ATTACK", "DEFENSE", "CHARM", "RAGE") }
        char.ts_29chunks = self.ts_29chunks
        char.ts_charEndingGarbage14 = self.ts_charEndingGarbage14
        char.ts_30chunks = self.ts_30chunks
        char.ts_charEndingLastThree = self.ts_charEndingLastThree

        return char


    def cumEnchant(self, enchStr, wg, retInt=False) -> float | int:
        """Always pass the enchStr (ex %DMG); the rest is handled inside."""
        lookup = ENCHANTS_STR_LOOKUP(enchStr, wg)
        total = 0
        for lst in self.charEnchants.values():
            if (ench := get(lst, key = lambda e: e.type == ENCHANTS_STR_LOOKUP(enchStr, "OG"))):
                total += ench.value
        for item in self.items["EQUIPPED"]:
            if (ench := get(item.enchants["PASSIVE"], key = lambda e: e.lu(wg) == lookup)):
                total += ench.value
        return int(total) if retInt else total


    def fullStrength(self, wg, baseNoRaceStrength = None, plusStrength = None, percStrength = None) -> int:
        """baseNoRaceStrength overrides self.str.
        percStrengh overrides self.cumEnchant('%STR').
        plusStrength overrides self.cumEnchantr('+STR').
        Accounts for TS race."""
        if baseNoRaceStrength is None: baseNoRaceStrength = self.str
        if percStrength is None: percStrength = self.cumEnchant("%STR", wg)
        race_plus, race_perc = RACE_STRENGTH_BONUSES.get(self.ts_race[2:].upper(), (0,0)) if wg == "TS" else (0,0)
        strength = baseNoRaceStrength + race_plus
        strength += ceil(self.str * (percStrength + race_perc)/100)
        return strength + (int(self.cumEnchant("+STR", wg)) if plusStrength is None else plusStrength)

    def fullDexterity(self, wg, baseNoRaceDexterity = None, plusDexterity = None, percDexterity = None) -> int:
        """baseNoRaceDexterity overrides self.dex.
        percDexterity overrides self.cumEnchant('%DEX').
        plusDexterity overrides self.cumEnchant('+DEX').
        Accounts for TS race."""
        if baseNoRaceDexterity is None: baseNoRaceDexterity = self.dex
        if percDexterity is None: percDexterity = self.cumEnchant("%DEX", wg)
        race_plus, race_perc = RACE_DEXTERITY_BONUSES.get(self.ts_race[2:].upper(), (0,0)) if wg == "TS" else (0,0)
        dexterity = baseNoRaceDexterity + race_plus
        dexterity += ceil(self.dex * (percDexterity + race_perc)/100)
        return dexterity + (int(self.cumEnchant("+DEX", wg)) if plusDexterity is None else plusDexterity)

    def fullAttack(self, fullDex, skill, *, percAtt = None, plusAtt = None) -> int:
        attack = 50 + fullDex // 2 + (skill + 20) + self.level
        attack += ceil(attack * (self.cumEnchant("%ATT") if percAtt is None else percAtt)/100)
        return attack + int(self.cumEnchant("+ATT") if plusAtt is None else plusAtt)

    #keep in mind block chance enchant and cast speed enchant
    def fullSkill(self, name, wg) -> int:
        """Collapses 'BOW' and 'CROSSBOW'. Accounts for TS race."""
        n = 7 if name == "CROSSBOW" else SKILLS_STR_INT[name]
        return int(self.skills[n] + self.cumEnchant(name, wg) + \
            ((5 if name in RACE_SKILL_BONUSES[self.ts_race[2:].upper()] else 0) if wg == "TS" else 0))


    def getWrite(self, indent, wg) -> (bytearray | None, str | None):
        yield None, f"{I*indent}Begin write: {self.levelFullTemplateName()}."

        yield self.urts_firstFour + \
            full(self.templateName) + \
            full(self.origTemplateName) + \
            pack('f', self.existenceTime) + \
            bytes([self.isPlayer]) + \
            self.journal + \
            self.transformationDuration + \
            pack('f', self.lifeDuration) + \
            self.townTimer + \
            self.difficulty.to_bytes(4, "little") + \
            pack('f', self.scale) + \
            pack('f', self.bravery) + \
            self.masInDungSeed + \
            full(self.name) + \
            full(self.ancestorName) + \
            self.lineage + \
            self.merchantStuff + \
            self.gender.to_bytes(4, "little") + \
            self.head.to_bytes(4, "little") + \
            self.hair.to_bytes(4, "little") + \
            self.dungLevel.to_bytes(4, "little") + \
            self.portalGarbage + \
            self._3d3xStuff + \
            self.level.to_bytes(4, "little") + \
            self.experience.to_bytes(4, "little") + \
            pack('f', self.hp) + self.max_hp.to_bytes(4, "little") + \
            self.fameStuff + \
            pack('f', self.stam) + self.max_stam.to_bytes(4, "little") + \
            pack('f', self.mana) + self.max_mana.to_bytes(4, "little") + \
            self.attack.to_bytes(4, "little") + self.origAttack.to_bytes(4, "little") + \
            self.natArmor.to_bytes(4, "little") + self.origNatArmor.to_bytes(4, "little") + \
            self.expFameAward + \
            self.unspentStats.to_bytes(4, "little") + \
            self.unspentSkills.to_bytes(4, "little") + \
            self.unique + \
            b''.join(n.to_bytes(4, "little", signed=True) for n in self.resists) + \
            b''.join(n.to_bytes(4, "little") for n in self.skills) + \
            self.spellNames + \
            b''.join(n.to_bytes(4, "little") for n in (self.str, self.ostr, self.dex, self.odex, self.vit, self.ovit, self.mag, self.omag)) + \
            pack('f', self.walkSpeed) + \
            pack('f', self.runSpeed) + \
            self.gold.to_bytes(4, "little", signed = (wg != "TS")), None

        #remember that these are written OG wg style
        for lst in self.charEnchants.values():
            yield len(lst).to_bytes(4, "little"), None
            for ench in lst:
                for writeThis, printThis in ench.getWrite(indent+1):
                    yield writeThis, printThis

        yield sum(len(lst) for lst in self.items.values()).to_bytes(4, "little"), None
        for lst in self.items.values():
            for it in lst:
                for writeThis, printThis in it.getWrite(indent+1, wg):
                    yield writeThis, printThis

        yield len(self.quests["REGULAR"]).to_bytes(4, "little"), None
        for q in self.quests["REGULAR"]:
            for writeThis, printThis in q.getWrite(indent+1, wg):
                yield writeThis, printThis
        if self.quests["MASTER"] is None:
            yield bytes(4), None
        else:
            yield bytes([1,0,0,0]), None
            for writeThis, printThis in self.quests["MASTER"].getWrite(indent+1, wg):
                yield writeThis, printThis

        if wg in {'UR', 'TS'}:
            writeThis = bytearray(self.urts_charEndingGarbage1)
            writeThis += len(self.urts_realmsComplete).to_bytes(2, "little") + \
                b''.join( n.to_bytes(4, "little") for n in self.urts_realmsComplete)
            writeThis += len(self.urts_resists).to_bytes(2, "little") + \
                b''.join( n.to_bytes(4, "little", signed=True) for n in self.urts_resists)
            writeThis += self.urts_charEndingGarbage2
            writeThis += self.urts_deaths
            writeThis += self.ts_race
            if wg == "TS":
                writeThis += len(self.ts_spells).to_bytes(4, "little") + \
                    b''.join( bToFull(sphere) + len(spells).to_bytes(4, "little") + b''.join( bToFull(spell) for spell in spells) \
                        for sphere, spells in self.ts_spells.items() )
            writeThis += self.ts_29chunks
            writeThis += self.ts_charEndingGarbage14
            writeThis += self.ts_30chunks
            writeThis += self.ts_charEndingLastThree

            yield writeThis, None
        
        yield None, f"{I*indent}Finish write: {self.levelFullTemplateName()}."