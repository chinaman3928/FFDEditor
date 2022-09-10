from re import findall, split as resplit, match
from collections import defaultdict as dd
from pathlib import Path
from math import ceil

import item
import c
import u
from navigator import makeItemCorpus, makeCharCorpus, getSpellSpheres


I = "    " #four spaces

def C(s,f:str = False) -> str:
    """Centers along 119, with option of filling with f."""
    return f"{s:{f}^119}" if f else f"{s:^119}"

def printHeader(head):
    print()
    print('='*119)
    print(C(f"{' < '.join(head)}"))
    print('='*119)

#-------------------------------------------------------------------------------------#
# Getting initial info.

def _getExts(baseExts: set, what: str) -> set:
    """what in {'items', 'monsters', 'spells'}"""
    print(f"\n{I}These are the {what}.dat files I will use:\n{chr(10).join(f'{I*2}...{s}' for s in baseExts)}")
    prompt = rf"{I}Add or remove any (ex. '[+/-] \BLAH\blah\{what}.dat')?: "
    while True:
        choice = input(prompt).strip()
        if u.splits(choice, lambda x: x in {'+', '-'}, lambda x: x):
            (set.add if choice[0] == '+' else set.discard)(baseExts, choice.split()[-1])
            prompt = f"{I}Got it, any more?: "
        elif not choice:
            break
        else:
            prompt = f"{I*2}Invalid input. Try again: "

    return baseExts

def getInitialInfo() -> "wg, steam_gog, pathStr, file, itemCorpus, charCorpus, spellSpheres":
    print(f"{'Reach me on Discord at: chinaman#3928':^119}")
    print(f"{'Join our server at: https://discord.gg/r2bZDk4C3y':^119}")
    print(f"{'Remember to back up your save!':^119}")
    print(f"{'=' * 119}\n")

    wg = input("Which game is this for? OG UR TS: ").strip().upper()
    while wg not in {"OG", "UR", "TS"}:
        wg = input(I + "Invalid input. Try again: ").strip().upper()

    steam_gog = input("\nIs this for Steam or GOG (not Wildtangent)? ('Y' for yes): ").strip().upper() == 'Y'

    prompt = "\nEnter full path of .FFD file: "
    while True:
        pathStr = input(prompt).strip()
        try:
            with open(pathStr, 'rb') as rObj:
                file = rObj.read()
        except OSError:
            prompt = f"{I}Invalid input. Try again: "
        else:
            break

    prompt = "\nEnter full path of the game folder (ex. where ITEMS, MONSTERS, REALMS are): "
    while True:
        gameDirStr = input(prompt).strip()
        if gameDirStr and Path(gameDirStr).is_dir():
            try:
                itemExts = _getExts(c.ITEM_EXTS(wg), "items")
                monsterExts = _getExts(c.MONSTER_EXTS(wg), "monsters")
                spellExts = _getExts(c.SPELL_EXTS(wg), "spells")

                itemCorpus = makeItemCorpus(gameDirStr, itemExts)
                spellSpheres = getSpellSpheres(gameDirStr, spellExts)
                charCorpus = makeCharCorpus(gameDirStr, monsterExts, spellSpheres)
                break

            except OSError:
                prompt = f"\nCan't use these file paths. Try again with the game folder: "

    return wg, steam_gog, pathStr, file, itemCorpus, charCorpus, spellSpheres


#-------------------------------------------------------------------------------------#
# MAIN SELECT.

def handleMainInterface(nav: "Navigator") -> None:
    head = ["MAIN SELECT"]
    print("\nYour player's enchants and resists:")
    _printCumEnchants(nav.player.items, nav.player.charEnchants, nav.player.resists if nav.wg == "OG" else nav.player.urts_resists, nav.wg)

    prompt = "Enter your choice: "
    printChoices = True
    while True:
        if printChoices:
            printHeader(head)

            print(f"{'What do you want to do?':^119}")
            print(f"{'—PLAYER':^119}")
            print(f"{'—PETS':^119}")
            print(f"{'—QUESTS':^119}")
            print(f"{'—HISTORIES':^119}")
            print(f"{'—UNRETIRE':^119}")
            print(f"{'—RESPEC':^119}")
            print(f"{'—DAMAGE':^119}")
            print(f"{'—END':^119}")

        choice = input(prompt).strip().upper()
        if choice == "PLAYER":
            _handleCharacterInterface(nav.player, nav.wg, head)
        elif choice == "PETS":
            _handlePetsInterface(nav.pets, nav.charCorpus, nav.wg, head)
        elif choice == "QUESTS":
            _handleQuestsInterface(nav.player.quests, nav.wg, head)
        elif choice == "HISTORIES":
            _handleHistoriesInterface(nav.histories, nav.player, nav.wg, head)
        elif choice == "UNRETIRE":
            nav.player.lineage = bytes(4)
            print("^ Got it, unretired.")
        elif choice == "RESPEC":
            _handleRespecInterface(nav.player, nav.wg, head)
        elif choice == "DAMAGE":
            _handleDamageInterface(nav.player, nav.itemCorpus, nav.wg, head)
        elif choice == "END":
            return
        else:
            prompt = f"{I}Invalid input. Try again: "
            printChoices = False
            continue
        prompt = "Enter your choice: "
        printChoices = True

#TODO FUTURE repreattedly update? for each character?
def _printCumEnchants(items, playerEnchants, resists, wg: str) -> None:
    d = dd(lambda: [0.0, dict()])

    for key, source in ( ("PASSIVE", "INTRINSIC"), ("USAGE", "SPELL") ):
        for ench in playerEnchants[key]:
            V = d[c.ENCHANTS_INT_STR[ench.type]]
            V[0] += ench.value
            V[1][u.repeatedDictKey(V[1], source)] = ench.value

    for eitem in items["EQUIPPED"]:
        for ench in eitem.enchants["PASSIVE"]:
            V = d[ench.s(wg)]
            V[0] += ench.value
            V[1][u.repeatedDictKey(V[1], u.btos(eitem.baseName))] = ench.value

    for i, value in enumerate(resists):
        d[c.DMG_TYPES_INT_STR(wg)[i]][0] += value
        d[c.DMG_TYPES_INT_STR(wg)[i]][1]["RESIST"] = value

    print()
    for chunk in u.yieldInChunks(sorted(d.items(), key = lambda x: -x[1][0]), 3):
        print('|'.join(f"{f' {V[0]} ({V[1][0]}) ':=^39}" if V is not None else ('='*39) for V in chunk))
        breakdowns = [[] if V is None else sorted(V[1][1].items(), key = lambda x: -x[1]) for V in chunk]
        print(f"{' '*39}|{' '*39}|{' '*39}")
        for row in u.zipAllTheWay(*breakdowns):
            print('|'.join(f"{f' {name_contrib[0]} ({name_contrib[1]}) ':^39}" if name_contrib is not None else (' '*39) for name_contrib in row))
        print(f"{' '*39}|{' '*39}|{' '*39}")


#-------------------------------------------------------------------------------------#
# Character and item interface.

