"""
Comsystem command module.
Comm commands are OOC commands and intended to be made available to
the Player at all times (they go into the PlayerCmdSet). So we
make sure to homogenize self.caller to always be the player object
for easy handling.
"""
from evennia.utils import create
from evennia.utils.create import create_object
from typeclasses import prettytable
from evennia.utils.evtable import EvTable
from evennia import default_cmds
from server.utils import sub_old_ansi
from world.boards.models import BulletinBoard, BoardPost
from commands.command import Command
from evennia.commands.default.muxcommand import MuxCommand


def get_boards(caller):
    """
    returns list of bulletin boards
    """
    bb_list = list(BulletinBoard.objects.all())
    #bb_list = [ob for ob in bb_list if ob.access(caller, "read")]
    return bb_list


def list_bboards(caller, old=False):
    """
    Helper function for listing all boards a player is subscribed
    to in some pretty format.
    """
    bb_list = get_boards(caller)
    if not bb_list:
        return
    # set this on the account level, which involves change of model
    my_subs = []
    for bb in bb_list:
        if caller in bb.has_subscriber.all():
            my_subs.append(bb)

    # just display the subscribed bboards with no extra info
    if old:
        caller.msg("Displaying only archived posts.")
    bbtable = EvTable(
        "bb #", "Name", "Posts", "Subscribed"
        )
    for bboard in bb_list:
        bb_number = bb_list.index(bboard)
        bb_name = bboard.db_name
        # caller.msg("In list_bboards call: type is {0}".format(type(caller).__name__))
        #unread_num = bboard.num_of_unread_posts(caller.account, old)

        # placeholder:
        unread_num = 0
        subbed = bboard in my_subs
        #posts = bboard.archived_posts if old else bboard.posts
        #if unread_num:
            #unread_str = " (%s new)" % unread_num
        #else:
            #unread_str = ""
        #bbtable.add_row(bb_number, bb_name, "%s%s" % (len(posts), unread_str))
        bbtable.add_row(bb_number, bb_name, unread_num, subbed)
    caller.msg("\n" + "=" * 60 + "\n%s" % bbtable)


def access_bboard(caller, args, request="read"):
    """
    Helper function for searching for a single bboard with
    some error handling.
    """
    bboards = get_boards(caller)
    if not bboards:
        return
    if args.isdigit():
        bb_num = int(args)
        if (bb_num < 0) or (bb_num >= len(bboards)):
            caller.msg("Invalid board number.")
            return
        board = bboards[bb_num]

    else:
        board_ids = [ob.id for ob in bboards]
        try:
            board = BulletinBoard.objects.get(db_key__icontains=args, id__in=board_ids)
        except BulletinBoard.DoesNotExist:
            caller.msg("Could not find a unique board by name %s." % args)
            return
        except BulletinBoard.MultipleObjectsReturned:
            boards = BulletinBoard.objects.filter(db_key__icontains=args, id__in=board_ids)
            caller.msg(
                "Too many boards returned, please pick one: %s"
                % ", ".join(str(ob) for ob in boards)
            )
            return
    '''
    removing the check on accesses for now. Later on put back (so staff can have private board)

    if not board.access(caller, request):
        caller.msg("You do not have the required privileges to do that.")
        return
    '''
    # passed all checks, so return board
    return board

def get_all_posts(board):
    try:
        posts = BoardPost.objects.get(db_board = board).db_board
    except LookupError:
        return 
    return posts

def list_messages(caller, board, board_num):
    """
    Helper function for printing all the posts on board
    to caller.
    """
    if not board:
        caller.msg("No bulletin board found.")
        return
    caller.msg("" + "=" * 60 + "\n")
    title = "**** %s ****" % board.db_name.capitalize()
    title = "{:^60}".format(title)
    caller.msg(title)
    posts = get_all_posts(board)
    if not posts:
        caller.msg = "No posts found yet on this board."
        return
    msgnum = 0
    msgtable = EvTable(
        "bb/msg", "Subject", "PostDate", "Posted By"
    )

    # to do - posts track if they are read-by characters.
    # not working for now.
    
    read_posts = get_unread_posts(caller)
    for post in posts:
        unread = post not in read_posts
        msgnum += 1
        if str(board_num).isdigit():
            bbmsgnum = str(board_num) + "/" + str(msgnum)
        else:
            bbmsgnum = board.db_name.capitalize() + "/" + str(msgnum)
        # if unread message, make the message white-bold
        if unread:
            bbmsgnum = "" + "{0}".format(bbmsgnum)
        subject = post.db_header[:35]
        date = post.db_date_created.strftime("%x")
        poster = board.get_poster(post)[:10]
        # turn off white-bold color if unread message
        if unread:
            poster = "{0}".format(poster) + ""
        msgtable.add_row(bbmsgnum, subject, date, poster)
    caller.msg(str(msgtable))
    pass


