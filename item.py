from bonus import Bonus
from enchant import makeNew
import c
from u import formatStr, full, btos


I = '    ' #four spaces


class Item:

    def __init__(self, superItem: "Item" = None):
        """Depends on Navigator._parseItem() for complete instantiation."""
        self.superItem = superItem
        self.urts_firstFour = b''
        #self.baseName
        #self.fullName
        #self.slotIndex
        #self.equipped
        #self.equippedGarbage
        #self.grade
        #self.gradeGarbage
        #self.armorBonus
        #self.sockets
        #self.socketsGarbage
        #self.bonuses
        self.ts_bonusesGarbage = b''
        #self.enchants
        #self.subItems
        self.ur_heroID = b''
        self.ts_subitemsGarbage = b''
        self.ts_ending = b''


    def __repr__(self) -> str:
        return f"<{btos(self.baseName)}>"

    def getWrite(self, indent, wg: str) -> (bytearray | None, str | None):
        writeThis = bytearray()
        writeThis += self.urts_firstFour
        writeThis += full(self.baseName)
        writeThis += full(self.fullName)
        writeThis += self.slotIndex.to_bytes(4, "little")
        writeThis += bytes([self.equipped])
        writeThis += self.equippedGarbage
        writeThis += self.grade.to_bytes(4, "little")
        writeThis += self.gradeGarbage
        writeThis += self.armorBonus.to_bytes(4, "little")
        writeThis += self.sockets.to_bytes(4, "little")
        writeThis += self.socketsGarbage

        writeThis += len(self.bonuses).to_bytes(4, "little")
        yield writeThis, None
        for bo in self.bonuses:
            for writeThis, printThis in bo.getWrite(indent+1):
                yield writeThis, printThis

        yield self.ts_bonusesGarbage, None

        if wg in {"OG", "UR"}:
            for lst in self.enchants.values():
                yield len(lst).to_bytes(4, "little"), None
                for ench in lst:
                    for writeThis, printThis in ench.getWrite(indent+1):
                        yield writeThis, printThis

            yield len(self.subItems).to_bytes(4, "little"), None
            for it in self.subItems:
                for writeThis, printThis in it.getWrite(indent+1, wg):
                    yield writeThis, printThis

            yield self.ur_heroID, f"{I*indent}wrote {self.fullBaseName()}"

        else:
            yield len(self.subItems).to_bytes(4, "little"), None
            for it in self.subItems:
                for writeThis, printThis in it.getWrite(indent+1, wg):
                    yield writeThis, printThis

            yield self.ts_subitemsGarbage, None

            yield len(self.enchants["PASSIVE"]).to_bytes(4, "little"), None
            for ench in self.enchants["PASSIVE"]:
                for writeThis, printThis in ench.getWrite(indent+1):
                    yield writeThis, printThis

            yield self.ts_ending, f"{I*indent}wrote {self.fullBaseName()}"

    def fullBaseName(self) -> str:
        """formatted in form {full} [{base}]"""
        return f"{btos(self.fullName)} [{btos(self.baseName)}]"

    def findBonus(self, type: int, val=False) -> int | None:
        """If not val: returns index of self.bonuses if found, else None.
        If val: returns value of the bonus if found, else None."""
        for i, bon in enumerate(self.bonuses):
            if bon.type == type:
                return bon.val if val else i
        return None

    def removeBonus(self, type: int) -> None:
        """Assumes this item has this bonus."""
        i = self.findBonus(type)
        del self.bonuses[i]

    def updateBonus(self, type: int, val: int) -> int:
        """Returns old val or 0."""
        i = self.findBonus(type)
        if i is None:
            self.bonuses.append(Bonus(type, val))
            return 0
        else:
            old = self.bonuses[i].val
            self.bonuses[i].val = val #mutate
            return old

    def findEnchant(self, lookup: int|str, val=False) -> int | None:
        """If not val: returns index of self.enchants if found, else None.
        If val: returns value of the enchant if found, else 0."""
        for i, ench in enumerate(self.enchants["PASSIVE"]):
            if ( ench.type if type(lookup) is int else btos(ench.ts_typeStr) ) == lookup:
                return ench.value if val else i
        return 0 if val else None

    def updateEnchant(self, lookup: int|str, val: int, add = False, keepIfZero = True) -> float:
        """If add == True, adds onto existing value.
        If keepIfZero == False and final val ends up being 0, removes enchant or doesnt add it.
        Returns the old val (or 0.0)."""
        #13 and 42 are +DMGTAKEN and %DMGTAKEN
        positive = (val >= 0) if lookup not in (13, 42) else (val <= 0)
        i = self.findEnchant(lookup)
        val = float(val)
        if i is None:
            self.enchants["PASSIVE"].append(makeNew(lookup, val, positive))
            self.trickleEnchantUp(lookup, val)
            return 0.0
        else:
            old = self.enchants["PASSIVE"][i].value
            if not keepIfZero and (old+val if add else val) == 0:
                self.removeEnchant(lookup)
            else:
                self.enchants["PASSIVE"][i].setVal( (old+val if add else val), positive )
                self.trickleEnchantUp(lookup, val if add else val-old)
            return old

    def removeEnchant(self, lookup: int|str) -> None:
        """Assumes item has this enchant."""
        i = self.findEnchant(lookup)
        self.trickleEnchantUp(lookup, -self.enchants["PASSIVE"][i].value)
        del self.enchants["PASSIVE"][i]

    def trickleEnchantUp(self, lookup: int|str, delta: float) -> None:
        """Applies delta to superItem if applicable, removing if new val is 0."""
        if self.superItem is not None:
            self.superItem.updateEnchant(lookup, delta, add = True, keepIfZero = False)

    def subContribToEnchant(self, type: int) -> float:
        total = 0.0
        for subitem in self.subItems:
            val = subitem.findEnchant(type, val=True)
            if val is not None:
                total += val
        return total

    def removeTheseSubitems(self, indexesToRem: set, wg) -> None:
        """While also appropriately changing self's enchants, removing if 0."""
        if indexesToRem:
            modified : {int} = set()
            for indexToRem in indexesToRem:
                sub = self.subItems[indexToRem]
                for ench in sub.enchants["PASSIVE"]:
                    if self.findEnchant(ench.lu(wg)) is not None: #but shouldnt it always be there?
                        self.updateEnchant(ench.lu(wg), -ench.value, add = True, keepIfZero = False)
            for i in sorted(indexesToRem, reverse=True):
                del self.subItems[i]