def _handleCharacterInterface(char: "Character", wg: str, HEAD: str) -> None:
    head = HEAD + [u.btos(char.name)]

    printChoices = True
    prompt = "Enter your choice: "
    while True:
        if printChoices:
            printHeader(head)

            print(f"\nOptions for editing {char.levelFullTemplateName()}:")
            print(f"{I}—ITEMS")
            print(f"{I}—NAME")
            print(f"{I}—GOLD [gold >= 0]" if wg == "TS" else f"{I}—GOLD [gold]")
            print(f"{I}—SKILLS")
            print(f"{I}—RESISTS")
            print(f"{I}—[str] [dex] [vit] [mag] (x if unchanged)")
            if char.isPlayer:
                DIFFS = c.DIFFICULTIES_S_INTSTR(wg)
                print(f"{I}—DIFF [difficulty] where {', '.join(f'[{s}]{intstr[1][len(s):]}' for s,intstr in DIFFS.items())}")
            print(f"{I}—'<' back to {head[-2]}")
            print()

        choice = input(prompt).strip().upper()
        if choice == "ITEMS":
            __handleItemInterface(char.items, wg, head)
        elif choice == "NAME":
            __handleName(char, head)
            head = HEAD + [u.btos(char.name)]
        elif choice == "SKILLS":
            __handleSkillsInterface(char.skills, head)
        elif choice == "RESISTS":
            __handleResistsInterface(char, wg, head)
        elif u.splits(choice, lambda x: x == "GOLD", lambda x: x.isdecimal() if wg == "TS" else u.strIsInt(x)):
            old = char.gold
            char.gold = int(choice.split()[1])
            print(f"Got it, gold changed from {old} —> {char.gold}")
        #TODO does this do what you want it to?
        elif u.splits(choice, lasts = (lambda x: x == 'X' or x.isdecimal()), exactly = 4): #stat cant be negative
            split = choice.split()
            str, dex, vit, mag = char.str, char.dex, char.vit, char.mag
            if split[0] != 'X': char.str = int(split[0]) #mutate
            if split[1] != 'X': char.dex = int(split[1]) #mutate
            if split[2] != 'X': char.vit = int(split[2]) #mutate
            if split[3] != 'X': char.mag = int(split[3]) #mutate
            print(f"^ Got it, STR {str} —> {char.str}, DEX {dex} —> {char.dex}, VIT {vit} —> {char.vit}, MAG {mag} —> {char.mag}.")

        elif char.isPlayer and u.splits(choice, lambda x: x == "DIFF", lambda x: x in DIFFS):
            DIFFS_INT_STR = {i:s for i,s in DIFFS.values()}
            old = char.difficulty
            char.difficulty = DIFFS[choice.split()[1]][0] #mutate
            print(f"^ Got it, difficulty from {DIFFS_INT_STR[old]} —> {DIFFS_INT_STR[char.difficulty]}.")
        elif choice == '<':
            return
        else:
            printChoices = False
            prompt = f"{I}Invalid input. Try again: "
            continue
        printChoices = True
        prompt = "Enter your choice: "

def __handleName(C_I: "Character/Item", HEAD: str) -> None:
    isItem = type(C_I) is item.Item
    head = HEAD + ["Name"]
    printHeader(head)

    old = u.btos(C_I.fullName if isItem else C_I.name)
    new = ''
    print(f"\nEnter the new name ('\\n' —> newline, '\\bTEXT\\b' —> bolded TEXT, '\\\\' —> backslash) or '<' to {head[-2]}.")
    prompt = "Enter your choice: "
    while new != "<" and (not new or len(findall(r'(?<!\\)\\b', new)) % 2 == 1):
        new = input(prompt)
        prompt = I + "Invalid name, try again: "

    if new == "<":
        print("^ Ok, item name unchanged.")
        return

    asLst = list(new)
    i = 0
    while i < len(asLst):
        if asLst[i : i + 2] == list('\\n'):
            asLst[i : i + 2] = '\n'
        elif asLst[i : i + 2] == list('\\b'):
            asLst[i : i + 2] = '\b'
        elif asLst[i : i + 2] == list('\\\\'):
            asLst[i : i + 2] = '\\'
        i += 1

    if isItem:
        C_I.fullName = ''.join(asLst).encode("utf-8") #mutate
    else:
        C_I.name = ''.join(asLst).encode("utf-8") #mutate
    print(f"^ Got it, {old} —> {u.btos(C_I.fullName if isItem else C_I.name)}")

def __handleResistsInterface(char, wg, HEAD) -> None:
    resists = char.resists if wg == "OG" else char.urts_resists
    TYPES = c.DMG_TYPES_STR_INT(wg)
    head = HEAD + ["Resists"]

    skipChoices = False
    prompt = "Enter your choice: "
    while True:
        if not skipChoices:
            printHeader(head)

            print('\n' + C(f"{'RESISTS':^22}|{'VALUES':^22}{7*' '}{'RESISTS':^22}|{'VALUES':^22}"))
            print( C(f"{22*'-'}|{22*'-'}{7*' '}{22*'-'}|{22*'-'}") )
            for l, r in u.downColumns(tuple(TYPES.items()), 2):
                (lr, lv) = ('', '') if l is None else (l[0], resists[l[1]])
                (rr, rv) = ('', '') if r is None else (r[0], resists[r[1]])
                print(C(f"{lr:^22}|{lv:^22}{7*' '}{rr:^22}|{rv:^22}"))
            print()
            print(f"Enter as many as you want (ex. '[value] x y z'), or '<' to {head[-2]}.")

        s = input(prompt).strip().upper().split()
        if u.splits(s, lambda x: u.strIsInt(x), lasts = lambda x: x in TYPES): #can go negative, no bounds
            new = int(s[0])
            for typeStr in s[1:]:
                old = resists[i := TYPES[typeStr]]
                resists[i] = new
                print(f"^ Got it, {typeStr} {old} —> {resists[i]}.")
        elif s == ["<"]:
            return
        else:
            prompt = I + "Invalid input, try again: "
            skipChoices = True
            continue
        skipChoices = False
        prompt = "Got it, any more?: "


def __handleItemInterface(items: dict["EQUIPPED", "INVENTORY"], wg, HEAD: str) -> None:
    head = HEAD + ["Item Select"]
    while True:
        theItem = ___getItemChoice(items, wg, head)
        if theItem is None:
            return

        skipPrintActionChoices = False
        prompt = "Enter your choice: "
        while True:
            newhead = head + [u.btos(theItem.baseName)]
            if not skipPrintActionChoices:
                header = ' < '.join(newhead)
                print(f"\n{f' {header} ':=^119}")
                ___printActionChoices(theItem, newhead)

            choice = input(prompt).strip().upper()
            if choice == "<":
                break
            elif choice == "NAME":
                __handleName(theItem, newhead)
            elif choice == "ENCHANTS":
                ___handleEnchant(theItem, wg, newhead)
            elif choice == "BONUS":
                ___handleBonus(theItem, wg, newhead)
            elif choice == "SOCKETS":
                ___handleSockets(theItem, wg, newhead)
            elif u.splits(choice, lambda x: x == "GRADE", lambda x: x in set("NSEF")):
                ___handleGrade(theItem, choice.split()[1], newhead)
            else:
                skipPrintActionChoices = True
                prompt = I + "Invalid input, try again: "
                continue
            skipPrintActionChoices = False
            prompt = "Enter your choice: "

def ___getItemChoice(items: dict, wg: str, HEAD: str) -> item.Item | None:
    """Ret: None if '<'."""

    skipPrintItemChoices = False
    prompt = "Enter your choice: "
    while True:
        if not skipPrintItemChoices:
            printHeader(HEAD)
            ____printItemChoices(HEAD, wg)
        choice = input(prompt).strip().upper()

        if choice in (c.OGUR_SHORTCUT_SLOT if wg in {"OG", "UR"} else c.TS_SHORTCUT_SLOT):
            theItem = ____handleEShortcut(choice, items, wg, HEAD)
        elif choice == "ALL":
            theItem = ____handleAll(items, HEAD)
        elif choice == "<":
            return None
        else: #then assume entering base name
            theItem = ____handleBaseName(items, choice, HEAD)
            if theItem is None: #then invalid input and ask to retry
                skipPrintItemChoices = True
                prompt = f"{I}Invalid input, try again: "
                continue

        if theItem is not None and ____confirmItemChoice(theItem):
            return theItem
        
        skipPrintItemChoices = False
        prompt = "Enter your choice: "
def ____printItemChoices(head: list, wg: str) -> None:
    print("\nWhat item do you want to edit? Options:")
    scs = ', '.join(sc for sc in (c.OGUR_SHORTCUT_SLOT if wg in {"OG", "UR"} else c.TS_SHORTCUT_SLOT))
    print(I + f"—Shortcuts for equipped items: {{{scs}}}")
    print(I + "—Base unenchanted name of your item — grade isn't included (ex. Legendary Cheese Sword)")
    print(I + "—ALL to bring up a list of all your items and then choose from the list")
    print(I + f"—'<' to {head[-2]}\n")
