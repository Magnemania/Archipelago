from typing import NamedTuple, Dict, List, Set, Union, Literal, Iterable, Callable
from enum import IntEnum, Enum, IntFlag, auto


class WC3Race(IntEnum):
    ANY = 0
    HUMAN = 1
    ORC = 2
    UNDEAD = 3
    NIGHT_ELF = 4
    NAGA = 5


class MissionPools(IntEnum):
    STARTER = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4
    FINAL = 5


class MissionFlags(IntFlag):
    none = 0
    # Playable races
    Human = auto()
    Orc = auto()
    Undead = auto()
    NightElf = auto()
    Naga = auto()
    # Flags used for logic
    NoBuild = auto()
    AirEnemy = auto()
    Defense = auto()
    Blink = auto()
    DrainAura = auto()


RACE_FLAGS = {
    WC3Race.HUMAN: MissionFlags.Human,
    WC3Race.ORC: MissionFlags.Orc,
    WC3Race.UNDEAD: MissionFlags.Undead,
    WC3Race.NIGHT_ELF: MissionFlags.NightElf,
    WC3Race.NAGA: MissionFlags.Naga
}

FLAG_RACES = {flag: race for race, flag in RACE_FLAGS.items()}


class WC3Hero(str, Enum):
    NONE = "None"
    PALADIN = "Paladin"
    ARCHMAGE = "Archmage"
    MOUNTAIN_KING = "Mountain King"
    BLOOD_MAGE = "Blood Mage"
    FAR_SEER = "Far Seer"
    BLADEMASTER = "Blademaster"
    TAUREN_CHIEFTAIN = "Tauren Chieftain"
    SHADOW_HUNTER = "Shadow Hunter"
    DEATH_KNIGHT = "Death Knight"
    LICH = "Lich"
    DREADLORD = "Dreadlord"
    CRYPT_LORD = "Crypt Lord"
    DARK_RANGER = "Dark Ranger"
    PRIESTESS_OF_THE_MOON = "Priestess of the Moon"
    KEEPER_OF_THE_GROVE = "Keeper of the Grove"
    DEMON_HUNTER = "Demon Hunter"
    WARDEN = "Warden"
    SEA_WITCH = "Naga Sea Witch"


class WC3Campaign(Enum):

    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, campaign_id: int, name: str, race: WC3Race, hero: WC3Hero):
        self.id = campaign_id
        self.campaign_name = name
        self.race = race
        self.hero = hero

    GLOBAL = 0, "Global", WC3Race.ANY, WC3Hero.NONE
    PROLOGUE = 1, "Exodus of the Horde", WC3Race.ORC, WC3Hero.FAR_SEER
    HUMAN = 2, "The Scourge of Lordaeron", WC3Race.HUMAN, WC3Hero.PALADIN
    UNDEAD = 3, "Path of the Damned", WC3Race.UNDEAD, WC3Hero.DEATH_KNIGHT
    ORC = 4, "The Invasion of Kalimdor", WC3Race.ORC, WC3Hero.FAR_SEER
    NIGHT_ELF = 5, "Eternity's End", WC3Race.NIGHT_ELF, WC3Hero.PRIESTESS_OF_THE_MOON
    SENTINEL = 6, "Terror of the Tides", WC3Race.NIGHT_ELF, WC3Hero.WARDEN
    ALLIANCE = 7, "Curse of the Blood Elves", WC3Race.HUMAN, WC3Hero.BLOOD_MAGE
    SCOURGE = 8, "Legacy of the Damned", WC3Race.UNDEAD, WC3Hero.DEATH_KNIGHT


