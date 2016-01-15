from django.http import HttpResponse
from django.template import Context, Engine
from django.views.debug import DEFAULT_URLCONF_TEMPLATE
from django.utils.translation import ugettext as _

DEBUG_ENGINE = Engine(debug=True)

class Middleware(object):

    def process_request(self, request):
        t = DEBUG_ENGINE.from_string(DEFAULT_URLCONF_TEMPLATE)
        c = Context({
            "title": _("Welcome to Django"),
            "heading": _("It worked!"),
            "subheading": _("Congratulations on your first Django-powered project on Heroku."),
            "instructions": _("Of course, you haven't actually done any work yet. "
                "<p>Next, start a Django-on-Heroku project by cloning this Heroku app and running the following commands</p>"
                "<p>Create a virtual environment and activate</p>"
                "<p><code>virtualenv venv</code></p>"
                "On Mac"
                "<p><code>source venv/bin/activate</code></p>"
                "On Windows"
                "<p><code>venv/bin/activate.bat</code></p>"
                "Clone Heroku application"
                "<p><code>heroku git:clone</code></p>"
                "Install requirements and freeze"
                "<p><code>pip install -r requirements.txt</code></p>"
                "<p><code>pip freeze > requirements.txt</code></p>"
                "Start a Django-on-Heorku project"
                "<p><code>PYTHONPATH=packages python -m django-on-heroku startproject [project_name]</code></p>"
                "Commit and push"
                "<p><code>git add .</code></p>"
                "<p><code>git commit</code></p>"
                "<p><code>git push heroku</code></p>"
                "Activate project"
                "<p><code>heroku config:set WSGI_APPLICATION=yourproject.wsgi</code></p>"
                ),
            "explanation": _("You're seeing this message because you have <code>DEBUG = True</code> in your "
                "Django settings file and you haven't configured any URLs. Get to work!"),
            })

        return HttpResponse(t.render(c), content_type='text/html')
