import os
import sys

from django.core.wsgi import get_wsgi_application

PROJECT_DIR = os.path.abspath(__file__)
sys.path.append(PROJECT_DIR)

# setdefault so a container can pick its own settings (e.g. jobsp.settings_cloud).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jobsp.settings_server")

application = get_wsgi_application()
