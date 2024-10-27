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
                {'nombre': 'Ver Grupos', 'url': '/groups/'}, 
                {'nombre': 'Invitar', 'url': '/groups/invite/'}, 
            ]
        },
        {
            'nombre': 'metadata', 
            'url': '#',
            'submenus': [
                {'nombre': 'Crear Metadata', 'url': '/metadata/create/'}, 
                {'nombre': 'Listar Metadata', 'url': '/metadata/metadata/'}, 

            ]
        },
    ]
    return {'menus': menus}