def get_unread_posts(caller):
    bb_list = get_boards(caller)
    if not bb_list:
        return
    my_subs = []
    for bb in bb_list:
        if caller in bb.has_subscriber.all():
            my_subs.append(bb)
    msg = "New @bb posts in: "
    unread = []
    for bb in my_subs:
        post = bb.get_latest_post()
        if not post:
            continue
        if not post.check_read(caller):
            unread.append(bb)
    if unread:
        msg += ", ".join(bb.key.capitalize() for bb in unread)
        caller.msg(msg)
    else:
        caller.msg("There are no unread posts on your subscribed bboards.")

class CmdGetUnreadPosts(MuxCommand):
    """
    +bbunread - get unread posts
    """

    key = "bbunread"
    aliases = ["@bbunread", "+bbunread"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned)"

    def func(self):
        caller = self.caller
        get_unread_posts(caller)

class CmdBBNew(MuxCommand):

    """
    bbnext to read an unread post from boards you are subscribed to

    Usage:
        +bbnext - retrieve a single post
        +bbnext <number of posts>[=<board num>] - retrieve posts
        +bbnext/all[=<board num>] - retrieve all posts

    This command will retrieve unread messages. If an argument is passed,
    it will retrieve up to the number of messages specified.

    You can use bbnext/all (or bbcatchup) to instantly see all unread posts.

    """

    key = "bbnext"
    aliases = ["+bbnext ", "@bbnext", "bbnew", "+bbnew", "+bbcatchup", "bbcatchup"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned)"

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.lhs
        bb_list = get_boards(caller)
        my_subs = []

        if not bb_list:
            return
        if not self.rhs:
            for bb in bb_list:
                if caller in bb.has_subscriber.all():
                    my_subs.append(bb)
        else:
            sub = access_bboard(caller, self.rhs)
            if sub:
                my_subs.append(sub)
        if not my_subs:
            caller.msg("Currently not subscribed to any boards.")
            return
        if not args:
            num_posts = 1
        elif "all" in args:
            num_posts = 500
        else:
            try:
                num_posts = int(args)
            except ValueError:
                caller.msg("Argument must either be 'all' or a number.")
                return
        # found_posts = 0
        # caller.msg("Unread posts:\n{}".format("-" * 60))
        # noread = "markread" in self.switches
        unread_count = 0
        for bb in my_subs:
            posts = bb.get_unread_posts(caller.account)
            if not posts:
                continue
            unread_count += 1
            # caller.msg("Board %s:" % bb.key)
            # posts_on_board = 0
            for post in posts:
                bb.read_post(caller, post)
                # if noread:
                #     bb.mark_read(caller, post)
                # else:
                #     bb.read_post(caller, post)
                # found_posts += 1
                # posts_on_board += 1
                # if found_posts >= num_posts:
                #     return
            # if noread:
            #     self.msg("You have marked %s posts as read." % posts_on_board)
        # if not found_posts:
        #     self.msg(
        #         "No new posts found on boards: %s."
        #         % ", ".join(str(sub) for sub in my_subs)
        #     )
        if unread_count != 0:
            caller.msg("Marked posts as read.")
        else:
            caller.msg("There are no unread posts on your subscribed bboards.")

        


class CmdBBRead(MuxCommand):

    """
    bbread to read posts on the bboards you are subscribed to.

    Usage:
        +bbread
        +bbread <Board Number>
        +bbread <Board Number>/<Message Number>

    The first command in the list returns a list of all the boards you are
    currently subscribed to. (You can also use +bblist for this.)

    The second command returns a list of all the posts made to the given  
    board.

    The third command returns a specific post on the given board.

    See also bbpost, bbedit, bbdel commands.

    """

    key = "bbread"
    aliases = ["+bbread", "@bbread", "bread", "+bread", "+bblist", "bblist"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned)"

    def func(self):
        caller = self.caller
        args = self.args

        
        
        if self.cmdstring == "bread" or self.cmdstring == "+bread":
            caller.msg("I assumed you meant bbread, but just in case, here's bread: https://www.youtube.com/watch?v=bHK0uFb6Vzw ")

        if not args:
            list_bboards(caller)
            return
        
        if self.cmdstring == "bblist" or self.cmdstring == "+bblist":
            #assuming I want the old bblist command
            list_bboards(caller)
            return
        
        # do the reading not listing 
        arglist = args.split("/")
        
        if len(arglist) < 2:
            board_to_check = access_bboard(caller, args)
            if not board_to_check:
                return
            board_subs = board_to_check.has_subscriber.all()
            if not caller in board_subs:
                caller.msg(
                    "You are not yet a subscriber to {0}.".format(board_to_check.db_name)
                )
                caller.msg("Use bbsub to subscribe to it.")
                return
            list_messages(caller, board_to_check, args)
            return

