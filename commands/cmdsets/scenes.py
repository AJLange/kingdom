"""
Commands

Commands describe the input the account can do to the game.

"""

from math import floor
#from typing import AwaitableGenerator
from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia import default_cmds
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from evennia.comms.models import Msg
from world.scenes.models import Scene, LogEntry
from typeclasses.rooms import Room
from world.supplemental import *

from datetime import datetime




# from evennia import default_cmds

def add_participant_to_scene(character, scene):
    '''
    Given a character, checks the given scene's participants for that character and, if
    NOT present, adds the character as a participant to the scene.
    '''

    if scene.participants.filter(pk=character.id):
        return

    scene.participants.add(character)

# Borrowing these functions from SCSMUSH autologger with permission
# text replacement function stolen from https://stackoverflow.com/questions/919056/case-insensitive-replace
def ireplace(old, repl, text):
    # This function is used in highlight_names to replace names: it is not case sensitive but maintains case.
    return re.sub('(?i)'+re.escape(old), lambda m: repl, text)

def prune_sessions(session_list):
    # This function modifies the display of "who" and "+pot" so that, if the same player is connected from multiple
    # devices, their character name is only displayed once to avoid confusion. Admin still see all connected sessions.
    session_accounts = [session.account.key for session in session_list]  # get a list of just the names

    unique_accounts = set(session_accounts)
    positions = []

    for acct in unique_accounts:
        # finds positions of account name matches in the session_accounts list
        account_positions = [i for i, x in enumerate(session_accounts) if x == acct]

        # add the position of the account entry we want to the positions list
        if len(account_positions) != 1:
            positions.append(account_positions[-1])
        else:
            positions.append(account_positions[0])

    positions.sort()  # since set() unorders the initial list and we want to keep a specific printed order
    pruned_sessions = []

    for pos in positions:
        pruned_sessions.append(session_list[pos])

    return pruned_sessions

def highlight_names(source_character, in_string, self_color, others_color):
    # This function is used in tailored_msg.
    if self_color is None:
        self_color = "550"

    if others_color is None:
        others_color = "055"

    # find all characters in current room
    char_list = source_character.location.contents_get(exclude=source_character.location.exits)
    name_list = []
    self_name_list = [] # These are necessary to color the source character's name separately
    full_list = []
    self_full_list = []

    # generate a list of all names of said characters, including aliases
    for character in char_list:
        name_list.append(character.key)
        name_list += character.aliases.all()
        if character == source_character:
            self_name_list.append(character.key)
            self_name_list += character.aliases.all()

    # generate a list of all occurrences of the name in the input string. This will allow us to print the names
    # exactly as they were written, without overriding case
    for name in name_list:
        full_list += re.findall(re.compile(re.escape(name), re.IGNORECASE), in_string)
        if name in self_name_list:
            self_full_list += re.findall(re.compile(re.escape(name), re.IGNORECASE), in_string)

    out_string = in_string
    # for each of the names in the list, replace the string with a colored version
    for name in full_list:
        if name in self_full_list:
            out_string = ireplace(name, "|" + self_color + name + "|n", out_string)
        else:
            out_string = ireplace(name, "|" + others_color + name + "|n", out_string)

    return out_string

def tailored_msg(caller, msg):
    # the point of this function is to
    # 1. Get a list of character objects in the room
    # 2. For each character, check whether names should be colored
    # 3. And custom color the names so that the receiving character's name is highlighted a different color
    char_list = caller.location.contents_get(exclude=caller.location.exits)
    # for char in char_list:
    #     caller.msg("{0}".format(char))

    for character in char_list:
        everyone_else = caller.location.contents_get(exclude=caller.location.exits)
        everyone_else.remove(character)
        # for char in everyone_else:
        #     caller.msg("{0}".format(char))
        # caller.msg("pose_colors_self for {0} is {1}".format(character, character.db.pose_colors_self))
        # caller.msg("pose_colors_others for {0} is {1}".format(character, character.db.pose_colors_others))
        # caller.msg("pose_colors_on for {0} is {1}".format(character, character.db.pose_colors_on))

        if character.db.pose_colors_on:
            caller.location.msg_contents(text=(highlight_names(character, msg, character.db.pose_colors_self,
                                                                    character.db.pose_colors_others),
                                                    {"type": "pose"}),
                                              exclude=everyone_else,
                                              from_obj=caller)
        else:
            caller.location.msg_contents(text=(msg, {"type": "pose"}),
                                              exclude=everyone_else,
                                              from_obj=caller)
    return


