"""
Home of mail and radio commands

"""


from evennia import default_cmds
from commands.command import CmdAbilities
from evennia import CmdSet
from commands import command
from commands.base import BaseCommand
from server.utils import sub_old_ansi
from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from evennia.comms.models import Msg
from evennia.commands.default.muxcommand import MuxCommand


class CmdMail(default_cmds.MuxAccountCommand):
    """
    Communicate with others by sending mail.
    Usage:
      @mail       - Displays all the mail an account has in their mailbox
      @mail <#>   - Displays a specific message
      @mail <accounts>=<subject>/<message>
              - Sends a message to the comma separated list of accounts.
      @mail/delete <#> - Deletes a specific message
      @mail/forward <account list>=<#>[/<Message>]
              - Forwards an existing message to the specified list of accounts,
                original message is delivered with optional Message prepended.
      @mail/reply <#>=<message>
              - Replies to a message #. Prepends message to the original
                message text.
    Switches:
      delete  - deletes a message
      forward - forward a received message to another object with an optional message attached.
      reply   - Replies to a received message, appending the original message to the bottom.
    Examples:
      @mail 2
      @mail Griatch=New mail/Hey man, I am sending you a message!
      @mail/delete 6
      @mail/forward feend78 Griatch=4/You guys should read this.
      @mail/reply 9=Thanks for the info!
    """

    key = "@mail"
    aliases = ["mail"]
    lock = "cmd:all()"
    help_category = "General"

    # These used to be global settings in the original code, but nothing else needs access to them.
    _HEAD_CHAR = "|015-|n"
    _SUB_HEAD_CHAR = "-"
    _WIDTH = 78

    # This is the @mail command from contrib. We have added MUSH parsing to sending @mail.
    def parse(self):
        """
        Add convenience check to know if caller is an Account or not since this cmd
        will be able to add to either Object- or Account level.
        """
        super().parse()
        self.caller_is_account = bool(
            inherits_from(self.caller, "evennia.accounts.accounts.DefaultAccount")
        )

    def search_targets(self, namelist):
        """
        Search a list of targets of the same type as caller.
        Args:
            caller (Object or Account): The type of object to search.
            namelist (list): List of strings for objects to search for.
        Returns:
            targetlist (Queryset): Any target matches.
        """
        nameregex = r"|".join(r"^%s$" % re.escape(name) for name in make_iter(namelist))
        if self.caller_is_account:
            matches = AccountDB.objects.filter(username__iregex=nameregex)
        else:
            matches = ObjectDB.objects.filter(db_key__iregex=nameregex)
        return matches

    def get_all_mail(self):
        """
        Returns a list of all the messages where the caller is a recipient. These
            are all messages tagged with tags of the `mail` category.
        Returns:
            messages (QuerySet): Matching Msg objects.
        """
        if self.caller_is_account:
            return Msg.objects.get_by_tag(category="mail").filter(db_receivers_accounts=self.caller)
        else:
            return Msg.objects.get_by_tag(category="mail").filter(db_receivers_objects=self.caller)

    def send_mail(self, recipients, subject, message, caller):
        """
        Function for sending new mail.  Also useful for sending notifications
        from objects or systems.
        Args:
            recipients (list): list of Account or Character objects to receive
                the newly created mails.
            subject (str): The header or subject of the message to be delivered.
            message (str): The body of the message being sent.
            caller (obj): The object (or Account or Character) that is sending the message.
        """
        for recipient in recipients:
            recipient.msg("You have received a new @mail from %s" % caller)
            new_message = create.create_message(
                self.caller, sub_old_ansi(message), receivers=recipient, header=subject
            )
            new_message.tags.add("new", category="mail")

        if recipients:
            caller.msg("You sent your message.")
            return
        else:
            caller.msg("No valid target(s) found. Cannot send message.")
            return

    def func(self):
        """
        Do the events command functionality
        """

        subject = ""
        body = ""

        if self.switches or self.args:
            if "delete" in self.switches or "del" in self.switches:
                try:
                    if not self.lhs:
                        self.caller.msg("No Message ID given. Unable to delete.")
                        return
                    else:
                        all_mail = self.get_all_mail()
                        mind_max = max(0, all_mail.count() - 1)
                        mind = max(0, min(mind_max, int(self.lhs) - 1))
                        if all_mail[mind]:
                            mail = all_mail[mind]
                            question = "Delete message {} ({}) [Y]/N?".format(mind + 1, mail.header)
                            ret = yield (question)
                            # handle not ret, it will be None during unit testing
                            if not ret or ret.strip().upper() not in ("N", "No"):
                                all_mail[mind].delete()
                                self.caller.msg("Message %s deleted" % (mind + 1,))
                            else:
                                self.caller.msg("Message not deleted.")
                        else:
                            raise IndexError
                except IndexError:
                    self.caller.msg("That message does not exist.")
                except ValueError:
                    self.caller.msg("Usage: @mail/delete <message ID>")
            elif "forward" in self.switches or "fwd" in self.switches:
                try:
                    if not self.rhs:
                        self.caller.msg(
                            "Cannot forward a message without a target list. " "Please try again."
                        )
                        return
                    elif not self.lhs:
                        self.caller.msg("You must define a message to forward.")
                        return
                    else:
                        all_mail = self.get_all_mail()
                        mind_max = max(0, all_mail.count() - 1)
                        if "/" in self.rhs:
                            message_number, message = self.rhs.split("/", 1)
                            mind = max(0, min(mind_max, int(message_number) - 1))

                            if all_mail[mind]:
                                old_message = all_mail[mind]

                                self.send_mail(
                                    self.search_targets(self.lhslist),
                                    "FWD: " + old_message.header,
                                    message
                                    + "\n---- Original Message ----\n"
                                    + old_message.message,
                                    self.caller,
                                )
                                self.caller.msg("Message forwarded.")
                            else:
                                raise IndexError
                        else:
                            mind = max(0, min(mind_max, int(self.rhs) - 1))
                            if all_mail[mind]:
                                old_message = all_mail[mind]
                                self.send_mail(
                                    self.search_targets(self.lhslist),
                                    "FWD: " + old_message.header,
                                    "\n---- Original Message ----\n" + old_message.message,
                                    self.caller,
                                )
                                self.caller.msg("Message forwarded.")
                                old_message.tags.remove("new", category="mail")
                                old_message.tags.add("fwd", category="mail")
                            else:
                                raise IndexError
                except IndexError:
                    self.caller.msg("Message does not exist.")
                except ValueError:
                    self.caller.msg("Usage: @mail/forward <account list>=<#>[/<Message>]")
            elif "reply" in self.switches or "rep" in self.switches:
                try:
                    if not self.rhs:
                        self.caller.msg("You must define a message to reply to.")
                        return
                    elif not self.lhs:
                        self.caller.msg("You must supply a reply message")
                        return
                    else:
                        all_mail = self.get_all_mail()
                        mind_max = max(0, all_mail.count() - 1)
                        mind = max(0, min(mind_max, int(self.lhs) - 1))
                        if all_mail[mind]:
                            old_message = all_mail[mind]
                            self.send_mail(
                                old_message.senders,
                                "RE: " + old_message.header,
                                self.rhs + "\n---- Original Message ----\n" + old_message.message,
                                self.caller,
                            )
                            old_message.tags.remove("new", category="mail")
                            old_message.tags.add("-", category="mail")
                            return
                        else:
                            raise IndexError
                except IndexError:
                    self.caller.msg("Message does not exist.")
                except ValueError:
                    self.caller.msg("Usage: @mail/reply <#>=<message>")
            else:
                # normal send
                if self.rhs:
                    if "/" in self.rhs:
                        subject, body = self.rhs.split("/", 1)
                    else:
                        body = self.rhs
                    self.send_mail(self.search_targets(self.lhslist), subject, body, self.caller)
                else:
                    all_mail = self.get_all_mail()
                    mind_max = max(0, all_mail.count() - 1)
                    try:
                        mind = max(0, min(mind_max, int(self.lhs) - 1))
                        message = all_mail[mind]
                    except (ValueError, IndexError):
                        self.caller.msg("'%s' is not a valid mail id." % self.lhs)
                        return

                    messageForm = []
                    if message:
                        messageForm.append(_HEAD_CHAR * _WIDTH)
                        messageForm.append(
                            "|wFrom:|n %s" % (message.senders[0].get_display_name(self.caller))
                        )
                        # note that we cannot use %-d format here since Windows does not support it
                        day = message.db_date_created.day
                        messageForm.append(
                            "|wSent:|n %s"
                            % message.db_date_created.strftime(f"%b {day}, %Y - %H:%M:%S")
                        )
                        messageForm.append("|wSubject:|n %s" % message.header)
                        messageForm.append(_SUB_HEAD_CHAR * _WIDTH)
                        messageForm.append(message.message)
                        messageForm.append(_HEAD_CHAR * _WIDTH)
                    self.caller.msg("\n".join(messageForm))
                    message.tags.remove("new", category="mail")
                    message.tags.add("-", category="mail")

        else:
            # list messages
            messages = self.get_all_mail()

            if messages:
                table = evtable.EvTable(
                    "|wID|n",
                    "|wFrom|n",
                    "|wSubject|n",
                    "|wArrived|n",
                    "",
                    table=None,
                    border="header",
                    header_line_char=_SUB_HEAD_CHAR,
                    width=_WIDTH,
                )
                index = 1
                for message in messages:
                    status = str(message.db_tags.last().db_key.upper())
                    if status == "NEW":
                        status = "|gNEW|n"

                    table.add_row(
                        index,
                        message.senders[0].get_display_name(self.caller),
                        message.header,
                        datetime_format(message.db_date_created),
                        status,
                    )
                    index += 1

                table.reformat_column(0, width=6)
                table.reformat_column(1, width=18)
                table.reformat_column(2, width=34)
                table.reformat_column(3, width=13)
                table.reformat_column(4, width=7)

                self.caller.msg(_HEAD_CHAR * _WIDTH)
                self.caller.msg(str(table))
                self.caller.msg(_HEAD_CHAR * _WIDTH)
            else:
                self.caller.msg("There are no messages in your inbox.")