class CmdBBPost(MuxCommand):
    """
    Post to boards that you are subscribed to.

    Usage:
       +bbpost <Board Number>/<Subject>=<Message>

    Use this syntax to post a new message to a bboard.

    Example:
       +bbpost 1/Greetings=This is my first post!
       bbpost 2/It's OK=The plus sign is optional.%R%RMUSH format works!

    Bulletin Boards are intended to be discussion groups divided
    by topic for news announcements.

    Most boards are considered OOC communication.

    Group-related boards are considered IC communication and can be used
    to share information between characters in those groups. This is a 
    good way for groups to be connected about RP they may have missed while
    offline. Please keep in mind that even if you can see a board OOCly,
    you can only ICly use information that you know ICly, such as being 
    a member of said group. Use boards responsibily!

    To subscribe to a board, use 'bbsub'. To read the newest post on
    a board, use bbnew.
    
    """

    key = "bbpost"
    aliases = ["+bbpost"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned), perm(Player)"
    # guests can read but only players should post.

    def func(self):
        """Implement the command"""
        caller = self.caller
        args = self.args
        
        if not args:
            caller.msg("Syntax: +bbpost <Board Number>/<Subject>=<Message>")
            return
        
        if not self.rhs:
                caller.msg("Usage: +bbpost <Board Number>/<Subject>=<Message>")
                return
        lhs = self.lhs
        arglist = lhs.split("/")
        if len(arglist) < 2:
            subject = "No Subject"
        else:
            subject = arglist[1].lstrip()
            if subject == "":
                subject = "No Subject"
            board = access_bboard(caller, arglist[0], "write")
            if not board:
                return
            message = self.rhs
            message = sub_old_ansi(message)
            # board.bb_post(caller, message, subject)
            bbpost = BoardPost.objects.create(db_title=subject, db_board=board, posted_by=caller,body_text=message)
            if not bbpost:
                caller.msg("Sorry, something went wrong. Usage: +bbpost <Board Number>/<Subject>=<Message>")
            else:
                caller.msg(f"Created post {subject} to board {board}.")
        return

class CmdBBEdit(MuxCommand):
    """
    bbedit to edit a segment of a post that you have already posted.

    Usage:
       +bbedit <Board Number>/<Message Number>=<Old Text>/<New Text>

    This command will search out for something within a post you made, and
    replace it with the new text. 

    Example:
      I'm a hungry boy who eats chips potato.
      +bbedit 2/13=eats chips potato/eats potato chips
      I'm a hungry boy who eats potato chips.

    """

    key = "bbedit"
    aliases = ["+bbedit"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned)"

    def func(self):
        """Implement the command"""

        caller = self.caller
        lhs = self.lhs
        arglist = lhs.split("/")
        if len(arglist) < 2 or not self.rhs:
            self.msg("Usage: bbedit <Board Number>/<Message Number>=<Old Text>/<New Text>")
            return
        try:
            post_num = int(arglist[1])
        except ValueError:
            self.msg("Invalid post number.")
            return
        board = access_bboard(caller, arglist[0], "write")
        if not board:
            return
        post = board.get_post(caller, post_num)
        if not post:
            return
        if not caller.account.check_permstring("Admins"):
            if (caller not in post.db_sender_accounts.all() and not board.access(
                    caller, "edit"
                )) or caller.key.upper() != post.poster_name.upper():
                    caller.msg("You cannot edit someone else's post, only your own.")
                    return
            if board.edit_post(self.caller, post, sub_old_ansi(self.rhs)):
                self.msg("Post edited.")

class CmdBBDel(MuxCommand):

    """
    bbdel - delete my post.

    Usage:
       bbdel <board>/<post>

    Removes a post that you have made from a bboard.

    """
    key = "bbdel"
    aliases = ["+bbdel", "bbremove", "+bbremove", "bbdelete", "+bbdelete"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned)"

    def func(self):
        """Implement the command"""

        caller = self.caller
        args = self.lhs
        switchname = "del"
        verb = "delete"
        method = "delete_post"
        switches = self.switches
        board = args
        if board.tags.get("only_staff_delete") and not caller.check_permstring(
                    "builders"
                ):
                    self.msg("Only builders may delete from that board.")
                    return
            
        elif "sticky" in switches:
            switchname = "sticky"
            verb = "sticky"
            method = "sticky_post"
        else:
            switchname = "archive"
            verb = "archive"
            method = "archive_post"
        if len(args) < 2:
            caller.msg("Usage: @bb/%s <board #>/<post #>" % switchname)
            return
        try:
            post_num = int(args[1])
        except ValueError:
            caller.msg("Invalid post number.")
            return
        post = board.get_post(caller, post_num)
        if not post:
            return
        if not caller.account.check_permstring("Admins"):
            if (caller not in post.db_sender_accounts.all() and not board.access(
                    caller, "edit"
                )) or caller.key.upper() != post.poster_name.upper():
                    caller.msg("You cannot %s someone else's post, only your own." % verb)
                    return
            if getattr(board, method)(post):
                caller.msg("Post %sd" % verb)

            else:
                caller.msg("Post %s failed for unknown reason." % verb)
            return

