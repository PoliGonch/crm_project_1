"""
WSGI config for crm_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

path_to_parent_file = Path(__file__).resolve().parent
dotenv_path = os.path.join(os.path.dirname(path_to_parent_file), '.env')
load_dotenv(dotenv_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_project.settings')
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm_project.settings.local")
# os.environ["DJANGO_SETTINGS_MODULE"] = "crm_project.settings"

application = get_wsgi_application()
