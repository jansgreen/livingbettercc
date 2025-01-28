def obtener_menu_docs(request):
        if request.user.is_authenticated:
            user_in_manager_group = (request.user.is_authenticated and request.user.groups.filter(name='manager').exists() or request.user.groups.filter(name='Superusuario').exists() )
            menu = [
                {
                    'nombre': 'Docs',
                    'url': '#',
                    'submenus': []
                }
            ]
            
            if user_in_manager_group:
                menu[0]['submenus'].append({'nombre': 'Formulario Evidencias', 'url': '/docs/evidences/evidence_google/'})
            return {'menu_setting': menu}
        else:
            menu = None
            return {'menu_setting': menu}