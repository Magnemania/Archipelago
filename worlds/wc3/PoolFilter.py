from typing import Callable, Dict, List, Set, Union, Tuple
from BaseClasses import Item, Location, ItemClassification
from .Items import get_full_item_list, HEROES
from .MissionTables import mission_orders, MissionInfo, MissionPools, WC3Campaign, WC3Race, WC3Mission, RACE_FLAGS, \
    WC3Hero
from .Options import get_option_value, MissionOrder, \
    get_enabled_campaigns, get_disabled_campaigns, RequiredTactics, get_excluded_missions, ShuffleNoBuild
from . import ItemNames
from worlds.AutoWorld import World

# Items with associated upgrades
UPGRADABLE_ITEMS = {item.parent_item for item in get_full_item_list().values() if item.parent_item}


def filter_missions(world: World) -> Dict[MissionPools, List[WC3Mission]]:

    """
    Returns a semi-randomly pruned tuple of no-build, easy, medium, and hard mission sets
    """
    world: World = world
    mission_order_type = get_option_value(world, "mission_order")
    shuffle_no_build = get_option_value(world, "shuffle_no_build")
    excluded_missions: Set[WC3Mission] = get_excluded_missions(world)
    mission_pools: Dict[MissionPools, List[WC3Mission]] = {}
    for mission in WC3Mission:
        if not mission_pools.get(mission.difficulty):
            mission_pools[mission.difficulty] = list()
        mission_pools[mission.difficulty].append(mission)
    # A bit of safeguard:
    for mission_pool in MissionPools:
        if not mission_pools.get(mission_pool):
            mission_pools[mission_pool] = []

    if mission_order_type == MissionOrder.option_vanilla:
        # TODO Decide how vanilla works in a game that is normally completely linear
        return []

    # Finding the goal map
    goal_mission = None
    for difficulty in (MissionPools.VERY_HARD, MissionPools.HARD, MissionPools.MEDIUM):
        available_missions = [mission for mission in mission_pools[difficulty] if mission not in excluded_missions]
        if available_missions:
            goal_mission = world.random.choice(available_missions)
            break
    if goal_mission is None:
        raise Exception("There are no valid goal missions. Please exclude fewer missions.")

    # Excluding missions
    for difficulty, mission_pool in mission_pools.items():
        mission_pools[difficulty] = [mission for mission in mission_pool if mission not in excluded_missions]
    mission_pools[MissionPools.FINAL] = [goal_mission]

    # Mission pool changes
    adv_tactics = get_option_value(world, "required_tactics") != RequiredTactics.option_standard

    def move_mission(mission: WC3Mission, current_pool, new_pool):
        if mission in mission_pools[current_pool]:
            mission_pools[current_pool].remove(mission)
            mission_pools[new_pool].append(mission)

    remove_final_mission_from_other_pools(mission_pools)
    return mission_pools


def remove_final_mission_from_other_pools(mission_pools: Dict[MissionPools, List[WC3Mission]]):
    final_missions = mission_pools[MissionPools.FINAL]
    for pool, missions in mission_pools.items():
        if pool == MissionPools.FINAL:
            continue
        for final_mission in final_missions:
            while final_mission in missions:
                missions.remove(final_mission)


def get_item_upgrades(inventory: List[Item], parent_item: Union[Item, str]) -> List[Item]:
    item_name = parent_item.name if isinstance(parent_item, Item) else parent_item
    return [
        inv_item for inv_item in inventory
        if get_full_item_list()[inv_item.name].parent_item == item_name
    ]


def get_item_quantity(item: Item, world: World):
    return get_full_item_list()[item.name].quantity


def copy_item(item: Item):
    return Item(item.name, item.classification, item.code, item.player)


def num_missions(world: World) -> int:
    mission_order_type = get_option_value(world, "mission_order")
    if mission_order_type != MissionOrder.option_grid:
        mission_order = mission_orders[mission_order_type]()
        missions = [mission for campaign in mission_order for mission in mission_order[campaign]]
        return len(missions) - 1  # Menu
    else:
        mission_pools = filter_missions(world)
        return sum(len(pool) for _, pool in mission_pools.items())


