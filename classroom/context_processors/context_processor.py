from django.urls import reverse

def obtener_menu_classroom(request):
    if request.user.is_authenticated:
        user_in_manager_group = request.user.groups.filter(name='manager').exists()
        menu = [
            {
                'nombre': 'Classroom',
                'url': '#',
                'submenus': []
            }
        ]
        
        if user_in_manager_group:
            menu[0]['submenus'].append({'nombre': 'Admin Panel', 'url':'/classroom/curso/admin/'})
            menu[0]['submenus'].append({'nombre': 'Crear Curso', 'url':'/classroom/curso/create/'})
            menu[0]['submenus'].append({'nombre': 'Actualizar Curso', 'url': '/classroom/curso/create/<int:pk>/'})
            menu[0]['submenus'].append({'nombre': 'Eliminar Curso', 'url': '/classroom/curso/delete//<int:pk>/'})
            menu[0]['submenus'].append({'nombre': 'Lista de Cursos', 'url': '/classroom/curso/list'})
        
        return {'menu_classroom': menu}
    else:
        return {'menu_classroom': None}
