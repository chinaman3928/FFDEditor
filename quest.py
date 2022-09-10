from u import btos, full
from c import URTS_REALMS_QUEST_INT_STR


I = '    ' #four spaces


class Quest:
    def __init__(self):
        """Depends on Navigator._parseQuest() for complete instantiation."""
        self.urts_firstFour = b''
        #self.level
        #self.questType
        #self.spawned
        #self.completed
        #self.completionNotified
        #self.questMonsterCount
        #self.questMonstersCompleted
        #self.questMinionCount
        #self.questMinionsCompleted
        #self.questItemCount
        #self.questItemsCompleted
        #self.goldReward
        #self.experienceReward
        #self.fameReward
        #self.questName
        #self.questMonsterName
        #self.questMonsterBaseName
        #self.questMinionMonsterBaseName
        #self.giverName
        #self.questDescription
        #self.questMiniDescription
        #self.completionDescription
        #self.incompleteDescription
        #self.questItem
        #self.theQuestItem
        #self.itemReward
        #self.theItemReward
        self.urts_realm, self.urts_realmGarbage = b'', b''
        self.ts_ending = b''


    def __repr__(self) -> str:
        return f"<{btos(self.giverName)} {self.level}>"


    def getWrite(self, indent, wg: str) -> (bytearray | None, str | None):
        ending = f"{btos(self.questName)} on {URTS_REALMS_QUEST_INT_STR(wg)[self.urts_realm]} {self.level}"
        yield None, f"{I*indent}Begin write: {ending}."

        writeThis = bytearray()

        writeThis += self.urts_firstFour

        for elem in self.level, self.questType:
            writeThis += elem.to_bytes(4, "little")

        for elem in self.spawned, self.completed, self.completionNotified:
            writeThis += bytes([elem])

        for elem in (self.questMonsterCount, self.questMonstersCompleted, self.questMinionCount, self.questMinionsCompleted,
                     self.questItemCount, self.questItemsCompleted, self.goldReward, self.experienceReward, self.fameReward):
            writeThis += elem.to_bytes(4, "little")

        for elem in (self.questName, self.questMonsterName, self.questMonsterBaseName, self.questMinionMonsterBaseName, self.giverName,
                     self.questDescription, self.questMiniDescription, self.completionDescription, self.incompleteDescription):
            writeThis += full(elem)

        yield writeThis, None

        yield bytes([self.questItem]), None
        if self.questItem:
            for writeThis, printThis in self.theQuestItem.getWrite(indent+1, wg):
                yield writeThis, printThis

        yield bytes([self.itemReward]), None
        if self.itemReward:
            for writeThis, printThis in self.theItemReward.getWrite(indent+1, wg):
                yield writeThis, printThis

        writeThis = bytearray()
        if wg in {"UR", "TS"}:
            writeThis += self.urts_realm.to_bytes(4, "little")
            writeThis += self.urts_realmGarbage

        yield writeThis + self.ts_ending, f"{I*indent}Finish write: {ending}."