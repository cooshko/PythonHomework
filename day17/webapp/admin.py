from django.contrib import admin
from .models import *


# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'gender', 'area')
#     list_filter = ('gender', 'area')
#     search_fields = ('user', 'area')


admin.site.register(Area)
admin.site.register(StaffRole)
admin.site.register(StaffStatus)


class StaffInfoAdmin(admin.ModelAdmin):
    list_display = ('cname', 'area', 'roles', 'gender', 'status')
    list_filter = ('area', 'roles', 'gender', 'status')
    search_fields = ('cname', 'area', 'roles', 'gender', 'status')

admin.site.register(StaffInfo, StaffInfoAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'area')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'teachers':
            kwargs["queryset"] = StaffInfo.teachers.all()
        return super(CourseAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(Course, CourseAdmin)
admin.site.register(StudentStatus)


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'area', 'gender', 'status')
    list_filter = ('area', 'gender', 'status')
    search_fields = ('name', 'area', 'gender', 'status')
admin.site.register(StudentInfo, StudentAdmin)


admin.site.register(CourseScore)