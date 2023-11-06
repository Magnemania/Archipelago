from typing import Callable, Union

from BaseClasses import MultiWorld
from ..generic.Rules import add_rule, set_rule
from .Locations import location_table
from .Regions import connect_regions, sm64courses, sm64paintings, sm64secrets, sm64entrances
from .Items import action_item_table

def fix_reg(entrance_ids, reg, invalidspot, swaplist, world):
    if entrance_ids.index(reg) == invalidspot: # Unlucky :C
            swaplist.remove(invalidspot)
            rand = world.random.choice(swaplist)
            entrance_ids[invalidspot], entrance_ids[rand] = entrance_ids[rand], entrance_ids[invalidspot]
            swaplist.append(invalidspot)
            swaplist.remove(rand)

def set_rules(world, player: int, area_connections, star_costs):
    destination_regions = list(range(13)) + [12,13,14] + list(range(15,15+len(sm64secrets))) # Two instances of Destination Course THI. Past normal course idx are secret regions
    secret_entrance_ids = list(range(len(sm64paintings), len(sm64paintings) + len(sm64secrets)))
    course_entrance_ids = list(range(len(sm64paintings)))
    valid_move_randomizer_start_courses = [0, 2, 3, 4, 6, 7, 8, 9]  # Excluding WF, HMC, WDW, TTM, THI, TTC, and RR
    if world.AreaRandomizer[player].value >= 1:  # Some randomization is happening, randomize Courses
        world.random.shuffle(course_entrance_ids)
        if world.AreaRandomizer[player].value < 3 and world.RandomizeMoves[player]:
            first_course = world.random.choice(valid_move_randomizer_start_courses)
            course_to_swap = course_entrance_ids.index(0)
            course_entrance_ids[first_course], course_entrance_ids[course_to_swap] = 0, course_entrance_ids[first_course]

    if world.AreaRandomizer[player].value == 2:  # Randomize Secrets as well
        world.random.shuffle(secret_entrance_ids)
    entrance_ids = course_entrance_ids + secret_entrance_ids
    if world.AreaRandomizer[player].value == 3:  # Randomize Courses and Secrets in one pool
        world.random.shuffle(entrance_ids)
        # Guarantee first entrance is a course
        swaplist = list(range(len(entrance_ids)))
        valid_first_courses = valid_move_randomizer_start_courses if world.RandomizeMoves[player] else list(range(15))
        if entrance_ids.index(0) not in valid_first_courses:  # Unlucky :C
            rand = world.random.choice(valid_first_courses)
            entrance_ids[entrance_ids.index(0)], entrance_ids[rand] = entrance_ids[rand], entrance_ids[entrance_ids.index(0)]
            swaplist.remove(entrance_ids.index(0))
        # Guarantee COTMC is not mapped to HMC, cuz thats impossible
        fix_reg(entrance_ids, 20, 5, swaplist, world)
        # Guarantee BITFS is not mapped to DDD
        fix_reg(entrance_ids, 22, 8, swaplist, world)
    temp_assign = dict(zip(entrance_ids,destination_regions)) # Used for Rules only

    # Destination Format: LVL | AREA with LVL = LEVEL_x, AREA = Area as used in sm64 code
    area_connections.update({sm64entrances[entrance]: destination for entrance, destination in zip(entrance_ids,sm64entrances)})

    rf = RuleFactory(world, player)

    connect_regions(world, player, "Menu", sm64courses[temp_assign[0]]) # BOB
    connect_regions(world, player, "Menu", sm64courses[temp_assign[1]], lambda state: state.has("Power Star", player, 1)) # WF
    connect_regions(world, player, "Menu", sm64courses[temp_assign[2]], lambda state: state.has("Power Star", player, 3)) # JRB
    connect_regions(world, player, "Menu", sm64courses[temp_assign[3]], lambda state: state.has("Power Star", player, 3)) # CCM
    connect_regions(world, player, "Menu", sm64courses[temp_assign[4]], lambda state: state.has("Power Star", player, 12)) # BBH
    connect_regions(world, player, "Menu", sm64courses[temp_assign[16]], lambda state: state.has("Power Star", player, 1)) # PSS
    connect_regions(world, player, sm64courses[temp_assign[2]], sm64courses[temp_assign[17]], rf.build_rule("SF/BF | TJ & LG | MOVELESS & TJ")) # SA
    connect_regions(world, player, "Menu", sm64courses[temp_assign[19]], lambda state: state.has("Power Star", player, 10)) # TOTWC
    connect_regions(world, player, "Menu", sm64courses[temp_assign[18]], lambda state: state.has("Power Star", player, star_costs["FirstBowserDoorCost"])) # BITDW

    connect_regions(world, player, "Menu", "Basement", lambda state: state.has("Basement Key", player) or state.has("Progressive Key", player, 1))

    connect_regions(world, player, "Basement", sm64courses[temp_assign[5]]) # HMC
    connect_regions(world, player, "Basement", sm64courses[temp_assign[6]]) # LLL
    connect_regions(world, player, "Basement", sm64courses[temp_assign[7]]) # SSL
    connect_regions(world, player, "Basement", sm64courses[temp_assign[8]], lambda state: state.has("Power Star", player, star_costs["BasementDoorCost"])) # DDD
    connect_regions(world, player, "Hazy Maze Cave", sm64courses[temp_assign[20]]) # COTMC
    connect_regions(world, player, "Basement", sm64courses[temp_assign[21]], rf.build_rule("GP")) # VCUTM
    connect_regions(world, player, "Basement", sm64courses[temp_assign[22]], lambda state: state.has("Power Star", player, star_costs["BasementDoorCost"]) and
                                                                                       state.can_reach("DDD: Board Bowser's Sub", 'Location', player)) # BITFS

    connect_regions(world, player, "Menu", "Second Floor", lambda state: state.has("Second Floor Key", player) or state.has("Progressive Key", player, 2))

    connect_regions(world, player, "Second Floor", sm64courses[temp_assign[9]]) # SL
    connect_regions(world, player, "Second Floor", sm64courses[temp_assign[10]]) # WDW
    connect_regions(world, player, "Second Floor", sm64courses[temp_assign[11]]) # TTM
    connect_regions(world, player, "Second Floor", sm64courses[temp_assign[12]]) # THI Tiny
    connect_regions(world, player, "Second Floor", sm64courses[temp_assign[13]]) # THI Huge

    connect_regions(world, player, "Second Floor", "Third Floor", lambda state: state.has("Power Star", player, star_costs["SecondFloorDoorCost"]))
    connect_regions(world, player, "Third Floor", sm64courses[temp_assign[14]], rf.build_rule("LG/TJ/SF/BF/WK")) # TTC
    connect_regions(world, player, "Third Floor", sm64courses[temp_assign[15]], rf.build_rule("TJ/SF/BF")) # RR
    connect_regions(world, player, "Third Floor", sm64courses[temp_assign[23]], rf.build_rule("TJ/SF/BF")) # WMOTR
    connect_regions(world, player, "Third Floor", "Bowser in the Sky", lambda state: state.has("Power Star", player, star_costs["StarsToFinish"])) # BITS

    # Course Rules
    # Bob-omb Battlefield
    rf.assign_rule("BoB: Island", "CANN | CANNLESS & WC & TJ | CAPLESS & CANNLESS & LJ")
    rf.assign_rule("BoB: Mario Wings to the Sky",  "CANN & WC | CAPLESS & CANN")
    rf.assign_rule("BoB: Behind Chain Chomp's Gate", "GP | MOVELESS")
    # Whomp's Fortress
    rf.assign_rule("WF: Tower", "{{WF: Chip Off Whomp's Block}}")
    rf.assign_rule("WF: Chip Off Whomp's Block", "GP")
    rf.assign_rule("WF: Shoot into the Wild Blue", "WK & TJ/SF | CANN")
    rf.assign_rule("WF: Fall onto the Caged Island", "CL & {WF: Tower} | MOVELESS & TJ | MOVELESS & LJ | MOVELESS & CANN")
    rf.assign_rule("WF: Blast Away the Wall", "CANN | CANNLESS & LG")
    # Jolly Roger Bay
    rf.assign_rule("JRB: Upper", "TJ/BF/SF/WK | MOVELESS & LG")
    rf.assign_rule("JRB: Red Coins on the Ship Afloat", "CL/CANN/TJ/BF/WK")
    rf.assign_rule("JRB: Blast to the Stone Pillar", "CANN+CL | CANNLESS & MOVELESS | CANN & MOVELESS")
    rf.assign_rule("JRB: Through the Jet Stream", "MC | CAPLESS")
    # Cool, Cool Mountain
    rf.assign_rule("CCM: Wall Kicks Will Work", "TJ/WK & CANN | CANNLESS & TJ/WK | MOVELESS")
    # Big Boo's Haunt
    rf.assign_rule("BBH: Third Floor", "WK+LG | MOVELESS & WK")
    rf.assign_rule("BBH: Roof", "LJ | MOVELESS")
    rf.assign_rule("BBH: Seek the 8 Red Coins", "BF/WK/TJ/SF")
    rf.assign_rule("BBH: Eye to Eye in the Secret Room", "VC")
    # Haze Maze Cave
    rf.assign_rule("HMC: Red Coin Area", "CL & WK/LG/BF/SF/TJ | MOVELESS & WK")
    rf.assign_rule("HMC: Pit Islands", "TJ+CL | MOVELESS & WK & TJ/LJ | MOVELESS & WK+SF+LG")
    rf.assign_rule("HMC: Metal-Head Mario Can Move!", "LJ+MC | CAPLESS & LJ+TJ | CAPLESS & MOVELESS & LJ/TJ/WK")
    rf.assign_rule("HMC: Navigating the Toxic Maze", "WK/SF/BF/TJ")
    rf.assign_rule("HMC: Watch for Rolling Rocks", "WK")
    # Lethal Lava Land
    rf.assign_rule("LLL: Hot-Foot-It into the Volcano", "CL | MOVELESS & WK")
    rf.assign_rule("LLL: Elevator Tour in the Volcano", "CL | MOVELESS & WK+LJ")
    # Shifting Sand Land
    rf.assign_rule("SSL: Upper Pyramid", "CL & TJ/BF/SF/LG | MOVELESS | WC+TJ | WC+CANN")
    rf.assign_rule("SSL: Free Flying for 8 Red Coins", "TJ+WC | WC+CANN")
    rf.assign_rule("SSL: Inside the Ancient Pyramid", "MOVELESS | WC+TJ | WC+CANN")
    # Dire, Dire Docks
    rf.assign_rule("DDD: Moving Poles", "CL & {{Bowser in the Fire Sea Key}} | TJ+DV+LG+WK & MOVELESS")
    rf.assign_rule("DDD: Through the Jet Stream", "MC | CAPLESS")
    rf.assign_rule("DDD: Collect the Caps...", "VC+MC | CAPLESS & VC")
    # Snowman's Land
    rf.assign_rule("SL: Snowman's Big Head", "BF/SF/CANN/TJ")
    rf.assign_rule("SL: In the Deep Freeze", "WK/SF/LG/BF/CANN/TJ")
    rf.assign_rule("SL: Into the Igloo", "VC")
    # Wet-Dry World
    rf.assign_rule("WDW: Top", "WK/TJ/SF/BF | MOVELESS")
    rf.assign_rule("WDW: Downtown", "NAR & LG | CANN | MOVELESS & TJ+DV")
    rf.assign_rule("WDW: Go to Town for Red Coins", "WK | MOVELESS & TJ")
    rf.assign_rule("WDW: Quick Race Through Downtown!", "VC & WK/BF | VC & TJ+LG | MOVELESS & VC & TJ")
    rf.assign_rule("WDW: Bob-omb Buddy", "TJ | SF+LG | NAR & BF/SF")
    # Tall, Tall Mountain
    rf.assign_rule("TTM: Top", "MOVELESS & TJ | LJ/DV & LG/KK | MOVELESS & WK & SF/LG | MOVELESS & KK/DV")
    rf.assign_rule("TTM: Blast to the Lonely Mushroom", "CANN | CANNLESS & LJ | MOVELESS & CANNLESS")
    # Tiny-Huge Island
    rf.assign_rule("THI: Pipes", "NAR | LJ/TJ/DV/LG | MOVELESS & BF/SF/KK")
    rf.assign_rule("THI: Large Top", "NAR | LJ/TJ/DV")
    rf.assign_rule("THI: Wiggler's Red Coins", "WK")
    rf.assign_rule("THI: Make Wiggler Squirm", "GP | MOVELESS & DV")
    # Tick Tock Clock
    rf.assign_rule("TTC: Lower", "LG/TJ/SF/BF/WK")
    rf.assign_rule("TTC: Upper", "CL | SF/TJ & WK")
    rf.assign_rule("TTC: Top", "SF/TJ & WK | MOVELESS & WK+LG")
    rf.assign_rule("TTC: Stomp on the Thwomp", "TJ+WK | MOVELESS & WK+LG")
    rf.assign_rule("TTC: Stop Time for Red Coins", "NAR | {TTC: Lower}")
    # Rainbow Ride
    rf.assign_rule("RR: Maze", "WK | LJ & SF/BF/TJ | MOVELESS & LG/TJ")
    rf.assign_rule("RR: Bob-omb Buddy", "WK | MOVELESS & LG")
    rf.assign_rule("RR: Swingin' in the Breeze", "LG/TJ/BF/SF")
    rf.assign_rule("RR: Tricky Triangles!", "LG/TJ/BF/SF")
    rf.assign_rule("RR: Cruiser", "WK/SF/BF/LG/TJ")
    rf.assign_rule("RR: House", "TJ/SF/BF/LG")
    rf.assign_rule("RR: Somewhere Over the Rainbow", "CANN")
    # Cavern of the Metal Cap
    rf.assign_rule("Cavern of the Metal Cap Red Coins", "MC | CAPLESS")
    # Vanish Cap Under the Moat
    rf.assign_rule("Vanish Cap Under the Moat Switch", "WK/TJ/BF/SF/LG")
    rf.assign_rule("Vanish Cap Under the Moat Red Coins", "TJ/BF/SF/LG/WK & VC | CAPLESS & WK")
    # Bowser in the Fire Sea
    rf.assign_rule("BitFS: Upper", "CL")
    rf.assign_rule("Bowser in the Fire Sea Red Coins", "LG/WK")
    rf.assign_rule("Bowser in the Fire Sea 1Up Block Near Poles", "LG/WK")
    # Wing Mario Over the Rainbow
    rf.assign_rule("Wing Mario Over the Rainbow Red Coins", "TJ+WC")
    rf.assign_rule("Wing Mario Over the Rainbow 1Up Block", "TJ+WC")
    # Bowser in the Sky
    rf.assign_rule("BitS: Top", "CL+TJ | CL+SF+LG | MOVELESS & TJ+WK+LG")
    # 100 Coin Stars
    if world.EnableCoinStars[player]:
        rf.assign_rule("BoB: 100 Coins", "CANN & WC | CANNLESS & WC & TJ")
        rf.assign_rule("WF: 100 Coins", "GP | MOVELESS")
        rf.assign_rule("JRB: 100 Coins", "GP & {JRB: Upper}")
        rf.assign_rule("HMC: 100 Coins", "GP")
        rf.assign_rule("SSL: 100 Coins", "{SSL: Upper Pyramid} | GP")
        rf.assign_rule("DDD: 100 Coins", "GP")
        rf.assign_rule("SL: 100 Coins", "VC | MOVELESS")
        rf.assign_rule("WDW: 100 Coins", "GP | {WDW: Downtown}")
        rf.assign_rule("TTC: 100 Coins", "GP")
        rf.assign_rule("THI: 100 Coins", "GP")
        rf.assign_rule("RR: 100 Coins", "GP & WK")
    # Castle Stars
    add_rule(world.get_location("Toad (Basement)", player), lambda state: state.can_reach("Basement", 'Region', player) and state.has("Power Star", player, 12))
    add_rule(world.get_location("Toad (Second Floor)", player), lambda state: state.can_reach("Second Floor", 'Region', player) and state.has("Power Star", player, 25))
    add_rule(world.get_location("Toad (Third Floor)", player), lambda state: state.can_reach("Third Floor", 'Region', player) and state.has("Power Star", player, 35))

    if star_costs["MIPS1Cost"] > star_costs["MIPS2Cost"]:
        (star_costs["MIPS2Cost"], star_costs["MIPS1Cost"]) = (star_costs["MIPS1Cost"], star_costs["MIPS2Cost"])
    add_rule(world.get_location("MIPS 1", player), lambda state: state.can_reach("Basement", 'Region', player) and state.has("Power Star", player, star_costs["MIPS1Cost"]))
    add_rule(world.get_location("MIPS 2", player), lambda state: state.can_reach("Basement", 'Region', player) and state.has("Power Star", player, star_costs["MIPS2Cost"]))
    rf.assign_rule("MIPS 1", "DV | MOVELESS")
    rf.assign_rule("MIPS 2", "DV | MOVELESS")

    world.completion_condition[player] = lambda state: state.can_reach("BitS: Top", 'Region', player)