class CmdBBSub(MuxCommand):
    """
    bbsub - subscribe to a bulletin board

    Usage:
       bbsub <board #>
       bbsub/add <board #>=<player>

    Subscribes to a board of the given number.
    """

    key = "bbsub"
    aliases = ["@bbsub", "+bbsub"]
    help_category = "Comms"
    locks = "cmd:not pperm(bboard_banned)"

    def func(self):
        """Implement the command"""

        caller = self.caller
        args = self.lhs

        if not args:
            self.msg("Usage: bbsub <board #>.")
            return

        bboard = access_bboard(caller, args)
        if not bboard:
            return

        # check permissions
        if not bboard.access(caller, "read"):
            self.msg("%s: You are not allowed to listen to this bboard." % bboard.key)
            return
        if "add" in self.switches:
            if not caller.check_permstring("builders"):
                caller.msg("You must be a builder or higher to use that switch.")
                return
            targ = caller.search(self.rhs)
        else:
            targ = caller
        if not targ:
            return
        if not bboard.subscribe_bboard(targ):
            if "quiet" not in self.switches:
                caller.msg("%s is already subscribed to that board." % targ)
            return
        caller.msg("Successfully subscribed %s to %s" % (targ, bboard.key.capitalize()))


class CmdBBUnsub(default_cmds.MuxCommand):
    """
    bbunsub - unsubscribe from a bulletin board

    Usage:
       bbunsub <board #>

    Removes a bulletin board from your list of subscriptions.
    """

    key = "bbunsub"
    aliases = ["@bbunsub, +bbunsub"]
    help_category = "Comms"
    locks = "cmd:not perm(bboard_banned)"

    def func(self):
        """Implementing the command."""

        caller = self.caller
        args = self.args
        if not args:
            self.msg("Usage: bbunsub <board #>.")
            return
        bboard = access_bboard(caller, args)
        if not bboard:
            return
        if not bboard.has_subscriber(caller):
            caller.msg("You are not subscribed to that board.")
            return
        bboard.unsubscribe_bboard(caller)
        caller.msg("Unsubscribed from %s" % bboard.key)


class CmdBBCreate(MuxCommand):
    """
 
    Usage:
       bbcreate <boardname>

    Creates a new bboard.
    Use the command bbperms to add groups to board permissions.

    """

    key = "bbcreate"
    aliases = ["+bbcreate", "@bbcreate"]
    locks = "cmd:perm(bbcreate) or perm(Wizards)"
    help_category = "Comms"

    def func(self):
        """Implement the command"""

        caller = self.caller

        if not self.args:
            self.msg("Usage bbcreate <boardname>")
            return

        lhs = self.lhs
        bboardname = lhs
        # Create and set the bboard up
        lockstring = "edit:all();write:all();read:all();control:id(%s)" % caller.id

        new_board = BulletinBoard.objects.create(db_name =bboardname)

        self.msg("Created bboard %s." % new_board.db_name)
        #new_board.subscribe_bboard(caller)
        #new_board.save()


class CmdBBPerms(MuxCommand):
    """
 
    Usage:
       bbperms <boardname>=<group>

    Add a group to the permissions for a bboard.
    This accepts player groups and permission groups (aka, staff).

    Does not work yet!

    """

    key = "bbcreate"
    aliases = ["+bbcreate", "@bbcreate"]
    locks = "cmd:perm(bbcreate) or perm(Wizards)"
    help_category = "Comms"

    def func(self):
        """Implement the command"""

        caller = self.caller

        if not self.args:
            self.msg("Usage bbcreate <boardname>")
            return

        lhs = self.lhs
        bboardname = lhs
        # Create and set the bboard up
        lockstring = "edit:all();write:all();read:all();control:id(%s)" % caller.id

        new_board = BulletinBoard.objects.create(db_name =bboardname, db_groups=None)

        self.msg("Created bboard %s." % new_board.db_name)
        #new_board.subscribe_bboard(caller)
        #new_board.save()