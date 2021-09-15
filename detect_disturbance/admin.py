from django.contrib import admin

# Register your models here.
from .models import Videos, FramePresence

admin.site.register(Videos)
admin.site.register(FramePresence)