class WC3Mission(Enum):

    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, mission_id: int, name: str, campaign: WC3Campaign, difficulty: MissionPools,
                 flags: IntFlag = MissionFlags.none, heroes: List[WC3Hero] = None):
        self.id = mission_id
        self.mission_name = name
        self.campaign = campaign
        self.difficulty = difficulty
        if heroes is None:
            self.heroes = [campaign.hero]
        else:
            self.heroes = heroes
        self.flags = flags

    # Exodus of the Horde
    CHASING_VISIONS = 1, "Chasing Visions", WC3Campaign.ORC, MissionPools.STARTER, MissionFlags.NoBuild
    DEPARTURES = 2, "Departures", WC3Campaign.ORC, MissionPools.STARTER
    RIDERS_ON_THE_STORM = 3, "Riders on the Storm", WC3Campaign.ORC, MissionPools.EASY
    THE_FIRES_DOWN_BELOW = 4, "The Fires Down Below", WC3Campaign.ORC, MissionPools.EASY
    COUNTDOWN_TO_EXTINCTION = 5, "Countdown to Extinction", WC3Campaign.ORC, MissionPools.HARD

    # The Scourge of Lordaeron
    THE_DEFENSE_OF_STRAHNBRAD = 6, "The Defense of Strahnbrad", WC3Campaign.HUMAN, MissionPools.STARTER, MissionFlags.NoBuild
    BLACKROCK_AND_ROLL = 7, "Blackrock and Roll", WC3Campaign.HUMAN, MissionPools.STARTER
    RAVAGES_OF_THE_PLAGUE = 8, "Ravages of the Plague", WC3Campaign.HUMAN, MissionPools.STARTER, \
                            MissionFlags.NoBuild, [WC3Hero.PALADIN, WC3Hero.ARCHMAGE]
    THE_CULT_OF_THE_DAMNED = 9, "The Cult of the Damned", WC3Campaign.HUMAN, MissionPools.EASY, \
                            MissionFlags.none, [WC3Hero.PALADIN, WC3Hero.ARCHMAGE]
    MARCH_OF_THE_SCOURGE = 10, "March of the Scourge", WC3Campaign.HUMAN, MissionPools.MEDIUM, MissionFlags.Defense
    THE_CULLING = 11, "The Culling", WC3Campaign.HUMAN, MissionPools.MEDIUM
    THE_SHORES_OF_NORTHREND = 12, "The Shores of Northrend", WC3Campaign.HUMAN, MissionPools.MEDIUM, MissionFlags.AirEnemy
    DISSENSION = 13, "Dissension", WC3Campaign.HUMAN, MissionPools.EASY, MissionFlags.NoBuild, [WC3Hero.PALADIN, WC3Hero.MOUNTAIN_KING]
    FROSTMOURNE = 14, "Frostmourne", WC3Campaign.HUMAN, MissionPools.VERY_HARD

    # Path of the Damned
    TRUDGING_THROUGH_THE_ASHES = 15, "Trudging through the Ashes", WC3Campaign.UNDEAD, MissionPools.STARTER, MissionFlags.NoBuild
    DIGGING_UP_THE_DEAD = 16, "Digging up the Dead", WC3Campaign.UNDEAD, MissionPools.STARTER
    INTO_THE_REALM_ETERNAL = 17, "Into the Realm Eternal", WC3Campaign.UNDEAD, MissionPools.EASY
    KEY_OF_THE_THREE_MOONS = 18, "Key of the Three Moons", WC3Campaign.UNDEAD, MissionPools.MEDIUM, MissionFlags.AirEnemy
    THE_FALL_OF_SILVERMOON = 19, "The Fall of Silvermoon", WC3Campaign.UNDEAD, MissionPools.MEDIUM
    BLACKROCK_AND_ROLL_TOO = 20, "Blackrock & Roll, Too!", WC3Campaign.UNDEAD, MissionPools.MEDIUM, \
                             MissionFlags.AirEnemy, [WC3Hero.DEATH_KNIGHT, WC3Hero.LICH]
    THE_SIEGE_OF_DALARAN = 21, "The Siege of Dalaran", WC3Campaign.UNDEAD, MissionPools.MEDIUM, \
                           MissionFlags.AirEnemy, [WC3Hero.DEATH_KNIGHT, WC3Hero.LICH]
    UNDER_THE_BURNING_SKY = 22, "Under the Burning Sky", WC3Campaign.UNDEAD, MissionPools.VERY_HARD, MissionFlags.AirEnemy

    # The Invasion of Kalimdor
    LANDFALL = 23, "Landfall", WC3Campaign.ORC, MissionPools.STARTER, MissionFlags.NoBuild
    THE_LONG_MARCH = 24, "The Long March", WC3Campaign.ORC, MissionPools.STARTER, MissionFlags.NoBuild, \
                     [WC3Hero.FAR_SEER, WC3Hero.TAUREN_CHIEFTAIN]
    CRY_OF_THE_WARSONG = 25, "Cry of the Warsong", WC3Campaign.ORC, MissionPools.STARTER, MissionFlags.AirEnemy
    THE_SPIRITS_OF_ASHENVALE = 26, "The Spirits of Ashenvale", WC3Campaign.ORC, MissionPools.MEDIUM, \
                               MissionFlags.AirEnemy, [WC3Hero.BLADEMASTER]
    THE_HUNTER_OF_SHADOWS = 27, "The Hunter of Shadows", WC3Campaign.ORC, MissionPools.MEDIUM, \
                               MissionFlags.AirEnemy, [WC3Hero.BLADEMASTER]
    WHERE_WYVERNS_DARE = 28, "Where Wyverns Dare", WC3Campaign.ORC, MissionPools.MEDIUM, MissionFlags.AirEnemy, \
                     [WC3Hero.FAR_SEER, WC3Hero.TAUREN_CHIEFTAIN]
    THE_ORACLE = 29, "The Oracle", WC3Campaign.ORC, MissionPools.EASY, MissionFlags.NoBuild, \
                     [WC3Hero.FAR_SEER, WC3Hero.TAUREN_CHIEFTAIN]
    BY_DEMONS_BE_DRIVEN = 30, "By Demons Be Driven", WC3Campaign.ORC, MissionPools.VERY_HARD, \
                     [WC3Hero.FAR_SEER, WC3Hero.TAUREN_CHIEFTAIN]

    # Eternity's End
    ENEMIES_AT_THE_GATE = 31, "Enemies at the Gate", WC3Campaign.NIGHT_ELF, MissionPools.STARTER
    DAUGHTERS_OF_THE_MOON = 32, "Daughters of the Moon", WC3Campaign.NIGHT_ELF, MissionPools.STARTER, MissionFlags.NoBuild
    THE_AWAKENING_OF_STORMRAGE = 33, "The Awakening of Stormrage", WC3Campaign.NIGHT_ELF, MissionPools.MEDIUM
    THE_DRUIDS_ARISE = 34, "The Druids Arise", WC3Campaign.NIGHT_ELF, MissionPools.MEDIUM, MissionFlags.AirEnemy, \
                       [WC3Hero.PRIESTESS_OF_THE_MOON, WC3Hero.KEEPER_OF_THE_GROVE]
    BROTHERS_IN_BLOOD = 35, "Brothers in Blood", WC3Campaign.NIGHT_ELF, MissionPools.EASY, MissionFlags.NoBuild, \
                       [WC3Hero.PRIESTESS_OF_THE_MOON, WC3Hero.KEEPER_OF_THE_GROVE]
    A_DESTINY_OF_FLAME_AND_SORROW = 36, "A Destiny of Flame and Sorrow", WC3Campaign.NIGHT_ELF, MissionPools.HARD, \
                                    MissionFlags.NoBuild, [WC3Hero.DEMON_HUNTER]
    TWILIGHT_OF_THE_GODS = 37, "Twilight of the Gods", WC3Campaign.NIGHT_ELF, MissionPools.VERY_HARD, MissionFlags.NoBuild, \
                           [WC3Hero.PRIESTESS_OF_THE_MOON, WC3Hero.KEEPER_OF_THE_GROVE]

    # Terror of the Tides
    RISE_OF_THE_NAGA = 32, "Rise of the Naga", WC3Campaign.SENTINEL, MissionPools.STARTER, MissionFlags.NoBuild
    THE_BROKEN_ISLES = 33, "The Broken Isles", WC3Campaign.SENTINEL, MissionPools.MEDIUM, MissionFlags.AirEnemy
    THE_TOMB_OF_SARGERAS = 34, "The Tomb of Sargeras", WC3Campaign.SENTINEL, MissionPools.EASY, MissionFlags.NoBuild
    WRATH_OF_THE_BETRAYER = 35, "Wrath of the Betrayer", WC3Campaign.SENTINEL, MissionPools.MEDIUM, MissionFlags.AirEnemy
    BALANCING_THE_SCALES = 36, "Balancing the Scales", WC3Campaign.SENTINEL, MissionPools.MEDIUM, \
                           MissionFlags.AirEnemy, [WC3Hero.WARDEN, WC3Hero.PRIESTESS_OF_THE_MOON, WC3Hero.KEEPER_OF_THE_GROVE]
    SHARDS_OF_THE_ALLIANCE = 37, "Shards of the Alliance", WC3Campaign.SENTINEL, MissionPools.EASY, MissionFlags.NoBuild
    THE_RUINS_OF_DALARAN = 38, "The Ruins of Dalaran", WC3Campaign.SENTINEL, MissionPools.HARD, MissionFlags.AirEnemy
    THE_BROTHERS_STORMRAGE = 39, "The Brothers Stormrage", WC3Campaign.SENTINEL, MissionPools.HARD, \
                             MissionFlags.Naga | MissionFlags.AirEnemy, [WC3Hero.DEMON_HUNTER, WC3Hero.KEEPER_OF_THE_GROVE]

    # Curse of the Blood Elves
    MISCONCEPTIONS = 40, "Misconceptions", WC3Campaign.ALLIANCE, MissionPools.EASY
    A_DARK_COVENANT = 41, "A Dark Covenant", WC3Campaign.ALLIANCE, MissionPools.MEDIUM, \
                      MissionFlags.Naga | MissionFlags.AirEnemy, [WC3Hero.BLOOD_MAGE, WC3Hero.SEA_WITCH]
    THE_DUNGEONS_OF_DALARAN = 42, "The Dungeons of Dalaran", WC3Campaign.ALLIANCE, MissionPools.EASY, \
                              MissionFlags.NoBuild | MissionFlags.Naga, [WC3Hero.BLOOD_MAGE, WC3Hero.SEA_WITCH]
    THE_CROSSING = 43, "The Crossing", WC3Campaign.ALLIANCE, MissionPools.EASY, \
                   MissionFlags.NoBuild | MissionFlags.Naga, [WC3Hero.BLOOD_MAGE, WC3Hero.SEA_WITCH]
    THE_SEARCH_FOR_ILLIDAN = 44, "The Search for Illidan", WC3Campaign.ALLIANCE, MissionPools.EASY, \
                             MissionFlags.NoBuild | MissionFlags.Naga, [WC3Hero.BLOOD_MAGE, WC3Hero.SEA_WITCH]
    GATES_OF_THE_ABYSS = 45, "Gates of the Abyss", WC3Campaign.ALLIANCE, MissionPools.HARD, MissionFlags.Naga, \
                        [WC3Hero.BLOOD_MAGE, WC3Hero.SEA_WITCH, WC3Hero.DEMON_HUNTER]
    LORD_OF_OUTLAND = 46, "Lord of Outland", WC3Campaign.ALLIANCE, MissionPools.HARD, MissionFlags.NoBuild | MissionFlags.Naga, \
                      [WC3Hero.BLOOD_MAGE, WC3Hero.SEA_WITCH, WC3Hero.DEMON_HUNTER]

    # Legacy of the Damned
    KING_ARTHAS = 47, "King Arthas", WC3Campaign.SCOURGE, MissionPools.MEDIUM
    THE_FLIGHT_FROM_LORDAERON = 48, "The Flight from Lordaeron", WC3Campaign.SCOURGE, MissionPools.EASY, MissionFlags.NoBuild
    THE_DARK_LADY = 49, "The Dark Lady", WC3Campaign.SCOURGE, MissionPools.EASY, MissionFlags.none, [WC3Hero.DARK_RANGER]
    THE_RETURN_TO_NORTHREND = 50, "The Return to Northrend", WC3Campaign.SCOURGE, MissionPools.MEDIUM, \
                              MissionFlags.AirEnemy, [WC3Hero.DEATH_KNIGHT, WC3Hero.CRYPT_LORD]
    DREADLORDS_FALL = 51, "Dreadlord's Fall", WC3Campaign.SCOURGE, MissionPools.MEDIUM, \
                      MissionFlags.AirEnemy, [WC3Hero.DARK_RANGER]
    A_NEW_POWER_IN_LORDAERON = 52, "A New Power in Lordaeron", WC3Campaign.SCOURGE, MissionPools.HARD, \
                               MissionFlags.Human, [WC3Hero.DARK_RANGER, WC3Hero.DREADLORD]
    INTO_THE_SHADOW_WEB_CAVERNS = 53, "Into the Shadow Web Caverns", WC3Campaign.SCOURGE, MissionPools.MEDIUM, \
                                  MissionFlags.NoBuild, [WC3Hero.DEATH_KNIGHT, WC3Hero.CRYPT_LORD]
    THE_FORGOTTEN_ONES = 54, "The Forgotten Ones", WC3Campaign.SCOURGE, MissionPools.MEDIUM, \
                         MissionFlags.NoBuild, [WC3Hero.DEATH_KNIGHT, WC3Hero.CRYPT_LORD]
    ASCENT_TO_THE_UPPER_KINGDOM = 55, "Ascent to the Upper Kingdom", WC3Campaign.SCOURGE, MissionPools.MEDIUM, \
                                  MissionFlags.NoBuild, [WC3Hero.DEATH_KNIGHT, WC3Hero.CRYPT_LORD]
    A_SYMPHONY_OF_FROST_AND_FLAME = 56, "A Symphony of Frost and FLame", WC3Campaign.SCOURGE, MissionPools.VERY_HARD, \
                                  MissionFlags.AirEnemy, [WC3Hero.DEATH_KNIGHT, WC3Hero.CRYPT_LORD]


