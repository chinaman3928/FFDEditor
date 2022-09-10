import navigator
import ui
from random import random

#NEW TODO mind blown, cant you do dmgs for everyone not just player?

#NEW TODO this assumes unmodded, not guaranteed to work for modded
#bruh
#WEBDEV TODO for damagewhatif: master values    

#NEW TODO scentific notation to not mess up formatting

#NEW TODO damage: if you override skill/crit then that bypasses race bonus and enchants, if you add str/dex that includes race bonus ... 
#   these are given just as examples, but everywhere else as applicable
#   think this can be solved by making separate STRSTAT and DEXSTAT and [SKILL]SKILL and CRITSKILL

#TODO FUTURE fast retire

#TODO FUTURE nothing stopping general overflow huh...

#TODO FUTURE include bonuses from skills too (like crit)

#SCIENCE resists seems to not work on 1st pet
# but enchants (like from items spells) add on to the in game displayed value near health bar
# and then specifically for player, changing undead just falls back to 100 ... but thunder dragon changing magic 90 doesnt revert?

#TODO what even is this?
#TODO 32<->0 steam_gog writing back

#TODO probs wont work for modded, say realms? but can test and ask

#TODO FUTURE character enchants

#TODO FUTURE for OGUR, [healing] charms are coded in enchants["ACTIVE"]

def _printCustomError(e: Exception, p1: str, changed: bool):
    """One input(), and program is expected to do no more work after."""
    A = '>' * 119
    p2 = f"{'The FFD MAY BE CHANGED (SEE ABOVE)' if changed else 'THE FFD IS UNCHANGED'}. The program will end on enter."
    input(f"\n{A}\n>>>{p1}\n{ui.I}[{type(e)}] {e}\n>>>{p2}\n{A}")


def _execWrite(wg: str, pathStr: str, nav: navigator.Navigator) -> None:
    confirm = ''.join(c.upper() if random() < 0.5 else c for c in "confirm")
    if input(f"\nEnter exactly {confirm} to write edits: ") == confirm:
        with open(pathStr, 'wb') as wObj:
            for writeThis, printThis in nav.getWrite(1):
                if writeThis is not None: wObj.write(writeThis)
                if printThis is not None: print(printThis)
        input("\nALL CHANGES HAVE BEEN MADE! HIT ENTER TO CLOSE.")
    else:
        input("\nNO CHANGES HAVE BEEN MADE. HIT ENTER TO CLOSE.")


def main() -> None:
    wg, steam_gog, pathStr, file, itemCorpus, charCorpus, spellSpheres = ui.getInitialInfo()

    try:
        nav = navigator.Navigator(wg, steam_gog, file, itemCorpus, charCorpus, spellSpheres)
    except navigator.BadAssumptionError as e:
        _printCustomError(e, "Bad assumption about FFD structure by me (please let me know!):", False)
    else:
        ui.handleMainInterface(nav)
        try:
            _execWrite(wg, pathStr, nav)
        except OSError as e:
            _printCustomError(e, f"Error while attempting to write to {pathStr}:", True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        _printCustomError(e, "Miscellaneous, unaccounted for error (please let me know!):", True)