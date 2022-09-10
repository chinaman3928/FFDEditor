from c import URTS_REALMS_HISTORY_INT_STR

I = '    ' #four spaces


class History:
    def __init__(self):
        self.urts_firstFour = b''
        #self.level
        #self.width
        #self.height
        #self.idk
        #self.vis
        #self.characters
        #self.items
        self.urts_ending = b''

    def __repr__(self) -> str:
        return f"<{self.level}>"

    def urts_realmInt(self, wg) -> int | None:
        """Returns None if OG."""
        if wg == "OG":
            return None
        return int.from_bytes(self.urts_ending[:4], "little") if wg == "UR" else self.urts_ending[-1]


    def getWrite(self, indent, wg) -> (bytes | None, str | None):
        printAs = f"(imported Grove?) {self.level}" if self.urts_realmInt(wg) == 0 \
            else f"{URTS_REALMS_HISTORY_INT_STR[self.urts_realmInt(wg)]} {self.level}"     #guard against og->ur import realm 0

        yield None, f"{I*indent}Begin write: {printAs} history." 

        writeThis = bytearray()
        writeThis += self.urts_firstFour
        writeThis += self.level.to_bytes(4, "little")
        writeThis += self.width.to_bytes(4, "little")
        writeThis += self.height.to_bytes(4, "little")
        writeThis += self.idk
        writeThis += self.vis
        yield writeThis, None

        yield len(self.characters).to_bytes(4, "little"), None
        for char in self.characters:
            for writeThis, printThis in char.getWrite(indent+1, wg):
                yield writeThis, printThis

        yield len(self.items).to_bytes(4, "little"), None
        for it in self.items:
            for writeThis, printThis in it.getWrite(indent+1, wg):
                yield writeThis, printThis

        yield self.urts_ending, f"{I*indent}Finish write: {printAs} history." 