class RuleFactory:

    world: MultiWorld
    player: int
    move_randomizer: bool
    area_randomizer: bool
    capless: bool
    cannonless: bool
    moveless: bool

    token_table = {
        "TJ": "Triple Jump",
        "LJ": "Long Jump",
        "BF": "Backflip",
        "SF": "Side Flip",
        "WK": "Wall Kick",
        "DV": "Dive",
        "GP": "Ground Pound",
        "KK": "Kick",
        "CL": "Climb",
        "LG": "Ledge Grab",
        "WC": "Wing Cap",
        "MC": "Metal Cap",
        "VC": "Vanish Cap"
    }

    class SM64LogicException(Exception):
        pass

    def __init__(self, world, player):
        self.world = world
        self.player = player
        self.move_randomizer = world.RandomizeMoves[player]
        self.area_randomizer = world.AreaRandomizer[player].value > 0
        self.capless = not world.StrictCapRequirements[player]
        self.cannonless = not world.StrictCannonRequirements[player]
        self.moveless = not world.StrictMoveRequirements[player] or not self.move_randomizer

    def assign_rule(self, target_name: str, rule_expr: str):
        target = self.world.get_location(target_name, self.player) if target_name in location_table else self.world.get_entrance(target_name, self.player)
        cannon_name = "Cannon Unlock " + target_name.split(':')[0]
        try:
            rule = self.build_rule(rule_expr, cannon_name)
        except RuleFactory.SM64LogicException as exception:
            raise RuleFactory.SM64LogicException(
                f"Error generating rule for {target_name} using rule expression {rule_expr}: {exception}")
        if rule:
            set_rule(target, rule)

    def build_rule(self, rule_expr: str, cannon_name: str = '') -> Callable:
        expressions = rule_expr.split(" | ")
        rules = []
        for expression in expressions:
            or_clause = self.combine_and_clauses(expression, cannon_name)
            if or_clause is True:
                return None
            if or_clause is not False:
                rules.append(or_clause)
        if rules:
            if len(rules) == 1:
                return rules[0]
            else:
                return lambda state: any(rule(state) for rule in rules)
        else:
            return None

    def combine_and_clauses(self, rule_expr: str, cannon_name: str) -> Union[Callable, bool]:
        expressions = rule_expr.split(" & ")
        rules = []
        for expression in expressions:
            and_clause = self.make_lambda(expression, cannon_name)
            if and_clause is False:
                return False
            if and_clause is not True:
                rules.append(and_clause)
        if rules:
            if len(rules) == 1:
                return rules[0]
            return lambda state: all(rule(state) for rule in rules)
        else:
            return True

    def make_lambda(self, expression: str, cannon_name: str) -> Union[Callable, bool]:
        if '+' in expression:
            tokens = expression.split('+')
            items = set()
            for token in tokens:
                item = self.parse_token(token, cannon_name)
                if item is True:
                    continue
                if item is False:
                    return False
                items.add(item)
            if items:
                return lambda state: state.has_all(items, self.player)
            else:
                return True
        if '/' in expression:
            tokens = expression.split('/')
            items = set()
            for token in tokens:
                item = self.parse_token(token, cannon_name)
                if item is True:
                    return True
                if item is False:
                    continue
                items.add(item)
            if items:
                return lambda state: state.has_any(items, self.player)
            else:
                return False
        if '{{' in expression:
            return lambda state: state.can_reach(expression[2:-2], "Location", self.player)
        if '{' in expression:
            return lambda state: state.can_reach(expression[1:-1], "Region", self.player)
        item = self.parse_token(expression, cannon_name)
        if item in (True, False):
            return item
        return lambda state: state.has(item, self.player)

    def parse_token(self, token: str, cannon_name: str) -> Union[str, bool]:
        if token == "CANN":
            return cannon_name
        if token == "CAPLESS":
            return self.capless
        if token == "CANNLESS":
            return self.cannonless
        if token == "MOVELESS":
            return self.moveless
        if token == "NAR":
            return not self.area_randomizer
        item = self.token_table.get(token, None)
        if not item:
            raise Exception(f"Invalid token: '{item}'")
        if not self.move_randomizer and item in action_item_table:
            # All move items are possessed from the start with MR off
            return True
        return item

