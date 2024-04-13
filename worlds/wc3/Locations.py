from enum import IntEnum
from typing import List, Tuple, Optional, Callable, NamedTuple, Set, Any
from BaseClasses import MultiWorld
from . import ItemNames
from .Options import get_option_value, RequiredTactics, ChecksPerVictory
from .MissionTables import WC3Mission
from .Rules import WC3Logic

from BaseClasses import Location
from worlds.AutoWorld import World

WC3_LOC_ID_OFFSET = 33333000
MAX_LOCATIONS_PER_MISSION = 100


class WC3Location(Location):
    game: str = "Starcraft2"


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

    def set_mission(self, mission: WC3Mission, mission_id: int):
        if self.mission:
            raise Exception(f'Attempted to set mission to {mission.mission_name} for already-set location {self.name}')
        self.name = mission.mission_name + ': ' + self.name
        self.code += mission_id


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
    adv_tactics = logic_level != RequiredTactics.option_standard
    if world is None:
        player = None
        location_count = ChecksPerVictory.range_end
    else:
        player = world.player
        location_count = world.options.checks_per_victory
    logic = WC3Logic(world)

    location_table: List[LocationData] = []

    def make_mission_locations(mission_id, mission: WC3Mission, victory_rule: Callable,
                               locations: List[LocationData]):
        locations = [LocationData('Victory', 0, LocationType.VICTORY, victory_rule)]
        for victory_ext in location_count:
            locations.append(LocationData('Victory', 1 + i))
    location_table: List[LocationData] = [
        # WoL
        LocationData("Liberation Day", "Liberation Day: Victory", 100, LocationType.VICTORY),
        LocationData("Liberation Day", "Liberation Day: First Statue", 101, LocationType.VANILLA),
        LocationData("Liberation Day", "Liberation Day: Second Statue", 102, LocationType.VANILLA),
        LocationData("Liberation Day", "Liberation Day: Third Statue", 103, LocationType.VANILLA),
        LocationData("Liberation Day", "Liberation Day: Fourth Statue", 104, LocationType.VANILLA),
        LocationData("Liberation Day", "Liberation Day: Fifth Statue", 105, LocationType.VANILLA),
        LocationData("Liberation Day", "Liberation Day: Sixth Statue", 106, LocationType.VANILLA),
        LocationData("Liberation Day", "Liberation Day: Special Delivery", 107, LocationType.EXTRA),
        LocationData("Liberation Day", "Liberation Day: Transport", 108, LocationType.EXTRA),
        LocationData("The Outlaws", "The Outlaws: Victory", 200, LocationType.VICTORY,
                     lambda state: logic.terran_early_tech(state)),
        LocationData("The Outlaws", "The Outlaws: Rebel Base", 201, LocationType.VANILLA,
                     lambda state: logic.terran_early_tech(state)),
        LocationData("The Outlaws", "The Outlaws: North Resource Pickups", 202, LocationType.EXTRA,
                     lambda state: logic.terran_early_tech(state)),
        LocationData("The Outlaws", "The Outlaws: Bunker", 203, LocationType.VANILLA,
                     lambda state: logic.terran_early_tech(state)),
        LocationData("The Outlaws", "The Outlaws: Close Resource Pickups", 204, LocationType.EXTRA),
        LocationData("Zero Hour", "Zero Hour: Victory", 300, LocationType.VICTORY,
                     lambda state: logic.terran_common_unit(state) and
                                   logic.terran_defense_rating(state, True) >= 2 and
                                   (adv_tactics or logic.terran_basic_anti_air(state)))
    ]

    beat_events = []
    # Filtering out excluded locations
    if world is not None:
        excluded_location_types = get_location_types(world, LocationInclusion.option_disabled)
        plando_locations = get_plando_locations(world)
        exclude_locations = get_option_value(world, "exclude_locations")
        location_table = [location for location in location_table
                          if (LocationType is LocationType.VICTORY or location.name not in exclude_locations)
                          and location.type not in excluded_location_types
                          or location.name in plando_locations]
    for i, location_data in enumerate(location_table):
        # Removing all item-based logic on No Logic
        if logic_level == RequiredTactics.option_no_logic:
            location_data = location_data._replace(rule=Location.access_rule)
            location_table[i] = location_data
        # Generating Beat event locations
        if location_data.name.endswith((": Victory", ": Defeat")):
            beat_events.append(
                location_data._replace(name="Beat " + location_data.name.rsplit(": ", 1)[0], code=None)
            )
    return tuple(location_table + beat_events)

lookup_location_id_to_type = {loc.code: loc.type for loc in get_locations(None) if loc.code is not None}