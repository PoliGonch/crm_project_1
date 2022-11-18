import logging
import traceback
from datetime import datetime

from django.db import IntegrityError
from django.http import HttpRequest
from django.urls import reverse, get_script_prefix



logger = logging.getLogger()

# @app.task()