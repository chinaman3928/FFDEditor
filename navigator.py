import chunk
import struct
import c
from u import repeatedDictKey, prefixRemoved

from character import Character
from item import Item
from bonus import Bonus
from enchant import Enchant
from quest import Quest
from history import History
from corpusCharacter import CorpusCharacter
from corpusItem import CorpusItem

I = '    ' #four spaces, but cant import from ui otherwise circular import

#hi yes note to self: sizeof( D3DXVECTOR3 ) + sizeof( D3DXMATRIX ) = 76
#new note to self: sizeof( D3DXVECTOR3 ) + sizeof( D3DXVECTOR3 ) + sizeof( D3DXMATRIX ) = 88 i think


class BadAssumptionError(Exception):
    pass


class Navigator:

    def __init__(self, wg: str, steam_gog: bool, file: bytes, itemCorpus: dict, charCorpus: dict, spellSpheres: dict):

        self.wg, self._steam_gog, self._file, self.itemCorpus, self.charCorpus, self.spellSpheres = \
                wg, steam_gog, file, itemCorpus, charCorpus, spellSpheres
        self._32_0 = self._steam_gog and self.wg == "TS"
        self._p = 0

        self._garbageUpTo = self._goTilPlayer()
        self.player = self._parseCharacter()
        self.pets = [self._parseCharacter() for _ in range(self._readInt())]
        self.histories = [self._parseHistory() for _ in range(self._readInt())]
        self._garbageResume = self._p

        
    #------------------------------------------------------------------------------------------------------------#
    # Methods for high-level navigation and reading.

    def _goTilPlayer(self) -> int:
        """Advances self._p til first byte of player. Then returns for self._garbageUpTo"""
        self._move(7 if self.wg == "OG" else 15)

        for n in range(c.MAX_HOTKEYS):
            self._passThisString()

        self._move(c.CONTEXT_TIPS)   #funny how all games have the same num of these tips
        
        return self._p
    
    def _parseCharacter(self) -> Character:
        char = Character()

        if self.wg in {"UR", "TS"}:
            char.urts_firstFour = self._read(4) #defaults to b'' in char.__init__

        char.templateName = self._passThisString(read = True)
        char.origTemplateName = self._passThisString(read = True)

        char.existenceTime = self._readFloat()
        char.isPlayer = bool(self._readInt(1))

        extra = (1 if self.wg == "OG" else 3) if self._steam_gog else 0
        char.journal = self._read((c.JOURNAL_STATISTICS + extra) * 4) if char.isPlayer else b''

        char.transformationDuration = self._read(4)
        char.lifeDuration = self._readFloat()
        char.townTimer = self._read(4)
        char.difficulty = self._readInt()
        char.scale = self._readFloat()
        char.bravery = self._readFloat()
        char.masInDungSeed = self._read(8)

        char.name = self._passThisString(read = True)
        char.ancestorName = self._passThisString(read = True)
        char.lineage = self._read(4)

        char.merchantStuff = self._read(5)
        char.gender, char.head, char.hair, char.dungLevel = (self._readInt() for _ in range(4))
        char.portalGarbage = self._read(5)
        char._3d3xStuff = self._read(88)
        char.level = self._readInt()
        char.experience = self._readInt()

        char.hp, char.max_hp = self._readFloat(), self._readInt()
        char.fameStuff = self._read(8)
        char.stam, char.max_stam = self._readFloat(), self._readInt()
        char.mana, char.max_mana = self._readFloat(), self._readInt()
        char.attack, char.origAttack = self._readInt(), self._readInt()
        char.natArmor, char.origNatArmor = self._readInt(), self._readInt()

        char.expFameAward = self._read(8)
        char.unspentStats = self._readInt()
        char.unspentSkills = self._readInt()
        char.unique = self._read(1)

        char.resists = [self._readInt(signed=True) for _ in range(len(c.DMG_TYPES_STR_INT("OG")))]

        char.skills = [self._readInt() for _ in range(len(c.SKILLS_STR_INT))]
        char.spellNames = b''.join((self._passThisString(read = True, full = True) \
            for _ in range(c.MAGIC_SPHERES*c.MAX_SPELLS_PER_SPHERE + 1)))

        char.str, char.ostr, char.dex, char.odex, char.vit, char.ovit, char.mag, char.omag = (self._readInt() for _ in range(8))
        char.walkSpeed, char.runSpeed = self._readFloat(), self._readFloat()
        char.gold = self._readInt(signed = (self.wg != "TS"))

        self._parseCharEnchants(char)

        for _ in range(self._readInt()):
            the_item = self._parseItem()
            char.items["EQUIPPED" if the_item.equipped else "INVENTORY"].append(the_item)

        char.quests["REGULAR"] = [self._parseQuest() for _ in range(self._readInt())]
        char.quests["MASTER"] = self._parseQuest() if bool(self._readInt()) else None

        self._urts_charEnding(char)

        return char

    def _urts_charEnding(self, char: "Character") -> None:
        """TODO FUTURE Still some assumptions. BadAssumptionError guards? Directly adds attributes."""
        if self.wg in {"UR", "TS"}:
            #lastRealm (4)(?) -> ts_weirdThree -> wholeTime (4) -> partTime (4) -> portalRealm (4) -> heroes
            char.urts_charEndingGarbage1 = self._read(18 if self.wg == "UR" else 21) #defaults to b'' in char.__init__()
            char.urts_charEndingGarbage1 += b''.join( self._passThisString(read = True, full = True) \
                for _ in range(int.from_bytes(char.urts_charEndingGarbage1[-2:], "little")) )

            char.urts_realmsComplete = [self._readInt() for _ in range(self._readInt(2))] #defaults to [] in char.__init__()
            
            char.urts_resists = [self._readInt(signed=True) for _ in range(self._readInt(2))] #defaults to [] in char.__init__()

            #postCount (4) -> portalCount (4)
            char.urts_charEndingGarbage2 = self._read(8) #defaults to b'' in char.__init__()
            char.urts_charEndingGarbage2 += b''.join( self._read(20) for _ in range(int.from_bytes(char.urts_charEndingGarbage2[-4:], "little")) )
                
            if self.wg == "UR" and self._steam_gog or self.wg == "TS":
                char.urts_deaths = self._read(4) #defaults to b'' in char.__init__()

            if self.wg == "TS":
                char.ts_race = self._passThisString(read = True, full = True) #defaults to b'' in char.__init__()

                char.ts_spells = { self._passThisString(read = True) : [self._passThisString(read = True) for spell in range(self._readInt())] \
                    for sphere in range(self._readInt()) } #defaults to dict() in char.__init__()

                char.ts_29chunks = self._read(4) #defaults to b'' in char.__init__()
                if char.isPlayer:
                    char.ts_29chunks += b''.join( (_16 := self._read(16)) + self._read(4*int.from_bytes(_16[-2:], "little") + 13) \
                        for _ in range(int.from_bytes(char.ts_29chunks[-4:], "little")) )

                char.ts_charEndingGarbage14 = self._read(14) #defaults to b'' in char.__init__()
                
                #idk what this is
                char.ts_30chunks = self._read(4) #defaults to b'' in char.__init__()
                char.ts_30chunks += b''.join( self._read(30) for _ in range(int.from_bytes(char.ts_30chunks[-4:], "little")) )

                char.ts_charEndingLastThree = self._read(3) #defaults to b'' in char.__init__()


    def _parseCharEnchants(self, char: Character) -> None:
        """Directly mutates char.charEnchants"""
        #storing oldwg and setting to OG bc every game writes the character's enchants the same way
        oldwg = self.wg
        self.wg = "OG"
        for key in char.charEnchants:
            for n in range(self._readInt()):
                char.charEnchants[key].append(self._parseEnchant())
        self.wg = oldwg

    def _parseItem(self, superItem: Item = None) -> Item:
        #cherry pick which i think are interestings
        it = Item(superItem)

        if self.wg in {"UR", "TS"}:
            it.urts_firstFour = self._read(4) #defaults to b'' in it.__init__

        it.baseName = self._passThisString(read = True)
        it.fullName = self._passThisString(read = True)

        it.slotIndex = self._readInt()
        it.equipped = bool(self._readInt(1))
        it.equippedGarbage = self._read(85)
        it.grade = self._readInt()
        it.gradeGarbage = self._read(3)
        it.armorBonus = self._readInt()
        it.sockets = self._readInt()
        it.socketsGarbage = self._read(7)
        it.bonuses = [self._parseBonus() for _ in range(self._readInt())]

        if self.wg == "TS":
            it.ts_bonusesGarbage = self._read(8) #defaults to b'' in it.__init__

        if self.wg in {"OG", "UR"}:
            it.enchants = {"PASSIVE": [self._parseEnchant() for _ in range(self._readInt())],
                           "USAGE":   [self._parseEnchant() for _ in range(self._readInt())]}

            it.subItems = [self._parseItem(it) for _ in range(self._readInt())]

            if self.wg == "UR":
                it.ur_heroID = self._passThisString(4, read = True, full = True) #defaults to b'' in it.__init__

        else:
            it.subItems = [self._parseItem(it) for _ in range(self._readInt())]

            toRead, expect = (8, bytes([2,0,0,0,0,0,0,0])) if self.ts_nonconforming(it.baseName) else (4, bytes([2,0,0,0]))
            it.ts_subitemsGarbage = self._passThisString(4, read = True, full = True) + self._read(toRead) #defaults to b'' in it.__init__
            if it.ts_subitemsGarbage[-toRead:] != expect:
                raise BadAssumptionError(f"Assumed [*] {expect} in enchants but got {it.ts_subitemsGarbage}. (pre-{self._p})")

            ### ASSUMPTION that only one enchant key ("PASSIVE")
            it.enchants = {"PASSIVE": [self._parseEnchant() for _ in range(self._readInt())],
                           "USAGE":   []}

            expectedZeroes = 2 if self.ts_nonconforming(it.baseName) else 6
            it.ts_ending = self._read(expectedZeroes) #defaults to b'' in it.__init__
            if it.ts_ending != b'\x00' * expectedZeroes:
                raise BadAssumptionError(f"Assumed {expectedZeroes} zeroes at the end but got {it.ts_ending}. (pre-{self._p})")

        return it

    def _parseBonus(self) -> Bonus:
        return Bonus(self._readInt(), self._readInt())

    def _parseEnchant(self) -> Enchant:
        ench = Enchant()

        if self.wg == "TS":
            ench.ts_firstFour = self._read(4) #defaults to b'' in ench.__init__
            if ench.ts_firstFour != b'\xff\xff\x01\x00':
                raise BadAssumptionError(f"Assumed b'\xff\xff\x01\x00' as ench.ts_firstFour, got {ench.ts_firstFour} (self._p-4)")

        ench.name = self._passThisString(read = True)
        ench.message = self._passThisString(read = True)

        ench.exclusive = bool(self._readInt(1))
        ench.type = self._readInt()
        ench.damageType = self._readInt()
        ench.positive = bool(self._readInt(1))
        ench.activation = self._readInt()
        ench.chanceOfSuccess = self._readInt()
        ench.chanceOfSuccessBonus = self._readInt()
        ench.chanceOfSuccessBonusPercent = self._readInt()
        ench.duration = self._readInt()
        ench.durationBonus = self._readInt() #stores it as a positive int but in the code a negative constant is used
        ench.durationBonusPercent = self._readInt()
        ench.value = self._readFloat()
        ench.valueBonus = self._readFloat()
        ench.valueBonusPercent = self._readFloat()
        ench.value2 = self._readFloat()
        ench.value2Bonus = self._readFloat()
        ench.value2BonusPercent = self._readFloat()
        ench.value3 = self._readFloat()
        ench.value3Bonus = self._readFloat()
        ench.value3BonusPercent = self._readFloat()
        ench.priceMultiplier = self._readFloat()

        if self.wg == "TS":
            ench.ts_beforeTypeStr = self._read(2) #defaults to b'' in ench.__init__
            if ench.ts_beforeTypeStr != b'\x00\x00':
                raise BadAssumptionError(f"Assumed 00 before enchant type string, got {ench.ts_beforeTypeStr}. ({self._p - 2})")
            ench.ts_typeStr = self._passThisString(read = True) #defaults to None in ench.__init__

        return ench

    def _parseQuest(self) -> Quest:
        q = Quest()

        if self.wg in {"UR", "TS"}:
            q.urts_firstFour = self._read(4) #defaults to b'' in q.__init__

        q.level = self._readInt()
        q.questType = self._readInt()

        q.spawned = bool(self._readInt(1))
        q.completed = bool(self._readInt(1))
        q.completionNotified = bool(self._readInt(1))

        q.questMonsterCount = self._readInt()
        q.questMonstersCompleted = self._readInt()
        q.questMinionCount = self._readInt()
        q.questMinionsCompleted = self._readInt()
        q.questItemCount = self._readInt()
        q.questItemsCompleted = self._readInt()
        q.goldReward = self._readInt()
        q.experienceReward = self._readInt()
        q.fameReward = self._readInt()

        q.questName = self._passThisString(read = True)
        q.questMonsterName = self._passThisString(read = True)
        q.questMonsterBaseName = self._passThisString(read = True)
        q.questMinionMonsterBaseName = self._passThisString(read = True)
        q.giverName = self._passThisString(read = True)
        q.questDescription = self._passThisString(read = True)
        q.questMiniDescription = self._passThisString(read = True)
        q.completionDescription = self._passThisString(read = True)
        q.incompleteDescription = self._passThisString(read = True)

        q.questItem = bool(self._readInt(1))
        q.theQuestItem = self._parseItem() if q.questItem else None
        q.itemReward = bool(self._readInt(1))
        q.theItemReward = self._parseItem() if q.itemReward else None

        if self.wg in {"UR", "TS"}:
            q.urts_realm, q.urts_realmGarbage = self._readInt(), self._read(6) #both default to b'' in q.__init__

        if self.wg == "TS":
            q.ts_ending = self._passThisString(read = True, full = True) + self._read(7) #defaults to b'' in q.__init__

        return q
    
    def _parseHistory(self) -> History:
        his = History()
        if self.wg in {"UR", "TS"}:
            his.urts_firstFour = self._read(4) #defaults to b'' in his.__init__
        his.level = self._readInt()
        his.width, his.height = self._readInt(), self._readInt()
        his.idk = self._read(4) #lstpopulationtime in OG? null in URTS?
        his.vis = self._read(his.width * his.height)
        his.characters = [self._parseCharacter() for _ in range(self._readInt())]
        his.items = [self._parseItem() for _ in range(self._readInt())]
        if self.wg in {"UR", "TS"}:
            his.urts_ending = self._read(11 if self.wg == "TS" else 8) #defaults to b'' in his.__init__

        return his


    #------------------------------------------------------------------------------------------------------------#
    # Methods for low-level bytes navigation and reading.

    def _move(self, by: int, rel = True) -> int:
        if rel:
            self._p += by
        else:
            self._p = by
        return self._p

    def _read(self, size: int, overriden_32_0 = True) -> bytes:
        """Both self._32_0 and overriden_32_0 have to be True to do 32 <-> 0."""
        toRet = self._file[self._p:self._p + size]
        if self._32_0 and overriden_32_0 and False:
            toRet = toRet.replace(b' ', b'\x00')
        self._p += size
        return toRet

    def _passThisString(self, size: int = 2, read: bool = False, full = False) -> bytes | None:
        """Assumes pos is at the first byte of the string size.
        Ret: BYTES not string."""
        sizeBytes = self._read(size)
        size = int.from_bytes(sizeBytes, "little")
        if read:
            return (sizeBytes if full else b'') + self._read(size, overriden_32_0 = False)         
        self._move(size)

    def _readInt(self, size = 4, signed=False) -> int:
        return int.from_bytes(self._read(size), "little", signed=signed)

    def _readFloat(self, size = 4) -> float:
        return struct.unpack('f', self._read(size))[0]


    #------------------------------------------------------------------------------------------------------------#
    # Public and private methods for writing.

    def getWrite(self, indent) -> (bytearray | None, str | None):
        yield self._everythingBefore(), f"{I*indent} Wrote everythingBefore."

        for writeThis, printThis in self.player.getWrite(indent+1, self.wg):
            yield writeThis, printThis

        yield len(self.pets).to_bytes(4, "little"), None
        for pet in self.pets:
            for writeThis, printThis in pet.getWrite(indent+1, self.wg):
                yield writeThis, printThis

        yield len(self.histories).to_bytes(4, "little"), None
        for his in self.histories:
            for writeThis, printThis in his.getWrite(indent+1, self.wg):
                yield writeThis, printThis

        yield self._everythingAfter(), f"{I*indent} Wrote everythingAfter."

    def _everythingBefore(self) -> bytes:
        return self._file[:self._garbageUpTo]

    def _everythingAfter(self) -> bytes:
        return self._file[self._garbageResume:]


    #------------------------------------------------------------------------------------------------------------#
    # ts_nonconforming

    def ts_nonconforming(self, baseName: bytes) -> bool:
        """Handles elites, so pass the full baseName.
        If even after handling elites not found, just returns False"""
        name = baseName.decode('utf-8').upper()
        if name not in self.itemCorpus:
            name = prefixRemoved(name, c.RANKS_WITH_POSTSPACE)
        if name not in self.itemCorpus: return False
        return self.itemCorpus[name].type in c.TS_NONCONFOM


