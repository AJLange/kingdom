from datetime import datetime, date
from functools import reduce
import random
import traceback

from django.db import models
from django.db.models import Q, Count, Avg
from django.conf import settings
from cloudinary.models import CloudinaryField
from evennia.locks.lockhandler import LockHandler
from evennia.utils.idmapper.models import SharedMemoryModel

from .managers import ArxRosterManager, AccountHistoryManager
from server.utils.arx_utils import CachedProperty
from server.utils.picker import WeightedPicker
from world.stats_and_skills import do_dice_check