def obtener_menu_Catálogo(request):
    return {
        'menu_Catálogo': [
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
            }
        ]
    }