class CmdWhisper(MuxCommand):
    """
    whisper - send private IC message

    Usage:
      whisper [<player>,<player>,... = <message>]
      whisper =<message> - sends whisper to last person you whispered
      whisper <name> <message>
      whisper/list <number> - Displays list of last <number> of recent whispers

    Switch:
      last - shows who you last messaged
      list - show your last <number> of messages (default)

    Send an IC message to a character in your room. A whisper of the format
    "whisper player=Hello" will send a message in the form of "You whisper
    <player>". A whisper of the format "whisper player=:does an emote" will appear
    in the form of "Discreetly, soandso does an emote" to <player>. 

    Whispering to another player in the room emits to the room a message that 
    a whisper occured between you, but not the message. Whisper accepts
    multiple targets.

    Characters with the enhanced_senses ability can overhear the text of
    whispers.

    If no argument is given, you will get a list of your whispers from this
    session.
    """

    key = "whisper"
    aliases = ["+whisper"]
    locks = "cmd:not pperm(page_banned)"
    help_category = "Social"
    simplified_key = "mutter"

    def func(self):
        """Implement function using the Msg methods"""

        # this is a MuxCommand, which means caller will be a Character.
        caller = self.caller
        # get the messages we've sent (not to channels)
        if not caller.ndb.whispers_sent:
            caller.ndb.whispers_sent = []
        pages_we_sent = caller.ndb.whispers_sent
        # get last messages we've got
        if not caller.ndb.whispers_received:
            caller.ndb.whispers_received = []
        pages_we_got = caller.ndb.whispers_received

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(str(obj) for obj in pages_we_sent[-1].receivers)
                self.msg(
                    "You last whispered {c%s{n:%s" % (recv, pages_we_sent[-1].message)
                )
                return
            else:
                self.msg("You haven't whispered anyone yet.")
                return

        if not self.args or "list" in self.switches:
            pages = list(pages_we_sent) + list(pages_we_got)
            pages.sort(key=lambda x: x.date_created)

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: whisper [<player> = msg]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "{w%s{n {c%s{n whispered to {c%s{n: %s"
            lastpages = "\n ".join(
                template
                % (
                    utils.datetime_format(page.date_created),
                    ",".join(obj.name for obj in page.senders),
                    "{n,{c ".join([obj.name for obj in page.receivers]),
                    page.message,
                )
                for page in lastpages
            )

            if lastpages:
                string = "Your latest whispers:\n %s" % lastpages
            else:
                string = "You haven't whispered anyone yet."
            self.msg(string)
            return
        # We are sending. Build a list of targets
        lhs = self.lhs
        rhs = self.rhs
        lhslist = self.lhslist
        if not self.rhs:
            # MMO-type whisper. 'whisper <name> <target>'
            arglist = self.args.lstrip().split(" ", 1)
            if len(arglist) < 2:
                caller.msg(
                    "The MMO-style whisper format requires both a name and a message."
                )
                caller.msg(
                    "To send a message to your last whispered character, use {wwhisper =<message>"
                )
                return
            lhs = arglist[0]
            rhs = arglist[1]
            lhslist = set(arglist[0].split(","))

        if not lhs and rhs:
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to whisper?")
                return
        else:
            receivers = lhslist

        #todo, emit that the person whispered to the room.

        recobjs = []
        for receiver in set(receivers):

            if isinstance(receiver, string_types):
                pobj = caller.search(receiver, use_nicks=True)
            elif hasattr(receiver, "character"):
                pobj = receiver.character
            elif hasattr(receiver, "player"):
                pobj = receiver
            else:
                self.msg("Who do you want to whisper?")
                return
            if pobj:
                if hasattr(pobj, "has_account") and not pobj.has_account:
                    self.msg("You may only send whispers to online characters.")
                elif not pobj.location or pobj.location != caller.location:
                    self.msg("You may only whisper characters in the same room as you.")
                else:
                    recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to whisper.")
            return
        header = "{c%s{n whispers," % caller.name
        message = rhs
        mutter_text = ""
        # if message begins with a :, we assume it is a 'whisper-pose'
        if message.startswith(":"):
            message = "%s {c%s{n %s" % (
                "Discreetly,",
                caller.name,
                message.strip(":").strip(),
            )
            is_a_whisper_pose = True
        elif message.startswith(";"):
            message = "%s {c%s{n%s" % (
                "Discreetly,",
                caller.name,
                message.lstrip(";").strip(),
            )
            is_a_whisper_pose = True
        else:
            is_a_whisper_pose = False
            message = '"' + message + '"'

        # create the temporary message object
        temp_message = TempMsg(senders=caller, receivers=recobjs, message=message)

        caller.ndb.whispers_sent.append(temp_message)

        # tell the players they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            otherobs = [ob for ob in recobjs if ob != pobj]
            if not pobj.access(caller, "tell"):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            if is_a_whisper_pose:
                omessage = message
                if otherobs:
                    omessage = "(Also sent to %s.) %s" % (
                        ", ".join(ob.name for ob in otherobs),
                        message,
                    )
                pobj.msg(omessage, from_obj=caller, options={"is_pose": True})
            else:
                if otherobs:
                    myheader = header + " to {cyou{n and %s," % ", ".join(
                        "{c%s{n" % ob.name for ob in otherobs
                    )
                else:
                    myheader = header
                pobj.msg(
                    "%s %s" % (myheader, message),
                    from_obj=caller,
                    options={"is_pose": True},
                )
            if not pobj.ndb.whispers_received:
                pobj.ndb.whispers_received = []
            pobj.ndb.whispers_received.append(temp_message)
            if hasattr(pobj, "has_account") and not pobj.has_account:
                received.append("{C%s{n" % pobj.name)
                rstrings.append(
                    "%s is offline. They will see your message if they list their pages later."
                    % received[-1]
                )
            else:
                received.append("{c%s{n" % pobj.name)
                # afk = pobj.player_ob and pobj.player_ob.db.afk
                # if afk:
                #     pobj.msg("{wYou inform {c%s{w that you are AFK:{n %s" % (caller, afk))
                #     rstrings.append("{c%s{n is AFK: %s" % (pobj.name, afk))
        if rstrings:
            self.msg("\n".join(rstrings))
        if received:
            if is_a_whisper_pose:
                self.msg("You posed to %s: %s" % (", ".join(received), message))
            else:
                self.msg("You whispered to %s, %s" % (", ".join(received), message))
                if "mutter" in self.switches or "mutter" in self.cmdstring:
                    from random import randint

                    word_list = rhs.split()
                    chosen = []
                    num_real = 0
                    for word in word_list:
                        if randint(0, 2):
                            chosen.append(word)
                            num_real += 1
                        else:
                            chosen.append("...")
                    if num_real:
                        mutter_text = " ".join(chosen)
                if mutter_text:
                    emit_string = ' mutters, "%s{n"' % mutter_text
                    exclude = [caller] + recobjs
                    caller.location.msg_action(
                        self.caller,
                        emit_string,
                        options={"is_pose": True},
                        exclude=exclude,
                    )
                    self.mark_command_used()
        caller.posecount += 1


