#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/survey_admin/")

from survey_admin import app as application
application.secret_key='secret'