def ____handleEShortcut(choice: str, items: dict, wg: str, HEAD: str) -> item.Item | None:
    slot = (c.OGUR_SHORTCUT_SLOT if wg in {"OG", "UR"} else c.TS_SHORTCUT_SLOT)[choice]
    theItem = item.findItemByESlot(slot, items["EQUIPPED"])
    if theItem is None:
        print("\nYou don't have an item in that slot!")
    return theItem
def ____handleAll(items: dict, HEAD: str) -> item.Item | None:
    head = HEAD + ["All"]
    printHeader(head)

    print("\n[E]QUIPPED")
    item.listOff(items["EQUIPPED"])

    print("\n[I]NVENTORY")
    item.listOff(items["INVENTORY"])

    prompt = f"\nPick your item (ex. 'E 3.2.1' or 'I 17') or '<' to {head[-2]}: "
    while True:
        the_input = input(prompt).strip().upper()
        if the_input == "<":
            print("^ Ok, back to Item Select.")
            return

        try:
            spec, nums = the_input.split()
            assert spec in ('E', 'I')

            nums = [int(num) for num in nums.split('.')]
            assert spec in ('E', 'I') and all([num > 0 for num in nums])
            theItem = items["EQUIPPED" if spec == 'E' else "INVENTORY"][nums[0] - 1]
            for num in nums[1:]:
                theItem = theItem.subItems[num - 1]
            return theItem
        except (AssertionError, ValueError, IndexError):
            prompt = I + "Invalid input, try again: "
def ____handleBaseName(items: dict, choice: str, HEAD: str) -> item.Item | None:
    theItem, cnt = item.findItemByBaseName(choice, items["EQUIPPED"] + items["INVENTORY"])
    if theItem is None:
        return None
    if cnt > 1:
        print(f"\nYou have {cnt} of these, but I'll just go with one of them.")
    return theItem
def ____confirmItemChoice(theItem: item.Item) -> bool:
    print(f"\nLooks like you chose {theItem.fullBaseName()}.")
    if input("Continue with this? ('Y' for yes): ").strip().upper() == 'Y':
        return True
    print("^ Ok, back to Item Select.")
    return False

def ___printActionChoices(theItem, head: list) -> None:
    print(f"\nChoices for editing {theItem.fullBaseName()}: ")
    print(I + "—NAME (bold purpletext + newlines)")
    print(I + "—ENCHANTS to edit enchants")
    print(I + "—BONUS to edit damage bonuses")
    print(I + "—GRADE [grade] where [N]ormal, [S]uperior, [E]xceptional, [F]lawless")
    print(I + "—SOCKETS to edit sockets and subitems")
    print(I + f"—'<' to {head[-2]}\n")
    
def ___handleEnchant(theItem: item.Item, wg, HEAD: str) -> None:
    """Prompts until useable input, so always returns None."""
    head = HEAD + ["Enchants"]

    prompt = "Enter your choice: "
    skipChoices = False
    while True:
        if not skipChoices:
            printHeader(head)
            ____printEnchantTable()
            if theItem.enchants["PASSIVE"]:
                print("\nThis item's enchants, with socketed contributions in parentheses:\n")
                for chunk in u.yieldInChunks(sorted(theItem.enchants["PASSIVE"], key = lambda e: -e.value), 3):
                    lookup = lambda e: e.type if wg in {'OG', 'UR'} else u.btos(e.ts_typeStr)
                    print('|'.join( f"{'-':^39}" if e is None else f"{f'{e.s(wg)} {e.value} ({theItem.subContribToEnchant(lookup(e))})':^39}" for e in chunk ))
            else:
                print("\nThis item has no enchants.")
            print(f"\nEnter as many as you want (ex. '[value / '-' to remove] x y z'), or '<' to {head[-2]}.")

        s = input(prompt).strip().upper().split()
        if u.splits(s, lambda x: x == '-', lasts = lambda x: x in c.ENCHANTS_STR_INT and theItem.findEnchant(c.ENCHANTS_STR_LOOKUP(x, wg)) is not None):
            for enchStr in set(s[1:]):
                lookup = c.ENCHANTS_STR_LOOKUP(enchStr, wg)
                subContrib = theItem.subContribToEnchant(lookup)
                if subContrib == 0:
                    theItem.removeEnchant(lookup)
                else:
                    theItem.updateEnchant(lookup, subContrib)
                print(f"^ Got it, {enchStr} removed." if subContrib == 0 else \
                    f"^ Got it, {enchStr} removed but ({theItem.findEnchant(lookup, val=True)}) still from sockets.")
        elif u.splits(s, lambda x: u.strIsInt(x), lasts = lambda x: x in c.ENCHANTS_STR_INT):
            for enchStr in s[1:]:
                lookup = c.ENCHANTS_STR_LOOKUPy(enchStr, wg)
                subContrib = theItem.subContribToEnchant(lookup)
                old = theItem.updateEnchant(lookup, int(s[0]) + subContrib)
                print(f"^ Got it, {enchStr} {old} ({subContrib}) —> {theItem.findEnchant(lookup, val=True)} ({subContrib})")

        elif s == ["<"]:
            return
        else:
            prompt = I + "Invalid input, try again: "
            skipChoices = True
            continue
        skipChoices = False
        prompt = "Got it, any more?: "
def ____printEnchantTable() -> None:
    print()
    indivs = c.ENCHANT_TABLE[0].split('/')
    thisRow = f"{indivs[0]:=^16}"
    for indiv in indivs[1:]:
        thisRow += f"|{indiv:=^16}"

    print(thisRow)

    for row in c.ENCHANT_TABLE[1:]:
        indivs = row.split('/')
        thisRow = f"{indivs[0]:^16}"
        for indiv in indivs[1:]:
            thisRow += f"|{indiv:^16}"
        print(thisRow)

def ___handleBonus(theItem: item.Item, wg, HEAD: str) -> None:
    BONUSES = c.DMG_TYPES_STR_INT(wg)
    head = HEAD + ["Bonuses"]

    skipChoices = False
    prompt = "Enter your choice: "
    while True:
        if not skipChoices:
            printHeader(head)

            print('\n' + C(f"{'BONUSES':^22}|{'VALUES':^22}{7*' '}{'BONUSES':^22}|{'VALUES':^22}"))
            print( C(f"{22*'-'}|{22*'-'}{7*' '}{22*'-'}|{22*'-'}") )
            for l, r in u.downColumns(tuple(BONUSES.items()), 2):
                (lb, lv) = ('', '') if l is None else (l[0], str(theItem.findBonus(l[1], val=True)))
                (rb, rv) = ('', '') if r is None else (r[0], str(theItem.findBonus(r[1], val=True)))
                print(C(f"{lb:^22}|{lv:^22}{7*' '}{rb:^22}|{rv:^22}"))
            print()
            print(f"Enter as many as you want (ex. '[value >= 0 / '-' to remove] x y z'), or '<' to {head[-2]}.")

        s = input(prompt).strip().upper().split()
        if u.splits(s, lambda x: x == '-', lasts = lambda x: x in BONUSES and theItem.findBonus(BONUSES[x]) is not None):
            for bonStr in s[1:]:
                theItem.removeBonus(BONUSES[bonStr])
                print(f"^ Got it, {bonStr} removed.")
        elif u.splits(s, lambda x: x.isdecimal(), lasts = lambda x: x in BONUSES):
            new = int(s[0])
            for bonStr in s[1:]:
                old = theItem.updateBonus(BONUSES[bonStr], new)
                print(f"^ Got it, {bonStr} {old} —> {theItem.findBonus(BONUSES[bonStr], val=True)}.")
        elif s == ["<"]:
            return
        else:
            prompt = I + "Invalid input, try again: "
            skipChoices = True
            continue
        skipChoices = False
        prompt = "Got it, any more?: "

