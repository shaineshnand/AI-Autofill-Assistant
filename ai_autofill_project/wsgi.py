"""
WSGI config for ai_autofill_project project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_autofill_project.settings')

application = get_wsgi_application()



