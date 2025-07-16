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
            #courses
            menu[0]['submenus'].append({'nombre': 'Crear Curso', 'url': reverse('courses:course-create')})
            menu[0]['submenus'].append({'nombre': 'Lista de Cursos', 'url': reverse('courses:course-list')})
            # Modules
            menu[0]['submenus'].append({'nombre': 'Crear Modulo', 'url': reverse('courses:module-create')})
            menu[0]['submenus'].append({'nombre': 'Modulos', 'url': reverse('courses:module-list')})
            # Lessons
            menu[0]['submenus'].append({'nombre': 'Lession', 'url': reverse('courses:lesson-list')})
            menu[0]['submenus'].append({'nombre': 'Crear Lession', 'url': reverse('courses:lesson-create')})

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
  
