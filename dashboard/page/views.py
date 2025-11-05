from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Page,  Footer, carouselPage, PageSection
from .forms import PageForm,PageSectionForm, FooterForm, carouselPageForm
from django.contrib import messages


# CRUD para el modelo Page
def page_create(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Página creada exitosamente.")
            return redirect('page:list')
    else:
        form = PageForm()
    return render(request, 'cms_pages/page_form.html', {'form': form, 'title': 'Crear Página'})

def page_list(request):
    pages = Page.objects.all().order_by('order')
    return render(request, 'cms_pages/page_list.html', {'pages': pages})

def page_update(request, slug):
    page = get_object_or_404(Page, slug=slug)
    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, "Página actualizada correctamente.")
            return redirect('page:list')
    else:
        form = PageForm(instance=page)
    return render(request, 'cms_pages/page_form.html', {'form': form, 'title': f'Editar: {page.name}'})

def page_delete(request, slug):
    page = get_object_or_404(Page, slug=slug)
    if request.method == 'POST':
        page.delete()
        messages.success(request, "Página eliminada correctamente.")
        return redirect('page:list')
    return render(request, 'cms_pages/page_confirm_delete.html', {'page': page})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    sections = page.sections.all().order_by('row', 'column')
    return render(request, 'cms_pages/page_detail.html', {'page': page, 'sections': sections})

# CRUD para el modelo PageSection
def section_create(request):
    if request.method == 'POST':
        form = PageSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sección creada exitosamente.")
            return redirect('page:sections_list')
        else:
            messages.error(request, f'{form.errors}Error al crear la sección. Por favor, verifica los datos ingresados.')
    else:
        form = PageSectionForm()
    return render(request, 'cms_pages/section_form.html', {'form': form, 'title': 'Crear Sección'})

def section_list(request):
    sections = PageSection.objects.select_related('page').all().order_by('page', 'row', 'column')
    return render(request, 'cms_pages/section_list.html', {'sections': sections})

def section_update(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    if request.method == 'POST':
        form = PageSectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            updated_section = form.save(commit=False)
            # ensure we update the existing instance instead of creating a new one
            updated_section.pk = section.pk
            updated_section.save()
            # save many-to-many data if present
            form.save_m2m()
            messages.success(request, "Sección actualizada correctamente.")
            return redirect('page:sections_list')
    else:
        form = PageSectionForm(instance=section)
    # Pasamos la sección al contexto para que las plantillas que lo requieran
    # puedan acceder a `section.pk` o a otros atributos sin causar NoReverseMatch.
    return render(request, 'cms_pages/sections_form_update.html', {
        'form': form,
        'title': f'Editar: {section.name}',
        'section': section,
    })

def section_delete(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    if request.method == 'POST':
        section.delete()
        messages.success(request, "Sección eliminada correctamente.")
        return redirect('page:sections_list')
    return render(request, 'cms_pages/section_confirm_delete.html', {'section': section})



def is_admin_or_editor(user):
    return user.is_superuser or user.groups.filter(name__in=['Admin', 'Editor']).exists()

def ver_footer(request):
    footer = Footer.objects.last()  # Obtener el último registro de Footer
    return render(request, 'ver_footer.html', {'footer': footer})

@user_passes_test(is_admin_or_editor)
def agregar_footer(request):
    if request.method == 'POST':
        form = FooterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ver_footer')  # Redirigir a la vista de visualización
    else:
        form = FooterForm()
    return render(request, 'agregar_footer.html', {'form': form})

def carouselPageFunction(request):
    if request.method == "POST":
        form = carouselPageForm(request.POST, request.FILES)
        if form.is_valid:
            form.save()
        return redirect('page:carouselPageFunction')
    form = carouselPageForm()
    image = carouselPage.objects.all()
    context = {
        'form':form,
        'image': image,
    }
    return render(request, 'img_list.html', context)

def imagen_delete(request, img_id):
    image = carouselPage.objects.get(id=img_id)
    image.delete()
    return redirect(carouselPageFunction)