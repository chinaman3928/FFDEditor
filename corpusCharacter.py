from collections import defaultdict as dd


class CorpusCharacter:
    def __init__(self):
        #self.name
        self.scaleRange = (1.0, 1.0)
        self.bravery = 1.0
        self.min_max_hp = (10, 16)
        self.natArmor = 0
        self.attack = 10
        self.str, self.dex, self.vit, self.mag = 10, 10, 10, 10
        self.maxDepth = 0
        self.walkSpeed, self.runSpeed = 15.0, 20.0
        self.isUndead = False
        self.baseLevel = 1
        self.resists: dict[int:int] = dict()
        self.skills: dict[int:int] = dict()
        self.spells: dd[str:list[str]] = dd(list)

    def __repr__(self) -> str:
        return f"<{self.scaleRange, self.bravery, self.min_max_hp, self.natArmor, self.attack, self.str, self.dex, self.vit, self.mag, self.maxDepth, self.resists, self.skills, self.spells}>"

    def __eq__(self, right) -> bool:
        """For testing"""
        return (self.scaleRange,
                self.bravery,
                self.min_max_hp,
                self.natArmor,
                self.attack,
                self.str, self.dex, self.vit, self.mag,
                self.maxDepth,
                self.resists,
                self.skills,
                self.spells) == (right.scaleRange,
                                  right.bravery,
                                  right.min_max_hp,
                                  right.natArmor,
                                  right.attack,
                                  right.str, right.dex, right.vit, right.mag,
                                  right.maxDepth,
                                  right.resists,
                                  right.skills,
                                  right.spells)