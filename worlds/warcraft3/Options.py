from dataclasses import dataclass, fields, Field
from typing import FrozenSet, Union, Set

from Options import Choice, Toggle, DefaultOnToggle, ItemSet, OptionSet, Range, PerGameCommonOptions
from .MissionTables import WC3Campaign, WC3Mission, lookup_name_to_mission, get_no_build_missions, campaign_mission_table
from worlds.AutoWorld import World


class GameDifficulty(Choice):
    """
    The difficulty of the campaign, affects enemy AI, starting units, and game speed.

    For those unfamiliar with the Archipelago randomizer, the recommended settings are one difficulty level
    lower than the vanilla game
    """
    display_name = "Game Difficulty"
    option_casual = 0
    option_normal = 1
    option_hard = 2
    option_brutal = 3
    default = 1


class MissionOrder(Choice):
    """
    Determines the order the missions are played in.  The last three mission orders end in a random mission.
    Vanilla (83 total if all campaigns enabled): Keeps the standard mission order and branching from the vanilla Campaigns.
    Vanilla Shuffled (83 total if all campaigns enabled): Keeps same branching paths from the vanilla Campaigns but randomizes the order of missions within.
    Mini Campaign (47 total if all campaigns enabled): Shorter version of the campaign with randomized missions and optional branches.
    Medium Grid (16):  A 4x4 grid of random missions.  Start at the top-left and forge a path towards bottom-right mission to win.
    Mini Grid (9):  A 3x3 version of Grid.  Complete the bottom-right mission to win.
    Blitz (12):  12 random missions that open up very quickly.  Complete the bottom-right mission to win.
    Gauntlet (7): Linear series of 7 random missions to complete the campaign.
    Mini Gauntlet (4): Linear series of 4 random missions to complete the campaign.
    Tiny Grid (4): A 2x2 version of Grid.  Complete the bottom-right mission to win.
    Grid (variable): A grid that will resize to use all non-excluded missions.  Corners may be omitted to make the grid more square.  Complete the bottom-right mission to win.
    """
    display_name = "Mission Order"
    option_vanilla = 0
    option_vanilla_shuffled = 1
    option_mini_campaign = 2
    option_medium_grid = 3
    option_mini_grid = 4
    option_blitz = 5
    option_gauntlet = 6
    option_mini_gauntlet = 7
    option_tiny_grid = 8
    option_grid = 9


class MaximumCampaignSize(Range):
    """
    Sets an upper bound on how many missions to include when a variable-size mission order is selected.
    If a set-size mission order is selected, does nothing.
    """
    display_name = "Maximum Campaign Size"
    range_start = 1
    range_end = 83
    default = 83


class GridTwoStartPositions(Toggle):
    """
    If turned on and 'grid' mission order is selected, removes a mission from the starting
    corner sets the adjacent two missions as the starter missions.
    """
    display_name = "Start with two unlocked missions on grid"
    default = Toggle.option_false


class EnabledCampaigns(OptionSet):
    """
    Which campaigns exist in the randomizer
    """
    display_name = "Enabled Campaigns"
    valid_keys = {campaign.campaign_name for campaign in WC3Campaign}
    default = {WC3Campaign.HUMAN.campaign_name}


class ShuffleNoBuild(DefaultOnToggle):
    """
    Determines if the no-build missions are included in the shuffle.
    If turned off, the no-build missions will not appear. Has no effect for Vanilla mission order.
    """
    display_name = "Shuffle No-Build Missions"


class StarterCache(Range):
    """
    How many items are given for free at the start of a game.
    If the campaign is forced to start with a harder mission,
    this option will be forced higher.
    """
    display_name = "Starter Cache"
    range_start = 0
    range_end = 10
    default = 0


class RequiredTactics(Choice):
    """
    Determines the maximum tactical difficulty of the world (separate from mission difficulty).  Higher settings
    increase randomness.

    Standard:  All missions can be completed with good micro and macro.
    Advanced:  Completing missions may require relying on starting units and micro-heavy units.
    No Logic:  Units and upgrades may be placed anywhere.  LIKELY TO RENDER THE RUN IMPOSSIBLE ON HARDER DIFFICULTIES!
               Locks Grant Story Tech option to true.
    """
    display_name = "Required Tactics"
    option_standard = 0
    option_advanced = 1
    option_no_logic = 2


class GenericUpgradeMissions(Range):
    """Determines the percentage of missions in the mission order that must be completed before
    level 1 of all weapon and armor upgrades is unlocked.  Level 2 upgrades require double the amount of missions,
    and level 3 requires triple the amount.  The required amounts are always rounded down.
    If set to 0, upgrades are instead added to the item pool and must be found to be used."""
    display_name = "Generic Upgrade Missions"
    range_start = 0
    range_end = 100
    default = 0