class ValidInventory:

    def has(self, item: str, player: int):
        return item in self.logical_inventory

    def has_any(self, items: Set[str], player: int):
        return any(item in self.logical_inventory for item in items)

    def has_all(self, items: Set[str], player: int):
        return all(item in self.logical_inventory for item in items)

    def has_group(self, item_group: str, player: int, count: int = 1):
        return len([1 for item_name in self.logical_inventory if item_name in self.item_groups[item_group]]) >= count

    def count_group(self, item_name_group: str, player: int) -> int:
        return 0  # For item filtering assume no missions are beaten

    def count(self, item: str, player: int) -> int:
        return len([inventory_item for inventory_item in self.logical_inventory if inventory_item == item])

    def generate_reduced_inventory(self, inventory_size: int, mission_requirements: List[Tuple[str, Callable]]) -> List[Item]:
        """Attempts to generate a reduced inventory that can fulfill the mission requirements."""
        inventory = list(self.item_pool)
        locked_items = list(self.locked_items)
        item_list = get_full_item_list()
        self.logical_inventory = [
            item.name for item in inventory + locked_items + self.existing_items
            if item_list[item.name].is_important_for_filtering()  # Track all Progression items and those with complex rules for filtering
        ]
        requirements = mission_requirements
        parent_items = self.item_children.keys()
        parent_lookup = {child: parent for parent, children in self.item_children.items() for child in children}

        def attempt_removal(item: Item) -> bool:
            inventory.remove(item)
            # Only run logic checks when removing logic items
            if item.name in self.logical_inventory:
                self.logical_inventory.remove(item.name)
                if not all(requirement(self) for (_, requirement) in mission_requirements):
                    # If item cannot be removed, lock or revert
                    self.logical_inventory.append(item.name)
                    for _ in range(get_item_quantity(item, self.world)):
                        locked_items.append(copy_item(item))
                    return False
            return True

        # Determining if the full-size inventory can complete campaign
        failed_locations: List[str] = [location for (location, requirement) in requirements if not requirement(self)]
        if len(failed_locations) > 0:
            raise Exception(f"Too many items excluded - couldn't satisfy access rules for the following locations:\n{failed_locations}")

        # Main cull process
        unused_items = [] # Reusable items for the second pass
        while len(inventory) + len(locked_items) > inventory_size:
            if len(inventory) == 0:
                # There are more items than locations and all of them are already locked due to YAML or logic.
                # If there still isn't enough space, push locked items into start inventory
                self.world.random.shuffle(locked_items)
                while len(locked_items) > inventory_size:
                    item: Item = locked_items.pop()
                    self.multiworld.push_precollected(item)
                break
            # Select random item from removable items
            item = self.world.random.choice(inventory)

            # Drop child items when removing a parent
            if item in parent_items:
                items_to_remove = [item for item in self.item_children[item] if item in inventory]
                success = attempt_removal(item)
                if success:
                    while len(items_to_remove) > 0:
                        item_to_remove = items_to_remove.pop()
                        if item_to_remove not in inventory:
                            continue
                        attempt_removal(item_to_remove)
            else:
                # Unimportant upgrades may be added again in the second pass
                if attempt_removal(item):
                    unused_items.append(item.name)

        # Removing extra dependencies

        # Cull finished, adding locked items back into inventory
        inventory += locked_items

        # Replacing empty space with generically useful items

        return inventory

    def __init__(self, world: World ,
                 item_pool: List[Item], existing_items: List[Item], locked_items: List[Item],
                 used_races: Set[WC3Race], used_heroes: Set[WC3Hero]):
        self.multiworld = world.multiworld
        self.player = world.player
        self.world: World = world
        self.logical_inventory = list()
        self.locked_items = locked_items[:]
        self.existing_items = existing_items
        # Initial filter of item pool
        self.item_pool = []
        item_quantities: dict[str, int] = dict()
        # Inventory restrictiveness based on number of missions with checks
        mission_count = num_missions(world)
        self.min_units_per_structure = int(mission_count / 7)
        min_upgrades = 1 if mission_count < 10 else 2
        unused_heroes = {hero for hero in HEROES if hero not in used_heroes}
        self.item_groups = {}
        for item in item_pool:
            item_info = get_full_item_list()[item.name]
            item_type = item_info.type
            if item_info.race not in used_races:
                continue
            if item_info.classification in (ItemClassification.progression, ItemClassification.progression_skip_balancing):
                if item_type not in self.item_groups:
                    self.item_groups[item_type] = {item.name}
                else:
                    self.item_groups[item_type].add(item.name)
            if item_type == "Forge":
                # Locking upgrades based on mission duration
                if item.name not in item_quantities:
                    item_quantities[item.name] = 0
                item_quantities[item.name] += 1
                if item_quantities[item.name] <= min_upgrades:
                    self.locked_items.append(item)
                else:
                    self.item_pool.append(item)
            elif item_type == "Goal":
                self.locked_items.append(item)
            elif item_info.type in unused_heroes:
                continue
            else:
                self.item_pool.append(item)
        self.item_children: Dict[Item, List[Item]] = dict()
        for item in self.item_pool + locked_items + existing_items:
            if item.name in UPGRADABLE_ITEMS:
                self.item_children[item] = get_item_upgrades(self.item_pool, item)


def filter_items(world: World, mission_req_table: Dict[WC3Campaign, Dict[str, MissionInfo]], location_cache: List[Location],
                 item_pool: List[Item], existing_items: List[Item], locked_items: List[Item]) -> List[Item]:
    """
    Returns a semi-randomly pruned set of items based on number of available locations.
    The returned inventory must be capable of logically accessing every location in the world.
    """
    open_locations = [location for location in location_cache if location.item is None]
    inventory_size = len(open_locations)
    used_races = get_used_races(mission_req_table, world)
    used_heroes = get_used_heroes(mission_req_table, world)
    mission_requirements = [(location.name, location.access_rule) for location in location_cache]
    valid_inventory = ValidInventory(world, item_pool, existing_items, locked_items, used_races, used_heroes)

    valid_items = valid_inventory.generate_reduced_inventory(inventory_size, mission_requirements)
    return valid_items


def get_used_races(mission_req_table: Dict[WC3Campaign, Dict[str, MissionInfo]], world: World) -> Set[WC3Race]:
    missions = missions_in_mission_table(mission_req_table)

    # By missions
    races = {WC3Race.ANY}
    for mission in missions:
        races.add(mission.campaign.race)
        for race, flag in RACE_FLAGS.items():
            if flag in mission.flags:
                races.add(race)
    return races


def get_used_heroes(mission_req_table: Dict[WC3Campaign, Dict[str, MissionInfo]], world: World) -> Set[WC3Race]:
    missions = missions_in_mission_table(mission_req_table)

    # By missions
    heroes = set()
    for mission in missions:
        heroes.update(mission.heroes)
    return heroes


def missions_in_mission_table(mission_req_table: Dict[WC3Campaign, Dict[str, MissionInfo]]) -> Set[WC3Mission]:
    return set([mission.mission for campaign_missions in mission_req_table.values() for mission in
                campaign_missions.values()])
