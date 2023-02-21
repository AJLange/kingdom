from evennia.commands.default.muxcommand import MuxCommand
from evennia import default_cmds, create_object
from evennia.utils import utils, create

from typeclasses.objects import MObject
from typeclasses.gear import Item


class CmdCraft(MuxCommand):
    """
    Create a small object.
    Players will have a limited quota of miscellaneous objects.
    These objects can hold a desc, but have no other 
    functionality. 

    Usage:
        craft <name of object>
        eg
        craft Soccer Ball

    To desc your craft, use the +craftdesc command.
    To delete a craft you no longer need, use +junk.

    """

    key = "craft"
    locks = "cmd:all()"
    help_category = "Building"
    

    
    def func(self):
        """Implements command"""
        caller = self.caller
        '''
        check if I'm an admin. If I'm not admin, check and see if I have quota.
        '''
        if not caller.check_permstring("builders"):
            caller.db.craftquota = caller.db.craftquota -1
        
        #subtract from my available quota and make an object with no special properties.

        if caller.db.craftquota < 1:
            caller.msg("Sorry, you are out of craft quota. +junk a craft to proceed.")
            return

        if not self.args:
            caller.msg("Usage: craft <Name of item>")
            return

        iname = self.args
        
        p_item = create_object("gear.Item",key=iname,location=caller.location,locks="edit:id(%i) and perm(Builders);call:false()" % caller.id)
        '''
        link entry room to city created
        '''
        # Create the new room

        new_obj = create.create_object(Item, iname, report_to=caller)
        lockstring = self.new_obj_lockstring.format(id=caller.id)
        new_obj.locks.add(lockstring)
        new_obj.db.protector = []
        new_obj.db.protector.append(caller)
        new_obj.db.owner = caller
        
        try:
            p_item.db.entry = new_obj
        except:
            caller.msg("Can't create %s." % new_obj)
            return

class CmdCraftDesc(MuxCommand):
    """
    Write the desc for a small object that you have created.

    Usage:
        craftdesc <name of object>=<desc>
        eg
        craftdesc Soccer Ball=A round ball for kicking!

    Craftdesc will search for all items that you own regardless
    of where you have left or dropped them.
    
    To make a craft, use +craft.
    To delete a craft, use +junk.
    
    """

    key = "craft"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("What do you want to desc?")
            return

        '''
        to-do, the command
        '''


class CmdJunkCraft(MuxCommand):
    """
    Destroy a crafted personal item that you don't need anymore.

    Usage:
        junk <name of object>
        eg
        junk Soccer Ball

    Junking can only occur with an item in your possession or
    in the same room as you, to prevent accidental junking.

    Junking an item will free up your quota to create a new
    item.
    
    To make a craft, use +craft.
    
    """

    key = "craft"
    locks = "cmd:all()"
    help_category = "Building"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("What do you want to desc?")
            return

        '''
        to-do, the command
        '''



'''
notes here on player quotas:
10 items
10 personal rooms
10 stages

per player character.
Pets can only be created by staff for now (may change later)

Also add the ability for staff to easily increase someone's quota or 
alter that quota if necessary.

'''