#------------------------------------------------------------------------------------------------------------#
# Non-method Item-related utility functions.


def findItemByESlot(slot: int, equippeds: list[Item]) -> Item | None:
    """Left hand and left arm (shield) are collapsed into 2."""
    for it in equippeds:
        if slot == 2:
            if it.slotIndex in (2, 4):
                return it
        elif it.slotIndex == slot:
            return it
    return None


def findItemByBaseName(baseName: int, items: list[Item]) -> (Item, int):
    """Compares to the all-caps version of the name.
    Returns only the first occurrence."""
    foundItem = None
    cnt = 0
    for it in items:
        if btos(it.baseName).upper() == baseName:
            if foundItem is None:
                foundItem = it
            cnt += 1

    return (foundItem, cnt)


def listOff(items: list[Item], parentNum: str = None) -> None:
    """Subitems too. If parentNum is x, then these items will have num x.1 x.2 etc."""
    num = '1' if parentNum is None else "    " + parentNum + '.1'
    for it in items:
        print(f"{num}) {it.fullBaseName()}")
        listOff(it.subItems, num)
        lastDot = num.rfind('.')
        newEndNum = int(num[lastDot + 1:]) + 1
        num = num[:lastDot + 1] + str(newEndNum)


#------------------------------------------------------------------------------------------------------------#