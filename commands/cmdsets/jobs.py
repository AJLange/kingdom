"""
Job/Request and character application command module.
Jobs and Apps will be two more manager objects that will
be cloned and set to some staff location or carried around
on the superuser. While a little clunky that they are in-
game objects, it allows for easy @ex, and doesn't require
database migration to add in their functionality.
"""
from django.conf import settings

from evennia.utils.create import create_object
from server.utils import prettytable, helpdesk_api
from web.helpdesk.models import Ticket, Queue

from evennia import default_cmds
from evennia import CmdSet
from commands import command
from commands.base import BaseCommand
from six import string_types
from server.utils import sub_old_ansi
from evennia.server.sessionhandler import SESSIONS
import time
import re
from evennia import ObjectDB, AccountDB
from evennia.utils import utils, create, evtable, make_iter, inherits_from, datetime_format
from evennia.comms.models import Msg
from evennia.commands.default.muxcommand import MuxCommand


def get_apps_manager():
    """
    returns apps manager object
    """
    try:
        return AppsManager.objects.get()
    except AppsManager.DoesNotExist:
        return create_object(AppsManager, key="Apps Manager", home=None, location=None)
    except AppsManager.MultipleObjectsReturned:
        return AppsManager.objects.first()


class CmdRequest(BaseCommand):
    """
    +request - Make a request for GM help
    Usage:
       +request [<#>]
       +request <title>=<message>
          
    Arx's ticketing system with extra command methods removed.
    Will update to match M3's ticket system, but this may
    need refactored due to different usage. 

    The alias for this on M3 is +jobs/+myjobs.
    """

    key = "request"
    aliases = ["requests"]
    help_category = "Admin"
    locks = "cmd:all()"

    def display_ticket(self, ticket):
        """Display the ticket to the caller"""
        self.msg(ticket.display())

    @property
    def tickets(self):
        """Property for displaying tickets. Omit defunct Story queue"""
        return self.caller.tickets.exclude(queue__slug="Story")

    def list_tickets(self):
        """List tickets for the caller"""
        closed = self.tickets.filter(
            status__in=[Ticket.CLOSED_STATUS, Ticket.RESOLVED_STATUS]
        )
        tickets = self.tickets.filter(status=Ticket.OPEN_STATUS)
        msg = "{wClosed tickets:{n %s" % ", ".join(str(ticket.id) for ticket in closed)
        msg += "\n{wOpen tickets:{n %s" % ", ".join(
            str(ticket.id) for ticket in tickets
        )
        msg += "\nUse {w+request <#>{n to view an individual ticket. "
        msg += "Use {w+request/followup <#>=<comment>{n to add a comment."
        self.msg(msg)

    def get_ticket_from_args(self, args):
        """Retrieve ticket or display valid choices if not found"""
        try:
            ticket = self.caller.tickets.get(id=args)
            return ticket
        except (Ticket.DoesNotExist, ValueError):
            self.msg("No ticket found by that number.")
            self.list_tickets()

    def create_ticket(self, title, message):
        caller = self.caller
        priority = 3
        slug = settings.REQUEST_QUEUE_SLUG

        optional_title = title if message else (title[:27] + "...")
        args = message if message else self.args
        email = caller.email if caller.email != "dummy@dummy.com" else None

       

        return helpdesk_api.create_ticket(
            caller,
            args,
            priority,
            queue_slug=slug,
            send_email=email,
            optional_title=optional_title,
        )

    def close_ticket(self, number, reason):
        caller = self.caller

        if not reason:
            caller.msg("Usage: <#>=<Reason>")
            return

        ticket = self.get_ticket_from_args(number)
        if not ticket:
            return

        if helpdesk_api.resolve_ticket(caller, ticket, reason, by_submitter=True):
            caller.msg(f"You have successfully closed ticket #{ticket.id}.")
        else:
            caller.msg(f"Failed to close ticket #{ticket.id}.")

        return

    def comment_on_ticket(self):
        caller = self.caller

        if not self.lhs or not self.rhs:
            msg = "Usage: <#>=<message>"
            ticketnumbers = ", ".join(str(ticket.id) for ticket in self.tickets)
            if ticketnumbers:
                msg += f"\nYour tickets: {ticketnumbers}"
            return caller.msg(msg)

        ticket = self.get_ticket_from_args(self.lhs)
        if not ticket:
            return

        if ticket.status == ticket.CLOSED_STATUS:
            self.msg("That ticket is already closed. Please make a new one.")
            return

        helpdesk_api.add_followup(caller, ticket, self.rhs, mail_player=False)
        caller.msg("Followup added.")

        return

    def func(self):
        """Implement the command"""
        caller = self.caller
        if "followup" in self.switches or "comment" in self.switches:
            self.comment_on_ticket()
            return

        if "close" in self.switches:
            self.close_ticket(self.lhs, self.rhs)
            return

        if not self.lhs:
            self.list_tickets()
            return

        if self.lhs.isdigit():
            ticket = self.get_ticket_from_args(self.lhs)
            if not ticket:
                return

            self.display_ticket(ticket)
            return

        new_ticket = self.create_ticket(self.lhs, self.rhs)
        if new_ticket:
            caller.msg(
                f"Thank you for submitting a request to the GM staff. Your ticket (#{new_ticket.id}) "
                "has been added to the queue."
            )
        else:
            caller.msg(
                "Ticket submission has failed for unknown reason. Please inform the administrators."
            )


