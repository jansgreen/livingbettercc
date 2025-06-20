from django.urls import reverse

def obtener_menu_classroom(request):
    if request.user.is_authenticated:
        user_has_module_access = request.user.has_perm('groups.access_module') or request.user.is_superuser
        menu = [
            {
                'nombre': 'Classroom',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_has_module_access:
            menu[0]['submenus'].append({'nombre': 'Admin Panel', 'url':'/classroom/curso/admin/'})
            menu[0]['submenus'].append({'nombre': 'Crear Curso', 'url':'/classroom/curso/create/'})
            menu[0]['submenus'].append({'nombre': 'Lista de Cursos', 'url': '/classroom/curso/list'})
            menu[0]['submenus'].append({'nombre': 'Crear Modulo', 'url': '/classroom/modules/new/'})
            menu[0]['submenus'].append({'nombre': 'Modulos', 'url': '/classroom/modules/'})
            menu[0]['submenus'].append({'nombre': 'Lession', 'url': '/classroom/lessons/'})
            menu[0]['submenus'].append({'nombre': 'Crear Lession', 'url': '/classroom/lessons/create/'})
            menu[0]['submenus'].append({'nombre': 'Material', 'url': '/classroom/materials/'})
            menu[0]['submenus'].append({'nombre': 'Crear Material', 'url': '/classroom/materials/create/'})

        return {'menu_classroom': menu}
    else:
        return {'menu_classroom': None}