class CmdPot(default_cmds.MuxCommand):
    """
    View the pose tracker (pot). The pose tracker displays the name,
    time connected, time idle, and time since last posed of every
    character in the room, ordered starting with whomever posed
    longest ago. Thus, during an ongoing scene, the person whose
    turn it is to pose will appear at the top of the list.
    Those who have not posed are listed below all those who have.
    To signify that you are leaving an ongoing scene, type +observe
    to reset your pose timer and move to the bottom (see "help observe").
    Usage:
      +pot
    """

    key = "+pot"
    aliases = ["pot"]
    locks = "cmd:all()"

    # this is used by the parent
    account_caller = True

    def func(self):
        """
        Get all connected accounts by polling session.
        """

        account = self.account
        all_sessions = SESSIONS.get_sessions()

        all_sessions = sorted(all_sessions, key=lambda o: o.account.character.get_pose_time()) # sort by last posed time
        pruned_sessions = prune_sessions(all_sessions)

        naccounts = SESSIONS.account_count()
        table = self.styled_table(
            "|wCharacter",
            "|wOn for",
            "|wIdle",
            "|wLast posed"
        )

        old_session_list = []

        for session in pruned_sessions:
            if not session.logged_in:
                continue

            session_account = session.get_account()
            puppet = session.get_puppet()
            delta_cmd = time.time() - session.cmd_last_visible
            delta_conn = time.time() - session.conn_time
            delta_pose_time = time.time() - puppet.get_pose_time()

            if delta_pose_time > 3600:
                old_session_list.append(session)
                continue

            if puppet.location == self.caller.character.location:
                # logic for setting up pose table
                table.add_row(puppet.key,
                              utils.time_format(delta_conn, 0),
                              utils.time_format(delta_cmd, 1),
                              utils.time_format(delta_pose_time, 1))

        for session in old_session_list:
            session_account = session.get_account()
            puppet = session.get_puppet()
            delta_cmd = time.time() - session.cmd_last_visible
            delta_conn = time.time() - session.conn_time
            delta_pose_time = time.time() - puppet.get_pose_time()

            if puppet.location == self.caller.character.location:
                if puppet.get_obs_mode() == True:
                    table.add_row("|y" + puppet.key + " (O)",
                                  utils.time_format(delta_conn, 0),
                                  utils.time_format(delta_cmd, 1),
                                  "-")
                else:
                    table.add_row(puppet.key,
                                  utils.time_format(delta_conn, 0),
                                  utils.time_format(delta_cmd, 1),
                                  "-")

        self.caller.msg(table)

class CmdObserve(default_cmds.MuxCommand):
    """
        Enter observer mode. This signifies that you are observing,
        and not participating, in a scene. In +pot, you will be
        displayed at the bottom of the list with an "(O)" before
        your name. If you have previously posed, your pose timer
        will also be reset.
        If your character is leaving an ongoing scene, +observe
        will help to  prevent anyone accidentally waiting on a pose
        from you.
        Usage:
          +observe
    """

    key = "+observe"
    aliases = ["observe"]
    locks = "cmd:all()"

    def func(self):
        self.caller.set_pose_time(0.0)
        self.caller.set_obs_mode(True)
        self.msg("Entering observer mode.")
        self.caller.location.msg_contents(
            "|y<SCENE>|n {0} is now an observer.".format(self.caller.name))




