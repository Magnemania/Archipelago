from BaseClasses import Item, ItemClassification, MultiWorld
import typing

from .Options import get_option_value, RequiredTactics
from .MissionTables import WC3Mission, WC3Race, WC3Campaign, campaign_mission_table
from . import ItemNames
from worlds.AutoWorld import World

WC3_ITEM_ID_OFFSET = 33333000


DEFAULT_CLASSIFICATION = {
    "Unit": ItemClassification.progression,
    "Building": ItemClassification.progression,
    "Level": ItemClassification.progression,
    "Forge": ItemClassification.progression,
    "Upgrade": ItemClassification.useful,
    "Caster Training": ItemClassification.useful,
    "Inventory": ItemClassification.filler,
    "Filler": ItemClassification.filler
}

HEROES = [
    'Paladin',
    'Archmage',
    'Mountain King',
    'Blood Mage',
    'Far Seer',
    'Blademaster',
    'Tauren Chieftain',
    'Shadow Hunter',
    'Death Knight',
    'Lich',
    'Dreadlord',
    'Crypt Lord',
    'Dark Ranger',
    'Priestess of the Moon',
    'Keeper of the Grove',
    'Demon Hunter',
    'Warden',
    'Naga Sea Witch'
]
DEFAULT_CLASSIFICATION.update({hero: ItemClassification.progression for hero in HEROES})


class ItemData:
    code: int
    number: int
    race: WC3Race
    type: str
    classification: ItemClassification = ItemClassification.useful
    quantity: int = 1
    parent_item: typing.Optional[str] = None
    description: typing.Optional[str] = None
    important_for_filtering: bool = False

    def is_important_for_filtering(self):
        return self.important_for_filtering \
               or self.classification == ItemClassification.progression \
               or self.classification == ItemClassification.progression_skip_balancing

    def __init__(self, number: int, item_type: str, race: WC3Race, classification: ItemClassification = None,
                 quantity: int = 1, parent_item: str = None, description: str = '', important_for_filtering: bool = False):
        if classification is None:
            classification = DEFAULT_CLASSIFICATION[item_type]
        self.code = number + WC3_ITEM_ID_OFFSET
        self.race = race
        self.type = item_type
        self.classification = classification
        self.quantity = quantity
        self.parent_item = parent_item
        self.description = description
        self.important_for_filtering = important_for_filtering

class WarcraftItem(Item):
    game: str = "Warcraft 3"

def get_full_item_list():
    return item_table