class CmdMutter(MuxCommand):
    """
    Mutter - send private IC message

    Usage:
      mutter [<player>,<player>,... = <message>]
      mutter =<message> - sends mutter to last person you muttered to
      mutter <name> <message>
      mutter/self message
      mutter/list <number> - Displays list of last <number> of recent whispers

    Switch:
      last - shows who you last messaged
      list - show your last <number> of messages (default)


    Send an IC message to a character in your room. A whisper of the format
    "mutter player=Hello" will send a message in the form of "You mutter to
    <player>". A mutter of the format "mutter player=:does an emote" will appear
    in the form of "Discreetly, soandso does an emote" to <player>. 
    Some of what you mutter will be overheard by the room, but not all of it.
    It's possible to mutter to a list of targets.
    
    Characters with the enhanced senses ability can hear all of a mutter.

    The switch mutter/self does the partial pose to yourself, just for people
    overhearing the partial mutter.

    If no argument is given, you will get a list of your mutters from this session.
    """

    key = "mutter"
    aliases = ["+mutter"]
    locks = "cmd:not pperm(page_banned)"
    help_category = "Social"
    simplified_key = "mutter"

    def func(self):
        """Implement function using the Msg methods"""

        # this is a MuxCommand, which means caller will be a Character.
        caller = self.caller
        # get the messages we've sent (not to channels)
        if not caller.ndb.whispers_sent:
            caller.ndb.whispers_sent = []
        pages_we_sent = caller.ndb.whispers_sent
        # get last messages we've got
        if not caller.ndb.whispers_received:
            caller.ndb.whispers_received = []
        pages_we_got = caller.ndb.whispers_received

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(str(obj) for obj in pages_we_sent[-1].receivers)
                self.msg(
                    "You last whispered {c%s{n:%s" % (recv, pages_we_sent[-1].message)
                )
                return
            else:
                self.msg("You haven't whispered anyone yet.")
                return

        if not self.args or "list" in self.switches:
            pages = list(pages_we_sent) + list(pages_we_got)
            pages.sort(key=lambda x: x.date_created)

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: whisper [<player> = msg]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "{w%s{n {c%s{n whispered to {c%s{n: %s"
            lastpages = "\n ".join(
                template
                % (
                    utils.datetime_format(page.date_created),
                    ",".join(obj.name for obj in page.senders),
                    "{n,{c ".join([obj.name for obj in page.receivers]),
                    page.message,
                )
                for page in lastpages
            )

            if lastpages:
                string = "Your latest whispers:\n %s" % lastpages
            else:
                string = "You haven't whispered anyone yet."
            self.msg(string)
            return
        # We are sending. Build a list of targets
        lhs = self.lhs
        rhs = self.rhs
        lhslist = self.lhslist
        if not self.rhs:
            # MMO-type whisper. 'whisper <name> <target>'
            arglist = self.args.lstrip().split(" ", 1)
            if len(arglist) < 2:
                caller.msg(
                    "The MMO-style whisper format requires both a name and a message."
                )
                caller.msg(
                    "To send a message to your last whispered character, use {wwhisper =<message>"
                )
                return
            lhs = arglist[0]
            rhs = arglist[1]
            lhslist = set(arglist[0].split(","))

        if not lhs and rhs:
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to whisper?")
                return
        else:
            receivers = lhslist

        recobjs = []
        for receiver in set(receivers):

            if isinstance(receiver, string_types):
                pobj = caller.search(receiver, use_nicks=True)
            elif hasattr(receiver, "character"):
                pobj = receiver.character
            elif hasattr(receiver, "player"):
                pobj = receiver
            else:
                self.msg("Who do you want to whisper?")
                return
            if pobj:
                if hasattr(pobj, "has_account") and not pobj.has_account:
                    self.msg("You may only send whispers to online characters.")
                elif not pobj.location or pobj.location != caller.location:
                    self.msg("You may only whisper characters in the same room as you.")
                else:
                    recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to whisper.")
            return
        header = "{c%s{n whispers," % caller.name
        message = rhs
        mutter_text = ""
        # if message begins with a :, we assume it is a 'whisper-pose'
        if message.startswith(":"):
            message = "%s {c%s{n %s" % (
                "Discreetly,",
                caller.name,
                message.strip(":").strip(),
            )
            is_a_whisper_pose = True
        elif message.startswith(";"):
            message = "%s {c%s{n%s" % (
                "Discreetly,",
                caller.name,
                message.lstrip(";").strip(),
            )
            is_a_whisper_pose = True
        else:
            is_a_whisper_pose = False
            message = '"' + message + '"'

        # create the temporary message object
        temp_message = TempMsg(senders=caller, receivers=recobjs, message=message)

        caller.ndb.whispers_sent.append(temp_message)

        # tell the players they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            otherobs = [ob for ob in recobjs if ob != pobj]
            if not pobj.access(caller, "tell"):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            if is_a_whisper_pose:
                omessage = message
                if otherobs:
                    omessage = "(Also sent to %s.) %s" % (
                        ", ".join(ob.name for ob in otherobs),
                        message,
                    )
                pobj.msg(omessage, from_obj=caller, options={"is_pose": True})
            else:
                if otherobs:
                    myheader = header + " to {cyou{n and %s," % ", ".join(
                        "{c%s{n" % ob.name for ob in otherobs
                    )
                else:
                    myheader = header
                pobj.msg(
                    "%s %s" % (myheader, message),
                    from_obj=caller,
                    options={"is_pose": True},
                )
            if not pobj.ndb.whispers_received:
                pobj.ndb.whispers_received = []
            pobj.ndb.whispers_received.append(temp_message)
            if hasattr(pobj, "has_account") and not pobj.has_account:
                received.append("{C%s{n" % pobj.name)
                rstrings.append(
                    "%s is offline. They will see your message if they list their pages later."
                    % received[-1]
                )
            else:
                received.append("{c%s{n" % pobj.name)
                # afk = pobj.player_ob and pobj.player_ob.db.afk
                # if afk:
                #     pobj.msg("{wYou inform {c%s{w that you are AFK:{n %s" % (caller, afk))
                #     rstrings.append("{c%s{n is AFK: %s" % (pobj.name, afk))
        if rstrings:
            self.msg("\n".join(rstrings))
        if received:
            if is_a_whisper_pose:
                self.msg("You posed to %s: %s" % (", ".join(received), message))
            else:
                self.msg("You whispered to %s, %s" % (", ".join(received), message))
                if "mutter" in self.switches or "mutter" in self.cmdstring:
                    from random import randint

                    word_list = rhs.split()
                    chosen = []
                    num_real = 0
                    for word in word_list:
                        if randint(0, 2):
                            chosen.append(word)
                            num_real += 1
                        else:
                            chosen.append("...")
                    if num_real:
                        mutter_text = " ".join(chosen)
                if mutter_text:
                    emit_string = ' mutters, "%s{n"' % mutter_text
                    exclude = [caller] + recobjs
                    caller.location.msg_action(
                        self.caller,
                        emit_string,
                        options={"is_pose": True},
                        exclude=exclude,
                    )
                    self.mark_command_used()
        caller.posecount += 1



