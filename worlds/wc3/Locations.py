from enum import IntEnum
from typing import List, Tuple, Optional, Callable, NamedTuple, Set, Any
from BaseClasses import MultiWorld
from . import ItemNames
from .Options import get_option_value, RequiredTactics, ChecksPerVictory
from .MissionTables import WC3Mission, MissionFlags, FLAG_RACES, MissionPools
from .Rules import WC3Logic

from BaseClasses import Location
from worlds.AutoWorld import World

WC3_LOC_ID_OFFSET = 33333000
MAX_LOCATIONS_PER_MISSION = 100

ROMAN_NUMERAL_MAP = [
    'I',
    'II',
    'III',
    'IV',
    'V',
    'VI',
    'VII',
    'VIII',
    'IX',
    'X'
]

required_ability_difficulty = {
    MissionPools.STARTER: 0,
    MissionPools.EASY: 1,
    MissionPools.MEDIUM: 2,
    MissionPools.HARD: 3,
    MissionPools.VERY_HARD: 5
}


class WC3Location(Location):
    game: str = "Warcraft 3"


class LocationType(IntEnum):
    VICTORY = 0  # Winning a mission.
    VICTORY_EXT = 1 # Additional rewards for winning a mission
    BONUS = 2  # Bonus objectives from the original campaign
    CREEP = 3  # Defeating specific creeps on the map (Replaces item rewards)


class LocationData:
    name: str
    code: Optional[int]
    type: LocationType
    rule: Callable[[Any], bool]
    mission: WC3Mission = None
    region: str = ''

    def __init__(self, name: str, code: int, location_type: LocationType, rule: Callable[[Any], bool] = Location.access_rule):
        self.name = name
        self.code = code
        if code is not None:
            self.code += WC3_LOC_ID_OFFSET
        self.type = location_type
        self.rule = rule

    def set_mission(self, mission: WC3Mission):
        self.mission = mission
        self.region = mission.mission_name


def get_plando_locations(world: World) -> List[str]:
    """

    :param world:
    :return: A list of locations affected by a plando in a world
    """
    if world is None:
        return []
    plando_locations = []
    for plando_setting in world.multiworld.plando_items[world.player]:
        plando_locations += plando_setting.get("locations", [])
        plando_setting_location = plando_setting.get("location", None)
        if plando_setting_location is not None:
            plando_locations.append(plando_setting_location)

    return plando_locations


