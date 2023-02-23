'''
Stages code. This is like Places, but not.

We want stages to broadcast, to organize big scenes, rather
than be private stages that don't broadcast out, so everything
should hit the main room.

'''

from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils.utils import list_to_string
from typeclasses.cities import Stage
from evennia import default_cmds, create_object
from evennia.utils import utils, create
from server.utils import sub_old_ansi
from evennia import ObjectDB



def get_movement_message(verb, stage):
    """Returns the movement message for joining/leaving a stage"""
    if not stage or not stage.key:
        return "You %s the stage." % verb
    prefix = stage.key.split()[0]
    article = ""
    if prefix.lower() not in ("the", "a", "an"):
        article = "the "
    return "You %s %s%s." % (verb, article, stage.key)


# ------------------------------------------------------------
# Commands defined for stages
# ------------------------------------------------------------


class CmdMakeStage(MuxCommand):
    """
    Create a stage.

    Usage:
        makestage <name of stage>
        makestage <name> = <desc>
        eg
        makestage Dinosaur Tank
        makestage Dinosaur Tank = <stage desc>

    A stage is an object that can be entered.
    It does not behave like a room; it simply shows a relative location 
    of players to ease in the creation of setpieces that may have 
    multiple sub-locations.

    Optionally, you can desc the stage when creating it, or use the 
    setstage command to desc after the fact.

    All poses done inside a stage append the name of the stage to the 
    front of the pose, for ease of readability.

    Stages are typically temporary, so use +clearstage to remove them
    when you are done using them.

    """

    key = "makestage"
    alias = "+makestage"
    locks = "cmd:all()"
    help_category = "Scenes"
    
    new_obj_lockstring = (
        "control:id({id}) or perm(Admin); "
        "delete:id({id}) or perm(Admin); "
        "edit:id({id}) or perm(Admin)"
        )
    
    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Syntax: stage <name of stage>")
            return

        ''' to do: the rest of the command '''

        if not caller.check_permstring("builders"):
            caller.db.stagequota = caller.db.stagequota -1
        
        #subtract from my available quota and make an object with no special properties.

        if caller.db.stagequota < 1:
            caller.msg("Sorry, you can't make any more stages.")
            return

        if not self.args:
            caller.msg("Usage: makestage <Name of item>")
            return

        iname = self.args
        
        new_obj = create_object("cities.Stage",key=iname,location=caller.location,locks="edit:id(%i) and perm(Builders);call:false()" % caller.id)

        lockstring = self.new_obj_lockstring.format(id=caller.id)
        new_obj.locks.add(lockstring)
        new_obj.db.owner = caller
        
        try:
            caller.msg("You created the stage %s." % str(new_obj))
        except:
            caller.msg("Can't create %s." % str(new_obj))
            return



class CmdSetStage(MuxCommand):
    """
    Describe a stage.

    Usage:
      setstage <name>=Description
      eg
      setstage Dinosaur Tank=It's the Dinosaur Tank!

    Describe a stage. This description will be visible when
    looking at the stage, or when entering it. Describing 
    a stage is optional.

    """

    key = "setstage"
    alias = "+setstage"
    locks = "cmd:all()"
    help_category = "Scenes"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Syntax: stage <number>=<Desc>")
            return

        ''' to do: the rest of the command '''

class CmdClearStage(MuxCommand):
    """
    Clears away all the stages in the room which were made
    by you.

    clearstage
    

    A stage is an object that can be entered.
    It does not behave like a room; it simply shows a relative location 
    of players to ease in the creation of setpieces that may have 
    multiple sub-locations.

    All poses done inside a stage append the name of the stage to the 
    front of the pose, for ease of readability.

    """

    key = "clearstage"
    aliases = ["+clearstage", "clearstages","+clearstages"]
    locks = "cmd:all()"
    help_category = "Scenes"
    

    def func(self):
        """Implements command"""
        caller = self.caller
        args = self.args

        if not args:
            caller.msg("Syntax: stage <name of stage>")
            return