def ___handleSockets(theItem: item.Item, wg, HEAD: str) -> None:
    head = HEAD + ["Sockets"]

    skipChoices = False
    prompt = "Enter your choice: "
    while True:
        if not skipChoices:
            printHeader(head)

            old = theItem.sockets
            print()
            item.listOff([theItem])
            print(f"(This item has {old} socket.)\n" if old == 1 else f"(This item has {old} sockets.)\n")

            print(f"Change number of sockets from 0-20 (ex. 'NUM 10') or remove subitems (ex. '- 1 2 3') or '<' to {head[-2]}.")

        s = input(prompt).strip().upper().split()
        if u.splits(s, lambda x: x == "NUM", lambda x: u.strRange(x, 21)):
            new = int(s[1])
            if new < len(theItem.subItems):
                numRem = len(theItem.subItems) - new
                print(f"\n{I}Pick <= {numRem} subitems to remove (ex. '1 2 3'), or '<' to back out.")
                prompt = I + "Enter your choice: "
                breakOut = False
                while True:
                    indexesToRem = set(input(prompt).strip().split())
                    if len(indexesToRem) <= numRem and all(u.strRange(i, 1, len(theItem.subItems) + 1) for i in indexesToRem):
                        indexesToRem = {int(i) - 1 for i in indexesToRem}
                        break
                    elif indexesToRem == {'<'}:
                        print("^ Ok, no changes made.")
                        breakOut = True
                        break
                    prompt = 2*I + "Invalid input, try again: "
                if breakOut:
                    prompt = "Enter your choice: "
                    skipChoices = False
                    continue

                i = len(theItem.subItems) - 1
                while len(indexesToRem) < numRem:
                    if i not in indexesToRem:
                        indexesToRem.add(i)
                    i -= 1

                print(f"\n{I}These {numRem} subitems will be removed:")
                for i in sorted(indexesToRem):
                    print(2*I + f"{i+1}) {theItem.subItems[i].fullBaseName()}")

                if input(I + "Continue? ('Y' for yes): ").strip().upper() == 'Y':
                    theItem.removeTheseSubitems(indexesToRem, wg)
                else:
                    print("^ Ok, no changes made.")
                    prompt = "Enter your choice: "
                    continue

            theItem.sockets = new #mutate
            print(f"^ Got it, sockets {old} —> {(old := theItem.sockets)}.")

        elif u.splits(s, lambda x: x == '-', lasts = lambda x: u.strRange(x, 1, len(theItem.subItems)+1)):
            indexesToRem = {int(i) - 1 for i in s[1:]}

            print(f"\nRemoving these {len(indexesToRem)} subitems:")
            for i in sorted(indexesToRem):
                print(I + f"{i+1}) {theItem.subItems[i].fullBaseName()}")
            theItem.removeTheseSubitems(indexesToRem, wg)
            print("^ Got it, subitems removed.")
        elif s == ['<']:
            return
        else:
            prompt = I + "Invalid input, try again: "
            skipChoices = True
            continue    
        prompt = "Got it, any more?: "
        skipChoices = False

def ___handleGrade(theItem: item.Item, p2: str, HEAD: str) -> None:
    grades = {'N': 0, 'S': 1, 'E': 2, 'F': 3}
    gradeStrs = {0: 'Normal', 1: 'Superior', 2: 'Exceptional', 3: 'Flawless',
                 'N': 'Normal', 'S': 'Superior', 'E': 'Exceptional', 'F': 'Flawless'}
    gradeAsBytes = {'N': b'', 'S': b"\x08Superior \x08", 'E': b"\x08Exceptional \x08", 'F': b"\x08Flawless \x08"}
                    
    old = theItem.grade
    theItem.grade = grades[p2] #mutate
                    
    encodedName = theItem.fullName

    firstAppear = u.firstToAppear(encodedName, set(gradeAsBytes.values()) - {b''})
    if firstAppear != None:
        theItem.fullName = encodedName.replace(firstAppear, gradeAsBytes[p2]) #mutate
    elif encodedName.find(b"'s \x10") != -1:
        i = encodedName.find(b"'s \x10")
        encodedName[i + 4 : i + 4] = gradeAsBytes[p2]
        theItem.fullName = encodedName #mutate
    else: #add onto the front
        theItem.fullName = gradeAsBytes[p2] + encodedName #mutate

    print(f"^ Got it, grade changed from {gradeStrs[old]} —> {gradeStrs[p2]}.")

def __handleSkillsInterface(skills: list[int], HEAD: str) -> None:
    head = HEAD + ["Skills"]

    prompt = "Enter your choice: "
    skipChoices = False
    while True:
        if not skipChoices:
            printHeader(head)

            print('\n' + C(f"{'SKILLS':^22}|{'POINTS':^22}{7*' '}{'SKILLS':^22}|{'POINTS':^22}"))
            print( C(f"{22*'-'}|{22*'-'}{7*' '}{22*'-'}|{22*'-'}") )
            for l, r in u.downColumns(tuple(c.SKILLS_STR_INT.items()), 2):
                (ls, lp) = ('', '') if l is None else (l[0], skills[l[1]])
                (rs, rp) = ('', '') if r is None else (r[0], skills[r[1]])
                print(C(f"{ls:^22}|{lp:^22}{7*' '}{rs:^22}|{rp:^22}"))

            print()
            print(f"Edit as many as you want (ex. '[value >= 0] x y z') or '<' back to {head[-2]}.")
        s = input(prompt).strip().upper().split()
        if u.splits(s, lambda x: x.isdecimal(), lasts = lambda x: x in c.SKILLS_STR_INT): #cant be negative
            new = int(s[0])
            for skillStr in s[1:]:
                i = c.SKILLS_STR_INT[skillStr]
                old = skills[i]
                skills[i] = new
                print(f"^ Got it, {skillStr} {old} —> {skills[i]}.")
        elif s == ['<']:
            return
        else:
            prompt = f"{I}Invalid input. Try again: "
            skipChoices = True
            continue
        skipChoices = False
        prompt = "Got it, any more?: "


#-------------------------------------------------------------------------------------#
# Pets interface.

def _handlePetsInterface(pets: ["Character"], charCorpus: dict, wg: str, HEAD: str) -> None:
    head = HEAD + ["Pets"]

    skipChoices = False
    while True:
        if not skipChoices:
            printHeader(head)

            print("\nYou have these pets:")
            print('\n'.join( (f"{I}{i}) {pet.levelFullTemplateName()}" for i, pet in enumerate(pets, 1)) ))

            print("\nWhat do you want to do?")
            print(f"{I}—Add pets (ex. 'Elite Floating Mind [level] [1 <= quantity <= 10] [ho;mi;se]')")
            print(f"{I}—Remove pets != 1 (ex. '- 2 3')")
            print(f"{I}—[num] to edit that pet")
            print(f"{I}—'<' back to {head[-2]}\n") 
            prompt = "Enter your choice: "

        choice = input(prompt).strip().upper()
        if len(s := resplit(r'\s+(?=\d)', choice)) == 4 and s[1].isdecimal() and u.strRange(s[2], 1, 11) and \
            u.splits(s[3], lasts = lambda x: x.isdecimal() and int(x)>=0, exactly=3, delim=';'): #these ints cant be negative
            
            if s[0] in charCorpus:
                corpusChar, rank = charCorpus[s[0]], ''
            elif s[0].startswith("ELITE") and s[0][6:] in charCorpus:
                corpusChar, rank = charCorpus[s[0][6:]], "ELITE"
                if 0 < corpusChar.maxDepth < 15:
                    print(f"^ Elite versions of {corpusChar.name} don't exist.\n")
                    skipChoices, prompt = True, f"{I}Invalid input. Try again: "
                    continue
            elif s[0].startswith("LEGENDARY") and s[0][10:] in charCorpus:
                corpusChar, rank = charCorpus[s[0][10:]], "LEGENDARY"
                if 0 < corpusChar.maxDepth < 15:
                    print(f"^ Legendary versions of {corpusChar.name} don't exist.\n")
                    skipChoices, prompt = True, f"{I}Invalid input. Try again: "
                    continue
            else:
                skipChoices, prompt = True, f"{I}Invalid input. Try again: "
                continue

            h, m, se = map(int, s[3].split(';'))
            for _ in range(int(s[2])):
                pets.append( pets[0].newPetHere(corpusChar, rank, int(s[1]), float(h*3600 + m*60 + se), wg) )
            print(f"^ Got it, ({int(s[2])}) {pets[-1].levelFullTemplateName()} added!")

        elif u.strRange(choice, 1, len(pets)+1):
            _handleCharacterInterface(pets[int(choice) - 1], wg, head)
        elif u.splits(choice, lambda x: x == "-", lasts = lambda x: u.strRange(x, 2, len(pets) + 1)):
            print("\nRemoving these pets:")
            for i in (l := sorted(map(int, set(choice.split()[1:])))):
                print(I + f"{i}) {u.btos(pets[i-1].name)} [{u.btos(pets[i-1].templateName)}]")
            for i in reversed(l):
                del pets[i-1]
            print("^ Got it, pets removed.")
        elif choice == "<":
            return
        else:
            prompt = f"{I}Invalid input. Try again: "
            skipChoices = True
            continue
        skipChoices = False


