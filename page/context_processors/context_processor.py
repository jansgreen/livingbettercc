from ..models import Footer

def footer_context(request):
    """
    Añade el contenido del footer al contexto global
    """
    footer = Footer.objects.last()  # Obtener el último registro de Footer
    return {
        'footer': footer
    }
