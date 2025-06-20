# your_project/context_processors.py
from django.conf import settings
from blog.models import blogPost
from dashboard.page.models import PageCategory

def bootstrap_css(request):
    return {'BOOTSTRAP_CSS': settings.BOOTSTRAP_CSS}

def bootstrap_js(request):
    return {'BOOTSTRAP_JS': settings.BOOTSTRAP_JS}

def obtener_navbar(request):
    options = []
    blog = blogPost.objects.all().exists()
    page = PageCategory.objects.all().exists()

    if blog:
        options.append({'nombre': 'Blog', 'url': '/Blog/check/'})
    if page:
        categories = PageCategory.objects.all()
        
        for category in categories:
            capitalized_name = category.name.capitalize()
            # Capitalizar el nombre de la categoría antes de agregarlo
            if capitalized_name != 'Home' and capitalized_name != 'Contactanos':
                options.append({'nombre': capitalized_name, 'url': f'/{category.slug}/'})
    
    # Retornar el menú sin envolver las opciones
    return {
        'menu_home': options
    }
