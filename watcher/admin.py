from django.contrib import admin

from .models import ByRwTask


class ByRwTaskAdmin(admin.ModelAdmin):
    list_display = ("train", "departure_point",
        "destination_point", "departure_date", "is_active", "is_successful")

    list_filter = ("train", "departure_date", "is_active", "is_successful")

    search_fields = ("train", "departure_point", "destination_point")

admin.site.register(ByRwTask, ByRwTaskAdmin)