item_table = {
    # Human
    ItemNames.FOOTMAN: ItemData(0, "Unit", WC3Race.HUMAN),
    ItemNames.RIFLEMAN: ItemData(1, "Unit", WC3Race.HUMAN),
    ItemNames.KNIGHT: ItemData(2, "Unit", WC3Race.HUMAN),
    ItemNames.PRIEST: ItemData(3, "Unit", WC3Race.HUMAN),
    ItemNames.SORCERESS: ItemData(4, "Unit", WC3Race.HUMAN),
    ItemNames.SPELL_BREAKER: ItemData(5, "Unit", WC3Race.HUMAN),
    ItemNames.FLYING_MACHINE: ItemData(6, "Unit", WC3Race.HUMAN),
    ItemNames.MORTAR_TEAM: ItemData(7, "Unit", WC3Race.HUMAN),
    ItemNames.SIEGE_ENGINE: ItemData(8, "Unit", WC3Race.HUMAN),
    ItemNames.DRAGONHAWK_RIDER: ItemData(9, "Unit", WC3Race.HUMAN),
    ItemNames.GRYPHON_RIDER: ItemData(10, "Unit", WC3Race.HUMAN),
    ItemNames.ARCANE_VAULT: ItemData(11, "Building", WC3Race.HUMAN),
    ItemNames.GUARD_TOWER: ItemData(12, "Building", WC3Race.HUMAN),
    ItemNames.ARCANE_TOWER: ItemData(13, "Building", WC3Race.HUMAN),
    ItemNames.CANNON_TOWER: ItemData(14, "Building", WC3Race.HUMAN),
    ItemNames.HUMAN_UPGRADES: ItemData(15, "Forge", WC3Race.HUMAN, quantity=3),
    ItemNames.PEASANT_CALL_TO_ARMS: ItemData(16, "Upgrade", WC3Race.HUMAN),
    ItemNames.PROGRESSIVE_MASONRY: ItemData(17, "Upgrade", WC3Race.HUMAN, quantity=2),
    ItemNames.FOOTMAN_DEFEND: ItemData(18, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.FOOTMAN),
    ItemNames.RIFLEMAN_LONG_RIFLES: ItemData(19, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.RIFLEMAN),
    ItemNames.KNIGHT_ANIMAL_WAR_TRAINING: ItemData(20, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.KNIGHT),
    ItemNames.PROGRESSIVE_PRIEST_TRAINING: ItemData(21, "Caster Training", WC3Race.HUMAN, quantity=2),
    ItemNames.PROGRESSIVE_SORCERESS_TRAINING: ItemData(22, "Caster Training", WC3Race.HUMAN, quantity=2),
    ItemNames.PROGRESSIVE_HUMAN_CASTER_TRAINING: ItemData(23, "Caster Training", WC3Race.HUMAN, quantity=2),
    ItemNames.SPELL_BREAKER_CONTROL_MAGIC: ItemData(24, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.SPELL_BREAKER),
    ItemNames.FLYING_MACHINE_FLAK_CANNONS: ItemData(25, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.FLYING_MACHINE),
    ItemNames.FLYING_MACHINE_BOMBS: ItemData(26, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.FLYING_MACHINE),
    ItemNames.MORTAR_TEAM_FLARE: ItemData(27, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.MORTAR_TEAM,
                                          classification=ItemClassification.filler),
    ItemNames.MORTAR_TEAM_FRAGMENTATION_SHARDS: ItemData(28, "Upgrade", WC3Race.HUMAN,
                                                         parent_item=ItemNames.MORTAR_TEAM),
    ItemNames.SIEGE_ENGINE_BARRAGE: ItemData(29, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.SIEGE_ENGINE,
                                         classification=ItemClassification.progression),
    ItemNames.DRAGONHAWK_RIDER_CLOUD: ItemData(30, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.DRAGONHAWK_RIDER),
    ItemNames.GRYPHON_RIDER_STORM_HAMMERS: ItemData(31, "Upgrade", WC3Race.HUMAN, parent_item=ItemNames.GRYPHON_RIDER),
    ItemNames.MAGIC_SENTRY: ItemData(32, "Upgrade", WC3Race.HUMAN, classification=ItemClassification.filler),
    ItemNames.HUMAN_LEVEL: ItemData(33, "Level", WC3Race.HUMAN),
    ItemNames.HOLY_LIGHT: ItemData(34, "Paladin", WC3Race.HUMAN, quantity=3),
    ItemNames.DIVINE_SHIELD: ItemData(35, "Paladin", WC3Race.HUMAN, quantity=3),
    ItemNames.DEVOTION_AURA: ItemData(36, "Paladin", WC3Race.HUMAN, quantity=3),
    ItemNames.RESURRECTION: ItemData(37, "Paladin", WC3Race.HUMAN),
    ItemNames.BLIZZARD: ItemData(38, "Archmage", WC3Race.HUMAN, quantity=3),
    ItemNames.SUMMON_WATER_ELEMENTAL: ItemData(39, "Archmage", WC3Race.HUMAN, quantity=3),
    ItemNames.BRILLIANCE_AURA: ItemData(40, "Archmage", WC3Race.HUMAN, quantity=3),
    ItemNames.MASS_TELEPORT: ItemData(41, "Archmage", WC3Race.HUMAN),
    ItemNames.STORM_BOLT: ItemData(42, "Mountain King", WC3Race.HUMAN, quantity=3),
    ItemNames.THUNDER_CLAP: ItemData(43, "Mountain King", WC3Race.HUMAN, quantity=3),
    ItemNames.BASH: ItemData(44, "Mountain King", WC3Race.HUMAN, quantity=3),
    ItemNames.AVATAR: ItemData(45, "Mountain King", WC3Race.HUMAN),
    ItemNames.FLAME_STRIKE: ItemData(46, "Blood Mage", WC3Race.HUMAN, quantity=3),
    ItemNames.BANISH: ItemData(47, "Blood Mage", WC3Race.HUMAN, quantity=3),
    ItemNames.SIPHON_MANA: ItemData(48, "Blood Mage", WC3Race.HUMAN, quantity=3),
    ItemNames.PHOENIX: ItemData(49, "Blood Mage", WC3Race.HUMAN),
    # Orc
    ItemNames.GRUNT: ItemData(50, "Unit", WC3Race.ORC),
    ItemNames.HEADHUNTER: ItemData(51, "Unit", WC3Race.ORC),
    ItemNames.DEMOLISHER: ItemData(52, "Unit", WC3Race.ORC),
    ItemNames.SHAMAN: ItemData(53, "Unit", WC3Race.ORC),
    ItemNames.WITCH_DOCTOR: ItemData(54, "Unit", WC3Race.ORC),
    ItemNames.SPIRIT_WALKER: ItemData(55, "Unit", WC3Race.ORC),
    ItemNames.RAIDER: ItemData(56, "Unit", WC3Race.ORC),
    ItemNames.WIND_RIDER: ItemData(57, "Unit", WC3Race.ORC),
    ItemNames.KODO_BEAST: ItemData(58, "Unit", WC3Race.ORC),
    ItemNames.BATRIDER: ItemData(59, "Unit", WC3Race.ORC),
    ItemNames.TAUREN: ItemData(60, "Unit", WC3Race.ORC),
    ItemNames.WATCH_TOWER: ItemData(61, "Building", WC3Race.ORC),
    ItemNames.VOODOO_LOUNGE: ItemData(62, "Building", WC3Race.ORC),
    ItemNames.ORC_UPGRADES: ItemData(63, "Forge", WC3Race.ORC, quantity=3),
    ItemNames.PEON_BATTLE_STATIONS: ItemData(64, "Upgrade", WC3Race.ORC),
    ItemNames.PROGRESSIVE_SPIKED_BARRICADES: ItemData(65, "Upgrade", WC3Race.ORC, quantity=2,
                                                      classification=ItemClassification.filler),
    ItemNames.REINFORCED_DEFENSES: ItemData(66, "Upgrade", WC3Race.ORC),
    ItemNames.PILLAGE: ItemData(67, "Upgrade", WC3Race.ORC),
    ItemNames.GRUNT_BRUTE_STRENGTH: ItemData(68, "Upgrade", WC3Race.ORC, parent_item=ItemNames.GRUNT,
                                         classification=ItemClassification.progression),
    ItemNames.HEADHUNTER_BERSERKER_UPGRADE: ItemData(69, "Upgrade", WC3Race.ORC, parent_item=ItemNames.HEADHUNTER),
    ItemNames.DEMOLISHER_BURNING_OIL: ItemData(70, "Upgrade", WC3Race.ORC, parent_item=ItemNames.DEMOLISHER),
    ItemNames.PROGRESSIVE_SHAMAN_TRAINING: ItemData(71, "Caster Training", WC3Race.ORC, quantity=2),
    ItemNames.PROGRESSIVE_WITCH_DOCTOR_TRAINING: ItemData(72, "Caster Training", WC3Race.ORC, quantity=2),
    ItemNames.PROGRESSIVE_ORC_CASTER_TRAINING: ItemData(73, "Caster Training", WC3Race.ORC, quantity=2),
    ItemNames.SPIRIT_WALKER_ANCESTRAL_SPIRIT: ItemData(74, "Upgrade", WC3Race.ORC, parent_item=ItemNames.SPIRIT_WALKER),
    ItemNames.RAIDER_ENSNARE: ItemData(75, "Upgrade", WC3Race.ORC, parent_item=ItemNames.RAIDER,
                                         classification=ItemClassification.progression),
    ItemNames.WIND_RIDER_ENVENOMED_SPEARS: ItemData(76, "Upgrade", WC3Race.ORC, parent_item=ItemNames.WIND_RIDER),
    ItemNames.KODO_BEAST_WAR_DRUMS: ItemData(77, "Upgrade", WC3Race.ORC, parent_item=ItemNames.KODO_BEAST),
    ItemNames.BATRIDER_LIQUID_FIRE: ItemData(78, "Upgrade", WC3Race.ORC, parent_item=ItemNames.BATRIDER,
                                         classification=ItemClassification.progression),
    ItemNames.TAUREN_PULVERIZE: ItemData(79, "Upgrade", WC3Race.ORC, parent_item=ItemNames.TAUREN),
    ItemNames.TROLL_REGENERATION: ItemData(80, "Upgrade", WC3Race.ORC),
    ItemNames.ORC_LEVEL: ItemData(81, "Level", WC3Race.ORC),
    ItemNames.CHAIN_LIGHTNING: ItemData(82, "Far Seer", WC3Race.ORC, quantity=3),
    ItemNames.FAR_SIGHT: ItemData(83, "Far Seer", WC3Race.ORC, quantity=3, classification=ItemClassification.filler),
    ItemNames.FERAL_SPIRIT: ItemData(84, "Far Seer", WC3Race.ORC, quantity=3),
    ItemNames.EARTHQUAKE: ItemData(85, "Far Seer", WC3Race.ORC),
    ItemNames.WIND_WALK: ItemData(86, "Blademaster", WC3Race.ORC, quantity=3),
    ItemNames.MIRROR_IMAGE: ItemData(87, "Blademaster", WC3Race.ORC, quantity=3),
    ItemNames.CRITICAL_STRIKE: ItemData(88, "Blademaster", WC3Race.ORC, quantity=3),
    ItemNames.BLADESTORM: ItemData(89, "Blademaster", WC3Race.ORC),
    ItemNames.SHOCKWAVE: ItemData(90, "Tauren Chieftain", WC3Race.ORC, quantity=3),
    ItemNames.WAR_STOMP: ItemData(91, "Tauren Chieftain", WC3Race.ORC),
    ItemNames.ENDURANCE_AURA: ItemData(92, "Tauren Chieftain", WC3Race.ORC),
    ItemNames.REINCARNATION: ItemData(93, "Tauren Chieftain", WC3Race.ORC),
    ItemNames.HEALING_WAVE: ItemData(94, "Shadow Hunter", WC3Race.ORC),
    ItemNames.HEX: ItemData(95, "Shadow Hunter", WC3Race.ORC),
    ItemNames.SERPENT_WARD: ItemData(96, "Shadow Hunter", WC3Race.ORC),
    ItemNames.BIG_BAD_VOODOO: ItemData(97, "Shadow Hunter", WC3Race.ORC),
    # Undead
    ItemNames.GHOUL: ItemData(98, "Unit", WC3Race.UNDEAD),
    ItemNames.CRYPT_FIEND: ItemData(99, "Unit", WC3Race.UNDEAD),
    ItemNames.GARGOYLE: ItemData(100, "Unit", WC3Race.UNDEAD),
    ItemNames.NECROMANCER: ItemData(101, "Unit", WC3Race.UNDEAD),
    ItemNames.BANSHEE: ItemData(102, "Unit", WC3Race.UNDEAD),
    ItemNames.MEAT_WAGON: ItemData(103, "Unit", WC3Race.UNDEAD),
    ItemNames.OBSIDIAN_STATUE: ItemData(104, "Unit", WC3Race.UNDEAD),
    ItemNames.ABOMINATION: ItemData(105, "Unit", WC3Race.UNDEAD),
    ItemNames.SHADE: ItemData(106, "Unit", WC3Race.UNDEAD),
    ItemNames.FROST_WYRM: ItemData(107, "Unit", WC3Race.UNDEAD),
    ItemNames.SPIRIT_TOWER: ItemData(108, "Building", WC3Race.UNDEAD),
    ItemNames.NERUBIAN_TOWER: ItemData(109, "Building", WC3Race.UNDEAD),
    ItemNames.TOMB_OF_RELICS: ItemData(110, "Building", WC3Race.UNDEAD),
    ItemNames.UNDEAD_UPGRADES: ItemData(111, "Forge", WC3Race.UNDEAD),
    ItemNames.ACOLYTE_UNSUMMON: ItemData(112, "Upgrade", WC3Race.UNDEAD),
    ItemNames.GHOUL_FRENZY: ItemData(113, "Upgrade", WC3Race.UNDEAD, parent_item=ItemNames.GHOUL,
                                     classification=ItemClassification.progression),
    ItemNames.CRYPT_FIEND_BURROW: ItemData(114, "Upgrade", WC3Race.UNDEAD, parent_item=ItemNames.CRYPT_FIEND),
    ItemNames.GARGOYLE_STONE_FORM: ItemData(115, "Upgrade", WC3Race.UNDEAD, parent_item=ItemNames.GARGOYLE),
    ItemNames.PROGRESSIVE_NECROMANCER_TRAINING: ItemData(116, "Caster Training", WC3Race.UNDEAD, quantity=2),
    ItemNames.PROGRESSIVE_BANSHEE_TRAINING: ItemData(117, "Caster Training", WC3Race.UNDEAD, quantity=2),
    ItemNames.PROGRESSIVE_UNDEAD_CASTER_TRAINING: ItemData(118, "Caster Training", WC3Race.UNDEAD, quantity=2),
    ItemNames.NECROMANCER_SKELETAL_MASTERY: ItemData(119, "Upgrade", WC3Race.UNDEAD, parent_item=ItemNames.NECROMANCER),
    ItemNames.MEAT_WAGON_EXHUME_CORPSES: ItemData(120, "Upgrade", WC3Race.UNDEAD, parent_item=ItemNames.MEAT_WAGON),
    ItemNames.OBSIDIAN_STATUE_DESTROYER_FORM: ItemData(121, "Upgrade", WC3Race.UNDEAD,
                                                       parent_item=ItemNames.OBSIDIAN_STATUE),
    ItemNames.FROST_WYRM_FREEZING_BREATH: ItemData(122, "Upgrade", WC3Race.UNDEAD, parent_item=ItemNames.FROST_WYRM,
                                         classification=ItemClassification.progression),
    ItemNames.CANNIBALIZE: ItemData(123, "Upgrade", WC3Race.UNDEAD),
    ItemNames.DISEASE_CLOUD: ItemData(124, "Upgrade", WC3Race.UNDEAD),
    ItemNames.DEATH_COIL: ItemData(125, "Death Knight", WC3Race.UNDEAD),
    ItemNames.DEATH_PACT: ItemData(126, "Death Knight", WC3Race.UNDEAD),
    ItemNames.UNHOLY_AURA: ItemData(127, "Death Knight", WC3Race.UNDEAD),
    ItemNames.REANIMATE_DEAD: ItemData(128, "Death Knight", WC3Race.UNDEAD),
    ItemNames.FROST_NOVA: ItemData(129, "Lich", WC3Race.UNDEAD),
    ItemNames.DARK_RITUAL: ItemData(130, "Lich", WC3Race.UNDEAD, classification=ItemClassification.useful),
    ItemNames.DEATH_AND_DECAY: ItemData(131, "Lich", WC3Race.UNDEAD),
    ItemNames.CARRION_SWARM: ItemData(132, "Dreadlord", WC3Race.UNDEAD),
    ItemNames.SLEEP: ItemData(133, "Dreadlord", WC3Race.UNDEAD),
    ItemNames.VAMPIRIC_AURA: ItemData(134, "Dreadlord", WC3Race.UNDEAD),
    ItemNames.INFERNO: ItemData(135, "Dreadlord", WC3Race.UNDEAD),
    ItemNames.IMPALE: ItemData(136, "Crypt Lord", WC3Race.UNDEAD),
    ItemNames.SPIKED_CARAPACE: ItemData(137, "Crypt Lord", WC3Race.UNDEAD),
    ItemNames.CARRION_BEETLES: ItemData(138, "Crypt Lord", WC3Race.UNDEAD),
    ItemNames.LOCUST_SWARM: ItemData(139, "Crypt Lord", WC3Race.UNDEAD),
    ItemNames.SILENCE: ItemData(140, "Dark Ranger", WC3Race.UNDEAD),
    ItemNames.BLACK_ARROW: ItemData(141, "Dark Ranger", WC3Race.UNDEAD),
    ItemNames.LIFE_DRAIN: ItemData(142, "Dark Ranger", WC3Race.UNDEAD),
    ItemNames.CHARM: ItemData(143, "Dark Ranger", WC3Race.UNDEAD),
    # Night Elf
    ItemNames.ARCHER: ItemData(144, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.HUNTRESS: ItemData(145, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.GLAIVE_THROWER: ItemData(146, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.DRYAD: ItemData(147, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.DRUID_OF_THE_CLAW: ItemData(148, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.MOUNTAIN_GIANT: ItemData(149, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.HIPPOGRYPH: ItemData(150, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.DRUID_OF_THE_TALON: ItemData(151, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.FAERIE_DRAGON: ItemData(152, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.CHIMERA: ItemData(153, "Unit", WC3Race.NIGHT_ELF),
    ItemNames.ANCIENT_PROTECTOR: ItemData(154, "Building", WC3Race.NIGHT_ELF),
    ItemNames.ANCIENT_OF_WONDERS: ItemData(155, "Building", WC3Race.NIGHT_ELF),
    ItemNames.NIGHT_ELF_UPGRADES: ItemData(156, "Forge", WC3Race.NIGHT_ELF),
    ItemNames.ULTRAVISION: ItemData(157, "Upgrade", WC3Race.NIGHT_ELF, classification=ItemClassification.filler),
    ItemNames.WELL_SPRING: ItemData(158, "Upgrade", WC3Race.NIGHT_ELF),
    ItemNames.NATURES_BLESSING: ItemData(159, "Upgrade", WC3Race.NIGHT_ELF),
    ItemNames.ARCHER_MARKSMANSHIP: ItemData(160, "Upgrade", WC3Race.NIGHT_ELF, parent_item=ItemNames.ARCHER),
    ItemNames.HUNTRESS_MOON_GLAIVE: ItemData(161, "Upgrade", WC3Race.NIGHT_ELF, parent_item=ItemNames.HUNTRESS),
    ItemNames.GLAIVE_THROWER_VORPAL_BLADES: ItemData(162, "Upgrade", WC3Race.NIGHT_ELF,
                                                     parent_item=ItemNames.GLAIVE_THROWER),
    ItemNames.DRYAD_ABOLISH_MAGIC: ItemData(163, "Upgrade", WC3Race.NIGHT_ELF, parent_item=ItemNames.DRYAD),
    ItemNames.PROGRESSIVE_BEAR_TRAINING: ItemData(164, "Caster Training", WC3Race.NIGHT_ELF, quantity=2,
                                                  parent_item=ItemNames.DRUID_OF_THE_CLAW,
                                                  classification=ItemClassification.progression),
    ItemNames.MOUNTAIN_GIANT_RESISTANT_SKIN: ItemData(165, "Upgrade", WC3Race.NIGHT_ELF,
                                                      parent_item=ItemNames.MOUNTAIN_GIANT),
    ItemNames.MOUNTAIN_GIANT_HARDENED_SKIN: ItemData(166, "Upgrade", WC3Race.NIGHT_ELF,
                                                     parent_item=ItemNames.MOUNTAIN_GIANT),
    ItemNames.PROGRESSIVE_CROW_TRAINING: ItemData(167, "Caster Training", WC3Race.NIGHT_ELF, quantity=2,
                                                  parent_item=ItemNames.DRUID_OF_THE_TALON),
    ItemNames.PROGRESSIVE_NIGHT_ELF_CASTER_TRAINING: ItemData(168, "Caster Training", WC3Race.NIGHT_ELF, quantity=2),
    ItemNames.CHIMERA_CORROSIVE_BREATH: ItemData(169, "Upgrade", WC3Race.NIGHT_ELF, parent_item=ItemNames.CHIMERA),
    ItemNames.IMPROVED_BOWS: ItemData(170, "Upgrade", WC3Race.NIGHT_ELF),
    ItemNames.NIGHT_ELF_LEVEL: ItemData(171, "Level", WC3Race.NIGHT_ELF),
    ItemNames.SCOUT: ItemData(172, "Priestess of the Moon", WC3Race.NIGHT_ELF, classification=ItemClassification.filler),
    ItemNames.SEARING_ARROWS: ItemData(173, "Priestess of the Moon", WC3Race.NIGHT_ELF),
    ItemNames.TRUESHOT_AURA: ItemData(174, "Priestess of the Moon", WC3Race.NIGHT_ELF),
    ItemNames.STARFALL: ItemData(175, "Priestess of the Moon", WC3Race.NIGHT_ELF),
    ItemNames.ENTANGLING_ROOTS: ItemData(176, "Keeper of the Grove", WC3Race.NIGHT_ELF),
    ItemNames.FORCE_OF_NATURE: ItemData(177, "Keeper of the Grove", WC3Race.NIGHT_ELF),
    ItemNames.THORNS_AURA: ItemData(178, "Keeper of the Grove", WC3Race.NIGHT_ELF),
    ItemNames.TRANQUILITY: ItemData(179, "Keeper of the Grove", WC3Race.NIGHT_ELF),
    ItemNames.MANA_BURN: ItemData(180, "Demon Hunter", WC3Race.NIGHT_ELF),
    ItemNames.IMMOLATION: ItemData(181, "Demon Hunter", WC3Race.NIGHT_ELF),
    ItemNames.EVASION: ItemData(182, "Demon Hunter", WC3Race.NIGHT_ELF),
    ItemNames.METAMORPHOSIS: ItemData(183, "Demon Hunter", WC3Race.NIGHT_ELF),
    ItemNames.FAN_OF_KNIVES: ItemData(184, "Warden", WC3Race.NIGHT_ELF),
    ItemNames.BLINK: ItemData(185, "Warden", WC3Race.NIGHT_ELF),
    ItemNames.SHADOW_STRIKE: ItemData(186, "Warden", WC3Race.NIGHT_ELF),
    ItemNames.VENGEANCE: ItemData(187, "Warden", WC3Race.NIGHT_ELF),
    # Naga
    ItemNames.MURGUL_REAVER: ItemData(188, "Unit", WC3Race.NAGA),
    ItemNames.MYRMIDON: ItemData(189, "Unit", WC3Race.NAGA),
    ItemNames.SNAP_DRAGON: ItemData(190, "Unit", WC3Race.NAGA),
    ItemNames.ROYAL_GUARD: ItemData(191, "Unit", WC3Race.NAGA),
    ItemNames.DRAGON_TURTLE: ItemData(192, "Unit", WC3Race.NAGA,
    ItemNames.SIREN: ItemData(193, "Unit", WC3Race.NAGA),
    ItemNames.COUATL: ItemData(194, "Unit", WC3Race.NAGA),
    ItemNames.TIDAL_GUARDIAN: ItemData(195, "Building", WC3Race.NAGA),
    ItemNames.COUATL_ABOLISH_MAGIC: ItemData(196, "Building", WC3Race.NAGA, parent_item=ItemNames.COUATL),
    ItemNames.NAGA_UPGRADES: ItemData(197, "Forge", WC3Race.NAGA),
    ItemNames.MYRMIDON_ENSNARE: ItemData(198, "Upgrade", WC3Race.NAGA, parent_item=ItemNames.MYRMIDON,
                                         classification=ItemClassification.progression),
    ItemNames.PROGRESSIVE_SIREN_TRAINING: ItemData(199, "Caster Training", WC3Race.NAGA, quantity=2),
    ItemNames.FORKED_LIGHTNING: ItemData(200, "Naga Sea Witch", WC3Race.NAGA),
    ItemNames.FROST_ARROWS: ItemData(201, "Naga Sea Witch", WC3Race.NAGA),
    ItemNames.MANA_SHIELD: ItemData(202, "Naga Sea Witch", WC3Race.NAGA),
    ItemNames.TORNADO: ItemData(203, "Naga Sea Witch", WC3Race.NAGA),
    ItemNames.STARTING_RESOURCES: ItemData(204, "Filler", WC3Race.ANY),
    ItemNames.HERO_LEVEL: ItemData(205, "Level", WC3Race.ANY),
    ItemNames.NOTHING: ItemData(206, "Filler", WC3Race.ANY),
}


def get_item_table():
    return item_table


basic_units = {
    WC3Race.HUMAN: {
        ItemNames.FOOTMAN,
        ItemNames.RIFLEMAN,
        ItemNames.KNIGHT,
        ItemNames.GRYPHON_RIDER
    },
    WC3Race.ORC: {
        ItemNames.GRUNT,
        ItemNames.HEADHUNTER,
        ItemNames.WIND_RIDER,
        ItemNames.TAUREN
    },
    WC3Race.UNDEAD: {
        ItemNames.CRYPT_FIEND,
        ItemNames.ABOMINATION
    },
    WC3Race.NIGHT_ELF: {
        ItemNames.ARCHER,
        ItemNames.HUNTRESS,
        ItemNames.DRYAD
    },
    WC3Race.NAGA: {
        ItemNames.MYRMIDON,
        ItemNames.SNAP_DRAGON,
        ItemNames.COUATL,
        ItemNames.ROYAL_GUARD
    }
}

advanced_basic_units = {
    WC3Race.HUMAN: basic_units[WC3Race.HUMAN].union({
        ItemNames.SPELL_BREAKER,
        ItemNames.MORTAR_TEAM,
        ItemNames.DRAGONHAWK_RIDER
    }),
    WC3Race.ORC: basic_units[WC3Race.ORC].union({
        ItemNames.RAIDER
    }),
    WC3Race.UNDEAD: basic_units[WC3Race.UNDEAD].union({
        ItemNames.GHOUL,
        ItemNames.NECROMANCER,
        ItemNames.FROST_WYRM
    }),
    WC3Race.NIGHT_ELF: basic_units[WC3Race.NIGHT_ELF].union({
        ItemNames.MOUNTAIN_GIANT,
        ItemNames.CHIMERA
    }),
    WC3Race.NAGA: basic_units[WC3Race.NAGA].union({
        ItemNames.DRAGON_TURTLE,
        ItemNames.MURGUL_REAVER
    })
}

no_logic_starting_units = {
    WC3Race.HUMAN: advanced_basic_units[WC3Race.HUMAN].union({
        ItemNames.PRIEST,
        ItemNames.SORCERESS,
        ItemNames.PEASANT_CALL_TO_ARMS
    }),
    WC3Race.ORC: advanced_basic_units[WC3Race.ORC].union({
        ItemNames.BATRIDER,
        ItemNames.SHAMAN,
        ItemNames.WITCH_DOCTOR,
        ItemNames.DEMOLISHER,
        ItemNames.PEON_BATTLE_STATIONS
    }),
    WC3Race.UNDEAD: advanced_basic_units[WC3Race.UNDEAD].union({
        ItemNames.BANSHEE,
        ItemNames.MEAT_WAGON
    }),
    WC3Race.NIGHT_ELF: advanced_basic_units[WC3Race.NIGHT_ELF].union({
        ItemNames.DRUID_OF_THE_CLAW,
        ItemNames.DRUID_OF_THE_TALON
    }),
    WC3Race.NAGA: advanced_basic_units[WC3Race.NAGA].union({
        ItemNames.SIREN
    })
}

not_balanced_starting_units = {
    ItemNames.GRYPHON_RIDER,
    ItemNames.WIND_RIDER,
    ItemNames.FROST_WYRM,
    ItemNames.CHIMERA,
    ItemNames.COUATL,
    ItemNames.ROYAL_GUARD
}

filler_items = [
    ItemNames.STARTING_RESOURCES
]

progressive_casters = {
    ItemNames.PRIEST,
    ItemNames.SORCERESS,
    ItemNames.SHAMAN,
    ItemNames.WITCH_DOCTOR,
    ItemNames.NECROMANCER,
    ItemNames.BANSHEE,
    ItemNames.DRUID_OF_THE_CLAW,
    ItemNames.DRUID_OF_THE_TALON,
    ItemNames.SIREN
}

caster_training = {
    0: [],
    1: [
        ItemNames.PROGRESSIVE_PRIEST_TRAINING,
        ItemNames.PROGRESSIVE_SORCERESS_TRAINING,
        ItemNames.PROGRESSIVE_SHAMAN_TRAINING,
        ItemNames.PROGRESSIVE_WITCH_DOCTOR_TRAINING,
        ItemNames.PROGRESSIVE_NECROMANCER_TRAINING,
        ItemNames.PROGRESSIVE_BANSHEE_TRAINING,
        ItemNames.PROGRESSIVE_BEAR_TRAINING,
        ItemNames.PROGRESSIVE_CROW_TRAINING,
        ItemNames.PROGRESSIVE_SIREN_TRAINING
    ],
    2: [
        ItemNames.PROGRESSIVE_HUMAN_CASTER_TRAINING,
        ItemNames.PROGRESSIVE_ORC_CASTER_TRAINING,
        ItemNames.PROGRESSIVE_UNDEAD_CASTER_TRAINING,
        ItemNames.PROGRESSIVE_NIGHT_ELF_CASTER_TRAINING,
        ItemNames.PROGRESSIVE_SIREN_TRAINING
    ],
    3: []
}


def get_basic_units(world: World, race: WC3Race) -> typing.Set[str]:
    logic_level = get_option_value(world, 'required_tactics')
    if race == WC3Race.ANY:
        return {}
    if logic_level == RequiredTactics.option_no_logic:
        return no_logic_starting_units[race]
    elif logic_level == RequiredTactics.option_advanced:
        return advanced_basic_units[race]
    else:
        return basic_units[race]
