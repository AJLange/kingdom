# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

 If you need to create an account, type (without the <>'s):
      |wcreate <username> <password>|n

"""

from django.conf import settings
from evennia import utils

'''to do - scrambled connections screens with random '''

CONNECTION_SCREEN = """|=z|[=aYou|_have|_arrived|_at...|444|[=a {}|/|_ |_ |_ |_ |_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|_|055|_/\ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |=z|_megamanmush.com|_1997|/ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |055/ |_\ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |=z|_www.megamanmush.com|/ |_ |_ |_ |_ |_ |_ |_ |_ |_|055 /\ |_ |_ |_ |_ |055/ |_ |_\ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_  |/ |_ |_ |_ |_ |_ |_ |_ |_ |015_|055/|015__|055\|015 |____ |055|_/ |_ |_ |_\ |_ |_ |015|_ |_ |______ |____ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |/ |_ |_ |_ |_ |055|_ |_ ____|015\ |_ ||\/ |_|||_|055/ |_ |_ |_ |_\ |_ |_ |_ |_|015 \ |_ |||_/ |_|| |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |/ |_ |_ |_ |055|_ |_ |_\ |_ |015|_/ |_ ||/ |_ ||/|_____|_____\ |____ |_ / |_ ||/ |_ || |____ |_ __ |___ |_ |_ |_ |_ |/ |_ |_ |_ |_ |_ |055|_ \ |_|015/ |_ |_ |_ |_ |||_/|___//|____/|_/ |_ |||_/ |_ |_ |_ |_ |||_/ |_ |||_/|_|||_/|_/ |_ |_ |_ |_ |/ |_ |_ |_ |_ |_ |_ |055|_\|015/ |_/|| |_/|| |_||/|__/|_/|_/___|_/|_/|||_||/ |_/|| |_/|| |_||/|_/|||_||/ |_||/|_/ |_ |_ |_ |_  |/|015 |_ |_ |_ |_ |_ |_ |_/ |_/|_||_/|_|| |_|||_/_|_/|_||_\|_//|___ |_|| |_/|_||_/|_|| |_|||___ |_|||_/|| |_/ |_ |_ |_ |_ |_ |/ |_ |_ |_ |_ |_ |015|_ /__/|055\ |_ |_ |015||__||___\\____//__/ |_||_||_/ |_ |_ |_||__||/ |_||_||/|_||_/ |_ |_ |_ |_ |_  |/ |_ |_ |_ |_ |_ |_ |_ |_ |055|_\ |_ |_/|_|055\/ |_ \ |_ |_/ |_ |_ |_ |_|015 _____ |____ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |/ |_ |_ |_ |_ |_ |_ |_ |_ |_|055 \ |_/ |_ |_ |_ |_\ |_/ |_ |_ |_ |_ |015|_\ |_ |||_/ |_|| |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |/ |_ |_ |_ |_ |_ |_ |_ |_ |_ |055|_\/ |_ |_ |_ |_ |_\/ |_ |_ |_ |_ |015|_ / |_ ||/ |_ |||____ |__________ |____ |_ |_ |/ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |015|_/ |_ |_ |_ |_ |||_|||_/|_/|_/|____/|_/_/|_/ |_ |_  |/ '|=zconnect|_guest' |_ |_ |_ |_ |_ |_ |_ |_ |_|_|_|_|_|_|_ |_|015 / |_/|| |_/|| |_||/|_/|_/|_/__|_\/|___ |_/ |_ |_ |_ |/ |_|=s |_ -|_Connect|_as|_a|_Guest|_character. |_ |_ |015|_/ |_/|_||_/|_|| |_|||_/_/|_/__/|_/|_/|_/|_/ |_ |_ |_  |/ '|=zconnect|_<name>|_<password>' |_ |_ |_ |_ |_ |_|015 /__/ |_ |_ |_||__||____/____/_/|_/_/ |_ |_ |_ |_ |/ |=s|_ |_ -|_Connect|_an|_existing|_character. |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |_ |/ '|=zQUIT'|=s|_to|_Disconnect |_ |_ |_ |_ |_ |_ |_ |_ |_|=s |_ |_Version|_{}|_ Running|_on|_Evennia|/ '|=zWHO'|=s|_to|_display|_who's online|_ |_ |_ |_ |_ |_|=s |_Contact|_us|_at|_|=zapps@megamanmush.com|/""".format(
    settings.SERVERNAME, utils.get_evennia_version("short")
)
