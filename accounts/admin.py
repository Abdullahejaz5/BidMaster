from django.contrib import admin
from .models import Members,Products,Messages
# Register your models here.
admin.site.register(Members)
admin.site.register(Products)
admin.site.register(Messages)