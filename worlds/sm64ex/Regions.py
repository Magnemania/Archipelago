import typing
from BaseClasses import MultiWorld, Region, Entrance, Location
from .Locations import SM64Location, location_table, locBoB_table, locWhomp_table, locJRB_table, locCCM_table, \
    locBBH_table, \
    locHMC_table, locLLL_table, locSSL_table, locDDD_table, locSL_table, \
    locWDW_table, locTTM_table, locTHI_table, locTTC_table, locRR_table, \
    locPSS_table, locSA_table, locBitDW_table, locTotWC_table, locCotMC_table, \
    locVCutM_table, locBitFS_table, locWMotR_table, locBitS_table, locSS_table

# List of all courses, including secrets, without BitS as that one is static
sm64courses = ["Bob-omb Battlefield", "Whomp's Fortress", "Jolly Roger Bay", "Cool, Cool Mountain", "Big Boo's Haunt",
               "Hazy Maze Cave", "Lethal Lava Land", "Shifting Sand Land", "Dire, Dire Docks", "Snowman's Land",
               "Wet-Dry World", "Tall, Tall Mountain", "Tiny-Huge Island", "Tick Tock Clock", "Rainbow Ride",
               "The Princess's Secret Slide", "The Secret Aquarium", "Bowser in the Dark World", "Tower of the Wing Cap",
               "Cavern of the Metal Cap", "Vanish Cap under the Moat", "Bowser in the Fire Sea", "Wing Mario over the Rainbow"]

# sm64paintings is list of entrances, format LEVEL | AREA. String Reference below
sm64paintings   = [91,241,121,51,41,71,221,81,231,101,111,361,132,131,141,151]
sm64paintings_s = ["BOB", "WF", "JRB", "CCM", "BBH", "HMC", "LLL", "SSL", "DDD", "SL", "WDW", "TTM", "THI Tiny", "THI Huge", "TTC", "RR"]
# sm64secrets is list of secret areas
sm64secrets = [271, 201, 171, 291, 281, 181, 191, 311]
sm64secrets_s = ["PSS", "SA", "BitDW", "TOTWC", "COTMC", "VCUTM", "BitFS", "WMOTR"]

sm64entrances = sm64paintings + sm64secrets
sm64entrances_s = sm64paintings_s + sm64secrets_s
sm64_internalloc_to_string = dict(zip(sm64paintings+sm64secrets, sm64entrances_s))
sm64_internalloc_to_regionid = dict(zip(sm64paintings+sm64secrets, list(range(13)) + [12,13,14] + list(range(15,15+len(sm64secrets)))))