#-------------------------------------------------------------------------------------#
# Quests interface.

#FUTURE TODO add quests
def _handleQuestsInterface(quests: dict["REGULAR", "MASTER"], wg, HEAD: str) -> None:
    head = HEAD + ["Quests"]

    skipChoices = False
    while True:
        if not skipChoices:
            printHeader(head)

            cols, tableIndexToQ = __quest_historyTable(quests, wg)

            print(f"\nEdit a quest with its num, remove (ex. '- 1 2 3'), or '<' back to {head[-2]}.")
            prompt = "Enter your choice: "

        choice = input(prompt).strip().upper()
        s = choice.split()
        if len(s) == 1 and u.strRange(s[0], 1, len(tableIndexToQ) + 1):
            __handleEditQuestInterface(tableIndexToQ[int(s[0])], head)
        elif u.splits(s, lambda x: x == '-', lasts = lambda x: u.strRange(x, 1, len(tableIndexToQ) + 1)):
            rem = sorted(set(map(int, s[1:])))
            masTableIndex = cols["Master"] and cols["Master"][0][0]
            print("\nRemoving these quests:")
            for n in rem:
                if n == masTableIndex:
                    quests["MASTER"] = None
                else:
                    quests["REGULAR"].remove(tableIndexToQ[n])
                print(f"{I}{n}) {u.btos(tableIndexToQ[n].giverName)} {tableIndexToQ[n].level}")
            print("^ Go it, quests removed.")
            
        elif choice == '<':
            return
        else:
            prompt = f"{I}Invalid input. Try again: "
            skipChoices = True
            continue
        skipChoices = False


#FUTURE TODO add more lol
def __handleEditQuestInterface(quest: "QUEST", HEAD: str) -> None:
    head = HEAD + [f"{u.btos(quest.giverName)} {quest.level}"]
    printHeader(head)

    print(f"Enter a new quest level >= 0 or '<' back to {head[-2]}.\n")
    prompt = "Enter your choice: "
    while True:
        choice = input(prompt).strip()
        if choice.isdecimal():
            old = quest.level
            quest.level = int(choice)
            print(f"^ Got it, {old} —> {quest.level}\n")
        elif choice == '<':
            return
        else:
            prompt = f"{I}Invalid input. Try again: "
            continue
        prompt = "Enter your choice: "


#-------------------------------------------------------------------------------------#
# Histories interface.

def __quest_historyTable(Q_H: "quests/histories", wg) -> (dict, dict):
    """No guards."""
    isQ = type(Q_H) is dict
    getRealm = lambda q_h: c.URTS_REALMS_QUEST_INT_STR(wg)[q_h.urts_realm] if isQ else c.URTS_REALMS_HISTORY_INT_STR[q_h.urts_realmInt(wg)]
    cell = lambda i_qh: f"{i_qh[0]}) {u.btos(i_qh[1].giverName[:16])} {i_qh[1].level}" if isQ else f"{i_qh[0]}) {i_qh[1].level}"
    #TODO FUTURE space out cols as large as you need them, rn state hero fatass so arbitrarily cut to 16

    iterable = Q_H["REGULAR"] if isQ else Q_H
    if wg == "OG":
        cols = dict(Grove = enumerate(so := sorted(iterable, key = lambda q_h: q_h.level), 1))
        if isQ: cols["Master"] = []
        tableIndexToQH = dict(enumerate(so, 1))
        if isQ and (q := Q_H["MASTER"]) is not None:
            cols["Master"].append( (len(Q_H["REGULAR"]) + 1, q) )
            tableIndexToQH[len(Q_H["REGULAR"]) + 1] = q
    else:
        cols = dict(Druantia = [], Typhon = [], Master = []) if wg == "UR" else \
            dict(Grove = [], Druantia = [], Typhon = [], Chamber = [], Master = [])
        for q_h in iterable:
            if isQ or not (wg == "UR" and q_h.urts_realmInt(wg) == 0): #guard only against og->ur realm 0 history
                cols[getRealm(q_h)].append([None, q_h])
        if isQ and (q := Q_H["MASTER"]) is not None:
            cols[getRealm(q)].append([None, q])

        i = 1
        tableIndexToQH = dict()
        for col in cols.values():
            col.sort(key = lambda i_qh: i_qh[1].level)
            for i_qh in col:
                i_qh[0] = i
                tableIndexToQH[i] = i_qh[1]
                i += 1
    print()
    print( C('|'.join(f"{realm:^23}" for realm in cols)) )
    print( C('|'.join(23*'-' for _ in range(len(cols)))) ) 
    for row in u.zipAllTheWay(*cols.values()):
        print( C('|'.join(f"{'-':^23}" if i_qh is None else f"{cell(i_qh):^23}" for i_qh in row)) )

    return cols, tableIndexToQH


def _handleHistoriesInterface(histories: list["History"], player: "Character", wg, HEAD: str) -> None:
    head = HEAD + ["Histories"]

    skipChoices = False
    while True:
        if not skipChoices:
            printHeader(head)

            _cols, tableIndexToH = __quest_historyTable(histories, wg)
            currRealm = c.URTS_REALMS_HISTORY_INT_STR[player.urts_realmInt(wg)]
            print(f"\nYou are currently on {currRealm} {player.dungLevel}.")

            print(f"\nRemove level histories (ex. '- 1 2 3') or '[ASCEND/DESCEND] [x >= 0]' or '<' back to {head[-2]}.")
            prompt = "Enter your choice: "

        s = input(prompt).strip().upper().split()
        if u.splits(s, lambda x: x == '-', lasts = lambda x: u.strRange(x, 1, len(tableIndexToH) + 1)):
            print("Removing these histories:")
            for n in sorted(map(int, set(s[1:]))):
                realm = c.URTS_REALMS_HISTORY_INT_STR[tableIndexToH[n].urts_realmInt(wg)]
                print(f"{I}{n}) {realm} {tableIndexToH[n].level}")
                histories.remove(tableIndexToH[n])
            print(f"^ Got it, histories removed.")
        elif u.splits(s, lambda x: x in {"ASCEND", "DESCEND"}, lambda x: x.isdecimal()): #int here cant be negative
            old = player.dungLevel
            new = player.dungLevel + (-1 if s[0] == "ASCEND" else 1)*int(s[1])
            if new < 0: new = 0
            player.dungLevel = new
            realm = c.URTS_REALMS_HISTORY_INT_STR[player.urts_realmInt(wg)]
            print(f"^ Got it, current level from {realm} {old} —> {new}")
        elif s == ['<']:
            return
        else:
            prompt = f"{I}Invalid input. Try again: "
            skipChoices = True
            continue
        skipChoices = False


#-------------------------------------------------------------------------------------#
# Respec interface.