class MissionConnection:
    campaign: WC3Campaign
    connect_to: int  # -1 connects to Menu

    def __init__(self, connect_to, campaign = WC3Campaign.GLOBAL):
        self.campaign = campaign
        self.connect_to = connect_to

    def _asdict(self):
        return {
            "campaign": self.campaign.id,
            "connect_to": self.connect_to
        }


class MissionInfo(NamedTuple):
    mission: WC3Mission
    required_world: List[Union[MissionConnection, Dict[Literal["campaign", "connect_to"], int]]]
    category: str
    number: int = 0  # number of worlds need beaten
    completion_critical: bool = False  # missions needed to beat game
    or_requirements: bool = False  # true if the requirements should be or-ed instead of and-ed
    ui_vertical_padding: int = 0


class FillMission(NamedTuple):
    type: MissionPools
    connect_to: List[MissionConnection]
    category: str
    number: int = 0  # number of worlds need beaten
    completion_critical: bool = False  # missions needed to beat game
    or_requirements: bool = False  # true if the requirements should be or-ed instead of and-ed
    removal_priority: int = 0  # how many missions missing from the pool required to remove this mission


def vanilla_shuffle_order() -> Dict[WC3Campaign, List[FillMission]]:
    mission_count = {campaign: 0 for campaign in WC3Campaign}
    for mission in WC3Mission:
        mission_count[mission.campaign] += 1
    campaign_missions = dict()
    prev_mission = -1
    for campaign in WC3Campaign:
        campaign_missions[campaign] = []
        if campaign in (WC3Campaign.ALLIANCE, WC3Campaign.SCOURGE):
            mission_pool = MissionPools.MEDIUM
        else:
            mission_pool = MissionPools.STARTER
        for i in range(mission_count[campaign]):
            if i == 1 and mission_pool == MissionPools.STARTER:
                mission_pool = MissionPools.EASY
            elif i == 3:
                mission_pool = MissionPools.MEDIUM
            elif i == 5:
                mission_pool == MissionPools.HARD
            campaign_missions[campaign].append(FillMission(mission_pool, [MissionConnection(prev_mission, campaign)], f"_{i}", completion_critical=True))
            prev_mission += 1
    return campaign_missions


