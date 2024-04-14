import typing
from dataclasses import fields

from typing import List, Set, Iterable, Sequence, Dict, Callable, Union
from math import floor, ceil
from BaseClasses import Item, MultiWorld, Location, Tutorial, ItemClassification
from worlds.AutoWorld import WebWorld, World
from . import ItemNames
from .Items import WarcraftItem, get_item_table, get_full_item_list, \
    get_basic_units, ItemData, not_balanced_starting_units, filler_items, caster_training, progressive_casters
from .Locations import get_locations, LocationType, get_plando_locations
from .Regions import create_regions
from .Options import get_option_value, get_enabled_campaigns, Warcraft3Options, CasterUpgradeItems
from .PoolFilter import filter_items, get_item_upgrades, UPGRADABLE_ITEMS, missions_in_mission_table, get_used_races
from .MissionTables import MissionInfo, WC3Campaign, lookup_name_to_mission, WC3Mission, \
    WC3Race, MissionFlags
from .ItemGroups import item_name_groups


class Warcraft3WebWorld(WebWorld):
    setup = Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing the semi-automatic WarCraft III randomizer",
        "English",
        "setup_en.md",
        "setup/en",
        ["Magnemania"]
    )

    tutorials = [setup]


class WC3World(World):
    """
    WarCraft III is a real-time strategy video game developed and published by Blizzard Entertainment.
    Play as one of four factions across many campaigns in a battle for Azeroth.
    """

    game = "Warcraft 3"
    web = Warcraft3WebWorld()
    data_version = 1

    item_name_to_id = {name: data.code for name, data in get_full_item_list().items()}
    location_name_to_id = {location.name: location.code for location in get_locations(None)}
    options_dataclass = Warcraft3Options
    options: Warcraft3Options

    locked_locations: typing.List[str]
    location_cache: typing.List[Location]

    item_name_groups = item_name_groups
    final_mission_id: int
    victory_item: str
    required_client_version = 0, 4, 5

    def __init__(self, multiworld: MultiWorld, player: int):
        super(WC3World, self).__init__(multiworld, player)
        self.location_cache = []
        self.locked_locations = []

    def create_item(self, name: str) -> Item:
        data = get_full_item_list()[name]
        return WarcraftItem(name, data.classification, data.code, self.player)

    def create_regions(self):
        self.mission_req_table, self.final_mission_id, self.victory_item = create_regions(
            self, get_locations(self), self.location_cache
        )

    def create_items(self):
        setup_events(self.player, self.locked_locations, self.location_cache)

        excluded_items = get_excluded_items(self)

        starter_items = assign_starter_items(self, excluded_items, self.locked_locations, self.location_cache)

        # Filling locations with generic items here when appropriate setting introduced

        pool = get_item_pool(self, self.mission_req_table, starter_items, excluded_items, self.location_cache)

        fill_item_pool_with_dummy_items(self, self.locked_locations, self.location_cache, pool)

        self.multiworld.itempool += pool

    def set_rules(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has(self.victory_item, self.player)

    def get_filler_item_name(self) -> str:
        return self.random.choice(filler_items)

    def fill_slot_data(self):
        slot_data = {}
        for option_name in [field.name for field in fields(Warcraft3Options)]:
            option = get_option_value(self, option_name)
            if type(option) in {str, int}:
                slot_data[option_name] = int(option)
        slot_req_table = {}

        # Serialize data
        for campaign in self.mission_req_table:
            slot_req_table[campaign.id] = {}
            for mission in self.mission_req_table[campaign]:
                slot_req_table[campaign.id][mission] = self.mission_req_table[campaign][mission]._asdict()
                # Replace mission objects with mission IDs
                slot_req_table[campaign.id][mission]["mission"] = slot_req_table[campaign.id][mission]["mission"].id

                for index in range(len(slot_req_table[campaign.id][mission]["required_world"])):
                    # TODO this is a band-aid, sometimes the mission_req_table already contains dicts
                    # as far as I can tell it's related to having multiple vanilla mission orders
                    if not isinstance(slot_req_table[campaign.id][mission]["required_world"][index], dict):
                        slot_req_table[campaign.id][mission]["required_world"][index] = slot_req_table[campaign.id][mission]["required_world"][index]._asdict()

        slot_data["plando_locations"] = get_plando_locations(self)
        slot_data["mission_req"] = slot_req_table
        slot_data["final_mission"] = self.final_mission_id
        slot_data["version"] = 3

        return slot_data


def setup_events(player: int, locked_locations: typing.List[str], location_cache: typing.List[Location]):
    for location in location_cache:
        if location.address is None:
            item = Item(location.name, ItemClassification.progression, None, player)

            locked_locations.append(location.name)

            location.place_locked_item(item)


def get_excluded_items(world: World) -> Set[str]:
    excluded_items: Set[str] = set(get_option_value(world, 'excluded_items'))
    locked_items: Set[str] = set(get_option_value(world, 'locked_items'))
    # Starter items are also excluded items
    starter_items: Set[str] = set(get_option_value(world, 'start_inventory'))
    item_table = get_full_item_list()
    enabled_campaigns = get_enabled_campaigns(world)

    # Ensure no item is both guaranteed and excluded
    invalid_items = excluded_items.intersection(locked_items)
    invalid_count = len(invalid_items)
    # Don't count starter items that can appear multiple times
    invalid_count -= len([item for item in starter_items.intersection(locked_items) if item_table[item].quantity != 1])
    if invalid_count > 0:
        raise Exception(f"{invalid_count} item{'s are' if invalid_count > 1 else ' is'} both locked and excluded from generation.  Please adjust your excluded items and locked items.")

    def smart_exclude(item_choices: Set[str], choices_to_keep: int):
        expected_choices = len(item_choices)
        if expected_choices == 0:
            return
        item_choices = set(item_choices)
        starter_choices = item_choices.intersection(starter_items)
        excluded_choices = item_choices.intersection(excluded_items)
        item_choices.difference_update(excluded_choices)
        item_choices.difference_update(locked_items)
        candidates = sorted(item_choices)
        exclude_amount = min(expected_choices - choices_to_keep - len(excluded_choices) + len(starter_choices), len(candidates))
        if exclude_amount > 0:
            excluded_items.update(world.random.sample(candidates, exclude_amount))

    return excluded_items


def assign_starter_items(world: World, excluded_items: Set[str], locked_locations: List[str], location_cache: typing.List[Location]) -> List[Item]:
    starter_items: List[Item] = []
    non_local_items = get_option_value(world, "non_local_items")
    enabled_campaigns = get_enabled_campaigns(world)
    first_mission_name = get_first_mission(world.mission_req_table)
    first_mission = lookup_name_to_mission[first_mission_name]
    starter_cache = get_option_value(world, "starter_cache")
    # Ensuring that first mission is completable
    starter_mission_locations = [location.name for location in location_cache
                                 if location.parent_region.name == first_mission
                                 and location.access_rule == Location.access_rule]
    if not starter_mission_locations:
        # Force starting cache on missions without free locations
        starter_cache = max(starter_cache, 1)

    if MissionFlags.NoBuild in first_mission.flags:
        first_hero = first_mission.heroes[0]
        candidates = [item_name for item_name, item_data in get_item_table().items() if item_data.type == first_hero.value]
    else:
        first_race = first_mission.campaign.race
        basic_units = get_basic_units(world, first_race)
        candidates = basic_units.difference(not_balanced_starting_units)
    local_candidate = sorted(item for item in candidates if item not in non_local_items and item not in excluded_items)

    unit: Item = add_starter_item(world, excluded_items, local_candidate)
    starter_items.append(unit)

    '''Rework this into WC3 version later
    starter_abilities = get_option_value(world, 'start_primary_abilities')
    assert isinstance(starter_abilities, int)
    if starter_abilities:
        ability_count = starter_abilities
        ability_tiers = [0, 1, 3]
        world.random.shuffle(ability_tiers)
        if ability_count > 3:
            ability_tiers.append(6)
        for tier in ability_tiers:
            abilities = kerrigan_actives[tier].union(kerrigan_passives[tier]).difference(excluded_items, non_local_items)
            if not abilities:
                abilities = kerrigan_actives[tier].union(kerrigan_passives[tier]).difference(excluded_items)
            if abilities:
                ability_count -= 1
                starter_items.append(add_starter_item(world, excluded_items, list(abilities)))
                if ability_count == 0:
                    break
    '''

    return starter_items


def get_first_mission(mission_req_table: Dict[WC3Campaign, Dict[str, MissionInfo]]) -> str:
    # The first world should also be the starting world
    campaigns = mission_req_table.keys()
    lowest_id = min([campaign.id for campaign in campaigns])
    first_campaign = [campaign for campaign in campaigns if campaign.id == lowest_id][0]
    first_mission = list(mission_req_table[first_campaign])[0]
    return first_mission


def add_starter_item(world: World, excluded_items: Set[str], item_list: Sequence[str]) -> Item:

    item_name = world.random.choice(sorted(item_list))

    item = create_item_with_correct_settings(world.player, item_name)

    world.multiworld.push_precollected(item)

    return item


def get_item_pool(world: World, mission_req_table: Dict[WC3Campaign, Dict[str, MissionInfo]],
                  starter_items: List[Item], excluded_items: Set[str], location_cache: List[Location]) -> List[Item]:
    pool: List[Item] = []

    # For the future: goal items like Artifact Shards go here
    locked_items = []

    # YAML items
    yaml_locked_items = get_option_value(world, 'locked_items')
    assert not isinstance(yaml_locked_items, int)

    # Adjust generic upgrade availability based on options
    override_quantity = dict()
    include_upgrades = get_option_value(world, 'generic_upgrade_missions') == 0
    caster_upgrade_items = get_option_value(world, 'caster_upgrade_items')
    valid_caster_upgrades = caster_training[caster_upgrade_items]
    if caster_training == CasterUpgradeItems.option_progressive_casters:
        override_quantity.update({caster: 3 for caster in progressive_casters})
    for item in starter_items:
        if item.name not in override_quantity:
            override_quantity[item.name] = get_item_table()[item.name].quantity - 1
        else:
            override_quantity[item.name] -= 1

    def allowed_quantity(name: str, data: ItemData) -> int:
        if name in excluded_items \
                or data.type == "Upgrade" and (not include_upgrades) \
                or data.type == "Caster Training" and name not in valid_caster_upgrades:
            return 0
        else:
            return override_quantity.get(name, data.quantity)

    for name, data in get_item_table().items():
        for _ in range(allowed_quantity(name, data)):
            item = create_item_with_correct_settings(world.player, name)
            if name in yaml_locked_items:
                locked_items.append(item)
            else:
                pool.append(item)

    existing_items = starter_items + [item for item in world.multiworld.precollected_items[world.player] if item not in starter_items]
    existing_names = [item.name for item in existing_items]

    # Check the parent item integrity, exclude items
    pool[:] = [item for item in pool if pool_contains_parent(item, pool + locked_items + existing_items)]

    # Removing upgrades for excluded items
    for item_name in excluded_items:
        if item_name in existing_names:
            continue
        invalid_upgrades = get_item_upgrades(pool, item_name)
        for invalid_upgrade in invalid_upgrades:
            pool.remove(invalid_upgrade)

    filtered_pool = filter_items(world, mission_req_table, location_cache, pool, existing_items, locked_items)
    return filtered_pool


def fill_item_pool_with_dummy_items(self: WC3World, locked_locations: List[str],
                                    location_cache: List[Location], pool: List[Item]):
    for _ in range(len(location_cache) - len(locked_locations) - len(pool)):
        item = create_item_with_correct_settings(self.player, self.get_filler_item_name())
        pool.append(item)


def create_item_with_correct_settings(player: int, name: str) -> Item:
    data = get_full_item_list()[name]

    item = Item(name, data.classification, data.code, player)

    return item


def pool_contains_parent(item: Item, pool: Iterable[Item]):
    item_data = get_full_item_list().get(item.name)
    if item_data.parent_item is None:
        # The item has not associated parent, the item is valid
        return True
    parent_item = item_data.parent_item
    # Check if the pool contains the parent item
    return parent_item in [pool_item.name for pool_item in pool]


def place_exclusion_item(item_name, location, locked_locations, player):
    item = create_item_with_correct_settings(player, item_name)
    location.place_locked_item(item)
    locked_locations.append(location.name)