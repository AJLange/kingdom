"""
Utilities for weapons and armor processing.

Just stubbing these things out.
"""

from datetime import datetime
from world.combat.models import Weapon, WeaponClass, WeaponFlag

'''
these need to parse lists in the situation where
a list is given
'''

def char_weakness(char):
    weakness = char.db.weakness
    return weakness

def char_resists(char):
    resist = char.db.resist
    return resist

def check_capabilities(char):
    cap = char.db.capabilities
    return cap

def check_weapons(char):
    weapon = char.db.weapons
    return weapon

def process_elements(val):
    '''
    process to convert string to structured data to see what element was used
    '''
    return val

def process_effects(target, attacker):
    pass


def process_attack(target, attacker):
    pass



def copy_attack(target, copier):
    cap_list = copier.check_capabilities()
    copy_type = 0
    for cap in cap_list:
        if cap == "Weapon_copy":
            copy_type = "Buster"
        if cap == "Technique_copy":
            copy_type = "Technique"
    if not copy_type:
        copier.msg("You can't copy a weapon.")
        return 0
    if copy_type == "Buster":
        # copy in the order we want to copy from
        copied_wpn = copier.copy_ranged_weapon(target, copier)
        copier.msg("You copy the weapon %s from the target." % copied_wpn)
        target.msg("%s copies your weapon." % copier.db.name)
        return 0
    if copy_type == "Technique":
        # copy in the order we want to copy from
        copied_wpn = copier.copy_melee_weapon(target, copier)
        copier.msg("You copy the technique %s from the target." % copied_wpn)
        target.msg("%s copies your technique." % copier.db.name)
        return 0


def copy_melee_weapon(target):
    weapon_list = target.check_weapons()
    # by default, copy the primary weapon if no other selection is viable
    copy_this = target.db.primary
    # maybe only a primary has priority but I'll check all just in case
    for weapon in weapon_list:
        if weapon.db_flag_1 == 3 or weapon.db_flag_2 == 3:
            # a weapon has priority, so we're done, copy it
            copy_this = weapon
            return copy_this
        if target.db.primary == weapon:
            if weapon.db_class >= 4 and weapon.db_class <= 7:
                # weapon is fine, copy it
                return copy_this
        if target.db.secondary == weapon:
            if weapon.db_class >= 4 and weapon.db_class <= 7:
                return copy_this
    if not copy_this.db_class >= 4 and copy_this.db_class <=7:
        # never found a suitable weapon, so copy primary as melee
        # todo - be sure effects doesn't process null
        # be sure the effect 'stable' never copies
        new_weapon = add_weapon_to_db(copy_this.db_name,4,copy_this.db_types,copy_this.db_effects)
        return new_weapon


def copy_ranged_weapon(target, copier):
    weapon_list = target.check_weapons()
    # by default, copy the primary weapon if no other selection is viable
    copy_this = target.db.primary
    # maybe only a primary has priority but I'll check all just in case
    for weapon in weapon_list:
        if weapon.db_flag_1 == 3 or weapon.db_flag_2 == 3:
            # a weapon has priority, so we're done, copy it
            copy_this = weapon
            return copy_this
        if target.db.primary == weapon:
            if weapon.db_class >= 1 and weapon.db_class <= 3:
                # weapon is fine, copy it
                return copy_this
        if target.db.secondary == weapon:
            if weapon.db_class >= 1 and weapon.db_class <= 3:
                return copy_this
    if not copy_this.db_class >= 1 and copy_this.db_class <=3:
        # never found a suitable weapon, so copy primary as ranged
        # to-do - if my aura stat is high enough, can copy spell or will, 
        # otherwise, copy spell or will as ranged
        new_weapon = add_weapon_to_db(copy_this.db_name,1,copy_this.db_types,copy_this.db_effects)
        return new_weapon


def add_weapon_to_db(name,wpn_class,wpn_types,wpn_effects):
    fx_int = 0
    if wpn_effects:
        fx_int = process_effects(wpn_effects)
    if wpn_class.isnumeric():
        #this is already parsed, add it
        type_int = process_elements(wpn_types)
        
        if fx_int:
            weapon = Weapon(name,wpn_class,type_int,None)
        else:
            weapon = Weapon(name,wpn_class,type_int,fx_int)
    return weapon