#------------------------------------------------------------------------------------------------------------#
# makeItemCorpus() and makeCharCorpus() and getSpellSpheres() called in ui.getInitialInfo().

#assumes that file has good formatting
def makeItemCorpus(gameDirStr: str, itemExts: set) -> dict[str:CorpusItem]:
    """Does not include elite/legendary versions; if 0 < char.maxDepth < 12 then no elite/legendary.
    All strings are dealt with in all caps."""
    itemCorpus = dict()

    chunkToSkip = None
    for ext in itemExts:
        with open(gameDirStr + ext) as rObj:
            for line in rObj:
                if line.strip() == "[ITEM]":
                    item = CorpusItem()
                    while (line := next(rObj).strip()) != "[/ITEM]":
                        if chunkToSkip:
                            if line.startswith(f"[/{chunkToSkip}]"):
                                chunkToSkip = None
                        elif line.startswith('['):
                            chunkToSkip = line[1:line.find(']')]
                        elif line.startswith("<NAME>:") and item.name is None: #star cowl then bee cowl in one, but the name is star cowl bruh TODO aplpies everywhere
                            item.name = line[7:].upper()
                        elif line.startswith("<TYPE>:"):
                            item.type = line[7:].upper()
                        elif line.startswith("<SPEED>:"):
                            item.attackSpeedStr = line[8:].upper()
                        elif line.startswith("<MAXIMUM_DEPTH>:"):
                            item.maxDepth = int(line[16:]) #not elite if < 12
                        elif line.startswith("<DAMAGE>:"):
                            item.dmgRange = [int(n) for n in line[9:].split(':')]
                    itemCorpus[repeatedDictKey(itemCorpus, item.name)] = item
        
    return itemCorpus