class CmdTelepathic(MuxCommand):
    """
    Telepathy - send private IC message

    Usage:
      telepath [<player>,<player>,... = <message>]
      telepath =<message> - sends whisper to last person you whispered
      telepath <name> <message>
      whisper/mutter

    Send an IC message to a character in your room. A whisper of the format
    "whisper player=Hello" will send a message in the form of "You whisper
    <player>". A whisper of the format "whisper player=:does an emote" will appear
    in the form of "Discreetly, soandso does an emote" to <player>. It's generally
    expected that for whispers during public roleplay scenes that the players
    involved should pose to the room with some small mention that they're
    communicating discreetly. For ooc messages, please use the 'page'/'tell'
    command instead. If the /mutter switch is used, some of your whisper will
    be overheard by the room. Mutter cannot be used for whisper-poses.

    Right now, If no argument is given, you will get a list of your whispers from this
    session, but I'm going to kill that functionality here is a comment indicating that's true.
    """

    key = "telepath"
    aliases = ["+telepath"]
    locks = "cmd:not pperm(page_banned)"
    help_category = "Social"

    def func(self):
        """Implement function using the Msg methods"""

        # this is a MuxCommand, which means caller will be a Character.
        caller = self.caller
        # get the messages we've sent (not to channels)
        if not caller.ndb.whispers_sent:
            caller.ndb.whispers_sent = []
        pages_we_sent = caller.ndb.whispers_sent
        # get last messages we've got
        if not caller.ndb.whispers_received:
            caller.ndb.whispers_received = []
        pages_we_got = caller.ndb.whispers_received

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(str(obj) for obj in pages_we_sent[-1].receivers)
                self.msg(
                    "You last whispered {c%s{n:%s" % (recv, pages_we_sent[-1].message)
                )
                return
            else:
                self.msg("You haven't whispered anyone yet.")
                return

        if not self.args or "list" in self.switches:
            pages = list(pages_we_sent) + list(pages_we_got)
            pages.sort(key=lambda x: x.date_created)

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: whisper [<player> = msg]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "{w%s{n {c%s{n whispered to {c%s{n: %s"
            lastpages = "\n ".join(
                template
                % (
                    utils.datetime_format(page.date_created),
                    ",".join(obj.name for obj in page.senders),
                    "{n,{c ".join([obj.name for obj in page.receivers]),
                    page.message,
                )
                for page in lastpages
            )

            if lastpages:
                string = "Your latest whispers:\n %s" % lastpages
            else:
                string = "You haven't whispered anyone yet."
            self.msg(string)
            return
        # We are sending. Build a list of targets
        lhs = self.lhs
        rhs = self.rhs
        lhslist = self.lhslist
        if not self.rhs:
            # MMO-type whisper. 'whisper <name> <target>'
            arglist = self.args.lstrip().split(" ", 1)
            if len(arglist) < 2:
                caller.msg(
                    "The MMO-style whisper format requires both a name and a message."
                )
                caller.msg(
                    "To send a message to your last whispered character, use {wwhisper =<message>"
                )
                return
            lhs = arglist[0]
            rhs = arglist[1]
            lhslist = set(arglist[0].split(","))

        if not lhs and rhs:
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to whisper?")
                return
        else:
            receivers = lhslist

        recobjs = []
        for receiver in set(receivers):

            if isinstance(receiver, string_types):
                pobj = caller.search(receiver, use_nicks=True)
            elif hasattr(receiver, "character"):
                pobj = receiver.character
            elif hasattr(receiver, "player"):
                pobj = receiver
            else:
                self.msg("Who do you want to whisper?")
                return
            if pobj:
                if hasattr(pobj, "has_account") and not pobj.has_account:
                    self.msg("You may only send whispers to online characters.")
                elif not pobj.location or pobj.location != caller.location:
                    self.msg("You may only whisper characters in the same room as you.")
                else:
                    recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to whisper.")
            return
        header = "{c%s{n whispers," % caller.name
        message = rhs
        mutter_text = ""
        # if message begins with a :, we assume it is a 'whisper-pose'
        if message.startswith(":"):
            message = "%s {c%s{n %s" % (
                "Discreetly,",
                caller.name,
                message.strip(":").strip(),
            )
            is_a_whisper_pose = True
        elif message.startswith(";"):
            message = "%s {c%s{n%s" % (
                "Discreetly,",
                caller.name,
                message.lstrip(";").strip(),
            )
            is_a_whisper_pose = True
        else:
            is_a_whisper_pose = False
            message = '"' + message + '"'

        # create the temporary message object
        temp_message = TempMsg(senders=caller, receivers=recobjs, message=message)

        caller.ndb.whispers_sent.append(temp_message)

        # tell the players they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            otherobs = [ob for ob in recobjs if ob != pobj]
            if not pobj.access(caller, "tell"):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            if is_a_whisper_pose:
                omessage = message
                if otherobs:
                    omessage = "(Also sent to %s.) %s" % (
                        ", ".join(ob.name for ob in otherobs),
                        message,
                    )
                pobj.msg(omessage, from_obj=caller, options={"is_pose": True})
            else:
                if otherobs:
                    myheader = header + " to {cyou{n and %s," % ", ".join(
                        "{c%s{n" % ob.name for ob in otherobs
                    )
                else:
                    myheader = header
                pobj.msg(
                    "%s %s" % (myheader, message),
                    from_obj=caller,
                    options={"is_pose": True},
                )
            if not pobj.ndb.whispers_received:
                pobj.ndb.whispers_received = []
            pobj.ndb.whispers_received.append(temp_message)
            if hasattr(pobj, "has_account") and not pobj.has_account:
                received.append("{C%s{n" % pobj.name)
                rstrings.append(
                    "%s is offline. They will see your message if they list their pages later."
                    % received[-1]
                )
            else:
                received.append("{c%s{n" % pobj.name)
                # afk = pobj.player_ob and pobj.player_ob.db.afk
                # if afk:
                #     pobj.msg("{wYou inform {c%s{w that you are AFK:{n %s" % (caller, afk))
                #     rstrings.append("{c%s{n is AFK: %s" % (pobj.name, afk))
        if rstrings:
            self.msg("\n".join(rstrings))
        if received:
            if is_a_whisper_pose:
                self.msg("You posed to %s: %s" % (", ".join(received), message))
            else:
                self.msg("You whispered to %s, %s" % (", ".join(received), message))
                if "mutter" in self.switches or "mutter" in self.cmdstring:
                    from random import randint

                    word_list = rhs.split()
                    chosen = []
                    num_real = 0
                    for word in word_list:
                        if randint(0, 2):
                            chosen.append(word)
                            num_real += 1
                        else:
                            chosen.append("...")
                    if num_real:
                        mutter_text = " ".join(chosen)
                if mutter_text:
                    emit_string = ' mutters, "%s{n"' % mutter_text
                    exclude = [caller] + recobjs
                    caller.location.msg_action(
                        self.caller,
                        emit_string,
                        options={"is_pose": True},
                        exclude=exclude,
                    )
                    self.mark_command_used()
        caller.posecount += 1

