from django.contrib import admin
from authentication.models.staffs import Staffs
from authentication.models.students import Students
from authentication.address.models import Address
from authentication.models.profiles import AcademicEvidence, Profiles, ScholarshipStudentInfo
from authentication.models.customers import Customers
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models.directives import Directives

# Unregister the default User model

@admin.register(Staffs)
class StaffsAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile', 'address']  # Cambiado 'Profiles' a 'profile'
    search_fields = ('user__username',)
    list_filter = ['user']

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ['user', 'cedula', 'telefono', 'regional', 'distrito_educativo', 'genero', 'cargo', 'institucion_laboral']
    search_fields = ('user__username', 'cedula', 'telefono', 'regional', 'distrito_educativo', 'genero', 'cargo', 'institucion_laboral')
    list_filter = ['user']  # Ensure 'grade' is a valid field in the Students model

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'neighborhood', 'city', 'state', 'zip_code')
    search_fields = ('user__username', 'street', 'neighborhood', 'city', 'state')
    list_filter = ('city', 'state')

@admin.register(Profiles)    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'numero_identidad', 'profesion', 'roll', 'nivel_academico', 'estado_academico')  # Ensure these fields exist in the Profiles model
    search_fields = ('user__username', 'telefono', 'numero_identidad', 'profesion', 'roll')
    list_filter = ('roll', 'nivel_academico', 'estado_academico')  # Ensure 'roll' is a valid field in the Profiles model

@admin.register(AcademicEvidence)
class AcademicEvidenceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'evidence_type', 'uploaded_at')
    search_fields = ('profile__user__username',)
    list_filter = ('evidence_type', 'uploaded_at')

@admin.register(ScholarshipStudentInfo)
class ScholarshipStudentInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'regional', 'district', 'province')
    search_fields = ('user__username', 'regional', 'province')
    list_filter = ('country', 'regional')

@admin.register(Directives)
class DirectivesAdmin(admin.ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username',)

@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username',)