def gauntlet_order() -> Dict[WC3Campaign, List[FillMission]]:
    return {
        WC3Campaign.GLOBAL: [
            FillMission(MissionPools.STARTER, [MissionConnection(-1)], "I", completion_critical=True),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "II", completion_critical=True),
            FillMission(MissionPools.EASY, [MissionConnection(1)], "III", completion_critical=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(2)], "IV", completion_critical=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(3)], "V", completion_critical=True),
            FillMission(MissionPools.HARD, [MissionConnection(4)], "VI", completion_critical=True),
            FillMission(MissionPools.FINAL, [MissionConnection(5)], "Final", completion_critical=True)
        ]
    }


def mini_gauntlet_order() -> Dict[WC3Campaign, List[FillMission]]:
    return {
        WC3Campaign.GLOBAL: [
            FillMission(MissionPools.STARTER, [MissionConnection(-1)], "I", completion_critical=True),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "II", completion_critical=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(1)], "III", completion_critical=True),
            FillMission(MissionPools.FINAL, [MissionConnection(2)], "Final", completion_critical=True)
        ]
    }


def grid_order() -> Dict[WC3Campaign, List[FillMission]]:
    return {
        WC3Campaign.GLOBAL: [
            FillMission(MissionPools.STARTER, [MissionConnection(-1)], "_1"),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "_1"),
            FillMission(MissionPools.MEDIUM, [MissionConnection(1), MissionConnection(6), MissionConnection( 3)], "_1", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(2), MissionConnection(7)], "_1", or_requirements=True),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "_2"),
            FillMission(MissionPools.MEDIUM, [MissionConnection(1), MissionConnection(4)], "_2", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(2), MissionConnection(5), MissionConnection(10), MissionConnection(7)], "_2", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(3), MissionConnection(6), MissionConnection(11)], "_2", or_requirements=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(4), MissionConnection(9), MissionConnection(12)], "_3", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(5), MissionConnection(8), MissionConnection(10), MissionConnection(13)], "_3", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(6), MissionConnection(9), MissionConnection(11), MissionConnection(14)], "_3", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(7), MissionConnection(10)], "_3", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(8), MissionConnection(13)], "_4", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(9), MissionConnection(12), MissionConnection(14)], "_4", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(10), MissionConnection(13)], "_4", or_requirements=True),
            FillMission(MissionPools.FINAL, [MissionConnection(11), MissionConnection(14)], "_4", or_requirements=True)
        ]
    }