class CmdSaraband(MuxCommand):
    """
    Saraband - send private IC message

    Usage:
      saraband[/switches] [<player>,<player>,... = <message>]
      saraband =<message> - sends whisper to last person you whispered
      saraband <name> <message>

    Send an IC message to a character in your room. A whisper of the format
    "whisper player=Hello" will send a message in the form of "You whisper
    <player>". A whisper of the format "whisper player=:does an emote" will appear
    in the form of "Discreetly, soandso does an emote" to <player>. It's generally
    expected that for whispers during public roleplay scenes that the players
    involved should pose to the room with some small mention that they're
    communicating discreetly. For ooc messages, please use the 'page'/'tell'
    command instead. If the /mutter switch is used, some of your whisper will
    be overheard by the room. Mutter cannot be used for whisper-poses.

    Right now, If no argument is given, you will get a list of your whispers from this
    session, but I'm going to kill that functionality here is a comment indicating that's true.
    """

    key = "saraband"
    aliases = ["+saraband"]
    locks = "cmd:not pperm(page_banned)"
    help_category = "Social"
    simplified_key = "mutter"

    def func(self):
        """Implement function using the Msg methods"""

        # this is a MuxCommand, which means caller will be a Character.
        caller = self.caller
        # get the messages we've sent (not to channels)
        if not caller.ndb.whispers_sent:
            caller.ndb.whispers_sent = []
        pages_we_sent = caller.ndb.whispers_sent
        # get last messages we've got
        if not caller.ndb.whispers_received:
            caller.ndb.whispers_received = []
        pages_we_got = caller.ndb.whispers_received

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(str(obj) for obj in pages_we_sent[-1].receivers)
                self.msg(
                    "You last whispered {c%s{n:%s" % (recv, pages_we_sent[-1].message)
                )
                return
            else:
                self.msg("You haven't whispered anyone yet.")
                return

        if not self.args or "list" in self.switches:
            pages = list(pages_we_sent) + list(pages_we_got)
            pages.sort(key=lambda x: x.date_created)

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: whisper [<player> = msg]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "{w%s{n {c%s{n whispered to {c%s{n: %s"
            lastpages = "\n ".join(
                template
                % (
                    utils.datetime_format(page.date_created),
                    ",".join(obj.name for obj in page.senders),
                    "{n,{c ".join([obj.name for obj in page.receivers]),
                    page.message,
                )
                for page in lastpages
            )

            if lastpages:
                string = "Your latest whispers:\n %s" % lastpages
            else:
                string = "You haven't whispered anyone yet."
            self.msg(string)
            return
        # We are sending. Build a list of targets
        lhs = self.lhs
        rhs = self.rhs
        lhslist = self.lhslist
        if not self.rhs:
            # MMO-type whisper. 'whisper <name> <target>'
            arglist = self.args.lstrip().split(" ", 1)
            if len(arglist) < 2:
                caller.msg(
                    "The MMO-style whisper format requires both a name and a message."
                )
                caller.msg(
                    "To send a message to your last whispered character, use {wwhisper =<message>"
                )
                return
            lhs = arglist[0]
            rhs = arglist[1]
            lhslist = set(arglist[0].split(","))

        if not lhs and rhs:
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to whisper?")
                return
        else:
            receivers = lhslist

        recobjs = []
        for receiver in set(receivers):

            if isinstance(receiver, string_types):
                pobj = caller.search(receiver, use_nicks=True)
            elif hasattr(receiver, "character"):
                pobj = receiver.character
            elif hasattr(receiver, "player"):
                pobj = receiver
            else:
                self.msg("Who do you want to whisper?")
                return
            if pobj:
                if hasattr(pobj, "has_account") and not pobj.has_account:
                    self.msg("You may only send whispers to online characters.")
                elif not pobj.location or pobj.location != caller.location:
                    self.msg("You may only whisper characters in the same room as you.")
                else:
                    recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to whisper.")
            return
        header = "{c%s{n whispers," % caller.name
        message = rhs
        mutter_text = ""
        # if message begins with a :, we assume it is a 'whisper-pose'
        if message.startswith(":"):
            message = "%s {c%s{n %s" % (
                "Discreetly,",
                caller.name,
                message.strip(":").strip(),
            )
            is_a_whisper_pose = True
        elif message.startswith(";"):
            message = "%s {c%s{n%s" % (
                "Discreetly,",
                caller.name,
                message.lstrip(";").strip(),
            )
            is_a_whisper_pose = True
        else:
            is_a_whisper_pose = False
            message = '"' + message + '"'

        # create the temporary message object
        temp_message = TempMsg(senders=caller, receivers=recobjs, message=message)

        caller.ndb.whispers_sent.append(temp_message)

        # tell the players they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            otherobs = [ob for ob in recobjs if ob != pobj]
            if not pobj.access(caller, "tell"):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            if is_a_whisper_pose:
                omessage = message
                if otherobs:
                    omessage = "(Also sent to %s.) %s" % (
                        ", ".join(ob.name for ob in otherobs),
                        message,
                    )
                pobj.msg(omessage, from_obj=caller, options={"is_pose": True})
            else:
                if otherobs:
                    myheader = header + " to {cyou{n and %s," % ", ".join(
                        "{c%s{n" % ob.name for ob in otherobs
                    )
                else:
                    myheader = header
                pobj.msg(
                    "%s %s" % (myheader, message),
                    from_obj=caller,
                    options={"is_pose": True},
                )
            if not pobj.ndb.whispers_received:
                pobj.ndb.whispers_received = []
            pobj.ndb.whispers_received.append(temp_message)
            if hasattr(pobj, "has_account") and not pobj.has_account:
                received.append("{C%s{n" % pobj.name)
                rstrings.append(
                    "%s is offline. They will see your message if they list their pages later."
                    % received[-1]
                )
            else:
                received.append("{c%s{n" % pobj.name)
                # afk = pobj.player_ob and pobj.player_ob.db.afk
                # if afk:
                #     pobj.msg("{wYou inform {c%s{w that you are AFK:{n %s" % (caller, afk))
                #     rstrings.append("{c%s{n is AFK: %s" % (pobj.name, afk))
        if rstrings:
            self.msg("\n".join(rstrings))
        if received:
            if is_a_whisper_pose:
                self.msg("You posed to %s: %s" % (", ".join(received), message))
            else:
                self.msg("You whispered to %s, %s" % (", ".join(received), message))
                if "mutter" in self.switches or "mutter" in self.cmdstring:
                    from random import randint

                    word_list = rhs.split()
                    chosen = []
                    num_real = 0
                    for word in word_list:
                        if randint(0, 2):
                            chosen.append(word)
                            num_real += 1
                        else:
                            chosen.append("...")
                    if num_real:
                        mutter_text = " ".join(chosen)
                if mutter_text:
                    emit_string = ' mutters, "%s{n"' % mutter_text
                    exclude = [caller] + recobjs
                    caller.location.msg_action(
                        self.caller,
                        emit_string,
                        options={"is_pose": True},
                        exclude=exclude,
                    )
                    self.mark_command_used()
        caller.posecount += 1


