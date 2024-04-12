import inspect
from pydoc import describe

from BaseClasses import Item, ItemClassification, MultiWorld
import typing

from .Options import get_option_value, RequiredTactics
from .MissionTables import SC2Mission, WC3Race, SC2Campaign, campaign_mission_table
from . import ItemNames
from worlds.AutoWorld import World


class ItemData(typing.NamedTuple):
    code: int
    type: str
    number: int  # Important for bot commands to send the item into the game
    race: WC3Race
    classification: ItemClassification = ItemClassification.useful
    quantity: int = 1
    parent_item: typing.Optional[str] = None
    origin: typing.Set[str] = {"wol"}
    description: typing.Optional[str] = None
    important_for_filtering: bool = False

    def is_important_for_filtering(self):
        return self.important_for_filtering \
            or self.classification == ItemClassification.progression \
            or self.classification == ItemClassification.progression_skip_balancing


class WarcraftItem(Item):
    game: str = "Warcraft 3"


def get_full_item_list():
    return item_table


SC2WOL_ITEM_ID_OFFSET = 1000
SC2HOTS_ITEM_ID_OFFSET = SC2WOL_ITEM_ID_OFFSET + 1000
SC2LOTV_ITEM_ID_OFFSET = SC2HOTS_ITEM_ID_OFFSET + 1000

# Descriptions
WEAPON_ARMOR_UPGRADE_NOTE = inspect.cleandoc("""
    Must be researched during the mission if the mission type isn't set to auto-unlock generic upgrades.
""")
LASER_TARGETING_SYSTEMS_DESCRIPTION = "Increases vision by 2 and weapon range by 1."
STIMPACK_SMALL_COST = 10
STIMPACK_SMALL_HEAL = 30
STIMPACK_LARGE_COST = 20
STIMPACK_LARGE_HEAL = 60
STIMPACK_TEMPLATE = inspect.cleandoc("""
    Level 1: Stimpack: Increases unit movement and attack speed for 15 seconds. Injures the unit for {} life.
    Level 2: Super Stimpack: Instead of injuring the unit, heals the unit for {} life instead.
""")
STIMPACK_SMALL_DESCRIPTION = STIMPACK_TEMPLATE.format(STIMPACK_SMALL_COST, STIMPACK_SMALL_HEAL)
STIMPACK_LARGE_DESCRIPTION = STIMPACK_TEMPLATE.format(STIMPACK_LARGE_COST, STIMPACK_LARGE_HEAL)
SMART_SERVOS_DESCRIPTION = "Increases transformation speed between modes."
INTERNAL_TECH_MODULE_DESCRIPTION_TEMPLATE = "{} can be trained from a {} without an attached Tech Lab."
RESOURCE_EFFICIENCY_DESCRIPTION_TEMPLATE = "Reduces {} resource and supply cost."
RESOURCE_EFFICIENCY_NO_SUPPLY_DESCRIPTION_TEMPLATE = "Reduces {} resource cost."
CLOAK_DESCRIPTION_TEMPLATE = "Allows {} to use the Cloak ability."


# The items are sorted by their IDs. The IDs shall be kept for compatibility with older games.
item_table = {
    # WoL
    ItemNames.MARINE:
        ItemData(0 + SC2WOL_ITEM_ID_OFFSET, "Unit", 0, WC3Race.TERRAN,
                 classification=ItemClassification.progression,
                 description="General-purpose infantry.")
}


def get_item_table():
    return item_table


basic_units = {
    WC3Race.TERRAN: {
        ItemNames.MARINE,
        ItemNames.MARAUDER,
        ItemNames.GOLIATH,
        ItemNames.HELLION,
        ItemNames.VULTURE,
        ItemNames.WARHOUND,
    },
    WC3Race.ZERG: {
        ItemNames.ZERGLING,
        ItemNames.SWARM_QUEEN,
        ItemNames.ROACH,
        ItemNames.HYDRALISK,
    },
    WC3Race.PROTOSS: {
        ItemNames.ZEALOT,
        ItemNames.CENTURION,
        ItemNames.SENTINEL,
        ItemNames.STALKER,
        ItemNames.INSTIGATOR,
        ItemNames.SLAYER,
        ItemNames.DRAGOON,
        ItemNames.ADEPT,
    }
}

advanced_basic_units = {
    WC3Race.TERRAN: basic_units[WC3Race.TERRAN].union({
        ItemNames.REAPER,
        ItemNames.DIAMONDBACK,
        ItemNames.VIKING,
        ItemNames.SIEGE_TANK,
        ItemNames.BANSHEE,
        ItemNames.THOR,
        ItemNames.BATTLECRUISER,
        ItemNames.CYCLONE
    }),
    WC3Race.ZERG: basic_units[WC3Race.ZERG].union({
        ItemNames.INFESTOR,
        ItemNames.ABERRATION,
    }),
    WC3Race.PROTOSS: basic_units[WC3Race.PROTOSS].union({
        ItemNames.DARK_TEMPLAR,
        ItemNames.BLOOD_HUNTER,
        ItemNames.AVENGER,
        ItemNames.IMMORTAL,
        ItemNames.ANNIHILATOR,
        ItemNames.VANGUARD,
    })
}

no_logic_starting_units = {
    WC3Race.TERRAN: advanced_basic_units[WC3Race.TERRAN].union({
        ItemNames.FIREBAT,
        ItemNames.GHOST,
        ItemNames.SPECTRE,
        ItemNames.WRAITH,
        ItemNames.RAVEN,
        ItemNames.PREDATOR,
        ItemNames.LIBERATOR,
        ItemNames.HERC,
    }),
    WC3Race.ZERG: advanced_basic_units[WC3Race.ZERG].union({
        ItemNames.ULTRALISK,
        ItemNames.SWARM_HOST
    }),
    WC3Race.PROTOSS: advanced_basic_units[WC3Race.PROTOSS].union({
        ItemNames.CARRIER,
        ItemNames.TEMPEST,
        ItemNames.VOID_RAY,
        ItemNames.DESTROYER,
        ItemNames.COLOSSUS,
        ItemNames.WRATHWALKER,
        ItemNames.SCOUT,
        ItemNames.HIGH_TEMPLAR,
        ItemNames.SIGNIFIER,
        ItemNames.ASCENDANT,
        ItemNames.DARK_ARCHON,
        ItemNames.SUPPLICANT,
    })
}

not_balanced_starting_units = {
    ItemNames.SIEGE_TANK,
    ItemNames.THOR,
    ItemNames.BANSHEE,
    ItemNames.BATTLECRUISER,
    ItemNames.ULTRALISK,
    ItemNames.CARRIER,
    ItemNames.TEMPEST,
}


def get_basic_units(world: World, race: WC3Race) -> typing.Set[str]:
    logic_level = get_option_value(world, 'required_tactics')
    if logic_level == RequiredTactics.option_no_logic:
        return no_logic_starting_units[race]
    elif logic_level == RequiredTactics.option_advanced:
        return advanced_basic_units[race]
    else:
        return basic_units[race]