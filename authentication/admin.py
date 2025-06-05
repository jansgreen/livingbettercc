from django.contrib import admin
from authentication.models.staffs import Staffs
from authentication.models.students import Students
from authentication.models.address import Address
from authentication.models.profiles import Profiles
from authentication.models.customers import Customers

@admin.register(Staffs)
class StaffsAdmin(admin.ModelAdmin):
    list_display = ['user', 'Profiles', 'address', 'nivel_acceso', 'biografia']  # Ensure these fields exist in the Staffs model
    search_fields = ('user__username', 'Profiles', 'address', 'nivel_acceso', 'biografia')
    list_filter = ['user']  # Ensure 'department' is a valid field in the Staffs model

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ['user', 'degree', 'certifications']  # Ensure these fields exist in the Students model
    search_fields = ('user__username', 'degree', 'certifications')
    list_filter = ['user']  # Ensure 'grade' is a valid field in the Students model

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'neighborhood', 'city', 'province', 'postal_code')
    search_fields = ('user__username', 'street', 'neighborhood', 'city', 'province')
    list_filter = ('city', 'province')

@admin.register(Profiles)    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'numero_identidad', 'profesion', 'roll')  # Ensure these fields exist in the Profiles model
    search_fields = ('user__username', 'telefono', 'numero_identidad', 'profesion', 'roll')
    list_filter = ('roll',)  # Ensure 'roll' is a valid field in the Profiles model

@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ['user', 'Profiles', 'address']  # Ensure these fields exist in the Customers model
    search_fields = ('user__username', 'Profiles', 'address')
    list_filter = ['user']  # Ensure 'roll' is a valid field in the Customers model