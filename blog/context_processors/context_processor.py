def obtener_menus(request):
    menus = [

        {
            'nombre': 'Post', 
            'url': '#',  # Aquí puedes usar # porque no es un enlace directo.
            'submenus': [
                {'nombre': 'Crear Categoria', 'url': '/blog/categorias/nueva/'},
                {'nombre': 'Crear Posicion', 'url': '/blog/posiciones/nueva/'},
                {'nombre': 'Crear Post', 'url': '/blog/post/nuevo/'},
                {'nombre': 'Listar Posts', 'url': '/blog/'},

            ]
        },
        {
            'nombre': 'Catálogo', 
            'url': '#',
            'submenus': [
                {'nombre': 'Crear Categoria', 'url': '/catalog/categorias/nueva/'},
                {'nombre': 'Listar Categoria', 'url': '/catalog/categorias/'},
                {'nombre': 'Crear Catálogo', 'url': '/catalog/producto/nuevo/'},
                {'nombre': 'Listar Catálogos', 'url': '/catalog/'},
                {'nombre': 'Actualizar Catálogo', 'url': '/catalog/editar/'},
                {'nombre': 'Eliminar Catálogo', 'url': '/catalog/eliminar/'},
            ]
        },

                {
            'nombre': 'Groups', 
            'url': '#',
            'submenus': [
                {'nombre': 'Listar Usuarios', 'url': '/groups/user_list/'},
                {'nombre': 'Ver Grupos', 'url': '/groups/group_list/'}, 
                {'nombre': 'Invitar', 'url': '/groups/invite/'}, 
            ]
        },
        {
            'nombre': 'Metadata', 
            'url': '#',
            'submenus': [
                {'nombre': 'Listar Usuarios', 'url': '/metadata/create/'},
            ]
        },
    ]
    return {'menus': menus}