def create_regions(world: MultiWorld, player: int):
    regSS = Region("Menu", player, world, "Castle Area")
    create_default_locs(regSS, locSS_table)
    world.regions.append(regSS)

    regBoB = create_region("Bob-omb Battlefield", player, world)
    create_locs(regBoB, "BoB: Big Bob-Omb on the Summit", "BoB: Footrace with Koopa The Quick",
                        "BoB: Mario Wings to the Sky", "BoB: Behind Chain Chomp's Gate", "BoB: Bob-omb Buddy")
    create_subregion(regBoB, "BoB: Island", "BoB: Shoot to the Island in the Sky", "BoB: Find the 8 Red Coins")
    if (world.EnableCoinStars[player].value):
        create_locs(regBoB, "BoB: 100 Coins")

    regWhomp = create_region("Whomp's Fortress", player, world)
    create_locs(regWhomp, "WF: Chip Off Whomp's Block", "WF: Shoot into the Wild Blue", "WF: Red Coins on the Floating Isle",
                          "WF: Fall onto the Caged Island", "WF: Blast Away the Wall")
    create_subregion(regWhomp, "WF: Tower", "WF: To the Top of the Fortress", "WF: Bob-omb Buddy")
    if (world.EnableCoinStars[player].value):
        create_locs(regWhomp, "WF: 100 Coins")

    regJRB = create_region("Jolly Roger Bay", player, world)
    create_locs(regJRB, "JRB: Plunder in the Sunken Ship", "JRB: Can the Eel Come Out to Play?", "JRB: Treasure of the Ocean Cave",
                        "JRB: Blast to the Stone Pillar", "JRB: Through the Jet Stream", "JRB: Bob-omb Buddy")
    jrb_upper = create_subregion(regJRB, 'JRB: Upper', "JRB: Red Coins on the Ship Afloat")
    if (world.EnableCoinStars[player].value):
        create_locs(jrb_upper, "JRB: 100 Coins")

    regCCM = create_region("Cool, Cool Mountain", player, world)
    create_default_locs(regCCM, locCCM_table)
    if (world.EnableCoinStars[player].value):
        create_locs(regCCM, "CCM: 100 Coins")

    regBBH = create_region("Big Boo's Haunt", player, world)
    create_locs(regBBH, "BBH: Go on a Ghost Hunt", "BBH: Ride Big Boo's Merry-Go-Round",
                        "BBH: Secret of the Haunted Books", "BBH: Seek the 8 Red Coins")
    bbh_third_floor = create_subregion(regBBH, "BBH: Third Floor", "BBH: Eye to Eye in the Secret Room")
    create_subregion(bbh_third_floor, "BBH: Roof", "BBH: Big Boo's Balcony", "BBH: 1Up Block Top of Mansion")
    if (world.EnableCoinStars[player].value):
        create_locs(regBBH, "BBH: 100 Coins")

    regPSS = create_region("The Princess's Secret Slide", player, world)
    create_default_locs(regPSS, locPSS_table)

    regSA = create_region("The Secret Aquarium", player, world)
    create_default_locs(regSA, locSA_table)

    regTotWC = create_region("Tower of the Wing Cap", player, world)
    create_default_locs(regTotWC, locTotWC_table)

    regBitDW = create_region("Bowser in the Dark World", player, world)
    create_default_locs(regBitDW, locBitDW_table)

    create_region("Basement", player, world)

    regHMC = create_region("Hazy Maze Cave", player, world)
    create_locs(regHMC, "HMC: Swimming Beast in the Cavern", "HMC: Metal-Head Mario Can Move!",
                        "HMC: Watch for Rolling Rocks", "HMC: Navigating the Toxic Maze","HMC: 1Up Block Past Rolling Rocks")
    hmc_red_coin_area = create_subregion(regHMC, "HMC: Red Coin Area", "HMC: Elevate for 8 Red Coins")
    create_subregion(regHMC, "HMC: Pit Islands", "HMC: A-Maze-Ing Emergency Exit", "HMC: 1Up Block above Pit")
    if (world.EnableCoinStars[player].value):
        create_locs(hmc_red_coin_area, "HMC: 100 Coins")

    regLLL = create_region("Lethal Lava Land", player, world)
    create_locs(regLLL, "LLL: Boil the Big Bully", "LLL: Bully the Bullies",
                        "LLL: 8-Coin Puzzle with 15 Pieces", "LLL: Red-Hot Log Rolling")
    create_subregion(regLLL, "LLL: Upper Volcano", "LLL: Hot-Foot-It into the Volcano", "LLL: Elevator Tour in the Volcano")
    if (world.EnableCoinStars[player].value):
        create_locs(regLLL, "LLL: 100 Coins")

    regSSL = create_region("Shifting Sand Land", player, world)
    create_locs(regSSL, "SSL: In the Talons of the Big Bird", "SSL: Shining Atop the Pyramid", "SSL: Inside the Ancient Pyramid",
                        "SSL: Free Flying for 8 Red Coins", "SSL: Bob-omb Buddy",
                        "SSL: 1Up Block Outside Pyramid", "SSL: 1Up Block Pyramid Left Path", "SSL: 1Up Block Pyramid Back")
    create_subregion(regSSL, "SSL: Upper Pyramid", "SSL: Stand Tall on the Four Pillars", "SSL: Pyramid Puzzle")
    if (world.EnableCoinStars[player].value):
        create_locs(regSSL, "SSL: 100 Coins")

    regDDD = create_region("Dire, Dire Docks", player, world)
    create_locs(regDDD, "DDD: Board Bowser's Sub", "DDD: Chests in the Current", "DDD: Through the Jet Stream",
                        "DDD: The Manta Ray's Reward", "DDD: Collect the Caps...")
    ddd_moving_poles = create_subregion(regDDD, "DDD: Moving Poles", "DDD: Pole-Jumping for Red Coins")
    if (world.EnableCoinStars[player].value):
        create_locs(ddd_moving_poles, "DDD: 100 Coins")

    regCotMC = create_region("Cavern of the Metal Cap", player, world)
    create_default_locs(regCotMC, locCotMC_table)

    regVCutM = create_region("Vanish Cap under the Moat", player, world)
    create_default_locs(regVCutM, locVCutM_table)

    regBitFS = create_region("Bowser in the Fire Sea", player, world)
    create_subregion(regBitFS, "BitFS: Upper", *locBitFS_table.keys())

    create_region("Second Floor", player, world)

    regSL = create_region("Snowman's Land", player, world)
    create_default_locs(regSL, locSL_table)
    if (world.EnableCoinStars[player].value):
        create_locs(regSL, "SL: 100 Coins")

    regWDW = create_region("Wet-Dry World", player, world)
    create_locs(regWDW, "WDW: Express Elevator--Hurry Up!")
    wdw_top = create_subregion(regWDW, "WDW: Top", "WDW: Shocking Arrow Lifts!", "WDW: Top o' the Town",
                                                   "WDW: Secrets in the Shallows & Sky", "WDW: Bob-omb Buddy")
    create_subregion(regWDW, "WDW: Downtown", "WDW: Go to Town for Red Coins", "WDW: Quick Race Through Downtown!", "WDW: 1Up Block in Downtown")
    if (world.EnableCoinStars[player].value):
        create_locs(wdw_top, "WDW: 100 Coins")

    regTTM = create_region("Tall, Tall Mountain", player, world)
    ttm_middle = create_subregion(regTTM, "TTM: Middle", "TTM: Scary 'Shrooms, Red Coins", "TTM: Blast to the Lonely Mushroom",
                                                         "TTM: Bob-omb Buddy", "TTM: 1Up Block on Red Mushroom")
    ttm_top = create_subregion(ttm_middle, "TTM: Top", "TTM: Scale the Mountain", "TTM: Mystery of the Monkey Cage",
                                                       "TTM: Mysterious Mountainside", "TTM: Breathtaking View from Bridge")
    if (world.EnableCoinStars[player].value):
        create_locs(ttm_top, "TTM: 100 Coins")

    regTHI = create_region("Tiny-Huge Island", player, world)
    create_locs(regTHI, "THI: The Tip Top of the Huge Island", "THI: 1Up Block THI Small near Start")
    thi_pipes = create_subregion(regTHI, "THI: Pipes", "THI: Pluck the Piranha Flower", "THI: Rematch with Koopa the Quick",
                                                       "THI: Five Itty Bitty Secrets", "THI: Wiggler's Red Coins", "THI: Bob-omb Buddy",
                                                       "THI: 1Up Block THI Large near Start", "THI: 1Up Block Windy Area")
    thi_large_top = create_subregion(thi_pipes, "THI: Large Top", "THI: Make Wiggler Squirm")
    if (world.EnableCoinStars[player].value):
        create_locs(thi_large_top, "THI: 100 Coins")

    regFloor3 = create_region("Third Floor", player, world)
    world.regions.append(regFloor3)

    regTTC = create_region("Tick Tock Clock", player, world)
    create_locs(regTTC, "TTC: Stop Time for Red Coins")
    ttc_lower = create_subregion(regTTC, "TTC: Lower", "TTC: Roll into the Cage", "TTC: Get a Hand", "TTC: 1Up Block Midway Up")
    ttc_upper = create_subregion(ttc_lower, "TTC: Upper", "TTC: Timed Jumps on Moving Bars", "TTC: The Pit and the Pendulums")
    ttc_top = create_subregion(ttc_upper, "TTC: Top", "TTC: Stomp on the Thwomp", "TTC: 1Up Block at the Top")
    if (world.EnableCoinStars[player].value):
        create_locs(ttc_top, "TTC: 100 Coins")

    regRR = create_region("Rainbow Ride", player, world)
    create_locs(regRR, "RR: Swingin' in the Breeze", "RR: Tricky Triangles!",
                       "RR: 1Up Block Top of Red Coin Maze", "RR: 1Up Block Under Fly Guy", "RR: Bob-omb Buddy")
    rr_maze = create_subregion(regRR, "RR: Maze", "RR: Coins Amassed in a Maze")
    create_subregion(regRR, "RR: Cruiser", "RR: Cruiser Crossing the Rainbow", "RR: Somewhere Over the Rainbow")
    create_subregion(regRR, "RR: House", "RR: The Big House in the Sky", "RR: 1Up Block On House in the Sky")
    if (world.EnableCoinStars[player].value):
        create_locs(rr_maze, "RR: 100 Coins")

    regWMotR = create_region("Wing Mario over the Rainbow", player, world)
    create_default_locs(regWMotR, locWMotR_table)

    regBitS = create_region("Bowser in the Sky", player, world)
    create_locs(regBitS, "Bowser in the Sky 1Up Block")
    create_subregion(regBitS, "BitS: Top", "Bowser in the Sky Red Coins")


def connect_regions(world: MultiWorld, player: int, source: str, target: str, rule=None):
    sourceRegion = world.get_region(source, player)
    targetRegion = world.get_region(target, player)

    connection = Entrance(player, '', sourceRegion)
    if rule:
        connection.access_rule = rule

    sourceRegion.exits.append(connection)
    connection.connect(targetRegion)


def create_region(name: str, player: int, world: MultiWorld) -> Region:
    region = Region(name, player, world)
    world.regions.append(region)
    return region


def create_subregion(source_region: Region, name: str, *locs: str) -> Region:
    region = Region(name, source_region.player, source_region.multiworld)
    connection = Entrance(source_region.player, name, source_region)
    source_region.exits.append(connection)
    connection.connect(region)
    source_region.multiworld.regions.append(region)
    create_locs(region, *locs)
    return region


def set_subregion_access_rule(world, player, region_name: str, rule):
    world.get_entrance(world, player, region_name).access_rule = rule


def create_default_locs(reg: Region, default_locs: dict):
    create_locs(reg, *default_locs.keys())


def create_locs(reg: Region, *locs: str):
    reg.locations += [SM64Location(reg.player, loc_name, location_table[loc_name], reg) for loc_name in locs]