def get_locations(world: Optional[World]) -> Tuple[LocationData, ...]:
    # Note: rules which are ended with or True are rules identified as needed later when restricted units is an option
    logic_level = get_option_value(world, 'required_tactics')
    if world is None:
        extra_victory_checks = ChecksPerVictory.range_end - 1
    else:
        extra_victory_checks = world.options.checks_per_victory
    logic = WC3Logic(world)

    def mission_locations(mission_id, mission: WC3Mission, victory_rule: Callable = None, locations: List[LocationData] = []):
        name_prefix = mission.mission_name + ':'
        races = [mission.campaign.race]
        # Default rules (Flag logic)
        if victory_rule is None:
            victory_rules = []
            hero_rules = []
            required_hero_abilities = required_ability_difficulty[mission.difficulty]
            if logic.advanced_tactics:
                required_hero_abilities -= 1
            logic_types = []
            for flag, race in FLAG_RACES.items():
                if flag in mission.flags:
                    races.append(race)
            if MissionFlags.AirEnemy in mission.flags:
                logic_types.append(logic.racial_anti_air)
            if MissionFlags.Defense in mission.flags:
                logic_types.append(logic.racial_defense)
            if MissionFlags.NoBuild in mission.flags:
                required_hero_abilities += 1
            else:
                if mission.difficulty in (MissionPools.STARTER, MissionPools.EASY):
                    logic_types.append(logic.racial_basic_unit)
                else:
                    logic_types.append(logic.racial_competent_comp)
                    if logic.racial_anti_air not in logic_types:
                        logic_types.append(logic.racial_anti_air)
            if required_hero_abilities > 0:
                for hero in mission.heroes:
                    hero_name = hero.value
                    hero_rules.append(lambda state: state.has_group(hero_name, logic.player, required_hero_abilities))
            for logic_type in logic_types:
                if len(races) == 1:
                    victory_rules.append(lambda state: logic_type[races[0]](logic, state))
                elif len(races) > 1:
                    victory_rules.append(lambda state: any([logic_type[race](logic, state) for race in races]))
            victory_rules += hero_rules
            if victory_rules:
                victory_rule = lambda state: all([rule(state) for rule in victory_rules])
            else:
                victory_rule = Location.access_rule
        victory_locations = [LocationData(f'{name_prefix} Victory', mission_id, LocationType.VICTORY, victory_rule)]
        for check in range(extra_victory_checks):
            victory_locations.append(LocationData(f'{name_prefix} Victory Cache {ROMAN_NUMERAL_MAP[check]}', mission_id + 1 + check,
                                                  LocationType.VICTORY_EXT, victory_rule))
        for location in locations:
            location.mission = mission
            location.name = f'{mission.mission}'
        all_locations = locations + victory_locations
        for location in all_locations:
            location.set_mission(mission)
        return all_locations

    location_table: List[LocationData] = [
        # Exodus of the Horde
        *mission_locations(100, WC3Mission.CHASING_VISIONS),
        *mission_locations(200, WC3Mission.DEPARTURES),
        *mission_locations(300, WC3Mission.RIDERS_ON_THE_STORM),
        *mission_locations(400, WC3Mission.THE_FIRES_DOWN_BELOW),
        *mission_locations(500, WC3Mission.COUNTDOWN_TO_EXTINCTION),
        # The Scourge of Lordaeron
        *mission_locations(600, WC3Mission.THE_DEFENSE_OF_STRAHNBRAD),
        *mission_locations(700, WC3Mission.BLACKROCK_AND_ROLL),
        *mission_locations(800, WC3Mission.RAVAGES_OF_THE_PLAGUE),
        *mission_locations(900, WC3Mission.THE_CULT_OF_THE_DAMNED),
        *mission_locations(1000, WC3Mission.MARCH_OF_THE_SCOURGE),
        *mission_locations(1100, WC3Mission.THE_CULLING),
        *mission_locations(1200, WC3Mission.THE_SHORES_OF_NORTHREND),
        *mission_locations(1300, WC3Mission.DISSENSION),
        *mission_locations(1400, WC3Mission.FROSTMOURNE),
        # Path of the Damned
        *mission_locations(1500, WC3Mission.TRUDGING_THROUGH_THE_ASHES),
        *mission_locations(1600, WC3Mission.DIGGING_UP_THE_DEAD),
        *mission_locations(1700, WC3Mission.INTO_THE_REALM_ETERNAL),
        *mission_locations(1800, WC3Mission.KEY_OF_THE_THREE_MOONS),
        *mission_locations(1900, WC3Mission.THE_FALL_OF_SILVERMOON),
        *mission_locations(2000, WC3Mission.BLACKROCK_AND_ROLL_TOO),
        *mission_locations(2100, WC3Mission.THE_SIEGE_OF_DALARAN),
        *mission_locations(2200, WC3Mission.UNDER_THE_BURNING_SKY),
        # The Invasion of Kalimdor
        *mission_locations(2300, WC3Mission.LANDFALL),
        *mission_locations(2400, WC3Mission.THE_LONG_MARCH),
        *mission_locations(2500, WC3Mission.CRY_OF_THE_WARSONG),
        *mission_locations(2600, WC3Mission.THE_SPIRITS_OF_ASHENVALE),
        *mission_locations(2700, WC3Mission.THE_HUNTER_OF_SHADOWS),
        *mission_locations(2800, WC3Mission.WHERE_WYVERNS_DARE),
        *mission_locations(2900, WC3Mission.THE_ORACLE),
        *mission_locations(3000, WC3Mission.BY_DEMONS_BE_DRIVEN),
        # Eternity's End
        *mission_locations(3100, WC3Mission.ENEMIES_AT_THE_GATE),
        *mission_locations(3200, WC3Mission.DAUGHTERS_OF_THE_MOON),
        *mission_locations(3300, WC3Mission.THE_AWAKENING_OF_STORMRAGE),
        *mission_locations(3400, WC3Mission.THE_DRUIDS_ARISE),
        *mission_locations(3500, WC3Mission.BROTHERS_IN_BLOOD),
        *mission_locations(3600, WC3Mission.A_DESTINY_OF_FLAME_AND_SORROW),
        *mission_locations(3700, WC3Mission.TWILIGHT_OF_THE_GODS),
        # Terror of the Tides
        *mission_locations(3800, WC3Mission.RISE_OF_THE_NAGA),
        *mission_locations(3900, WC3Mission.THE_BROKEN_ISLES),
        *mission_locations(4000, WC3Mission.THE_TOMB_OF_SARGERAS),
        *mission_locations(4100, WC3Mission.WRATH_OF_THE_BETRAYER),
        *mission_locations(4200, WC3Mission.BALANCING_THE_SCALES),
        *mission_locations(4300, WC3Mission.SHARDS_OF_THE_ALLIANCE),
        *mission_locations(4400, WC3Mission.THE_RUINS_OF_DALARAN),
        *mission_locations(4500, WC3Mission.THE_BROTHERS_STORMRAGE),
        # Curse of the Blood Elves
        *mission_locations(4600, WC3Mission.MISCONCEPTIONS),
        *mission_locations(4700, WC3Mission.A_DARK_COVENANT),
        *mission_locations(4800, WC3Mission.THE_DUNGEONS_OF_DALARAN),
        *mission_locations(4900, WC3Mission.THE_CROSSING),
        *mission_locations(5000, WC3Mission.THE_SEARCH_FOR_ILLIDAN),
        *mission_locations(5100, WC3Mission.GATES_OF_THE_ABYSS),
        *mission_locations(5200, WC3Mission.LORD_OF_OUTLAND),
        # Legacy of the Damned
        *mission_locations(5300, WC3Mission.KING_ARTHAS),
        *mission_locations(5400, WC3Mission.THE_FLIGHT_FROM_LORDAERON),
        *mission_locations(5500, WC3Mission.THE_DARK_LADY),
        *mission_locations(5600, WC3Mission.THE_RETURN_TO_NORTHREND),
        *mission_locations(5700, WC3Mission.DREADLORDS_FALL),
        *mission_locations(5800, WC3Mission.A_NEW_POWER_IN_LORDAERON),
        *mission_locations(5900, WC3Mission.INTO_THE_SHADOW_WEB_CAVERNS),
        *mission_locations(6000, WC3Mission.THE_FORGOTTEN_ONES),
        *mission_locations(6100, WC3Mission.ASCENT_TO_THE_UPPER_KINGDOM),
        *mission_locations(6200, WC3Mission.A_SYMPHONY_OF_FROST_AND_FLAME)
    ]

    beat_events = []
    # Filtering out excluded locations
    if world is not None:
        excluded_location_types = {}
        plando_locations = get_plando_locations(world)
        exclude_locations = get_option_value(world, "exclude_locations")
        location_table = [location for location in location_table
                          if (LocationType is LocationType.VICTORY or location.name not in exclude_locations)
                          and location.type not in excluded_location_types
                          or location.name in plando_locations]
    for location_data in location_table:
        # Removing all item-based logic on No Logic
        if logic_level == RequiredTactics.option_no_logic:
            location_data.rule = Location.access_rule
        # Generating Beat event locations
        if location_data.type == LocationType.VICTORY:
            beat_event = LocationData('Beat ' + location_data.mission.mission_name, None, None, location_data.rule)
            beat_event.set_mission(location_data.mission)
            beat_events.append(beat_event)
    return tuple(location_table + beat_events)


lookup_location_id_to_type = {loc.code: loc.type for loc in get_locations(None) if loc.code is not None}
