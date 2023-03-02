"""
Job/Request module.

Jobs and apps will be in the database using a Request and Application model.

Player applications will still be by email until PC self-creation is working.
"""
from django.conf import settings

from evennia.utils.create import create_object
from typeclasses import prettytable

from evennia import default_cmds
from evennia import CmdSet
from commands import command
from evennia.commands.default.muxcommand import MuxCommand
from six import string_types
from server.utils import sub_old_ansi
from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from evennia.comms.models import Msg
from evennia.commands.default.muxcommand import MuxCommand
from world.requests.models import Request,RequestResponse,File,Topic


class CmdRequest(MuxCommand):
    """
    +request - Make a request for GM help

    Usage:
       +request
       +request <#>

       +request <title>=<description>
       +request/bug <title>=<description>
       +request/char <title>=<description>
       +request/news <title>=<description>
    
       

    This command requests <title> and <description> from staff. The request is    
    added to the jobs list and will be tended to as soon as possible. There is a  
    standard three to four day turnaround time on +requests.                      

    +request is a method of getting information about any subject, IC or OOC, from
    the administration. It is used to get details about the world, request        
    background plot information, investigate ongoing TPs, and to contact the admin
    for various OOC purposes.

    Typing just +request with no arguments gives you back your list of active
    +requests. +request <#> to view the text of that request.
    
    """

    key = "request"
    aliases = ["requests", "+request","+requests","myjobs","+myjobs"]
    help_category = "Requests"
    locks = "perm(Player))"

    def list_tickets(self):
        """List tickets for the caller"""
        caller = self.caller
        my_requests = Request.objects.filter(db_submitter=caller)
        msg = "\n|wMy Requests:|n\n\n"
        for request in my_requests:
            msg += "ID: %s  " % str(request.id)
            if request.db_is_open:
                msg += "Status: |gOpen|n \n"
            else:
                msg += "Status: |rClosed|n \n"
            msg += "Subject: %s\n\n" % request.db_title
        msg += "Use |w+request <#>|n to view an individual ticket. "
        self.msg(msg)

    def get_ticket_from_args(self, args):
        """Retrieve ticket or display valid choices if not found"""
        caller = self.caller
        try:
            my_requests = Request.objects.filter(db_submitter=caller)
            ticket = my_requests.get(id=args)
            return ticket
        except (Request.DoesNotExist, ValueError):
            self.msg("No request found by that number.")
            self.list_tickets()

    def display_ticket(self, ticket):
        msg = "\n|wRequest " + str(ticket.id) + "|n \n"
        if ticket.db_is_open:
            msg += "Status: |gOpen|n"
        else:
            msg += "Status: |rClosed|n"
        msg += "\nSubject: " + ticket.db_title + "\n\n" + ticket.db_message_body + "\n"

        self.caller.msg(msg)
        return


    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args
        switches = self.switches

        if not args:
            self.list_tickets()
            return

        if self.lhs.isdigit():
            ticket = self.get_ticket_from_args(self.lhs)
            if not ticket:
                caller.msg("No such request was found.")
                return

            self.display_ticket(ticket)
            return
        category = 1

        if switches:
            if "bug" in switches:
                category = 2
            if "char" in switches:
                category = 3
            if "news" in switches:
                category = 4
        
        title = self.lhs
        message = sub_old_ansi(self.rhs)
        if not message:
            caller.msg("Syntax error - no message. +request <title>=<message>.")
            return

        new_ticket = Request.objects.create(db_title=title, db_submitter=caller,db_message_body=message,type=category)
        if new_ticket:
            caller.msg(
                f"Thank you for submitting a request to the GM staff. Your ticket (#{new_ticket.id}) "
                "has been added to the queue."
            )
        else:
            caller.msg(
                "Request submission has failed for unknown reason. Please inform the administrators."
            )


class CmdCheckJobs(MuxCommand):
    """
    Command for admin to check request queue.

    Usage:
       +jobs
       +job <#>

       +job/assign <#>=<person>
       +job/category <#>=<category>
       +job/file <#>=<file>
       +job/respond <#>=<description>
       +job/add <#>=<description>
       +job/close <#>
          
    This command is for staff to answer requests.

    It's just outlined.
    +job/assign to flag a job for a certain staffer to answer.
    +job/category to put a job in a particular category.
    +job/file attaches a file to a job.
    +job/respond creates a one-off response and sends it out.
    Be careful not to create one-off off responses that should be files.

    +job/add will allow you to tag in other people to a job.
    +job/close to archive a job, removing it from active job list.

    """

    key = "job"
    aliases = ["jobs","job", "+job"]
    help_category = "Requests"
    locks = "perm(Builder))"

    def display_ticket(self, ticket):
        """Display the ticket to the caller"""
        self.msg(ticket.display())
    
    def close_ticket(self, number, reason):
        caller = self.caller

        ticket = self.get_ticket_from_args(number)
        if not ticket:
            return

        if ticket:
            caller.msg(f"You have successfully closed ticket #{ticket.id}.")
        else:
            caller.msg(f"Failed to close ticket #{ticket.id}.")

        return


class CmdCheckFiles(MuxCommand):
    """
    Command to read files sent to you about story.

    Usage:
       +files
       +file <#>

       +file/send <#>=<person>
       +file/share <#>=<group>

          
    This command is to share files among players.

    It's just outlined.
    +file/send to send along a file to another player.
    +file/share to share a file to an entire group.

    Files contain lore which is ICly known. It is usually the subject of a research
    +request.

    """

    key = "file"
    aliases = ["files", "+file","files"]
    help_category = "Requests"
    locks = "perm(Player))"

    def display_ticket(self, ticket):
        """Display the ticket to the caller"""
        self.msg(ticket.display())