#assumes that file has good formatting
def makeCharCorpus(gameDirStr: str, monsterExts: set, spellSpheres: dict) -> dict[str:CorpusCharacter]:
    """Does not include elite/legendary versions; if 0 < char.maxDepth < 15 then no elite/legendary.
    You have to tweak to level elsewhere; that is not done here.
    All name keys are in all caps."""
    charCorpus = dict()
    DMG_TYPES_STR_INT = c.DMG_TYPES_STR_INT("TS")
    for ext in monsterExts:
        with open(gameDirStr + ext) as rObj:
            for line in rObj:
                line = line.strip()
                if line.strip() == "[MONSTER]":
                    char = CorpusCharacter()
                    blockToSkip = ''
                    while line != "[/MONSTER]":
                        line = next(rObj).strip()
                        if not blockToSkip and line.startswith('['):
                            blockToSkip = line[1:-1]
                        elif blockToSkip and line == f"[/{blockToSkip}]":
                            blockToSkip = ''
                        elif blockToSkip:
                            pass
                        elif line.startswith("<NAME>:"):
                            char.name = line[7:]
                        elif line.startswith("<SCALE>:"):
                            s = line.split(':')
                            char.scaleRange = (float(s[1]), float(s[2]))
                        elif line.startswith("<BRAVERY>:"):
                            char.bravery = float(line[10:])
                        elif line.startswith("<HP>:"):
                            s = line.split(':')
                            char.min_max_hp = (int(s[1]), int(s[2]))
                        elif line.startswith("<NATURAL_ARMOR>:"):
                            char.natArmor = int(line[16:])
                        elif line.startswith("<TOHIT>:"):
                            char.attack = int(line[8:])
                        elif line.startswith("<STRENGTH>:"):
                            char.str = int(line[11:])
                        elif line.startswith("<DEXTERITY>:"):
                            char.dex = int(line[12:])
                        elif line.startswith("<VITALITY>:"):
                            char.vit = int(line[11:])
                        elif line.startswith("<MAGIC>:"):
                            char.mag = int(line[8:])
                        elif line.startswith("<MAXIMUM_DEPTH>:"):
                            char.maxDepth = int(line[16:])
                        elif line.startswith("<WALKING_SPEED>:"):
                            char.walkSpeed = float(line[16:])
                        elif line.startswith("<RUNNING_SPEED>:"):
                            char.runSpeed = float(line[16:])
                        elif line.startswith("<SKILL>:"):
                            s = line.split(':')
                            char.skills[c.SKILLS_GAMESTR_INT[s[1]]] = int(s[2])
                        elif line.startswith("<SPELL>:"):
                            if line[8:].upper() in spellSpheres:
                                char.spells[spellSpheres[line[8:].upper()]].append(line[8:].upper())
                        elif line.startswith("<DAMAGE_RESISTANCE>:"):
                            s = line.split(':')
                            if s[1] in DMG_TYPES_STR_INT: #doesnt hurt to include HEROIC
                                char.resists[DMG_TYPES_STR_INT[s[1]]] = int(s[2])
                        elif line.startswith("<FAMILY>:"):
                            char.isUndead = line[9:].upper() == "UNDEAD"
                        elif line.startswith("<BASE_LEVEL>:"):
                            char.baseLevel = int(line[13:])
                    charCorpus[repeatedDictKey(charCorpus, char.name.upper())] = char

    return charCorpus

#assumes that file has good formatting
def getSpellSpheres(gameDirStr: str, spellExts: set) -> dict[str:str]:
    """Spell names and spheres are in all caps."""
    spellSpheres = dict()
    for ext in spellExts:
        with open(gameDirStr + ext) as rObj:
            enum = enumerate(rObj)
            for i, line in enum:
                if line.startswith("[SPELL]"):
                    name, sphere, skipThisBlock = '', '', ''
                    while not name or not sphere:
                        i, line = next(enum)
                        line=line.strip()
                        if skipThisBlock:
                            if line == f"[/{skipThisBlock}]":
                                skipThisBlock = ''
                        elif line.startswith('['):
                            skipThisBlock = line[1:line.find(']')]
                        elif line.startswith("<NAME>:"):
                            name = line[7:]
                        elif line.startswith("<SPHERE>:"):
                            sphere = line[9:]
                    spellSpheres[repeatedDictKey(spellSpheres, name.upper())] = sphere.upper()

    return spellSpheres