import struct
import c
from u import full, btos

class Enchant:
    
    def __init__(self):
        """Depends on Navigator._parseEnchant() OR makeNew() for complete instantiation."""
        self.ts_firstFour = b''
        #self.name
        #self.message
        #self.exclusive
        #self.type
        #self.damageType
        #self.positive
        #self.activation
        #self.chanceOfSuccess
        #self.chanceOfSuccessBonus
        #self.chanceOfSuccessBonusPercent
        #self.duration
        #self.durationBonus
        #self.durationBonusPercent
        #self.value
        #self.valueBonus
        #self.valueBonusPercent
        #self.value2
        #self.value2Bonus
        #self.value2BonusPercent
        #self.value3
        #self.value3Bonus
        #self.value3BonusPercent
        #self.priceMultiplier
        self.ts_beforeTypeStr = b''
        self.ts_typeStr = None #to avoid clashes if it happens to be b''

    def __repr__(self) -> str:
        return f"<(OGUR type) {c.ENCHANTS_INT_STR[self.type]} ; {(self.value, self.value2, self.value3)} ; {self.positive}>"

    def setVal(self, new: int, positive: bool) -> None:
        if self.positive != positive:
            self.positive = positive
        self.value = new

    def s(self, wg: str) -> str:
        return c.ENCHANTS_INT_STR[self.type] if wg in {"OG", "UR"} else c.ENCHANTS_GAMESTR_STR[btos(self.ts_typeStr)]

    def lu(self, wg: str, forceOGUR = False) -> int|str:
        return self.type if wg in {'OG', 'UR'} or forceOGUR else self.ts_typeStr.decode('utf-8')

    def getWrite(self, indent) -> (bytearray | None, str | None):
        writeThis = bytearray()

        writeThis += self.ts_firstFour

        writeThis += full(self.name)
        writeThis += full(self.message)

        writeThis += bytes([self.exclusive])
        writeThis += self.type.to_bytes(4, "little")
        writeThis += self.damageType.to_bytes(4, "little")
        writeThis += bytes([self.positive])

        for elem in (self.activation,
                     self.chanceOfSuccess,
                     self.chanceOfSuccessBonus,
                     self.chanceOfSuccessBonusPercent,
                     self.duration,
                     self.durationBonus,
                     self.durationBonusPercent):
            writeThis += elem.to_bytes(4, "little")

        for elem in (self.value,
                     self.valueBonus,
                     self.valueBonusPercent,
                     self.value2,
                     self.value2Bonus,
                     self.value2BonusPercent,
                     self.value3,
                     self.value3Bonus,
                     self.value3BonusPercent,
                     self.priceMultiplier):
            writeThis += struct.pack('f', elem)

        writeThis += self.ts_beforeTypeStr

        if self.ts_typeStr is not None:
            writeThis += full(self.ts_typeStr)

        yield writeThis, None


def makeNew(lookup: int|str, val: int, positive: bool) -> Enchant:
    isTS = type(lookup) is str
    ench = Enchant()

    ench.ts_firstFour                = b'\xff\xff\x01\x00'if isTS else b''
    ench.name                        = b''
    ench.message                     = b''
    ench.exclusive                   = False
    ench.type                        = lookup if type(lookup) is int else 0
    ench.damageType                  = 3
    ench.positive                    = positive
    ench.activation                  = 0
    ench.chanceOfSuccess             = 100
    ench.chanceOfSuccessBonus        = 0
    ench.chanceOfSuccessBonusPercent = 0
    ench.duration                    = 4294966296
    ench.durationBonus               = 0
    ench.durationBonusPercent        = 0
    ench.value                       = val
    ench.valueBonus                  = 0
    ench.valueBonusPercent           = 0
    ench.value2                      = 0
    ench.value2Bonus                 = 0
    ench.value2BonusPercent          = 0
    ench.value3                      = 0
    ench.value3Bonus                 = 0
    ench.value3BonusPercent          = 0
    ench.priceMultiplier             = 0
    ench.ts_beforeTypeStr            = bytes(2) if isTS else b''
    ench.ts_typeStr                  = lookup.encode('utf-8') if isTS else None #to avoid clashes if it happens to be b''

    return ench