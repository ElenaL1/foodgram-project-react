from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Subscribe

User = get_user_model()


class MyUserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )


class SubcribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, MyUserAdmin)
admin.site.register(Subscribe, SubcribeAdmin)
