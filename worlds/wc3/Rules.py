from typing import Set

from BaseClasses import  CollectionState
from .Options import get_option_value, RequiredTactics, get_enabled_campaigns, MissionOrder
from .Items import get_basic_units, get_full_item_list
from .MissionTables import WC3Race, WC3Campaign
from . import ItemNames
from worlds.AutoWorld import World


class WC3Logic:

    def human_basic_unit(self, state):
        return state.has_any(self.basic_units[WC3Race.HUMAN], self.player)

    def orc_basic_unit(self, state):
        return state.has_any(self.basic_units[WC3Race.ORC], self.player)

    def undead_basic_unit(self, state):
        return state.has_any(self.basic_units[WC3Race.UNDEAD], self.player)

    def night_elf_basic_unit(self, state):
        return state.has_any(self.basic_units[WC3Race.NIGHT_ELF], self.player)

    def naga_basic_unit(self, state):
        return state.has_any(self.basic_units[WC3Race.NAGA], self.player)

    racial_basic_unit = {
        WC3Race.HUMAN: human_basic_unit,
        WC3Race.ORC: orc_basic_unit,
        WC3Race.UNDEAD: undead_basic_unit,
        WC3Race.NIGHT_ELF: night_elf_basic_unit,
        WC3Race.NAGA: naga_basic_unit
    }

    def human_anti_air(self, state):
        return state.has_any({ItemNames.RIFLEMAN, ItemNames.FLYING_MACHINE,
                              ItemNames.DRAGONHAWK_RIDER, ItemNames.GRYPHON_RIDER}, self.player) \
               or state.has_all({ItemNames.SIEGE_ENGINE, ItemNames.SIEGE_ENGINE_BARRAGE}, self.player)

    def orc_anti_air(self, state):
        return state.has_any({ItemNames.HEADHUNTER, ItemNames.WIND_RIDER, ItemNames.BATRIDER}, self.player) \
               or state.has_all({ItemNames.RAIDER, ItemNames.RAIDER_ENSNARE}, self.player)

    def undead_anti_air(self, state):
        return state.has_any({ItemNames.GARGOYLE, ItemNames.CRYPT_FIEND}, self.player)

    def night_elf_anti_air(self, state):
        return state.has_any({ItemNames.ARCHER, ItemNames.DRYAD, ItemNames.HIPPOGRYPH}, self.player)

    def naga_anti_air(self, state):
        return (
                       state.has_any({ItemNames.SNAP_DRAGON, ItemNames.COUATL}, self.player)
                       or state.has_all({ItemNames.MYRMIDON, ItemNames.MYRMIDON_ENSNARE}, self.player)
               ) or self.advanced_tactics and state.has(ItemNames.ROYAL_GUARD, self.player)

    racial_anti_air = {
        WC3Race.HUMAN: human_anti_air,
        WC3Race.ORC: orc_anti_air,
        WC3Race.UNDEAD: undead_anti_air,
        WC3Race.NIGHT_ELF: night_elf_anti_air,
        WC3Race.NAGA: naga_anti_air
    }

    def human_defense(self, state):
        return state.has_any({ItemNames.GUARD_TOWER, ItemNames.ARCANE_TOWER, ItemNames.CANNON_TOWER}, self.player)

    def orc_defense(self, state):
        return state.has(ItemNames.WATCH_TOWER, self.player)

    def undead_defense(self, state):
        return state.has_any({ItemNames.SPIRIT_TOWER, ItemNames.NERUBIAN_TOWER}, self.player)

    def night_elf_defense(self, state):
        return state.has(ItemNames.ANCIENT_PROTECTOR, self.player)

    def naga_defense(self, state):
        return state.has(ItemNames.TIDAL_GUARDIAN, self.player)

    racial_defense = {
        WC3Race.HUMAN: human_defense,
        WC3Race.ORC: orc_defense,
        WC3Race.UNDEAD: undead_defense,
        WC3Race.NIGHT_ELF: night_elf_defense,
        WC3Race.NAGA: naga_defense
    }

    def human_competent_comp(self, state):
        anti_air = self.human_anti_air(state)
        frontline = state.has_any({ItemNames.FOOTMAN, ItemNames.KNIGHT}, self.player)
        damage = state.has_any({ItemNames.RIFLEMAN, ItemNames.GRYPHON_RIDER}, self.player) \
                 or self.advanced_tactics and state.has(ItemNames.MORTAR_TEAM, self.player)
        support = state.has_any({ItemNames.PRIEST, ItemNames.SORCERESS, ItemNames.DRAGONHAWK_RIDER}, self.player)
        siege = state.has_any({ItemNames.MORTAR_TEAM, ItemNames.SIEGE_ENGINE}, self.player) \
                or self.advanced_tactics and state.has_all({ItemNames.FLYING_MACHINE, ItemNames.FLYING_MACHINE_BOMBS}, self.player)
        if self.advanced_tactics:
            conditions = sum([1 for condition in (frontline, damage, support, siege) if condition])
            return anti_air and conditions >= 3
        else:
            return anti_air and frontline and damage and support and siege

    def orc_competent_comp(self, state):
        anti_air = self.orc_anti_air(state)
        frontline = state.has_any({ItemNames.GRUNT, ItemNames.TAUREN}, self.player)
        damage = state.has_any({ItemNames.HEADHUNTER, ItemNames.WIND_RIDER}, self.player) \
                 or self.advanced_tactics and state.has_all({ItemNames.GRUNT, ItemNames.GRUNT_BRUTE_STRENGTH}, self.player)
        support = state.has_any({ItemNames.SHAMAN, ItemNames.WITCH_DOCTOR, ItemNames.SPIRIT_WALKER}, self.player)
        siege = state.has_any({ItemNames.DEMOLISHER, ItemNames.RAIDER}, self.player) \
                or self.advanced_tactics and state.has_all({ItemNames.BATRIDER, ItemNames.BATRIDER_LIQUID_FIRE},
                                                           self.player)
        if self.advanced_tactics:
            conditions = sum([1 for condition in (frontline, damage, support, siege) if condition])
            return anti_air and conditions >= 3
        else:
            return anti_air and frontline and damage and support and siege

    def undead_competent_comp(self, state):
        anti_air = self.undead_anti_air(state)
        frontline = state.has_any({ItemNames.CRYPT_FIEND, ItemNames.GARGOYLE}, self.player) \
                    or state.has_all({ItemNames.GHOUL, ItemNames.GHOUL_FRENZY}, self.player)
        damage = state.has_any({ItemNames.CRYPT_FIEND, ItemNames.FROST_WYRM}, self.player)
        support = state.has_any({ItemNames.NECROMANCER, ItemNames.BANSHEE, ItemNames.OBSIDIAN_STATUE}, self.player)
        siege = state.has(ItemNames.MEAT_WAGON, self.player) \
                or state.has_all({ItemNames.FROST_WYRM, ItemNames.FROST_WYRM_FREEZING_BREATH}, self.player)
        if self.advanced_tactics:
            conditions = sum([1 for condition in (frontline, damage, support, siege) if condition])
            return anti_air and conditions >= 3
        else:
            return anti_air and frontline and damage and support and siege

    def night_elf_competent_comp(self, state):
        anti_air = self.night_elf_anti_air(state)
        frontline = state.has_any({ItemNames.DRUID_OF_THE_CLAW, ItemNames.MOUNTAIN_GIANT}, self.player)
        damage = state.has_any({ItemNames.ARCHER, ItemNames.DRYAD}, self.player)
        support = state.has_any({ItemNames.DRUID_OF_THE_CLAW, ItemNames.DRUID_OF_THE_TALON}, self.player)
        siege = state.has_any({ItemNames.GLAIVE_THROWER, ItemNames.MOUNTAIN_GIANT}, self.player)
        if self.advanced_tactics:
            conditions = sum([1 for condition in (frontline, damage, support, siege) if condition])
            return anti_air and conditions >= 3
        else:
            return anti_air and frontline and damage and support and siege

    def naga_competent_comp(self, state):
        return state.has_any({ItemNames.ROYAL_GUARD, ItemNames.COUATL}, self.player)

    racial_competent_comp = {
        WC3Race.HUMAN: human_competent_comp,
        WC3Race.ORC: orc_competent_comp,
        WC3Race.UNDEAD: undead_competent_comp,
        WC3Race.NIGHT_ELF: night_elf_competent_comp,
        WC3Race.NAGA: naga_competent_comp
    }

    def __init__(self, world: World):
        self.world: World = world
        self.player = None if world is None else world.player
        self.logic_level = get_option_value(world, 'required_tactics')
        self.advanced_tactics = self.logic_level != RequiredTactics.option_standard
        self.basic_units = {}
        for race in WC3Race:
            self.basic_units[race] = get_basic_units(world, race)
        self.enabled_campaigns = get_enabled_campaigns(world)
        self.mission_order = get_option_value(world, "mission_order")