def mini_grid_order() -> Dict[WC3Campaign, List[FillMission]]:
    return {
        WC3Campaign.GLOBAL: [
            FillMission(MissionPools.STARTER, [MissionConnection(-1)], "_1"),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "_1"),
            FillMission(MissionPools.MEDIUM, [MissionConnection(1), MissionConnection(5)], "_1", or_requirements=True),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "_2"),
            FillMission(MissionPools.MEDIUM, [MissionConnection(1), MissionConnection(3)], "_2", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(2), MissionConnection(4)], "_2", or_requirements=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(3), MissionConnection(7)], "_3", or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(4), MissionConnection(6)], "_3", or_requirements=True),
            FillMission(MissionPools.FINAL, [MissionConnection(5), MissionConnection(7)], "_3", or_requirements=True)
        ]
    }

def tiny_grid_order() -> Dict[WC3Campaign, List[FillMission]]:
    return {
        WC3Campaign.GLOBAL: [
            FillMission(MissionPools.STARTER, [MissionConnection(-1)], "_1"),
            FillMission(MissionPools.MEDIUM, [MissionConnection(0)], "_1"),
            FillMission(MissionPools.EASY, [MissionConnection(0)], "_2"),
            FillMission(MissionPools.FINAL, [MissionConnection(1), MissionConnection(2)], "_2", or_requirements=True),
        ]
    }

