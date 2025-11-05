
def obtener_navbar(request):
    options = []
    blog = blogPost.objects.all().exists()
    page = PageSection.objects.all().exists()

    if blog:
        options.append({'nombre': 'Blog', 'url': '/Blog/check/'})
    if page:
        sections = PageSection.objects.all()

        for section in sections:
            capitalized_name = section.name.capitalize()
            # Capitalizar el nombre de la sección antes de agregarlo
            if capitalized_name != 'Home' and capitalized_name != 'Contactanos':
                options.append({'nombre': capitalized_name, 'url': f'/{section.slug}/'})

    # Retornar el menú sin envolver las opciones
    return {
        'menu_home': options
    }