class CmdTightbeam(MuxCommand):
    """
    Tightbeam - send private IC message

    Usage:
      2way[/switches] [<player>,<player>,... = <message>]
      whisper =<message> - sends whisper to last person you whispered
      2way <name> <message>
      tightbeam/switches 


    Send an IC message to a character in your room. A whisper of the format
    "whisper player=Hello" will send a message in the form of "You whisper
    <player>". A whisper of the format "whisper player=:does an emote" will appear
    in the form of "Discreetly, soandso does an emote" to <player>. It's generally
    expected that for whispers during public roleplay scenes that the players
    involved should pose to the room with some small mention that they're
    communicating discreetly. For ooc messages, please use the 'page'/'tell'
    command instead. If the /mutter switch is used, some of your whisper will
    be overheard by the room. Mutter cannot be used for whisper-poses.

    +2way and +tightbeam do the same thing. For radio messages to talk within a group
    or on open bands, see the help for the +radio commands.

    Right now, If no argument is given, you will get a list of your whispers from this
    session, but I'm going to kill that functionality here is a comment indicating that's true.
    """

    key = "tightbeam"
    aliases = ["+2way, +tightbeam", "2way"]
    locks = "cmd:not pperm(page_banned)"
    help_category = "Social"
    simplified_key = "mutter"

    def func(self):
        """Implement function using the Msg methods"""

        # this is a MuxCommand, which means caller will be a Character.
        caller = self.caller
        # get the messages we've sent (not to channels)
        if not caller.ndb.whispers_sent:
            caller.ndb.whispers_sent = []
        pages_we_sent = caller.ndb.whispers_sent
        # get last messages we've got
        if not caller.ndb.whispers_received:
            caller.ndb.whispers_received = []
        pages_we_got = caller.ndb.whispers_received

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(str(obj) for obj in pages_we_sent[-1].receivers)
                self.msg(
                    "You last whispered {c%s{n:%s" % (recv, pages_we_sent[-1].message)
                )
                return
            else:
                self.msg("You haven't whispered anyone yet.")
                return

        if not self.args or "list" in self.switches:
            pages = list(pages_we_sent) + list(pages_we_got)
            pages.sort(key=lambda x: x.date_created)

            number = 5
            if self.args:
                try:
                    number = int(self.args)
                except ValueError:
                    self.msg("Usage: whisper [<player> = msg]")
                    return

            if len(pages) > number:
                lastpages = pages[-number:]
            else:
                lastpages = pages
            template = "{w%s{n {c%s{n whispered to {c%s{n: %s"
            lastpages = "\n ".join(
                template
                % (
                    utils.datetime_format(page.date_created),
                    ",".join(obj.name for obj in page.senders),
                    "{n,{c ".join([obj.name for obj in page.receivers]),
                    page.message,
                )
                for page in lastpages
            )

            if lastpages:
                string = "Your latest whispers:\n %s" % lastpages
            else:
                string = "You haven't whispered anyone yet."
            self.msg(string)
            return
        # We are sending. Build a list of targets
        lhs = self.lhs
        rhs = self.rhs
        lhslist = self.lhslist
        if not self.rhs:
            # MMO-type whisper. 'whisper <name> <target>'
            arglist = self.args.lstrip().split(" ", 1)
            if len(arglist) < 2:
                caller.msg(
                    "The MMO-style whisper format requires both a name and a message."
                )
                caller.msg(
                    "To send a message to your last whispered character, use {wwhisper =<message>"
                )
                return
            lhs = arglist[0]
            rhs = arglist[1]
            lhslist = set(arglist[0].split(","))

        if not lhs and rhs:
            # If there are no targets, then set the targets
            # to the last person we paged.
            if pages_we_sent:
                receivers = pages_we_sent[-1].receivers
            else:
                self.msg("Who do you want to whisper?")
                return
        else:
            receivers = lhslist

        recobjs = []
        for receiver in set(receivers):

            if isinstance(receiver, string_types):
                pobj = caller.search(receiver, use_nicks=True)
            elif hasattr(receiver, "character"):
                pobj = receiver.character
            elif hasattr(receiver, "player"):
                pobj = receiver
            else:
                self.msg("Who do you want to whisper?")
                return
            if pobj:
                if hasattr(pobj, "has_account") and not pobj.has_account:
                    self.msg("You may only send whispers to online characters.")
                elif not pobj.location or pobj.location != caller.location:
                    self.msg("You may only whisper characters in the same room as you.")
                else:
                    recobjs.append(pobj)
        if not recobjs:
            self.msg("No one found to whisper.")
            return
        header = "{c%s{n whispers," % caller.name
        message = rhs
        mutter_text = ""
        # if message begins with a :, we assume it is a 'whisper-pose'
        if message.startswith(":"):
            message = "%s {c%s{n %s" % (
                "Discreetly,",
                caller.name,
                message.strip(":").strip(),
            )
            is_a_whisper_pose = True
        elif message.startswith(";"):
            message = "%s {c%s{n%s" % (
                "Discreetly,",
                caller.name,
                message.lstrip(";").strip(),
            )
            is_a_whisper_pose = True
        else:
            is_a_whisper_pose = False
            message = '"' + message + '"'

        # create the temporary message object
        temp_message = TempMsg(senders=caller, receivers=recobjs, message=message)

        caller.ndb.whispers_sent.append(temp_message)

        # tell the players they got a message.
        received = []
        rstrings = []
        for pobj in recobjs:
            otherobs = [ob for ob in recobjs if ob != pobj]
            if not pobj.access(caller, "tell"):
                rstrings.append("You are not allowed to page %s." % pobj)
                continue
            if is_a_whisper_pose:
                omessage = message
                if otherobs:
                    omessage = "(Also sent to %s.) %s" % (
                        ", ".join(ob.name for ob in otherobs),
                        message,
                    )
                pobj.msg(omessage, from_obj=caller, options={"is_pose": True})
            else:
                if otherobs:
                    myheader = header + " to {cyou{n and %s," % ", ".join(
                        "{c%s{n" % ob.name for ob in otherobs
                    )
                else:
                    myheader = header
                pobj.msg(
                    "%s %s" % (myheader, message),
                    from_obj=caller,
                    options={"is_pose": True},
                )
            if not pobj.ndb.whispers_received:
                pobj.ndb.whispers_received = []
            pobj.ndb.whispers_received.append(temp_message)
            if hasattr(pobj, "has_account") and not pobj.has_account:
                received.append("{C%s{n" % pobj.name)
                rstrings.append(
                    "%s is offline. They will see your message if they list their pages later."
                    % received[-1]
                )
            else:
                received.append("{c%s{n" % pobj.name)
                # afk = pobj.player_ob and pobj.player_ob.db.afk
                # if afk:
                #     pobj.msg("{wYou inform {c%s{w that you are AFK:{n %s" % (caller, afk))
                #     rstrings.append("{c%s{n is AFK: %s" % (pobj.name, afk))
        if rstrings:
            self.msg("\n".join(rstrings))
        if received:
            if is_a_whisper_pose:
                self.msg("You posed to %s: %s" % (", ".join(received), message))
            else:
                self.msg("You whispered to %s, %s" % (", ".join(received), message))
                if "mutter" in self.switches or "mutter" in self.cmdstring:
                    from random import randint

                    word_list = rhs.split()
                    chosen = []
                    num_real = 0
                    for word in word_list:
                        if randint(0, 2):
                            chosen.append(word)
                            num_real += 1
                        else:
                            chosen.append("...")
                    if num_real:
                        mutter_text = " ".join(chosen)
                if mutter_text:
                    emit_string = ' mutters, "%s{n"' % mutter_text
                    exclude = [caller] + recobjs
                    caller.location.msg_action(
                        self.caller,
                        emit_string,
                        options={"is_pose": True},
                        exclude=exclude,
                    )
                    self.mark_command_used()
        caller.posecount += 1
