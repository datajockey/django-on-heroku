from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.startproject import Command as BaseStartProject

import os
import re


BASE_DIR = os.path.dirname(settings.BASE_DIR)

class Command(BaseStartProject):

    project_name = None

    def handle(self, *args, **options):

        target = options.get('directory')
        options['directory'] = target if target is not None else BASE_DIR

        super(Command, self).handle(*args, **options)

        self.project_name = options.pop('name')

        # update settings
        settings = ''
        settings_file = os.path.join(BASE_DIR, self.project_name, 'settings.py')
        with open(settings_file, 'r') as f:
            settings = f.read()

        settings = self.update_settings(settings)

        with open(settings_file, 'w') as f:
            f.write(settings)

        # update wsgi
        wsgi = ''
        wsgi_file = os.path.join(BASE_DIR, self.project_name, 'wsgi.py')
        with open(wsgi_file, 'r') as f:
            wsgi = f.read()

        wsgi = self.update_wsgi(wsgi)

        with open(wsgi_file, 'w') as f:
            f.write(wsgi)

        # create .env
        with open(os.path.join(BASE_DIR, '.env'), 'w') as f:
            f.write('WSGI_APPLICATION=' + self.project_name + '.wsgi')

    def update_settings(self, settings):

        # update sys.path
        settings = re.sub(
            r"^import os$",
            ("import os\n"
             "import sys"
             ),
            settings,
            flags=re.M
            )

        settings = re.sub(
            r"^BASE_DIR = (.*)$",
            ("BASE_DIR = \g<1>\n"
             "\n"
             "# Add vendored 'packages' directory to sys.path\n"
             "PACKAGES = os.path.join(BASE_DIR, 'packages')\n"
             "if PACKAGES not in sys.path:\n"
             "    sys.path.append(PACKAGES)"
             ),
            settings,
            flags=re.M
            )

        # update ALLOWED_HOSTS
        settings = re.sub(
            r"^ALLOWED_HOSTS = \[\]$",
            "ALLOWED_HOSTS = ['*']",
            settings,
            flags=re.M
            )

        # update SECRET_KEY
        settings = re.sub(
            r"^SECRET_KEY = ('.*')$",
            ("SECRET_KEY = os.environ.get(\n"
             "    'SECRET_KEY', \g<1>\n"
             "    )"
             ),
            settings,
            flags=re.M
            )

        # update DATABASES
        if re.search(r"^import dj_database_url$", settings, re.M) is None:
            settings = re.sub(
                r"^import os$",
                ("import dj_database_url\n"
                 "import os"
                 ),
                settings,
                flags=re.M
                )

        settings = re.sub(
            r"^DATABASES = .*^}\n$",
            ("DATABASES = {\n"
             "    'default': dj_database_url.config(\n"
             "        default='postgres://localhost/" + self.project_name + "-local'\n"
             "        )\n"
             "    }"
             ),
             settings,
             flags=re.M|re.S
            )

        # add STATIC_ROOT & STATICFILES_STORAGE
        settings = re.sub(
            r"^STATIC_URL = '/static/'$",
            ("STATIC_URL = '/static/'\n"
             "\n"
             "STATIC_ROOT = os.path.join(BASE_DIR, '.staticfiles')\n"
             "\n"
             "STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'"
             ),
            settings,
            flags=re.M
            )

        # add SECURE_PROXY_SSL_HEADER
        if re.search(r"^SECURE_PROXY_SSL_HEADER", settings, flags=re.M) is None:
            settings += (
                "\n"
                "\n"
                "# Honor the 'X-Forwarded-Proto' header for request.is_secure()\n"
                "SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')\n"
                "\n"
                )

        return settings


    def update_wsgi(self, wsgi):

        # enable WhiteNoise
        wsgi = re.sub(
            r"^from django.core.wsgi import get_wsgi_application$",
            ("from django.core.wsgi import get_wsgi_application\n"
             "from whitenoise.django import DjangoWhiteNoise"
             ),
             wsgi,
             flags=re.M
            )

        wsgi = re.sub(
            r"^application = get_wsgi_application\(\)$",
            ("application = get_wsgi_application()\n"
             "application = DjangoWhiteNoise(application)"
             ),
             wsgi,
             flags=re.M
            )

        return wsgi
