# your_project/context_processors.py
from django.conf import settings

def bootstrap_css(request):
    return {'BOOTSTRAP_CSS': settings.BOOTSTRAP_CSS}

def bootstrap_js(request):
    return {'BOOTSTRAP_JS': settings.BOOTSTRAP_JS}
