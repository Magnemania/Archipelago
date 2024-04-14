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
    option_blitz = 2
    option_gauntlet = 3
    option_grid = 4


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
    range_start = 1
    range_end = 10
    default = 1


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


class CasterUpgradeItems(Choice):
    """Determines how caster Adept and Master Training upgrades are split into items.
    Upgrades: Adept Training is unlocked at Level 2 Weapons and Armor and Master Training at Level 3 weapons and armor.
    By Unit: Two Progressive Caster Training items are shuffled into the pool for each caster.
    By Race: Two Progressive Caster Training items are shuffled into the pool for each race.
    Progressive Casters: Two additional copies of each caster unit are shuffled into the pool.
    Each item after the first unlocks a tier of Training for that unit.
    """
    display_name = "Caster Upgrade Items"
    option_upgrades = 0
    option_by_unit = 1
    option_by_race = 2
    option_progressive_casters = 3
    default = 1


class HeroLevels(Choice):
    """Determines how heroes gain levels.  All heroes of the same race will share their level.
    Vanilla: Heroes start each mission at their normal starting level in vanilla.
    Racial: 10 levels are shuffled into the pool for each race.
    Global: 10 levels are shuffled into the pool for all races."""
    display_name = "Hero Levels"
    option_vanilla = 0
    option_racial = 1
    option_global = 2


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
    default = 3


class ResourcesPerItem(Range):
    """
    Configures how many minerals are given per resource item.
    """
    display_name = "Resources Per Item"
    range_start = 0
    range_end = 500
    default = 25


@dataclass
class Warcraft3Options(PerGameCommonOptions):
    game_difficulty: GameDifficulty
    mission_order: MissionOrder
    maximum_campaign_size: MaximumCampaignSize
    grid_two_start_positions: GridTwoStartPositions
    enabled_campaigns: EnabledCampaigns
    shuffle_no_build: ShuffleNoBuild
    starter_cache: StarterCache
    required_tactics: RequiredTactics
    generic_upgrade_missions: GenericUpgradeMissions
    caster_upgrade_items: CasterUpgradeItems
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
    if world:
        enabled_campaigns = world.options.enabled_campaigns
        return {campaign for campaign in WC3Campaign if campaign.campaign_name in enabled_campaigns}
    else:
        return {campaign for campaign in WC3Campaign}


def get_disabled_campaigns(world: World) -> Set[WC3Campaign]:
    if world:
        enabled_campaigns = world.options.enabled_campaigns
        return {campaign for campaign in WC3Campaign if campaign.campaign_name not in enabled_campaigns}
    else:
        return {}


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