class CmdJoin(MuxCommand):
    """
    Enters a particular stage.

    Usage:
        join <stage #>

    Enters a stage in the room.
    
    Posing while in a stage will append the location of the 
    stage to your pose. This is for organizing plot scenes 
    that technically take place in more than one location.

    To leave, use 'depart'.
    """

    key = "join"
    locks = "cmd:all()"
    help_category = "Scenes"

    def func(self):
        """Implements command"""
        caller = self.caller
        all_stages = caller.location.stages
        stage = caller.sitting_at_stage
        args = self.args
        if not args or not args.strip("#").strip().isdigit():
            caller.msg("Usage: {wjoin <stage #>{n")
            caller.msg("To see a list of stages: {wstages{n")
            return
        if stage:
            stage.leave(caller)
        # The player probably only has this command if it's in their inventory
        if not all_stages:
            caller.msg("This room has no stages.")
            return
        args = args.strip("#").strip()
        args = int(args) - 1
        if not (0 <= args < len(all_stages)):
            caller.msg("Number specified does not match any of the stages here.")
            return
        stage = all_stages[args]
        occupants = stage.item_data.occupants
        if len(occupants) >= stage.item_data.max_spots:
            caller.msg("There is no room at %s." % stage.key)
            return
        stage.join(caller)
        caller.msg(get_movement_message("join", stage))


class CmdListStages(MuxCommand):
    """
    Lists stages in current room.

    Usage:
        stages

    Lists all the stages in the current room that you can enter,
    and which players are in which stage.
    
    If there any stages within the room, the 'join' command will 
    be available. 
    
    Posing while in a stage will append the location of the stage 
    to your pose. This is for organizing plot scenes that technically 
    take place in more than one location. There's no coded limit to how
    many people can be in the same stage, but scene-runners may set
    soft limits.

    Logging out or disconnecting will require you to join a stage 
    once more. To leave a stage on your own, use 'depart'.
    """

    key = "stages"
    alias = "+stages"
    locks = "cmd:all()"
    help_category = "Scenes"

    def func(self):
        """Implements command"""
        caller = self.caller
        stages = caller.location.stages
        caller.msg("{wStages here:{n")
        caller.msg("{w------------{n")
        if not stages:
            caller.msg("No stages found.")
            return
        for num in range(len(stages)):
            p_name = stages[num].key
            max_spots = stages[num].item_data.max_spots
            occupants = stages[num].item_data.occupants
            spots = max_spots - len(occupants)
            caller.msg("%s (#%s) : %s empty spaces" % (p_name, num + 1, spots))
            if occupants:
                # get names
                names = [ob.name for ob in occupants if ob.access(caller, "view")]
                caller.msg("-Occupants: %s" % list_to_string(names))


class CmdDepart(MuxCommand):
    """
    Leaves your current stage. 

    Usage:
        depart

    Leaves your current stage. Logging out or disconnecting will
    cause you to leave automatically. To see available stages,
    use 'stages'. To join a stage, use 'join'.
    """

    key = "depart"
    locks = "cmd:all()"
    help_category = "Scenes"

    def func(self):
        """Implements command"""
        caller = self.caller
        stage = caller.sitting_at_stage
        if not stage:
            caller.msg("You are not in a stage.")
            return
        stage.leave(caller)
        caller.msg(get_movement_message("leave", stage))


class CmdStageMute(MuxCommand):
    """
    Mutes stages you aren't in.

    Usage:
        +stagemute

    Stages are sub-locations meant to split up RP during plot scenes.
    If you are in a stage, you may want to mute the output of stages
    you are not in to cut down on screen spam. To do this, use the
    +stagemute command.

    This command only works if you are in a stage. 

    This is a toggle; to turn off stagemute, just use the +stagemute 
    command again. If you leave the stage you are in, other stages
    automatically unmute.
    """

    key = "stagemute"
    alias= "+stagemute"
    locks = "cmd:all()"
    help_category = "Scenes"
    # characters used for poses/emits
    char_symbols = (";", ":", "|")

    def func(self):
        """Implement this command"""
        return
        



'''
notes here on player quotas:
10 items
10 personal rooms
10 stages

per player character.
Pets can only be created by staff for now (may change later)

'''

