from django.urls import reverse
from classroom.courses.models import Course

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
            #courses/
            menu[0]['submenus'].append({'nombre': 'Crear Curso', 'url': reverse('courses:course_create')})
            menu[0]['submenus'].append({'nombre': 'Lista de Cursos', 'url': reverse('courses:course_list')})
            # Modules
            menu[0]['submenus'].append({'nombre': 'Crear Modulo', 'url': reverse('courses:module_create')})
            menu[0]['submenus'].append({'nombre': 'Modulos', 'url': reverse('courses:module_list')})
            # Lessons
            menu[0]['submenus'].append({'nombre': 'Lecciones', 'url': reverse('courses:lesson_list')})
            menu[0]['submenus'].append({'nombre': 'Crear Lección', 'url': reverse('courses:lesson_create')})

        return {'menu_classroom': menu}
    else:
        return {'menu_classroom': None}

def obtener_progress_class(request):
    if request.user.is_authenticated:
        courses = Course.objects.filter(published=True)
        progress = []
        for course in courses:
            progress.append({
                'course': course,
                'modules': course.modules.all(),
                'lessons': [lesson for module in course.modules.all() for lesson in module.lessons.all()]
            })
        return {'progress_classroom': progress}
    else:   
        return {'progress_classroom': None}
  