class CmdEvent(default_cmds.MuxCommand):
    """
    The @event command is used to log scenes.
    Usage:
            @event/start: Create a scene and begin logging poses in the current room.
            @event/stop: Stop the log currently running in the room.
            @event/info: Display the current log's ID number, name, etc.
            @event/name [string]: Set the current log's name as [string].
            @event/desc [string]: Set the current log's desc as [string].
    """

    key = "@event"
    aliases = ["event", "@scene", "scene"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        if not self.switches:
            caller.msg("You must add a switch, like '@event/start' or '@event/stop'.")
            return

        elif "start" in self.switches:
            # Make sure the current room doesn't already have an active event, and otherwise mark it
            if caller.location.db.active_event:
                caller.msg("There is currently an active event running in this room already.")
                return
            caller.location.db.active_event = True
            event = Scene.objects.create(
                name='Unnamed Event',
                start_time=datetime.now(),
                description='Placeholder description of scene plz change k thx bai',
                location=caller.location,
            )

            caller.msg("DEBUG: this event has the following information:\nname = {0}\ndescription = {1}\nlocation = {2}\nid = {3}".format(event.name, event.description, event.location, event.id))

            caller.location.db.event_id = event.id

            self.caller.location.msg_contents("|y<SCENE>|n A log has been started in this room with scene ID {0}.".format(event.id))
            return

        elif "stop" in self.switches:
            # Make sure the current room's event hasn't already been stopped
            if not caller.location.db.active_event:
                caller.msg("There is no active event running in this room.")
                return

            # Find the scene object that matches the scene/event reference on the
            # location.
            try:
                events = Scene.objects.filter(id=caller.location.db.event_id).get()
            except Exception as original:
                raise Exception("Found zero or multiple Scenes :/") from original

            # Stop the Room's active event by removing the active event attribute.
            Scene.objects.filter(id=caller.location.db.event_id).update(end_time=datetime.now())
            self.caller.location.msg_contents("|y<SCENE>|n A log has been stopped in this room with scene ID {0}.".format(events.id))
            del caller.location.db.active_event
            return

        elif "info" in self.switches:
            # First, check that there is a log running.
            if not caller.location.db.active_event:
                caller.msg("There is no active event running in this room.")
                return

            # Find the scene object that matches the scene/event reference on the
            # location.
            try:
                events = Scene.objects.filter(id=caller.location.db.event_id).get()
            except Exception as original:
                raise Exception("Found zero or multiple Scenes :/") from original

            caller.msg("This event has the following information:\nName = {0}\nDescription = {1}\nLocation = {2}\nID = {3}".format(events.name, events.description, events.location, events.id))

        elif "name" in self.switches:
            # First, check that there is a log running.
            if not caller.location.db.active_event:
                caller.msg("There is no active event running in this room.")
                return

            # Then, check that the user has inputted a string.
            if not self.args:
                caller.msg("Name the log what?")
                return

            # Find the scene object that matches the scene/event reference on the
            # location.
            try:
                events = Scene.objects.filter(id=caller.location.db.event_id).get()
            except Exception as original:
                raise Exception("Found zero or multiple Scenes :/") from original

            Scene.objects.filter(id=caller.location.db.event_id).update(name=self.args)
            caller.msg("Scene name set.")

        elif "desc" in self.switches:
            # First, check that there is a log running.
            if not caller.location.db.active_event:
                caller.msg("There is no active event running in this room.")
                return

            # Then, check that the user has inputted a string.
            if not self.args:
                caller.msg("Name the log description what?")
                return

            # Find the scene object that matches the scene/event reference on the
            # location.
            try:
                events = Scene.objects.filter(id=caller.location.db.event_id).get()
            except Exception as original:
                raise Exception("Found zero or multiple Scenes :/") from original

            Scene.objects.filter(id=caller.location.db.event_id).update(description=self.args)
            caller.msg("Scene description set.")