def _handleRespecInterface(player, wg, HEAD: list) -> None:
    player.str, player.dex, player.vit, player.mag = (0,0,0,0)#(25, 20, 25, 10)
    player.skills = [0]*15
    player.unspentStats, player.unspentSkills = player.level*5 - 5, player.level*2 - 2
    print(f"^ Got it, you now have {player.unspentStats, player.unspentSkills} from being lv. {player.level}.")


#-------------------------------------------------------------------------------------#
# Damage interface.

def _handleDamageInterface(pl, itemCorpus, wg, HEAD: list) -> None:
    #--------------------------------------------------------------------------------------------------------------------------------#
    # Helper functions rely on names local to their enclosing function.
    def __computeWhatIf(whatIf: dict[str:(int or 'X',bool)], ID: str) -> ("dps", (tuple[tuple[str]], tuple[tuple[str]]) ):
        def actual(n, hand: str = None) -> int:
            """pass hand (R/L) iff DUALWIELDING"""
            n += int(n * fullStrength/100)
            n += ceil(n * percDmg/100)
            n += int(plusDmg)
            n += skill[cx.type if not DUALWIELDING else (cr.type if hand == "R" else cl.type)]
            if DUALWIELDING: n = int(n * c.DUAL_SKILL_TO_MULT(dual, "P" if (hand == "R" and not swap or hand == "L" and swap) else "S"))
            n += xbonuses if not DUALWIELDING else (rbonuses if hand == "R" else lbonuses)
            return n

        def displayed(n, hand: str = None) -> int:
            """pass hand (R/L) iff DUALWIELDING.
            ADDS ON BOTH HANDS' BONUSES IF DUAL WIELDING"""
            n += int(n * fullStrength/100)
            n += skill[cx.type if not DUALWIELDING else (cr.type if hand == "R" else cl.type)]
            if DUALWIELDING: n = int(n * c.DUAL_SKILL_TO_MULT(dual, "P" if (hand == "R" and not swap or hand == "L" and swap) else "S"))
            n += ceil(n * percDmg/100)
            n += int(plusDmg)
            n += xbonuses if not DUALWIELDING else rbonuses + lbonuses
            return n

        baseNoRaceStrength, plusStrength, percStrength = def_baseNoRaceStrength, def_plusStrength, def_percStrength
        baseNoRaceDexterity, plusDexterity, percDexterity = def_baseNoRaceDexterity, def_plusDexterity, def_percDexterity
        plusDmg, percDmg = def_plusDmg, def_percDmg
        plusAtt, percAtt = def_plusAtt, def_percAtt
        skill: dict = dict(def_skill)
        crit, dual = def_crit, def_dual
        attSpeed = def_attSpeed
        defense = def_defense
        swap = def_swap

        #applying whatif
        for name, (val, plus) in whatIf.items():
            if DUALWIELDING and name == "SWAP":
                swap = not swap
            elif name.endswith("STR"):
                if name[0] == '+':
                    if val == 'X': val = ORIG_PLUSSTRENGTH
                    if plus: plusStrength += val 
                    else: plusStrength = val 
                elif name[0] == '%':
                    if val == 'X': val = ORIG_PERCSTRENGTH
                    if plus: percStrength += val 
                    else: percStrength = val
                else:
                    if val == 'X': val = ORIG_BASENORACESTRENGTH
                    if plus: baseNoRaceStrength += val 
                    else: baseNoRaceStrength = val 
            elif name.endswith("DEX"):
                if name[0] == '+':
                    if val == 'X': val = ORIG_PLUSDEXTERITY
                    if plus: plusDexterity += val 
                    else: plusDexterity = val 
                elif name[0] == '%':
                    if val == 'X': val = ORIG_PERCDEXTERITY
                    if plus: percDexterity += val 
                    else: percDexterity = val
                else:
                    if val == 'X': val = ORIG_BASENORACEDEXTERITY
                    if plus: baseNoRaceDexterity += val 
                    else: baseNoRaceDexterity = val 
            elif name == "%DMG":
                if val == 'X': val = ORIG_PERCDMG
                if plus: percDmg += val 
                else: percDmg = val 
            elif name == "+DMG":
                if val == 'X': val = ORIG_PLUSDMG
                if plus: plusDmg += val 
                else: plusDmg = val 
            elif name == "%ATT":
                if val == 'X': val = ORIG_PERCATT
                if plus: percAtt += val 
                else: percAtt = val 
            elif name == "+ATT":
                if val == 'X': val = ORIG_PLUSATT
                if plus: plusAtt += val 
                else: plusAtt = val 
            elif name in skill:
                if val == 'X': val = ORIG_SKILL[name]
                if plus: skill[name] += val 
                else: skill[name] = val
            elif name == "CRIT":
                if val == 'X': val = ORIG_CRIT
                if plus: crit += val 
                else: crit = val 
            elif name == "DUAL":
                if val == 'X': val = ORIG_DUAL
                if plus: dual += val 
                else: dual = val 
            elif name == "ATTSPEED":
                if val == 'X': val = ORIG_ATTSPEED
                if plus: attSpeed += val
                else: attSpeed = val
            elif name == "DEF":
                if val == 'X': val = ORIG_DEFENSE
                if plus: defense += val
                else: defense = val

        fullStrength = pl.fullStrength(wg, baseNoRaceStrength , plusStrength, percStrength)

        if not DUALWIELDING:
            baseMin, baseMax = c.DMG_APPLY_RANK_GRADE(cx.dmgRange, xrank, xgrade)
            minDisplayed, maxDisplayed = displayed(baseMin), displayed(baseMax)
            minActual, maxActual, avgActual = actual(baseMin), actual(baseMax), u.avg( [actual(n) for n in u.irange(baseMin, baseMax)] )

            critChance = c.CRITSHIELD_SKILL_TO_PERC(crit)
            avgActual = (1 + critChance/100) * (avgActual - xbonuses) + xbonuses

            attackSpeed = (1 + attSpeed/100) * c.ATTACKSPEEDS[cx.attackSpeedStr]
            if attackSpeed < 0.2: attackSpeed = 0.2
            attackTimer = u.avg(c.ATTACKTYPE_ANIMATIONLENGTHS[c.WEAPONTYPE_ATTACKTYPE[cx.type]]) * 0.8
            attackTimer /= attackSpeed

            fullDex = pl.fullDexterity(wg, baseNoRaceDexterity, plusDexterity, percDexterity)
            hitChance = (a := pl.fullAttack(fullDex, skill[cx.type], percAtt = percAtt, plusAtt = plusAtt)) / (a + defense)
            if hitChance < 0.05: hitChance = 0.05
            elif hitChance > 0.95: hitChance = 0.95
            hitChance *= 100

            dps = avgActual * (1/attackTimer) * hitChance/100

            return (dps, (  ((ID,),
                             (fullStrength,),
                             (fullDex,),
                             (f"{plusDmg} / {percDmg}",),
                             (a,),
                             (skill[cx.type],),
                             (attSpeed,),
                             (defense,)),
            
                            ((ID,),
                             (f"{minActual}—{maxActual}",),
                             (f"{critChance:.3f}",),
                             (f"{1/attackTimer:.3f}",),
                             (f"{hitChance:.3f}",),
                             (f"{minDisplayed}—{maxDisplayed}",),
                             (f"{dps:.3f}",))   ))

        else: #DUALWIELDING
            r_baseMin, r_baseMax = c.DMG_APPLY_RANK_GRADE(cr.dmgRange, rrank, rgrade)
            r_minDisplayed, r_maxDisplayed = displayed(r_baseMin, "R"), displayed(r_baseMax, "R")
            l_baseMin, l_baseMax = c.DMG_APPLY_RANK_GRADE(cl.dmgRange, lrank, lgrade)
            l_minDisplayed, l_maxDisplayed = displayed(l_baseMin, 'L'), displayed(l_baseMax, "L")
            minDisplayed = min(r_minDisplayed, l_minDisplayed)
            maxDisplayed = max(r_maxDisplayed, l_maxDisplayed)

            r_minActual, r_maxActual, r_avgActual = actual(r_baseMin, "R"), actual(r_baseMax, "R"), u.avg( [actual(n, "R") for n in u.irange(r_baseMin, r_baseMax)] )
            l_minActual, l_maxActual, l_avgActual = actual(l_baseMin, "L"), actual(l_baseMax, "L"), u.avg( [actual(n, "L") for n in u.irange(l_baseMin, l_baseMax)] )

            critChance = c.CRITSHIELD_SKILL_TO_PERC(crit)
            r_avgActual = (1 + critChance/100) * (r_avgActual - rbonuses) + rbonuses
            l_avgActual = (1 + critChance/100) * (l_avgActual - lbonuses) + lbonuses

            r_attackSpeed = (1 + attSpeed/100) * c.ATTACKSPEEDS[cr.attackSpeedStr]
            if r_attackSpeed < 0.2: r_attackSpeed = 0.2
            r_attackTimer = u.avg(c.ATTACKTYPE_ANIMATIONLENGTHS[c.WEAPONTYPE_ATTACKTYPE[cr.type]]) * 0.6
            r_attackTimer /= r_attackSpeed
            l_attackSpeed = (1 + attSpeed/100) * c.ATTACKSPEEDS[cl.attackSpeedStr]
            if l_attackSpeed < 0.2: l_attackSpeed = 0.2
            l_attackTimer = u.avg(c.ATTACKTYPE_ANIMATIONLENGTHS[c.WEAPONTYPE_ATTACKTYPE[cl.type]]) * 0.6
            l_attackTimer /= l_attackSpeed

            fullDex = pl.fullDexterity(wg, baseNoRaceDexterity, plusDexterity, percDexterity)
            r_hitChance = (ra := pl.fullAttack(fullDex, skill[cr.type], percAtt = percAtt, plusAtt = plusAtt)) / (ra + defense)
            if r_hitChance < 0.05: r_hitChance = 0.05
            elif r_hitChance > 0.95: r_hitChance = 0.95
            r_hitChance *= 100
            l_hitChance = (la := pl.fullAttack(fullDex, skill[cl.type], percAtt = percAtt, plusAtt = plusAtt)) / (la + defense)
            if l_hitChance < 0.05: l_hitChance = 0.05
            elif l_hitChance > 0.95: l_hitChance = 0.95
            l_hitChance *= 100

            dps = ((r_avgActual * (1/r_attackTimer) * r_hitChance/100) + (l_avgActual * (1/l_attackTimer) * l_hitChance/100)) / 2

            return (dps, (  ((ID,),
                             ("Y" if swap else "N",),
                             (fullStrength,),
                             (fullDex,),
                             (f"{plusDmg} / {percDmg}",),
                             (f"{ra}/{la}",),
                             ("/".join(map(str, skill.values())),),
                             (attSpeed,),
                             (defense,)),

                            ((ID,),
                             (*("PS" if not swap else "SP"),),
                             (f"{r_minDisplayed}—{r_maxDisplayed}({lbonuses})", f"{l_minDisplayed}—{l_maxDisplayed}({rbonuses})",),
                             (f"{r_minActual}—{r_maxActual}", f"{l_minActual}—{l_maxActual}",),
                             (f"{critChance:.3f}",),
                             (f"{1/r_attackTimer:.3f}", f"{1/l_attackTimer:.3f}",),
                             (f"{r_hitChance:.3f}", f"{l_hitChance:.3f}",),
                             (f"{minDisplayed}—{maxDisplayed}",),
                             (f"{dps:.3f}",))  ))

    #--------------------------------------------------------------------------------------------------------------------------------#

    head = HEAD + ["Damage"]

    if (r := item.findItemByESlot(3, pl.items["EQUIPPED"])):
        rname = r.baseName.decode('utf-8').upper()
        cr = itemCorpus[rname] if rname in itemCorpus else itemCorpus[u.prefixRemoved(rname, c.RANKS_WITH_POSTSPACE)]
        rrank = '' if rname in itemCorpus else rname[:rname.find(' ')]
        rgrade = r.grade
        rbonuses = sum(b.val for b in r.bonuses)
    if (l := item.findItemByESlot(2, pl.items["EQUIPPED"])):
        lname = l.baseName.decode('utf-8').upper()
        cl = itemCorpus[lname] if lname in itemCorpus else itemCorpus[u.prefixRemoved(lname, c.RANKS_WITH_POSTSPACE)]
        lrank = '' if lname in itemCorpus else lname[:lname.find(' ')]
        lgrade = l.grade
        lbonuses = sum(b.val for b in l.bonuses)
    DUALWIELDING = r and l and cl.type != "SHIELD"
    if not DUALWIELDING: x, cx, xrank, xgrade, xbonuses = (r, cr, rrank, rgrade, rbonuses) if r else (l, cl, lrank, lgrade, lbonuses)

    ORIG_BASENORACESTRENGTH, ORIG_PLUSSTRENGTH, ORIG_PERCSTRENGTH = def_baseNoRaceStrength, def_plusStrength, def_percStrength = \
        pl.str, pl.cumEnchant("+STR", wg, True), pl.cumEnchant("%STR", wg, True)
    ORIG_BASENORACEDEXTERITY, ORIG_PLUSDEXTERITY, ORIG_PERCDEXTERITY = def_baseNoRaceDexterity, def_plusDexterity, def_percDexterity = \
        pl.dex, pl.cumEnchant("+DEX", wg, True), pl.cumEnchant("%DEX", wg, True)
    ORIG_PLUSDMG, ORIG_PERCDMG = def_plusDmg, def_percDmg = pl.cumEnchant("+DMG", wg, True), pl.cumEnchant("%DMG", wg, True)
    ORIG_PLUSATT, ORIG_PERCATT = def_plusAtt, def_percAtt = pl.cumEnchant("+ATT", wg, True), pl.cumEnchant("%ATT", wg, True)
    ORIG_SKILL = dict(def_skill := {cr.type : pl.fullSkill(cr.type, wg), cl.type : pl.fullSkill(cl.type, wg)} if DUALWIELDING else {cx.type : pl.fullSkill(cx.type, wg)})
    ORIG_CRIT, ORIG_DUAL = def_crit, def_dual = pl.fullSkill("CRIT", wg), pl.fullSkill("DUAL", wg)
    ORIG_ATTSPEED = def_attSpeed = pl.cumEnchant("ATTSPEED", wg, True)
    ORIG_DEFENSE = def_defense = 0
    ORIG_SWAP = def_swap = False

    SKILL_PRINT = '/'.join(TYPES := ([cr.type, cl.type] if DUALWIELDING else [cx.type]))
    printChoices = True
    prompt = "Enter your choice: "
    while True:
        if printChoices:
            PNTS_ORIG_PRINT = '/'.join(map(str, ORIG_SKILL.values()))
            PNTS_DEF_PRINT = '/'.join(map(str, def_skill.values()))
            printHeader(head)
            print(f"\nSet defaults in [] at the front (ex. '[SWAP 100 CRIT X DUAL] 50 %DMG ; SWAP +50 +DMG ; 50 CRIT +X {SKILL_PRINT}').")
            print(f"Comparisons (<= 26) separated by ';' override DEFAULTS (ex. '50 %DMG ; SWAP +50 +DMG ; 50 CRIT +X {SKILL_PRINT}').")
            print(I + "—SWAP Primary/Secondary hands (put at front)")
            print(I + f"—STR [{ORIG_BASENORACESTRENGTH} —> {def_baseNoRaceStrength}], +STR [{ORIG_PLUSSTRENGTH} —> {def_plusStrength}], %STR [{ORIG_PERCSTRENGTH} —> {def_percStrength}]")
            print(I + f"—DEX [{ORIG_BASENORACEDEXTERITY} —> {def_baseNoRaceDexterity}], +DEX [{ORIG_PLUSDEXTERITY} —> {def_plusDexterity}], %DEX [{ORIG_PERCDEXTERITY} —> {def_percDexterity}]")
            print(I + f"—+DMG [{ORIG_PLUSDMG} —> {def_plusDmg}], %DMG [{ORIG_PERCDMG} —> {def_percDmg}]")
            print(I + f"—+ATT [{ORIG_PLUSATT} —> {def_plusAtt}], %ATT [{ORIG_PERCATT} —> {def_percAtt}]")
            print(I + f"—{SKILL_PRINT} [{PNTS_ORIG_PRINT} —> {PNTS_DEF_PRINT}], CRIT [{ORIG_CRIT} —> {def_crit}], DUAL [{ORIG_DUAL} —> {def_dual}]")
            print(I + f"—ATTSPEED [{ORIG_ATTSPEED} —> {def_attSpeed}]")
            print(I + f"—DEF (opposing) [{ORIG_DEFENSE} —> {def_defense}]")
            print("[actual —> default]. Use N >= 0. '+N' adds N instead of overriding. 'X' means actual value.")
            print(f"Your defaulted damage calculations will be displayed for reference. '<' to {head[-2]}.\n")

        choice = input(prompt).strip().upper()
        if choice == '<':
            return
        else:
            firstSplit = resplit(r'^\[([^\[]*)\]\s*', choice, 1)
            if len(firstSplit) > 1:
                default = [firstSplit[1]] ; s = firstSplit[2]
                if not (def_whatIfs := __getWhatIfs(default, TYPES)):
                    prompt = I + "Try again: " ; printChoices = False ; continue
            else:
                def_whatIfs = [dict()] ; s = firstSplit[0]

            s = resplit(r'\s*;[\s;]*', s)
            if not (whatIfs := __getWhatIfs(s, TYPES)) or len(whatIfs) > 26+1:
                prompt = I + "Try again: " ; printChoices = False ; continue

        #applying defaults
        for name, (val, plus) in def_whatIfs[-1].items():
            if name == "SWAP" and DUALWIELDING:
                def_swap = not def_swap
            elif name.endswith("STR"):
                if name[0] == '+':
                    if val == 'X': val = ORIG_PLUSSTRENGTH
                    if plus: def_plusStrength += val 
                    else: def_plusStrength = val 
                elif name[0] == '%':
                    if val == 'X': val = ORIG_PERCSTRENGTH
                    if plus: def_percStrength += val 
                    else: def_percStrength = val
                else:
                    if val == 'X': val = ORIG_BASENORACESTRENGTH
                    if plus: def_baseNoRaceStrength += val 
                    else: def_baseNoRaceStrength = val 
            elif name.endswith("DEX"):
                if name[0] == '+':
                    if val == 'X': val = ORIG_PLUSDEXTERITY
                    if plus: def_plusDexterity += val 
                    else: def_plusDexterity = val 
                elif name[0] == '%':
                    if val == 'X': val = ORIG_PERCDEXTERITY
                    if plus: def_percDexterity += val 
                    else: def_percDexterity = val
                else:
                    if val == 'X': val = ORIG_BASENORACEDEXTERITY
                    if plus: def_baseNoRaceDexterity += val 
                    else: def_baseNoRaceDexterity = val 
            elif name == "%DMG":
                if val == 'X': val = ORIG_PERCDMG
                if plus: def_percDmg += val 
                else: def_percDmg = val 
            elif name == "+DMG":
                if val == 'X': val = ORIG_PLUSDMG
                if plus: def_plusDmg += val 
                else: def_plusDmg = val 
            elif name == "%ATT":
                if val == 'X': val = ORIG_PERCATT
                if plus: def_percAtt += val 
                else: def_percAtt = val 
            elif name == "+ATT":
                if val == 'X': val = ORIG_PLUSATT
                if plus: def_plusAtt += val 
                else: def_plusAtt = val 
            elif name in def_skill:
                if val == 'X': val = ORIG_SKILL[name]
                if plus: def_skill[name] += val 
                else: def_skill[name] = val
            elif name == "CRIT":
                if val == 'X': val = ORIG_CRIT
                if plus: def_crit += val 
                else: def_crit = val 
            elif name == "DUAL":
                if val == 'X': val = ORIG_DUAL
                if plus: def_dual += val 
                else: def_dual = val 
            elif name == "ATTSPEED":
                if val == 'X': val = ORIG_ATTSPEED
                if plus: def_attSpeed += val
                else: def_attSpeed = val
            elif name == "DEF":
                if val == 'X': val = ORIG_DEFENSE
                if plus: def_defense += val
                else: def_defense = val

        computedVals = [__computeWhatIf(whatIf, chr(ord('@')+i)) for i, whatIf in enumerate(whatIfs)]
        ret_place = {ret : i for i, ret in enumerate(sorted(computedVals, key = lambda x: -x[0]), 1)}
        
        print(f"\n{C('The comparisons lettered in the order entered (+ default @), numbered by descending DPS: ')}\n")
        TABLE1COLS = c.DMGWHATIF_COLS1_DUAL(SKILL_PRINT) if DUALWIELDING else c.DMGWHATIF_COLS1_NODUAL(SKILL_PRINT)
        print('|'.join(f"{string:^{pad}}" for pad, string in TABLE1COLS))
        for ret in computedVals:
            print('|'.join('—'*pad for pad, _ in TABLE1COLS))
            whatIfRow = u.zipAllTheWay(*ret[1][0])
            for rowi, row in enumerate(whatIfRow):
                if rowi == 0: row[0] = f"{row[0]} (#{ret_place[ret]})"
                print('|'.join(f"{chunk:^{TABLE1COLS[i][0]}}" if chunk is not None else ' '*TABLE1COLS[i][0] for i, chunk in enumerate(row)))
        print(f"\n{C('The damage calculations in order of descending DPS: ')}\n")
        TABLE2COLS = c.DMGWHATIF_COLS2_DUAL if DUALWIELDING else c.DMGWHATIF_COLS2_NODUAL
        print('|'.join(f"{string:^{pad}}" for pad, string in TABLE2COLS))
        for ret, place in ret_place.items():
            print('|'.join('—'*pad for pad, _ in TABLE2COLS))
            whatIfRow = u.zipAllTheWay(*ret[1][1])
            for rowi, row in enumerate(whatIfRow):
                if rowi == 0: row[0] = f"{place}) {row[0]}"
                print('|'.join(f"{chunk:^{TABLE2COLS[i][0]}}" if chunk is not None else ' '*TABLE2COLS[i][0] for i, chunk in enumerate(row)))

        prompt = "Got it, any more?: " ; printChoices = True