def blitz_order() -> Dict[WC3Campaign, List[FillMission]]:
    return {
        WC3Campaign.GLOBAL: [
            FillMission(MissionPools.STARTER, [MissionConnection(-1)], "I"),
            FillMission(MissionPools.EASY, [MissionConnection(-1)], "I"),
            FillMission(MissionPools.MEDIUM, [MissionConnection(0), MissionConnection(1)], "II", number=1, or_requirements=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(0), MissionConnection(1)], "II", number=1, or_requirements=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(0), MissionConnection(1)], "III", number=2, or_requirements=True),
            FillMission(MissionPools.MEDIUM, [MissionConnection(0), MissionConnection(1)], "III", number=2, or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(0), MissionConnection(1)], "IV", number=3, or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(0), MissionConnection(1)], "IV", number=3, or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(0), MissionConnection(1)], "V", number=4, or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(0), MissionConnection(1)], "V", number=4, or_requirements=True),
            FillMission(MissionPools.HARD, [MissionConnection(0), MissionConnection(1)], "Final", number=5, or_requirements=True),
            FillMission(MissionPools.FINAL, [MissionConnection(0), MissionConnection(1)], "Final", number=5, or_requirements=True)
        ]
    }


mission_orders: List[Callable[[], Dict[WC3Campaign, List[FillMission]]]] = [
    vanilla_shuffle_order,
    vanilla_shuffle_order,
    blitz_order,
    gauntlet_order,
    grid_order
]


def get_vanilla_mission_req_table() -> Dict[WC3Campaign, Dict[str, MissionInfo]]:
    campaigns = {campaign: dict() for campaign in WC3Campaign}
    mission_req = []
    for mission in WC3Mission:
        campaign = campaigns[mission.campaign]
        campaign[mission.mission_name] = MissionInfo(mission, mission_req, "_" + str(len(campaign) + 1), completion_critical=True)
    return campaigns


lookup_id_to_mission: Dict[int, WC3Mission] = {
    mission.id: mission for mission in WC3Mission
}

lookup_name_to_mission: Dict[str, WC3Mission] = {
    mission.mission_name: mission for mission in WC3Mission
}

lookup_id_to_campaign: Dict[int, WC3Campaign] = {
    campaign.id: campaign for campaign in WC3Campaign
}


campaign_mission_table: Dict[WC3Campaign, Set[WC3Mission]] = {
    campaign: set() for campaign in WC3Campaign
}
for mission in WC3Mission:
    campaign_mission_table[mission.campaign].add(mission)


class WC3CampaignGoal(NamedTuple):
    mission: WC3Mission
    location: str


def get_no_build_missions() -> List[WC3Mission]:
    return [mission for mission in WC3Mission if mission.flags & MissionFlags.NoBuild]
