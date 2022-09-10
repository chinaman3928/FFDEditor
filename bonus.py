class Bonus:

    def __init__(self, type, val):
        """Depends on Navigator._parseBonus() for complete instantiation."""
        self.type, self.val = type, val

    
    def __repr__(self) -> str:
        return f"<{self.type} {self.val}>"


    def getWrite(self, indent) -> (bytes | None, str | None):
        writeThis = self.type.to_bytes(4, "little") + self.val.to_bytes(4, "little")
        yield writeThis, None