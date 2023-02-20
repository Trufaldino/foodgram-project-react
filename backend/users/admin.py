from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


@admin.register(User)
class OwnUserAdmin(UserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'first_name',)


@admin.register(Subscription)
class SubscriptionModlelAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