def __getWhatIfs(s: list[str], TYPES: list) -> list[dict[str:(int or 'X',bool)]] or False:
    """Returns False if continue to try again."""
    POSS_NO_SWAP = {"STR", "+STR", "%STR", "DEX", "+DEX", "%DEX", "%DMG", "+DMG", "%ATT", "+ATT", "CRIT", "DUAL", "ATTSPEED", "DEF"}
    for t in TYPES: POSS_NO_SWAP.add(t)

    whatIfs: list[dict[str:(int or 'X',bool)]] = [dict()]
    for whatIfStr in s:
        if whatIfStr:
            whatIfWords = whatIfStr.split()
            thisWhatIf: dict[str:(int or 'X',bool)] = dict()
            if whatIfWords[0] == "SWAP": thisWhatIf["SWAP"] = (None, None)
            whatIfWords = iter(whatIfWords)
            if "SWAP" in thisWhatIf: next(whatIfWords)
            thisNum = thisNumApplied = None
            for word in whatIfWords:
                if match(r'^\+?(X|\d+)$', word):
                    if thisNumApplied is False: return False                        #if number not applied
                    thisNum = ('X' if word[-1] == 'X' else int(word), word[0] == '+')
                    thisNumApplied = False
                else:
                    if thisNum is None: return False                                #if a non-first-SWAP word before a number
                    if word not in POSS_NO_SWAP or word in thisWhatIf: return False #if bogus or already used word
                    thisWhatIf[word] = thisNum
                    thisNumApplied = True
            if thisNumApplied is False: return False                                #if last number not applied
            whatIfs.append(thisWhatIf)

    return whatIfs