class GenericUpgradeItems(Choice):
    """Determines how weapon and armor upgrades are split into items.  All options produce 3 levels of each item.
    Does nothing if upgrades are unlocked by completed mission counts.

    Individual Items:  All weapon and armor upgrades are each an item,
    resulting in 18 total upgrade items for Terran and 15 total items for Zerg and Protoss each.
    Bundle Weapon And Armor:  All types of weapon upgrades are one item per race,
    and all types of armor upgrades are one item per race,
    resulting in 18 total items.
    Bundle Unit Class:  Weapon and armor upgrades are merged,
    but upgrades are bundled separately for each race:
    Infantry, Vehicle, and Starship upgrades for Terran (9 items),
    Ground and Flyer upgrades for Zerg (6 items),
    Ground and Air upgrades for Protoss (6 items),
    resulting in 21 total items.
    Bundle All:  All weapon and armor upgrades are one item per race,
    resulting in 9 total items."""
    display_name = "Generic Upgrade Items"
    option_individual_items = 0
    option_bundle_weapon_and_armor = 1
    option_bundle_unit_class = 2
    option_bundle_all = 3


class EnsureGenericItems(Range):
    """
    Specifies a minimum percentage of the generic item pool that will be present for the slot.
    The generic item pool is the pool of all generically useful items after all exclusions.
    Generically-useful items include: Worker upgrades, Building upgrades, economy upgrades,
    Mercenaries, Kerrigan levels and abilities, and Spear of Adun abilities
    Increasing this percentage will make units less common.
    """
    display_name = "Ensure Generic Items"
    range_start = 0
    range_end = 100
    default = 25


class LockedItems(ItemSet):
    """Guarantees that these items will be unlockable"""
    display_name = "Locked Items"


class ExcludedItems(ItemSet):
    """Guarantees that these items will not be unlockable"""
    display_name = "Excluded Items"


class ExcludedMissions(OptionSet):
    """Guarantees that these missions will not appear in the campaign
    Doesn't apply to vanilla mission order.
    It may be impossible to build a valid campaign if too many missions are excluded."""
    display_name = "Excluded Missions"
    valid_keys = {mission.mission_name for mission in WC3Mission}


class ChecksPerVictory(Range):
    """How many checks the player gains for completing a mission"""
    display_name = "Checks Per Victory"
    range_start = 1
    range_end = 10


class ResourcesPerItem(Range):
    """
    Configures how many minerals are given per resource item.
    """
    display_name = "Minerals Per Item"
    range_start = 0
    range_end = 500
    default = 25


@dataclass
class Warcraft3Options(PerGameCommonOptions):
    game_difficulty: GameDifficulty
    mission_order: MissionOrder
    maximum_campaign_size: MaximumCampaignSize
    grid_two_start_positions: GridTwoStartPositions
    shuffle_no_build: ShuffleNoBuild
    starter_cache: StarterCache
    required_tactics: RequiredTactics
    ensure_generic_items: EnsureGenericItems
    generic_upgrade_missions: GenericUpgradeMissions
    generic_upgrade_items: GenericUpgradeItems
    locked_items: LockedItems
    excluded_items: ExcludedItems
    excluded_missions: ExcludedMissions
    checks_per_victory: ChecksPerVictory
    resources_per_item: ResourcesPerItem


def get_option_value(world: World, name: str) -> Union[int,  FrozenSet]:
    if world is None:
        field: Field = [class_field for class_field in fields(Warcraft3Options) if class_field.name == name][0]
        return field.type.default

    player_option = getattr(world.options, name)

    return player_option.value


def get_enabled_campaigns(world: World) -> Set[WC3Campaign]:
    enabled_campaigns = get_option_value(world, "enabled_campaigns")
    return {campaign for campaign in WC3Campaign if campaign.campaign_name in enabled_campaigns}


def get_disabled_campaigns(world: World) -> Set[WC3Campaign]:
    enabled_campaigns = get_option_value(world, "enabled_campaigns")
    return {campaign for campaign in WC3Campaign if campaign.campaign_name not in enabled_campaigns}


def get_excluded_missions(world: World) -> Set[WC3Mission]:
    excluded_mission_names = get_option_value(world, "excluded_missions")
    shuffle_no_build = get_option_value(world, "shuffle_no_build")
    disabled_campaigns = get_disabled_campaigns(world)

    excluded_missions: Set[WC3Mission] = set([lookup_name_to_mission[name] for name in excluded_mission_names])

    # Omitting No-Build missions if not shuffling no-build
    if not shuffle_no_build:
        excluded_missions = excluded_missions.union(get_no_build_missions())
    # Omitting missions not in enabled campaigns
    for campaign in disabled_campaigns:
        excluded_missions = excluded_missions.union(campaign_mission_table[campaign])

    return excluded_missions
